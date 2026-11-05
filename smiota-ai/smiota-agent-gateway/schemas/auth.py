"""Schemas for Spring Boot code exchange and chatbot session establishment."""

from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator


class UserProfileDTO(BaseModel):
    """Verified user profile returned by Smiota Java server /internal/ai/auth/exchange."""
    valid: bool = True
    id: Optional[int] = None
    uuid: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    recipientName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    customerId: Optional[int] = None
    tenantId: Optional[int] = None
    tenantName: Optional[str] = None
    locationId: Optional[int] = None
    locationName: Optional[str] = None
    buildingId: Optional[int] = None
    buildingName: Optional[str] = None
    unitNo: Optional[str] = None
    roles: List[str] = []


class AuthExchangeRequest(BaseModel):
    """Payload to exchange a single-use bootstrap code or parent app session token for an authenticated chatbot session."""
    code: str = Field(..., min_length=1, description="One-time bootstrap code or session token issued by parent app / Spring Boot backend")
    token: str | None = Field(None, description="Session token issued by parent app (alias for code)")
    session_id: str | None = Field(None, description="Optional active session ID to resume conversation continuity")

    @model_validator(mode="before")
    @classmethod
    def resolve_code_or_token(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # If code is missing or None, try token
            if ("code" not in data or data["code"] is None) and "token" in data and data["token"] is not None:
                data["code"] = data["token"]
            raw_code = data.get("code")
            if raw_code is not None:
                trimmed = str(raw_code).strip()
                if not trimmed:
                    raise ValueError("Bootstrap code cannot be empty or whitespace.")
                data["code"] = trimmed
                data.setdefault("token", trimmed)
        return data


class UserIdentityInfo(BaseModel):
    """Public user identity metadata verified by trusted Spring Boot backend."""
    user_id: str = Field(..., description="Unique user identifier")
    tenant_id: str = Field(..., description="Tenant identifier for isolation")
    roles: list[str] = Field(default_factory=list, description="Verified roles assigned to user")
    email: str | None = Field(None, description="User email address if available")
    name: str | None = Field(None, description="User or resident full name")
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")
    phone: str | None = Field(None, description="User contact phone number")
    location_id: str | None = Field(None, description="Location identifier")
    location_name: str | None = Field(None, description="Location name")
    building_id: str | None = Field(None, description="Building identifier")
    building_name: str | None = Field(None, description="Building name")
    tenant_name: str | None = Field(None, description="Tenant company name")
    unit_no: str | None = Field(None, description="Unit or suite number")
    passcode: str | None = Field(None, description="Resident pickup or access passcode")
    parent_token: str | None = Field(None, description="Session token from parent application")
    raw_profile: dict[str, Any] | None = Field(default=None, description="Raw profile payload from Smiota Main Core")



class AuthExchangeResponse(BaseModel):
    """Response returned upon successful code exchange and session establishment."""
    token_type: str = Field("Bearer", description="Credential type")
    access_token: str = Field(..., description="Signed JWT session token for chatbot API requests")
    expires_in: int = Field(..., description="Session token lifespan in seconds")
    session_id: str = Field(..., description="Chatbot session identifier")
    user: UserIdentityInfo = Field(..., description="Verified user identity")
