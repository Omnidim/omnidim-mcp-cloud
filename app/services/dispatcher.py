from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final
from urllib.parse import quote

import httpx
import structlog
from opentelemetry import trace
from opentelemetry.trace import StatusCode

from app import __version__
from app._generated.tools import TOOLS
from app.config import get_settings
from app.procedures import EXTRA_TOOLS
from app.services.bearer import ResolvedToken

log = structlog.get_logger()

USER_AGENT: Final = f"omnidim-mcp-cloud/{__version__}"
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

_TOOLS_BY_NAME: Final = {t["name"]: t for t in (*TOOLS, *EXTRA_TOOLS)}


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


# Credential-bearing keys are redacted from tool output.
_SENSITIVE_KEY_RE = re.compile(
    r"api_key|api_token|access_token|refresh_token|password|secret", re.IGNORECASE
)
_SECRET_QUERY_RE = re.compile(r"(secret=)[^&\s\"]+")


def _redact(value: Any) -> Any:
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, dict):
        return {
            k: (
                "[redacted]"
                if _SENSITIVE_KEY_RE.search(k) and isinstance(v, str) and v
                else _redact(v)
            )
            for k, v in value.items()
        }
    if isinstance(value, str):
        return _SECRET_QUERY_RE.sub(r"\1[redacted]", value)
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


def _without_turn_detail(data: Any) -> tuple[Any, bool]:
    """Call logs without their per-turn `interactions`, which are most of a call log's size."""
    found = _find_list(data)
    rows = found[0] if found else [data]
    if not any(isinstance(r, dict) and "interactions" in r for r in rows):
        return data, False
    slim = [
        {k: v for k, v in r.items() if k != "interactions"} if isinstance(r, dict) else r
        for r in rows
    ]
    if found is None:
        return slim[0], True
    key = found[1]
    return ({**data, key: slim} if key is not None else slim), True


def _shorten(value: Any, limit: int, items: int) -> Any:
    """Cut long strings to `limit` chars and long lists to `items` entries, keeping the shape."""
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + f"...[truncated {len(value) - limit} chars]"
    if isinstance(value, dict):
        return {k: _shorten(v, limit, items) for k, v in value.items()}
    if isinstance(value, list):
        kept = [_shorten(v, limit, items) for v in value[:items]]
        if len(value) > items:
            kept.append(f"...[truncated {len(value) - items} more items]")
        return kept
    return value


def _with_note(data: Any, note: str) -> str:
    # The note rides inside the JSON so clients can always parse the result.
    if isinstance(data, dict):
        return json.dumps({**data, "_note": note}, indent=2, ensure_ascii=False)
    return json.dumps({"items": data, "_note": note}, indent=2, ensure_ascii=False)


def _trim(data: Any) -> ToolResult:
    """Fit a result under MAX_LIST_CHARS while keeping it valid JSON."""
    redacted = _redact(data)
    full = json.dumps(redacted, indent=2, ensure_ascii=False)
    if len(full) <= MAX_LIST_CHARS:
        return ToolResult(text=full)

    # Turn detail goes before rows or a cut, so transcript, recording and cost always arrive.
    slim, dropped = _without_turn_detail(redacted)
    drop_note = " Left out per-turn detail (interactions)." if dropped else ""
    if dropped:
        slim_text = json.dumps(slim, indent=2, ensure_ascii=False)
        if len(slim_text) <= MAX_LIST_CHARS:
            note = (
                "Left out per-turn detail (interactions) to fit. call_conversation "
                "has the transcript."
            )
            return ToolResult(text=_with_note(slim, note))
        redacted, full = slim, slim_text

    found = _find_list(redacted)
    if found is not None:
        arr, key = found
        page_links = ("next_cursor", "has_more")
        kept = len(arr)
        while kept > 1:
            trimmed = arr[:kept]
            body: Any = trimmed
            if key is not None and isinstance(redacted, dict):
                rest = {k: v for k, v in redacted.items() if k not in page_links}
                body = {**rest, key: trimmed}
            note = (
                f"Showing {kept} of {len(arr)} items.{drop_note} The rest were cut to fit, "
                f"and the next page would skip them: ask again with pagesize {kept} to read "
                "every row, filter, or fetch a specific item by ID for full detail."
            )
            candidate = _with_note(body, note)
            if len(candidate) <= MAX_LIST_CHARS:
                return ToolResult(text=candidate)
            kept = max(1, int(kept * 0.6))
        if key is not None and isinstance(redacted, dict):
            rest = {k: v for k, v in redacted.items() if k not in page_links}
            redacted = {**rest, key: arr[:1]}
        else:
            redacted = arr[:1]

    # Still too big (one huge item, or no list): shorten long strings and nested lists.
    # ponytail: halving both caps until it fits; fine for the few huge fields (transcripts).
    limit, items = 4000, 200
    while limit >= 50:
        candidate = _with_note(
            _shorten(redacted, limit, items),
            f"Long text fields were truncated. Full size: {len(full)} chars.{drop_note}",
        )
        if len(candidate) <= MAX_LIST_CHARS:
            return ToolResult(text=candidate)
        limit, items = limit // 2, max(1, items // 2)
    return ToolResult(
        text=_with_note({}, f"Result too large to return ({len(full)} chars). Fetch by ID.")
    )


def _path_value(name: str, value: Any, declared: Any) -> str:
    if declared not in ("integer", "number"):
        return str(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str) and value.isascii() and value.isdigit():
        return str(int(value))
    raise DispatchError(-32602, f"{name} must be a whole number")


def _substitute_path(
    template: str, args: dict[str, Any], path_params: list[str], schema: dict[str, Any]
) -> str:
    props = schema.get("properties", {})
    path = template
    for p in path_params:
        if p not in args:
            raise DispatchError(-32602, f"missing required path parameter: {p}")
        value = _path_value(p, args[p], props.get(p, {}).get("type"))
        # Percent-encode the whole value: an unencoded `../` or `?` in a path
        # argument would rewrite the upstream URL and reach endpoints outside
        # the generated tool surface.
        path = path.replace(f"{{{p}}}", quote(value, safe=""))
    return path


def _split_args(
    args: dict[str, Any],
    path_params: list[str],
    query_params: list[str],
    header_params: list[str],
) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
    query = {p: args[p] for p in query_params if p in args}
    # HTTP header names are case-insensitive, so a model's lowercase key still counts.
    by_lower = {p.lower(): p for p in header_params}
    headers: dict[str, str] = {}
    header_args: set[str] = set()
    for k, v in args.items():
        name = by_lower.get(k.lower())
        if name is None:
            continue
        value = str(v)
        if not value.isascii():
            raise DispatchError(-32602, f"{name} must be plain ASCII text")
        headers[name] = value
        header_args.add(k)
    routed = {*path_params, *query_params, *header_args}
    body = {k: v for k, v in args.items() if k not in routed}
    return query, headers, body


def _coerce_args(args: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Parse JSON-encoded strings for arguments declared as object or array.

    Some clients serialize nested values as JSON strings even when the
    schema declares structured types. Forwarding those strings upstream
    fails, so decode them when the parsed value matches the declared type.
    """
    props = schema.get("properties", {})
    out = dict(args)
    for k, v in args.items():
        declared = props.get(k, {}).get("type")
        if declared not in ("object", "array") or not isinstance(v, str):
            continue
        try:
            parsed = json.loads(v)
        except ValueError:
            continue
        if (declared == "object" and isinstance(parsed, dict)) or (
            declared == "array" and isinstance(parsed, list)
        ):
            out[k] = parsed
    return out


def _unknown_tool(name: str) -> DispatchError:
    for tool in _TOOLS_BY_NAME.values():
        for action, route in tool.get("actions", {}).items():
            if route["operation"] == name != tool["name"]:
                return DispatchError(
                    -32602,
                    f"unknown tool: {name}. Call {tool['name']} with {tool['field']} {action}.",
                )
    return DispatchError(-32602, f"unknown tool: {name}")


def _pick_action(
    tool: dict[str, Any], arguments: dict[str, Any]
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    field = tool["field"]
    action = arguments.get(field)
    route = tool["actions"].get(action) if isinstance(action, str) else None
    if not isinstance(action, str) or route is None:
        raise DispatchError(-32602, f"{field} must be one of: {', '.join(tool['actions'])}")
    other_inputs = set(tool["input_schema"]["properties"]) - set(route["inputs"]) - {field}
    if not route["sends_field"]:
        other_inputs.add(field)
    other_lower = {name.lower() for name in other_inputs}
    kept = {k: v for k, v in arguments.items() if k.lower() not in other_lower}
    headers_sent = {k.lower() for k in kept}
    header_params = set(route["header_params"])
    missing = [
        r
        for r in route["required"]
        if r not in kept and not (r in header_params and r.lower() in headers_sent)
    ]
    if missing:
        raise DispatchError(-32602, f"{field} {action} needs: {', '.join(missing)}")
    return action, route, kept


async def dispatch_tool(
    *,
    name: str,
    arguments: dict[str, Any],
    token: ResolvedToken,
) -> ToolResult:
    tool = _TOOLS_BY_NAME.get(name)
    if tool is None:
        raise _unknown_tool(name)

    if not token.odoo_api_key_value:
        raise DispatchError(-32000, "missing upstream credential")

    action: str | None = None
    route = tool
    if "actions" in tool:
        action, route, arguments = _pick_action(tool, arguments)

    # Schemas allow extra keys: drop the reseller switch regen strips (acts on a client).
    if "user_id" not in tool["input_schema"].get("properties", {}):
        arguments = {k: v for k, v in arguments.items() if k != "user_id"}
    arguments = _coerce_args(arguments, tool["input_schema"])
    path = _substitute_path(
        route["path"], arguments, route["path_params"], tool["input_schema"]
    )
    query, spec_headers, body = _split_args(
        arguments, route["path_params"], route["query_params"], route["header_params"]
    )

    url = f"{get_settings().backend_base_url.rstrip('/')}{path}"
    # Spec headers first, so a tool argument can never replace the credential.
    headers = {
        **spec_headers,
        "Authorization": f"Bearer {token.odoo_api_key_value}",
        "User-Agent": USER_AGENT,
    }
    if request_id := structlog.contextvars.get_contextvars().get("request_id"):
        headers["X-Request-ID"] = request_id
    method = route["method"]
    # Every PUT and PATCH tool changes fields; with none, the API gets no body at all.
    if method in ("PUT", "PATCH") and not body:
        log.info(
            "tool_result",
            tool=name,
            action=action,
            outcome="no_fields",
            status=None,
            duration_ms=0,
            client_id=token.client_id,
            client_name=token.client_name,
            odoo_user_id=token.odoo_user_id,
        )
        error = {"error": f"{name} needs at least one field to change besides the ids."}
        return ToolResult(text=json.dumps(error), is_error=True)

    request_kwargs: dict[str, Any] = {"params": query} if query else {}
    sent: Any = body.get(list_arg) if (list_arg := route.get("body_list_arg")) else body
    if method != "GET" and sent:
        request_kwargs["json"] = sent

    log.info(
        "tool_call",
        tool=name,
        action=action,
        method=method,
        path=path,
        client_id=token.client_id,
        client_name=token.client_name,
        odoo_user_id=token.odoo_user_id,
    )

    # One tool_result line per call, however it ends: Grafana's MCP board reads outcome,
    # status and duration_ms from it.
    started = time.monotonic()
    outcome, status = "network_error", None
    try:
        try:
            async with _client_factory() as client:
                res = await client.request(method, url, headers=headers, **request_kwargs)
        except httpx.TimeoutException as exc:
            outcome = "timeout"
            raise DispatchError(-32000, "upstream timeout", {"tool": name}) from exc
        except httpx.HTTPError as exc:
            raise DispatchError(-32000, "upstream network error", {"tool": name}) from exc

        outcome, status = "bad_response", res.status_code
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

        if res.status_code >= 500:
            outcome = "server_error"
            # The raw body often carries upstream stack-trace strings; keep
            # those in our logs and hand the client something actionable.
            log.warning(
                "tool_upstream_5xx",
                tool=name,
                status=res.status_code,
                body=json.dumps(payload)[:500],
            )
            envelope: dict[str, Any] = {
                "error": "The OmniDimension API could not process this request.",
                "status": res.status_code,
                "hint": (
                    "Check that nested fields match the tool's input schema "
                    "and retry once. If the error persists, try a smaller request."
                ),
            }
            # A tool whose 5xx says what to do next (a booking that may have gone
            # through must not be retried) relays the API's own message and code.
            if tool.get("relay_server_errors") and isinstance(payload, dict):
                envelope = {
                    "error": str(payload.get("error_description") or envelope["error"]),
                    "code": payload.get("code") or payload.get("error"),
                    "status": res.status_code,
                }
            return ToolResult(
                text=json.dumps(envelope, indent=2, ensure_ascii=False), is_error=True
            )

        if res.status_code >= 400:
            outcome = "client_error"
            text = json.dumps(payload, indent=2, ensure_ascii=False)
            return ToolResult(text=text, is_error=True)

        outcome = "ok"
        return _trim(payload)
    finally:
        span = trace.get_current_span()
        span.set_attributes(
            {"mcp.tool": name, "mcp.outcome": outcome, "omni.client_name": token.client_name or ""}
        )
        if outcome in ("server_error", "timeout", "network_error"):
            span.set_status(StatusCode.ERROR)
        log.info(
            "tool_result",
            tool=name,
            action=action,
            outcome=outcome,
            status=status,
            duration_ms=round((time.monotonic() - started) * 1000),
            client_id=token.client_id,
            client_name=token.client_name,
            odoo_user_id=token.odoo_user_id,
        )
