import base64
import hashlib
import secrets

from httpx import AsyncClient


def _make_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


async def _register(
    client: AsyncClient, redirect_uri: str = "https://example.com/cb"
) -> str:
    res = await client.post(
        "/register",
        json={"redirect_uris": [redirect_uri], "client_name": "FlowTest"},
    )
    return res.json()["client_id"]


async def _authorize(client: AsyncClient, client_id: str, challenge: str) -> str:
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
    return res.headers["location"].rsplit("=", 1)[1]


async def _approve(client: AsyncClient, request_id: str) -> str:
    res = await client.post(
        "/internal/issue-code",
        headers={"X-Internal-Secret": "test-shared-secret"},
        json={
            "request_id": request_id,
            "odoo_user_id": 2943,
            "odoo_api_key_id": 1,
            "approved_scope": "omnidim:all",
        },
    )
    assert res.status_code == 200, res.text
    return res.json()["code"]


async def test_full_authorization_code_flow(client: AsyncClient) -> None:
    client_id = await _register(client)
    verifier, challenge = _make_pkce()
    request_id = await _authorize(client, client_id, challenge)
    code = await _approve(client, request_id)

    res = await client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": "https://example.com/cb",
            "code_verifier": verifier,
        },
    )
    assert res.status_code == 200
    tokens = res.json()
    assert tokens["token_type"] == "Bearer"  # noqa: S105
    assert tokens["expires_in"] == 3600
    assert tokens["scope"] == "omnidim:all"
    assert len(tokens["access_token"]) >= 40
    assert len(tokens["refresh_token"]) >= 40


async def test_pkce_verifier_mismatch_rejected(client: AsyncClient) -> None:
    client_id = await _register(client)
    _, challenge = _make_pkce()
    request_id = await _authorize(client, client_id, challenge)
    code = await _approve(client, request_id)

    res = await client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": "https://example.com/cb",
            "code_verifier": "wrong-verifier-that-will-not-match",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "invalid_grant"


async def test_code_is_single_use(client: AsyncClient) -> None:
    client_id = await _register(client)
    verifier, challenge = _make_pkce()
    request_id = await _authorize(client, client_id, challenge)
    code = await _approve(client, request_id)

    form = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": "https://example.com/cb",
        "code_verifier": verifier,
    }
    assert (await client.post("/token", data=form)).status_code == 200
    res2 = await client.post("/token", data=form)
    assert res2.status_code == 400
    assert res2.json()["detail"]["error"] == "invalid_grant"


async def test_issue_code_rejects_unknown_scope(client: AsyncClient) -> None:
    client_id = await _register(client)
    _, challenge = _make_pkce()
    request_id = await _authorize(client, client_id, challenge)

    res = await client.post(
        "/internal/issue-code",
        headers={"X-Internal-Secret": "test-shared-secret"},
        json={
            "request_id": request_id,
            "odoo_user_id": 1,
            "odoo_api_key_id": 1,
            "approved_scope": "no-such-scope",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "invalid_scope"


async def test_issue_code_consumes_request_once(client: AsyncClient) -> None:
    client_id = await _register(client)
    _, challenge = _make_pkce()
    request_id = await _authorize(client, client_id, challenge)

    payload = {
        "request_id": request_id,
        "odoo_user_id": 1,
        "odoo_api_key_id": 1,
        "approved_scope": "omnidim:all",
    }
    headers = {"X-Internal-Secret": "test-shared-secret"}
    res1 = await client.post("/internal/issue-code", headers=headers, json=payload)
    assert res1.status_code == 200
    res2 = await client.post("/internal/issue-code", headers=headers, json=payload)
    assert res2.status_code == 400
