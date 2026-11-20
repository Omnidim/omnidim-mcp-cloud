"""Booking a demo with the OmniDimension team from chat: the tools and their procedure."""

from __future__ import annotations

import json
from collections.abc import Iterator

import httpx
import pytest

from app.annotations import tool_annotations
from app.procedures import EXTRA_TOOLS, ROUTING_GUIDE, build_prompt
from app.routes.mcp import INSTRUCTIONS
from app.services import dispatcher
from app.services.bearer import ResolvedToken

TOKEN = ResolvedToken(
    odoo_user_id=7, odoo_api_key_id=1, odoo_api_key_value="key", client_id="app-1", scope=""
)
ANSWERS = {
    "name": "Dana Shah",
    "email": "dana@acme.com",
    "timezone": "Asia/Kolkata",
    "guests": ["cto@acme.com"],
    "answers": {"Company name": "Acme", "What is your Monthly Call Volume?": "20,000+ calls/month"},
}


@pytest.fixture
def seen() -> Iterator[list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        requests.append(req)
        return httpx.Response(200, json={"status": "booked", "meeting": {"join_url": "x"}})

    transport = httpx.MockTransport(handler)
    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    yield requests
    dispatcher.reset_client_factory()


def _tool(name: str) -> dict:
    return next(t for t in EXTRA_TOOLS if t["name"] == name)


def test_the_three_demo_tools_have_titles_and_honest_hints() -> None:
    questions = tool_annotations("getDemoQuestions", _tool("getDemoQuestions")["method"])
    assert questions["readOnlyHint"] is True
    for name in ("requestDemo", "bookDemo"):
        hints = tool_annotations(name, _tool(name)["method"])
        assert "title" in hints, name
        # Both reach people outside the chat: a call from our team, or a calendar invite.
        assert hints["readOnlyHint"] is False, name
        assert hints["openWorldHint"] is True, name


def test_every_hand_written_tool_has_a_title() -> None:
    missing = [
        t["name"] for t in EXTRA_TOOLS if "title" not in tool_annotations(t["name"], t["method"])
    ]
    assert missing == []


def test_only_the_answers_are_required() -> None:
    assert _tool("getDemoQuestions")["input_schema"]["required"] == []
    request = _tool("requestDemo")["input_schema"]
    assert "after" in request["properties"]
    assert "after" not in request["required"]
    assert set(_tool("bookDemo")["input_schema"]["required"]) == {
        "name", "email", "timezone", "answers", "start_time"
    }


def test_the_routing_guide_sends_demo_requests_to_the_procedure() -> None:
    # Clients without prompts pick tools from this guide and the tool text alone.
    assert "`book_demo` prompt" in ROUTING_GUIDE
    assert "Use it when the user asks for a demo" in _tool("getDemoQuestions")["description"]


def test_the_server_instructions_say_when_to_offer_a_demo() -> None:
    # Clients defer tool descriptions, so only the instructions reach every session.
    assert "getDemoQuestions" in INSTRUCTIONS
    assert "thousands of calls a month" in INSTRUCTIONS
    assert "do not offer again" in INSTRUCTIONS


def test_the_procedure_never_dead_ends_on_an_empty_week() -> None:
    text = build_prompt("book_demo", {})["messages"][0]["content"]["text"]
    assert "next_after" in text
    assert "next_after" in _tool("requestDemo")["description"]


async def test_book_demo_sends_the_answers_and_the_picked_slot(seen: list[httpx.Request]) -> None:
    args = {**ANSWERS, "start_time": "2026-11-21T09:30:00Z"}
    result = await dispatcher.dispatch_tool(name="bookDemo", arguments=args, token=TOKEN)

    (req,) = seen
    assert (req.method, str(req.url)) == ("POST", "https://omnidim.io/api/v1/demo/book")
    assert req.headers["authorization"] == "Bearer key"
    assert json.loads(req.content) == args
    assert "join_url" in result.text


async def test_request_demo_posts_to_the_routing_endpoint(seen: list[httpx.Request]) -> None:
    await dispatcher.dispatch_tool(name="requestDemo", arguments=ANSWERS, token=TOKEN)
    assert [(r.method, r.url.path) for r in seen] == [("POST", "/api/v1/demo/request")]


def test_the_procedure_asks_everything_then_routes_then_books() -> None:
    text = build_prompt("book_demo", {})["messages"][0]["content"]["text"]
    order = [text.index(step) for step in ("getDemoQuestions", "requestDemo", "bookDemo")]
    assert order == sorted(order)
    # Below the gate the server's own `message` is the whole reply: no meeting is promised.
    assert "tell the user the `message` and stop" in text
    assert "join link" in text


def _answering(status: int, body: dict) -> None:
    transport = httpx.MockTransport(lambda _req: httpx.Response(status, json=body))
    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))


UNCONFIRMED = {
    "error": "calendly_error",
    "error_description": (
        "The calendar did not confirm the booking. "
        "Check your email for an invite before you try again."
    ),
    "code": "booking_unconfirmed",
}


async def test_an_unconfirmed_booking_reaches_the_model_with_its_own_message() -> None:
    _answering(502, UNCONFIRMED)
    try:
        args = {**ANSWERS, "start_time": "2026-11-21T09:30:00Z"}
        result = await dispatcher.dispatch_tool(name="bookDemo", arguments=args, token=TOKEN)
    finally:
        dispatcher.reset_client_factory()
    body = json.loads(result.text)
    assert result.is_error
    assert body["code"] == "booking_unconfirmed"
    assert "Check your email" in body["error"]
    # The generic 5xx hint says to retry once, which could book the demo twice.
    assert "hint" not in body


async def test_other_tools_keep_the_generic_server_error() -> None:
    _answering(502, UNCONFIRMED)
    try:
        result = await dispatcher.dispatch_tool(name="listAgents", arguments={}, token=TOKEN)
    finally:
        dispatcher.reset_client_factory()
    assert "could not process this request" in json.loads(result.text)["error"]
