"""searchDocs and readDoc: answers from the public docs at docs.omnidim.io, no account data."""

from __future__ import annotations

import json
import re
import time
from typing import Any, Final
from urllib.parse import unquote, urlsplit

import httpx
import structlog

from app.docs_tools import DOCS_TOOLS
from app.services import dispatcher
from app.services.bearer import ResolvedToken
from app.services.dispatcher import DispatchError, ToolResult

log = structlog.get_logger()

DOCS_ORIGIN: Final = "https://docs.omnidim.io"
_MAX_DOC_CHARS: Final = 25_000
# One segment per path part: letters, digits, dash, underscore, dot (never a bare "." or "..").
_DOC_PATH_RE: Final = re.compile(r"^/docs(/(?!\.{1,2}(/|$))[A-Za-z0-9._-]+)*/?$")

DOCS_TOOL_NAMES: Final = frozenset(t["name"] for t in DOCS_TOOLS)


def _doc_path(raw: object) -> str:
    """The /docs/ path of a docs.omnidim.io page url or path, or a -32602 for anything else."""
    if not isinstance(raw, str) or not raw.strip():
        raise DispatchError(-32602, "readDoc needs a url")
    try:
        parts = urlsplit(raw.strip())
    except ValueError as exc:
        raise DispatchError(-32602, "readDoc needs a docs.omnidim.io url") from exc
    if parts.scheme or parts.netloc:
        if f"{parts.scheme}://{parts.netloc}" != DOCS_ORIGIN:
            raise DispatchError(-32602, "readDoc reads only https://docs.omnidim.io pages")
    path = unquote(parts.path)
    # fullmatch: match() with $ would let a trailing newline through.
    if not _DOC_PATH_RE.fullmatch(path):
        raise DispatchError(-32602, "readDoc reads only pages under /docs/")
    # The docs site redirects a trailing slash, and httpx does not follow redirects.
    return path.rstrip("/") or "/docs"


async def _get(url: str, **kwargs: Any) -> httpx.Response:
    # The user's API key never goes to the docs site: these requests carry no Authorization.
    headers = {"User-Agent": dispatcher.USER_AGENT, **kwargs.pop("headers", {})}
    async with dispatcher._client_factory() as client:
        return await client.get(url, headers=headers, **kwargs)


def _upstream_error(res: httpx.Response) -> ToolResult:
    if res.status_code == 429:
        text = "The docs search is busy. Wait a minute, then try again."
    else:
        text = f"docs.omnidim.io answered {res.status_code}. Try again later."
    return ToolResult(text=json.dumps({"error": text}), is_error=True)


async def _search(arguments: dict[str, Any]) -> ToolResult:
    query = arguments.get("query")
    if not isinstance(query, str) or not query.strip():
        raise DispatchError(-32602, "searchDocs needs a query")
    # /api/spotlight ranks pages the way the docs site's own search and chat do.
    res = await _get(f"{DOCS_ORIGIN}/api/spotlight", params={"q": query.strip()[:200]})
    if res.status_code != 200:
        return _upstream_error(res)
    hits = res.json()
    pages = [
        {
            "title": h.get("title"),
            "description": h.get("description"),
            "url": DOCS_ORIGIN + h["url"],
        }
        for h in hits
        if isinstance(h, dict) and isinstance(h.get("url"), str) and h["url"].startswith("/")
    ]
    return ToolResult(text=json.dumps({"pages": pages}, indent=2, ensure_ascii=False))


async def _read(arguments: dict[str, Any]) -> ToolResult:
    path = _doc_path(arguments.get("url"))
    res = await _get(f"{DOCS_ORIGIN}{path}", headers={"Accept": "text/markdown"})
    if res.status_code == 404:
        return ToolResult(text=json.dumps({"error": f"No docs page at {path}."}), is_error=True)
    if res.status_code != 200:
        return _upstream_error(res)
    text = res.text
    if len(text) > _MAX_DOC_CHARS:
        text = text[:_MAX_DOC_CHARS] + f"\n\n[Page cut at {_MAX_DOC_CHARS} of {len(text)} chars.]"
    return ToolResult(text=text)


async def call_docs_tool(name: str, arguments: dict[str, Any], token: ResolvedToken) -> ToolResult:
    started = time.monotonic()
    outcome = "network_error"
    try:
        try:
            result = await (_search if name == "searchDocs" else _read)(arguments)
        except DispatchError:
            outcome = "bad_arguments"
            raise
        except httpx.TimeoutException as exc:
            outcome = "timeout"
            raise DispatchError(-32000, "docs.omnidim.io timed out", {"tool": name}) from exc
        except httpx.HTTPError as exc:
            raise DispatchError(-32000, "docs.omnidim.io network error", {"tool": name}) from exc
        outcome = "client_error" if result.is_error else "ok"
        return result
    finally:
        # Same tool_result line as dispatch_tool, so the MCP board counts docs tools too.
        log.info(
            "tool_result",
            tool=name,
            outcome=outcome,
            status=None,
            duration_ms=round((time.monotonic() - started) * 1000),
            client_id=token.client_id,
            client_name=token.client_name,
            odoo_user_id=token.odoo_user_id,
        )
