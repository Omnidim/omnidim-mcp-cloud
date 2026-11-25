"""OAuth scope catalogue.

Single coarse scope for v1. The consent screen treats the grant as binary:
the user is either letting the third-party app act on their OmniDimension
account, or they're not. Per-tool gating happens at the MCP transport
later if we need it; nothing in the OAuth flow itself depends on it.
"""
from typing import Final

DEFAULT_SCOPE: Final[str] = "omnidim:all"
SUPPORTED_SCOPES: Final[tuple[str, ...]] = (DEFAULT_SCOPE,)
# Read-only tools only. Issued to operator sessions via /internal/issue-token;
# not offered in the OAuth flow.
READ_SCOPE: Final[str] = "omnidim:read"


def parse_scope(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [s for s in raw.split() if s]


def unknown_scopes(requested: list[str]) -> list[str]:
    return [s for s in requested if s not in SUPPORTED_SCOPES]


def can_write(scope: str) -> bool:
    """Fail closed: only a token holding omnidim:all may call non-read tools."""
    return DEFAULT_SCOPE in parse_scope(scope)
