from __future__ import annotations

from typing import Literal

import structlog
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["telemetry"])
log = structlog.get_logger()


class ToolErrorEntry(BaseModel):
    code: str = Field(min_length=1, max_length=48)
    count: int = Field(ge=0, le=100_000)


class ToolUseEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tool: str = Field(min_length=1, max_length=64)
    count: int = Field(ge=0, le=100_000)
    ok: int | None = Field(default=None, ge=0, le=100_000)
    errors: list[ToolErrorEntry] | None = None


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event: Literal[
        "install",
        "session_start",
        "session_end",
        "session_crash",
        "setup_started",
        "setup_key_result",
        "setup_client_result",
        "setup_finished",
    ]
    install_id: str = Field(min_length=8, max_length=64)
    package: str = Field(min_length=1, max_length=64)
    package_version: str = Field(min_length=1, max_length=32)
    node_version: str | None = Field(default=None, max_length=32)
    os_platform: str | None = Field(default=None, max_length=16)
    os_arch: str | None = Field(default=None, max_length=16)
    # session_end / session_crash
    duration_s: int | None = Field(default=None, ge=0, le=60 * 60 * 24 * 30)
    tools_called: list[ToolUseEntry] | None = None
    tool_errors_total: int | None = Field(default=None, ge=0, le=10_000_000)
    # session_crash
    phase: str | None = Field(default=None, max_length=16)
    # setup funnel + crash failure category (sanitized, never a raw message)
    outcome: str | None = Field(default=None, max_length=32)
    client: str | None = Field(default=None, max_length=32)
    error_code: str | None = Field(default=None, max_length=48)
    error_class: str | None = Field(default=None, max_length=48)
    # Wide enough for Windows process exit codes (uint32, e.g. NTSTATUS).
    exit_code: int | None = Field(default=None, ge=-2_147_483_648, le=4_294_967_295)
    # setup_finished
    clients_installed: int | None = Field(default=None, ge=0, le=64)
    clients_failed: int | None = Field(default=None, ge=0, le=64)


# Optional fields are logged only when present so each event line stays lean.
_OPTIONAL_SCALARS = (
    "node_version",
    "os_platform",
    "os_arch",
    "duration_s",
    "tool_errors_total",
    "phase",
    "outcome",
    "client",
    "error_code",
    "error_class",
    "exit_code",
    "clients_installed",
    "clients_failed",
)


@router.post("/api/telemetry/event")
async def receive_event(body: TelemetryEvent) -> Response:
    payload: dict[str, object] = {
        "install_id": body.install_id,
        "package": body.package,
        "package_version": body.package_version,
    }
    for name in _OPTIONAL_SCALARS:
        value = getattr(body, name)
        if value is not None:
            payload[name] = value
    if body.tools_called is not None:
        payload["tools_called"] = [t.model_dump(exclude_none=True) for t in body.tools_called]
    log.info(body.event, **payload)
    return Response(status_code=204)
