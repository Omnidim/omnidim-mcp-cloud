from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

import httpx
import structlog

from app._generated.tools import TOOLS
from app.services.bearer import ResolvedToken

log = structlog.get_logger()

BACKEND_BASE_URL: Final = "https://backend.omnidim.io/api/v1"
USER_AGENT: Final = "omnidim-mcp-cloud/0.2.6"
TIMEOUT_SECONDS: Final = 60.0
MAX_LIST_CHARS: Final = 25_000

LIST_KEYS: Final = (
    "bots",
    "call_log_data",
    "records",
    "files",
    "phone_numbers",
    "llms",
    "voices",
    "stt",
    "tts",
    "services",
    "organizations",
    "data",
    "results",
    "items",
)

_TOOLS_BY_NAME: Final = {t["name"]: t for t in TOOLS}


def _default_client_factory() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=TIMEOUT_SECONDS)


_client_factory: Callable[[], httpx.AsyncClient] = _default_client_factory


def set_client_factory(factory: Callable[[], httpx.AsyncClient]) -> None:
    global _client_factory
    _client_factory = factory


def reset_client_factory() -> None:
    global _client_factory
    _client_factory = _default_client_factory


class DispatchError(Exception):
    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


@dataclass(frozen=True)
class ToolResult:
    text: str
    is_error: bool = False


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, dict):
        return {k: ("[redacted]" if k == "api_key" else _redact(v)) for k, v in value.items()}
    return value


def _find_list(data: Any) -> tuple[list[Any], str | None] | None:
    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for k in LIST_KEYS:
            v = data.get(k)
            if isinstance(v, list):
                return v, k
    return None


def _trim(data: Any) -> ToolResult:
    redacted = _redact(data)
    full = json.dumps(redacted, indent=2, ensure_ascii=False)
    found = _find_list(redacted)
    if found is None or len(full) <= MAX_LIST_CHARS:
        return ToolResult(text=full)

    arr, key = found
    kept = len(arr)
    while kept > 1:
        trimmed = arr[:kept]
        if key is not None and isinstance(redacted, dict):
            candidate = json.dumps({**redacted, key: trimmed}, indent=2, ensure_ascii=False)
        else:
            candidate = json.dumps(trimmed, indent=2, ensure_ascii=False)
        if len(candidate) <= MAX_LIST_CHARS:
            note = (
                f"\n\n[Showing {kept} of {len(arr)} items. Lower pagesize, filter "
                "by name, or fetch a specific item by ID for full detail.]"
            )
            return ToolResult(text=candidate + note)
        kept = max(1, int(kept * 0.6))

    return ToolResult(
        text=full[:MAX_LIST_CHARS] + f"\n\n[Response truncated. Full size: {len(full)} chars.]",
    )


def _substitute_path(template: str, args: dict[str, Any], path_params: list[str]) -> str:
    path = template
    for p in path_params:
        if p not in args:
            raise DispatchError(-32602, f"missing required path parameter: {p}")
        path = path.replace(f"{{{p}}}", str(args[p]))
    return path


def _split_args(
    args: dict[str, Any], path_params: list[str], query_params: list[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    query = {p: args[p] for p in query_params if p in args}
    body = {k: v for k, v in args.items() if k not in path_params and k not in query_params}
    return query, body


async def dispatch_tool(
    *,
    name: str,
    arguments: dict[str, Any],
    token: ResolvedToken,
) -> ToolResult:
    tool = _TOOLS_BY_NAME.get(name)
    if tool is None:
        raise DispatchError(-32602, f"unknown tool: {name}")

    if not token.odoo_api_key_value:
        raise DispatchError(-32000, "missing upstream credential")

    path = _substitute_path(tool["path"], arguments, tool["path_params"])
    query, body = _split_args(arguments, tool["path_params"], tool["query_params"])

    url = f"{BACKEND_BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {token.odoo_api_key_value}",
        "User-Agent": USER_AGENT,
    }
    method = tool["method"]

    request_kwargs: dict[str, Any] = {"params": query} if query else {}
    if method != "GET" and body:
        request_kwargs["json"] = body

    log.info(
        "tool_call",
        tool=name,
        method=method,
        path=path,
        client_id=token.client_id,
        odoo_user_id=token.odoo_user_id,
    )

    try:
        async with _client_factory() as client:
            res = await client.request(method, url, headers=headers, **request_kwargs)
    except httpx.TimeoutException as exc:
        raise DispatchError(-32000, "upstream timeout", {"tool": name}) from exc
    except httpx.HTTPError as exc:
        raise DispatchError(-32000, "upstream network error", {"tool": name}) from exc

    ctype = res.headers.get("content-type", "")
    if "application/json" not in ctype:
        snippet = res.text[:200].strip().replace("\n", " ")
        raise DispatchError(
            -32000,
            f"upstream returned non-JSON ({res.status_code})",
            {"snippet": snippet},
        )

    try:
        payload = res.json()
    except ValueError as exc:
        raise DispatchError(-32000, "upstream JSON parse error") from exc

    if res.status_code >= 400:
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        return ToolResult(text=text, is_error=True)

    return _trim(payload)
