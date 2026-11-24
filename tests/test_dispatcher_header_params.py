"""Header parameters from the spec reach the API as headers, not body fields.

sendWhatsappMessage and launchWhatsappCampaign require `Idempotency-Key`. Sent in
the JSON body, the API sees no key and refuses the call.
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
    req = await _sent(
        "whatsappCampaignActions", {"action": "launch", "campaign_id": 5, "Idempotency-Key": "k-2"}
    )
    assert req.headers["Idempotency-Key"] == "k-2"
    assert req.url.path.endswith("/whatsapp/campaigns/5/launch")
    assert not req.content


async def test_a_header_param_cannot_replace_the_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # No spec tool declares Authorization today; a future one must not leak it.
    tool = dict(dispatcher._TOOLS_BY_NAME["whatsappCampaignActions"])
    launch = {**tool["actions"]["launch"], "header_params": ["Idempotency-Key", "Authorization"]}
    tool["actions"] = {**tool["actions"], "launch": launch}
    monkeypatch.setitem(dispatcher._TOOLS_BY_NAME, "whatsappCampaignActions", tool)
    req = await _sent(
        "whatsappCampaignActions",
        {
            "action": "launch",
            "campaign_id": 5,
            "Idempotency-Key": "k-3",
            "Authorization": "Bearer other",
        },
    )
    assert req.headers["Authorization"] == "Bearer key"


async def test_header_param_names_match_in_any_case() -> None:
    req = await _sent(
        "whatsappCampaignActions", {"action": "launch", "campaign_id": 5, "idempotency-key": "k-4"}
    )
    assert req.headers["Idempotency-Key"] == "k-4"
    assert not req.content


async def test_a_header_value_that_is_not_ascii_is_refused() -> None:
    with pytest.raises(dispatcher.DispatchError) as err:
        await _sent(
            "whatsappCampaignActions",
            {"action": "launch", "campaign_id": 5, "Idempotency-Key": "clé"},
        )
    assert err.value.code == -32602
