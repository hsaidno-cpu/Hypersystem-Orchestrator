#!/usr/bin/env python3
"""Scoped, idempotent GitHub -> Notion evidence synchronizer for HSO.

The initial vertical slice writes only to the HSO Evidence Registry. It never
changes roadmap status, gate state, work-item progress, approvals, or deletes records.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

API_BASE = "https://api.notion.com/v1"
API_VERSION = "2025-09-03"
REPOSITORY = "hsaidno-cpu/Hypersystem-Orchestrator"
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "github-notion-sync.json"
RETRYABLE = {429, 500, 502, 503, 504}


class SyncError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_record(record: dict[str, Any]) -> str:
    # Observation timestamps change on replay; source-content digest must not.
    stable_content = {
        key: value for key, value in record.items()
        if key not in {"observed_at", "verified_at"}
    }
    return hashlib.sha256(canonical_json(stable_content).encode("utf-8")).hexdigest()


def read_rich_text(properties: dict[str, Any], name: str) -> str:
    prop = properties.get(name, {})
    for kind in ("title", "rich_text"):
        parts = prop.get(kind)
        if isinstance(parts, list):
            return "".join(
                item.get("plain_text") or item.get("text", {}).get("content", "")
                for item in parts if isinstance(item, dict)
            )
    return ""


def page_digest(page: dict[str, Any]) -> str:
    return read_rich_text(page.get("properties", {}), "Content Digest")


def related_ids(config: dict[str, Any], pr_number: int | None, branch: str) -> list[str]:
    pr_map = config.get("pull_request_relation_map", {})
    branch_map = config.get("branch_relation_map", {})
    ids: list[str] = []
    if pr_number is not None and str(pr_number) in pr_map:
        ids.append(pr_map[str(pr_number)])
    if not ids and branch in branch_map:
        ids.append(branch_map[branch])
    if not ids:
        ids = list(config.get("default_relation_ids", []))
    return list(dict.fromkeys(ids))


def base_record(
    *, title: str, evidence_type: str, evidence_state: str, claim: str,
    limitation: str, locator: str, repository_url: str, observed_at: str,
    commit_sha: str = "", branch: str = "", pr_url: str = "", ci_url: str = "",
    verifier_role: str = "HSO", related_work_item_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "title": title[:200], "evidence_type": evidence_type,
        "evidence_state": evidence_state, "evidence_freshness": "FRESH",
        "claim": claim[:1900], "limitation": limitation[:1900],
        "source_locator": locator, "repository_url": repository_url,
        "commit_sha": commit_sha, "branch": branch, "pr_url": pr_url,
        "ci_url": ci_url, "verifier_role": verifier_role,
        "observed_at": observed_at, "verified_at": observed_at,
        "related_work_item_ids": related_work_item_ids or [],
    }


def build_event_record(
    event_name: str, payload: dict[str, Any], config: dict[str, Any],
    *, today: date | None = None,
) -> dict[str, Any] | None:
    """Normalize supported GitHub events without converting events into gates."""
    repo = config.get("repository", REPOSITORY)
    repo_url = f"https://github.com/{repo}"
    observed = (today or datetime.now(timezone.utc).date()).isoformat()

    if event_name in {"pull_request", "pull_request_target"}:
        pr = payload.get("pull_request") or {}
        head_repo = (pr.get("head") or {}).get("repo") or {}
        if head_repo.get("full_name") != repo:
            return None
        number = payload.get("number") or pr.get("number")
        if not number or not pr.get("html_url"):
            raise SyncError("pull request event lacks its number or canonical URL")
        branch = (pr.get("head") or {}).get("ref") or ""
        sha = (pr.get("head") or {}).get("sha") or ""
        claim = (
            f"PR #{number} action={payload.get('action', 'unknown')}; "
            f"state={pr.get('state', 'unknown')}; merged={bool(pr.get('merged'))}; "
            f"head={sha}; branch={branch}. This is source metadata only."
        )
        limitation = (
            "PR metadata does not prove CI success, human approval, security sign-off, "
            "host activation, runtime execution, release, or milestone acceptance. "
            "Roadmap and gate properties are never changed by this synchronizer."
        )
        return base_record(
            title=f"PR #{number} — {pr.get('title') or 'Untitled'}",
            evidence_type="Pull Request", evidence_state="UNKNOWN",
            claim=claim, limitation=limitation, locator=pr["html_url"],
            repository_url=repo_url, observed_at=observed, commit_sha=sha,
            branch=branch, pr_url=pr["html_url"],
            related_work_item_ids=related_ids(config, int(number), branch),
        )

    if event_name == "workflow_run":
        run = payload.get("workflow_run") or {}
        if (run.get("head_repository") or {}).get("full_name") != repo:
            return None
        if run.get("name") not in set(config.get("workflow_names", [])):
            return None
        if not run.get("id") or not run.get("html_url"):
            raise SyncError("workflow_run event lacks its run ID or URL")
        conclusion = run.get("conclusion") or "unknown"
        state_map = {
            "success": "PASS", "failure": "FAIL", "timed_out": "FAIL",
            "action_required": "FAIL", "queued": "RUNNING", "in_progress": "RUNNING",
            "requested": "RUNNING", "waiting": "RUNNING", "skipped": "NOT_APPLICABLE",
            "cancelled": "UNKNOWN",
        }
        branch = run.get("head_branch") or ""
        sha = run.get("head_sha") or ""
        prs = run.get("pull_requests") or []
        pr_number = prs[0].get("number") if prs else None
        pr_url = f"{repo_url}/pull/{pr_number}" if pr_number else ""
        claim = (
            f"Workflow {run.get('name')} run #{run.get('run_number')} concluded "
            f"{conclusion} on {branch}@{sha}. Evidence is scoped to this run and commit."
        )
        limitation = (
            "A workflow result is not human approval or release. A green parent workflow "
            "does not prove plugin host activation, live Remote MCP invocation, production "
            "readiness, or milestone acceptance. Skipped jobs remain skipped."
        )
        return base_record(
            title=f"CI — {run.get('name')} #{run.get('run_number')}",
            evidence_type="CI Run", evidence_state=state_map.get(conclusion, "UNKNOWN"),
            claim=claim, limitation=limitation, locator=run["html_url"],
            repository_url=repo_url, observed_at=observed, commit_sha=sha,
            branch=branch, pr_url=pr_url, ci_url=run["html_url"],
            verifier_role="Automated CI",
            related_work_item_ids=related_ids(config, int(pr_number) if pr_number else None, branch),
        )

    if event_name == "push":
        main_ref = "refs/heads/" + config.get("main_branch", "main")
        if payload.get("ref") != main_ref:
            return None
        commit = payload.get("head_commit") or {}
        sha = commit.get("id") or ""
        if not sha:
            commits = payload.get("commits") or []
            sha = commits[-1].get("id", "") if commits else ""
        if not sha:
            return None
        claim = (
            f"Commit {sha} was pushed to {main_ref}; message="
            f"{(commit.get('message') or 'not supplied')[:300]}. Commit event confirms source movement only."
        )
        return base_record(
            title=f"Main commit — {sha[:12]}", evidence_type="Commit",
            evidence_state="UNKNOWN", claim=claim,
            limitation="A commit is not a successful test, review, deployment, or accepted milestone.",
            locator=f"{repo_url}/commit/{sha}", repository_url=repo_url,
            observed_at=observed, commit_sha=sha, branch=main_ref,
            related_work_item_ids=related_ids(config, None, "main"),
        )
    return None


def notion_properties(record: dict[str, Any]) -> dict[str, Any]:
    props: dict[str, Any] = {
        "Evidence Title": {"title": [{"text": {"content": record["title"]}}]},
        "Evidence Type": {"select": {"name": record["evidence_type"]}},
        "Evidence State": {"select": {"name": record["evidence_state"]}},
        "Evidence Freshness": {"select": {"name": record["evidence_freshness"]}},
        "Claim Supported": {"rich_text": [{"text": {"content": record["claim"]}}]},
        "Known Limitation": {"rich_text": [{"text": {"content": record["limitation"]}}]},
        "Source Locator": {"url": record["source_locator"]},
        "Repository URL": {"url": record["repository_url"]},
        "Verifier Role": {"select": {"name": record["verifier_role"]}},
        "Observed At": {"date": {"start": record["observed_at"]}},
        "Verified At": {"date": {"start": record["verified_at"]}},
        "Content Digest": {"rich_text": [{"text": {"content": digest_record(record)}}]},
    }
    for key, name in (("commit_sha", "Commit SHA"), ("branch", "Branch / Ref")):
        if record.get(key):
            props[name] = {"rich_text": [{"text": {"content": record[key][:1900]}}]}
    for key, name in (("pr_url", "PR URL"), ("ci_url", "CI Run URL")):
        if record.get(key):
            props[name] = {"url": record[key]}
    if record.get("related_work_item_ids"):
        props["Related Work Item"] = {
            "relation": [{"id": item} for item in record["related_work_item_ids"]]
        }
    return props


class NotionClient:
    def __init__(self, token: str, data_source_id: str, *, opener=None, sleeper=time.sleep):
        if not token:
            raise SyncError("NOTION_API_KEY is not configured")
        if not data_source_id:
            raise SyncError("NOTION_DATA_SOURCE_ID is not configured")
        self.token = token
        self.data_source_id = data_source_id.removeprefix("collection://")
        self.opener = opener or urllib.request.urlopen
        self.sleeper = sleeper

    def request(self, method: str, path: str, body: dict[str, Any] | None = None, *, retry_transient: bool = True) -> dict[str, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": os.environ.get("NOTION_API_VERSION", API_VERSION),
            "Accept": "application/json",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(f"{API_BASE}/{path.lstrip('/')}", data=data, headers=headers, method=method)
        for attempt in range(1, 5):
            try:
                with self.opener(req, timeout=20) as response:
                    raw = response.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as exc:
                if not retry_transient or exc.code not in RETRYABLE or attempt == 4:
                    raise SyncError(f"Notion API request failed with HTTP {exc.code}") from None
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = min(30, max(1, int(retry_after))) if retry_after else min(2 ** attempt, 16)
                except ValueError:
                    delay = min(2 ** attempt, 16)
                self.sleeper(delay)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if not retry_transient or attempt == 4:
                    raise SyncError("Notion API transport failed; create outcome may require locator reconciliation") from None
                self.sleeper(min(2 ** attempt, 16))
        raise SyncError("Notion API retry loop exhausted")

    def query_by_locator(self, locator: str) -> list[dict[str, Any]]:
        body: dict[str, Any] = {
            "filter": {"property": "Source Locator", "url": {"equals": locator}},
            "page_size": 100,
        }
        results = []
        while True:
            page = self.request("POST", f"data_sources/{self.data_source_id}/query", body)
            results.extend(page.get("results", []))
            if not page.get("has_more") or not page.get("next_cursor"):
                return results
            body["start_cursor"] = page["next_cursor"]

    def query_all(self) -> list[dict[str, Any]]:
        body: dict[str, Any] = {"page_size": 100}
        results = []
        while True:
            page = self.request("POST", f"data_sources/{self.data_source_id}/query", body)
            results.extend(page.get("results", []))
            if not page.get("has_more") or not page.get("next_cursor"):
                return results
            body["start_cursor"] = page["next_cursor"]

    def create_page(self, properties: dict[str, Any], source_locator: str) -> dict[str, Any]:
        body = {
            "parent": {"data_source_id": self.data_source_id},
            "properties": properties,
        }
        try:
            # Page creation is non-idempotent. Never blindly retry a POST /pages
            # after an ambiguous timeout/5xx; first reconcile by canonical locator.
            return self.request("POST", "pages", body, retry_transient=False)
        except SyncError:
            matches = self.query_by_locator(source_locator)
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise SyncError(
                    f"Duplicate Source Locator after ambiguous create ({len(matches)} rows); manual reconciliation required"
                ) from None
            raise SyncError(
                "Page create outcome is ambiguous and no matching Source Locator exists; "
                "retry only after a fresh source-locator preflight"
            ) from None

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.request("PATCH", f"pages/{page_id}", {"properties": properties})


def upsert_record(client: Any, record: dict[str, Any], *, apply: bool) -> dict[str, Any]:
    matches = client.query_by_locator(record["source_locator"])
    if len(matches) > 1:
        raise SyncError(f"Duplicate Source Locator ({len(matches)} rows); refusing ambiguous update")
    props = notion_properties(record)
    if not matches:
        if not apply:
            return {"operation": "CREATE", "source_locator": record["source_locator"]}
        page = client.create_page(props, record["source_locator"])
        return {"operation": "CREATED", "page_id": page.get("id")}
    existing = matches[0]
    if page_digest(existing) == digest_record(record):
        return {"operation": "NO_OP", "page_id": existing.get("id")}
    if not apply:
        return {"operation": "UPDATE", "page_id": existing.get("id")}
    page = client.update_page(existing["id"], props)
    return {"operation": "UPDATED", "page_id": page.get("id", existing["id"])}


def stale_sweep(client: Any, *, today: date, stale_after_days: int, apply: bool) -> dict[str, Any]:
    cutoff = (today - timedelta(days=stale_after_days)).isoformat()
    candidates = []
    for page in client.query_all():
        props = page.get("properties", {})
        freshness = (props.get("Evidence Freshness", {}).get("select") or {}).get("name")
        verified = (props.get("Verified At", {}).get("date") or {}).get("start")
        if freshness == "FRESH" and verified and verified < cutoff:
            candidates.append(page)
    if apply:
        for page in candidates:
            client.update_page(page["id"], {"Evidence Freshness": {"select": {"name": "STALE"}}})
    return {
        "operation": "STALE_SWEEP", "cutoff": cutoff,
        "candidate_count": len(candidates), "updated_count": len(candidates) if apply else 0,
        "dry_run": not apply,
    }


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"Cannot read sync config ({exc.__class__.__name__})") from None
    if config.get("repository") != REPOSITORY or not config.get("evidence_data_source_id"):
        raise SyncError("Sync config is not bound to the approved repository and Evidence Registry")
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HSO GitHub-to-Notion evidence synchronization")
    parser.add_argument("--event-file", type=Path, default=Path(os.environ.get("GITHUB_EVENT_PATH", "")))
    parser.add_argument("--event-name", default=os.environ.get("GITHUB_EVENT_NAME", ""))
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--apply", action="store_true", help="Write to Notion; default is dry-run")
    parser.add_argument("--stale-sweep", action="store_true", help="Mark old FRESH evidence as STALE only")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        client = NotionClient(
            os.environ.get("NOTION_API_KEY", ""),
            os.environ.get("NOTION_DATA_SOURCE_ID", config["evidence_data_source_id"]),
        )
        if args.stale_sweep:
            result = stale_sweep(
                client, today=datetime.now(timezone.utc).date(),
                stale_after_days=int(config.get("stale_after_days", 14)), apply=args.apply,
            )
        else:
            if not args.event_file or not args.event_file.is_file():
                raise SyncError("GitHub event payload file is unavailable")
            payload = json.loads(args.event_file.read_text(encoding="utf-8"))
            record = build_event_record(args.event_name, payload, config)
            result = {"operation": "SKIPPED_UNSUPPORTED_OR_UNTRUSTED_EVENT"} if record is None else upsert_record(client, record, apply=args.apply)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (SyncError, ValueError) as exc:
        print(f"HSO_NOTION_SYNC_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
