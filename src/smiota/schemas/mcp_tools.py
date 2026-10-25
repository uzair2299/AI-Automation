"""Pydantic schemas and standard result envelopes for Smiota Customer MCP Tools."""
import re
from enum import Enum
from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class ToolResultCode(str, Enum):
    """Standardized business and technical outcome codes across all Smiota MCP tools."""
    SUCCESS = "SUCCESS"
    EMPTY_RESULT = "EMPTY_RESULT"
    INVALID_INPUT = "INVALID_INPUT"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    ACCESS_DENIED = "ACCESS_DENIED"
    INVALID_IDENTIFIER = "INVALID_IDENTIFIER"
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMITED = "RATE_LIMITED"
    UPSTREAM_TIMEOUT = "UPSTREAM_TIMEOUT"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    UNEXPECTED_RESPONSE = "UNEXPECTED_RESPONSE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class SmiotaToolResult(BaseModel):
    """Production-grade standardized envelope for all Smiota MCP tool execution results."""
    success: bool = Field(..., description="Whether the tool operation succeeded")
    status: ToolResultCode = Field(..., description="Stable outcome status code")
    message: str = Field(..., description="User-safe, concise explanation of the outcome")
    data: Optional[Any] = Field(None, description="Validated structured business payload")
    correlation_id: Optional[str] = Field(None, description="Request correlation identifier for traceability")
    requires_auth: bool = Field(False, description="True if customer must log in to view requested data")
    requires_input: bool = Field(False, description="True if additional information is required from the customer")
    missing_fields: List[str] = Field(default_factory=list, description="Fields required to continue the workflow")

    @classmethod
    def success_result(cls, data: Any, message: str = "Operation completed successfully.", correlation_id: Optional[str] = None) -> "SmiotaToolResult":
        return cls(
            success=True,
            status=ToolResultCode.SUCCESS,
            message=message,
            data=data,
            correlation_id=correlation_id,
        )

    @classmethod
    def empty_result(cls, message: str = "No matching packages or records found.", correlation_id: Optional[str] = None) -> "SmiotaToolResult":
        return cls(
            success=True,
            status=ToolResultCode.EMPTY_RESULT,
            message=message,
            data={"total_count": 0, "packages": []},
            correlation_id=correlation_id,
        )

    @classmethod
    def auth_required(cls, message: str = "You’re using Smiota Support as a guest. For your privacy and security, please log in to your Smiota account.", correlation_id: Optional[str] = None) -> "SmiotaToolResult":
        return cls(
            success=False,
            status=ToolResultCode.AUTHENTICATION_REQUIRED,
            message=message,
            data=None,
            correlation_id=correlation_id,
            requires_auth=True,
        )

    @classmethod
    def not_found(cls, message: str = "Package or record not found.", correlation_id: Optional[str] = None) -> "SmiotaToolResult":
        return cls(
            success=False,
            status=ToolResultCode.NOT_FOUND,
            message=message,
            data=None,
            correlation_id=correlation_id,
        )

    @classmethod
    def invalid_input(cls, message: str, missing_fields: Optional[List[str]] = None, correlation_id: Optional[str] = None) -> "SmiotaToolResult":
        return cls(
            success=False,
            status=ToolResultCode.INVALID_INPUT,
            message=message,
            data=None,
            correlation_id=correlation_id,
            requires_input=True,
            missing_fields=missing_fields or [],
        )

    @classmethod
    def error_result(cls, status: ToolResultCode, message: str, correlation_id: Optional[str] = None) -> "SmiotaToolResult":
        return cls(
            success=False,
            status=status,
            message=message,
            data=None,
            correlation_id=correlation_id,
        )


# ==============================================================================
# Tool Input Schemas
# ==============================================================================

class SearchPackagesInput(BaseModel):
    """Input parameters for searching and summarizing packages."""
    status_group: Optional[Literal["PENDING", "RELEASED", "OUTBOUND", "ALL"]] = Field(
        default="PENDING",
        description="Filter by package lifecycle group: PENDING (awaiting pickup), RELEASED (collected history), OUTBOUND (returns), ALL.",
    )
    status: Optional[str] = Field(
        default=None,
        description=(
            "Optional specific package status filter. Supported Smiota statuses: "
            "'pickup_request_submitted', 'received', 'delivered_to_station', 'released', "
            "'sent back', 'attempted to deliver', 'courier to mailroom', 'in transit', "
            "'return to hub', 'Ready to Ship', 'In Transit to Warehouse', 'In Transit to Pod', "
            "'Hold', 'In Warehouse', 'Research', 'Transferred', 'Processed'."
        ),
    )
    carrier: Optional[str] = Field(
        default=None,
        description="Optional carrier filter (e.g., 'Amazon', 'FedEx', 'UPS', 'USPS', 'DHL'). Substring match.",
        max_length=50,
    )
    storage_type: Optional[Literal["ALL", "LOCKER", "SHELF"]] = Field(
        default="ALL",
        description="Filter by storage location: 'LOCKER' (smart locker compartment), 'SHELF' (mailroom shelf/counter), or 'ALL'.",
    )
    days: Optional[int] = Field(
        default=None,
        description="Historical lookback window in days (e.g. 0 for today, 30 for past month, 90 for past quarter). Maximum 365.",
        ge=0,
        le=365,
    )
    is_perishable: Optional[bool] = Field(
        default=None,
        description="Filter for temperature-sensitive / cold storage / grocery items.",
    )

    @field_validator("carrier")
    @classmethod
    def sanitize_carrier(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = re.sub(r"[^\w\s-]", "", v).strip()
        return cleaned or None


class GetPackageDetailsInput(BaseModel):
    """Input parameters for retrieving 360-degree attributes of a specific package."""
    identifier: str = Field(
        ...,
        description="Carrier tracking number (e.g. '1Z9999999999999999'), package UUID, PO number (e.g. 'PO-88421'), or release passcode.",
        min_length=1,
        max_length=100,
    )

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Package identifier cannot be empty.")
        if re.search(r"[\x00-\x1f\x7f;<>'\"`]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b", cleaned, re.IGNORECASE):
            raise ValueError("Package identifier contains invalid characters.")
        return cleaned


class GetPackageTimelineInput(BaseModel):
    """Input parameters for retrieving package chain-of-custody and delivery audit timeline."""
    identifier: str = Field(
        ...,
        description="Carrier tracking number or package ID to trace audit timeline and dock reconciliation for.",
        min_length=1,
        max_length=100,
    )

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Package identifier cannot be empty.")
        if re.search(r"[\x00-\x1f\x7f;<>'\"`]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b", cleaned, re.IGNORECASE):
            raise ValueError("Package identifier contains invalid characters.")
        return cleaned


class GetUserPreferencesAndServicesInput(BaseModel):
    """Input parameters for checking accessibility, proxy delegates, and personal day-use pods."""
    pass


class GetPickupPinInput(BaseModel):
    """Input parameters for retrieving the 6-digit pickup PIN and locker door."""
    identifier: Optional[str] = Field(
        default=None,
        description="Optional tracking number, package UUID, or PO number. If omitted, retrieves PIN for the resident's active pending delivery.",
        max_length=100,
    )

    @field_validator("identifier")
    @classmethod
    def sanitize_identifier(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if re.search(r"[\x00-\x1f\x7f;<>'\"`]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b", cleaned, re.IGNORECASE):
            raise ValueError("Package identifier contains invalid characters.")
        return cleaned or None


class GetLockerDetailsInput(BaseModel):
    """Input parameters for looking up locker compartment door, bank, and location."""
    identifier: Optional[str] = Field(
        default=None,
        description="Optional tracking number or package ID. If omitted, retrieves locker details for the resident's active pending delivery.",
        max_length=100,
    )

    @field_validator("identifier")
    @classmethod
    def sanitize_identifier(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        if re.search(r"[\x00-\x1f\x7f;<>'\"`]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b", cleaned, re.IGNORECASE):
            raise ValueError("Package identifier contains invalid characters.")
        return cleaned or None
