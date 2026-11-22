from httpx import AsyncClient


async def test_authorization_server_metadata_shape(client: AsyncClient) -> None:
    res = await client.get("/.well-known/oauth-authorization-server")
    assert res.status_code == 200
    body = res.json()

    for field in (
        "issuer",
        "authorization_endpoint",
        "token_endpoint",
        "registration_endpoint",
        "revocation_endpoint",
        "introspection_endpoint",
        "response_types_supported",
        "grant_types_supported",
        "token_endpoint_auth_methods_supported",
        "code_challenge_methods_supported",
        "scopes_supported",
        "authorization_response_iss_parameter_supported",
    ):
        assert field in body, f"missing {field}"

    assert body["code_challenge_methods_supported"] == ["S256"]
    assert body["authorization_response_iss_parameter_supported"] is True
    assert res.headers.get("cache-control") == "public, max-age=3600"


async def test_protected_resource_metadata_shape(client: AsyncClient) -> None:
    res = await client.get("/.well-known/oauth-protected-resource")
    assert res.status_code == 200
    body = res.json()

    for field in (
        "resource",
        "resource_name",
        "authorization_servers",
        "scopes_supported",
        "bearer_methods_supported",
    ):
        assert field in body, f"missing {field}"

    assert body["bearer_methods_supported"] == ["header"]
    assert res.headers.get("cache-control") == "public, max-age=3600"


def test_issuer_drops_trailing_slash() -> None:
    from app.config import Settings

    assert Settings(public_base_url="https://mcp.example.com/").issuer == "https://mcp.example.com"


def test_issuer_rejects_query_and_fragment() -> None:
    # RFC 8414 section 2: the issuer has no query or fragment component.
    import pytest
    from pydantic import ValidationError

    from app.config import Settings

    for bad in ("https://mcp.example.com/?a=1", "https://mcp.example.com/#x"):
        with pytest.raises(ValidationError):
            Settings(public_base_url=bad)



async def test_server_card_lists_the_live_tools_without_auth(client: AsyncClient) -> None:
    from app import __version__
    from app.routes.mcp import _tools_for_listing

    res = await client.get("/.well-known/mcp/server-card.json")
    assert res.status_code == 200
    card = res.json()

    live = [t["name"] for t in _tools_for_listing(read_only=False)]
    assert [t["name"] for t in card["tools"]] == live
    assert "searchDocs" in live and "bookDemo" in live
    assert card["version"] == __version__
    assert card["name"] == "io.github.Omnidim/omnidim-mcp-server"
    assert card["remotes"][0]["url"].endswith("/mcp")
    # A catalogue for discovery, not a second tools/list: no input schemas.
    assert all(set(t) <= {"name", "title", "description", "annotations"} for t in card["tools"])
    assert all(t["title"] for t in card["tools"])
