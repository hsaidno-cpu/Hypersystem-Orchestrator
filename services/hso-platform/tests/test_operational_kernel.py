from __future__ import annotations

import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from hso_platform.app import create_app
from hso_platform.domain import (
    DomainError, append_audit, claim_next_package, complete_package,
    create_workflow, register_plugin, verify_audit_chain, verify_package,
)
from hso_platform.models import AuditEvent, AuditHead, Base, Capability, WorkPackage
from hso_platform.settings import Settings


def make_test_database():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session, session.begin():
        if session.get(AuditHead, 1) is None:
            session.add(AuditHead(id=1, last_hash="0" * 64, event_count=0))
    return engine, factory


def plugin_data(key="skill-analyzer", rights="CLEARED"):
    return {
        "plugin_key": key,
        "display_name": key,
        "source_state": "integrated_submodule",
        "source_url": "https://example.com/source.git",
        "source_commit": "a" * 40,
        "execution_rights_status": rights,
        "distribution_rights_status": rights,
        "metadata_json": {},
    }


def add_c4_capability(session, plugin_key, capability_key="test-capability"):
    item = Capability(
        capability_id=f"cap-{plugin_key}",
        plugin_key=plugin_key,
        capability_key=capability_key,
        version="1.0.0",
        contract_version="1.0.0",
        protocol="MCP",
        endpoint="https://mcp.example.test",
        permission_scopes=["capability:invoke"],
        enabled=True,
        evidence_reference="evidence://c4",
        last_health_status="C4_PASS",
        metadata_json={
            "host": "test-host",
            "host_version": "1.0",
            "adapter_version": "1.0",
        },
    )
    session.add(item)
    session.flush()
    return item


def workflow_data(*packages):
    return {
        "case_id": "TEST-CASE",
        "intent": "Test a governed workflow",
        "action_authority": "S3",
        "work_packages": list(packages),
    }


def package_data(package_id="WP-01", *, depends_on=None, capability="READY", specialists=None):
    return {
        "package_id": package_id,
        "primary_owner": "skill-analyzer",
        "supporting_specialists": [item["plugin_key"] for item in (specialists or [])],
        "specialist_contributions": specialists or [],
        "depends_on": depends_on or [],
        "capability_status": capability,
        "capability_evidence": "Verified primary capability evidence",
        "write_scope": "READ_ONLY",
        "requires_approval": False,
        "approval_status": "NOT_REQUIRED",
        "approval_reference": None,
        "expected_output": "A test result",
        "acceptance_criteria": ["Result is traceable"],
        "max_attempts": 3,
    }


class OperationalKernelTests(unittest.TestCase):
    def setUp(self):
        self.engine, self.factory = make_test_database()

    def tearDown(self):
        self.engine.dispose()

    def test_workflow_is_blocked_when_execution_rights_are_not_cleared(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(rights="REVIEW_REQUIRED"), "test")
            workflow = create_workflow(session, workflow_data(package_data()), "test")
            package = session.scalar(
                select(WorkPackage).where(WorkPackage.workflow_id == workflow.workflow_id)
            )
            self.assertEqual(workflow.state, "BLOCKED")
            self.assertEqual(package.state, "BLOCKED")
            self.assertIn("PRIMARY_OWNER_EXECUTION_RIGHTS_NOT_CLEARED", package.blockers)

    def test_workflow_validates_dependency_cycle(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            with self.assertRaises(DomainError):
                create_workflow(
                    session,
                    workflow_data(
                        package_data("WP-01", depends_on=["WP-02"]),
                        package_data("WP-02", depends_on=["WP-01"]),
                    ),
                    "test",
                )

    def test_unknown_dependency_is_rejected(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            with self.assertRaises(DomainError):
                create_workflow(
                    session,
                    workflow_data(package_data(depends_on=["MISSING"])),
                    "test",
                )

    def test_duplicate_package_id_is_rejected(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            with self.assertRaises(DomainError):
                create_workflow(
                    session,
                    workflow_data(package_data(), package_data()),
                    "test",
                )

    def test_supporting_specialist_requires_distinct_contribution_and_readiness(self):
        specialist = {
            "plugin_key": "asfree-canonical",
            "expected_contribution": "Independent technical anatomy dossier",
            "required": True,
            "capability_status": "NOT_CHECKED",
            "capability_evidence": None,
        }
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            register_plugin(
                session,
                {**plugin_data(key="asfree-canonical"), "display_name": "A.S.F.R.E.E"},
                "test",
            )
            workflow = create_workflow(
                session,
                workflow_data(package_data(specialists=[specialist])),
                "test",
            )
            package = session.scalar(
                select(WorkPackage).where(WorkPackage.workflow_id == workflow.workflow_id)
            )
            self.assertEqual(workflow.state, "BLOCKED")
            self.assertTrue(
                any(
                    "SPECIALIST_asfree-canonical_CAPABILITY_NOT_CHECKED" in item
                    for item in package.blockers
                )
            )

    def test_missing_specialist_contribution_contract_is_rejected(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            register_plugin(session, plugin_data(key="asfree-canonical"), "test")
            payload = package_data()
            payload["supporting_specialists"] = ["asfree-canonical"]
            with self.assertRaisesRegex(DomainError, "exactly one contribution contract"):
                create_workflow(session, workflow_data(payload), "test")

    def test_claim_is_blocked_without_c4_host_capability(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            workflow = create_workflow(session, workflow_data(package_data()), "test")
            claimed = claim_next_package(session, "worker-a", Settings(environment="test"))
            self.assertIsNone(claimed)
            package = session.scalar(
                select(WorkPackage).where(WorkPackage.workflow_id == workflow.workflow_id)
            )
            self.assertEqual(package.state, "BLOCKED")
            self.assertIn("NO_ENABLED_C4_VERIFIED_PRIMARY_CAPABILITY", package.blockers)

    def test_output_requires_c5_evidence_and_independent_verification(self):
        with self.factory() as session, session.begin():
            register_plugin(session, plugin_data(), "test")
            add_c4_capability(session, "skill-analyzer")
            workflow = create_workflow(session, workflow_data(package_data()), "test")
            package = claim_next_package(session, "worker-a", Settings(environment="test"))
            self.assertIsNotNone(package)

            with self.assertRaisesRegex(DomainError, "C5 result is missing runtime evidence"):
                complete_package(
                    session,
                    workflow.workflow_id,
                    package.package_id,
                    "worker-a",
                    {"artifact": "result.json"},
                )
            result = complete_package(
                session,
                workflow.workflow_id,
                package.package_id,
                "worker-a",
                {
                    "output_locator": "artifact://result.json",
                    "runtime_trace_reference": "trace://run-001",
                    "host": "test-host",
                    "host_version": "1.0",
                    "adapter_version": "1.0",
                    "artifact": "result.json",
                },
            )
            self.assertEqual(result.state, "AWAITING_VERIFICATION")
            with self.assertRaisesRegex(DomainError, "cannot independently verify"):
                verify_package(
                    session,
                    workflow.workflow_id,
                    package.package_id,
                    "skill-analyzer",
                    "PASS",
                    "evidence://self-review",
                )
            verified = verify_package(
                session,
                workflow.workflow_id,
                package.package_id,
                "independent-reviewer",
                "PASS",
                "evidence://independent-review",
            )
            self.assertEqual(verified.state, "SUCCEEDED")
            self.assertEqual(workflow.state, "COMPLETED")
            self.assertEqual(verified.runtime_trace_reference, "trace://run-001")

    def test_audit_chain_detects_tampering(self):
        with self.factory() as session, session.begin():
            append_audit(session, "test.created", "test", "aggregate-1", {"value": 1})
        with self.factory() as session, session.begin():
            result = verify_audit_chain(session)
            self.assertTrue(result["valid"])
            event = session.scalar(select(AuditEvent))
            event.payload = {"value": 2}
        with self.factory() as session:
            result = verify_audit_chain(session)
            self.assertFalse(result["valid"])

    def test_audit_chain_uses_sequence_not_timestamp_order(self):
        with self.factory() as session, session.begin():
            append_audit(session, "first", "test", "a", {})
            append_audit(session, "second", "test", "b", {})
        with self.factory() as session:
            events = session.scalars(
                select(AuditEvent).order_by(AuditEvent.sequence.asc())
            ).all()
            self.assertEqual([item.sequence for item in events], [1, 2])
            self.assertTrue(verify_audit_chain(session)["valid"])

    def test_app_health_and_registry_use_development_bypass_only_in_test(self):
        settings = Settings(
            environment="test",
            database_url="sqlite+pysqlite://",
            auth_mode="disabled",
        )
        app = create_app(settings, engine=self.engine, session_factory=self.factory)
        with TestClient(app) as client:
            self.assertEqual(client.get("/health/live").status_code, 200)
            self.assertEqual(client.get("/health/ready").status_code, 200)
            response = client.get("/api/v1/registry/plugins")
            self.assertEqual(response.status_code, 200)

    def test_production_settings_reject_disabled_authentication(self):
        settings = Settings(environment="production", auth_mode="disabled")
        with self.assertRaises(ValueError):
            settings.validate()


if __name__ == "__main__":
    unittest.main()
