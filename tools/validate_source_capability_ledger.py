#!/usr/bin/env python3
"""Validate HSO's pinned source-file ledger and skill-to-source path crosswalk."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HEX_40 = re.compile(r"^[0-9a-f]{40}$")
PARTS = [
    "catalog/source-file-ledger-2026-11-26-part-01.json",
    "catalog/source-file-ledger-2026-11-26-part-02.json",
    "catalog/source-file-ledger-2026-11-26-part-03.json",
]
INDEX = "catalog/source-file-ledger-2026-11-26-index.json"
CROSSWALK = "catalog/skill-source-crosswalk-2026-11-26.json"


class LedgerValidationError(ValueError):
    """Raised when pinned source/capability evidence is inconsistent."""


def _read_json(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerValidationError(f"cannot read {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise LedgerValidationError(f"{relative} must contain a JSON object")
    return value


def validate_ledgers(root: Path) -> dict[str, Any]:
    index = _read_json(root, INDEX)
    crosswalk = _read_json(root, CROSSWALK)
    if index.get("schema_version") != "1.0.0" or crosswalk.get("schema_version") != "1.0.0":
        raise LedgerValidationError("unsupported index/crosswalk schema version")

    boundaries: list[dict[str, Any]] = []
    all_paths: list[dict[str, Any]] = []
    for expected_part, relative in enumerate(PARTS, start=1):
        part = _read_json(root, relative)
        if part.get("schema_version") != "1.0.0":
            raise LedgerValidationError(f"{relative}: unsupported schema version")
        if part.get("ledger_id") != "HSO-SOURCE-FILE-LEDGER-2026-11-26":
            raise LedgerValidationError(f"{relative}: wrong ledger_id")
        if part.get("part") != expected_part or part.get("part_count") != len(PARTS):
            raise LedgerValidationError(f"{relative}: incorrect part ordinal/count")
        part_boundaries = part.get("boundaries")
        if not isinstance(part_boundaries, list):
            raise LedgerValidationError(f"{relative}: boundaries must be an array")
        for boundary in part_boundaries:
            for field in ("boundary_key", "repository", "source_commit", "source_tree_sha", "source_type"):
                if not isinstance(boundary.get(field), str) or not boundary[field]:
                    raise LedgerValidationError(f"{relative}: boundary missing {field}")
            if not HEX_40.fullmatch(boundary["source_commit"]) or not HEX_40.fullmatch(boundary["source_tree_sha"]):
                raise LedgerValidationError(f"{relative}: invalid source commit/tree SHA")
            if boundary.get("recursive_tree_truncated") is not False:
                raise LedgerValidationError(f"{relative}: recursive tree is truncated or unknown")
            entries = boundary.get("entries")
            if not isinstance(entries, list):
                raise LedgerValidationError(f"{relative}: boundary entries must be an array")
            if boundary.get("enumerated_file_blobs") != len(entries):
                raise LedgerValidationError(f"{relative}: declared file count disagrees with entries")
            if boundary.get("count_delta") != len(entries) - boundary.get("previous_expected_file_blobs", 0):
                raise LedgerValidationError(f"{relative}: count delta is inconsistent")
            for entry in entries:
                if not isinstance(entry.get("path"), str) or not entry["path"]:
                    raise LedgerValidationError(f"{relative}: empty source path")
                if not HEX_40.fullmatch(entry.get("blob_sha1", "")):
                    raise LedgerValidationError(f"{relative}: invalid Git blob SHA-1")
                if not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] < 0:
                    raise LedgerValidationError(f"{relative}: missing/invalid file size")
                all_paths.append({
                    "boundary_key": boundary["boundary_key"],
                    "repository": boundary["repository"],
                    "source_commit": boundary["source_commit"],
                    "path": entry["path"],
                    "blob_sha1": entry["blob_sha1"],
                    "size_bytes": entry["size_bytes"],
                })
            boundaries.append({
                "boundary_key": boundary["boundary_key"],
                "repository": boundary["repository"],
                "source_commit": boundary["source_commit"],
                "source_tree_sha": boundary["source_tree_sha"],
                "previous_expected": boundary["previous_expected_file_blobs"],
                "actual": len(entries),
                "delta": boundary["count_delta"],
            })

    if len({b["boundary_key"] for b in boundaries}) != 10:
        raise LedgerValidationError("expected exactly ten distinct source boundaries")
    path_keys = [(x["repository"], x["source_commit"], x["path"]) for x in all_paths]
    if len(path_keys) != len(set(path_keys)):
        raise LedgerValidationError("duplicate source path within the same repository/commit")
    blob_groups: dict[str, list[dict[str, str]]] = {}
    for item in all_paths:
        blob_groups.setdefault(item["blob_sha1"], []).append({
            "boundary_key": item["boundary_key"],
            "repository": item["repository"],
            "path": item["path"],
        })
    duplicates = {k: v for k, v in blob_groups.items() if len(v) > 1}
    duplicate_path_records = sum(len(v) for v in duplicates.values())

    expected_total = index.get("previous_expected_file_paths")
    actual_total = len(all_paths)
    if index.get("total_enumerated_file_paths") != actual_total:
        raise LedgerValidationError("index total does not equal the part manifests")
    if index.get("previous_expected_file_paths") != 864:
        raise LedgerValidationError("the previous 864-path L1 denominator must remain explicitly recorded")
    if actual_total != 869:
        raise LedgerValidationError(f"observed source path count changed: expected 869, found {actual_total}")
    if index.get("git_blob_sha1_unique_content_groups") != len(blob_groups):
        raise LedgerValidationError("index unique Git blob SHA-1 count disagrees with path manifest")
    if index.get("duplicate_blob_groups") != len(duplicates):
        raise LedgerValidationError("index duplicate group count disagrees with path manifest")
    if index.get("duplicate_path_records") != duplicate_path_records:
        raise LedgerValidationError("index duplicate path count disagrees with path manifest")

    hso = next((x for x in boundaries if x["boundary_key"] == "hso"), None)
    if not hso or hso["previous_expected"] != 161 or hso["actual"] != 166 or hso["delta"] != 5:
        raise LedgerValidationError("the five-path HSO L1 count drift must remain visible")

    crosswalk_records = crosswalk.get("records")
    if not isinstance(crosswalk_records, list) or len(crosswalk_records) != 289:
        raise LedgerValidationError("crosswalk must contain exactly 289 skill metadata rows")
    if crosswalk.get("skill_metadata_count") != 289:
        raise LedgerValidationError("crosswalk metadata count is inconsistent")
    path_index = {
        (x["boundary_key"], x["path"]): x
        for x in all_paths
    }
    observed_states = Counter()
    for row in crosswalk_records:
        for field in ("plugin_key", "skill_name", "source_uri", "source_mapping_status"):
            if not isinstance(row.get(field), str) or not row[field]:
                raise LedgerValidationError(f"skill crosswalk row missing {field}")
        observed_states[row["source_mapping_status"]] += 1
        candidates = row.get("source_path_candidates", [])
        if not isinstance(candidates, list):
            raise LedgerValidationError("source_path_candidates must be an array")
        expected_state = (
            "UNIQUE_PATH_NAME_MATCH_PENDING_CONTENT_PARITY" if len(candidates) == 1
            else "AMBIGUOUS_PATH_NAME_MATCH" if len(candidates) > 1
            else None
        )
        if expected_state and row["source_mapping_status"] != expected_state:
            raise LedgerValidationError("crosswalk state does not match candidate path cardinality")
        for candidate in candidates:
            boundary_key = row.get("source_boundary_key")
            key = (boundary_key, candidate.get("path"))
            source = path_index.get(key)
            if source is None:
                raise LedgerValidationError("skill source candidate is absent from the source-file ledger")
            if candidate.get("blob_sha1") != source["blob_sha1"]:
                raise LedgerValidationError("skill source candidate blob SHA disagrees with source-file ledger")
            if candidate.get("size_bytes") != source["size_bytes"]:
                raise LedgerValidationError("skill source candidate size disagrees with source-file ledger")

    if crosswalk.get("state_counts") != dict(observed_states):
        raise LedgerValidationError("crosswalk state_counts do not match records")

    return {
        "source_boundaries": len(boundaries),
        "source_file_paths": actual_total,
        "previous_expected_paths": expected_total,
        "hso_count_delta": hso["delta"],
        "unique_git_blob_sha1_groups": len(blob_groups),
        "duplicate_blob_groups": len(duplicates),
        "duplicate_path_records": duplicate_path_records,
        "skill_metadata_rows": len(crosswalk_records),
        "skill_mapping_states": dict(observed_states),
        "content_sha256": "NOT_COMPUTED",
        "semantic_parity": "NOT_COMPARED",
        "behavior_tests": "NOT_RUN",
        "host_runtime": "NOT_RUN",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        report = validate_ledgers(args.root)
    except LedgerValidationError as exc:
        print(f"source-ledger-validation-error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
