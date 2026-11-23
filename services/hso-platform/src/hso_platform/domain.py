from __future__ import annotations

import base64
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    APIKey, AuditEvent, AuditHead, Capability, Entitlement, Installation,
    OutboxEvent, PackageRelease, Plugin, SpecialistAssignment, UsageRecord,
    WorkPackage, Workflow, utcnow,
)
from .security import create_api_key
from .settings import Settings


class DomainError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _id() -> str:
    return str(uuid.uuid4())


def _sha256_json(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def append_audit(
    session: Session,
    event_type: str,
    actor: str,
    aggregate_id: str,
    payload: dict[str, Any],
):
    head = session.scalar(
        select(AuditHead).where(AuditHead.id == 1).with_for_update()
    )
    if head is None:
        head = AuditHead(id=1, last_hash="0" * 64, event_count=0)
        session.add(head)
        session.flush()

    event_id = _id()
    body = {
        "event_id": event_id,
        "event_type": event_type,
        "actor": actor,
        "aggregate_id": aggregate_id,
        "payload": payload,
        "previous_hash": head.last_hash,
    }
    digest = _sha256_json(body)
    session.add(AuditEvent(
        event_id=event_id,
        event_type=event_type,
        actor=actor,
        aggregate_id=aggregate_id,
        payload=payload,
        previous_hash=head.last_hash,
        event_hash=digest,
    ))
    head.last_hash = digest
    head.event_count += 1
    session.flush()
    return event_id


def emit_outbox(
    session: Session,
    event_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
):
    event = OutboxEvent(
        event_id=_id(),
        event_type=event_type,
        aggregate_id=aggregate_id,
        payload=payload,
        state="PENDING",
        attempts=0,
        available_at=utcnow(),
    )
    session.add(event)
    return event


def register_plugin(session: Session, data: dict[str, Any], actor: str):
    existing = session.get(Plugin, data["plugin_key"])
    if existing:
        existing.display_name = data["display_name"]
        existing.source_state = data["source_state"]
        existing.source_url = data.get("source_url")
        existing.source_commit = data.get("source_commit")
        existing.execution_rights_status = data.get(
            "execution_rights_status", existing.execution_rights_status
        )
        existing.distribution_rights_status = data.get(
            "distribution_rights_status", existing.distribution_rights_status
        )
        existing.owner_reference = data.get("owner_reference")
        existing.metadata_json = data.get("metadata_json", {})
        plugin = existing
        event_type = "plugin.registry.updated"
    else:
        plugin = Plugin(
            plugin_key=data["plugin_key"],
            display_name=data["display_name"],
            source_state=data["source_state"],
            source_url=data.get("source_url"),
            source_commit=data.get("source_commit"),
            execution_rights_status=data.get("execution_rights_status", "NOT_ASSESSED"),
            distribution_rights_status=data.get("distribution_rights_status", "NOT_ASSESSED"),
            owner_reference=data.get("owner_reference"),
            metadata_json=data.get("metadata_json", {}),
        )
        session.add(plugin)
        event_type = "plugin.registry.created"
    session.flush()
    append_audit(session, event_type, actor, plugin.plugin_key, {
        "source_state": plugin.source_state,
        "source_commit": plugin.source_commit,
        "execution_rights_status": plugin.execution_rights_status,
        "distribution_rights_status": plugin.distribution_rights_status,
    })
    emit_outbox(session, event_type, plugin.plugin_key, {"plugin_key": plugin.plugin_key})
    return plugin


def register_capability(session: Session, plugin_key: str, data: dict[str, Any], actor: str):
    plugin = session.get(Plugin, plugin_key)
    if not plugin:
        raise DomainError(404, "Plugin not found")
    if data["protocol"] not in {"REST", "MCP"}:
        raise DomainError(422, "Capability protocol must be REST or MCP")
    endpoint = data.get("endpoint")
    if not endpoint or not endpoint.startswith("https://"):
        raise DomainError(422, "Remote capability endpoints must use HTTPS")
    capability = Capability(
        capability_id=_id(),
        plugin_key=plugin_key,
        capability_key=data["capability_key"],
        version=data["version"],
        contract_version=data["contract_version"],
        protocol=data["protocol"],
        endpoint=endpoint,
        permission_scopes=sorted(set(data.get("permission_scopes", []))),
        enabled=False,
        evidence_reference=data.get("evidence_reference"),
        last_health_status="NOT_CHECKED",
        metadata_json=data.get("metadata_json", {}),
    )
    session.add(capability)
    session.flush()
    append_audit(session, "capability.registered", actor, capability.capability_id, {
        "plugin_key": plugin_key,
        "protocol": capability.protocol,
        "enabled": False,
        "endpoint_host": endpoint.split("/", 3)[2],
    })
    emit_outbox(session, "capability.registered", capability.capability_id, {
        "plugin_key": plugin_key, "capability_id": capability.capability_id,
    })
    return capability


def _stable_topological_order(packages: list[dict[str, Any]]) -> list[str]:
    ids = [item["package_id"] for item in packages]
    if len(ids) != len(set(ids)):
        raise DomainError(422, "Duplicate package_id")
    package_by_id = {item["package_id"]: item for item in packages}
    for item in packages:
        if item["package_id"] in item["depends_on"]:
            raise DomainError(422, f"{item['package_id']} cannot depend on itself")
        if len(item["depends_on"]) != len(set(item["depends_on"])):
            raise DomainError(422, f"{item['package_id']} contains duplicate dependencies")
        for dependency in item["depends_on"]:
            if dependency not in package_by_id:
                raise DomainError(422, f"{item['package_id']} has unknown dependency {dependency}")
    order: list[str] = []
    pending = list(ids)
    while pending:
        ready = [
            key for key in pending
            if all(dependency in order for dependency in package_by_id[key]["depends_on"])
        ]
        if not ready:
            raise DomainError(422, "Dependency cycle detected")
        for key in ready:
            order.append(key)
            pending.remove(key)
    return order


AUTHORITY_RANK = {f"S{i}": i for i in range(6)}
WRITE_SCOPE_MINIMUM = {
    "READ_ONLY": 0,
    "PARENT_REPOSITORY_BRANCH_WRITE": 3,
    "CHILD_REPOSITORY_CHANGE": 3,
    "EXTERNAL_SIDE_EFFECT": 4,
    "PRODUCTION_RELEASE": 5,
}
MANDATORY_APPROVAL = {
    "CHILD_REPOSITORY_CHANGE", "EXTERNAL_SIDE_EFFECT", "PRODUCTION_RELEASE",
}
CANONICAL_SOURCE_STATES = {"integrated_submodule", "integrated_submodule_private"}


def _source_and_rights_blockers(plugin: Plugin, label: str) -> list[str]:
    blockers: list[str] = []
    if plugin.source_state not in CANONICAL_SOURCE_STATES or not plugin.source_commit:
        blockers.append(f"{label}_CANONICAL_SOURCE_NOT_PINNED")
    if plugin.execution_rights_status != "CLEARED":
        blockers.append(f"{label}_EXECUTION_RIGHTS_NOT_CLEARED")
    return blockers


def create_workflow(
    session: Session,
    data: dict[str, Any],
    actor: str,
    idempotency_key: str | None = None,
):
    if idempotency_key:
        existing = session.scalar(
            select(Workflow).where(Workflow.idempotency_key == idempotency_key)
        )
        if existing:
            return existing

    packages = data["work_packages"]
    order = _stable_topological_order(packages)
    package_map = {item["package_id"]: item for item in packages}
    workflow_id = _id()
    blockers_by_id: dict[str, list[str]] = {}
    records: dict[str, WorkPackage] = {}

    for package_id in order:
        item = package_map[package_id]
        owner_key = item["primary_owner"]
        owner = session.get(Plugin, owner_key)
        if not owner:
            raise DomainError(422, f"Unknown primary owner: {owner_key}")
        if owner.source_state == "canonical_redirect":
            raise DomainError(422, f"Legacy redirect cannot own a work package: {owner_key}")

        contributions = item.get("specialist_contributions", [])
        contribution_keys = [value["plugin_key"] for value in contributions]
        if len(contribution_keys) != len(set(contribution_keys)):
            raise DomainError(422, f"{package_id} has duplicate specialist contribution records")
        if set(contribution_keys) != set(item.get("supporting_specialists", [])):
            raise DomainError(
                422,
                f"{package_id}: each supporting specialist must have exactly one contribution contract",
            )
        if owner_key in contribution_keys:
            raise DomainError(422, "Primary owner cannot also be a supporting specialist")

        blockers = _source_and_rights_blockers(owner, "PRIMARY_OWNER")
        if item["capability_status"] not in {"READY", "READY_WITH_LIMITATIONS"}:
            blockers.append(f"PRIMARY_CAPABILITY_{item['capability_status']}")
        elif not item.get("capability_evidence"):
            blockers.append("PRIMARY_CAPABILITY_EVIDENCE_MISSING")

        write_scope = item["write_scope"]
        if write_scope not in WRITE_SCOPE_MINIMUM:
            raise DomainError(422, f"Unsupported write_scope: {write_scope}")
        if AUTHORITY_RANK[data["action_authority"]] < WRITE_SCOPE_MINIMUM[write_scope]:
            blockers.append("ACTION_AUTHORITY_INSUFFICIENT")
        if write_scope in MANDATORY_APPROVAL and not item["requires_approval"]:
            raise DomainError(422, f"{write_scope} requires explicit approval")
        if item["requires_approval"]:
            if item["approval_status"] != "APPROVED":
                blockers.append(f"APPROVAL_{item['approval_status']}")
            if item["approval_status"] == "APPROVED" and not item.get("approval_reference"):
                raise DomainError(422, "Approved work packages require an approval_reference")
        elif item["approval_status"] != "NOT_REQUIRED":
            raise DomainError(422, "approval_status must be NOT_REQUIRED when approval is false")

        for contribution in contributions:
            specialist_key = contribution["plugin_key"]
            specialist = session.get(Plugin, specialist_key)
            if not specialist:
                raise DomainError(422, f"Unknown supporting specialist: {specialist_key}")
            if specialist.source_state == "canonical_redirect":
                raise DomainError(422, f"Legacy redirect cannot be a specialist: {specialist_key}")
            if not contribution["expected_contribution"].strip():
                raise DomainError(422, f"{specialist_key} must have a distinct expected contribution")
            if contribution["required"]:
                blockers.extend(_source_and_rights_blockers(specialist, f"SPECIALIST_{specialist_key}"))
                if contribution["capability_status"] not in {"READY", "READY_WITH_LIMITATIONS"}:
                    blockers.append(
                        f"SPECIALIST_{specialist_key}_CAPABILITY_{contribution['capability_status']}"
                    )
                elif not contribution.get("capability_evidence"):
                    blockers.append(f"SPECIALIST_{specialist_key}_CAPABILITY_EVIDENCE_MISSING")

        for dependency in item["depends_on"]:
            if blockers_by_id.get(dependency):
                blockers.append(f"DEPENDENCY_BLOCKED:{dependency}")

        # Preserve order but de-duplicate repeated reasons.
        blockers = list(dict.fromkeys(blockers))
        blockers_by_id[package_id] = blockers
        records[package_id] = WorkPackage(
            id=_id(),
            workflow_id=workflow_id,
            package_id=package_id,
            primary_owner=owner_key,
            supporting_specialists=item.get("supporting_specialists", []),
            depends_on=item["depends_on"],
            capability_status=item["capability_status"],
            capability_evidence=item.get("capability_evidence"),
            write_scope=write_scope,
            required_approval=item["requires_approval"],
            approval_status=item["approval_status"],
            approval_reference=item.get("approval_reference"),
            expected_output=item["expected_output"],
            acceptance_criteria=item["acceptance_criteria"],
            state="BLOCKED" if blockers else "PENDING",
            blockers=blockers,
            attempt=0,
            max_attempts=item.get("max_attempts", 4),
        )

    workflow_blocked = any(blockers_by_id.values())
    workflow = Workflow(
        workflow_id=workflow_id,
        case_id=data["case_id"],
        intent=data["intent"],
        state="BLOCKED" if workflow_blocked else "QUEUED",
        action_authority=data["action_authority"],
        created_by=actor,
        idempotency_key=idempotency_key,
    )
    session.add(workflow)
    for package_id in order:
        record = records[package_id]
        session.add(record)
        session.flush()
        for contribution in package_map[package_id].get("specialist_contributions", []):
            session.add(SpecialistAssignment(
                assignment_id=_id(),
                work_package_id=record.id,
                plugin_key=contribution["plugin_key"],
                expected_contribution=contribution["expected_contribution"],
                required=contribution["required"],
                capability_status=contribution["capability_status"],
                capability_evidence=contribution.get("capability_evidence"),
                state="BLOCKED" if contribution["required"] and (
                    contribution["capability_status"] not in {"READY", "READY_WITH_LIMITATIONS"}
                    or not contribution.get("capability_evidence")
                ) else "PENDING",
            ))

    session.flush()
    append_audit(session, "workflow.created", actor, workflow_id, {
        "case_id": data["case_id"],
        "package_count": len(records),
        "blocked_package_count": sum(1 for value in blockers_by_id.values() if value),
        "specialist_assignment_count": sum(
            len(item.get("specialist_contributions", [])) for item in packages
        ),
    })
    emit_outbox(session, "workflow.created", workflow_id, {
        "workflow_id": workflow_id, "state": workflow.state,
    })
    return workflow


def get_workflow(session: Session, workflow_id: str):
    return session.get(Workflow, workflow_id)


def recover_expired_leases(session: Session):
    now = utcnow()
    expired = session.scalars(
        select(WorkPackage)
        .where(
            WorkPackage.state == "RUNNING",
            WorkPackage.lease_expires_at < now,
        )
        .with_for_update(skip_locked=True)
    ).all()
    recovered = 0
    for package in expired:
        old_owner = package.lease_owner or "unknown-worker"
        package.lease_owner = None
        package.lease_expires_at = None
        if package.attempt < package.max_attempts:
            package.state = "PENDING"
            package.run_after = now + timedelta(seconds=min(300, 2 ** package.attempt))
        else:
            package.state = "FAILED"
        append_audit(session, "work_package.lease_expired", "lease-reaper", package.id, {
            "previous_worker": old_owner, "next_state": package.state,
        })
        emit_outbox(session, "work_package.lease_expired", package.id, {
            "workflow_id": package.workflow_id,
            "package_id": package.package_id,
            "next_state": package.state,
        })
        recovered += 1
    return recovered


def claim_next_package(session: Session, worker_id: str, settings: Settings):
    now = utcnow()
    recover_expired_leases(session)
    candidates = session.scalars(
        select(WorkPackage)
        .where(
            WorkPackage.state == "PENDING",
            WorkPackage.run_after <= now,
            WorkPackage.attempt < WorkPackage.max_attempts,
        )
        .order_by(WorkPackage.created_at.asc(), WorkPackage.package_id.asc())
        .with_for_update(skip_locked=True)
        .limit(50)
    ).all()

    for package in candidates:
        dependencies = session.scalars(
            select(WorkPackage).where(
                WorkPackage.workflow_id == package.workflow_id,
                WorkPackage.package_id.in_(package.depends_on or ["__none__"]),
            )
        ).all()
        if any(item.state in {"BLOCKED", "FAILED", "CANCELLED"} for item in dependencies):
            package.state = "BLOCKED"
            package.blockers = ["DEPENDENCY_BLOCKED"]
            continue
        if any(item.state != "SUCCEEDED" for item in dependencies):
            continue

        owner = session.get(Plugin, package.primary_owner)
        if not owner or owner.source_state not in CANONICAL_SOURCE_STATES or not owner.source_commit:
            package.state = "BLOCKED"
            package.blockers = ["CANONICAL_SOURCE_NOT_PINNED"]
            continue
        if owner.execution_rights_status != "CLEARED":
            package.state = "BLOCKED"
            package.blockers = ["EXECUTION_RIGHTS_NOT_CLEARED"]
            continue
        if package.capability_status not in {"READY", "READY_WITH_LIMITATIONS"} or not package.capability_evidence:
            package.state = "BLOCKED"
            package.blockers = ["CAPABILITY_NOT_VERIFIED"]
            continue

        assignments = session.scalars(
            select(SpecialistAssignment).where(
                SpecialistAssignment.work_package_id == package.id,
                SpecialistAssignment.required.is_(True),
            )
        ).all()
        specialist_blockers = []
        for assignment in assignments:
            specialist = session.get(Plugin, assignment.plugin_key)
            if (
                not specialist
                or specialist.source_state not in CANONICAL_SOURCE_STATES
                or not specialist.source_commit
                or specialist.execution_rights_status != "CLEARED"
            ):
                specialist_blockers.append(f"SPECIALIST_NOT_ELIGIBLE:{assignment.plugin_key}")
            if (
                assignment.capability_status not in {"READY", "READY_WITH_LIMITATIONS"}
                or not assignment.capability_evidence
            ):
                specialist_blockers.append(f"SPECIALIST_CAPABILITY_NOT_READY:{assignment.plugin_key}")
        if specialist_blockers:
            package.state = "BLOCKED"
            package.blockers = specialist_blockers
            continue

        package.state = "RUNNING"
        package.attempt += 1
        package.lease_owner = worker_id
        package.lease_expires_at = now + timedelta(seconds=settings.lease_seconds)
        workflow = session.get(Workflow, package.workflow_id)
        if workflow:
            workflow.state = "RUNNING"
        append_audit(session, "work_package.claimed", worker_id, package.id, {
            "workflow_id": package.workflow_id,
            "package_id": package.package_id,
            "attempt": package.attempt,
            "lease_expires_at": package.lease_expires_at.isoformat(),
        })
        emit_outbox(session, "work_package.claimed", package.id, {
            "workflow_id": package.workflow_id, "package_id": package.package_id,
        })
        session.flush()
        return package
    return None


def _assert_lease(package: WorkPackage | None, worker_id: str):
    if not package:
        raise DomainError(404, "Work package not found")
    if package.state != "RUNNING" or package.lease_owner != worker_id:
        raise DomainError(409, "Worker does not own an active package lease")
    if not package.lease_expires_at or package.lease_expires_at <= utcnow():
        raise DomainError(409, "Work package lease expired")


def complete_package(
    session: Session,
    workflow_id: str,
    package_id: str,
    worker_id: str,
    result: dict[str, Any],
):
    package = session.scalar(
        select(WorkPackage).where(
            WorkPackage.workflow_id == workflow_id,
            WorkPackage.package_id == package_id,
        ).with_for_update()
    )
    _assert_lease(package, worker_id)
    package.state = "AWAITING_VERIFICATION"
    package.result_json = result
    package.lease_owner = None
    package.lease_expires_at = None
    append_audit(session, "work_package.output_submitted", worker_id, package.id, {
        "workflow_id": workflow_id,
        "result_keys": sorted(result.keys()),
    })
    emit_outbox(session, "work_package.output_submitted", package.id, {
        "workflow_id": workflow_id, "package_id": package_id,
    })
    session.add(UsageRecord(
        usage_id=_id(),
        subject=worker_id,
        workflow_id=workflow_id,
        event_type="work_package.output_submitted",
        units=1,
        dimensions={"package_id": package_id, "owner": package.primary_owner},
    ))
    workflow = session.get(Workflow, workflow_id)
    if workflow:
        workflow.state = "AWAITING_VERIFICATION"
    session.flush()
    return package


def verify_package(
    session: Session,
    workflow_id: str,
    package_id: str,
    reviewer: str,
    disposition: str,
    evidence_reference: str,
    notes: str | None = None,
):
    package = session.scalar(
        select(WorkPackage).where(
            WorkPackage.workflow_id == workflow_id,
            WorkPackage.package_id == package_id,
        ).with_for_update()
    )
    if not package:
        raise DomainError(404, "Work package not found")
    if package.state != "AWAITING_VERIFICATION":
        raise DomainError(409, "Only AWAITING_VERIFICATION outputs can be reviewed")
    if reviewer == package.primary_owner:
        raise DomainError(403, "The primary owner cannot independently verify its own output")
    if disposition not in {"PASS", "PASS_WITH_CAVEATS", "REJECT"}:
        raise DomainError(422, "Unsupported verification disposition")
    if not evidence_reference.strip():
        raise DomainError(422, "Verification evidence_reference is required")

    package.verification_status = disposition
    package.verification_evidence = evidence_reference
    package.verified_by = reviewer
    package.verification_notes = (notes or "")[:4000]
    if disposition == "REJECT":
        package.state = "FAILED"
    else:
        package.state = "SUCCEEDED"

    remaining = session.scalars(
        select(WorkPackage).where(
            WorkPackage.workflow_id == workflow_id,
            WorkPackage.state.notin_(["SUCCEEDED", "FAILED", "BLOCKED", "CANCELLED"]),
        )
    ).all()
    all_packages = session.scalars(
        select(WorkPackage).where(WorkPackage.workflow_id == workflow_id)
    ).all()
    workflow = session.get(Workflow, workflow_id)
    if workflow:
        if any(item.state == "BLOCKED" for item in all_packages):
            workflow.state = "BLOCKED"
        elif any(item.state == "FAILED" for item in all_packages):
            workflow.state = "PARTIAL"
        elif not remaining:
            workflow.state = "COMPLETED"
        elif any(item.state == "AWAITING_VERIFICATION" for item in all_packages):
            workflow.state = "AWAITING_VERIFICATION"
        else:
            workflow.state = "RUNNING"

    append_audit(session, "work_package.verified", reviewer, package.id, {
        "workflow_id": workflow_id,
        "package_id": package_id,
        "disposition": disposition,
        "verification_evidence": evidence_reference,
    })
    emit_outbox(session, "work_package.verified", package.id, {
        "workflow_id": workflow_id,
        "package_id": package_id,
        "disposition": disposition,
    })
    session.flush()
    return package


def fail_package(
    session: Session,
    workflow_id: str,
    package_id: str,
    worker_id: str,
    error: str,
):
    package = session.scalar(
        select(WorkPackage).where(
            WorkPackage.workflow_id == workflow_id,
            WorkPackage.package_id == package_id,
        ).with_for_update()
    )
    _assert_lease(package, worker_id)
    package.error_detail = error[:4000]
    package.lease_owner = None
    package.lease_expires_at = None
    if package.attempt < package.max_attempts:
        package.state = "PENDING"
        package.run_after = utcnow() + timedelta(seconds=min(300, 2 ** package.attempt))
    else:
        package.state = "FAILED"
    append_audit(session, "work_package.execution_failed", worker_id, package.id, {
        "workflow_id": workflow_id,
        "retry_scheduled": package.state == "PENDING",
    })
    emit_outbox(session, "work_package.execution_failed", package.id, {
        "workflow_id": workflow_id,
        "package_id": package_id,
        "state": package.state,
    })
    workflow = session.get(Workflow, workflow_id)
    if workflow and package.state == "FAILED":
        workflow.state = "PARTIAL"
    session.flush()
    return package


def block_package(
    session: Session,
    workflow_id: str,
    package_id: str,
    worker_id: str,
    reason: str,
):
    package = session.scalar(
        select(WorkPackage).where(
            WorkPackage.workflow_id == workflow_id,
            WorkPackage.package_id == package_id,
        ).with_for_update()
    )
    _assert_lease(package, worker_id)
    package.state = "BLOCKED"
    package.blockers = [reason]
    package.lease_owner = None
    package.lease_expires_at = None
    append_audit(session, "work_package.blocked", worker_id, package.id, {
        "workflow_id": workflow_id, "reason": reason,
    })
    emit_outbox(session, "work_package.blocked", package.id, {
        "workflow_id": workflow_id, "package_id": package_id, "reason": reason,
    })
    workflow = session.get(Workflow, workflow_id)
    if workflow:
        workflow.state = "BLOCKED"
    session.flush()
    return package


def claim_outbox(session: Session, worker_id: str, lease_seconds: int = 60):
    now = utcnow()
    event = session.scalar(
        select(OutboxEvent)
        .where(
            (
                (OutboxEvent.state == "PENDING")
                & (OutboxEvent.available_at <= now)
            )
            | (
                (OutboxEvent.state == "LEASED")
                & (OutboxEvent.lease_expires_at < now)
            )
        )
        .order_by(OutboxEvent.created_at.asc())
        .with_for_update(skip_locked=True)
        .limit(1)
    )
    if not event:
        return None
    event.state = "LEASED"
    event.lease_owner = worker_id
    event.lease_expires_at = now + timedelta(seconds=lease_seconds)
    event.attempts += 1
    session.flush()
    return event


def ack_outbox(session: Session, event_id: str, worker_id: str):
    event = session.scalar(
        select(OutboxEvent).where(OutboxEvent.event_id == event_id).with_for_update()
    )
    if not event or event.state != "LEASED" or event.lease_owner != worker_id:
        raise DomainError(409, "Outbox lease does not belong to this worker")
    event.state = "DELIVERED"
    event.delivered_at = utcnow()
    event.lease_owner = None
    event.lease_expires_at = None
    session.flush()
    return event


def fail_outbox(session: Session, event_id: str, worker_id: str, error: str):
    event = session.scalar(
        select(OutboxEvent).where(OutboxEvent.event_id == event_id).with_for_update()
    )
    if not event or event.state != "LEASED" or event.lease_owner != worker_id:
        raise DomainError(409, "Outbox lease does not belong to this worker")
    event.error_detail = error[:4000]
    event.lease_owner = None
    event.lease_expires_at = None
    if event.attempts >= event.max_attempts:
        event.state = "DEAD"
    else:
        event.state = "PENDING"
        event.available_at = utcnow() + timedelta(seconds=min(900, 2 ** event.attempts))
    append_audit(session, "outbox.delivery_failed", worker_id, event.event_id, {
        "state": event.state, "attempts": event.attempts,
    })
    session.flush()
    return event


def verify_audit_chain(session: Session):
    head = session.get(AuditHead, 1)
    events = session.scalars(
        select(AuditEvent).order_by(AuditEvent.sequence.asc())
    ).all()
    previous = "0" * 64
    count = 0
    for event in events:
        body = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "actor": event.actor,
            "aggregate_id": event.aggregate_id,
            "payload": event.payload,
            "previous_hash": event.previous_hash,
        }
        if event.previous_hash != previous or _sha256_json(body) != event.event_hash:
            return {
                "valid": False,
                "checked_events": count,
                "failed_event_id": event.event_id,
                "failed_sequence": event.sequence,
            }
        previous = event.event_hash
        count += 1
    return {
        "valid": bool(head and head.event_count == count and head.last_hash == previous),
        "checked_events": count,
        "head_event_count": head.event_count if head else 0,
        "head_hash_matches": bool(head and head.last_hash == previous),
    }


def add_entitlement(session: Session, data: dict[str, Any], actor: str):
    existing = session.scalar(
        select(Entitlement).where(
            Entitlement.subject == data["subject"],
            Entitlement.product_key == data["product_key"],
        )
    )
    if existing:
        existing.status = data.get("status", "ACTIVE")
        existing.scopes = data.get("scopes", [])
        existing.valid_until = data.get("valid_until")
        existing.source_reference = data.get("source_reference")
        record = existing
        event_type = "entitlement.updated"
    else:
        record = Entitlement(
            entitlement_id=_id(),
            subject=data["subject"],
            product_key=data["product_key"],
            status=data.get("status", "ACTIVE"),
            scopes=data.get("scopes", []),
            valid_until=data.get("valid_until"),
            source_reference=data.get("source_reference"),
        )
        session.add(record)
        event_type = "entitlement.granted"
    session.flush()
    append_audit(session, event_type, actor, record.entitlement_id, {
        "subject": record.subject,
        "product_key": record.product_key,
        "status": record.status,
        "scopes": record.scopes,
    })
    return record


def create_release(session: Session, data: dict[str, Any], actor: str):
    plugin = session.get(Plugin, data["plugin_key"])
    if not plugin:
        raise DomainError(404, "Plugin not found")
    if plugin.source_state not in CANONICAL_SOURCE_STATES or not plugin.source_commit:
        raise DomainError(409, "Canonical Git source is not pinned")
    if plugin.source_commit != data["source_commit"]:
        raise DomainError(409, "Release source_commit does not match the current registry pin")
    if plugin.distribution_rights_status != "CLEARED":
        raise DomainError(403, "Redistribution rights are not cleared")
    if not data["artifact_url"].startswith("https://"):
        raise DomainError(422, "Published artifact URL must use HTTPS")
    if len(data["artifact_sha256"]) != 64 or any(
        character not in "0123456789abcdefABCDEF" for character in data["artifact_sha256"]
    ):
        raise DomainError(422, "artifact_sha256 must be a 64-character hexadecimal SHA-256 digest")
    release = PackageRelease(
        release_id=_id(),
        plugin_key=data["plugin_key"],
        version=data["version"],
        source_commit=data["source_commit"],
        artifact_url=data["artifact_url"],
        artifact_sha256=data["artifact_sha256"].lower(),
        signature_b64=data["signature_b64"],
        signing_key_id=data["signing_key_id"],
        state="DRAFT",
    )
    session.add(release)
    session.flush()
    append_audit(session, "release.created", actor, release.release_id, {
        "plugin_key": release.plugin_key,
        "version": release.version,
        "artifact_sha256": release.artifact_sha256,
    })
    return release


def verify_release(
    session: Session,
    release_id: str,
    artifact_bytes: bytes,
    settings: Settings,
    actor: str,
):
    release = session.get(PackageRelease, release_id)
    if not release:
        raise DomainError(404, "Release not found")
    if release.state != "DRAFT":
        raise DomainError(409, "Only DRAFT releases can be verified")
    if len(artifact_bytes) > settings.max_artifact_bytes:
        raise DomainError(413, "Artifact exceeds configured upload verification limit")
    digest = hashlib.sha256(artifact_bytes).hexdigest()
    if digest != release.artifact_sha256:
        raise DomainError(422, "Artifact bytes do not match the registered SHA-256 digest")
    if release.signing_key_id != settings.release_public_key_id or not settings.release_public_key_pem:
        raise DomainError(503, "Trusted release verification key is not configured")
    try:
        key = serialization.load_pem_public_key(settings.release_public_key_pem.encode("utf-8"))
        if not isinstance(key, Ed25519PublicKey):
            raise TypeError("Expected Ed25519 public key")
        signature = base64.b64decode(release.signature_b64, validate=True)
        signed_payload = f"{release.plugin_key}:{release.version}:{release.source_commit}:{release.artifact_sha256}".encode("utf-8")
        key.verify(signature, signed_payload)
    except Exception as exc:
        raise DomainError(422, "Release signature verification failed") from exc
    release.state = "VERIFIED"
    release.verified_at = utcnow()
    append_audit(session, "release.verified", actor, release.release_id, {
        "artifact_sha256": digest, "signing_key_id": release.signing_key_id,
    })
    emit_outbox(session, "release.verified", release.release_id, {
        "plugin_key": release.plugin_key, "version": release.version,
    })
    session.flush()
    return release


def publish_release(session: Session, release_id: str, actor: str):
    release = session.get(PackageRelease, release_id)
    if not release:
        raise DomainError(404, "Release not found")
    if release.state != "VERIFIED":
        raise DomainError(409, "Only VERIFIED releases can be published")
    plugin = session.get(Plugin, release.plugin_key)
    if not plugin or plugin.distribution_rights_status != "CLEARED":
        raise DomainError(403, "Distribution rights must be CLEARED at publication time")
    if plugin.source_commit != release.source_commit:
        raise DomainError(409, "Source pin changed after release verification")
    release.state = "PUBLISHED"
    release.published_at = utcnow()
    append_audit(session, "release.published", actor, release.release_id, {
        "plugin_key": release.plugin_key, "version": release.version,
    })
    emit_outbox(session, "release.published", release.release_id, {
        "plugin_key": release.plugin_key, "version": release.version,
    })
    session.flush()
    return release


def create_installation(
    session: Session,
    data: dict[str, Any],
    subject: str,
    idempotency_key: str | None = None,
):
    if idempotency_key:
        existing = session.scalar(
            select(Installation).where(
                Installation.subject == subject,
                Installation.idempotency_key == idempotency_key,
            )
        )
        if existing:
            return existing
    release = session.get(PackageRelease, data["release_id"])
    if not release or release.state != "PUBLISHED":
        raise DomainError(409, "Only PUBLISHED releases can be installed")
    entitlement = session.scalar(
        select(Entitlement).where(
            Entitlement.subject == subject,
            Entitlement.product_key == release.plugin_key,
            Entitlement.status == "ACTIVE",
        )
    )
    if not entitlement or (entitlement.valid_until and entitlement.valid_until <= utcnow()):
        raise DomainError(403, "Active entitlement is required")
    installation = Installation(
        installation_id=_id(),
        subject=subject,
        release_id=release.release_id,
        target=data["target"],
        state="BLOCKED_ADAPTER_UNAVAILABLE",
        blocker="TARGET_PLATFORM_ADAPTER_NOT_PROVISIONED",
        idempotency_key=idempotency_key,
    )
    session.add(installation)
    session.flush()
    append_audit(session, "installation.blocked", subject, installation.installation_id, {
        "release_id": release.release_id,
        "target": data["target"],
        "blocker": installation.blocker,
    })
    emit_outbox(session, "installation.blocked", installation.installation_id, {
        "release_id": release.release_id,
        "target": data["target"],
    })
    return installation
