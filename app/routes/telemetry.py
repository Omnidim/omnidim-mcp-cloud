from __future__ import annotations

from typing import Literal

import structlog
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(tags=["telemetry"])
log = structlog.get_logger()


class ToolUseEntry(BaseModel):
    tool: str = Field(min_length=1, max_length=64)
    count: int = Field(ge=0, le=100_000)


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event: Literal["install", "session_start", "session_end"]
    install_id: str = Field(min_length=8, max_length=64)
    package: str = Field(min_length=1, max_length=64)
    package_version: str = Field(min_length=1, max_length=32)
    node_version: str | None = Field(default=None, max_length=32)
    os_platform: str | None = Field(default=None, max_length=16)
    os_arch: str | None = Field(default=None, max_length=16)
    duration_s: int | None = Field(default=None, ge=0, le=60 * 60 * 24 * 30)
    tools_called: list[ToolUseEntry] | None = None


@router.post("/api/telemetry/event")
async def receive_event(body: TelemetryEvent) -> Response:
    payload: dict[str, object] = {
        "install_id": body.install_id,
        "package": body.package,
        "package_version": body.package_version,
        "node_version": body.node_version,
        "os_platform": body.os_platform,
        "os_arch": body.os_arch,
    }
    if body.duration_s is not None:
        payload["duration_s"] = body.duration_s
    if body.tools_called is not None:
        payload["tools_called"] = [t.model_dump() for t in body.tools_called]
    log.info(body.event, **payload)
    return Response(status_code=204)
