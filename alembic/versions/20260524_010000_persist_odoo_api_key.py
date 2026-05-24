"""persist plaintext odoo api_key for proxying

Revision ID: 0004_persist_odoo_api_key
Revises: 0003_auth_code_api_key_id
Create Date: 2026-05-24

Stores the plaintext upstream credential (Odoo user.api.key value) on
oauth_authorization_code and oauth_access_token so the MCP transport
can attach it to backend proxy calls without an extra round-trip.

This is NOT a violation of the hash-only token rule: that rule applies
to secrets we ISSUE to clients (auth codes, access tokens, refresh
tokens, client secrets). The Odoo api_key is an upstream credential we
INHERIT from Odoo and use as a client of backend.omnidim.io.
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_persist_odoo_api_key"
down_revision: str | Sequence[str] | None = "0003_auth_code_api_key_id"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "oauth_authorization_code",
        sa.Column("odoo_api_key_value", sa.Text(), nullable=True),
    )
    op.add_column(
        "oauth_access_token",
        sa.Column("odoo_api_key_value", sa.Text(), nullable=True),
    )
    # Existing rows can't be backfilled. Tokens issued before this migration
    # will fail at dispatch time with a clean "missing upstream credential"
    # error rather than a crash. Acceptable: token TTL is 1 hour, the
    # window of stale tokens closes quickly. Nullable for the same reason.


def downgrade() -> None:
    op.drop_column("oauth_access_token", "odoo_api_key_value")
    op.drop_column("oauth_authorization_code", "odoo_api_key_value")
