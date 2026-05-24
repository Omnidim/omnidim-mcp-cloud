from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.config import Settings, get_settings
from app.scopes import SUPPORTED_SCOPES

router = APIRouter(tags=["discovery"])

_CACHE_HEADERS = {"Cache-Control": "public, max-age=3600"}

_SCOPES = list(SUPPORTED_SCOPES)


@router.get("/.well-known/oauth-authorization-server")
async def authorization_server_metadata(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, object]:
    base = settings.public_base_url.rstrip("/")
    auth_methods = ["client_secret_basic", "client_secret_post", "none"]
    for k, v in _CACHE_HEADERS.items():
        response.headers[k] = v
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/authorize",
        "token_endpoint": f"{base}/token",
        "registration_endpoint": f"{base}/register",
        "revocation_endpoint": f"{base}/revoke",
        "introspection_endpoint": f"{base}/introspect",
        "response_types_supported": ["code"],
        "response_modes_supported": ["query"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": auth_methods,
        "revocation_endpoint_auth_methods_supported": auth_methods,
        "introspection_endpoint_auth_methods_supported": auth_methods,
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": _SCOPES,
        "authorization_response_iss_parameter_supported": True,
        "service_documentation": "https://docs.omnidim.io/docs/get-started/authentication",
    }


@router.get("/.well-known/oauth-protected-resource")
async def protected_resource_metadata(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, object]:
    base = settings.public_base_url.rstrip("/")
    for k, v in _CACHE_HEADERS.items():
        response.headers[k] = v
    return {
        "resource": base,
        "resource_name": "OmniDimension MCP",
        "authorization_servers": [base],
        "scopes_supported": _SCOPES,
        "bearer_methods_supported": ["header"],
        "resource_documentation": "https://docs.omnidim.io/docs/get-started/authentication",
    }
