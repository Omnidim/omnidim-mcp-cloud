"""Every tool call logs one `tool_result` line with its outcome, HTTP status and duration.

Grafana's MCP board reads these lines to show error rates and slow tools per tool, so each
way a call can end must produce exactly one of them.
"""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Iterator
from typing import Any

import httpx
import pytest

from app.services import dispatcher
from app.services.bearer import ResolvedToken

TOKEN = ResolvedToken(
    odoo_user_id=7, odoo_api_key_id=1, odoo_api_key_value="key", client_id="app-1", scope=""
)


@pytest.fixture
def backend() -> Iterator[Callable[[Callable[[httpx.Request], httpx.Response]], None]]:
    def setup(handler: Callable[[httpx.Request], httpx.Response]) -> None:
        transport = httpx.MockTransport(handler)
        dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))

    yield setup
    dispatcher.reset_client_factory()


class _Recorder:
    """Stands in for the dispatcher's logger. structlog's capture_logs misses a logger that
    another test already cached, so record the calls themselves."""

    def __init__(self) -> None:
        self.lines: list[dict[str, Any]] = []

    def _record(self, event: str, **fields: Any) -> None:
        self.lines.append({"event": event, **fields})

    info = warning = error = _record


async def _result_lines(
    backend: Callable[[Callable[[httpx.Request], httpx.Response]], None],
    handler: Callable[[httpx.Request], httpx.Response],
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, Any]]:
    backend(handler)
    recorder = _Recorder()
    monkeypatch.setattr(dispatcher, "log", recorder)
    # Timeouts and network errors end in DispatchError by design; the line is what we test.
    with contextlib.suppress(dispatcher.DispatchError):
        await dispatcher.dispatch_tool(name="listAgents", arguments={}, token=TOKEN)
    return [line for line in recorder.lines if line["event"] == "tool_result"]


def _raise_timeout(req: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("slow", request=req)


def _raise_network(req: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("refused", request=req)


@pytest.mark.parametrize(
    ("handler", "outcome", "status"),
    [
        (lambda req: httpx.Response(200, json={"agents": []}), "ok", 200),
        (lambda req: httpx.Response(403, json={"error": "forbidden"}), "client_error", 403),
        (lambda req: httpx.Response(500, json={"error": "boom"}), "server_error", 500),
        (lambda req: httpx.Response(502, text="<html>bad gateway</html>"), "bad_response", 502),
        (_raise_timeout, "timeout", None),
        (_raise_network, "network_error", None),
    ],
)
async def test_each_outcome_logs_one_result_line(
    backend, handler, outcome, status, monkeypatch
) -> None:
    lines = await _result_lines(backend, handler, monkeypatch)

    assert len(lines) == 1
    line = lines[0]
    assert line["outcome"] == outcome
    assert line["status"] == status
    assert line["tool"] == "listAgents"
    assert line["client_id"] == "app-1"
    assert line["odoo_user_id"] == 7
    assert isinstance(line["duration_ms"], int)
    assert line["duration_ms"] >= 0
