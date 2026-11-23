#!/usr/bin/env python3
"""HSO controlled runtime: capability probe, route arbitration, policy, dispatch, recovery and audit."""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, platform, sqlite3, sys, tempfile, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_PATH = ROOT / "catalog" / "hso-runtime-capabilities.json"
ROUTES_PATH = ROOT / "catalog" / "hso-routing-policy.json"
POLICY_PATH = ROOT / "governance" / "hso-execution-policy.json"
CATALOG_PATH = ROOT / "catalog" / "plugins.json"
SCHEMA_PATH = ROOT / "contracts" / "hso-runtime-workflow.schema.json"
AUTHORITY_RANK = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
MAX_FILE_BYTES = 100_000
RETRY_DELAY_SECONDS = 0.05

class RuntimeErrorBase(Exception): pass
class PermanentActionError(RuntimeErrorBase): pass
class RetryableActionError(RuntimeErrorBase): pass
class PolicyDenied(RuntimeErrorBase): pass
class IdempotencyConflict(RuntimeErrorBase): pass

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def digest_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))

def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeErrorBase(f"Cannot read valid JSON from {path}: {exc}") from exc

def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def _safe_target(workspace: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise PermanentActionError("target_path must be a non-empty relative path")
    part = Path(relative)
    if part.is_absolute() or any(piece in {"..", "."} for piece in part.parts):
        raise PermanentActionError("target_path must be relative and cannot contain dot segments")
    root = workspace.resolve()
    cursor = root
    for piece in part.parts:
        cursor = cursor / piece
        if cursor.is_symlink():
            raise PermanentActionError("target_path cannot traverse a symbolic link")
    resolved = cursor.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PermanentActionError("target_path escapes the declared workspace") from exc
    return resolved

def _write_text(workspace: Path, target_path: str, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    content = payload.get("content")
    if not isinstance(content, str):
        raise PermanentActionError("sandbox.write_text requires string input.content")
    raw = content.encode("utf-8")
    if len(raw) > MAX_FILE_BYTES:
        raise PermanentActionError(f"artifact exceeds the {MAX_FILE_BYTES}-byte runtime limit")
    target = _safe_target(workspace, target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target = _safe_target(workspace, target_path)
    if target.exists():
        if not target.is_file():
            raise PermanentActionError("target exists and is not a regular file")
        if target.read_bytes() == raw:
            return {"target_path": target_path, "sha256": sha256_bytes(raw), "created": False, "no_op": True}
        raise PermanentActionError("refusing to overwrite an existing target with different content")
    try:
        with target.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        if target.read_bytes() == raw:
            return {"target_path": target_path, "sha256": sha256_bytes(raw), "created": False, "no_op": True}
        raise PermanentActionError("target was concurrently created with different content")
    return {"target_path": target_path, "sha256": sha256_bytes(raw), "created": True, "no_op": False}

def _verify_sha256(workspace: Path, target_path: str, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    target = _safe_target(workspace, target_path)
    if not target.is_file():
        raise PermanentActionError("verification target does not exist as a regular file")
    actual = sha256_bytes(target.read_bytes())
    expected = payload.get("expected_sha256")
    if not isinstance(expected, str) or len(expected) != 64:
        raise PermanentActionError("verification requires a 64-character expected_sha256")
    if not hmac.compare_digest(actual, expected.lower()):
        raise PermanentActionError(f"target digest mismatch: expected {expected.lower()}, observed {actual}")
    return {"target_path": target_path, "expected_sha256": expected.lower(), "observed_sha256": actual, "verified": True}

def _flaky_write_text(workspace: Path, target_path: str, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    marker_name = ".hso-internal/" + digest_json({"key": context["idempotency_key"], "fault": "once"}) + ".seen"
    marker = _safe_target(workspace, marker_name)
    marker.parent.mkdir(parents=True, exist_ok=True)
    if not marker.exists():
        marker.write_text("fault injected once\n", encoding="utf-8")
        raise RetryableActionError("injected transient failure before target mutation")
    return _write_text(workspace, target_path, payload, context)

HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "write_text": _write_text, "verify_sha256": _verify_sha256,
}
TEST_HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {"flaky_write_text": _flaky_write_text}

class AuditLog:
    """Hash-chained JSONL audit events. Hash chaining detects edits; it is not a digital signature."""
    def __init__(self, path: Path, run_id: str):
        self.path, self.run_id = path, run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.sequence, self.previous_hash = 0, "0" * 64
        if self.path.exists() and self.path.stat().st_size:
            valid, details = self.verify(self.path)
            if not valid:
                raise RuntimeErrorBase(f"existing audit log is not valid: {details}")
            events = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if events:
                self.sequence, self.previous_hash = events[-1]["sequence"], events[-1]["event_hash"]

    @staticmethod
    def _redact(value: Any, key: str = "") -> Any:
        sensitive = ("secret", "token", "password", "authorization", "cookie", "private_key", "api_key")
        if any(part in key.lower() for part in sensitive):
            return "[REDACTED]"
        if isinstance(value, dict):
            return {str(k): AuditLog._redact(v, str(k)) for k, v in value.items()}
        if isinstance(value, list):
            return [AuditLog._redact(item) for item in value]
        if isinstance(value, str) and len(value) > 512:
            return value[:512] + "[TRUNCATED]"
        return value

    def emit(self, event_type: str, package_id: str | None = None, **details: Any) -> dict[str, Any]:
        self.sequence += 1
        body = {
            "sequence": self.sequence, "event_id": f"{self.run_id}:{self.sequence}",
            "run_id": self.run_id, "timestamp": utc_now(), "event_type": event_type,
            "package_id": package_id, "details": self._redact(details),
            "previous_hash": self.previous_hash,
        }
        event_hash = sha256_bytes(canonical_json(body).encode("utf-8"))
        event = {**body, "event_hash": event_hash}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(canonical_json(event) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.previous_hash = event_hash
        return event

    @staticmethod
    def verify(path: Path) -> tuple[bool, str]:
        previous, expected_sequence = "0" * 64, 1
        try:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip(): continue
                event = json.loads(line)
                if event.get("sequence") != expected_sequence:
                    return False, f"sequence mismatch at line {line_number}"
                if event.get("previous_hash") != previous:
                    return False, f"previous_hash mismatch at line {line_number}"
                recorded_hash = event.pop("event_hash", None)
                computed_hash = sha256_bytes(canonical_json(event).encode("utf-8"))
                if not isinstance(recorded_hash, str) or not hmac.compare_digest(recorded_hash, computed_hash):
                    return False, f"event_hash mismatch at line {line_number}"
                previous, expected_sequence = recorded_hash, expected_sequence + 1
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            return False, f"cannot verify audit log: {exc}"
        return True, previous

def _load_registries():
    return (load_json(CAPABILITIES_PATH), load_json(ROUTES_PATH),
            load_json(POLICY_PATH), load_json(CATALOG_PATH))

def discover_capabilities(include_test: bool = False) -> dict[str, Any]:
    config, _, _, _ = _load_registries()
    actions = []
    with tempfile.TemporaryDirectory(prefix="hso-capability-probe-") as temp:
        probe_root = Path(temp)
        for item in config["capabilities"]:
            cap_id, name = item["capability_id"], item.get("handler")
            test_only = bool(item.get("test_only", False))
            registry = TEST_HANDLERS if test_only else HANDLERS
            status, evidence = "NOT_CONFIGURED", item.get("unavailable_reason")
            if item.get("enabled") and (not test_only or include_test) and name in registry:
                try:
                    expected = (f"hso-probe:{cap_id}\n").encode("utf-8")
                    if name == "verify_sha256":
                        target = _safe_target(probe_root, "probe/target.txt")
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(expected)
                        result = registry[name](probe_root, "probe/target.txt",
                            {"expected_sha256": sha256_bytes(expected)}, {})
                    elif name == "flaky_write_text":
                        args = {"content": expected.decode("utf-8")}
                        context = {"idempotency_key": "probe-" + cap_id}
                        try: registry[name](probe_root, "probe/target.txt", args, context)
                        except RetryableActionError: pass
                        result = registry[name](probe_root, "probe/target.txt", args, context)
                    else:
                        result = registry[name](probe_root, "probe/target.txt",
                            {"content": expected.decode("utf-8")}, {"idempotency_key": "probe-" + cap_id})
                    observed = _safe_target(probe_root, "probe/target.txt").read_bytes()
                    if observed != expected or result.get("sha256", result.get("observed_sha256")) != sha256_bytes(expected):
                        raise RuntimeErrorBase("write/read-back or digest probe did not match")
                    status, evidence = "READY", "live temporary-file action plus independent read-back probe passed"
                except Exception as exc:
                    status, evidence = "UNAVAILABLE", f"runtime probe failed: {type(exc).__name__}: {exc}"
            elif test_only and not include_test:
                status, evidence = "DISABLED_TEST_ONLY", "test adapter excluded from normal runtime discovery"
            actions.append({
                "capability_id": cap_id, "adapter_id": item["adapter_id"], "status": status,
                "handler": name, "test_only": test_only, "evidence": evidence,
                "probed_at": utc_now(), "host": os.environ.get("GITHUB_WORKFLOW", "local-python-runtime"),
                "python": platform.python_version(), "scope": item.get("scope"),
            })
    for cap_id, adapter, scope, evidence in [
        ("plugin.skill.invoke", "host-plugin-bridge", "host_plugin",
         "no verified host plugin-dispatch adapter is installed in this repository runtime"),
        ("mcp.remote.invoke", "remote-mcp", "remote_mcp",
         "no endpoint, authentication provider, egress policy or remote MCP adapter is configured"),
    ]:
        actions.append({"capability_id": cap_id, "adapter_id": adapter, "status": "NOT_CONFIGURED",
            "handler": None, "test_only": False, "evidence": evidence, "probed_at": utc_now(),
            "host": os.environ.get("GITHUB_WORKFLOW", "local-python-runtime"),
            "python": platform.python_version(), "scope": scope})
    return {"schema_version": "1.0.0", "probe_id": "CAP-" + uuid.uuid4().hex,
            "generated_at": utc_now(), "runtime": "HSO_BUILTIN_PYTHON_SANDBOX", "capabilities": actions}

def _plugin_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["plugin_key"]: item for item in catalog.get("plugins", [])}

def resolve_route(task_type: str, routes: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    route = routes.get("task_types", {}).get(task_type)
    if not route: raise PolicyDenied(f"no routing policy is registered for task_type '{task_type}'")
    primary = route.get("primary_owner")
    if not isinstance(primary, str) or not primary.strip():
        raise PolicyDenied(f"route '{task_type}' must resolve exactly one primary owner")
    components, plugins = set(routes.get("control_plane_components", [])), _plugin_index(catalog)
    if primary not in components and primary not in plugins:
        raise PolicyDenied(f"route primary owner '{primary}' is not registered")
    specialists = route.get("supporting_specialists", [])
    if not isinstance(specialists, list) or len(specialists) != len(set(specialists)):
        raise PolicyDenied(f"route '{task_type}' has invalid or duplicate specialists")
    if primary in specialists: raise PolicyDenied("primary owner cannot also be a supporting specialist")
    for specialist in specialists:
        if specialist in components: continue
        if specialist not in plugins: raise PolicyDenied(f"supporting specialist '{specialist}' is not in the catalog")
        if plugins[specialist].get("source_state") == "canonical_redirect":
            raise PolicyDenied(f"supporting specialist '{specialist}' is a legacy redirect")
    return {"task_type": task_type, "primary_owner": primary, "supporting_specialists": specialists,
            "required_capabilities": route.get("required_capabilities", []),
            "action_id": route.get("action_id"), "routing_rule": route.get("rule_id"),
            "invocation_boundary": "ROUTED_BY_HSO; specialist invocation requires a separately configured host adapter"}

def topological_order(packages: list[dict[str, Any]]) -> list[str]:
    by_id = {item["package_id"]: item for item in packages}
    if len(by_id) != len(packages): raise RuntimeErrorBase("duplicate package_id in workflow")
    for item in packages:
        for dep in item["depends_on"]:
            if dep not in by_id: raise RuntimeErrorBase(f"{item['package_id']}: unknown dependency '{dep}'")
            if dep == item["package_id"]: raise RuntimeErrorBase(f"{item['package_id']}: cannot depend on itself")
    index = {item["package_id"]: i for i, item in enumerate(packages)}
    indegree = {item["package_id"]: len(item["depends_on"]) for item in packages}
    children = {key: [] for key in by_id}
    for item in packages:
        for dep in item["depends_on"]: children[dep].append(item["package_id"])
    ready = sorted((key for key, degree in indegree.items() if degree == 0), key=index.get)
    result = []
    while ready:
        current = ready.pop(0); result.append(current)
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child); ready.sort(key=index.get)
    if len(result) != len(packages): raise RuntimeErrorBase("dependency cycle detected in workflow")
    return result

def verify_approval(receipt: dict[str, Any] | None, case_id: str, action_id: str,
                    target_path: str, authority: str) -> None:
    if not isinstance(receipt, dict): raise PolicyDenied("a signed approval receipt is required")
    secret = os.environ.get("HSO_APPROVAL_HMAC_KEY")
    if not secret: raise PolicyDenied("HSO_APPROVAL_HMAC_KEY unavailable; approval cannot be authenticated")
    signature = receipt.get("signature")
    unsigned = {key: value for key, value in receipt.items() if key != "signature"}
    expected = hmac.new(secret.encode(), canonical_json(unsigned).encode(), hashlib.sha256).hexdigest()
    if not isinstance(signature, str) or not hmac.compare_digest(signature, expected):
        raise PolicyDenied("approval receipt signature is invalid")
    if unsigned.get("case_id") != case_id or unsigned.get("action_id") != action_id:
        raise PolicyDenied("approval receipt is not bound to this case and action")
    if unsigned.get("target_path") != target_path or unsigned.get("authority") != authority:
        raise PolicyDenied("approval receipt scope does not match target and authority")
    try:
        issued_at = datetime.fromisoformat(str(unsigned["issued_at"]).replace("Z", "+00:00"))
        expiry = datetime.fromisoformat(str(unsigned["expires_at"]).replace("Z", "+00:00"))
    except (KeyError, ValueError) as exc:
        raise PolicyDenied("approval receipt issued_at/expires_at is missing or invalid") from exc
    now = datetime.now(timezone.utc)
    if issued_at.tzinfo is None or expiry.tzinfo is None:
        raise PolicyDenied("approval receipt timestamps must include a timezone")
    if issued_at > now:
        raise PolicyDenied("approval receipt issue time is in the future")
    if expiry <= now or expiry <= issued_at:
        raise PolicyDenied("approval receipt is expired or has an invalid validity window")
    if (expiry - issued_at).total_seconds() > 900:
        raise PolicyDenied("approval receipt validity window exceeds the 15-minute policy limit")
    if not unsigned.get("approver") or not unsigned.get("nonce"):
        raise PolicyDenied("approval receipt requires approver identity and nonce")

class IdempotencyLedger:
    def __init__(self, path: Path):
        self.path = path; self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS package_runs (
                idempotency_key TEXT PRIMARY KEY, action_digest TEXT NOT NULL,
                status TEXT NOT NULL, receipt_json TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            conn.commit()
    def begin(self, key: str, action_digest: str) -> tuple[str, dict[str, Any] | None]:
        with sqlite3.connect(self.path, timeout=10) as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT action_digest,status,receipt_json FROM package_runs WHERE idempotency_key=?", (key,)).fetchone()
            if row:
                if row[0] != action_digest:
                    conn.rollback(); raise IdempotencyConflict("idempotency key reused with a different action digest")
                receipt = json.loads(row[2] or "{}")
                if row[1] == "SUCCEEDED":
                    conn.commit(); return "EXISTING_SUCCESS", receipt
                if row[1] == "RUNNING":
                    conn.rollback(); raise PolicyDenied("another execution owns this idempotency key")
                if row[1] in {"OUTCOME_UNKNOWN", "PARTIAL_MANUAL_REVIEW", "FAILED_VERIFICATION"}:
                    conn.rollback(); raise PolicyDenied(
                        f"prior status {row[1]} requires manual reconciliation before replay"
                    )
                conn.execute("UPDATE package_runs SET status='RUNNING',updated_at=? WHERE idempotency_key=?", (utc_now(), key))
                conn.commit(); return "RETRY_PRIOR_FAILURE", receipt
            conn.execute("INSERT INTO package_runs VALUES (?,?,'RUNNING','{}',?)", (key, action_digest, utc_now()))
            conn.commit(); return "NEW", None
    def finish(self, key: str, status: str, receipt: dict[str, Any]) -> None:
        with sqlite3.connect(self.path, timeout=10) as conn:
            conn.execute("UPDATE package_runs SET status=?,receipt_json=?,updated_at=? WHERE idempotency_key=?",
                         (status, canonical_json(receipt), utc_now(), key)); conn.commit()

def _policy_check(action_id: str, authority: str, environment: str,
                  package: dict[str, Any], case_id: str, policy: dict[str, Any]) -> dict[str, Any]:
    item = policy.get("actions", {}).get(action_id)
    if not item: raise PolicyDenied(f"action '{action_id}' is not allow-listed; default-deny policy")
    if environment not in item.get("allowed_environments", []):
        raise PolicyDenied(f"action '{action_id}' is not permitted in environment '{environment}'")
    required = item["minimum_authority"]
    if AUTHORITY_RANK.get(authority, -1) < AUTHORITY_RANK[required]:
        raise PolicyDenied(f"authority {authority} is below required {required}")
    if item.get("approval_required"):
        verify_approval(package.get("approval_receipt"), case_id, action_id, package["target_path"], authority)
    if package["max_attempts"] > item["max_attempts"]:
        raise PolicyDenied("requested max_attempts exceeds the action policy limit")
    if package["max_attempts"] > 1 and not item.get("idempotent"):
        raise PolicyDenied("retry is prohibited for a non-idempotent action")
    if item.get("test_only") and os.environ.get("HSO_ENABLE_TEST_ADAPTERS") != "1":
        raise PolicyDenied("test-only adapter is disabled")
    return item

def _verify_target(workspace: Path, package: dict[str, Any]) -> dict[str, Any]:
    target = _safe_target(workspace, package["target_path"])
    if not target.is_file(): raise PermanentActionError("target read-back failed: file is missing")
    actual, expected = sha256_bytes(target.read_bytes()), package["expected_sha256"].lower()
    if not hmac.compare_digest(actual, expected):
        raise PermanentActionError(f"target read-back digest mismatch: expected {expected}, observed {actual}")
    return {"verified": True, "target_path": package["target_path"], "sha256": actual,
            "verification_method": "independent_filesystem_readback_sha256"}

def _rollback_if_created(workspace: Path, package: dict[str, Any], action_result: dict[str, Any]) -> dict[str, Any]:
    if not action_result.get("created"): return {"status": "NOT_NEEDED", "reason": "target not created by this run"}
    target = _safe_target(workspace, package["target_path"])
    if not target.is_file(): return {"status": "ALREADY_ABSENT"}
    actual, expected = sha256_bytes(target.read_bytes()), action_result.get("sha256")
    if not isinstance(expected, str) or not hmac.compare_digest(actual, expected):
        return {"status": "BLOCKED", "reason": "target changed after creation; refusing destructive rollback"}
    target.unlink()
    return {"status": "ROLLED_BACK", "reason": "removed only the exact file created by this run"}

def _validate_workflow(workflow: dict[str, Any]) -> None:
    schema = load_json(SCHEMA_PATH); Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(workflow), key=lambda err: list(err.path))
    if errors:
        first = errors[0]; location = ".".join(str(part) for part in first.path) or "$"
        raise RuntimeErrorBase(f"workflow schema violation at {location}: {first.message}")
    topological_order(workflow["work_packages"])
    keys = [item["idempotency_key"] for item in workflow["work_packages"]]
    if len(keys) != len(set(keys)): raise RuntimeErrorBase("idempotency_key values must be unique within one workflow")
    if workflow["environment"] != "SANDBOX":
        raise PolicyDenied("this runtime only executes in an isolated SANDBOX; staging and production are unavailable")

def execute_workflow(workflow: dict[str, Any], workspace: Path, ledger_path: Path,
                     audit_path: Path, receipt_path: Path, include_test: bool = False) -> dict[str, Any]:
    _validate_workflow(workflow)
    capability_config, route_config, policy, catalog = _load_registries()
    capability_receipt = discover_capabilities(include_test=include_test)
    cap_status = {item["capability_id"]: item["status"] for item in capability_receipt["capabilities"]}
    package_by_id = {item["package_id"]: item for item in workflow["work_packages"]}
    order = topological_order(workflow["work_packages"])
    workspace.mkdir(parents=True, exist_ok=True); workspace = workspace.resolve()
    ledger, run_id = IdempotencyLedger(ledger_path), "RUN-" + uuid.uuid4().hex
    audit = AuditLog(audit_path, run_id)
    audit.emit("RUN_STARTED", authority=workflow["action_authority"], environment=workflow["environment"],
               package_count=len(order), workspace_scope="isolated_workspace")
    outcomes, route_receipts = {}, {}
    for package_id in order:
        package = package_by_id[package_id]
        route = resolve_route(package["task_type"], route_config, catalog); route_receipts[package_id] = route
        audit.emit("ROUTE_SELECTED", package_id, primary_owner=route["primary_owner"],
                   supporting_specialists=route["supporting_specialists"], rule_id=route["routing_rule"])
        failed_deps = [dep for dep in package["depends_on"]
                       if outcomes.get(dep, {}).get("status") not in {"SUCCEEDED", "SKIPPED_IDEMPOTENT"}]
        if failed_deps:
            outcomes[package_id] = {"status": "BLOCKED_DEPENDENCY", "blocked_by": failed_deps}
            audit.emit("PACKAGE_BLOCKED", package_id, reason="DEPENDENCY_NOT_SUCCESSFUL", dependencies=failed_deps); continue
        if route["action_id"] != package["action_id"]:
            outcomes[package_id] = {"status": "REJECTED_ROUTE_ACTION_MISMATCH"}
            audit.emit("PACKAGE_REJECTED", package_id, reason="ROUTE_ACTION_MISMATCH"); continue
        missing = sorted(cap for cap in set(route["required_capabilities"]) if cap_status.get(cap) != "READY")
        if missing:
            outcomes[package_id] = {"status": "BLOCKED_CAPABILITY", "missing_capabilities": missing}
            audit.emit("PACKAGE_BLOCKED", package_id, reason="CAPABILITY_NOT_READY", missing=missing); continue
        try:
            action_policy = _policy_check(package["action_id"], workflow["action_authority"],
                workflow["environment"], package, workflow["case_id"], policy)
        except PolicyDenied as exc:
            outcomes[package_id] = {"status": "REJECTED_POLICY", "reason": str(exc)}
            audit.emit("PACKAGE_REJECTED", package_id, reason=str(exc)); continue
        registry = TEST_HANDLERS if action_policy.get("test_only") else HANDLERS
        handler_name = next((item["handler"] for item in capability_config["capabilities"]
                             if item["capability_id"] == package["action_id"]), None)
        handler = registry.get(handler_name)
        if not handler:
            outcomes[package_id] = {"status": "BLOCKED_ADAPTER", "reason": "trusted handler not registered"}
            audit.emit("PACKAGE_BLOCKED", package_id, reason="HANDLER_NOT_REGISTERED"); continue
        action_digest = digest_json({"action_id": package["action_id"], "target_path": package["target_path"],
                                     "input": package["input"], "expected_sha256": package["expected_sha256"]})
        try: ledger_state, _ = ledger.begin(package["idempotency_key"], action_digest)
        except (PolicyDenied, IdempotencyConflict) as exc:
            outcomes[package_id] = {"status": "BLOCKED_IDEMPOTENCY", "reason": str(exc)}
            audit.emit("PACKAGE_BLOCKED", package_id, reason=str(exc)); continue
        if ledger_state == "EXISTING_SUCCESS":
            try:
                verification = _verify_target(workspace, package)
                outcomes[package_id] = {"status": "SKIPPED_IDEMPOTENT", "verification": verification}
                audit.emit("IDEMPOTENT_REPLAY", package_id, action_digest=action_digest,
                           verification=verification["verification_method"]); continue
            except PermanentActionError as exc:
                ledger.finish(package["idempotency_key"], "OUTCOME_UNKNOWN", {"reason": str(exc)})
                outcomes[package_id] = {"status": "BLOCKED_OUTCOME_UNKNOWN", "reason": str(exc)}
                audit.emit("OUTCOME_UNKNOWN", package_id, reason=str(exc)); continue
        audit.emit("DISPATCH_STARTED", package_id, adapter=action_policy["adapter_id"],
                   action_id=package["action_id"], target_path=package["target_path"],
                   action_digest=action_digest, idempotency_key=package["idempotency_key"])
        action_result, last_error, attempts_used, succeeded = {}, None, 0, False
        for attempt in range(1, package["max_attempts"] + 1):
            attempts_used = attempt; audit.emit("ATTEMPT_STARTED", package_id, attempt=attempt)
            try:
                action_result = handler(workspace, package["target_path"], package["input"],
                    {"idempotency_key": package["idempotency_key"], "case_id": workflow["case_id"]})
                audit.emit("ACTION_RETURNED", package_id, attempt=attempt,
                    target_path=action_result.get("target_path"), output_sha256=action_result.get("sha256"),
                    created=action_result.get("created"))
                succeeded = True; break
            except RetryableActionError as exc:
                last_error = str(exc); audit.emit("ATTEMPT_FAILED", package_id, attempt=attempt,
                    error_class="RETRYABLE", error=last_error)
                if attempt < package["max_attempts"]:
                    audit.emit("RETRY_SCHEDULED", package_id, next_attempt=attempt + 1,
                               delay_seconds=RETRY_DELAY_SECONDS); time.sleep(RETRY_DELAY_SECONDS)
            except (PermanentActionError, OSError) as exc:
                last_error = str(exc); audit.emit("ATTEMPT_FAILED", package_id, attempt=attempt,
                    error_class="PERMANENT", error=last_error); break
            except Exception as exc:
                last_error = f"unexpected handler error: {type(exc).__name__}: {exc}"
                audit.emit("ATTEMPT_FAILED", package_id, attempt=attempt, error_class="UNEXPECTED",
                           error=last_error); break
        if succeeded:
            try:
                verification = _verify_target(workspace, package)
                outcomes[package_id] = {"status": "SUCCEEDED", "attempts": attempts_used,
                    "action_result": action_result, "verification": verification, "route": route}
                ledger.finish(package["idempotency_key"], "SUCCEEDED", {
                    "action_digest": action_digest, "target_path": package["target_path"],
                    "sha256": verification["sha256"], "run_id": run_id})
                audit.emit("TARGET_VERIFIED", package_id, method=verification["verification_method"],
                           observed_sha256=verification["sha256"])
                audit.emit("PACKAGE_SUCCEEDED", package_id, attempts=attempts_used)
            except PermanentActionError as exc:
                rollback = {"status": "NOT_REQUESTED"}
                if package["recovery"]["on_verification_failure"] == "ROLLBACK_IF_CREATED":
                    rollback = _rollback_if_created(workspace, package, action_result)
                    audit.emit("COMPENSATION_FINISHED", package_id, **rollback)
                status = "FAILED_VERIFICATION" if rollback["status"] != "BLOCKED" else "PARTIAL_MANUAL_REVIEW"
                outcomes[package_id] = {"status": status, "attempts": attempts_used, "reason": str(exc), "recovery": rollback}
                ledger.finish(package["idempotency_key"], status, {"reason": str(exc), "recovery": rollback})
                audit.emit("TARGET_VERIFICATION_FAILED", package_id, reason=str(exc))
        else:
            rollback = {"status": "NOT_NEEDED"}
            if package["recovery"]["on_action_failure"] == "ROLLBACK_IF_CREATED" and action_result:
                rollback = _rollback_if_created(workspace, package, action_result)
                audit.emit("COMPENSATION_FINISHED", package_id, **rollback)
            status = "FAILED" if rollback["status"] != "BLOCKED" else "PARTIAL_MANUAL_REVIEW"
            outcomes[package_id] = {"status": status, "attempts": attempts_used, "reason": last_error, "recovery": rollback}
            ledger.finish(package["idempotency_key"], status, {"reason": last_error, "recovery": rollback})
            audit.emit("PACKAGE_FAILED", package_id, attempts=attempts_used, reason=last_error)
    states = [item["status"] for item in outcomes.values()]
    overall = ("SUCCEEDED" if states and all(s in {"SUCCEEDED", "SKIPPED_IDEMPOTENT"} for s in states)
               else "PARTIAL" if any(s in {"SUCCEEDED", "SKIPPED_IDEMPOTENT"} for s in states) else "FAILED")
    valid, audit_head = AuditLog.verify(audit_path)
    receipt = {
        "schema_version": "1.0.0", "run_id": run_id, "case_id": workflow["case_id"],
        "status": overall, "environment": workflow["environment"], "authority": workflow["action_authority"],
        "planned_order": order, "capability_receipt": capability_receipt, "routes": route_receipts,
        "package_outcomes": outcomes,
        "audit": {"path": str(audit_path), "hash_chain_valid": valid, "event_count": audit.sequence,
                  "head_sha256": audit_head, "tamper_evidence": "HASH_CHAIN_ONLY_UNSIGNED"},
        "runtime_boundary": {"actual_dispatch": "BUILTIN_PYTHON_SANDBOX_HANDLER",
            "target_verification": "INDEPENDENT_FILESYSTEM_READBACK", "plugin_skill_invocation": "NOT_PERFORMED",
            "remote_mcp_invocation": "NOT_CONFIGURED", "production_execution": "NOT_SUPPORTED"}}
    audit.emit("RUN_FINISHED", status=overall, audit_chain_verified=valid,
               successful_packages=sum(s in {"SUCCEEDED", "SKIPPED_IDEMPOTENT"} for s in states),
               total_packages=len(states))
    valid, audit_head = AuditLog.verify(audit_path)
    receipt["audit"].update({"hash_chain_valid": valid, "event_count": audit.sequence, "head_sha256": audit_head})
    write_json(receipt_path, receipt)
    if not valid: raise RuntimeErrorBase("audit chain failed self-verification")
    return receipt

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HSO supervised sandbox runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("discover"); p.add_argument("--output", type=Path, required=True); p.add_argument("--include-test", action="store_true")
    p = sub.add_parser("run"); p.add_argument("workflow", type=Path); p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True); p.add_argument("--audit", type=Path, required=True); p.add_argument("--receipt", type=Path, required=True)
    p = sub.add_parser("verify-audit"); p.add_argument("audit", type=Path)
    p = sub.add_parser("route"); p.add_argument("task_type")
    args = parser.parse_args(argv)
    try:
        if args.command == "discover":
            receipt = discover_capabilities(args.include_test); write_json(args.output, receipt)
            print(json.dumps({"probe_id": receipt["probe_id"], "capabilities": receipt["capabilities"]}, indent=2)); return 0
        if args.command == "run":
            receipt = execute_workflow(load_json(args.workflow), args.workspace, args.ledger, args.audit, args.receipt,
                                       include_test=os.environ.get("HSO_ENABLE_TEST_ADAPTERS") == "1")
            print(json.dumps({"run_id": receipt["run_id"], "status": receipt["status"],
                "planned_order": receipt["planned_order"], "package_outcomes": receipt["package_outcomes"],
                "audit": receipt["audit"]}, indent=2))
            return 0 if receipt["status"] == "SUCCEEDED" else 1
        if args.command == "verify-audit":
            valid, head = AuditLog.verify(args.audit); print(json.dumps({"valid": valid, "head_sha256": head}, indent=2))
            return 0 if valid else 1
        if args.command == "route":
            _, routes, _, catalog = _load_registries()
            print(json.dumps(resolve_route(args.task_type, routes, catalog), indent=2)); return 0
    except (RuntimeErrorBase, PolicyDenied, IdempotencyConflict, OSError, ValueError) as exc:
        print(f"HSO_RUNTIME_ERROR: {exc}", file=sys.stderr); return 2
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
