import base64
import hashlib
import secrets

from httpx import AsyncClient

SECRET = {"X-Internal-Secret": "test-shared-secret"}
REDIRECT = "https://claude.ai/api/mcp/auth_callback"


def pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


async def approve(
    client: AsyncClient,
    *,
    app_name: str,
    odoo_user_id: int,
    api_key_id: int,
    browser_id: str | None,
) -> dict[str, str]:
    res = await client.post(
        "/register", json={"redirect_uris": [REDIRECT], "client_name": app_name}
    )
    client_id = res.json()["client_id"]
    verifier, challenge = pkce()
    res = await client.get(
        "/authorize",
        params={
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "omnidim:all",
            "state": "s",
        },
        follow_redirects=False,
    )
    request_id = res.headers["location"].rsplit("=", 1)[1]
    body: dict[str, object] = {
        "request_id": request_id,
        "odoo_user_id": odoo_user_id,
        "odoo_api_key_id": api_key_id,
        "odoo_api_key_value": f"key-{api_key_id}",
        "approved_scope": "omnidim:all",
    }
    if browser_id is not None:
        body["browser_id"] = browser_id
    res = await client.post("/internal/issue-code", headers=SECRET, json=body)
    assert res.status_code == 200, res.text
    res = await client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": res.json()["code"],
            "redirect_uri": REDIRECT,
            "code_verifier": verifier,
        },
    )
    assert res.status_code == 200, res.text
    return {"client_id": client_id, **res.json()}


async def refresh(client: AsyncClient, grant: dict[str, str]) -> dict[str, str]:
    res = await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": grant["client_id"],
            "refresh_token": grant["refresh_token"],
        },
    )
    assert res.status_code == 200, res.text
    return {"client_id": grant["client_id"], **res.json()}


async def mcp_status(client: AsyncClient, grant: dict[str, str]) -> int:
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {grant['access_token']}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    return res.status_code


def new_browser_id() -> str:
    return secrets.token_urlsafe(32)


def new_user_id() -> int:
    return 10_000_000 + secrets.randbelow(1_000_000_000)
