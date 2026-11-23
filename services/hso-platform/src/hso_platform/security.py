from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256

import jwt
from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import APIKey
from .settings import Settings


@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: frozenset[str]
    auth_method: str


def _secret_hash(token: str, pepper: str) -> str:
    return hmac.new(pepper.encode("utf-8"), token.encode("utf-8"), sha256).hexdigest()


def create_api_key(session: Session, subject: str, scopes: list[str], pepper: str, expires_at=None):
    token = "hso_live_" + secrets.token_urlsafe(32)
    key_id = secrets.token_hex(16)
    prefix = token[:24]
    record = APIKey(
        key_id=key_id,
        prefix=prefix,
        secret_hash=_secret_hash(token, pepper),
        subject=subject,
        scopes=sorted(set(scopes)),
        expires_at=expires_at,
    )
    session.add(record)
    session.flush()
    return token, record


@lru_cache(maxsize=8)
def _jwks_client(url: str):
    return jwt.PyJWKClient(url, cache_keys=True, timeout=5)


def _principal_from_bearer(token: str, settings: Settings) -> Principal:
    if not (settings.oidc_issuer and settings.oidc_audience and settings.oidc_jwks_url):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OIDC is not configured")
    try:
        signing_key = _jwks_client(settings.oidc_jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
            options={"require": ["exp", "iat", "iss", "sub", "aud"]},
            leeway=30,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token") from exc

    raw_scopes = claims.get("scope", "")
    scopes = raw_scopes.split() if isinstance(raw_scopes, str) else raw_scopes
    if not isinstance(scopes, list) or any(not isinstance(item, str) for item in scopes):
        scopes = []
    return Principal(subject=str(claims["sub"]), scopes=frozenset(scopes), auth_method="oidc")


def authenticate(request: Request, session: Session, settings: Settings) -> Principal:
    authorization = request.headers.get("authorization", "")
    api_key = request.headers.get("x-api-key", "")

    if authorization.lower().startswith("bearer "):
        return _principal_from_bearer(authorization[7:].strip(), settings)

    if api_key:
        if not settings.api_key_pepper:
            raise HTTPException(status_code=503, detail="API-key authentication is not configured")
        prefix = api_key[:24]
        record = session.scalar(select(APIKey).where(APIKey.prefix == prefix, APIKey.revoked_at.is_(None)))
        if not record:
            raise HTTPException(status_code=401, detail="Invalid API key")
        expected = _secret_hash(api_key, settings.api_key_pepper)
        if not hmac.compare_digest(expected, record.secret_hash):
            raise HTTPException(status_code=401, detail="Invalid API key")
        now = datetime.now(timezone.utc)
        if record.expires_at and record.expires_at <= now:
            raise HTTPException(status_code=401, detail="API key expired")
        record.last_used_at = now
        return Principal(subject=record.subject, scopes=frozenset(record.scopes), auth_method="api_key")

    if settings.auth_mode == "disabled" and settings.environment in {"development", "test"}:
        return Principal(
            subject="local-development",
            scopes=frozenset({
                "registry:read", "registry:write", "workflow:read", "workflow:write",
                "workflow:execute", "workers:manage", "keys:manage", "entitlements:manage",
                "package:publish", "package:install", "audit:read", "mcp:invoke",
                "metrics:read", "outbox:manage",
            }),
            auth_method="development-bypass",
        )

    raise HTTPException(status_code=401, detail="Authentication required")


def require_scope(scope: str):
    def dependency(request: Request) -> Principal:
        principal = getattr(request.state, "principal", None)
        if principal is None:
            factory = request.app.state.session_factory
            settings = request.app.state.settings
            with factory() as session:
                principal = authenticate(request, session, settings)
        if scope not in principal.scopes:
            raise HTTPException(status_code=403, detail=f"Missing required scope: {scope}")
        return principal
    return dependency
