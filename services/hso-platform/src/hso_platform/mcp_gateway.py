from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from .models import Plugin, WorkPackage, Workflow


def build_mcp_gateway(
    session_factory: sessionmaker[Session],
    allowed_hosts: tuple[str, ...],
    allowed_origins: tuple[str, ...],
):
    server = MCPServer(
        "Hypersystem Orchestrator",
        instructions=(
            "Read-only MCP interface to the HSO control plane. "
            "It exposes registry and workflow status. It does not execute plugins."
        ),
    )

    @server.tool()
    def list_registered_plugins() -> list[dict]:
        """List plugin identities, source pins and entitlement/readiness declarations."""
        with session_factory() as session:
            records = session.scalars(select(Plugin).order_by(Plugin.plugin_key.asc())).all()
            return [
                {
                    "plugin_key": item.plugin_key,
                    "display_name": item.display_name,
                    "source_state": item.source_state,
                    "source_commit": item.source_commit,
                    "execution_rights_status": item.execution_rights_status,
                    "distribution_rights_status": item.distribution_rights_status,
                }
                for item in records
            ]

    @server.tool()
    def get_workflow_status(workflow_id: str) -> dict:
        """Return workflow and work-package states for a known workflow ID."""
        with session_factory() as session:
            workflow = session.get(Workflow, workflow_id)
            if not workflow:
                return {"found": False, "workflow_id": workflow_id}
            packages = session.scalars(
                select(WorkPackage)
                .where(WorkPackage.workflow_id == workflow_id)
                .order_by(WorkPackage.package_id.asc())
            ).all()
            return {
                "found": True,
                "workflow_id": workflow.workflow_id,
                "case_id": workflow.case_id,
                "state": workflow.state,
                "packages": [
                    {
                        "package_id": item.package_id,
                        "primary_owner": item.primary_owner,
                        "supporting_specialists": item.supporting_specialists,
                        "state": item.state,
                        "blockers": item.blockers,
                        "attempt": item.attempt,
                        "verification_status": item.verification_status,
                    }
                    for item in packages
                ],
            }

    transport_security = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=list(allowed_hosts),
        allowed_origins=list(allowed_origins),
    )
    asgi_app = server.streamable_http_app(
        streamable_http_path="/",
        stateless_http=True,
        json_response=True,
        transport_security=transport_security,
        max_request_body_size=4 * 1024 * 1024,
        host="127.0.0.1",
    )
    return server, asgi_app
