"""Tool definitions for searchDocs and readDoc. The calls live in app/services/docs.py."""

from __future__ import annotations

from typing import Any, Final

_READ: Final = {"readOnlyHint": True, "openWorldHint": False}

DOCS_TOOLS: Final[list[dict[str, Any]]] = [
    {
        "name": "searchDocs",
        "description": (
            "Search the OmniDimension documentation (guides and API reference) at "
            "docs.omnidim.io. Use it before guessing how a feature, field or error works. "
            "Returns up to 8 pages, best first, each with title, description and url. Read a "
            "page with `readDoc`.\n\n(Tags: Docs)"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to look for, in a few words."}
            },
            "required": ["query"],
        },
        "annotations": {"title": "Search the docs", **_READ},
    },
    {
        "name": "readDoc",
        "description": (
            "Read one docs.omnidim.io page as Markdown. Pass a `url` from `searchDocs`, or a "
            "path that starts with /docs/.\n\n(Tags: Docs)"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": (
                        "A docs.omnidim.io page url or path, e.g. /docs/get-started/quickstart."
                    ),
                }
            },
            "required": ["url"],
        },
        "annotations": {"title": "Read a docs page", **_READ},
    },
]
