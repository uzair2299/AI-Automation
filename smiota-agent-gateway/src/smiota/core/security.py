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
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    roles: list[str] = ["user"]
    tenant_id: str = "default"
    tenant_name: str = ""
    location_id: str = ""
    location_name: str = ""
    building_id: str = ""
    building_name: str = ""
    unit_no: str = ""
    parent_token: str | None = None
    session_id: str | None = None
    user_profile: dict[str, Any] = {}

    def to_user_info_dict(self) -> dict[str, Any]:
        """Return standardized necessary user information object."""
        return {
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "tenant_name": self.tenant_name,
            "location_id": self.location_id,
            "location_name": self.location_name,
            "building_id": self.building_id,
            "building_name": self.building_name,
            "unit_no": self.unit_no,
            "roles": self.roles,
            "parent_token": self.parent_token,
        }


def create_session_token(
    user_id: str,
    tenant_id: str,
    roles: list[str],
    email: str | None = None,
    session_id: str | None = None,
    name: str | None = None,
    location_id: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    tenant_name: str | None = None,
    location_name: str | None = None,
    building_id: str | None = None,
    building_name: str | None = None,
    unit_no: str | None = None,
    parent_token: str | None = None,
    user_profile: dict[str, Any] | None = None,
) -> tuple[str, str, int]:
    """Issue a tamper-proof signed JWT session token storing complete user information.

    Returns:
        tuple[str, str, int]: (jwt_token, session_id, expires_in_seconds)
    """
    settings = get_settings()
    active_session_id = session_id or f"sess-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    exp = now + expires_delta
    expires_in_seconds = int(expires_delta.total_seconds())

    display_name = name or f"{first_name or ''} {last_name or ''}".strip() or None

    user_info = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "name": display_name or "",
        "first_name": first_name or "",
        "last_name": last_name or "",
        "email": email or "",
        "phone": phone or "",
        "tenant_name": tenant_name or "",
        "location_id": location_id or "",
        "location_name": location_name or "",
        "building_id": building_id or "",
        "building_name": building_name or "",
        "unit_no": unit_no or "",
        "roles": roles,
        "parent_token": parent_token or "",
    }
    if user_profile:
        for k, v in user_profile.items():
            if k not in user_info and v is not None:
                user_info[k] = v

    payload = {
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "sub": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "email": email or "",
        "name": display_name or "",
        "first_name": first_name or "",
        "last_name": last_name or "",
        "phone": phone or "",
        "tenant_name": tenant_name or "",
        "location_id": location_id or "",
        "location_name": location_name or "",
        "building_id": building_id or "",
        "building_name": building_name or "",
        "unit_no": unit_no or "",
        "parent_token": parent_token or "",
        "session_id": active_session_id,
        "user": user_info,  # Complete user information object stored in token!
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

