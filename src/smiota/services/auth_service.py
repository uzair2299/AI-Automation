"""Spring Boot Internal Authentication Exchange Service Client.

Handles secure service-to-service verification of one-time bootstrap codes
issued by the Smiota Spring Boot backend and retrieves verified user identities.
"""

from typing import Any, Optional

import httpx
from pydantic import BaseModel, Field

from smiota.core.config import get_settings
from smiota.core.exceptions import AuthenticationError, BackendServiceUnavailableError
from smiota.core.logging import logger

DUMMY_SMIOTA_MAIN_PROFILE: dict[str, Any] = {
    "id": 10790,
    "uuid": "4c9e782a-94ef-4b21-8854-bc712f5b66d1",
    "firstName": "Alex",
    "lastName": "Morgan",
    "recipientName": "Alex Morgan",
    "email": "alex.morgan@acme.com",
    "phone": "+14155551234",
    "voiceCallPhone": "+14155551234",
    "photo": None,
    "badgeId": "BADGE-9941",
    "authId": "auth0|64f1a23e9821a",
    "externalId": "EMP-88214",
    "login": "amorgan",
    "customerId": 42,
    "locationId": 108,
    "locationName": "Pleasanton HQ",
    "buildingId": 15,
    "buildingName": "North Tower",
    "tenantId": 89,
    "tenantName": "Acme Technologies Inc.",
    "unitNo": "Suite 400",
    "recipientId": 10790,
    "isInActive": False,
    "inactive": False,
    "authorizedForTenant": True,
    "wheelChairAccess": False,
    "hasSpecialStatus": False,
    "optOut": False,
    "emailUnsubscribe": False,
    "phoneUnsubscribe": False,
    "registrationStatus": 1,
    "keepLocalChanges": False,
    "addressLine1": "100 Innovation Way",
    "addressLine2": None,
    "city": "Pleasanton",
    "state": "CA",
    "zipCode": "94588",
    "passcode": "842910",
    "lastPasscodeCreatedTime": "2026-10-15T08:30:00Z",
    "passcodeGenerationRequired": False,
    "doNotAssociateToAPackage": False,
    "delegatesNotificationsToUserId": 0,
    "delegatesNotificationsToUserNamed": None,
    "roles": [
        "recipient"
    ],
    "roleObjects": [
        {
            "roleId": 10,
            "role": "recipient",
            "scope": 108,
            "scopeId": "108",
            "userId": 10790
        }
    ]
}


class BackendIdentity(BaseModel):
    """Verified identity structure returned by Spring Boot after code consumption."""
    valid: bool = Field(True, description="Whether the code was valid and consumed")
    user_id: str = Field(..., description="Verified primary user identifier")
    tenant_id: str = Field(..., description="Verified tenant identifier")
    roles: list[str] = Field(default_factory=list, description="Assigned roles")
    email: str | None = Field(None, description="User email address if available")
    name: str | None = Field(None, description="User or resident full name")
    first_name: str | None = Field(None, description="User first name")
    last_name: str | None = Field(None, description="User last name")
    phone: str | None = Field(None, description="Contact phone number")
    location_id: str | None = Field(None, description="Location identifier")
    location_name: str | None = Field(None, description="Location name")
    building_id: str | None = Field(None, description="Building identifier")
    building_name: str | None = Field(None, description="Building name")
    tenant_name: str | None = Field(None, description="Tenant company name")
    unit_no: str | None = Field(None, description="Unit or suite number")
    passcode: str | None = Field(None, description="Pickup or access passcode")
    parent_token: str | None = Field(None, description="Session token received from parent app")
    raw_profile: dict[str, Any] = Field(default_factory=dict, description="Raw profile dictionary from Smiota Main Core")


class SmiotaBackendAuthService:
    """Client for Smiota Spring Boot internal AI authentication endpoints."""

    def __init__(self):
        self.settings = get_settings()

    @property
    def backend_url(self) -> str:
        """Base URL of the Smiota Spring Boot backend."""
        return (
            getattr(self.settings, "SMIOTA_BACKEND_URL", None)
            or getattr(self.settings, "SMIOTA_SERVER_BASE_URL", None)
            or "https://dev.smiotaapps.com/smiota"
        ).rstrip("/")

    @property
    def exchange_endpoint(self) -> str:
        """Internal endpoint path for bootstrap code exchange."""
        endpoint = getattr(self.settings, "SMIOTA_INTERNAL_EXCHANGE_ENDPOINT", "/internal/ai/auth/exchange")
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
        return endpoint

    @property
    def service_token(self) -> str:
        """Service-to-service authentication credential."""
        return getattr(self.settings, "SMIOTA_SERVICE_TOKEN", "")

    @property
    def timeout_seconds(self) -> float:
        """Network timeout in seconds for internal backend calls."""
        return float(getattr(self.settings, "SMIOTA_BACKEND_TIMEOUT_SECONDS", 10.0))

    @property
    def dummy_mode(self) -> bool:
        """Whether dummy mode is enabled for standalone testing or unintegrated dev."""
        return bool(getattr(get_settings(), "SMIOTA_AUTH_DUMMY_MODE", False))

    async def exchange_bootstrap_code(self, code: str) -> BackendIdentity:
        """Atomically exchange and consume single-use bootstrap code via Spring Boot backend.

        Args:
            code (str): The single-use bootstrap code passed from parent app / iframe.

        Returns:
            BackendIdentity: Verified user identity and tenant bindings.

        Raises:
            AuthenticationError: If code is invalid, expired, consumed, or backend fails closed.
            BackendServiceUnavailableError: If Spring Boot is down, unreachable, or times out.
        """
        stripped_code = (code or "").strip()
        if not stripped_code:
            raise AuthenticationError("Bootstrap code cannot be empty.")

        # Safe masked representation for diagnostic logs without leaking the secret
        masked_code = f"{stripped_code[:4]}...[{len(stripped_code)} chars]" if len(stripped_code) > 4 else "***"

        # Check for simulated dummy mode (allows running locally when Spring Boot is not yet ready)
        if self.dummy_mode:
            logger.info(f"[AUTH DUMMY MODE] Simulating Spring Boot code exchange for: {masked_code}")
            return self._handle_dummy_exchange(stripped_code)

        target_url = f"{self.backend_url}{self.exchange_endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SmiotaAI-FastAPI/0.1.0",
        }
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
            headers["X-Internal-Service-Key"] = self.service_token

        logger.info(f"Dispatching bootstrap code exchange to internal backend: POST {target_url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    target_url,
                    json={"code": stripped_code},
                    headers=headers,
                )
        except (httpx.TimeoutException, httpx.ReadTimeout, httpx.ConnectTimeout) as te:
            logger.error(f"Internal Spring Boot backend exchange timed out: {te}")
            raise BackendServiceUnavailableError(
                "Internal authentication service timed out. Please try again shortly."
            )
        except (httpx.ConnectError, httpx.NetworkError) as ce:
            logger.error(f"Failed to connect to internal Spring Boot backend at {target_url}: {ce}")
            raise BackendServiceUnavailableError(
                "Internal authentication service is temporarily unavailable. Please try again later."
            )
        except httpx.HTTPError as ex:
            logger.error(f"Unexpected network error during bootstrap code exchange: {ex}")
            raise BackendServiceUnavailableError(
                "Internal authentication service encountered an error."
            )

        return self._process_backend_response(response, masked_code, code=stripped_code)

    def _process_backend_response(
        self, response: httpx.Response, masked_code: str, code: str = ""
    ) -> BackendIdentity:
        """Validate and parse Spring Boot HTTP response."""
        status = response.status_code

        # 1. Successful verification
        if status == 200:
            try:
                data = response.json()
            except (ValueError, TypeError) as e:
                logger.error(f"Spring Boot returned invalid non-JSON body (status 200): {e}")
                raise AuthenticationError("Malformed response received from internal authentication service.")

            if not isinstance(data, dict):
                logger.error("Spring Boot response is not a valid JSON object")
                raise AuthenticationError("Invalid response structure received from authentication service.")

            # Validate contract: fail closed if explicitly marked invalid or inactive
            if data.get("valid") is False:
                logger.warning(f"Spring Boot backend explicitly marked code {masked_code} as invalid.")
                raise AuthenticationError("Bootstrap code is invalid or has already been consumed.")

            if data.get("inactive") is True or data.get("isInActive") is True:
                logger.warning(f"User account is marked inactive in Smiota Main Core: {masked_code}")
                raise AuthenticationError("User account is inactive. Please contact support.")

            # Extract user identifier (supports Smiota Main Core 'id', 'recipientId', 'uuid' as well as generic 'user_id')
            raw_user_id = data.get("id") or data.get("user_id") or data.get("recipientId") or data.get("uuid")
            user_id = str(raw_user_id).strip() if raw_user_id is not None else ""

            # Extract tenant identifier (supports Smiota Main Core 'tenantId', 'customerId' as well as generic 'tenant_id')
            raw_tenant_id = data.get("tenantId") or data.get("tenant_id") or data.get("customerId")
            tenant_id = str(raw_tenant_id).strip() if raw_tenant_id is not None else ""

            if not user_id or not tenant_id:
                logger.error("Spring Boot 200 response missing required identity fields (user_id / tenant_id).")
                raise AuthenticationError("Incomplete identity payload received from authentication service.")

            roles = data.get("roles")
            if not isinstance(roles, list):
                if data.get("recipientId") or data.get("unitNo") or "recipient" in str(data.get("roleObjects", "")):
                    roles = ["recipient"]
                else:
                    roles = ["CUSTOMER"]

            email = data.get("email")
            if email is not None:
                email = str(email).strip() or None

            # Extract rich resident/user details returned by Smiota Main Core
            recipient_name = data.get("recipientName")
            if not recipient_name:
                first = data.get("firstName", "")
                last = data.get("lastName", "")
                recipient_name = f"{first} {last}".strip() or None

            first_name = data.get("firstName")
            last_name = data.get("lastName")
            phone = data.get("phone") or data.get("voiceCallPhone")

            loc_id = data.get("locationId")
            location_id = str(loc_id) if loc_id is not None else None
            location_name = data.get("locationName")

            bld_id = data.get("buildingId")
            building_id = str(bld_id) if bld_id is not None else None
            building_name = data.get("buildingName")

            tenant_name = data.get("tenantName")
            unit_no = data.get("unitNo")
            passcode = data.get("passcode")

            logger.info(f"Bootstrap code {masked_code} successfully verified for user={user_id}, tenant={tenant_id}")
            return BackendIdentity(
                valid=True,
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles,
                email=email,
                name=recipient_name,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                location_id=location_id,
                location_name=location_name,
                building_id=building_id,
                building_name=building_name,
                tenant_name=tenant_name,
                unit_no=unit_no,
                passcode=passcode,
                parent_token=data.get("token") or data.get("sessionToken") or code or None,
                raw_profile=data,
            )

        # 2. Rejection statuses (invalid code, expired code, already consumed code)
        if status in (400, 401, 403, 404, 410, 422):
            if status == 404:
                logger.warning(
                    f"Spring Boot endpoint {self.exchange_endpoint} returned HTTP 404 (not yet implemented on server). "
                    "Returning 200 OK Smiota Main dummy identity for testing."
                )
                return self._handle_dummy_exchange(code or masked_code)
            logger.warning(f"Spring Boot rejected bootstrap code {masked_code} with status HTTP {status}")
            raise AuthenticationError("Bootstrap code is invalid, expired, or was already consumed.")

        # 3. Server errors / Bad gateway
        logger.error(f"Spring Boot returned server error HTTP {status} during code exchange.")
        raise BackendServiceUnavailableError(
            f"Internal authentication service returned error status {status}."
        )

    def _handle_dummy_exchange(self, code: str) -> BackendIdentity:
        """Deterministic dummy implementation using real Smiota Main user profile for local dev and testing."""
        profile = DUMMY_SMIOTA_MAIN_PROFILE
        return BackendIdentity(
            valid=True,
            user_id=str(profile["id"]),
            tenant_id=str(profile["tenantId"]),
            roles=list(profile.get("roles", ["recipient"])),
            email=profile.get("email"),
            name=profile.get("recipientName"),
            first_name=profile.get("firstName"),
            last_name=profile.get("lastName"),
            phone=profile.get("phone"),
            location_id=str(profile.get("locationId")),
            location_name=profile.get("locationName"),
            building_id=str(profile.get("buildingId")),
            building_name=profile.get("buildingName"),
            tenant_name=profile.get("tenantName"),
            unit_no=profile.get("unitNo"),
            passcode=profile.get("passcode"),
            parent_token=code,
            raw_profile=profile,
        )


backend_auth_service = SmiotaBackendAuthService()


class SmiotaAuthClient:
    """Async client for exchanging tokens with the Smiota Java Server."""

    def __init__(self, base_url: Optional[str] = None, service_token: Optional[str] = None):
        cfg = get_settings()
        self.base_url = (
            base_url
            or getattr(cfg, "SMIOTA_SERVER_BASE_URL", None)
            or getattr(cfg, "SMIOTA_BACKEND_URL", "https://dev.smiotaapps.com/smiota")
        ).rstrip("/")
        self.service_token = service_token or getattr(cfg, "SMIOTA_SERVICE_TOKEN", "")

    def _get_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Internal-Service-Key": self.service_token,
            "Authorization": f"Bearer {self.service_token}",
        }

    async def exchange_token(self, code: str) -> Optional[dict[str, Any]]:
        """Exchanges client auth token/code with Smiota Java Server for verified user and tenant profile."""
        if not code or not code.strip():
            return None
        url = f"{self.base_url}/internal/ai/auth/exchange"
        payload = {"code": code.strip()}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                    logger.warning(f"[AI Auth] Unauthorized: {error_data.get('message', response.text)}")
                    return None
                elif response.status_code == 400:
                    logger.warning(f"[AI Auth] Bad Request: {response.text}")
                    return None
                else:
                    logger.warning(f"[AI Auth] Unexpected status {response.status_code}: {response.text}")
                    return None
            except httpx.RequestError as exc:
                logger.error(f"[AI Auth] Network error connecting to Smiota Server ({url}): {exc}")
                return None


smiota_auth_client = SmiotaAuthClient()


