"""Header parameters from the spec reach the API as headers, not body fields.

sendWhatsappMessage and launchWhatsappCampaign require `Idempotency-Key`. Sent in
the JSON body, the API sees no key and refuses the call.
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


async def test_idempotency_key_is_a_header_on_a_body_request() -> None:
    req = await _sent(
        "sendWhatsappMessage",
        {"Idempotency-Key": "k-1", "number_id": 5, "to": "+15550100", "type": "text"},
    )
    assert req.headers["Idempotency-Key"] == "k-1"
    body = json.loads(req.content)
    assert "Idempotency-Key" not in body
    assert body["to"] == "+15550100"


async def test_idempotency_key_is_a_header_with_no_body() -> None:
    req = await _sent("launchWhatsappCampaign", {"campaign_id": 5, "Idempotency-Key": "k-2"})
    assert req.headers["Idempotency-Key"] == "k-2"
    assert req.url.path.endswith("/whatsapp/campaigns/5/launch")
    assert not req.content


async def test_auth_headers_cannot_be_overridden_by_arguments() -> None:
    req = await _sent(
        "launchWhatsappCampaign",
        {"campaign_id": 5, "Idempotency-Key": "k-3", "Authorization": "Bearer other"},
    )
    assert req.headers["Authorization"] == "Bearer key"
