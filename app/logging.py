import logging
import sys
from typing import Any

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
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logs (uvicorn, gunicorn, sqlalchemy) through the same JSON pipeline.
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(log_level)

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "gunicorn.error",
        "gunicorn.access",
    ):
        logger = logging.getLogger(name)
        logger.handlers = [handler]
        logger.propagate = False
