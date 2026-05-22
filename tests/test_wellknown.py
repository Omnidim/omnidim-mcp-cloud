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
