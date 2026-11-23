from __future__ import annotations

import json
from typing import Annotated, Any

import structlog
from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import __version__
from app._generated.tools import TOOLS
from app.dependencies import get_session_factory
from app.procedures import (
    DEMO_OFFER_RULE,
    EXTRA_TOOLS,
    build_prompt,
    prompts_for_listing,
    read_resource,
    resources_for_listing,
    tool_meta,
)
from app.services.bearer import BearerError, ResolvedToken, resolve_bearer
from app.services.dispatcher import DispatchError, dispatch_tool
from app.services.docs import DOCS_TOOL_NAMES, call_docs_tool
from app.services.guides import read_guide

router = APIRouter(tags=["mcp"])
log = structlog.get_logger()

PROTOCOL_VERSION = "2025-11-25"
SERVER_INFO = {"name": "OmniDimension", "version": __version__}
INSTRUCTIONS = (
    "OmniDimension voice AI platform. Tools cover agents, calls, bulk calls, "
    "phone numbers, knowledge base, and providers. Pagination uses `pageno` "
    "(>=1) and `pagesize` (1-150) on list endpoints. All requests run as the "
    "user who authorized the OAuth grant. "
    "Dispatching calls: before dispatchCall, run listPhoneNumbers. If the "
    "account has numbers, pass the chosen one as from_number_id. If it has "
    "none, omit from_number_id and the platform's default number is used. "
    "Never guess a from_number_id. "
    "Before you build an agent, launch a call campaign, build a workflow, review calls or "
    "roll an agent back, call `readGuide` with the matching playbook (provision_agent, "
    "build_outbound_campaign, build_workflow, audit_calls, restore_agent_version) and follow "
    "its steps. If you are unsure which tool fits, read `omnidim://guide/routing` with "
    "`readGuide`. "
    + DEMO_OFFER_RULE
)


def _result(req_id: object, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _error(req_id: object, code: int, message: str, data: Any = None) -> dict[str, Any]:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": req_id, "error": err}


_READ_ONLY_TOOLS = frozenset(
    t["name"] for t in (*TOOLS, *EXTRA_TOOLS) if t["annotations"].get("readOnlyHint")
)


def _tools_for_listing(read_only: bool) -> list[dict[str, Any]]:
    tools = []
    for t in (*TOOLS, *EXTRA_TOOLS):
        if read_only and t["name"] not in _READ_ONLY_TOOLS:
            continue
        tool: dict[str, Any] = {
            "name": t["name"],
            "description": t["description"],
            "inputSchema": t["input_schema"],
            "annotations": t["annotations"],
        }
        meta = tool_meta(t["name"])
        if meta:
            tool["_meta"] = meta
        tools.append(tool)
    return tools


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
    return await _serve(request, factory, authorization, read_only=False)


@router.post("/mcp/readonly")
async def mcp_readonly_endpoint(
    request: Request,
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> JSONResponse:
    return await _serve(request, factory, authorization, read_only=True)


async def _serve(
    request: Request,
    factory: async_sessionmaker[AsyncSession],
    authorization: str | None,
    *,
    read_only: bool,
) -> JSONResponse:
    try:
        async with factory() as session:
            token: ResolvedToken = await resolve_bearer(session, authorization)
    except BearerError as exc:
        # A first request without a token is the normal start of sign-in; the reason tells
        # that apart from expired or revoked tokens.
        log.info("mcp_auth_failed", reason=exc.description)
        return _bearer_challenge(exc)

    response = await _answer(request, token, read_only=read_only)
    await _log_error(request, response, token, read_only=read_only)
    return response


async def _log_error(
    request: Request, response: JSONResponse, token: ResolvedToken, *, read_only: bool
) -> None:
    """One mcp_error line for every JSON-RPC error we send back, so failures that happen
    before a tool runs (bad arguments, unknown tool or method) show on the MCP board."""
    payload = json.loads(bytes(response.body))
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        return
    try:
        raw = await request.json()
    except ValueError:
        raw = None
    body: dict[str, Any] = raw if isinstance(raw, dict) else {}
    method = body.get("method")
    raw_params = body.get("params")
    params: dict[str, Any] = raw_params if isinstance(raw_params, dict) else {}
    log.warning(
        "mcp_error",
        # Both come from the caller: cap them like the message.
        method=str(method)[:100] if method is not None else None,
        tool=str(params.get("name"))[:100] if method == "tools/call" else None,
        code=error.get("code"),
        message=str(error.get("message"))[:200],
        read_only=read_only,
        client_id=token.client_id,
        client_name=token.client_name,
        odoo_user_id=token.odoo_user_id,
    )


async def _answer(request: Request, token: ResolvedToken, *, read_only: bool) -> JSONResponse:
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
        read_only=read_only,
        client_id=token.client_id,
        client_name=token.client_name,
        odoo_user_id=token.odoo_user_id,
    )

    if method == "initialize":
        return JSONResponse(
            content=_result(
                req_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "serverInfo": SERVER_INFO,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "prompts": {"listChanged": False},
                        "resources": {"listChanged": False},
                    },
                    "instructions": INSTRUCTIONS,
                },
            )
        )

    if method == "notifications/initialized":
        return JSONResponse(status_code=202, content={})

    if method == "tools/list":
        return JSONResponse(content=_result(req_id, {"tools": _tools_for_listing(read_only)}))

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
        if read_only and tool_name not in _READ_ONLY_TOOLS:
            return JSONResponse(
                content=_error(
                    req_id,
                    -32602,
                    f"{tool_name} changes data, so the read-only endpoint does not run it",
                )
            )
        try:
            if tool_name == "readGuide":
                result = read_guide(arguments, token)
            elif tool_name in DOCS_TOOL_NAMES:
                result = await call_docs_tool(tool_name, arguments, token)
            else:
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

    if method == "prompts/list":
        return JSONResponse(content=_result(req_id, {"prompts": prompts_for_listing()}))

    if method == "prompts/get":
        prompt_name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(prompt_name, str) or not isinstance(arguments, dict):
            return JSONResponse(
                content=_error(
                    req_id, -32602, "prompts/get requires name (str) + arguments (object)",
                ),
            )
        prompt = build_prompt(prompt_name, arguments)
        if prompt is None:
            return JSONResponse(content=_error(req_id, -32602, f"unknown prompt: {prompt_name}"))
        return JSONResponse(content=_result(req_id, prompt))

    if method == "resources/list":
        return JSONResponse(content=_result(req_id, {"resources": resources_for_listing()}))

    if method == "resources/read":
        uri = params.get("uri")
        if not isinstance(uri, str):
            return JSONResponse(content=_error(req_id, -32602, "resources/read requires uri (str)"))
        resource = read_resource(uri)
        if resource is None:
            return JSONResponse(content=_error(req_id, -32602, f"unknown resource: {uri}"))
        return JSONResponse(content=_result(req_id, resource))

    return JSONResponse(
        status_code=400,
        content=_error(req_id, -32601, f"method not supported: {method}"),
    )
