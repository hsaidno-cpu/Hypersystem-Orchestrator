from __future__ import annotations

import base64
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from .database import build_engine, build_session_factory, database_is_ready
from .domain import (
    DomainError, ack_outbox, add_entitlement, append_audit, block_package,
    claim_next_package, claim_outbox, complete_package, create_installation,
    create_release, create_workflow, fail_outbox, fail_package, publish_release,
    register_capability, register_plugin, verify_audit_chain, verify_package,
    verify_release,
)
from .mcp_gateway import build_mcp_gateway
from .models import (
    APIKey, AuditHead, Base, Capability, OutboxEvent, Plugin, WorkPackage,
    Workflow,
)
from .schemas import (
    APIKeyCreate, CapabilityCreate, CapabilityHostVerification, CompletePackage,
    EntitlementCreate, FailPackage, InstallationCreate, OutboxAck, PluginCreate,
    ReleaseCreate, ReleaseVerify, VerificationDecision, WorkflowCreate,
)
from .security import Principal, authenticate, create_api_key, require_scope
from .settings import Settings

logger = logging.getLogger("hso.control_plane")
REQUESTS = Counter("hso_http_requests_total", "HTTP requests handled", ["method", "path", "status"])
READINESS = Counter("hso_capability_host_verifications_total", "Host verification results", ["protocol", "result"])


def _plugin_view(item: Plugin) -> dict:
    return {
        "plugin_key": item.plugin_key,
        "display_name": item.display_name,
        "source_state": item.source_state,
        "source_url": item.source_url,
        "source_commit": item.source_commit,
        "execution_rights_status": item.execution_rights_status,
        "distribution_rights_status": item.distribution_rights_status,
        "metadata": item.metadata_json,
    }


def _capability_view(item: Capability) -> dict:
    return {
        "capability_id": item.capability_id,
        "plugin_key": item.plugin_key,
        "capability_key": item.capability_key,
        "version": item.version,
        "contract_version": item.contract_version,
        "protocol": item.protocol,
        "endpoint": item.endpoint,
        "permission_scopes": item.permission_scopes,
        "enabled": item.enabled,
        "evidence_reference": item.evidence_reference,
        "last_health_status": item.last_health_status,
        "last_health_at": item.last_health_at.isoformat() if item.last_health_at else None,
    }


def _workflow_view(session: Session, workflow: Workflow) -> dict:
    packages = session.scalars(
        select(WorkPackage)
        .where(WorkPackage.workflow_id == workflow.workflow_id)
        .order_by(WorkPackage.package_id.asc())
    ).all()
    output = []
    for item in packages:
        output.append({
            "package_id": item.package_id,
            "primary_owner": item.primary_owner,
            "supporting_specialists": item.supporting_specialists,
            "depends_on": item.depends_on,
            "state": item.state,
            "blockers": item.blockers,
            "attempt": item.attempt,
            "lease_owner": item.lease_owner,
            "lease_expires_at": item.lease_expires_at.isoformat() if item.lease_expires_at else None,
            "result": item.result_json,
            "error_detail": item.error_detail,
            "output_locator": item.output_locator,
            "runtime_trace_reference": item.runtime_trace_reference,
            "runtime_host": item.runtime_host,
            "runtime_host_version": item.runtime_host_version,
            "runtime_adapter_version": item.runtime_adapter_version,
            "verification_status": item.verification_status,
            "verification_evidence": item.verification_evidence,
            "verified_by": item.verified_by,
            "specialist_assignments": [
                {
                    "plugin_key": assignment.plugin_key,
                    "expected_contribution": assignment.expected_contribution,
                    "required": assignment.required,
                    "capability_status": assignment.capability_status,
                    "state": assignment.state,
                }
                for assignment in item.specialist_assignments
            ],
        })
    return {
        "workflow_id": workflow.workflow_id,
        "case_id": workflow.case_id,
        "intent": workflow.intent,
        "state": workflow.state,
        "action_authority": workflow.action_authority,
        "created_by": workflow.created_by,
        "created_at": workflow.created_at.isoformat(),
        "packages": output,
    }


def create_app(
    settings: Settings | None = None,
    engine=None,
    session_factory: sessionmaker[Session] | None = None,
) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.validate()
    engine = engine or build_engine(settings)
    session_factory = session_factory or build_session_factory(engine)
    mcp_server, mcp_asgi = build_mcp_gateway(
        session_factory,
        settings.mcp_allowed_hosts,
        settings.mcp_allowed_origins,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if settings.environment in {"development", "test"}:
            Base.metadata.create_all(bind=engine)
        with session_factory() as session, session.begin():
            if session.get(AuditHead, 1) is None:
                session.add(AuditHead(id=1, last_hash="0" * 64, event_count=0))
        async with mcp_server.session_manager.run():
            yield
        engine.dispose()

    app = FastAPI(
        title="Hypersystem Orchestrator Control Plane",
        version="0.1.0",
        description=(
            "Governed registry, persistent workflow, identity, runtime adapter, "
            "release, installation and synchronization control plane."
        ),
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    @app.middleware("http")
    async def request_context_and_mcp_auth(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.monotonic()

        if request.url.path.startswith("/mcp"):
            try:
                with session_factory() as session:
                    authenticated = authenticate(request, session, settings)
                if "mcp:invoke" not in authenticated.scopes:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "Missing required scope: mcp:invoke", "request_id": request_id},
                    )
                request.state.principal = authenticated
            except HTTPException as exc:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail, "request_id": request_id},
                    headers=exc.headers,
                )

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        elapsed_ms = round((time.monotonic() - started) * 1000, 2)
        REQUESTS.labels(request.method, request.url.path, str(response.status_code)).inc()
        logger.info(json.dumps({
            "event": "http.request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "elapsed_ms": elapsed_ms,
        }, separators=(",", ":")))
        return response

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

    @app.get("/health/live")
    def liveness():
        return {"status": "LIVE", "service": "hso-control-plane"}

    @app.get("/health/ready")
    def readiness():
        if not database_is_ready(engine):
            raise HTTPException(status_code=503, detail="Database is not ready")
        return {"status": "READY", "database": "CONNECTED"}

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics(actor: Principal = Depends(require_scope("metrics:read"))):
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/api/v1/registry/plugins")
    def list_plugins(actor: Principal = Depends(require_scope("registry:read"))):
        with session_factory() as session:
            records = session.scalars(select(Plugin).order_by(Plugin.plugin_key.asc())).all()
            return {"items": [_plugin_view(item) for item in records]}

    @app.post("/api/v1/registry/plugins", status_code=201)
    def upsert_plugin(
        payload: PluginCreate,
        actor: Principal = Depends(require_scope("registry:write")),
    ):
        with session_factory() as session, session.begin():
            item = register_plugin(session, payload.model_dump(), actor.subject)
            return _plugin_view(item)

    @app.get("/api/v1/registry/capabilities")
    def list_capabilities(actor: Principal = Depends(require_scope("registry:read"))):
        with session_factory() as session:
            records = session.scalars(
                select(Capability).order_by(Capability.plugin_key.asc(), Capability.capability_key.asc())
            ).all()
            return {"items": [_capability_view(item) for item in records]}

    @app.post("/api/v1/registry/plugins/{plugin_key}/capabilities", status_code=201)
    def add_capability(
        plugin_key: str,
        payload: CapabilityCreate,
        actor: Principal = Depends(require_scope("registry:write")),
    ):
        with session_factory() as session, session.begin():
            item = register_capability(session, plugin_key, payload.model_dump(), actor.subject)
            return _capability_view(item)

    @app.post("/api/v1/registry/capabilities/{capability_id}/host-verification")
    def record_host_verification(
        capability_id: str,
        payload: CapabilityHostVerification,
        actor: Principal = Depends(require_scope("capabilities:verify")),
    ):
        with session_factory() as session, session.begin():
            item = session.scalar(
                select(Capability).where(Capability.capability_id == capability_id).with_for_update()
            )
            if not item:
                raise HTTPException(status_code=404, detail="Capability not found")
            item.last_health_status = "C4_PASS" if payload.disposition == "PASS" else "C4_FAIL"
            item.last_health_at = datetime.now(timezone.utc)
            item.evidence_reference = payload.evidence_reference
            item.metadata_json = {
                **(item.metadata_json or {}),
                "host": payload.host,
                "host_version": payload.host_version,
                "adapter_version": payload.adapter_version,
                "host_verification_disposition": payload.disposition,
            }
            if payload.disposition == "FAIL":
                item.enabled = False
            append_audit(session, "capability.host_verification", actor.subject, capability_id, {
                "protocol": item.protocol,
                "disposition": payload.disposition,
                "host": payload.host,
                "host_version": payload.host_version,
                "adapter_version": payload.adapter_version,
                "evidence_reference": payload.evidence_reference,
            })
            READINESS.labels(item.protocol, payload.disposition).inc()
            return _capability_view(item)

    @app.post("/api/v1/registry/capabilities/{capability_id}/enable")
    def enable_capability(
        capability_id: str,
        actor: Principal = Depends(require_scope("registry:write")),
    ):
        with session_factory() as session, session.begin():
            item = session.scalar(
                select(Capability).where(Capability.capability_id == capability_id).with_for_update()
            )
            if not item:
                raise HTTPException(status_code=404, detail="Capability not found")
            plugin = session.get(Plugin, item.plugin_key)
            if (
                not plugin
                or plugin.source_state not in {"integrated_submodule", "integrated_submodule_private"}
                or not plugin.source_commit
                or plugin.execution_rights_status != "CLEARED"
            ):
                raise HTTPException(status_code=409, detail="Canonical source and execution rights are not cleared")
            if item.last_health_status != "C4_PASS" or not item.evidence_reference:
                raise HTTPException(status_code=409, detail="Named-host C4 verification is required before enablement")
            item.enabled = True
            append_audit(session, "capability.enabled", actor.subject, capability_id, {
                "plugin_key": item.plugin_key,
                "protocol": item.protocol,
                "evidence_reference": item.evidence_reference,
            })
            return _capability_view(item)

    @app.post("/api/v1/registry/capabilities/{capability_id}/disable")
    def disable_capability(
        capability_id: str,
        actor: Principal = Depends(require_scope("registry:write")),
    ):
        with session_factory() as session, session.begin():
            item = session.get(Capability, capability_id)
            if not item:
                raise HTTPException(status_code=404, detail="Capability not found")
            item.enabled = False
            append_audit(session, "capability.disabled", actor.subject, capability_id, {})
            return _capability_view(item)

    @app.post("/api/v1/workflows", status_code=201)
    def submit_workflow(
        payload: WorkflowCreate,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
        actor: Principal = Depends(require_scope("workflow:write")),
    ):
        if idempotency_key and len(idempotency_key) > 160:
            raise HTTPException(status_code=422, detail="Idempotency-Key is too long")
        with session_factory() as session, session.begin():
            workflow = create_workflow(
                session,
                payload.model_dump(),
                actor.subject,
                idempotency_key=idempotency_key,
            )
            return _workflow_view(session, workflow)

    @app.get("/api/v1/workflows/{workflow_id}")
    def read_workflow(
        workflow_id: str,
        actor: Principal = Depends(require_scope("workflow:read")),
    ):
        with session_factory() as session:
            workflow = session.get(Workflow, workflow_id)
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return _workflow_view(session, workflow)

    @app.post("/api/v1/workers/{worker_id}/claim")
    def worker_claim(
        worker_id: str,
        actor: Principal = Depends(require_scope("workflow:execute")),
    ):
        if actor.subject != worker_id and "workers:manage" not in actor.scopes:
            raise HTTPException(status_code=403, detail="Worker identity must match authenticated subject")
        with session_factory() as session, session.begin():
            package = claim_next_package(session, worker_id, settings)
            if not package:
                return {"claimed": False}
            return {
                "claimed": True,
                "workflow_id": package.workflow_id,
                "package_id": package.package_id,
                "primary_owner": package.primary_owner,
                "lease_expires_at": package.lease_expires_at.isoformat(),
                "attempt": package.attempt,
            }

    @app.post("/api/v1/workflows/{workflow_id}/packages/{package_id}/complete")
    def worker_complete(
        workflow_id: str,
        package_id: str,
        payload: CompletePackage,
        actor: Principal = Depends(require_scope("workflow:execute")),
    ):
        with session_factory() as session, session.begin():
            package = complete_package(
                session, workflow_id, package_id, actor.subject, payload.result
            )
            return {"package_id": package.package_id, "state": package.state}

    @app.post("/api/v1/workflows/{workflow_id}/packages/{package_id}/fail")
    def worker_fail(
        workflow_id: str,
        package_id: str,
        payload: FailPackage,
        actor: Principal = Depends(require_scope("workflow:execute")),
    ):
        with session_factory() as session, session.begin():
            package = fail_package(
                session, workflow_id, package_id, actor.subject, payload.error
            )
            return {
                "package_id": package.package_id,
                "state": package.state,
                "attempt": package.attempt,
            }

    @app.post("/api/v1/workflows/{workflow_id}/packages/{package_id}/verify")
    def independent_package_verify(
        workflow_id: str,
        package_id: str,
        payload: VerificationDecision,
        actor: Principal = Depends(require_scope("workflow:verify")),
    ):
        with session_factory() as session, session.begin():
            package = verify_package(
                session,
                workflow_id,
                package_id,
                actor.subject,
                payload.disposition,
                payload.evidence_reference,
                payload.notes,
            )
            return {
                "package_id": package.package_id,
                "state": package.state,
                "verification_status": package.verification_status,
                "verified_by": package.verified_by,
            }

    @app.post("/api/v1/api-keys", status_code=201)
    def issue_api_key(
        payload: APIKeyCreate,
        actor: Principal = Depends(require_scope("keys:manage")),
    ):
        if not settings.api_key_pepper:
            raise HTTPException(status_code=503, detail="API-key issuance is not configured")
        if not set(payload.scopes).issubset(actor.scopes):
            raise HTTPException(status_code=403, detail="Cannot delegate scopes the caller does not possess")
        with session_factory() as session, session.begin():
            token, record = create_api_key(
                session,
                payload.subject,
                payload.scopes,
                settings.api_key_pepper,
                payload.expires_at,
            )
            append_audit(session, "api_key.created", actor.subject, record.key_id, {
                "subject": record.subject,
                "scopes": record.scopes,
                "prefix": record.prefix,
            })
            return {
                "api_key": token,
                "key_id": record.key_id,
                "prefix": record.prefix,
                "scopes": record.scopes,
                "warning": "This secret is displayed once. Store it in a secret manager immediately.",
            }

    @app.post("/api/v1/api-keys/{key_id}/revoke")
    def revoke_api_key(
        key_id: str,
        actor: Principal = Depends(require_scope("keys:manage")),
    ):
        with session_factory() as session, session.begin():
            record = session.scalar(
                select(APIKey).where(APIKey.key_id == key_id).with_for_update()
            )
            if not record:
                raise HTTPException(status_code=404, detail="API key not found")
            if record.revoked_at is None:
                record.revoked_at = datetime.now(timezone.utc)
                append_audit(session, "api_key.revoked", actor.subject, key_id, {
                    "subject": record.subject,
                    "prefix": record.prefix,
                })
            return {"key_id": key_id, "revoked": True}

    @app.post("/api/v1/api-keys/{key_id}/rotate")
    def rotate_api_key(
        key_id: str,
        actor: Principal = Depends(require_scope("keys:manage")),
    ):
        with session_factory() as session, session.begin():
            old = session.scalar(
                select(APIKey).where(APIKey.key_id == key_id).with_for_update()
            )
            if not old:
                raise HTTPException(status_code=404, detail="API key not found")
            if old.revoked_at is not None:
                raise HTTPException(status_code=409, detail="Revoked API keys cannot be rotated")
            if not set(old.scopes).issubset(actor.scopes):
                raise HTTPException(status_code=403, detail="Caller cannot rotate a key with broader scopes")
            new_token, new_record = create_api_key(
                session, old.subject, old.scopes, settings.api_key_pepper, old.expires_at
            )
            old.revoked_at = datetime.now(timezone.utc)
            append_audit(session, "api_key.rotated", actor.subject, key_id, {
                "new_key_id": new_record.key_id,
                "subject": old.subject,
            })
            return {
                "api_key": new_token,
                "key_id": new_record.key_id,
                "replaces_key_id": key_id,
                "warning": "New secret is displayed once. Store it in a secret manager immediately.",
            }

    @app.post("/api/v1/entitlements", status_code=201)
    def grant_entitlement(
        payload: EntitlementCreate,
        actor: Principal = Depends(require_scope("entitlements:manage")),
    ):
        with session_factory() as session, session.begin():
            item = add_entitlement(session, payload.model_dump(), actor.subject)
            return {
                "entitlement_id": item.entitlement_id,
                "subject": item.subject,
                "product_key": item.product_key,
                "status": item.status,
                "valid_until": item.valid_until.isoformat() if item.valid_until else None,
            }

    @app.post("/api/v1/releases", status_code=201)
    def stage_release(
        payload: ReleaseCreate,
        actor: Principal = Depends(require_scope("package:publish")),
    ):
        with session_factory() as session, session.begin():
            item = create_release(session, payload.model_dump(), actor.subject)
            return {
                "release_id": item.release_id,
                "plugin_key": item.plugin_key,
                "version": item.version,
                "state": item.state,
                "artifact_sha256": item.artifact_sha256,
            }

    @app.post("/api/v1/releases/{release_id}/verify")
    def verify_staged_release(
        release_id: str,
        payload: ReleaseVerify,
        actor: Principal = Depends(require_scope("package:publish")),
    ):
        try:
            artifact_bytes = base64.b64decode(payload.artifact_content_b64, validate=True)
        except Exception as exc:
            raise HTTPException(status_code=422, detail="artifact_content_b64 is invalid") from exc
        if len(artifact_bytes) > settings.max_artifact_bytes:
            raise HTTPException(status_code=413, detail="Artifact exceeds configured upload verification limit")
        with session_factory() as session, session.begin():
            item = verify_release(session, release_id, artifact_bytes, settings, actor.subject)
            return {
                "release_id": item.release_id,
                "state": item.state,
                "verified_at": item.verified_at.isoformat() if item.verified_at else None,
            }

    @app.post("/api/v1/releases/{release_id}/publish")
    def publish_staged_release(
        release_id: str,
        actor: Principal = Depends(require_scope("package:publish")),
    ):
        with session_factory() as session, session.begin():
            item = publish_release(session, release_id, actor.subject)
            return {
                "release_id": item.release_id,
                "state": item.state,
                "published_at": item.published_at.isoformat(),
            }

    @app.post("/api/v1/installations", status_code=202)
    def request_installation(
        payload: InstallationCreate,
        actor: Principal = Depends(require_scope("package:install")),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ):
        if idempotency_key and len(idempotency_key) > 160:
            raise HTTPException(status_code=422, detail="Idempotency-Key is too long")
        with session_factory() as session, session.begin():
            item = create_installation(session, payload.model_dump(), actor.subject, idempotency_key)
            return {
                "installation_id": item.installation_id,
                "state": item.state,
                "blocker": item.blocker,
            }

    @app.post("/api/v1/outbox/claim")
    def claim_sync_event(
        worker_id: str = Header(alias="X-Worker-ID"),
        actor: Principal = Depends(require_scope("outbox:manage")),
    ):
        if actor.subject != worker_id and "workers:manage" not in actor.scopes:
            raise HTTPException(status_code=403, detail="Worker identity mismatch")
        with session_factory() as session, session.begin():
            event = claim_outbox(session, worker_id)
            if not event:
                return {"claimed": False}
            return {
                "claimed": True,
                "event_id": event.event_id,
                "event_type": event.event_type,
                "aggregate_id": event.aggregate_id,
                "payload": event.payload,
                "attempts": event.attempts,
            }

    @app.post("/api/v1/outbox/{event_id}/ack")
    def acknowledge_sync_event(
        event_id: str,
        payload: OutboxAck,
        actor: Principal = Depends(require_scope("outbox:manage")),
    ):
        if actor.subject != payload.worker_id and "workers:manage" not in actor.scopes:
            raise HTTPException(status_code=403, detail="Worker identity mismatch")
        with session_factory() as session, session.begin():
            event = ack_outbox(session, event_id, payload.worker_id)
            return {"event_id": event.event_id, "state": event.state}

    @app.post("/api/v1/outbox/{event_id}/fail")
    def fail_sync_event(
        event_id: str,
        payload: FailPackage,
        worker_id: str = Header(alias="X-Worker-ID"),
        actor: Principal = Depends(require_scope("outbox:manage")),
    ):
        if actor.subject != worker_id and "workers:manage" not in actor.scopes:
            raise HTTPException(status_code=403, detail="Worker identity mismatch")
        with session_factory() as session, session.begin():
            event = fail_outbox(session, event_id, worker_id, payload.error)
            return {"event_id": event.event_id, "state": event.state, "attempts": event.attempts}

    @app.get("/api/v1/outbox/dead")
    def list_dead_outbox(actor: Principal = Depends(require_scope("outbox:manage"))):
        with session_factory() as session:
            records = session.scalars(
                select(OutboxEvent).where(OutboxEvent.state == "DEAD").order_by(OutboxEvent.created_at.asc())
            ).all()
            return {
                "items": [
                    {
                        "event_id": item.event_id,
                        "event_type": item.event_type,
                        "aggregate_id": item.aggregate_id,
                        "attempts": item.attempts,
                        "error_detail": item.error_detail,
                    }
                    for item in records
                ]
            }

    @app.get("/api/v1/audit/verify")
    def audit_verify(actor: Principal = Depends(require_scope("audit:read"))):
        with session_factory() as session:
            return verify_audit_chain(session)

    app.mount("/mcp", mcp_asgi)
    return app


app = create_app()
