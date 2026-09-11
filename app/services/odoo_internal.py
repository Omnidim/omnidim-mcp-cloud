from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable
from typing import Final

import httpx
import structlog

from app.config import get_settings

log = structlog.get_logger()

TIMEOUT_SECONDS: Final = 3.0
ATTEMPTS: Final = 2
RETRY_BACKOFF_SECONDS: Final = 0.25


def _default_client_factory() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIMEOUT_SECONDS)


_client_factory: Callable[[], httpx.AsyncClient] = _default_client_factory


def set_client_factory(factory: Callable[[], httpx.AsyncClient]) -> None:
    global _client_factory
    _client_factory = factory


def reset_client_factory() -> None:
    global _client_factory
    _client_factory = _default_client_factory


async def revoke_api_keys(api_key_ids: Iterable[int], *, grant_id: str) -> None:
    """Deactivate the upstream API keys that back a grant.

    Never raises. The local revocation is authoritative and has already been
    committed by the caller, so an upstream outage must not surface as an
    error or undo it.

    ponytail: best effort with a short retry. If upstream is down for the whole
    window the key stays live and only this ERROR log records it. Closing that
    needs a persisted pending-revocation flag plus a reconciliation sweep.
    """
    settings = get_settings()
    url = f"{settings.odoo_internal_base_url.rstrip('/')}/api/internal/revoke-key"
    headers = {"X-Internal-Secret": settings.odoo_internal_shared_secret}

    for api_key_id in dict.fromkeys(api_key_ids):
        await _revoke_one(url, headers, api_key_id, grant_id)


async def _revoke_one(
    url: str, headers: dict[str, str], api_key_id: int, grant_id: str
) -> None:
    reason = "no_attempt"
    for attempt in range(ATTEMPTS):
        if attempt:
            await asyncio.sleep(RETRY_BACKOFF_SECONDS)
        try:
            async with _client_factory() as client:
                res = await client.post(url, headers=headers, json={"api_key_id": api_key_id})
        except httpx.HTTPError as exc:
            reason = type(exc).__name__
            continue
        # 404 means the key is already gone, which is the state we wanted.
        if res.status_code in (200, 404):
            log.info(
                "upstream_key_revoked",
                grant_id=grant_id,
                odoo_api_key_id=api_key_id,
                status=res.status_code,
            )
            return
        reason = f"http_{res.status_code}"
        if res.status_code < 500:
            break

    log.error(
        "upstream_key_revoke_failed",
        grant_id=grant_id,
        odoo_api_key_id=api_key_id,
        reason=reason,
    )
