from __future__ import annotations

from typing import Any

import structlog

from app.procedures import GUIDE_NAMES, guide_text
from app.services.bearer import ResolvedToken
from app.services.dispatcher import DispatchError, ToolResult

log = structlog.get_logger()


def read_guide(arguments: dict[str, Any], token: ResolvedToken) -> ToolResult:
    name = arguments.get("name")
    text = guide_text(name) if isinstance(name, str) else None
    log.info(
        "tool_result",
        tool="readGuide",
        guide=name if text is not None else None,
        outcome="ok" if text is not None else "bad_arguments",
        status=None,
        duration_ms=0,
        client_id=token.client_id,
        client_name=token.client_name,
        odoo_user_id=token.odoo_user_id,
    )
    if text is None:
        raise DispatchError(-32602, f"readGuide needs a name from: {', '.join(GUIDE_NAMES)}")
    return ToolResult(text=text)
