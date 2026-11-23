from __future__ import annotations

import argparse
import logging
import time
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select

from .database import build_engine, build_session_factory
from .domain import block_package, claim_next_package, complete_package, fail_package
from .models import Capability, SpecialistAssignment
from .settings import Settings

logger = logging.getLogger("hso.worker")


class RuntimeAdapter(Protocol):
    """Explicitly registered adapter. Do not load executable code from registry metadata."""

    def invoke(self, capability: Capability, package: dict, idempotency_key: str) -> dict:
        ...


@dataclass
class RuntimeBroker:
    adapters: dict[str, RuntimeAdapter]

    def resolve(self, protocol: str) -> RuntimeAdapter | None:
        return self.adapters.get(protocol.upper())


def run_once(session_factory, settings: Settings, worker_id: str, broker: RuntimeBroker) -> bool:
    with session_factory() as session, session.begin():
        package = claim_next_package(session, worker_id, settings)
        if package is None:
            return False

        capability = session.scalar(
            select(Capability)
            .where(
                Capability.plugin_key == package.primary_owner,
                Capability.enabled.is_(True),
                Capability.last_health_status == "C4_PASS",
            )
            .order_by(Capability.created_at.desc())
            .limit(1)
        )
        if capability is None:
            block_package(
                session, package.workflow_id, package.package_id,
                worker_id, "NO_ENABLED_C4_VERIFIED_RUNTIME_CAPABILITY",
            )
            return True

        specialist_rows = session.scalars(
            select(SpecialistAssignment).where(
                SpecialistAssignment.work_package_id == package.id,
                SpecialistAssignment.required.is_(True),
            ).order_by(SpecialistAssignment.plugin_key.asc())
        ).all()
        specialist_capabilities = []
        for assignment in specialist_rows:
            specialist_capability = session.scalar(
                select(Capability).where(
                    Capability.plugin_key == assignment.plugin_key,
                    Capability.enabled.is_(True),
                    Capability.last_health_status == "C4_PASS",
                ).order_by(Capability.created_at.desc()).limit(1)
            )
            if specialist_capability is None:
                block_package(
                    session, package.workflow_id, package.package_id,
                    worker_id, f"SPECIALIST_CAPABILITY_NOT_AVAILABLE:{assignment.plugin_key}",
                )
                return True
            specialist_capabilities.append({
                "plugin_key": assignment.plugin_key,
                "expected_contribution": assignment.expected_contribution,
                "capability_id": specialist_capability.capability_id,
                "capability_key": specialist_capability.capability_key,
                "version": specialist_capability.version,
                "contract_version": specialist_capability.contract_version,
                "protocol": specialist_capability.protocol,
                "endpoint": specialist_capability.endpoint,
                "permission_scopes": specialist_capability.permission_scopes,
            })

        adapter = broker.resolve(capability.protocol)
        if adapter is None:
            block_package(
                session, package.workflow_id, package.package_id,
                worker_id, f"RUNTIME_ADAPTER_NOT_REGISTERED:{capability.protocol}",
            )
            return True

        claimed = {
            "workflow_id": package.workflow_id,
            "package_id": package.package_id,
            "primary_owner": package.primary_owner,
            "supporting_specialists": package.supporting_specialists,
            "expected_output": package.expected_output,
            "acceptance_criteria": package.acceptance_criteria,
            "capability_id": capability.capability_id,
            "capability_key": capability.capability_key,
            "capability_version": capability.version,
            "contract_version": capability.contract_version,
            "permission_scopes": capability.permission_scopes,
            "specialist_capabilities": specialist_capabilities,
        }

    # At-least-once delivery is assumed. The exact same idempotency key is reused
    # across retries; adapters must reject duplicate side effects.
    idempotency_key = f"{claimed['workflow_id']}:{claimed['package_id']}"
    try:
        result = adapter.invoke(capability, claimed, idempotency_key)
        if not isinstance(result, dict):
            raise TypeError("Runtime adapters must return a JSON object")
    except Exception as exc:
        logger.exception("runtime adapter failed for %s", idempotency_key)
        with session_factory() as session, session.begin():
            fail_package(
                session,
                claimed["workflow_id"],
                claimed["package_id"],
                worker_id,
                f"{type(exc).__name__}: {exc}",
            )
        return True

    with session_factory() as session, session.begin():
        complete_package(
            session,
            claimed["workflow_id"],
            claimed["package_id"],
            worker_id,
            result,
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="HSO persistent workflow worker")
    parser.add_argument("--once", action="store_true", help="Claim and process at most one package")
    parser.add_argument("--worker-id", default="hso-worker-local")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    args = parser.parse_args()

    settings = Settings.from_env()
    settings.validate()
    engine = build_engine(settings)
    session_factory = build_session_factory(engine)
    # Deliberately empty. Runtime dispatch stays blocked until a reviewed,
    # host-specific adapter is installed and tested.
    broker = RuntimeBroker(adapters={})
    try:
        if args.once:
            run_once(session_factory, settings, args.worker_id, broker)
            return 0
        while True:
            worked = run_once(session_factory, settings, args.worker_id, broker)
            if not worked:
                time.sleep(max(0.25, min(args.poll_interval, 30.0)))
    except KeyboardInterrupt:
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
