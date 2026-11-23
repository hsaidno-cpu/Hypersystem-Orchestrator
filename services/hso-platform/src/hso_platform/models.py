from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Plugin(Base):
    __tablename__ = "plugins"

    plugin_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(240), nullable=False)
    source_state: Mapped[str] = mapped_column(String(40), nullable=False, default="pending_repository")
    source_url: Mapped[str | None] = mapped_column(String(1000))
    source_commit: Mapped[str | None] = mapped_column(String(40))
    execution_rights_status: Mapped[str] = mapped_column(String(40), nullable=False, default="NOT_ASSESSED")
    distribution_rights_status: Mapped[str] = mapped_column(String(40), nullable=False, default="NOT_ASSESSED")
    owner_reference: Mapped[str | None] = mapped_column(String(240))
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    capabilities: Mapped[list["Capability"]] = relationship(back_populates="plugin")
    work_packages: Mapped[list["WorkPackage"]] = relationship(back_populates="owner")


class Capability(Base):
    __tablename__ = "capabilities"
    __table_args__ = (
        UniqueConstraint("plugin_key", "capability_key", "version", name="uq_capability_version"),
    )

    capability_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    plugin_key: Mapped[str] = mapped_column(ForeignKey("plugins.plugin_key"), nullable=False, index=True)
    capability_key: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    contract_version: Mapped[str] = mapped_column(String(32), nullable=False)
    protocol: Mapped[str] = mapped_column(String(16), nullable=False)
    endpoint: Mapped[str | None] = mapped_column(String(1000))
    permission_scopes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    evidence_reference: Mapped[str | None] = mapped_column(String(1000))
    last_health_status: Mapped[str] = mapped_column(String(32), nullable=False, default="NOT_CHECKED")
    last_health_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    plugin: Mapped[Plugin] = relationship(back_populates="capabilities")


class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="PLANNED")
    action_authority: Mapped[str] = mapped_column(String(2), nullable=False)
    created_by: Mapped[str] = mapped_column(String(240), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(160), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    packages: Mapped[list["WorkPackage"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class WorkPackage(Base):
    __tablename__ = "work_packages"
    __table_args__ = (
        UniqueConstraint("workflow_id", "package_id", name="uq_workflow_package"),
        Index("ix_work_package_claim", "state", "run_after", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.workflow_id", ondelete="CASCADE"), nullable=False, index=True)
    package_id: Mapped[str] = mapped_column(String(128), nullable=False)
    primary_owner: Mapped[str] = mapped_column(ForeignKey("plugins.plugin_key"), nullable=False)
    supporting_specialists: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    depends_on: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    capability_status: Mapped[str] = mapped_column(String(32), nullable=False)
    capability_evidence: Mapped[str | None] = mapped_column(Text)
    write_scope: Mapped[str] = mapped_column(String(64), nullable=False, default="READ_ONLY")
    required_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approval_status: Mapped[str] = mapped_column(String(24), nullable=False, default="NOT_REQUIRED")
    approval_reference: Mapped[str | None] = mapped_column(String(240))
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_criteria: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="BLOCKED")
    blockers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    run_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(160))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result_json: Mapped[dict | None] = mapped_column(JSON)
    error_detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    owner: Mapped[Plugin] = relationship(back_populates="work_packages")
    workflow: Mapped[Workflow] = relationship(back_populates="packages")
    specialist_assignments: Mapped[list["SpecialistAssignment"]] = relationship(
        back_populates="work_package", cascade="all, delete-orphan"
    )


class SpecialistAssignment(Base):
    __tablename__ = "specialist_assignments"
    __table_args__ = (
        UniqueConstraint("work_package_id", "plugin_key", name="uq_package_specialist"),
    )

    assignment_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    work_package_id: Mapped[str] = mapped_column(ForeignKey("work_packages.id", ondelete="CASCADE"), nullable=False, index=True)
    plugin_key: Mapped[str] = mapped_column(ForeignKey("plugins.plugin_key"), nullable=False)
    expected_contribution: Mapped[str] = mapped_column(Text, nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    capability_status: Mapped[str] = mapped_column(String(32), nullable=False)
    capability_evidence: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(24), nullable=False, default="PENDING")

    work_package: Mapped[WorkPackage] = relationship(back_populates="specialist_assignments")


class AuditHead(Base):
    __tablename__ = "audit_chain_head"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_hash: Mapped[str] = mapped_column(String(64), nullable=False, default="0" * 64)
    event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_event_aggregate_sequence", "aggregate_id", "sequence"),
    )

    sequence: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    actor: Mapped[str] = mapped_column(String(240), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)


class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    __table_args__ = (Index("ix_outbox_pending", "state", "available_at"),)

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    state: Mapped[str] = mapped_column(String(24), nullable=False, default="PENDING")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(160))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class APIKey(Base):
    __tablename__ = "api_keys"

    key_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prefix: Mapped[str] = mapped_column(String(24), nullable=False, unique=True, index=True)
    secret_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    subject: Mapped[str] = mapped_column(String(240), nullable=False)
    scopes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Entitlement(Base):
    __tablename__ = "entitlements"
    __table_args__ = (UniqueConstraint("subject", "product_key", name="uq_entitlement_subject_product"),)

    entitlement_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subject: Mapped[str] = mapped_column(String(240), nullable=False)
    product_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="ACTIVE")
    scopes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_reference: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class PackageRelease(Base):
    __tablename__ = "package_releases"
    __table_args__ = (UniqueConstraint("plugin_key", "version", name="uq_plugin_release_version"),)

    release_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    plugin_key: Mapped[str] = mapped_column(ForeignKey("plugins.plugin_key"), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    source_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    artifact_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    artifact_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    signature_b64: Mapped[str] = mapped_column(Text, nullable=False)
    signing_key_id: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Installation(Base):
    __tablename__ = "installations"
    __table_args__ = (
        UniqueConstraint("subject", "idempotency_key", name="uq_installation_idempotency"),
    )

    installation_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subject: Mapped[str] = mapped_column(String(240), nullable=False)
    release_id: Mapped[str] = mapped_column(ForeignKey("package_releases.release_id"), nullable=False)
    target: Mapped[str] = mapped_column(String(240), nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False)
    blocker: Mapped[str | None] = mapped_column(String(160))
    idempotency_key: Mapped[str | None] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class UsageRecord(Base):
    __tablename__ = "usage_records"

    usage_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    subject: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    workflow_id: Mapped[str | None] = mapped_column(String(36), index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    dimensions: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
