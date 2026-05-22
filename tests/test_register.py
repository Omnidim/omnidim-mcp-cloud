import asyncio

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import OAuthClient
from app.services.clients import hash_secret


def _minimal_public_body(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {"redirect_uris": ["https://example.com/cb"]}
    body.update(overrides)
    return body


async def test_register_public_client_minimal(client: AsyncClient) -> None:
    res = await client.post("/register", json=_minimal_public_body())
    assert res.status_code == 201
    body = res.json()

    assert body["client_id"]
    assert len(body["client_id"]) >= 32
    assert body["redirect_uris"] == ["https://example.com/cb"]
    assert body["token_endpoint_auth_method"] == "none"
    assert body["grant_types"] == ["authorization_code", "refresh_token"]
    assert body["response_types"] == ["code"]
    assert "client_secret" not in body
    assert "client_secret_expires_at" not in body
    assert body["client_id_issued_at"] > 0


async def test_register_confidential_client_returns_secret_once(client: AsyncClient) -> None:
    res = await client.post(
        "/register",
        json=_minimal_public_body(token_endpoint_auth_method="client_secret_basic"),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["token_endpoint_auth_method"] == "client_secret_basic"
    assert isinstance(body["client_secret"], str)
    assert len(body["client_secret"]) >= 32
    assert body["client_secret_expires_at"] == 0


async def test_register_persists_only_hashed_secret(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    res = await client.post(
        "/register",
        json=_minimal_public_body(token_endpoint_auth_method="client_secret_post"),
    )
    body = res.json()
    plaintext = body["client_secret"]

    async with session_factory() as s:
        rec = (
            await s.execute(select(OAuthClient).where(OAuthClient.client_id == body["client_id"]))
        ).scalar_one()
    assert rec.client_secret_hash is not None
    assert rec.client_secret_hash != plaintext
    assert rec.client_secret_hash == hash_secret(plaintext)
    assert len(rec.client_secret_hash) == 64  # SHA-256 hex


async def test_register_rejects_missing_redirect_uris(client: AsyncClient) -> None:
    res = await client.post("/register", json={})
    assert res.status_code == 400
    body = res.json()
    assert body["error"] == "invalid_redirect_uri"


async def test_register_rejects_empty_redirect_uris(client: AsyncClient) -> None:
    res = await client.post("/register", json={"redirect_uris": []})
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_redirect_uri"


async def test_register_rejects_non_https_redirect(client: AsyncClient) -> None:
    res = await client.post(
        "/register",
        json={"redirect_uris": ["http://attacker.example.com/cb"]},
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_redirect_uri"


async def test_register_rejects_redirect_with_fragment(client: AsyncClient) -> None:
    res = await client.post(
        "/register", json={"redirect_uris": ["https://example.com/cb#evil"]}
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_redirect_uri"


async def test_register_rejects_redirect_with_userinfo(client: AsyncClient) -> None:
    res = await client.post(
        "/register", json={"redirect_uris": ["https://user:pass@example.com/cb"]}
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_redirect_uri"


async def test_register_allows_loopback_http(client: AsyncClient) -> None:
    for loopback in ("http://localhost:1234/cb", "http://127.0.0.1:9876/cb"):
        res = await client.post("/register", json={"redirect_uris": [loopback]})
        assert res.status_code == 201, loopback


async def test_register_rejects_inconsistent_grant_and_response_types(client: AsyncClient) -> None:
    res = await client.post(
        "/register",
        json=_minimal_public_body(
            grant_types=["authorization_code"], response_types=["code"]
        ),
    )
    assert res.status_code == 201  # consistent — sanity check

    res = await client.post(
        "/register",
        json=_minimal_public_body(grant_types=["refresh_token"]),
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_client_metadata"


async def test_register_rejects_software_statement_until_validation_exists(
    client: AsyncClient,
) -> None:
    res = await client.post(
        "/register",
        json=_minimal_public_body(software_statement="ey.fake.jwt"),
    )
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_software_statement"


async def test_register_honours_provided_client_name(client: AsyncClient) -> None:
    res = await client.post("/register", json=_minimal_public_body(client_name="Claude Desktop"))
    assert res.status_code == 201
    assert res.json()["client_name"] == "Claude Desktop"


async def test_register_assigns_default_client_name(client: AsyncClient) -> None:
    res = await client.post("/register", json=_minimal_public_body())
    assert res.status_code == 201
    assert res.json()["client_name"].startswith("client_")


async def test_register_silently_ignores_unknown_fields(client: AsyncClient) -> None:
    res = await client.post(
        "/register",
        json=_minimal_public_body(some_unknown_field="ignore-me", another_one={"x": 1}),
    )
    assert res.status_code == 201


async def test_register_generates_unique_client_ids(client: AsyncClient) -> None:
    seen: set[str] = set()
    for _ in range(5):
        res = await client.post("/register", json=_minimal_public_body())
        seen.add(res.json()["client_id"])
    assert len(seen) == 5


async def test_register_concurrent_requests_get_distinct_ids(client: AsyncClient) -> None:
    results = await asyncio.gather(
        *[client.post("/register", json=_minimal_public_body()) for _ in range(8)]
    )
    ids = {r.json()["client_id"] for r in results}
    assert len(ids) == 8
    assert all(r.status_code == 201 for r in results)


async def test_register_duplicate_body_returns_distinct_client_ids(client: AsyncClient) -> None:
    body = _minimal_public_body(client_name="Same Name")
    a = await client.post("/register", json=body)
    b = await client.post("/register", json=body)
    assert a.json()["client_id"] != b.json()["client_id"]
