from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


def _csv(value: str | None, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    if not value:
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    database_url: str = "sqlite:///./hso-dev.db"
    auth_mode: str = "disabled"
    api_key_pepper: str = ""
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""
    mcp_allowed_hosts: tuple[str, ...] = ("localhost:*", "127.0.0.1:*", "[::1]:*")
    mcp_allowed_origins: tuple[str, ...] = ()
    release_public_key_pem: str = ""
    release_public_key_id: str = ""
    max_artifact_bytes: int = 25 * 1024 * 1024
    lease_seconds: int = 90
    max_work_package_attempts: int = 4

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "Settings":
        env = environ if environ is not None else os.environ
        return cls(
            environment=env.get("HSO_ENV", "development").strip().lower(),
            database_url=env.get("HSO_DATABASE_URL", "sqlite:///./hso-dev.db"),
            auth_mode=env.get("HSO_AUTH_MODE", "disabled").strip().lower(),
            api_key_pepper=env.get("HSO_API_KEY_PEPPER", ""),
            oidc_issuer=env.get("HSO_OIDC_ISSUER", "").rstrip("/"),
            oidc_audience=env.get("HSO_OIDC_AUDIENCE", ""),
            oidc_jwks_url=env.get("HSO_OIDC_JWKS_URL", ""),
            mcp_allowed_hosts=_csv(
                env.get("HSO_MCP_ALLOWED_HOSTS"),
                ("localhost:*", "127.0.0.1:*", "[::1]:*"),
            ),
            mcp_allowed_origins=_csv(env.get("HSO_MCP_ALLOWED_ORIGINS")),
            release_public_key_pem=env.get("HSO_RELEASE_PUBLIC_KEY_PEM", "").replace("\\n", "\n"),
            release_public_key_id=env.get("HSO_RELEASE_PUBLIC_KEY_ID", ""),
            max_artifact_bytes=int(env.get("HSO_MAX_ARTIFACT_BYTES", str(25 * 1024 * 1024))),
            lease_seconds=int(env.get("HSO_LEASE_SECONDS", "90")),
            max_work_package_attempts=int(env.get("HSO_MAX_WORK_PACKAGE_ATTEMPTS", "4")),
        )

    def validate(self) -> None:
        if self.environment not in {"development", "test", "staging", "production"}:
            raise ValueError("HSO_ENV must be development, test, staging or production")
        if self.auth_mode not in {"disabled", "required"}:
            raise ValueError("HSO_AUTH_MODE must be disabled or required")
        if not 1024 <= self.max_artifact_bytes <= 100 * 1024 * 1024:
            raise ValueError("HSO_MAX_ARTIFACT_BYTES must be between 1 KiB and 100 MiB")
        if self.lease_seconds < 10 or self.max_work_package_attempts < 1:
            raise ValueError("Lease and retry settings are outside safe bounds")

        if self.environment in {"staging", "production"}:
            if self.auth_mode != "required":
                raise ValueError("Staging/production must use HSO_AUTH_MODE=required")
            if not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Staging/production requires PostgreSQL via psycopg")
            if not self.api_key_pepper or len(self.api_key_pepper) < 32:
                raise ValueError("HSO_API_KEY_PEPPER must be at least 32 characters")
            if not (self.oidc_issuer and self.oidc_audience and self.oidc_jwks_url):
                raise ValueError("OIDC issuer, audience and JWKS URL are required")
            if not self.mcp_allowed_hosts:
                raise ValueError("MCP host allowlist must be explicit")
            if not self.release_public_key_pem or not self.release_public_key_id:
                raise ValueError("Release verification public key and key ID are required")
            for value in (self.oidc_issuer, self.oidc_jwks_url):
                if not value.startswith("https://"):
                    raise ValueError("Production OIDC issuer/JWKS endpoints must use HTTPS")
