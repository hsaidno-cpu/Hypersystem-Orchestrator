#!/usr/bin/env python3
"""Least-privilege GitHub-to-Notion HSAR PR evidence synchronizer.

Pilot scope: upsert GitHub pull-request metadata into the HSAR Change & Evidence
Ledger only. Human decision fields are deliberately never written.
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
NOTION_API_BASE = "https://api.notion.com/v1"
GITHUB_API_BASE = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
MAX_RETRIES = 5
MAX_FILES = 200
MAX_RICH_TEXT_CHARS = 1900

_SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [^-]*PRIVATE KEY-----[\s\S]*?-----END [^-]*PRIVATE KEY-----", re.I), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bsecret_[A-Za-z0-9]{20,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s\"']+"), r"\1[REDACTED]"),
    (re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[:=]\s*([^\s,;]+)"), r"\1=[REDACTED]"),
]


class SyncError(RuntimeError):
    """Safe-to-log synchronization error; never includes request headers."""


def redact(value: Any) -> str:
    text = str(value or "")
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def rich_text(value: Any) -> dict[str, Any]:
    text = redact(value)
    chunks = [text[i : i + MAX_RICH_TEXT_CHARS] for i in range(0, len(text), MAX_RICH_TEXT_CHARS)]
    if not chunks:
        chunks = [""]
    if len(chunks) > 100:
        chunks = chunks[:99] + [chunks[99][:MAX_RICH_TEXT_CHARS] + " [TRUNCATED]"]
    return {"rich_text": [{"type": "text", "text": {"content": chunk}} for chunk in chunks]}


def title_text(value: Any) -> dict[str, Any]:
    text = redact(value)[:MAX_RICH_TEXT_CHARS]
    return {"title": [{"type": "text", "text": {"content": text}}]}


def read_rich_text(properties: dict[str, Any], name: str) -> str:
    prop = properties.get(name) or {}
    items = prop.get("rich_text") or prop.get("title") or []
    return "".join(item.get("plain_text") or item.get("text", {}).get("content", "") for item in items)


def read_select(properties: dict[str, Any], name: str) -> str | None:
    selected = (properties.get(name) or {}).get("select")
    return selected.get("name") if isinstance(selected, dict) else None


def split_sha(value: Any) -> str:
    text = str(value or "")
    return text if re.fullmatch(r"[0-9a-fA-F]{40}", text) else "UNKNOWN"


def date_value(value: Any) -> str:
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.date().isoformat()
    except (TypeError, ValueError):
        return dt.datetime.now(dt.timezone.utc).date().isoformat()


def stable_json_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class JsonHttpClient:
    def __init__(self, token: str, base_url: str, headers: dict[str, str] | None = None, timeout: int = 20):
        if not token:
            raise SyncError("Required API credential is not configured")
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._headers = headers or {}
        self._timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        retry_safe: bool = True,
    ) -> dict[str, Any]:
        url = self._base_url + path
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json", **self._headers}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        last_error = "unknown transport error"
        for attempt in range(MAX_RETRIES):
            try:
                with urllib.request.urlopen(request, timeout=self._timeout) as response:
                    raw = response.read()
                    return json.loads(raw.decode("utf-8")) if raw else {}
            except urllib.error.HTTPError as exc:
                code = exc.code
                try:
                    error_body = json.loads(exc.read().decode("utf-8"))
                except Exception:
                    error_body = {}
                notion_code = redact(error_body.get("code", "http_error"))
                transient = code in (408, 429, 500, 502, 503, 504, 529)
                # A 429 is an explicit rejection. For non-idempotent page creation,
                # never retry ambiguous 408/5xx responses that may have committed.
                may_retry = retry_safe or code == 429
                if not transient or not may_retry or attempt == MAX_RETRIES - 1:
                    raise SyncError(f"API request failed: HTTP {code} ({notion_code})") from None
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                try:
                    delay = min(30.0, max(0.0, float(retry_after))) if retry_after else min(2**attempt, 16)
                except (TypeError, ValueError):
                    delay = min(2**attempt, 16)
                last_error = f"HTTP {code} ({notion_code})"
                time.sleep(delay)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if not retry_safe or attempt == MAX_RETRIES - 1:
                    raise SyncError(
                        f"API transport outcome is ambiguous after {type(exc).__name__}; reconcile by stable key before retrying"
                        if not retry_safe
                        else f"API transport failed after {MAX_RETRIES} attempts ({type(exc).__name__})"
                    ) from None
                last_error = type(exc).__name__
                time.sleep(min(2**attempt, 16))
            except json.JSONDecodeError:
                raise SyncError("API returned invalid JSON") from None
        raise SyncError(f"API request failed ({last_error})")


class NotionClient(JsonHttpClient):
    def __init__(self, token: str, data_source_id: str):
        super().__init__(
            token,
            NOTION_API_BASE,
            {"Notion-Version": NOTION_API_VERSION},
        )
        self.data_source_id = data_source_id

    def query_pr_url(self, pr_url: str) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            query: dict[str, Any] = {
                "filter": {"property": "PR URL", "url": {"equals": pr_url}},
                "page_size": 100,
            }
            if cursor:
                query["start_cursor"] = cursor
            result = self.request("POST", f"/data_sources/{self.data_source_id}/query", query)
            matches.extend(result.get("results") or [])
            if not result.get("has_more"):
                return matches
            cursor = result.get("next_cursor")
            if not cursor:
                raise SyncError("Notion query reported more pages without a cursor")

    def create_page(self, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request(
            "POST",
            "/pages",
            {"parent": {"type": "data_source_id", "data_source_id": self.data_source_id}, "properties": properties},
            retry_safe=False,
        )

    def get_page(self, page_id: str) -> dict[str, Any]:
        return self.request("GET", f"/pages/{urllib.parse.quote(page_id, safe='')}")

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request(
            "PATCH",
            f"/pages/{urllib.parse.quote(page_id, safe='')}",
            {"properties": properties},
        )


class GitHubClient(JsonHttpClient):
    def __init__(self, token: str):
        super().__init__(
            token,
            GITHUB_API_BASE,
            {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
        )

    def get_pr(self, repo: str, number: int) -> dict[str, Any]:
        return self.request("GET", f"/repos/{repo}/pulls/{number}")

    def list_pr_files(self, repo: str, number: int) -> tuple[list[dict[str, Any]], bool]:
        items: list[dict[str, Any]] = []
        page = 1
        truncated = False
        while page <= 10:
            batch = self.request("GET", f"/repos/{repo}/pulls/{number}/files?per_page=100&page={page}")
            if not isinstance(batch, list):
                raise SyncError("GitHub returned an invalid pull-request file list")
            items.extend(batch)
            if len(items) >= MAX_FILES:
                truncated = True
                return items[:MAX_FILES], truncated
            if len(batch) < 100:
                return items, truncated
            page += 1
        return items[:MAX_FILES], True

    def list_workflow_runs(self, repo: str, head_sha: str) -> list[dict[str, Any]]:
        if head_sha == "UNKNOWN":
            return []
        result = self.request("GET", f"/repos/{repo}/actions/runs?head_sha={head_sha}&per_page=100")
        runs = result.get("workflow_runs") or []
        return [
            {
                "name": redact(run.get("name", ""))[:180],
                "run_number": run.get("run_number"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "url": run.get("html_url"),
                "head_sha": run.get("head_sha"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
            }
            for run in runs
            if run.get("head_sha") == head_sha
        ]

    def list_prs(self, repo: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, 21):
            batch = self.request(
                "GET",
                f"/repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=100&page={page}",
            )
            if not isinstance(batch, list):
                raise SyncError("GitHub returned an invalid pull-request reconciliation list")
            items.extend(batch)
            if len(batch) < 100:
                return items
        raise SyncError("Reconciliation cap reached (2,000 PRs); refusing partial silent completion")


@dataclass
class SyncResult:
    status: str
    pr_number: int
    page_id: str | None
    content_hash: str


class HsarSyncService:
    def __init__(self, github: GitHubClient, notion: NotionClient, repo: str):
        self.github = github
        self.notion = notion
        self.repo = repo

    def _pr_record(self, pr: dict[str, Any], files: list[dict[str, Any]], files_truncated: bool, runs: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        number = int(pr["number"])
        pr_url = str(pr.get("html_url") or "")
        expected_prefix = f"https://github.com/{self.repo}/pull/{number}"
        if pr_url != expected_prefix:
            raise SyncError("Canonical pull-request URL did not match the allowlisted repository and number")

        base = pr.get("base") or {}
        head = pr.get("head") or {}
        base_sha = split_sha(base.get("sha"))
        head_sha = split_sha(head.get("sha"))
        title = redact(pr.get("title", "(untitled pull request)"))[:MAX_RICH_TEXT_CHARS]
        state = pr.get("state", "unknown")
        merged = bool(pr.get("merged", False))
        changed = []
        for item in files[:MAX_FILES]:
            changed.append({
                "path": redact(item.get("filename", ""))[:500],
                "blob_sha": str(item.get("sha") or "UNKNOWN"),
                "status": str(item.get("status") or "unknown"),
                "changes": int(item.get("changes") or 0),
            })
        changed.sort(key=lambda item: item["path"])
        run_rows = sorted(
            [
                {
                    "name": redact(run.get("name", ""))[:180],
                    "run_number": run.get("run_number"),
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "url": run.get("url"),
                    "head_sha": run.get("head_sha"),
                    "created_at": run.get("created_at"),
                    "updated_at": run.get("updated_at"),
                }
                for run in runs
                if run.get("head_sha") == head_sha
            ],
            key=lambda item: (str(item.get("created_at") or ""), str(item.get("name")), int(item.get("run_number") or 0)),
        )
        fingerprint = {
            "repository": self.repo,
            "pr_number": number,
            "pr_url": pr_url,
            "title": title,
            "state": state,
            "merged": merged,
            "merged_at": pr.get("merged_at"),
            "updated_at": pr.get("updated_at"),
            "base_ref": str(base.get("ref") or "unknown"),
            "base_sha": base_sha,
            "head_ref": str(head.get("ref") or "unknown"),
            "head_sha": head_sha,
            "changed_files_total": int(pr.get("changed_files") or len(changed)),
            "files_truncated": bool(files_truncated),
            "changed_files": changed,
            "workflow_runs": run_rows,
        }
        content_hash = stable_json_hash(fingerprint)
        ci_urls = [str(run.get("url")) for run in run_rows if run.get("url")]
        evidence_lines = [
            f"Canonical GitHub PR API re-read; PR #{number}; state={state}; merged={merged}.",
            f"base={base_sha}; head={head_sha}; changed_files={fingerprint['changed_files_total']}; manifest_truncated={files_truncated}.",
        ]
        if run_rows:
            evidence_lines.extend(
                f"Workflow {run.get('name')}: status={run.get('status')}; conclusion={run.get('conclusion')}; run={run.get('run_number')}; {run.get('url')}"
                for run in run_rows
            )
        else:
            evidence_lines.append("No GitHub Actions workflow-run records were returned for this exact head at observation time.")
        summary = (
            f"GitHub PR #{number}: {title}. State={state}; merged={merged}; "
            f"base={base_sha}; head={head_sha}; files={fingerprint['changed_files_total']}."
        )
        paths = "\n".join(f"{item['path']} | blob={item['blob_sha']} | {item['status']} | changes={item['changes']}" for item in changed)
        if files_truncated:
            paths += f"\n[TRUNCATED: only first {MAX_FILES} file entries retained]"
        positive = "Canonical GitHub pull-request metadata was re-read; exact refs and the bounded changed-file manifest were captured."
        negative = "This projection does not assess code quality, prove runtime behavior, infer a human decision, or authorize merge/release/deployment."
        properties: dict[str, Any] = {
            "Change": title_text(f"GH PR #{number} — {title}"),
            "Project Area": {"select": {"name": "HSO" if self.repo.endswith("Hypersystem-Orchestrator") else "HSMART"}},
            "Repository": {"url": f"https://github.com/{self.repo}"},
            "PR URL": {"url": pr_url},
            "Change Summary": rich_text(summary),
            "Branch": rich_text(head.get("ref") or "unknown"),
            "Base SHA": rich_text(base_sha),
            "Head SHA": rich_text(head_sha),
            "Changed Paths / Blob Hashes": rich_text(paths),
            "Acceptance Evidence": rich_text("\n".join(evidence_lines)),
            "Positive Findings": rich_text(positive),
            "Negative Findings": rich_text(negative),
            "GitHub Sync Status": {"select": {"name": "Partial"}},
            "Notion Sync Status": {"select": {"name": "Partial"}},
            "Content Hash": rich_text(content_hash),
            "Changed At": {"date": {"start": date_value(pr.get("updated_at"))}},
        }
        properties["CI URL"] = {"url": ci_urls[-1] if ci_urls else None}
        return fingerprint, properties

    @staticmethod
    def _hash_from_page(page: dict[str, Any]) -> str:
        return read_rich_text(page.get("properties") or {}, "Content Hash")

    def upsert_pr(self, pr: dict[str, Any], dry_run: bool = False) -> SyncResult:
        number = int(pr["number"])
        files, files_truncated = self.github.list_pr_files(self.repo, number)
        head_sha = split_sha((pr.get("head") or {}).get("sha"))
        runs = self.github.list_workflow_runs(self.repo, head_sha)
        fingerprint, properties = self._pr_record(pr, files, files_truncated, runs)
        expected_hash = stable_json_hash(fingerprint)
        if dry_run:
            return SyncResult("DRY_RUN", number, None, expected_hash)

        matches = self.notion.query_pr_url(fingerprint["pr_url"])
        if len(matches) > 1:
            raise SyncError(f"Duplicate stable-key conflict for PR #{number}; no Notion record was changed")

        if not matches:
            created_page = self.notion.create_page(properties)
            page_id = created_page.get("id")
            if not page_id:
                raise SyncError(f"Notion create response omitted page ID for PR #{number}")
            state = "CREATED"
            page = self.notion.get_page(page_id)
        else:
            page_id = matches[0].get("id")
            if not page_id:
                raise SyncError(f"Notion query returned a page without an ID for PR #{number}")
            page = self.notion.get_page(page_id)
            old_hash = self._hash_from_page(page)
            old_github_status = read_select(page.get("properties") or {}, "GitHub Sync Status")
            old_notion_status = read_select(page.get("properties") or {}, "Notion Sync Status")
            if old_hash == expected_hash and old_github_status == "Synced" and old_notion_status == "Synced":
                return SyncResult("NOOP", number, page_id, expected_hash)
            if old_hash == expected_hash:
                state = "STATUS_REPAIRED"
            else:
                state = "UPDATED"
            self.notion.update_page(page_id, properties)
            page = self.notion.get_page(page_id)

        if self._hash_from_page(page) != expected_hash:
            raise SyncError(f"Notion read-back content hash mismatch for PR #{number}")

        self.notion.update_page(
            page_id,
            {
                "GitHub Sync Status": {"select": {"name": "Synced"}},
                "Notion Sync Status": {"select": {"name": "Synced"}},
            },
        )
        verified = self.notion.get_page(page_id)
        if self._hash_from_page(verified) != expected_hash:
            raise SyncError(f"Notion post-status read-back hash mismatch for PR #{number}")
        props = verified.get("properties") or {}
        if read_select(props, "GitHub Sync Status") != "Synced" or read_select(props, "Notion Sync Status") != "Synced":
            raise SyncError(f"Notion post-status read-back failed for PR #{number}")
        return SyncResult(state, number, page_id, expected_hash)


def load_event(path: str) -> dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, dict):
            raise ValueError("event payload is not an object")
        return value
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SyncError(f"GitHub event payload unavailable or invalid ({type(exc).__name__})") from None


def is_same_repository_pull_request(pr: dict[str, Any], repo: str) -> bool:
    base_repo = (pr.get("base") or {}).get("repo") or {}
    head_repo = (pr.get("head") or {}).get("repo") or {}
    return base_repo.get("full_name") == repo and head_repo.get("full_name") == repo


def event_pr_numbers(event_name: str, event: dict[str, Any]) -> list[int]:
    if event_name == "pull_request":
        number = (event.get("pull_request") or {}).get("number")
        return [int(number)] if number else []
    if event_name == "workflow_run":
        numbers = []
        for item in (event.get("workflow_run") or {}).get("pull_requests") or []:
            if item.get("number"):
                numbers.append(int(item["number"]))
        return sorted(set(numbers))
    return []


def emit_summary(text: str) -> None:
    safe = redact(text)
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(safe + "\n")
    print(safe)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Read GitHub metadata and build receipts without writing to Notion")
    args = parser.parse_args()
    try:
        repo = os.environ.get("GITHUB_REPOSITORY", "")
        allowed = {item.strip() for item in os.getenv("HSAR_ALLOWED_REPOSITORIES", "hsaidno-cpu/Hypersystem-Orchestrator").split(",") if item.strip()}
        if repo not in allowed:
            raise SyncError("Repository is outside HSAR synchronization allowlist")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise SyncError("Invalid GitHub repository identifier")
        github_token = os.getenv("GH_TOKEN")
        if not github_token:
            raise SyncError("GitHub read token is not configured")
        event_name = os.getenv("GITHUB_EVENT_NAME", "")
        event_path = os.getenv("GITHUB_EVENT_PATH", "")
        event = load_event(event_path)
        github = GitHubClient(github_token)

        if args.dry_run:
            notion = None
        else:
            notion_token = os.getenv("NOTION_API_TOKEN")
            data_source_id = os.getenv("NOTION_HSAR_CHANGE_DATA_SOURCE_ID")
            if not notion_token or not data_source_id:
                raise SyncError("Notion secret or Change & Evidence Ledger data-source variable is not configured")
            notion = NotionClient(notion_token, data_source_id)
        service = HsarSyncService(github, notion, repo) if notion else None

        numbers = event_pr_numbers(event_name, event)
        if event_name in ("schedule", "workflow_dispatch") or not numbers:
            if event_name == "workflow_run" and not numbers:
                emit_summary("HSAR sync: workflow run has no linked pull request; no record was written.")
                return 0
            prs = github.list_prs(repo)
            numbers = [int(pr["number"]) for pr in prs]
        results: list[SyncResult] = []
        for number in sorted(set(numbers)):
            pr = github.get_pr(repo, number)
            if not is_same_repository_pull_request(pr, repo):
                emit_summary(f"HSAR sync: skipped PR #{number}; base/head repository is outside the same-repository pilot scope.")
                continue
            if service:
                results.append(service.upsert_pr(pr, dry_run=False))
            else:
                files, truncated = github.list_pr_files(repo, number)
                runs = github.list_workflow_runs(repo, split_sha(pr.get("head", {}).get("sha")))
                fingerprint, _ = HsarSyncService._pr_record(
                    HsarSyncService(github, None, repo), pr, files, truncated, runs
                )
                results.append(SyncResult("DRY_RUN", number, None, stable_json_hash(fingerprint)))
        lines = ["## HSAR GitHub → Notion synchronization", f"Repository: {repo}", f"Event: {event_name}"]
        lines.extend(f"- PR #{item.pr_number}: {item.status}; hash {item.content_hash}; page {item.page_id or 'not written'}" for item in results)
        lines.append(f"Processed: {len(results)}; no decision/approval fields were written.")
        emit_summary("\n".join(lines))
        return 0
    except SyncError as exc:
        emit_summary(f"## HSAR synchronization BLOCKED\n\n{redact(exc)}")
        return 1
    except Exception as exc:  # fail closed while keeping credentials and payloads out of logs
        emit_summary(f"## HSAR synchronization FAILED\n\nUnexpected error type: {type(exc).__name__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
