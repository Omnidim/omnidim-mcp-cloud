"""Rules the Claude and ChatGPT directories check on every tool we list.

Regen PRs run these too, so a spec change that breaks a rule fails CI here,
not in a directory review.
"""
from typing import Any

import pytest

from app.routes.mcp import _tools_for_listing

TOOLS = _tools_for_listing(read_only=False)
HINTS = ("readOnlyHint", "destructiveHint", "openWorldHint")


def _untyped_properties(node: Any, path: str) -> list[str]:
    if not isinstance(node, dict):
        return []
    found: list[str] = []
    for key, prop in (node.get("properties") or {}).items():
        if isinstance(prop, dict) and "type" not in prop:
            found.append(f"{path}.{key}")
        found += _untyped_properties(prop, f"{path}.{key}")
    found += _untyped_properties(node.get("items"), f"{path}[]")
    return found


@pytest.mark.parametrize("tool", TOOLS, ids=lambda t: t["name"])
def test_tool_meets_directory_rules(tool: dict[str, Any]) -> None:
    annotations = tool["annotations"]
    # Claude: names of 64 characters or fewer, and a title on every tool.
    assert len(tool["name"]) <= 64
    assert annotations.get("title")
    # ChatGPT: each hint set explicitly to true or false.
    assert [h for h in HINTS if not isinstance(annotations.get(h), bool)] == []
    # Claude's portal refuses a parameter with no top-level `type`.
    assert _untyped_properties(tool["inputSchema"], "") == []
