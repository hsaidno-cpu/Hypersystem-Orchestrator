#!/usr/bin/env python3
"""Read-only, evidence-bound independent evaluation gate for HSO candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"
DOMAIN_WEIGHTS = {
    "provenance": 15,
    "source_parity": 20,
    "behavior": 20,
    "security": 15,
    "runtime": 20,
    "independence": 10,
}
CHECK_STATUSES = {"PASS", "PASS_WITH_CAVEATS", "FAIL", "NOT_RUN", "BLOCKED", "UNVERIFIABLE"}
HARD_FAIL_DOMAINS = {"provenance", "security", "independence"}
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")


class EvaluationInputError(ValueError):
    """The candidate evidence dossier is malformed or unsafe to evaluate."""


class EvaluationReportError(ValueError):
    """The evaluation report or its digest sidecar is invalid."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvaluationInputError(f"{field} must be a non-empty string")
    return value.strip()


def validate_input(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise EvaluationInputError("evaluation input must be a JSON object")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise EvaluationInputError(f"schema_version must equal {SCHEMA_VERSION}")
    candidate = document.get("candidate")
    if not isinstance(candidate, dict):
        raise EvaluationInputError("candidate must be an object")
    for key in ("candidate_id", "plugin_key", "version", "source_repository", "source_commit", "package_release_id", "target_host"):
        _nonempty(candidate.get(key), f"candidate.{key}")
    if not HEX_40.fullmatch(candidate["source_commit"]):
        raise EvaluationInputError("candidate.source_commit must be a full 40-character Git SHA")
    package_digest = candidate.get("package_digest")
    if package_digest is not None and (not isinstance(package_digest, str) or not HEX_64.fullmatch(package_digest)):
        raise EvaluationInputError("candidate.package_digest must be null or a 64-character SHA-256")

    builder = _nonempty(document.get("builder_identity"), "builder_identity")
    approver = _nonempty(document.get("approver_identity"), "approver_identity")
    evaluator = document.get("evaluator")
    if not isinstance(evaluator, dict):
        raise EvaluationInputError("evaluator must be an object")
    evaluator_id = _nonempty(evaluator.get("identity"), "evaluator.identity")
    evaluator_version = _nonempty(evaluator.get("version"), "evaluator.version")
    if not isinstance(evaluator.get("read_only"), bool):
        raise EvaluationInputError("evaluator.read_only must be boolean")

    required = document.get("required_domains")
    if not isinstance(required, list) or not required:
        raise EvaluationInputError("required_domains must be a non-empty array")
    if any(not isinstance(x, str) or x not in DOMAIN_WEIGHTS for x in required):
        raise EvaluationInputError("required_domains contains an unknown domain")
    if len(set(required)) != len(required):
        raise EvaluationInputError("required_domains cannot contain duplicates")

    checks = document.get("checks")
    if not isinstance(checks, list):
        raise EvaluationInputError("checks must be an array")
    normalized: dict[str, dict[str, Any]] = {}
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise EvaluationInputError(f"checks[{index}] must be an object")
        domain = check.get("domain")
        if not isinstance(domain, str) or domain not in DOMAIN_WEIGHTS or domain == "independence":
            raise EvaluationInputError(f"checks[{index}].domain is invalid or evaluator-owned")
        if domain in normalized:
            raise EvaluationInputError(f"duplicate check for domain {domain}")
        status = check.get("status")
        if not isinstance(status, str) or status not in CHECK_STATUSES:
            raise EvaluationInputError(f"checks[{index}].status is invalid")
        rationale = _nonempty(check.get("rationale"), f"checks[{index}].rationale")
        refs = check.get("evidence_refs", [])
        digests = check.get("evidence_digests", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) or not x.strip() for x in refs):
            raise EvaluationInputError(f"checks[{index}].evidence_refs must be an array of non-empty strings")
        if not isinstance(digests, list) or any(not isinstance(x, str) or not (HEX_40.fullmatch(x) or HEX_64.fullmatch(x)) for x in digests):
            raise EvaluationInputError(f"checks[{index}].evidence_digests must contain Git SHA-1 or SHA-256 values")
        normalized[domain] = {"status": status, "rationale": rationale, "evidence_refs": refs, "evidence_digests": digests}

    return {
        "candidate": candidate,
        "builder_identity": builder,
        "approver_identity": approver,
        "evaluator_identity": evaluator_id,
        "evaluator_version": evaluator_version,
        "evaluator_read_only": evaluator["read_only"],
        "required_domains": required,
        "checks": normalized,
    }


def _trusted_evaluator_context(context: dict[str, str] | None) -> bool:
    """Trust evaluation only when the workflow itself runs from protected main."""
    context = context or {}
    workflow_ref = context.get("GITHUB_WORKFLOW_REF", "")
    return (
        context.get("GITHUB_EVENT_NAME") in {"push", "workflow_dispatch"}
        and context.get("GITHUB_REF") == "refs/heads/main"
        and context.get("GITHUB_REF_PROTECTED", "").lower() == "true"
        and workflow_ref.endswith("@refs/heads/main")
    )


def evaluate_document(
    document: Any,
    *,
    input_sha256: str,
    evaluator_engine_sha256: str,
    execution_context: dict[str, str] | None = None,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    data = validate_input(document)
    identity_separated = (
        data["evaluator_identity"] != data["builder_identity"]
        and data["evaluator_identity"] != data["approver_identity"]
        and data["evaluator_read_only"] is True
    )
    trusted_execution_context = _trusted_evaluator_context(execution_context)
    results: list[dict[str, Any]] = []
    hard_failures: list[str] = []
    unresolved: list[str] = []
    awarded = 0.0
    available = sum(DOMAIN_WEIGHTS[d] for d in data["required_domains"])

    for domain in data["required_domains"]:
        weight = DOMAIN_WEIGHTS[domain]
        if domain == "independence":
            if not identity_separated:
                status = "FAIL"
                rationale = "Evaluator identity overlaps builder/approver or evaluator is not read-only."
            elif trusted_execution_context:
                status = "PASS"
                rationale = "Evaluator is read-only and distinct from builder/approver; execution came from the protected main workflow context."
            else:
                status = "UNVERIFIABLE"
                rationale = "Evaluator label and read-only job are declared, but the workflow did not execute from a protected main ref. PR-controlled evaluator code cannot certify its own independence."
            refs = ["independent-evaluation CI job and evaluator engine source", "GitHub Actions event/ref/protection context"]
            digests = [evaluator_engine_sha256]
        else:
            check = data["checks"].get(domain)
            if check is None:
                status, rationale, refs, digests = "NOT_RUN", "No evidence check was supplied for this required domain.", [], []
            else:
                status = check["status"]
                rationale = check["rationale"]
                refs = check["evidence_refs"]
                digests = check["evidence_digests"]
                if status in {"PASS", "PASS_WITH_CAVEATS"} and not refs:
                    status = "UNVERIFIABLE"
                    rationale += " A passing claim without an evidence reference was downgraded."
        awarded_points = float(weight) if status == "PASS" else weight * 0.5 if status == "PASS_WITH_CAVEATS" else 0.0
        awarded += awarded_points
        results.append({
            "domain": domain,
            "required": True,
            "weight": weight,
            "status": status,
            "points_awarded": awarded_points,
            "rationale": rationale,
            "evidence_refs": refs,
            "evidence_digests": digests,
        })
        if status == "FAIL" and domain in HARD_FAIL_DOMAINS:
            hard_failures.append(domain)
        elif status != "PASS":
            unresolved.append(domain)

    if hard_failures:
        disposition = "FAIL"
    elif unresolved:
        disposition = "HOLD"
    elif any(row["status"] == "PASS_WITH_CAVEATS" for row in results):
        disposition = "PASS_WITH_CAVEATS"
    else:
        disposition = "PASS"

    reasons = []
    if hard_failures:
        reasons.append("Hard-fail domain(s): " + ", ".join(hard_failures))
    if unresolved:
        reasons.append("Required domain(s) remain unresolved: " + ", ".join(unresolved))
    if not reasons:
        reasons.append("All required domains passed with evidence and separated read-only evaluator authority.")

    timestamp = evaluated_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "report_schema_version": SCHEMA_VERSION,
        "evaluation_id": "EVAL-" + input_sha256[:16],
        "evaluated_at": timestamp,
        "candidate": data["candidate"],
        "builder_identity": data["builder_identity"],
        "approver_identity": data["approver_identity"],
        "evaluator": {
            "identity": data["evaluator_identity"],
            "version": data["evaluator_version"],
            "read_only": data["evaluator_read_only"],
            "identity_separated": identity_separated,
            "trusted_execution_context": trusted_execution_context,
            "engine_sha256": evaluator_engine_sha256,
        },
        "required_domains": data["required_domains"],
        "criteria_results": results,
        "score": {
            "awarded_points": awarded,
            "available_points": available,
            "percent": round(awarded / available * 100, 2) if available else 0.0,
        },
        "disposition": disposition,
        "decision_reasons": reasons,
        "integrity": {
            "input_sha256": input_sha256,
            "evaluator_engine_sha256": evaluator_engine_sha256,
            "report_is_read_only_assessment": True,
            "candidate_mutated": False,
        },
        "execution_context": execution_context or {},
    }


def write_report(report: dict[str, Any], output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256(raw)
    sidecar = Path(str(output_path) + ".sha256")
    with output_path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        with sidecar.open("x", encoding="ascii") as stream:
            stream.write(digest + "  " + output_path.name + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        output_path.unlink(missing_ok=True)
        raise
    return digest


def verify_report(report_path: Path) -> dict[str, Any]:
    try:
        raw = report_path.read_bytes()
        sidecar = Path(str(report_path) + ".sha256").read_text(encoding="ascii").strip()
        expected = sidecar.split()[0]
        report = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, IndexError) as exc:
        raise EvaluationReportError(f"report or SHA-256 sidecar cannot be read ({type(exc).__name__})") from exc
    actual = _sha256(raw)
    if not HEX_64.fullmatch(expected) or actual != expected:
        raise EvaluationReportError("report SHA-256 does not match its sidecar")
    if not isinstance(report, dict) or report.get("report_schema_version") != SCHEMA_VERSION:
        raise EvaluationReportError("report schema version or JSON shape is invalid")
    integrity = report.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("candidate_mutated") is not False:
        raise EvaluationReportError("report does not attest read-only assessment")
    if report.get("disposition") not in {"PASS", "PASS_WITH_CAVEATS", "HOLD", "FAIL"}:
        raise EvaluationReportError("report disposition is invalid")
    return {"report": report, "report_sha256": actual}


def _engine_sha256() -> str:
    try:
        return _sha256(Path(__file__).read_bytes())
    except OSError as exc:
        raise EvaluationReportError("cannot read evaluator engine source for self-attestation") from exc


def evaluate_file(input_path: Path, output_path: Path) -> dict[str, Any]:
    try:
        raw = input_path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvaluationInputError(f"input dossier cannot be read ({type(exc).__name__})") from exc
    context = {
        key: os.environ[key]
        for key in ("GITHUB_SHA", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_WORKFLOW", "GITHUB_ACTOR", "GITHUB_EVENT_NAME", "GITHUB_REF", "GITHUB_REF_PROTECTED", "GITHUB_WORKFLOW_REF", "GITHUB_WORKFLOW_SHA")
        if os.environ.get(key)
    }
    report = evaluate_document(
        document,
        input_sha256=_sha256(raw),
        evaluator_engine_sha256=_engine_sha256(),
        execution_context=context,
    )
    digest = write_report(report, output_path)
    return {"report": report, "report_sha256": digest, "report_path": str(output_path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    evaluate = sub.add_parser("evaluate", help="evaluate a frozen candidate dossier")
    evaluate.add_argument("input", type=Path)
    evaluate.add_argument("--output", required=True, type=Path)
    verify = sub.add_parser("verify", help="verify a report using its SHA-256 sidecar")
    verify.add_argument("report", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "evaluate":
            result = evaluate_file(args.input, args.output)
            report = result["report"]
            print(json.dumps({
                "evaluation_id": report["evaluation_id"],
                "candidate_id": report["candidate"]["candidate_id"],
                "disposition": report["disposition"],
                "score_percent": report["score"]["percent"],
                "report_sha256": result["report_sha256"],
                "report_path": result["report_path"],
            }, indent=2))
            return 0
        verified = verify_report(args.report)
        report = verified["report"]
        print(json.dumps({
            "evaluation_id": report["evaluation_id"],
            "disposition": report["disposition"],
            "report_sha256": verified["report_sha256"],
            "integrity_verified": True,
        }, indent=2))
        return 0
    except (EvaluationInputError, EvaluationReportError) as exc:
        print(f"independent-evaluation-error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
