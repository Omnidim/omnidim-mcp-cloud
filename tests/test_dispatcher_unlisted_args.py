"""The reseller `user_id` never reaches the API from a tool call.

Regen strips `user_id` from every tool, but schemas allow extra keys, so a
model can still send it. Forwarded, it makes the API act on a client account.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.services import dispatcher
from app.services.bearer import ResolvedToken

TOKEN = ResolvedToken(
    odoo_user_id=7, odoo_api_key_id=1, odoo_api_key_value="key", client_id="app-1", scope=""
)


async def _sent(name: str, arguments: dict[str, Any]) -> httpx.Request:
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
    return seen[0]


async def test_user_id_never_reaches_the_api_body() -> None:
    req = await _sent(
        "purchasePhoneNumber", {"phone_number": "+15550100", "user_id": 99}
    )
    body = json.loads(req.content)
    assert "user_id" not in body
    assert body["phone_number"] == "+15550100"
    assert "user_id" not in req.url.params


async def test_user_id_never_reaches_the_api_query() -> None:
    req = await _sent("listAgents", {"pageno": 2, "user_id": 99})
    assert req.url.params.get("pageno") == "2"
    assert "user_id" not in req.url.params


async def test_other_unlisted_body_keys_still_pass() -> None:
    req = await _sent("createAgent", {"name": "a", "some_new_field": 1, "user_id": 99})
    body = json.loads(req.content)
    assert body["some_new_field"] == 1
    assert "user_id" not in body
