import secrets

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import AuthorizationRequest

VALID_PKCE_CHALLENGE = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


async def _register_public_client(
    client: AsyncClient, redirect_uri: str = "https://example.com/cb"
) -> str:
    res = await client.post(
        "/register",
        json={
            "redirect_uris": [redirect_uri],
            "client_name": "Test",
        },
    )
    return res.json()["client_id"]


def _base_params(client_id: str, **overrides: str) -> dict[str, str]:
    params: dict[str, str] = {
        "client_id": client_id,
        "redirect_uri": "https://example.com/cb",
        "response_type": "code",
        "code_challenge": VALID_PKCE_CHALLENGE,
        "code_challenge_method": "S256",
        "scope": "omnidim:all",
        "state": "xyz",
    }
    params.update(overrides)
    return params


async def test_authorize_happy_path_redirects_to_consent(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    client_id = await _register_public_client(client)
    res = await client.get("/authorize", params=_base_params(client_id), follow_redirects=False)
    assert res.status_code == 302
    location = res.headers["location"]
    assert location.startswith("http://localhost:3000/oauth/consent?request_id=")

    async with session_factory() as s:
        rows = (await s.execute(select(AuthorizationRequest))).scalars().all()
    assert any(r.client_id == client_id for r in rows)


async def test_authorize_unknown_client_returns_400(client: AsyncClient) -> None:
    res = await client.get(
        "/authorize",
        params=_base_params("not-a-real-client"),
        follow_redirects=False,
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_client"


async def test_authorize_unregistered_redirect_uri_returns_400(client: AsyncClient) -> None:
    client_id = await _register_public_client(client)
    res = await client.get(
        "/authorize",
        params=_base_params(client_id, redirect_uri="https://evil.example/cb"),
        follow_redirects=False,
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_request"


async def test_authorize_unsupported_response_type_redirects_with_error(
    client: AsyncClient,
) -> None:
    client_id = await _register_public_client(client)
    res = await client.get(
        "/authorize",
        params=_base_params(client_id, response_type="token"),
        follow_redirects=False,
    )
    assert res.status_code == 302
    loc = res.headers["location"]
    assert loc.startswith("https://example.com/cb?")
    assert "error=unsupported_response_type" in loc
    assert "state=xyz" in loc


async def test_authorize_plain_pkce_rejected(client: AsyncClient) -> None:
    client_id = await _register_public_client(client)
    res = await client.get(
        "/authorize",
        params=_base_params(client_id, code_challenge_method="plain"),
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "error=invalid_request" in res.headers["location"]


async def test_authorize_short_pkce_rejected(client: AsyncClient) -> None:
    client_id = await _register_public_client(client)
    res = await client.get(
        "/authorize",
        params=_base_params(client_id, code_challenge="too-short"),
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "error=invalid_request" in res.headers["location"]


async def test_authorize_unknown_scope_rejected(client: AsyncClient) -> None:
    client_id = await _register_public_client(client)
    res = await client.get(
        "/authorize",
        params=_base_params(client_id, scope="no-such-scope"),
        follow_redirects=False,
    )
    assert res.status_code == 302
    assert "error=invalid_scope" in res.headers["location"]


async def test_authorize_missing_scope_defaults_to_omnidim_all(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    client_id = await _register_public_client(client)
    params = _base_params(client_id)
    del params["scope"]
    res = await client.get("/authorize", params=params, follow_redirects=False)
    assert res.status_code == 302
    async with session_factory() as s:
        row = (
            await s.execute(
                select(AuthorizationRequest).where(AuthorizationRequest.client_id == client_id)
            )
        ).scalar_one()
    assert row.scope == "omnidim:all"


async def test_internal_fetch_returns_request_metadata(client: AsyncClient) -> None:
    client_id = await _register_public_client(client)
    res = await client.get("/authorize", params=_base_params(client_id), follow_redirects=False)
    request_id = res.headers["location"].rsplit("=", 1)[1]

    res = await client.get(
        f"/internal/authorization-request/{request_id}",
        headers={"X-Internal-Secret": "test-shared-secret"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["client_id"] == client_id
    assert body["client_name"] == "Test"
    assert body["redirect_uri"] == "https://example.com/cb"
    assert body["scope"] == "omnidim:all"
    assert body["state"] == "xyz"
    assert body["consumed"] is False
    assert body["expired"] is False


async def test_internal_fetch_requires_shared_secret(client: AsyncClient) -> None:
    res = await client.get(f"/internal/authorization-request/{secrets.token_urlsafe(32)}")
    assert res.status_code == 401


async def test_internal_fetch_wrong_secret_rejected(client: AsyncClient) -> None:
    res = await client.get(
        f"/internal/authorization-request/{secrets.token_urlsafe(32)}",
        headers={"X-Internal-Secret": "wrong"},
    )
    assert res.status_code == 401


async def test_internal_fetch_unknown_id_returns_404(client: AsyncClient) -> None:
    res = await client.get(
        f"/internal/authorization-request/{secrets.token_urlsafe(32)}",
        headers={"X-Internal-Secret": "test-shared-secret"},
    )
    assert res.status_code == 404
