"""Schemas for Spring Boot code exchange and chatbot session establishment."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class AuthExchangeRequest(BaseModel):
    """Payload to exchange a single-use bootstrap code for an authenticated chatbot session."""
    code: str = Field(..., min_length=1, description="One-time bootstrap code issued by Spring Boot backend")

    @field_validator("code")
    @classmethod
    def validate_code_not_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Bootstrap code cannot be empty or whitespace.")
        return trimmed


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
    raw_profile: dict[str, Any] | None = Field(default=None, description="Raw profile payload from Smiota Main Core")



class AuthExchangeResponse(BaseModel):
    """Response returned upon successful code exchange and session establishment."""
    token_type: str = Field("Bearer", description="Credential type")
    access_token: str = Field(..., description="Signed JWT session token for chatbot API requests")
    expires_in: int = Field(..., description="Session token lifespan in seconds")
    session_id: str = Field(..., description="Chatbot session identifier")
    user: UserIdentityInfo = Field(..., description="Verified user identity")
