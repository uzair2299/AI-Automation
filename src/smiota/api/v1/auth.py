"""FastAPI Authentication and One-Time Bootstrap Code Exchange Router."""
from fastapi import APIRouter, Depends, status

from smiota.api.deps import get_backend_auth_service
from smiota.core.logging import logger
from smiota.core.security import create_session_token
from smiota.schemas.auth import (
    AuthExchangeRequest,
    AuthExchangeResponse,
    UserIdentityInfo,
)
from smiota.services.auth_service import SmiotaBackendAuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Session Exchange"])


@router.post(
    "/exchange",
    response_model=AuthExchangeResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange Spring Boot bootstrap code for authenticated chatbot session",
    description=(
        "Consumes a single-use bootstrap code issued by the Spring Boot backend, "
        "validates user identity and tenant bindings, and issues a tamper-proof "
        "JWT session token for subsequent chatbot interactions."
    ),
)
async def exchange_bootstrap_code(
    payload: AuthExchangeRequest,
    auth_service: SmiotaBackendAuthService = Depends(get_backend_auth_service),  # noqa: B008
) -> AuthExchangeResponse:
    """Exchange single-use bootstrap code with trusted Spring Boot backend."""
    # 1. Atomically consume code and retrieve verified identity from Spring Boot
    identity = await auth_service.exchange_bootstrap_code(payload.code)

    # 2. Establish signed JWT session for the chatbot
    token, session_id, expires_in = create_session_token(
        user_id=identity.user_id,
        tenant_id=identity.tenant_id,
        roles=identity.roles,
        email=identity.email,
        name=identity.name,
        location_id=identity.location_id,
    )

    logger.info(
        f"Authenticated chatbot session established: session_id={session_id}, "
        f"user_id={identity.user_id}, tenant_id={identity.tenant_id}, name={identity.name}"
    )

    return AuthExchangeResponse(
        token_type="Bearer",
        access_token=token,
        expires_in=expires_in,
        session_id=session_id,
        user=UserIdentityInfo(
            user_id=identity.user_id,
            tenant_id=identity.tenant_id,
            roles=identity.roles,
            email=identity.email,
            name=identity.name,
            first_name=identity.first_name,
            last_name=identity.last_name,
            phone=identity.phone,
            location_id=identity.location_id,
            location_name=identity.location_name,
            building_id=identity.building_id,
            building_name=identity.building_name,
            tenant_name=identity.tenant_name,
            unit_no=identity.unit_no,
            passcode=identity.passcode,
            raw_profile=identity.raw_profile,
        ),
    )
