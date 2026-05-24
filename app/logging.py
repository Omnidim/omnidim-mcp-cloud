import logging
import os
import sys
from typing import Any
from urllib.parse import urlparse

import structlog

SENSITIVE_LOG_KEYS = frozenset(
    {
        "odoo_api_key_value",
        "api_key",
        "access_token",
        "refresh_token",
        "client_secret",
        "code_verifier",
        "Authorization",
        "authorization",
        "X-Internal-Secret",
        "x-internal-secret",
    }
)


def _scrub(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: ("[redacted]" if k in SENSITIVE_LOG_KEYS else _scrub(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_scrub(v) for v in value]
    return value


def _scrub_processor(_logger: Any, _method: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    return _scrub(event_dict)  # type: ignore[no-any-return]


def _parse_labels(raw: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _build_loki_handler() -> logging.Handler | None:
    push_url = os.environ.get("LOKI_PUSH_URL", "").strip()
    if not push_url:
        return None
    try:
        import logging_loki  # type: ignore[import-untyped]
    except ImportError:
        return None

    parsed = urlparse(push_url)
    auth: tuple[str, str] | None = None
    if parsed.username:
        auth = (parsed.username, parsed.password or "")
        clean_url = push_url.replace(f"{parsed.username}:{parsed.password}@", "", 1)
    else:
        clean_url = push_url

    labels = _parse_labels(os.environ.get("LOKI_LABELS", "service=omni-mcp-cloud"))
    handler: logging.Handler = logging_loki.LokiHandler(
        url=clean_url,
        tags=labels,
        auth=auth,
        version="1",
    )
    return handler


def configure_logging(level: str = "info") -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _scrub_processor,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logs (uvicorn, gunicorn, sqlalchemy) through the same JSON pipeline.
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handlers: list[logging.Handler] = [handler]

    loki_handler = _build_loki_handler()
    if loki_handler is not None:
        loki_handler.setFormatter(formatter)
        handlers.append(loki_handler)

    root = logging.getLogger()
    root.handlers = handlers
    root.setLevel(log_level)

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "gunicorn.error",
        "gunicorn.access",
    ):
        logger = logging.getLogger(name)
        logger.handlers = handlers
        logger.propagate = False
