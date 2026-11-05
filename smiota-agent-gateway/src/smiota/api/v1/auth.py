"""FastAPI Authentication and One-Time Bootstrap Code Exchange Router."""
from fastapi import APIRouter, Depends, status

from smiota.api.deps import get_backend_auth_service, get_chat_repo
from smiota.core.logging import logger
from smiota.core.security import create_session_token
from smiota.repositories.chat_repository import BaseChatRepository
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
    chat_repo: BaseChatRepository = Depends(get_chat_repo),  # noqa: B008
) -> AuthExchangeResponse:
    """Exchange single-use bootstrap code with trusted Spring Boot backend."""
    # 1. Atomically consume code and retrieve verified identity from Spring Boot
    identity = await auth_service.exchange_bootstrap_code(payload.code)

    # 2. Re-attach to ongoing conversation session if one exists for this resident
    active_session_id = None
    if payload.session_id:
        existing = await chat_repo.get_session(payload.session_id)
        if existing and existing.user_id == identity.user_id and existing.tenant_id == identity.tenant_id:
            active_session_id = existing.session_id

    if not active_session_id:
        existing_sessions = await chat_repo.list_user_sessions(
            user_id=identity.user_id,
            tenant_id=identity.tenant_id,
        )
        if existing_sessions:
            active_session_id = existing_sessions[0].session_id

    parent_tok = identity.parent_token or getattr(payload, "token", None) or payload.code or ""
    user_info_dict = {
        "user_id": identity.user_id,
        "tenant_id": identity.tenant_id,
        "name": identity.name or "",
        "first_name": identity.first_name or "",
        "last_name": identity.last_name or "",
        "email": identity.email or "",
        "phone": identity.phone or "",
        "tenant_name": identity.tenant_name or "",
        "location_id": identity.location_id or "",
        "location_name": identity.location_name or "",
        "building_id": identity.building_id or "",
        "building_name": identity.building_name or "",
        "unit_no": identity.unit_no or "",
        "roles": identity.roles,
        "parent_token": parent_tok,
    }

    # 3. Establish signed JWT session for the chatbot storing complete user information
    token, session_id, expires_in = create_session_token(
        user_id=identity.user_id,
        tenant_id=identity.tenant_id,
        roles=identity.roles,
        email=identity.email,
        name=identity.name,
        location_id=identity.location_id,
        session_id=active_session_id,
        first_name=identity.first_name,
        last_name=identity.last_name,
        phone=identity.phone,
        tenant_name=identity.tenant_name,
        location_name=identity.location_name,
        building_id=identity.building_id,
        building_name=identity.building_name,
        unit_no=identity.unit_no,
        parent_token=parent_tok,
        user_profile=identity.raw_profile,
    )

    # 4. Attach complete user necessary info to chat session
    await chat_repo.get_or_create_session(
        session_id=session_id,
        user_id=identity.user_id,
        tenant_id=identity.tenant_id,
        channel="webchat",
        metadata={
            "user": user_info_dict,
            "user_id": identity.user_id,
            "tenant_id": identity.tenant_id,
            "user_name": identity.name,
            "email": identity.email,
            "phone": identity.phone,
            "unit_no": identity.unit_no,
            "building_id": identity.building_id,
            "location_id": identity.location_id,
            "parent_token": parent_tok,
        },
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
