import hashlib
import secrets

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OAuthClient
from app.schemas.oauth import ClientRegistrationRequest

log = structlog.get_logger()


def _generate_client_id() -> str:
    return secrets.token_urlsafe(32)


def _generate_client_secret() -> str:
    return secrets.token_urlsafe(48)


# SHA-256 is appropriate for high-entropy bearer-style secrets (the 48-byte
# token_urlsafe gives ~256 bits, so brute-force is not the threat). Verification
# must use hmac.compare_digest to avoid timing oracles.
def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


async def register_client(
    session: AsyncSession,
    req: ClientRegistrationRequest,
) -> tuple[OAuthClient, str | None]:
    """Insert a new client. Returns (record, plaintext_secret_if_any).

    The plaintext secret is returned only to the caller for one-time
    inclusion in the registration response; only the hash is persisted.
    """
    client_id = _generate_client_id()
    plaintext_secret: str | None = None
    secret_hash: str | None = None
    if req.token_endpoint_auth_method != "none":
        plaintext_secret = _generate_client_secret()
        secret_hash = hash_secret(plaintext_secret)

    client = OAuthClient(
        client_id=client_id,
        client_secret_hash=secret_hash,
        client_name=req.client_name or f"client_{client_id[:8]}",
        redirect_uris=list(req.redirect_uris),
        grant_types=list(req.grant_types),
        response_types=list(req.response_types),
        scope=req.scope or "",
        token_endpoint_auth_method=req.token_endpoint_auth_method,
        software_id=req.software_id,
        software_version=req.software_version,
        software_statement=req.software_statement,
    )
    session.add(client)
    log.info(
        "oauth_client_registered",
        client_id=client_id,
        software_id=req.software_id,
        software_version=req.software_version,
        redirect_uris_count=len(req.redirect_uris),
        is_confidential=plaintext_secret is not None,
    )
    return client, plaintext_secret
