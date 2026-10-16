"""Authentication, OIDC token validation, and Role-Based Access Control (RBAC)."""
from typing import Optional
from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str
    roles: list[str] = ["user"]
    tenant_id: str = "default"


async def get_current_user_stub() -> AuthenticatedUser:
    """Mock/stub for authentication in local development.

    In production, this validates JWTs issued by Google Cloud Identity / Okta / Azure AD.
    """
    return AuthenticatedUser(
        user_id="user-123",
        email="sre.engineer@smiota.com",
        roles=["sre", "developer", "admin"],
        tenant_id="smiota-internal",
    )
