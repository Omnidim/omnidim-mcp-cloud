from __future__ import annotations

from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app._generated.tools import TOOLS
from app.dependencies import get_session_factory
from app.services.bearer import BearerError, ResolvedToken, resolve_bearer
from app.services.dispatcher import DispatchError, dispatch_tool

router = APIRouter(tags=["mcp"])
log = structlog.get_logger()

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "OmniDimension", "version": "0.2.1"}
INSTRUCTIONS = (
    "OmniDimension voice AI platform. Tools cover agents, calls, bulk calls, "
    "phone numbers, knowledge base, simulations, providers, and reseller "
    "operations. Pagination uses `pageno` (>=1) and `pagesize` (1-150) on list "
    "endpoints. All requests run as the user who authorized the OAuth grant."
)


def _result(req_id: object, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: object, code: int, message: str, data: Any = None) -> dict[str, Any]:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}


def _tools_for_listing() -> list[dict[str, Any]]:
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "inputSchema": t["input_schema"],
        }
        for t in TOOLS
    ]


def _bearer_challenge(exc: BearerError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"error": "invalid_token", "error_description": exc.description},
        headers={"WWW-Authenticate": exc.www_authenticate},
    )


@router.post("/mcp")
async def mcp_endpoint(
    request: Request,
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> JSONResponse:
    try:
        async with factory() as session:
            token: ResolvedToken = await resolve_bearer(session, authorization)
    except BearerError as exc:
        return _bearer_challenge(exc)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content=_error(None, -32700, "parse error"),
        )

    method = body.get("method")
    req_id = body.get("id")
    params = body.get("params") or {}

    if method is None:
        return JSONResponse(
            status_code=400,
            content=_error(req_id, -32600, "missing method"),
        )

    log.info(
        "mcp_request",
        method=method,
        client_id=token.client_id,
        odoo_user_id=token.odoo_user_id,
    )

    if method == "initialize":
        return JSONResponse(
            content=_result(
                req_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "serverInfo": SERVER_INFO,
                    "capabilities": {"tools": {"listChanged": False}},
                    "instructions": INSTRUCTIONS,
                },
            )
        )

    if method == "notifications/initialized":
        return JSONResponse(status_code=202, content={})

    if method == "tools/list":
        return JSONResponse(content=_result(req_id, {"tools": _tools_for_listing()}))

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(tool_name, str) or not isinstance(arguments, dict):
            return JSONResponse(
                content=_error(
                    req_id, -32602,
                    "tools/call requires name (str) + arguments (object)",
                ),
            )
        try:
            result = await dispatch_tool(name=tool_name, arguments=arguments, token=token)
        except DispatchError as exc:
            return JSONResponse(content=_error(req_id, exc.code, exc.message, exc.data))
        return JSONResponse(
            content=_result(
                req_id,
                {
                    "content": [{"type": "text", "text": result.text}],
                    "isError": result.is_error,
                },
            )
        )

    return JSONResponse(
        status_code=400,
        content=_error(req_id, -32601, f"method not supported: {method}"),
    )
