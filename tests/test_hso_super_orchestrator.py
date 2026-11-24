"""Regression tests for the supervised HSO runtime and its safety boundaries."""
from __future__ import annotations
import copy, json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from tools import hso_super_orchestrator as hso

ROOT = Path(__file__).resolve().parents[1]
NORMAL = ROOT / "examples" / "hso-runtime-execution.example.json"
RECOVERY = ROOT / "examples" / "hso-runtime-recovery.example.json"

class HsoRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.ledger = self.root / "ledger.sqlite"
        self.audit = self.root / "audit.jsonl"
        self.receipt = self.root / "receipt.json"

    def tearDown(self):
        self.temp.cleanup()

    def workflow(self, path=NORMAL):
        return json.loads(path.read_text(encoding="utf-8"))

    def run_workflow(self, data, **kwargs):
        return hso.execute_workflow(data, self.workspace, self.ledger, self.audit,
                                    self.receipt, **kwargs)

    def test_capability_registry_cannot_alias_untrusted_adapter(self):
        registry = json.loads(hso.CAPABILITIES_PATH.read_text(encoding="utf-8"))
        entry = next(item for item in registry["capabilities"] if item["capability_id"] == "sandbox.write_text")
        entry["adapter_id"] = "attacker.untrusted"
        modified = self.root / "modified-capabilities.json"
        modified.write_text(json.dumps(registry), encoding="utf-8")
        with patch.object(hso, "CAPABILITIES_PATH", modified):
            result = hso.discover_capabilities()
        status = next(item["status"] for item in result["capabilities"]
                      if item["capability_id"] == "sandbox.write_text")
        self.assertEqual(status, "UNAVAILABLE")

    def test_valid_scoped_approval_receipt_is_accepted_and_wrong_scope_rejected(self):
        import datetime, hashlib, hmac
        now = datetime.datetime.now(datetime.timezone.utc)
        unsigned = {
            "case_id":"CASE-VALID", "action_id":"approved.action", "target_path":"safe/target.txt",
            "authority":"S4", "approver":"reviewer@example.test", "nonce":"single-use-test-nonce",
            "issued_at":(now-datetime.timedelta(seconds=5)).isoformat(),
            "expires_at":(now+datetime.timedelta(minutes=5)).isoformat()
        }
        secret = "unit-test-approval-key"
        signature = hmac.new(secret.encode(), hso.canonical_json(unsigned).encode(), hashlib.sha256).hexdigest()
        receipt = {**unsigned, "signature":signature}
        with patch.dict(os.environ, {"HSO_APPROVAL_HMAC_KEY":secret}):
            hso.verify_approval(receipt, "CASE-VALID", "approved.action", "safe/target.txt", "S4")
            with self.assertRaisesRegex(hso.PolicyDenied, "scope"):
                hso.verify_approval(receipt, "CASE-VALID", "approved.action", "other/target.txt", "S4")

    def test_live_capability_discovery_only_marks_probed_adapters_ready(self):
        with patch.dict(os.environ, {}, clear=True):
            result = hso.discover_capabilities()
        states = {item["capability_id"]: item["status"] for item in result["capabilities"]}
        self.assertEqual(states["sandbox.write_text"], "READY")
        self.assertEqual(states["sandbox.verify_sha256"], "READY")
        self.assertEqual(states["test.flaky_write_text"], "DISABLED_TEST_ONLY")
        self.assertEqual(states["plugin.skill.invoke"], "NOT_CONFIGURED")
        self.assertEqual(states["mcp.remote.invoke"], "NOT_CONFIGURED")
        self.assertEqual(states["plugin.skill.invoke.remote-mcp.skill-analyzer"], "NOT_CONFIGURED")

    def test_route_has_exactly_one_primary_owner_and_minimal_specialist(self):
        _, routes, _, catalog = hso._load_registries()
        route = hso.resolve_route("artifact.create", routes, catalog)
        self.assertEqual(route["primary_owner"], "HSO.CP-05")
        self.assertEqual(route["supporting_specialists"], ["HSO.CP-07"])

    def test_ponytail_engineering_route_has_single_owner_and_bounded_support(self):
        _, routes, _, catalog = hso._load_registries()
        route = hso.resolve_route("plugin.engineering_method", routes, catalog)
        self.assertEqual(route["primary_owner"], "ponytail-engineering-optimizer")
        self.assertEqual(route["supporting_specialists"], ["skill-developer-orchestrator", "evaluator-team"])

    def test_ponytail_route_is_blocked_until_plugin_host_adapter_exists(self):
        data = self.workflow()
        item = data["work_packages"][0]
        item["task_type"] = "plugin.engineering_method"
        item["action_id"] = "plugin.skill.invoke"
        result = self.run_workflow(data)
        self.assertEqual(result["package_outcomes"][item["package_id"]]["status"], "BLOCKED_CAPABILITY")
        self.assertNotEqual(result["status"], "SUCCEEDED")

    def test_plugin_route_is_selected_but_not_dispatchable_without_host_adapter(self):
        _, routes, catalog_policy, catalog = hso._load_registries()
        route = hso.resolve_route("plugin.forensic_audit", routes, catalog)
        self.assertEqual(route["primary_owner"], "skill-analyzer")
        self.assertEqual(route["supporting_specialists"], ["asfree-canonical"])
        states = {item["capability_id"]: item["status"] for item in hso.discover_capabilities()["capabilities"]}
        self.assertNotEqual(states["plugin.skill.invoke"], "READY")

    def test_stable_topological_order_and_cycle_rejection(self):
        packages = [
            {"package_id":"C","depends_on":["A"]},
            {"package_id":"B","depends_on":[]},
            {"package_id":"A","depends_on":[]}
        ]
        self.assertEqual(hso.topological_order(packages), ["B", "A", "C"])
        with self.assertRaisesRegex(hso.RuntimeErrorBase, "cycle"):
            hso.topological_order([
                {"package_id":"A","depends_on":["B"]},
                {"package_id":"B","depends_on":["A"]}
            ])

    def test_duplicate_idempotency_keys_rejected(self):
        data = self.workflow()
        data["work_packages"].append(copy.deepcopy(data["work_packages"][0]))
        data["work_packages"][-1]["package_id"] = "WP-ARTIFACT-002"
        with self.assertRaisesRegex(hso.RuntimeErrorBase, "idempotency_key values must be unique"):
            hso._validate_workflow(data)

    def test_actual_sandbox_dispatch_and_independent_target_verification(self):
        result = self.run_workflow(self.workflow())
        target = self.workspace / "artifacts" / "runtime-proof.txt"
        self.assertEqual(result["status"], "SUCCEEDED")
        self.assertEqual(target.read_text(encoding="utf-8"), "Hypersystem Orchestrator runtime proof v1\n")
        outcome = result["package_outcomes"]["WP-ARTIFACT-CREATE"]
        self.assertEqual(outcome["status"], "SUCCEEDED")
        self.assertTrue(outcome["verification"]["verified"])
        self.assertEqual(outcome["verification"]["verification_method"], "independent_filesystem_readback_sha256")
        self.assertEqual(result["planned_order"], ["WP-ARTIFACT-CREATE", "WP-ARTIFACT-VERIFY"])
        self.assertEqual(result["package_outcomes"]["WP-ARTIFACT-VERIFY"]["status"], "SUCCEEDED")
        self.assertEqual(result["package_outcomes"]["WP-ARTIFACT-VERIFY"]["route"]["primary_owner"], "HSO.CP-07")

    def test_idempotent_replay_rechecks_target_before_skipping(self):
        data = self.workflow()
        first = self.run_workflow(data)
        second = self.run_workflow(data)
        self.assertEqual(first["status"], "SUCCEEDED")
        self.assertEqual(second["package_outcomes"]["WP-ARTIFACT-CREATE"]["status"], "SKIPPED_IDEMPOTENT")
        self.assertEqual(second["package_outcomes"]["WP-ARTIFACT-VERIFY"]["status"], "SKIPPED_IDEMPOTENT")
        valid, _ = hso.AuditLog.verify(self.audit)
        self.assertTrue(valid)

    def test_reuse_of_idempotency_key_with_different_payload_is_blocked(self):
        data = self.workflow()
        self.run_workflow(data)
        changed = self.workflow()
        changed["work_packages"][0]["input"]["content"] = "different target\n"
        changed["work_packages"][0]["expected_sha256"] = hso.sha256_bytes(b"different target\n")
        result = self.run_workflow(changed)
        self.assertEqual(result["package_outcomes"]["WP-ARTIFACT-CREATE"]["status"], "BLOCKED_IDEMPOTENCY")

    def test_retry_and_recovery_after_injected_transient_failure(self):
        data = self.workflow(RECOVERY)
        with patch.dict(os.environ, {"HSO_ENABLE_TEST_ADAPTERS":"1"}):
            result = self.run_workflow(data, include_test=True)
        outcome = result["package_outcomes"]["WP-RECOVERY-001"]
        self.assertEqual(result["status"], "SUCCEEDED", result["package_outcomes"])
        self.assertEqual(outcome["attempts"], 2)
        events = [json.loads(line)["event_type"] for line in self.audit.read_text(encoding="utf-8").splitlines()]
        self.assertIn("RETRY_SCHEDULED", events)
        self.assertIn("TARGET_VERIFIED", events)

    def test_failed_target_verification_compensates_only_created_file(self):
        data = self.workflow()
        data["work_packages"][0]["expected_sha256"] = "0" * 64
        result = self.run_workflow(data)
        outcome = result["package_outcomes"]["WP-ARTIFACT-CREATE"]
        self.assertEqual(outcome["status"], "FAILED_VERIFICATION")
        self.assertEqual(outcome["recovery"]["status"], "ROLLED_BACK")
        self.assertFalse((self.workspace / "artifacts" / "runtime-proof.txt").exists())

    def test_symlink_target_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        link = self.workspace / "linked"
        self.workspace.mkdir(parents=True)
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are unavailable on this platform")
        with self.assertRaisesRegex(hso.PermanentActionError, "symbolic link"):
            hso._safe_target(self.workspace, "linked/escape.txt")

    def test_path_traversal_is_rejected(self):
        with self.assertRaisesRegex(hso.PermanentActionError, "relative"):
            hso._safe_target(self.workspace, "../escape.txt")

    def test_different_existing_file_is_not_overwritten(self):
        self.workspace.mkdir()
        target = self.workspace / "existing.txt"
        target.write_text("protected\n", encoding="utf-8")
        with self.assertRaisesRegex(hso.PermanentActionError, "refusing to overwrite"):
            hso._write_text(self.workspace, "existing.txt", {"content":"overwrite\n"}, {})

    def test_insufficient_authority_is_denied(self):
        _, _, policy, _ = hso._load_registries()
        with self.assertRaisesRegex(hso.PolicyDenied, "below required S3"):
            hso._policy_check("sandbox.write_text", "S2", "SANDBOX",
                {"max_attempts":1,"target_path":"x.txt"}, "CASE-1", policy)

    def test_staging_and_production_are_not_enabled(self):
        data = self.workflow()
        data["environment"] = "PRODUCTION"
        with self.assertRaisesRegex(hso.PolicyDenied, "only executes in an isolated SANDBOX"):
            hso._validate_workflow(data)

    def test_unknown_actions_are_denied_by_default_policy(self):
        _, _, policy, _ = hso._load_registries()
        with self.assertRaisesRegex(hso.PolicyDenied, "default-deny"):
            hso._policy_check("external.http.post", "S5", "PRODUCTION",
                {"max_attempts":1,"target_path":"x"}, "CASE-1", policy)

    def test_approval_rejects_future_issue_time_and_long_validity(self):
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        unsigned = {
            "case_id": "CASE-1", "action_id": "external.action", "target_path": "x",
            "authority": "S4", "approver": "reviewer", "nonce": "N-1",
            "issued_at": (now + datetime.timedelta(minutes=1)).isoformat(),
            "expires_at": (now + datetime.timedelta(minutes=2)).isoformat()
        }
        secret = "unit-test-only-secret"
        import hashlib, hmac
        signature = hmac.new(secret.encode(), hso.canonical_json(unsigned).encode(), hashlib.sha256).hexdigest()
        with patch.dict(os.environ, {"HSO_APPROVAL_HMAC_KEY": secret}):
            with self.assertRaisesRegex(hso.PolicyDenied, "future"):
                hso.verify_approval({**unsigned, "signature":signature}, "CASE-1", "external.action", "x", "S4")
            unsigned["issued_at"] = now.isoformat()
            unsigned["expires_at"] = (now + datetime.timedelta(hours=1)).isoformat()
            signature = hmac.new(secret.encode(), hso.canonical_json(unsigned).encode(), hashlib.sha256).hexdigest()
            with self.assertRaisesRegex(hso.PolicyDenied, "15-minute"):
                hso.verify_approval({**unsigned, "signature":signature}, "CASE-1", "external.action", "x", "S4")

    def test_unknown_outcome_requires_manual_reconciliation_before_retry(self):
        ledger = hso.IdempotencyLedger(self.ledger)
        state, _ = ledger.begin("manual-reconcile-key", "action-digest")
        self.assertEqual(state, "NEW")
        ledger.finish("manual-reconcile-key", "OUTCOME_UNKNOWN", {"reason":"uncertain target"})
        with self.assertRaisesRegex(hso.PolicyDenied, "manual reconciliation"):
            ledger.begin("manual-reconcile-key", "action-digest")

    def test_approval_fails_closed_without_receipt_or_secret(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(hso.PolicyDenied, "signed approval receipt"):
                hso.verify_approval(None, "CASE-1", "external.action", "x", "S4")

    def test_audit_chain_detects_tampering(self):
        result = self.run_workflow(self.workflow())
        valid, _ = hso.AuditLog.verify(self.audit)
        self.assertTrue(valid)
        lines = self.audit.read_text(encoding="utf-8").splitlines()
        event = json.loads(lines[0])
        event["details"]["environment"] = "PRODUCTION"
        lines[0] = hso.canonical_json(event)
        self.audit.write_text("\n".join(lines) + "\n", encoding="utf-8")
        valid, detail = hso.AuditLog.verify(self.audit)
        self.assertFalse(valid)
        self.assertIn("event_hash mismatch", detail)

    def test_audit_redacts_secret_like_fields(self):
        log = hso.AuditLog(self.audit, "RUN-REDACT")
        log.emit("TEST", api_key="do-not-store", ordinary="kept")
        event = json.loads(self.audit.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(event["details"]["api_key"], "[REDACTED]")
        self.assertEqual(event["details"]["ordinary"], "kept")


    def _p0_approval_receipt(self, secret="p0-test-approval-key-with-enough-entropy"):
        import datetime, hashlib, hmac
        from tools import remote_mcp_responses_adapter as adapter
        now = datetime.datetime.now(datetime.timezone.utc)
        data = json.loads((ROOT / "examples" / "hso-p0-skill-invocation-request.json").read_text(encoding="utf-8"))
        package = data["work_packages"][0]
        payload = dict(package["input"])
        payload["skill_sha256"] = "a" * 64
        arguments = adapter._expected_arguments(payload)
        unsigned = {
            "case_id": data["case_id"],
            "action_id": package["action_id"],
            "target_path": package["target_path"],
            "authority": data["action_authority"],
            "approver": "hsaidno-cpu",
            "issued_at": now.isoformat(),
            "expires_at": (now + datetime.timedelta(minutes=5)).isoformat(),
            "nonce": "p0-remote-mcp-test-nonce",
            "workflow_run_id": "test-run-001",
            "workflow_run_attempt": "1",
            "host": adapter.HOST_ID,
            "mcp_server_label": adapter.SERVER_LABEL,
            "mcp_tool_name": adapter.TOOL_NAME,
            "mcp_server_url_sha256": hashlib.sha256(b"https://gateway.example.com/mcp").hexdigest(),
            "tool_arguments_sha256": adapter.sha256_json(arguments),
            "plugin_source_commit": adapter.SOURCE_PIN,
            "skill_sha256": "a" * 64,
        }
        signature = hmac.new(secret.encode(), hso.canonical_json(unsigned).encode(), hashlib.sha256).hexdigest()
        return {**unsigned, "signature": signature}, secret

    def _p0_workflow(self):
        path = ROOT / "examples" / "hso-p0-skill-invocation-request.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        approval, _ = self._p0_approval_receipt()
        package = data["work_packages"][0]
        package["input"]["skill_sha256"] = approval["skill_sha256"]
        package["approval_receipt"] = approval
        return data

    def _p0_preflight(self):
        return {
            "status": "READY_WITH_LIMITATIONS",
            "host": "openai-responses-api",
            "evidence": "fake zero-inference fixture",
            "server_label": "skill_analyzer_internal",
            "tool_name": "invoke_skill_analyzer",
            "allowed_tools": ["invoke_skill_analyzer"],
            "billable_inference_performed": False,
        }

    def test_p0_route_has_one_owner_and_one_remote_mcp_capability(self):
        _, routes, _, catalog = hso._load_registries()
        route = hso.resolve_route("plugin.skill_analyzer_p0_pilot", routes, catalog)
        self.assertEqual(route["primary_owner"], "skill-analyzer")
        self.assertEqual(route["supporting_specialists"], [])
        self.assertEqual(route["action_id"], "plugin.skill.invoke.remote-mcp.skill-analyzer")
        self.assertEqual(route["required_capabilities"], ["plugin.skill.invoke.remote-mcp.skill-analyzer"])

    def test_p0_zero_inference_preflight_remains_distinct_from_live_invocation(self):
        with patch.dict(os.environ, {}, clear=True):
            result = hso.discover_capabilities()
        capability = next(item for item in result["capabilities"]
                          if item["capability_id"] == "plugin.skill.invoke.remote-mcp.skill-analyzer")
        self.assertEqual(capability["status"], "NOT_CONFIGURED")
        self.assertEqual(capability["handler"], "remote_mcp_skill_invoke")
        self.assertEqual(capability["adapter_id"], "builtin.openai.responses-remote-mcp")
        self.assertNotEqual(capability["status"], "READY")

    def test_p0_approval_receipt_cannot_be_replayed_in_a_different_workflow_run(self):
        receipt, secret = self._p0_approval_receipt()
        with patch.dict(os.environ, {
            "HSO_APPROVAL_HMAC_KEY": secret,
            "GITHUB_RUN_ID": "different-run",
            "GITHUB_RUN_ATTEMPT": "1",
        }, clear=True):
            with self.assertRaisesRegex(hso.PolicyDenied, "exact workflow run"):
                hso.verify_approval(
                    receipt,
                    "HSO-P0-SKILL-ANALYZER-001",
                    "plugin.skill.invoke.remote-mcp.skill-analyzer",
                    "artifacts/p0-skill-analyzer-invocation.json",
                    "S4",
                )

    def test_p0_runtime_dispatch_receipt_and_independent_target_readback(self):
        data = self._p0_workflow()
        secret = "p0-test-approval-key-with-enough-entropy"
        invocations = []
        def fake_invoke(workspace, target_path, payload, context):
            from tools import remote_mcp_responses_adapter as adapter
            self.assertTrue(context["approval_verified"])
            self.assertEqual(context["approval_receipt"]["tool_arguments_sha256"], adapter.sha256_json(adapter._expected_arguments(payload)))
            self.assertEqual(context["approval_receipt"]["mcp_tool_name"], "invoke_skill_analyzer")
            invocations.append(context["case_id"])
            artifact = {
                "invocation_receipt": {
                    "host": "openai-responses-api",
                    "plugin": {
                        "source_commit": adapter.SOURCE_PIN,
                        "skill_sha256": payload["skill_sha256"],
                        "remote_source_attestation": "NOT_EXPOSED_BY_CURRENT_GATEWAY",
                    },
                    "remote_mcp": {
                        "server_label": "skill_analyzer_internal",
                        "tool_name": "invoke_skill_analyzer",
                        "allowed_tools": ["invoke_skill_analyzer"],
                    },
                    "host_session": {
                        "initial_response_id": "resp-initial-test",
                        "final_response_id": "resp-final-test",
                        "approval_request_id": "mcpr-approval-test",
                        "mcp_call_id": "mcp-call-test",
                    },
                    "verification": {
                        "mcp_call_completed": True,
                        "gateway_result_contract_valid": True,
                        "remote_source_attestation": "NOT_EXPOSED_BY_CURRENT_GATEWAY",
                    },
                },
                "analysis_result": {"result": "synthetic test result"},
            }
            target = hso._safe_target(workspace, target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            with target.open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            return {
                "target_path": target_path,
                "sha256": hso.sha256_bytes(raw),
                "created": True,
                "no_op": False,
                "host_response_id": "resp-final-test",
                "mcp_call_id": "mcp-call-test",
                "approval_request_id": "mcpr-approval-test",
            }

        with patch.dict(os.environ, {
            "HSO_APPROVAL_HMAC_KEY": secret,
            "GITHUB_RUN_ID": "test-run-001",
            "GITHUB_RUN_ATTEMPT": "1",
        }, clear=True):
            with patch.object(hso.remote_mcp_responses_adapter, "probe_remote_mcp_host",
                              return_value=self._p0_preflight()):
                with patch.object(hso.remote_mcp_responses_adapter, "invoke_remote_mcp_skill",
                                  side_effect=fake_invoke):
                    result = self.run_workflow(data)

        package = result["package_outcomes"]["WP-P0-SKILL-ANALYZER-INVOKE"]
        self.assertEqual(result["status"], "SUCCEEDED", result["package_outcomes"])
        self.assertEqual(package["status"], "SUCCEEDED")
        self.assertEqual(package["route"]["primary_owner"], "skill-analyzer")
        self.assertEqual(package["route"]["supporting_specialists"], [])
        self.assertEqual(package["verification"]["verification_method"], "independent_filesystem_readback_sha256")
        self.assertEqual(package["verification"]["sha256"], package["action_result"]["sha256"])
        self.assertEqual(invocations, ["HSO-P0-SKILL-ANALYZER-001"])
        artifact_path = self.workspace / "artifacts" / "p0-skill-analyzer-invocation.json"
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        receipt = artifact["invocation_receipt"]
        self.assertEqual(receipt["host"], "openai-responses-api")
        self.assertEqual(receipt["host_session"]["mcp_call_id"], "mcp-call-test")
        self.assertEqual(receipt["verification"]["remote_source_attestation"], "NOT_EXPOSED_BY_CURRENT_GATEWAY")
        self.assertTrue(result["audit"]["hash_chain_valid"])

    def test_p0_ambiguous_post_dispatch_failure_is_outcome_unknown_and_never_replayed(self):
        data = self._p0_workflow()
        secret = "p0-test-approval-key-with-enough-entropy"
        invocation_count = []
        def uncertain(*args, **kwargs):
            invocation_count.append("attempt")
            raise TimeoutError("ambiguous post-dispatch response timeout")
        with patch.dict(os.environ, {
            "HSO_APPROVAL_HMAC_KEY": secret,
            "GITHUB_RUN_ID": "test-run-001",
            "GITHUB_RUN_ATTEMPT": "1",
        }, clear=True):
            with patch.object(hso.remote_mcp_responses_adapter, "probe_remote_mcp_host",
                              return_value=self._p0_preflight()):
                with patch.object(hso.remote_mcp_responses_adapter, "invoke_remote_mcp_skill", side_effect=uncertain):
                    first = self.run_workflow(data)
                    second = self.run_workflow(data)
        self.assertEqual(first["package_outcomes"]["WP-P0-SKILL-ANALYZER-INVOKE"]["status"], "OUTCOME_UNKNOWN")
        self.assertEqual(second["package_outcomes"]["WP-P0-SKILL-ANALYZER-INVOKE"]["status"], "BLOCKED_IDEMPOTENCY")
        self.assertEqual(len(invocation_count), 1)

    def test_p0_invalid_scope_bound_approval_blocks_before_dispatch(self):
        data = self._p0_workflow()
        data["work_packages"][0]["approval_receipt"]["signature"] = "0" * 64
        secret = "p0-test-approval-key-with-enough-entropy"
        with patch.dict(os.environ, {
            "HSO_APPROVAL_HMAC_KEY": secret,
            "GITHUB_RUN_ID": "test-run-001",
            "GITHUB_RUN_ATTEMPT": "1",
        }, clear=True):
            with patch.object(hso.remote_mcp_responses_adapter, "probe_remote_mcp_host",
                              return_value=self._p0_preflight()):
                with patch.object(hso.remote_mcp_responses_adapter, "invoke_remote_mcp_skill") as invoke:
                    result = self.run_workflow(data)
        self.assertEqual(result["package_outcomes"]["WP-P0-SKILL-ANALYZER-INVOKE"]["status"], "REJECTED_POLICY")
        invoke.assert_not_called()

    def test_plugin_route_is_blocked_at_capability_gate(self):
        data = self.workflow()
        item = data["work_packages"][0]
        item["task_type"] = "plugin.forensic_audit"
        item["action_id"] = "plugin.skill.invoke"
        result = self.run_workflow(data)
        self.assertEqual(result["package_outcomes"][item["package_id"]]["status"], "BLOCKED_CAPABILITY")

    def test_ponytail_engineering_route_is_selected_but_blocked_without_host_adapter(self):
        _, routes, _, catalog = hso._load_registries()
        route = hso.resolve_route("plugin.engineering_method", routes, catalog)
        self.assertEqual(route["primary_owner"], "ponytail-engineering-optimizer")
        self.assertEqual(route["supporting_specialists"], ["skill-developer-orchestrator", "evaluator-team"])
        self.assertEqual(route["action_id"], "plugin.skill.invoke")
        self.assertEqual(route["required_capabilities"], ["plugin.skill.invoke"])

        capability_states = {
            item["capability_id"]: item["status"]
            for item in hso.discover_capabilities()["capabilities"]
        }
        self.assertEqual(capability_states["plugin.skill.invoke"], "NOT_CONFIGURED")

        data = self.workflow()
        item = data["work_packages"][0]
        item["task_type"] = "plugin.engineering_method"
        item["action_id"] = "plugin.skill.invoke"
        result = self.run_workflow(data)
        outcome = result["package_outcomes"][item["package_id"]]
        self.assertEqual(outcome["status"], "BLOCKED_CAPABILITY")
        self.assertIn("plugin.skill.invoke", outcome["missing_capabilities"])
        self.assertFalse((self.workspace / item["target_path"]).exists())

if __name__ == "__main__":
    unittest.main()
