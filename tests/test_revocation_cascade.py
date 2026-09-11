"""Revoking a grant must also deactivate the upstream API key behind it.

Every path that kills a grant family (the /revoke endpoint on either token
type, and refresh-token reuse detection) is covered here. The upstream is
mocked at the HTTP boundary, so no real internal traffic is generated.
"""
import base64
import hashlib
import json
import secrets
from collections.abc import Callable, Iterator

import httpx
import pytest
from httpx import AsyncClient

from app.services import odoo_internal

REVOKE_KEY_URL = "http://localhost:8069/api/internal/revoke-key"
API_KEY_ID = 4242


@pytest.fixture
def mock_upstream() -> Iterator[
    Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]]
]:
    """Install an httpx MockTransport into the upstream revoke client.

    Pass a handler, get back the list that captured requests accumulate in.
    """
    captured: list[httpx.Request] = []

    def setup(
        handler: Callable[[httpx.Request], httpx.Response],
    ) -> list[httpx.Request]:
        def wrapped(req: httpx.Request) -> httpx.Response:
            captured.append(req)
            return handler(req)

        transport = httpx.MockTransport(wrapped)
        odoo_internal.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
        return captured

    yield setup
    odoo_internal.reset_client_factory()


def _ok(_req: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"revoked": True, "api_key_id": API_KEY_ID})


def _make_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


async def _grant(client: AsyncClient) -> tuple[str, dict[str, str]]:
    """Run register -> authorize -> issue-code -> token. Returns (client_id, tokens)."""
    res = await client.post(
        "/register",
        json={"redirect_uris": ["https://example.com/cb"], "client_name": "RevokeCascade"},
    )
    client_id = res.json()["client_id"]

    verifier, challenge = _make_pkce()
    res = await client.get(
        "/authorize",
        params={
            "client_id": client_id,
            "redirect_uri": "https://example.com/cb",
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "omnidim:all",
            "state": "abc",
        },
        follow_redirects=False,
    )
    assert res.status_code == 302
    request_id = res.headers["location"].rsplit("=", 1)[1]

    res = await client.post(
        "/internal/issue-code",
        headers={"X-Internal-Secret": "test-shared-secret"},
        json={
            "request_id": request_id,
            "odoo_user_id": 2943,
            "odoo_api_key_id": API_KEY_ID,
            "odoo_api_key_value": "fake-upstream-key",
            "approved_scope": "omnidim:all",
        },
    )
    assert res.status_code == 200, res.text

    res = await client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": res.json()["code"],
            "redirect_uri": "https://example.com/cb",
            "code_verifier": verifier,
        },
    )
    assert res.status_code == 200, res.text
    return client_id, res.json()


async def _mcp_status(client: AsyncClient, access_token: str) -> int:
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    return res.status_code


def _assert_revoked_key(requests: list[httpx.Request]) -> None:
    assert len(requests) == 1, f"expected 1 upstream revoke call, got {len(requests)}"
    req = requests[0]
    assert str(req.url) == REVOKE_KEY_URL
    assert req.method == "POST"
    assert req.headers["X-Internal-Secret"] == "test-shared-secret"
    assert json.loads(req.content) == {"api_key_id": API_KEY_ID}


async def test_revoke_access_token_revokes_upstream_key(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(_ok)
    client_id, tokens = await _grant(client)

    res = await client.post(
        "/revoke", data={"client_id": client_id, "token": tokens["access_token"]}
    )
    assert res.status_code == 200
    _assert_revoked_key(requests)
    assert await _mcp_status(client, tokens["access_token"]) == 401


async def test_revoke_refresh_token_revokes_upstream_key(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(_ok)
    client_id, tokens = await _grant(client)

    res = await client.post(
        "/revoke", data={"client_id": client_id, "token": tokens["refresh_token"]}
    )
    assert res.status_code == 200
    _assert_revoked_key(requests)
    assert await _mcp_status(client, tokens["access_token"]) == 401


async def test_refresh_reuse_revokes_upstream_key(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(_ok)
    client_id, tokens = await _grant(client)

    rotated = await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": tokens["refresh_token"],
        },
    )
    assert rotated.status_code == 200
    rotated_access = rotated.json()["access_token"]
    assert not requests, "a clean rotation must not revoke the upstream key"

    replay = await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": tokens["refresh_token"],
        },
    )
    assert replay.status_code == 400
    _assert_revoked_key(requests)
    # The aborted request must not roll the local revocation back either.
    assert await _mcp_status(client, rotated_access) == 401


async def test_upstream_404_is_not_an_error(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(
        lambda _req: httpx.Response(404, json={"revoked": False, "reason": "not_found"})
    )
    client_id, tokens = await _grant(client)

    res = await client.post(
        "/revoke", data={"client_id": client_id, "token": tokens["access_token"]}
    )
    assert res.status_code == 200
    # Already gone upstream is the state we wanted, so no retry.
    assert len(requests) == 1
    assert await _mcp_status(client, tokens["access_token"]) == 401


async def test_upstream_500_does_not_block_local_revocation(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(lambda _req: httpx.Response(500, json={"error": "boom"}))
    client_id, tokens = await _grant(client)

    res = await client.post(
        "/revoke", data={"client_id": client_id, "token": tokens["access_token"]}
    )
    assert res.status_code == 200
    assert len(requests) == odoo_internal.ATTEMPTS
    assert await _mcp_status(client, tokens["access_token"]) == 401


async def test_upstream_timeout_does_not_block_local_revocation(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    def timeout(_req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("upstream is not answering")

    requests = mock_upstream(timeout)
    client_id, tokens = await _grant(client)

    res = await client.post(
        "/revoke", data={"client_id": client_id, "token": tokens["access_token"]}
    )
    assert res.status_code == 200
    assert len(requests) == odoo_internal.ATTEMPTS
    assert await _mcp_status(client, tokens["access_token"]) == 401


async def test_double_revoke_is_idempotent(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(_ok)
    client_id, tokens = await _grant(client)

    form = {"client_id": client_id, "token": tokens["access_token"]}
    assert (await client.post("/revoke", data=form)).status_code == 200
    assert (await client.post("/revoke", data=form)).status_code == 200
    # The second call finds nothing left to revoke, so the cascade fires once.
    _assert_revoked_key(requests)
    assert await _mcp_status(client, tokens["access_token"]) == 401


async def test_401_from_upstream_is_not_retried(
    client: AsyncClient, mock_upstream: Callable[..., list[httpx.Request]]
) -> None:
    requests = mock_upstream(lambda _req: httpx.Response(401, json={"error": "unauthorized"}))
    client_id, tokens = await _grant(client)

    res = await client.post(
        "/revoke", data={"client_id": client_id, "token": tokens["access_token"]}
    )
    assert res.status_code == 200
    # A bad shared secret is a config bug, not a transient one.
    assert len(requests) == 1
    assert await _mcp_status(client, tokens["access_token"]) == 401
