"""The request id is the trace id when tracing is on, and nothing changes when it is off."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
import respx
import structlog
from httpx import ASGITransport, AsyncClient
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind, StatusCode

from app.main import create_app
from app.services import dispatcher
from app.services.bearer import ResolvedToken
from app.tracing import setup_tracing

HEX32 = re.compile(r"[0-9a-f]{32}")
TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"
TOKEN = ResolvedToken(
    odoo_user_id=7,
    odoo_api_key_id=1,
    odoo_api_key_value="key",
    client_id="app-1",
    scope="",
    client_name="Claude",
)


@pytest.fixture
def exporter() -> Iterator[InMemorySpanExporter]:
    mem = InMemorySpanExporter()
    yield mem


@pytest.fixture
async def traced(exporter: InMemorySpanExporter) -> AsyncIterator[AsyncClient]:
    app = create_app()
    provider = setup_tracing(app, exporter)
    app.state.tracer_provider = provider
    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            yield ac
    provider.force_flush()
    FastAPIInstrumentor.uninstrument_app(app)
    HTTPXClientInstrumentor().uninstrument()


def _spans(traced: AsyncClient, exporter: InMemorySpanExporter) -> tuple[ReadableSpan, ...]:
    traced._transport.app.state.tracer_provider.force_flush()  # type: ignore[attr-defined]
    return exporter.get_finished_spans()


async def test_traceparent_trace_id_is_the_request_id(traced: AsyncClient) -> None:
    res = await traced.get(
        "/.well-known/oauth-protected-resource",
        headers={"traceparent": f"00-{TRACE_ID}-00f067aa0ba902b7-01"},
    )
    assert res.headers["x-request-id"] == TRACE_ID


async def test_hex_request_id_becomes_the_trace_id(
    traced: AsyncClient, exporter: InMemorySpanExporter
) -> None:
    res = await traced.get(
        "/.well-known/oauth-protected-resource", headers={"x-request-id": TRACE_ID}
    )
    assert res.headers["x-request-id"] == TRACE_ID
    assert {format(s.context.trace_id, "032x") for s in _spans(traced, exporter)} == {TRACE_ID}


async def test_no_incoming_id_uses_the_span_trace_id(
    traced: AsyncClient, exporter: InMemorySpanExporter
) -> None:
    res = await traced.get("/.well-known/oauth-protected-resource")
    rid = res.headers["x-request-id"]
    assert HEX32.fullmatch(rid)
    assert format(_spans(traced, exporter)[0].context.trace_id, "032x") == rid


async def test_non_hex_request_id_stays_a_log_id(traced: AsyncClient) -> None:
    res = await traced.get("/.well-known/oauth-protected-resource", headers={"x-request-id": "abc"})
    assert HEX32.fullmatch(res.headers["x-request-id"])


async def test_health_checks_are_not_traced(
    traced: AsyncClient, exporter: InMemorySpanExporter
) -> None:
    for path in ("/healthz", "/readyz"):
        await traced.get(path)
    assert _spans(traced, exporter) == ()


async def test_odoo_call_carries_traceparent_and_request_id(
    traced: AsyncClient, exporter: InMemorySpanExporter
) -> None:
    seen: list[httpx.Headers] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req.headers)
        return httpx.Response(500, json={"error": "boom"})

    tracer = traced._transport.app.state.tracer_provider.get_tracer("test")  # type: ignore[attr-defined]
    try:
        with respx.mock() as mock, tracer.start_as_current_span("root") as root:
            mock.route().mock(side_effect=handler)
            rid = format(root.get_span_context().trace_id, "032x")
            structlog.contextvars.bind_contextvars(request_id=rid)
            await dispatcher.dispatch_tool(name="listAgents", arguments={}, token=TOKEN)
    finally:
        structlog.contextvars.clear_contextvars()
        dispatcher.reset_client_factory()
    assert seen[0]["traceparent"].split("-")[1] == rid
    assert seen[0]["x-request-id"] == rid
    root_span = next(s for s in _spans(traced, exporter) if s.name == "root")
    assert root_span.attributes is not None
    assert root_span.attributes["mcp.tool"] == "listAgents"
    assert root_span.attributes["mcp.outcome"] == "server_error"
    assert root_span.attributes["omni.client_name"] == "Claude"
    assert root_span.status.status_code == StatusCode.ERROR


async def test_tracing_off_keeps_todays_behaviour(
    client: AsyncClient, exporter: InMemorySpanExporter
) -> None:
    res = await client.get("/healthz", headers={"x-request-id": TRACE_ID})
    assert res.headers["x-request-id"] == TRACE_ID
    res = await client.get(
        "/healthz", headers={"traceparent": f"00-{TRACE_ID}-00f067aa0ba902b7-01"}
    )
    assert res.headers["x-request-id"] != TRACE_ID
    assert exporter.get_finished_spans() == ()


async def test_traces_carry_no_secrets(traced: AsyncClient, exporter: InMemorySpanExporter) -> None:
    tracer = traced._transport.app.state.tracer_provider.get_tracer("test")  # type: ignore[attr-defined]
    with respx.mock() as mock:
        mock.route().mock(return_value=httpx.Response(200, json={}))
        with tracer.start_as_current_span("api"):
            async with httpx.AsyncClient() as c:
                await c.get("https://omnidim.io/api/v1/agents?token=SEKRET")
        with pytest.raises(ValueError, match="SEKRET"), tracer.start_as_current_span("boom"):
            raise ValueError("SEKRET in message")
    app_res = await traced.get("/.well-known/oauth-protected-resource?token=SEKRET")
    assert app_res.status_code == 200
    spans = _spans(traced, exporter)
    dump = repr([(s.name, dict(s.attributes or {}), s.events, s.status) for s in spans])
    assert "SEKRET" not in dump
    client_span = next(s for s in spans if s.kind == SpanKind.CLIENT)
    assert client_span.attributes["http.url"] == "https://omnidim.io"  # type: ignore[index]
    server_span = next(s for s in spans if s.kind == SpanKind.SERVER)
    assert server_span.attributes["http.route"] == "/.well-known/oauth-protected-resource"  # type: ignore[index]
    boom = next(s for s in spans if s.name == "boom")
    assert boom.events == () and boom.status.description == "ValueError"
