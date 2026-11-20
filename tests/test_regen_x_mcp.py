"""Regen builds tools from each operation's x-mcp block in the spec.

The block is the one source for a tool's title, its confirm hints, whether it is
hidden, and which inputs it never takes. An operation without one fails the regen,
so a new endpoint cannot reach agents before someone decides how it should.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

_spec = importlib.util.spec_from_file_location(
    "regen", Path(__file__).parent.parent / "scripts" / "regen.py"
)
assert _spec and _spec.loader
regen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(regen)


def _spec_with(**ops: dict[str, Any]) -> dict[str, Any]:
    paths: dict[str, Any] = {}
    for op_id, op in ops.items():
        method = op.pop("_method", "post")
        paths.setdefault(f"/{op_id}", {})[method] = {"operationId": op_id, **op}
    return {"paths": paths}


def _by_name(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tools, _ = regen.build_tools(spec)
    return {t["name"]: t for t in tools}


def test_an_operation_without_x_mcp_fails_the_regen() -> None:
    with pytest.raises(SystemExit, match="newThing has no x-mcp block"):
        regen.build_tools(_spec_with(newThing={}))


@pytest.mark.parametrize(
    "block",
    [
        {"title": "T", "effect": "maybe"},
        {"effect": "read"},
        {"title": "T", "effect": "read", "open-world": True},
        {"title": "T", "effect": "write", "colour": "red"},
        {"hidden": ""},
        {"hidden": "why", "title": "T"},
        {"title": 5, "effect": "write"},
        {"hidden": None},
        {"hidden": False},
        {"title": "T", "effect": "write", "hide-params": "user_id"},
        {"title": "T", "effect": "write", "hide-params": [1]},
        {"title": "T", "effect": "write", "open-world": 1},
        {"title": "T", "effect": ["write"]},
    ],
)
def test_a_malformed_block_fails_the_regen(block: dict[str, Any]) -> None:
    with pytest.raises(SystemExit, match="bad x-mcp on op"):
        regen.build_tools(_spec_with(op={"x-mcp": block}))


def test_a_get_must_be_a_read() -> None:
    with pytest.raises(SystemExit, match="bad x-mcp on op"):
        regen.build_tools(
            _spec_with(op={"_method": "get", "x-mcp": {"title": "T", "effect": "write"}})
        )


def test_a_hidden_operation_is_not_a_tool() -> None:
    spec = _spec_with(
        shown={"x-mcp": {"title": "Shown", "effect": "write"}},
        secret={"x-mcp": {"hidden": "Admin only."}},
    )
    tools, skipped = regen.build_tools(spec)
    assert [t["name"] for t in tools] == ["shown"]
    assert skipped == ["POST /secret"]


@pytest.mark.parametrize(
    ("block", "method", "expected"),
    [
        (
            {"title": "List things", "effect": "read"},
            "get",
            {"title": "List things", "readOnlyHint": True, "openWorldHint": False},
        ),
        (
            {"title": "Save thing", "effect": "write"},
            "post",
            {
                "title": "Save thing",
                "readOnlyHint": False,
                "destructiveHint": False,
                "openWorldHint": False,
            },
        ),
        (
            {"title": "Call someone", "effect": "destructive", "open-world": True},
            "post",
            {
                "title": "Call someone",
                "readOnlyHint": False,
                "destructiveHint": True,
                "openWorldHint": True,
            },
        ),
    ],
)
def test_effect_sets_the_hints(
    block: dict[str, Any], method: str, expected: dict[str, Any]
) -> None:
    tool = _by_name(_spec_with(op={"_method": method, "x-mcp": block}))["op"]
    assert tool["annotations"] == expected


def test_hide_params_drops_query_and_body_inputs() -> None:
    spec = _spec_with(
        buy={
            "x-mcp": {"title": "Buy", "effect": "destructive", "hide-params": ["user_id"]},
            "parameters": [{"name": "user_id", "in": "query", "schema": {"type": "integer"}}],
            "requestBody": {
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "required": ["number", "user_id"],
                            "properties": {
                                "number": {"type": "string"},
                                "user_id": {"type": "integer"},
                            },
                        }
                    }
                }
            },
        }
    )
    tool = _by_name(spec)["buy"]
    assert set(tool["input_schema"]["properties"]) == {"number"}
    assert tool["input_schema"]["required"] == ["number"]
    assert tool["query_params"] == []


_BRIEF = "Post-call actions. Add them with addPostCallAction."


def _briefed_spec(brief: Any = _BRIEF) -> dict[str, Any]:
    big = {
        "type": "object",
        "x-mcp-brief": brief,
        "properties": {
            f"field{i}": {"type": "string", "description": "x" * 200} for i in range(40)
        },
    }
    body = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "actions": {"$ref": "#/components/schemas/Big"},
            "per_call": {
                "allOf": [{"$ref": "#/components/schemas/Big"}],
                "description": "For this call only.",
            },
        },
    }
    spec = _spec_with(
        createThing={
            "x-mcp": {"title": "Create thing", "effect": "write"},
            "requestBody": {"content": {"application/json": {"schema": body}}},
        }
    )
    spec["components"] = {"schemas": {"Big": big}}
    return spec


def test_a_briefed_schema_becomes_one_free_form_line() -> None:
    props = _by_name(_briefed_spec())["createThing"]["input_schema"]["properties"]

    for name in ("actions", "per_call"):
        text = json.dumps(props[name])
        assert '"properties"' not in text, name
        assert _BRIEF in text, name
        assert len(text) < 400, name
    assert props["actions"] == {
        "type": "object",
        "additionalProperties": True,
        "description": _BRIEF,
    }
    assert props["per_call"]["description"] == "For this call only."
    assert props["name"] == {"type": "string"}


@pytest.mark.parametrize("brief", ["", "  ", 3, "two\nlines", "x" * 401])
def test_a_bad_brief_fails_the_regen(brief: Any) -> None:
    with pytest.raises(SystemExit, match="x-mcp-brief on Big"):
        regen.build_tools(_briefed_spec(brief))
