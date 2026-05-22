from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.dependencies import get_session_factory
from app.schemas.oauth import ClientRegistrationRequest, ClientRegistrationResponse
from app.services.clients import register_client

router = APIRouter(tags=["oauth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ClientRegistrationResponse,
    response_model_exclude_none=True,
)
async def register(
    body: ClientRegistrationRequest,
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> ClientRegistrationResponse:
    async with factory() as session:
        client, secret = await register_client(session, body)
        await session.commit()
        await session.refresh(client)

    return ClientRegistrationResponse(
        client_id=client.client_id,
        client_id_issued_at=int(client.created_at.timestamp()),
        redirect_uris=client.redirect_uris,
        grant_types=client.grant_types,
        response_types=client.response_types,
        token_endpoint_auth_method=client.token_endpoint_auth_method,
        client_name=client.client_name,
        scope=client.scope or None,
        software_id=client.software_id,
        software_version=client.software_version,
        client_secret=secret,
        client_secret_expires_at=0 if secret else None,
    )
