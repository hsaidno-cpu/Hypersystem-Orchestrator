from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PluginCreate(StrictModel):
    plugin_key: str = Field(min_length=2, max_length=128)
    display_name: str = Field(min_length=2, max_length=240)
    source_state: Literal["integrated_submodule", "integrated_submodule_private", "candidate_repository", "pending_repository", "canonical_redirect"]
    source_url: str | None = None
    source_commit: str | None = None
    execution_rights_status: Literal["NOT_ASSESSED", "REVIEW_REQUIRED", "CLEARED", "DENIED"] = "NOT_ASSESSED"
    distribution_rights_status: Literal["NOT_ASSESSED", "REVIEW_REQUIRED", "CLEARED", "DENIED"] = "NOT_ASSESSED"
    owner_reference: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_commit")
    @classmethod
    def validate_commit(cls, value: str | None):
        if value is not None and (len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value.lower())):
            raise ValueError("source_commit must be a full 40-character hexadecimal Git SHA")
        return value.lower() if value else value


class CapabilityCreate(StrictModel):
    capability_key: str = Field(min_length=2, max_length=128)
    version: str = Field(min_length=1, max_length=64)
    contract_version: str = Field(min_length=1, max_length=32)
    protocol: Literal["REST", "MCP"]
    endpoint: str | None = None
    permission_scopes: list[str] = Field(default_factory=list)
    evidence_reference: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class SpecialistContribution(StrictModel):
    plugin_key: str = Field(min_length=2, max_length=128)
    expected_contribution: str = Field(min_length=1, max_length=2000)
    required: bool = True
    capability_status: Literal["READY", "READY_WITH_LIMITATIONS", "NOT_CHECKED", "UNAVAILABLE", "ACCESS_DENIED", "EXPIRED", "BLOCKED", "OUT_OF_SCOPE"]
    capability_evidence: str | None = None


class WorkPackagePlan(StrictModel):
    package_id: str = Field(min_length=1, max_length=128)
    primary_owner: str = Field(min_length=2, max_length=128)
    supporting_specialists: list[str] = Field(default_factory=list)
    specialist_contributions: list[SpecialistContribution] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    capability_status: Literal["READY", "READY_WITH_LIMITATIONS", "NOT_CHECKED", "UNAVAILABLE", "ACCESS_DENIED", "EXPIRED", "BLOCKED", "OUT_OF_SCOPE"]
    capability_evidence: str | None = None
    write_scope: Literal["READ_ONLY", "PARENT_REPOSITORY_BRANCH_WRITE", "CHILD_REPOSITORY_CHANGE", "EXTERNAL_SIDE_EFFECT", "PRODUCTION_RELEASE"] = "READ_ONLY"
    requires_approval: bool = False
    approval_status: Literal["NOT_REQUIRED", "PENDING", "APPROVED", "DENIED"] = "NOT_REQUIRED"
    approval_reference: str | None = None
    expected_output: str = Field(min_length=1)
    acceptance_criteria: list[str] = Field(min_length=1)
    max_attempts: int = Field(default=4, ge=1, le=10)

    @field_validator("supporting_specialists", "depends_on", "acceptance_criteria")
    @classmethod
    def unique_values(cls, value: list[str]):
        if len(value) != len(set(value)):
            raise ValueError("List values must be unique")
        if any(not item.strip() for item in value):
            raise ValueError("List values cannot be empty")
        return value

    @field_validator("specialist_contributions")
    @classmethod
    def unique_specialist_contributions(cls, value: list[SpecialistContribution]):
        keys = [item.plugin_key for item in value]
        if len(keys) != len(set(keys)):
            raise ValueError("specialist_contributions must not contain duplicate plugin keys")
        return value


class WorkflowCreate(StrictModel):
    case_id: str = Field(min_length=1, max_length=160)
    intent: str = Field(min_length=1, max_length=10000)
    action_authority: Literal["S0", "S1", "S2", "S3", "S4", "S5"]
    work_packages: list[WorkPackagePlan] = Field(min_length=1)


class APIKeyCreate(StrictModel):
    subject: str = Field(min_length=2, max_length=240)
    scopes: list[str] = Field(min_length=1)
    expires_at: datetime | None = None


class EntitlementCreate(StrictModel):
    subject: str = Field(min_length=2, max_length=240)
    product_key: str = Field(min_length=2, max_length=128)
    scopes: list[str] = Field(default_factory=list)
    valid_until: datetime | None = None
    source_reference: str | None = None


class ReleaseCreate(StrictModel):
    plugin_key: str
    version: str
    source_commit: str = Field(min_length=40, max_length=40)
    artifact_url: str
    artifact_sha256: str = Field(min_length=64, max_length=64)
    signature_b64: str
    signing_key_id: str


class ReleaseVerify(StrictModel):
    artifact_content_b64: str = Field(min_length=1)


class InstallationCreate(StrictModel):
    release_id: str
    target: str = Field(min_length=1, max_length=240)


class CompletePackage(StrictModel):
    result: dict[str, Any] = Field(default_factory=dict)


class FailPackage(StrictModel):
    error: str = Field(min_length=1, max_length=4000)


class OutboxAck(StrictModel):
    worker_id: str = Field(min_length=1, max_length=160)
