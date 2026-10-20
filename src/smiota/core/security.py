"""Authentication, JWT session token issuance, validation, and Role-Based Access Control (RBAC)."""
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pydantic import BaseModel

from smiota.core.config import get_settings
from smiota.core.exceptions import AuthenticationError


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str = ""
    roles: list[str] = ["user"]
    tenant_id: str = "default"
    session_id: str | None = None


def create_session_token(
    user_id: str,
    tenant_id: str,
    roles: list[str],
    email: str | None = None,
    session_id: str | None = None,
) -> tuple[str, str, int]:
    """Issue a tamper-proof signed JWT session token for an authenticated chatbot session.

    Returns:
        tuple[str, str, int]: (jwt_token, session_id, expires_in_seconds)
    """
    settings = get_settings()
    active_session_id = session_id or f"sess-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    exp = now + expires_delta
    expires_in_seconds = int(expires_delta.total_seconds())

    payload = {
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "sub": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "email": email or "",
        "session_id": active_session_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": uuid.uuid4().hex,
    }

    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, active_session_id, expires_in_seconds


def verify_session_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT session token.

    Validates signature, algorithm, expiration, issuer, audience, and essential claims.
    Raises AuthenticationError on invalid, expired, or tampered tokens.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options={
                "require": ["exp", "iat", "sub", "tenant_id", "iss", "aud"],
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
                "verify_aud": True,
            },
        )
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Chatbot session token has expired. Please re-authenticate.")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid or tampered session token: {e}")
    except (jwt.PyJWTError, ValueError, KeyError, TypeError) as e:
        raise AuthenticationError(f"Failed to validate session token: {e}")

    user_id = str(payload.get("sub") or "").strip()
    tenant_id = str(payload.get("tenant_id") or "").strip()

    if not user_id or not tenant_id:
        raise AuthenticationError("Session token missing required identity claims (sub or tenant_id).")

    return payload


async def get_current_user_stub() -> AuthenticatedUser:
    """Mock/stub for authentication in local development."""
    return AuthenticatedUser(
        user_id="user-123",
        email="sre.engineer@smiota.com",
        roles=["sre", "developer", "admin"],
        tenant_id="smiota-internal",
        session_id="sess-dev-stub-001",
    )

