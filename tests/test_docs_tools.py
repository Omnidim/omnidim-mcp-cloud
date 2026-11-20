"""searchDocs and readDoc answer from docs.omnidim.io, and readDoc reads nothing outside /docs/."""

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from httpx import AsyncClient

from tests.test_mcp_transport import _mint_access_token, mock_backend  # noqa: F401

Backend = Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]]

_HITS = [
    {
        "url": "/docs/bulk-calls/overview",
        "title": "Bulk Call Campaign Guide",
        "description": "Create and manage bulk call campaigns.",
        "kind": "guide",
    },
]


async def _call(client: AsyncClient, name: str, arguments: dict[str, Any]) -> Any:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
    )
    return res.json()


async def test_docs_tools_are_listed_as_read_only(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )
    tools = {t["name"]: t for t in res.json()["result"]["tools"]}

    for name in ("searchDocs", "readDoc"):
        assert tools[name]["annotations"]["readOnlyHint"] is True
        assert tools[name]["annotations"]["openWorldHint"] is False


async def test_search_docs_returns_pages_with_full_urls(
    client: AsyncClient,
    mock_backend: Backend,  # noqa: F811
) -> None:
    captured = mock_backend(lambda req: httpx.Response(200, json=_HITS))

    body = await _call(client, "searchDocs", {"query": "bulk call concurrency"})

    result = body["result"]
    assert result["isError"] is False
    pages = json.loads(result["content"][0]["text"])["pages"]
    assert pages[0]["url"] == "https://docs.omnidim.io/docs/bulk-calls/overview"
    assert pages[0]["title"] == "Bulk Call Campaign Guide"
    (req,) = captured
    assert req.url.host == "docs.omnidim.io"
    assert req.url.params["q"] == "bulk call concurrency"
    assert "authorization" not in req.headers


async def test_search_docs_needs_a_query(client: AsyncClient) -> None:
    body = await _call(client, "searchDocs", {"query": "  "})

    assert body["error"]["code"] == -32602


async def test_search_docs_reports_a_busy_docs_site(
    client: AsyncClient,
    mock_backend: Backend,  # noqa: F811
) -> None:
    mock_backend(lambda req: httpx.Response(429, json={"error": "too many searches"}))

    body = await _call(client, "searchDocs", {"query": "webhook"})

    assert body["result"]["isError"] is True
    assert "try again" in body["result"]["content"][0]["text"]


async def test_read_doc_returns_the_page_as_markdown(
    client: AsyncClient,
    mock_backend: Backend,  # noqa: F811
) -> None:
    captured = mock_backend(
        lambda req: httpx.Response(
            200, text="# Quickstart\n\nSteps.", headers={"content-type": "text/markdown"}
        )
    )

    body = await _call(
        client, "readDoc", {"url": "https://docs.omnidim.io/docs/get-started/quickstart"}
    )

    assert body["result"]["content"][0]["text"].startswith("# Quickstart")
    (req,) = captured
    assert req.url.path == "/docs/get-started/quickstart"
    assert req.headers["accept"] == "text/markdown"
    assert "authorization" not in req.headers


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example/docs/x",
        "/api/chat",
        "/docs/../api/chat",
        "/docs/%2e%2e/api/chat",
        "//evil.example/docs/x",
        "http://docs.omnidim.io/docs/x",
        "https://docs.omnidim.io.evil.example/docs/x",
    ],
)
async def test_read_doc_refuses_anything_outside_the_docs(
    client: AsyncClient,
    mock_backend: Backend,  # noqa: F811
    url: str,
) -> None:
    captured = mock_backend(lambda req: httpx.Response(200, text="x"))

    body = await _call(client, "readDoc", {"url": url})

    assert body["error"]["code"] == -32602
    assert captured == []
