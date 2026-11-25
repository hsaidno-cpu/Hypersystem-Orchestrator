#!/usr/bin/env python3
"""Least-privilege GitHub-to-Notion HSAR PR evidence synchronizer.

Pilot: HSO PR metadata -> Change & Evidence Ledger. Human-owned fields are not written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

NOTION_API_VERSION = "2026-03-11"
NOTION_API = "https://api.notion.com/v1"
GITHUB_API = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
MAX_RETRIES = 5
MAX_FILES = 200
RICH_TEXT_LIMIT = 1900

_SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----[\s\S]*?-----END [^-]*PRIVATE KEY-----", re.I), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"), r"\1=[REDACTED]"),
]


class SyncError(RuntimeError):
    """Sanitized operational error; credentials are never included."""


def redact(value: Any) -> str:
    text = str(value or "")
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def rich_text(value: Any) -> dict[str, Any]:
    text = redact(value)
    chunks = [text[i:i + RICH_TEXT_LIMIT] for i in range(0, len(text), RICH_TEXT_LIMIT)] or [""]
    if len(chunks) > 100:
        chunks = chunks[:99] + [chunks[99][:RICH_TEXT_LIMIT] + " [TRUNCATED]"]
    return {"rich_text": [{"type": "text", "text": {"content": part}} for part in chunks]}


def title_text(value: Any) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": redact(value)[:RICH_TEXT_LIMIT]}}]}


def read_rich_text(properties: dict[str, Any], name: str) -> str:
    prop = properties.get(name) or {}
    items = prop.get("rich_text") or prop.get("title") or []
    return "".join(i.get("plain_text") or i.get("text", {}).get("content", "") for i in items)


def read_select(properties: dict[str, Any], name: str) -> str | None:
    value = (properties.get(name) or {}).get("select")
    return value.get("name") if isinstance(value, dict) else None


def sha40(value: Any) -> str:
    value = str(value or "")
    return value if re.fullmatch(r"[0-9a-fA-F]{40}", value) else "UNKNOWN"


def date_value(value: Any) -> str:
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).date().isoformat()
    except (TypeError, ValueError):
        return dt.datetime.now(dt.timezone.utc).date().isoformat()


def stable_hash(value: dict[str, Any]) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


stable_json_hash = stable_hash


class JsonHttpClient:
    def __init__(self, token: str, base: str, headers: dict[str, str] | None = None, timeout: int = 20):
        if not token:
            raise SyncError("Required API credential is not configured")
        self.token, self.base, self.headers, self.timeout = token, base.rstrip("/"), headers or {}, timeout

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None, *, retry_safe: bool = True) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json", **self.headers}
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(self.base + path, data=body, headers=headers, method=method)
        last_error = "unknown transport error"
        for attempt in range(MAX_RETRIES):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except urllib.error.HTTPError as exc:
                try:
                    detail = redact(json.loads(exc.read().decode("utf-8")).get("code", "http_error"))
                except Exception:
                    detail = "http_error"
                transient = exc.code in (408, 429, 500, 502, 503, 504, 529)
                if not transient or (not retry_safe and exc.code != 429) or attempt == MAX_RETRIES - 1:
                    raise SyncError(f"API request failed: HTTP {exc.code} ({detail})") from None
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    delay = min(30.0, max(0.0, float(retry_after))) if retry_after else min(2 ** attempt, 16)
                except (TypeError, ValueError):
                    delay = min(2 ** attempt, 16)
                last_error = f"HTTP {exc.code} ({detail})"
                time.sleep(delay)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if not retry_safe or attempt == MAX_RETRIES - 1:
                    detail = f"ambiguous {type(exc).__name__}; reconcile by stable key before retrying" if not retry_safe else f"failed after {MAX_RETRIES} attempts ({type(exc).__name__})"
                    raise SyncError(f"API transport {detail}") from None
                last_error = type(exc).__name__
                time.sleep(min(2 ** attempt, 16))
            except json.JSONDecodeError:
                raise SyncError("API returned invalid JSON") from None
        raise SyncError(f"API request failed ({last_error})")


class NotionClient(JsonHttpClient):
    def __init__(self, token: str, data_source_id: str):
        super().__init__(token, NOTION_API, {"Notion-Version": NOTION_API_VERSION})
        self.data_source_id = data_source_id

    def query_pr_url(self, url: str) -> list[dict[str, Any]]:
        out, cursor = [], None
        while True:
            payload: dict[str, Any] = {"filter": {"property": "PR URL", "url": {"equals": url}}, "page_size": 100}
            if cursor:
                payload["start_cursor"] = cursor
            result = self.request("POST", f"/data_sources/{self.data_source_id}/query", payload)
            out.extend(result.get("results") or [])
            if not result.get("has_more"):
                return out
            cursor = result.get("next_cursor")
            if not cursor:
                raise SyncError("Notion query returned has_more without a cursor")

    def create_page(self, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/pages", {"parent": {"type": "data_source_id", "data_source_id": self.data_source_id}, "properties": properties}, retry_safe=False)

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{urllib.parse.quote(page_id, safe='')}")

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("PATCH", f"/pages/{urllib.parse.quote(page_id, safe='')}", {"properties": properties})


class GitHubClient(JsonHttpClient):
    def __init__(self, token: str):
        super().__init__(token, GITHUB_API, {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})

    def get_pr(self, repo: str, number: int) -> dict[str, Any]:
        return self.request("GET", f"/repos/{repo}/pulls/{number}")

    def list_pr_files(self, repo: str, number: int) -> tuple[list[dict[str, Any]], bool]:
        rows = []
        for page in range(1, 11):
            batch = self.request("GET", f"/repos/{repo}/pulls/{number}/files?per_page=100&page={page}")
            if not isinstance(batch, list):
                raise SyncError("GitHub returned an invalid PR file list")
            rows.extend(batch)
            if len(rows) >= MAX_FILES:
                return rows[:MAX_FILES], True
            if len(batch) < 100:
                return rows, False
        return rows[:MAX_FILES], True

    def list_workflow_runs(self, repo: str, head_sha: str) -> list[dict[str, Any]]:
        if head_sha == "UNKNOWN":
            return []
        payload = self.request("GET", f"/repos/{repo}/actions/runs?head_sha={head_sha}&per_page=100")
        return [{
            "name": redact(r.get("name", ""))[:180], "run_number": r.get("run_number"),
            "status": r.get("status"), "conclusion": r.get("conclusion"),
            "url": r.get("html_url"), "head_sha": r.get("head_sha"),
            "created_at": r.get("created_at"), "updated_at": r.get("updated_at"),
        } for r in payload.get("workflow_runs", []) if r.get("head_sha") == head_sha]

    def list_prs(self, repo: str) -> list[dict[str, Any]]:
        out = []
        for page in range(1, 21):
            batch = self.request("GET", f"/repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=100&page={page}")
            if not isinstance(batch, list):
                raise SyncError("GitHub returned an invalid PR reconciliation list")
            out.extend(batch)
            if len(batch) < 100:
                return out
        raise SyncError("Reconciliation cap reached (2,000 PRs); refusing silent partial completion")


@dataclass
class SyncResult:
    status: str
    pr_number: int
    page_id: str | None
    content_hash: str


class HsarSyncService:
    MACHINE_FIELDS = {
        "Branch", "Base SHA", "Head SHA", "Changed Paths / Blob Hashes", "CI URL",
        "Content Hash", "GitHub Sync Status", "Notion Sync Status", "Changed At",
        "Automation Sync Receipt",
    }

    def __init__(self, github: GitHubClient, notion: NotionClient, repo: str):
        self.github, self.notion, self.repo = github, notion, repo

    def build_record(self, pr: dict[str, Any], files: list[dict[str, Any]], truncated: bool, runs: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        number = int(pr["number"])
        pr_url = str(pr.get("html_url") or "")
        if pr_url != f"https://github.com/{self.repo}/pull/{number}":
            raise SyncError("Canonical PR URL does not match allowlisted repository and PR number")
        base, head = pr.get("base") or {}, pr.get("head") or {}
        base_sha, head_sha = sha40(base.get("sha")), sha40(head.get("sha"))
        title = redact(pr.get("title", "(untitled)"))[:RICH_TEXT_LIMIT]
        changed = sorted([{
            "path": redact(f.get("filename", ""))[:500], "blob_sha": str(f.get("sha") or "UNKNOWN"),
            "status": str(f.get("status") or "unknown"), "changes": int(f.get("changes") or 0),
        } for f in files[:MAX_FILES]], key=lambda x: x["path"])
        workflow = sorted([{
            "name": redact(r.get("name", ""))[:180], "run_number": r.get("run_number"),
            "status": r.get("status"), "conclusion": r.get("conclusion"), "url": r.get("url"),
            "head_sha": r.get("head_sha"), "created_at": r.get("created_at"), "updated_at": r.get("updated_at"),
        } for r in runs if r.get("head_sha") == head_sha], key=lambda x: (str(x.get("created_at") or ""), str(x.get("name")), int(x.get("run_number") or 0)))
        source = {
            "repository": self.repo, "pr_number": number, "pr_url": pr_url, "title": title,
            "state": pr.get("state", "unknown"), "merged": bool(pr.get("merged", False)),
            "merged_at": pr.get("merged_at"), "updated_at": pr.get("updated_at"),
            "base_ref": str(base.get("ref") or "unknown"), "base_sha": base_sha,
            "head_ref": str(head.get("ref") or "unknown"), "head_sha": head_sha,
            "changed_files_total": int(pr.get("changed_files") or len(changed)),
            "files_truncated": bool(truncated), "changed_files": changed, "workflow_runs": workflow,
        }
        digest = stable_hash(source)
        receipt = [
            f"Canonical GitHub PR API re-read; PR #{number}; state={source['state']}; merged={source['merged']}.",
            f"base={base_sha}; head={head_sha}; changed_files={source['changed_files_total']}; manifest_truncated={truncated}.",
        ]
        receipt.extend(f"Workflow {r['name']}: status={r['status']}; conclusion={r['conclusion']}; run={r['run_number']}; {r['url']}" for r in workflow)
        if not workflow:
            receipt.append("No GitHub Actions workflow-run records were returned for this exact head at observation time.")
        paths = "\n".join(f"{f['path']} | blob={f['blob_sha']} | {f['status']} | changes={f['changes']}" for f in changed)
        if truncated:
            paths += f"\n[TRUNCATED: first {MAX_FILES} file entries only]"
        urls = [r["url"] for r in workflow if r.get("url")]
        props = {
            "Change": title_text(f"GH PR #{number} — {title}"),
            "Project Area": {"select": {"name": "HSO"}},
            "Repository": {"url": f"https://github.com/{self.repo}"}, "PR URL": {"url": pr_url},
            "Branch": rich_text(head.get("ref") or "unknown"), "Base SHA": rich_text(base_sha),
            "Head SHA": rich_text(head_sha), "Changed Paths / Blob Hashes": rich_text(paths),
            "Automation Sync Receipt": rich_text("\n".join(receipt)),
            "CI URL": {"url": urls[-1] if urls else None}, "Content Hash": rich_text(digest),
            "GitHub Sync Status": {"select": {"name": "Partial"}},
            "Notion Sync Status": {"select": {"name": "Partial"}},
            "Changed At": {"date": {"start": date_value(pr.get("updated_at"))}},
        }
        return source, props

    def upsert_pr(self, pr: dict[str, Any], dry_run: bool = False) -> SyncResult:
        number = int(pr["number"])
        files, truncated = self.github.list_pr_files(self.repo, number)
        head_sha = sha40((pr.get("head") or {}).get("sha"))
        source, props = self.build_record(pr, files, truncated, self.github.list_workflow_runs(self.repo, head_sha))
        digest = stable_hash(source)
        if dry_run:
            return SyncResult("DRY_RUN", number, None, digest)
        matches = self.notion.query_pr_url(source["pr_url"])
        if len(matches) > 1:
            raise SyncError(f"Duplicate stable-key conflict for PR #{number}; no Notion record was changed")
        if not matches:
            created = self.notion.create_page(props)
            page_id = created.get("id")
            if not page_id:
                raise SyncError(f"Notion create response omitted page ID for PR #{number}")
            status = "CREATED"
            page = self.notion.get_page(page_id)
        else:
            page_id = matches[0].get("id")
            if not page_id:
                raise SyncError(f"Notion query returned a page without ID for PR #{number}")
            page = self.notion.get_page(page_id)
            old_hash = read_rich_text(page.get("properties") or {}, "Content Hash")
            old_gh = read_select(page.get("properties") or {}, "GitHub Sync Status")
            old_notion = read_select(page.get("properties") or {}, "Notion Sync Status")
            if old_hash == digest and old_gh == "Synced" and old_notion == "Synced":
                return SyncResult("NOOP", number, page_id, digest)
            status = "STATUS_REPAIRED" if old_hash == digest else "UPDATED"
            patch = {key: value for key, value in props.items() if key in self.MACHINE_FIELDS}
            self.notion.update_page(page_id, patch)
            page = self.notion.get_page(page_id)
        if read_rich_text(page.get("properties") or {}, "Content Hash") != digest:
            raise SyncError(f"Notion read-back content hash mismatch for PR #{number}")
        self.notion.update_page(page_id, {
            "GitHub Sync Status": {"select": {"name": "Synced"}},
            "Notion Sync Status": {"select": {"name": "Synced"}},
        })
        verified = self.notion.get_page(page_id)
        vprops = verified.get("properties") or {}
        if read_rich_text(vprops, "Content Hash") != digest:
            raise SyncError(f"Notion post-status hash mismatch for PR #{number}")
        if read_select(vprops, "GitHub Sync Status") != "Synced" or read_select(vprops, "Notion Sync Status") != "Synced":
            raise SyncError(f"Notion post-status read-back failed for PR #{number}")
        return SyncResult(status, number, page_id, digest)


def assert_write_enabled(dry_run: bool) -> None:
    if not dry_run and os.getenv("HSAR_NOTION_SYNC_ENABLED", "false").lower() != "true":
        raise SyncError("Notion write gate is disabled; set HSAR_NOTION_SYNC_ENABLED=true only after least-privilege setup")


def event_pr_numbers(name: str, event: dict[str, Any]) -> list[int]:
    if name == "pull_request":
        number = (event.get("pull_request") or {}).get("number")
        return [int(number)] if number else []
    if name == "workflow_run":
        return sorted({int(x["number"]) for x in (event.get("workflow_run") or {}).get("pull_requests", []) if x.get("number")})
    return []


def is_same_repository_pull_request(pr: dict[str, Any], repo: str) -> bool:
    return (pr.get("base", {}).get("repo", {}) or {}).get("full_name") == repo and (pr.get("head", {}).get("repo", {}) or {}).get("full_name") == repo


def load_event(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as stream:
            event = json.load(stream)
        if not isinstance(event, dict):
            raise ValueError("event payload is not an object")
        return event
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SyncError(f"GitHub event payload invalid ({type(exc).__name__})") from None


def emit(text: str) -> None:
    safe = redact(text)
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(safe + "\n")
    print(safe)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Read GitHub state without calling Notion")
    args = parser.parse_args()
    try:
        repo = os.getenv("GITHUB_REPOSITORY", "")
        allowed = {x.strip() for x in os.getenv("HSAR_ALLOWED_REPOSITORIES", "hsaidno-cpu/Hypersystem-Orchestrator").split(",") if x.strip()}
        if repo not in allowed or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise SyncError("Repository is outside the HSAR allowlist or malformed")
        gh_token = os.getenv("GH_TOKEN")
        if not gh_token:
            raise SyncError("GitHub read token is not configured")
        event_name = os.getenv("GITHUB_EVENT_NAME", "")
        event = load_event(os.getenv("GITHUB_EVENT_PATH", ""))
        github = GitHubClient(gh_token)
        assert_write_enabled(args.dry_run)
        if args.dry_run:
            notion = None
        else:
            notion_token = os.getenv("NOTION_API_TOKEN")
            data_source = os.getenv("NOTION_HSAR_CHANGE_DATA_SOURCE_ID")
            if not notion_token or not data_source:
                raise SyncError("Notion secret or Change & Evidence Ledger data-source variable is not configured")
            notion = NotionClient(notion_token, data_source)
        service = HsarSyncService(github, notion, repo) if notion else None
        numbers = event_pr_numbers(event_name, event)
        if event_name in ("schedule", "workflow_dispatch", "push") or (not numbers and event_name != "workflow_run"):
            numbers = [int(p["number"]) for p in github.list_prs(repo)]
        if event_name == "workflow_run" and not numbers:
            emit("HSAR sync: workflow run is not linked to a PR; no row written.")
            return 0
        results = []
        for number in sorted(set(numbers)):
            pr = github.get_pr(repo, number)
            if not is_same_repository_pull_request(pr, repo):
                emit(f"HSAR sync: skipped PR #{number}; outside same-repository pilot scope.")
                continue
            if service:
                results.append(service.upsert_pr(pr))
            else:
                files, truncated = github.list_pr_files(repo, number)
                source, _ = HsarSyncService(github, None, repo).build_record(pr, files, truncated, github.list_workflow_runs(repo, sha40(pr.get("head", {}).get("sha"))))
                results.append(SyncResult("DRY_RUN", number, None, stable_hash(source)))
        lines = ["## HSAR GitHub → Notion synchronization", f"Repository: {repo}", f"Event: {event_name}"]
        lines.extend(f"- PR #{r.pr_number}: {r.status}; hash {r.content_hash}; page {r.page_id or 'not written'}" for r in results)
        lines.append(f"Processed: {len(results)}; no human decision or acceptance field was written.")
        emit("\n".join(lines))
        return 0
    except SyncError as exc:
        emit(f"## HSAR synchronization BLOCKED\n\n{redact(exc)}")
        return 1
    except Exception as exc:
        emit(f"## HSAR synchronization FAILED\n\nUnexpected error type: {type(exc).__name__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
