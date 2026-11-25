"""scripts/regen.py: the internal spec fragment, its operator-only tools and extra parameters."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from typing import Any

import pytest

_spec = importlib.util.spec_from_file_location(
    "regen", Path(__file__).parent.parent / "scripts" / "regen.py"
)
assert _spec and _spec.loader
regen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(regen)

READ = {"title": "T", "effect": "read"}
SPEC: dict[str, Any] = {
    "paths": {
        "/calls/logs": {
            "get": {
                "operationId": "listCallLogs",
                "x-mcp": READ,
                "parameters": [
                    {"$ref": "#/components/parameters/ClientUserId"},
                    {"name": "pageno", "in": "query", "schema": {"type": "integer"}},
                ],
            }
        },
    },
    "components": {
        "parameters": {
            "ClientUserId": {"name": "user_id", "in": "query", "schema": {"type": "integer"}}
        },
        "schemas": {"Agent": {"type": "object"}},
    },
}
INTERNAL: dict[str, Any] = {
    "paths": {
        "/calls/logs/{call_log_id}/events": {
            "get": {
                "operationId": "getCallEvents",
                "x-mcp": READ,
                "parameters": [
                    {"$ref": "#/components/parameters/ClientUserId"},
                    {"name": "call_log_id", "in": "path", "schema": {"type": "integer"}},
                ],
            }
        },
        "/support/cases": {
            "post": {"operationId": "createSupportCase", "x-mcp": {"title": "C", "effect": "write"}}
        },
    },
    "components": {"schemas": {"SupportCase": {"type": "object"}}},
    "x-extra-parameters": {
        "listCallLogs": [{"name": "date_from", "in": "query", "schema": {"type": "string"}}]
    },
}


def _build(internal: dict[str, Any]) -> dict[str, dict[str, Any]]:
    spec = copy.deepcopy(SPEC)
    operator_only = regen.merge_internal(spec, copy.deepcopy(internal))
    tools, _ = regen.build_tools(spec, operator_only)
    return {t["name"]: t for t in tools}


def test_internal_operations_are_operator_only_and_ref_params_resolve() -> None:
    tools = _build(INTERNAL)
    assert tools["getCallEvents"]["operator_only"] is True
    assert tools["createSupportCase"]["operator_only"] is True
    assert "operator_only" not in tools["listCallLogs"]
    assert list(tools["getCallEvents"]["input_schema"]["properties"]) == ["call_log_id"]
    assert tools["listCallLogs"]["query_params"] == ["pageno", "date_from"]


@pytest.mark.parametrize(
    "internal",
    [
        {"paths": {"/calls/logs": {}}},
        {"components": {"schemas": {"Agent": {}}}},
        {"x-extra-parameters": {"listCallLogs": [{"name": "pageno", "in": "query"}]}},
        {"x-extra-parameters": {"listCallLogs": [{"name": "user_id", "in": "query"}]}},
        {"x-extra-parameters": {"noSuchOp": [{"name": "x", "in": "query"}]}},
    ],
)
def test_overlaps_with_the_public_spec_stop_the_regen(internal: dict[str, Any]) -> None:
    with pytest.raises(SystemExit):
        _build(internal)


def test_committed_internal_spec_builds() -> None:
    import yaml

    internal = yaml.safe_load((Path(__file__).parent.parent / "internal-openapi.yaml").read_text())
    assert set(internal["x-extra-parameters"]) == {"listCallLogs"}
    ops = {
        op["operationId"] for item in internal["paths"].values() for op in item.values()
    }
    assert ops == {
        "getCallEvents", "getPlanAndAddons", "createSupportCase", "getSupportCase", "addCaseMessage"
    }
