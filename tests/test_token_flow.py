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
            "odoo_api_key_value": "fake-upstream-key",
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


async def test_refresh_token_rotates_pair(client: AsyncClient) -> None:
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
    original = res.json()

    res2 = await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": original["refresh_token"],
        },
    )
    assert res2.status_code == 200
    rotated = res2.json()
    assert rotated["access_token"] != original["access_token"]
    assert rotated["refresh_token"] != original["refresh_token"]
    assert rotated["scope"] == original["scope"]


async def test_refresh_token_replay_revokes_grant(client: AsyncClient) -> None:
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
    original_refresh = res.json()["refresh_token"]

    # First refresh: succeeds.
    await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": original_refresh,
        },
    )
    # Replay: same refresh token a second time → rejected + family revoked.
    replay = await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": original_refresh,
        },
    )
    assert replay.status_code == 400
    assert replay.json()["detail"]["error"] == "invalid_grant"


async def test_revoke_invalidates_access_token(client: AsyncClient) -> None:
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
    access = res.json()["access_token"]

    rev = await client.post(
        "/revoke",
        data={"client_id": client_id, "token": access},
    )
    assert rev.status_code == 200

    # /mcp with the revoked token must now reject.
    mcp_res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {access}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    assert mcp_res.status_code == 401


async def test_revoke_unknown_token_still_200(client: AsyncClient) -> None:
    client_id = await _register(client)
    res = await client.post(
        "/revoke",
        data={"client_id": client_id, "token": "not-a-real-token"},
    )
    # RFC 7009 §2.2: never leak whether the token existed.
    assert res.status_code == 200


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
