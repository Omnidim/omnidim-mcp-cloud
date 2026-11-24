from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import httpx
import pytest

from app.services import dispatcher
from app.services.bearer import ResolvedToken

_spec = importlib.util.spec_from_file_location(
    "regen", Path(__file__).parent.parent / "scripts" / "regen.py"
)
assert _spec and _spec.loader
regen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(regen)

TOKEN = ResolvedToken(
    odoo_user_id=7, odoo_api_key_id=1, odoo_api_key_value="key", client_id="app-1", scope=""
)

ID = [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}]


def _body(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    schema = {"type": "object", "required": required, "properties": properties}
    return {"content": {"application/json": {"schema": schema}}}


def _op(op_id: str, tool: str, action: Any, **extra: Any) -> dict[str, Any]:
    marks = {"title": op_id, "effect": "destructive", "merge": {"tool": tool, "action": action}}
    return {"operationId": op_id, "summary": op_id, "x-mcp": marks, "parameters": ID, **extra}


SPEC: dict[str, Any] = {
    "x-mcp-tools": {
        "bulkCallActions": {"title": "Control", "description": "Control a campaign."},
        "phoneNumberAgentActions": {"title": "Attach", "description": "Attach or detach."},
    },
    "paths": {
        "/bulk/{id}/start": {"post": _op("startBulkCall", "bulkCallActions", "start")},
        "/bulk/{id}/actions": {
            "put": _op(
                "bulkCallActions",
                "bulkCallActions",
                ["pause", "resume"],
                requestBody=_body(
                    {"action": {"type": "string", "enum": ["pause", "resume"]}}, ["action"]
                ),
            )
        },
        "/numbers/{id}/attach": {
            "post": _op(
                "attachPhoneNumber",
                "phoneNumberAgentActions",
                "attach",
                requestBody=_body({"agent_id": {"type": "integer"}}, ["agent_id"]),
            )
        },
        "/numbers/{id}/detach": {
            "post": _op("detachPhoneNumber", "phoneNumberAgentActions", "detach")
        },
    },
}


@pytest.fixture(autouse=True)
def merged_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    tools, _ = regen.build_tools(json.loads(json.dumps(SPEC)))
    monkeypatch.setattr(dispatcher, "_TOOLS_BY_NAME", {t["name"]: t for t in tools})


async def _sent(name: str, arguments: dict[str, Any]) -> list[httpx.Request]:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)
    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    try:
        await dispatcher.dispatch_tool(name=name, arguments=arguments, token=TOKEN)
    finally:
        dispatcher.reset_client_factory()
    return seen


async def test_the_action_picks_the_operation_route() -> None:
    [req] = await _sent("bulkCallActions", {"action": "start", "id": 4})
    assert req.method == "POST"
    assert req.url.path.endswith("/bulk/4/start")
    assert not req.content


async def test_a_listed_action_reaches_the_api_in_the_body() -> None:
    [req] = await _sent("bulkCallActions", {"action": "pause", "id": 4})
    assert req.method == "PUT"
    assert req.url.path.endswith("/bulk/4/actions")
    assert json.loads(req.content) == {"action": "pause"}


async def test_an_input_of_another_action_is_not_forwarded() -> None:
    [req] = await _sent("phoneNumberAgentActions", {"action": "detach", "id": 9, "agent_id": 3})
    assert req.url.path.endswith("/numbers/9/detach")
    assert not req.content


async def test_an_input_the_action_needs_is_asked_for_before_any_request() -> None:
    with pytest.raises(dispatcher.DispatchError, match="attach needs: agent_id"):
        await _sent("phoneNumberAgentActions", {"action": "attach", "id": 9})


@pytest.mark.parametrize("arguments", [{"id": 4}, {"action": "explode", "id": 4}])
async def test_an_unknown_action_lists_the_choices(arguments: dict[str, Any]) -> None:
    with pytest.raises(dispatcher.DispatchError, match="action must be one of: start, pause"):
        await _sent("bulkCallActions", arguments)


async def test_an_old_tool_name_points_at_its_new_tool() -> None:
    with pytest.raises(dispatcher.DispatchError) as caught:
        await _sent("detachPhoneNumber", {"id": 9})
    assert caught.value.message == (
        "unknown tool: detachPhoneNumber. Call phoneNumberAgentActions with action detach."
    )


async def test_a_name_that_never_existed_stays_unknown() -> None:
    with pytest.raises(dispatcher.DispatchError) as caught:
        await _sent("launchRocket", {})
    assert caught.value.message == "unknown tool: launchRocket"


class _Recorder:
    def __init__(self) -> None:
        self.lines: list[dict[str, Any]] = []

    def _record(self, event: str, **fields: Any) -> None:
        self.lines.append({"event": event, **fields})

    info = warning = error = _record


async def test_the_result_log_names_the_action(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _Recorder()
    monkeypatch.setattr(dispatcher, "log", recorder)
    await _sent("bulkCallActions", {"action": "resume", "id": 4})
    [result] = [line for line in recorder.lines if line["event"] == "tool_result"]
    assert (result["tool"], result["action"], result["outcome"]) == (
        "bulkCallActions",
        "resume",
        "ok",
    )
