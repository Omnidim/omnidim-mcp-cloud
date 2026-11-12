"""An update call with no fields to change is refused before it reaches the API.

2026-11-12: Cursor called updateAgent with only agent_id. The dispatcher sent a PUT with
no body, the API answered 500, and the model got no hint of what it did wrong.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from app.services import dispatcher
from app.services.bearer import ResolvedToken

TOKEN = ResolvedToken(
    odoo_user_id=7, odoo_api_key_id=1, odoo_api_key_value="key", client_id="app-1", scope=""
)


@pytest.fixture
def sent() -> list[httpx.Request]:
    requests: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        requests.append(req)
        return httpx.Response(200, json={"success": True})

    transport = httpx.MockTransport(handler)
    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    yield requests
    dispatcher.reset_client_factory()


async def test_update_with_no_fields_is_refused(
    sent: list[httpx.Request], monkeypatch: pytest.MonkeyPatch
) -> None:
    lines: list[dict[str, Any]] = []
    monkeypatch.setattr(
        dispatcher.log, "info", lambda event, **kw: lines.append({"event": event, **kw})
    )
    result = await dispatcher.dispatch_tool(
        name="updateAgent", arguments={"agent_id": 279990}, token=TOKEN
    )

    assert result.is_error
    assert "at least one field" in json.loads(result.text)["error"]
    assert sent == []
    # status None keeps the paging alert (400, 422, 5xx) quiet: the model is told already.
    [line] = [x for x in lines if x["event"] == "tool_result"]
    assert (line["outcome"], line["status"]) == ("no_fields", None)


async def test_update_with_a_field_is_sent(sent: list[httpx.Request]) -> None:
    result = await dispatcher.dispatch_tool(
        name="updateAgent", arguments={"agent_id": 279990, "name": "Front desk"}, token=TOKEN
    )

    assert not result.is_error
    assert json.loads(sent[0].content) == {"name": "Front desk"}
