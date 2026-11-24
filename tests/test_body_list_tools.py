from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import httpx

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
CONTACT = {"type": "object", "properties": {"phone_number": {"type": "string"}}}


def _one_or_many_tool() -> dict[str, Any]:
    spec = {
        "paths": {
            "/campaigns/{campaign_id}/contacts": {
                "post": {
                    "operationId": "addContacts",
                    "x-mcp": {"title": "Add contacts", "effect": "write"},
                    "parameters": [
                        {
                            "name": "campaign_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "description": "One contact object, or an array of 1 to 500.",
                                    "oneOf": [CONTACT, {"type": "array", "items": CONTACT}],
                                }
                            }
                        },
                    },
                }
            }
        }
    }
    tools, _ = regen.build_tools(spec)
    return tools[0]


def test_a_one_or_many_body_becomes_a_required_items_list() -> None:
    tool = _one_or_many_tool()
    items = tool["input_schema"]["properties"]["items"]
    assert items["type"] == "array"
    assert items["items"]["properties"]["phone_number"]["type"] == "string"
    assert "items" in tool["input_schema"]["required"]
    assert tool["body_list_arg"] == "items"


def test_a_plain_object_body_has_no_list_argument() -> None:
    spec = {
        "paths": {
            "/x": {
                "post": {
                    "operationId": "x",
                    "x-mcp": {"title": "X", "effect": "write"},
                    "requestBody": {"content": {"application/json": {"schema": CONTACT}}},
                }
            }
        }
    }
    tools, _ = regen.build_tools(spec)
    assert "body_list_arg" not in tools[0]


async def test_the_items_list_is_sent_as_the_request_body() -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json={})

    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    try:
        await dispatcher.dispatch_tool(
            name="addWhatsappCampaignContacts",
            arguments={"campaign_id": 5, "items": [{"phone_number": "+15550100"}]},
            token=TOKEN,
        )
    finally:
        dispatcher.reset_client_factory()
    assert seen[0].url.path.endswith("/whatsapp/campaigns/5/contacts")
    assert json.loads(seen[0].content) == [{"phone_number": "+15550100"}]
