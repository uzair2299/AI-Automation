"""Spring Boot Internal Authentication Exchange Service Client.

Handles secure service-to-service verification of one-time bootstrap codes
issued by the Smiota Spring Boot backend and retrieves verified user identities.
"""

import httpx
from pydantic import BaseModel, Field

from smiota.core.config import get_settings
from smiota.core.exceptions import AuthenticationError, BackendServiceUnavailableError
from smiota.core.logging import logger


class BackendIdentity(BaseModel):
    """Verified identity structure returned by Spring Boot after code consumption."""
    valid: bool = Field(True, description="Whether the code was valid and consumed")
    user_id: str = Field(..., description="Verified primary user identifier")
    tenant_id: str = Field(..., description="Verified tenant identifier")
    roles: list[str] = Field(default_factory=list, description="Assigned roles")
    email: str | None = Field(None, description="User email address if available")


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
        return bool(getattr(self.settings, "SMIOTA_AUTH_DUMMY_MODE", False))

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

        return self._process_backend_response(response, masked_code)

    def _process_backend_response(self, response: httpx.Response, masked_code: str) -> BackendIdentity:
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

            # Validate contract: 'valid' flag must be True
            if data.get("valid") is not True:
                logger.warning(f"Spring Boot backend explicitly marked code {masked_code} as invalid.")
                raise AuthenticationError("Bootstrap code is invalid or has already been consumed.")

            user_id = str(data.get("user_id") or "").strip()
            tenant_id = str(data.get("tenant_id") or "").strip()

            if not user_id or not tenant_id:
                logger.error("Spring Boot 200 response missing required identity fields (user_id / tenant_id).")
                raise AuthenticationError("Incomplete identity payload received from authentication service.")

            roles = data.get("roles")
            if not isinstance(roles, list):
                roles = ["CUSTOMER"]

            email = data.get("email")
            if email is not None:
                email = str(email).strip() or None

            logger.info(f"Bootstrap code {masked_code} successfully verified for user={user_id}, tenant={tenant_id}")
            return BackendIdentity(
                valid=True,
                user_id=user_id,
                tenant_id=tenant_id,
                roles=roles,
                email=email,
            )

        # 2. Rejection statuses (invalid code, expired code, already consumed code)
        if status in (400, 401, 403, 404, 410, 422):
            logger.warning(f"Spring Boot rejected bootstrap code {masked_code} with status HTTP {status}")
            raise AuthenticationError("Bootstrap code is invalid, expired, or was already consumed.")

        # 3. Server errors / Bad gateway
        logger.error(f"Spring Boot returned server error HTTP {status} during code exchange.")
        raise BackendServiceUnavailableError(
            f"Internal authentication service returned error status {status}."
        )

    def _handle_dummy_exchange(self, code: str) -> BackendIdentity:
        """Deterministic dummy implementation for local dev/testing."""
        lower_code = code.lower()
        if any(term in lower_code for term in ("invalid", "bad", "wrong", "reject")):
            raise AuthenticationError("Bootstrap code is invalid, expired, or was already consumed.")
        if any(term in lower_code for term in ("expire", "consumed", "used")):
            raise AuthenticationError("Bootstrap code has expired or was already consumed.")
        if any(term in lower_code for term in ("timeout", "slow")):
            raise BackendServiceUnavailableError("Internal authentication service timed out.")
        if any(term in lower_code for term in ("unavail", "down", "error")):
            raise BackendServiceUnavailableError("Internal authentication service is temporarily unavailable.")
        if "malformed" in lower_code:
            raise AuthenticationError("Malformed response received from internal authentication service.")

        return BackendIdentity(
            valid=True,
            user_id="user-123",
            tenant_id="tenant-45",
            roles=["CUSTOMER"],
            email="user-123@customer.smiota.com",
        )


backend_auth_service = SmiotaBackendAuthService()
