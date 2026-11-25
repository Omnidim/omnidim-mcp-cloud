from __future__ import annotations

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

GROUP = {"workflowActions": {"title": "Turn workflow on or off", "description": "Turn it."}}


def _op(op_id: str, merge: dict[str, Any] | None, **extra: Any) -> dict[str, Any]:
    marks: dict[str, Any] = {"title": op_id, "effect": extra.pop("_effect", "destructive")}
    if merge is not None:
        marks["merge"] = merge
    return {"operationId": op_id, "summary": f"{op_id} summary", "x-mcp": marks, **extra}


def _workflow_spec(groups: dict[str, Any] | None = None) -> dict[str, Any]:
    path_param = [
        {"name": "workflow_id", "in": "path", "required": True, "schema": {"type": "integer"}}
    ]
    return {
        "x-mcp-tools": GROUP if groups is None else groups,
        "paths": {
            "/workflows/{workflow_id}/activate": {
                "parameters": path_param,
                "post": _op("activateWorkflow", {"tool": "workflowActions", "action": "activate"}),
            },
            "/workflows/{workflow_id}/deactivate": {
                "parameters": path_param,
                "post": _op(
                    "deactivateWorkflow", {"tool": "workflowActions", "action": "deactivate"}
                ),
            },
            "/workflows": {"get": _op("listWorkflows", None, _effect="read")},
        },
    }


def _by_name(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tools, _ = regen.build_tools(spec)
    return {t["name"]: t for t in tools}


def test_merged_operations_become_one_tool_with_an_action_field() -> None:
    tools = _by_name(_workflow_spec())
    assert set(tools) == {"workflowActions", "listWorkflows"}
    tool = tools["workflowActions"]
    action = tool["input_schema"]["properties"]["action"]
    assert action["enum"] == ["activate", "deactivate"]
    assert tool["input_schema"]["required"] == ["action", "workflow_id"]
    assert tool["annotations"]["title"] == "Turn workflow on or off"
    assert "activateWorkflow summary" in tool["description"]
    assert "deactivateWorkflow summary" in tool["description"]


def test_a_description_names_the_merged_tool_in_place_of_a_folded_operation() -> None:
    spec = _workflow_spec()
    spec["paths"]["/workflows"]["get"]["description"] = "To pause one, use `deactivateWorkflow`."
    spec["paths"]["/workflows/{workflow_id}/activate"]["post"]["description"] = (
        "Undo it with `deactivateWorkflow`."
    )
    tools = _by_name(spec)

    pointer = "use `workflowActions` with `action` `deactivate`."
    assert pointer in tools["listWorkflows"]["description"]
    merged = tools["workflowActions"]["description"]
    assert "Undo it with `workflowActions` with `action` `deactivate`." in merged
    assert "`deactivateWorkflow`" not in merged


def test_each_action_keeps_its_own_route() -> None:
    routes = _by_name(_workflow_spec())["workflowActions"]["actions"]
    assert routes["deactivate"]["operation"] == "deactivateWorkflow"
    assert routes["deactivate"]["method"] == "POST"
    assert routes["deactivate"]["path"] == "/workflows/{workflow_id}/deactivate"
    assert routes["deactivate"]["path_params"] == ["workflow_id"]
    assert routes["activate"]["path"] == "/workflows/{workflow_id}/activate"


def test_an_input_only_some_actions_take_is_optional_and_says_so() -> None:
    spec = _workflow_spec()
    spec["paths"]["/workflows/{workflow_id}/activate"]["post"]["requestBody"] = {
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["reason"],
                    "properties": {"reason": {"type": "string", "description": "Why."}},
                }
            }
        },
    }
    tool = _by_name(spec)["workflowActions"]
    assert "reason" not in tool["input_schema"]["required"]
    assert tool["input_schema"]["properties"]["reason"]["description"].startswith(
        "Only for `activate`."
    )
    assert tool["actions"]["activate"]["required"] == ["reason", "workflow_id"]
    assert "reason" not in tool["actions"]["deactivate"]["inputs"]


def test_a_listed_action_passes_through_to_the_operation_body() -> None:
    body = {
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["action"],
                    "properties": {"action": {"type": "string", "enum": ["pause", "resume"]}},
                }
            }
        }
    }
    spec = {
        "x-mcp-tools": {"bulkCallActions": {"title": "Control", "description": "Control it."}},
        "paths": {
            "/bulk/{id}/start": {
                "post": _op(
                    "startBulkCall",
                    {"tool": "bulkCallActions", "action": "start"},
                    parameters=[{"name": "id", "in": "path", "required": True}],
                )
            },
            "/bulk/{id}/actions": {
                "put": _op(
                    "bulkCallActions",
                    {"tool": "bulkCallActions", "action": ["pause", "resume"]},
                    parameters=[{"name": "id", "in": "path", "required": True}],
                    requestBody=body,
                )
            },
        },
    }
    tool = _by_name(spec)["bulkCallActions"]
    assert tool["input_schema"]["properties"]["action"]["enum"] == ["start", "pause", "resume"]
    assert tool["actions"]["pause"]["sends_field"] is True
    assert tool["actions"]["start"]["sends_field"] is False
    assert tool["actions"]["pause"]["operation"] == "bulkCallActions"


def test_the_merged_tool_asks_before_its_strongest_action() -> None:
    spec = _workflow_spec()
    spec["paths"]["/workflows/{workflow_id}/activate"]["post"]["x-mcp"]["effect"] = "write"
    spec["paths"]["/workflows/{workflow_id}/activate"]["post"]["x-mcp"]["open-world"] = True
    annotations = _by_name(spec)["workflowActions"]["annotations"]
    assert annotations["destructiveHint"] is True
    assert annotations["openWorldHint"] is True


def test_a_custom_field_name_replaces_action() -> None:
    groups = {"workflowActions": {**GROUP["workflowActions"], "field": "state"}}
    tool = _by_name(_workflow_spec(groups))["workflowActions"]
    assert "state" in tool["input_schema"]["properties"]
    assert "action" not in tool["input_schema"]["properties"]
    assert tool["field"] == "state"


def test_a_merge_into_an_undeclared_tool_fails_the_regen() -> None:
    with pytest.raises(SystemExit, match="workflowActions is not declared under x-mcp-tools"):
        regen.build_tools(_workflow_spec(groups={}))


def test_a_merged_tool_needs_two_operations() -> None:
    spec = _workflow_spec()
    del spec["paths"]["/workflows/{workflow_id}/deactivate"]
    with pytest.raises(SystemExit, match="workflowActions folds one operation"):
        regen.build_tools(spec)


def test_two_actions_that_disagree_on_an_input_fail_the_regen() -> None:
    spec = _workflow_spec()
    path = spec["paths"]["/workflows/{workflow_id}/deactivate"]
    path["parameters"] = [
        {"name": "workflow_id", "in": "path", "required": True, "schema": {"type": "string"}}
    ]
    with pytest.raises(SystemExit, match="workflow_id differs"):
        regen.build_tools(spec)


@pytest.mark.parametrize(
    "merge",
    [
        {"tool": "workflowActions"},
        {"tool": "workflowActions", "action": ""},
        {"tool": "workflowActions", "action": "Turn On"},
        {"tool": 5, "action": "on"},
        {"tool": "workflowActions", "action": []},
    ],
)
def test_a_bad_merge_mark_fails_the_regen(merge: dict[str, Any]) -> None:
    spec = _workflow_spec()
    spec["paths"]["/workflows/{workflow_id}/activate"]["post"]["x-mcp"]["merge"] = merge
    with pytest.raises(SystemExit, match="bad x-mcp on activateWorkflow: merge takes"):
        regen.build_tools(spec)
