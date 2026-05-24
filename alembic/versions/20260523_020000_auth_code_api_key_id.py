"""auth code carries odoo_api_key_id

Revision ID: 0003_auth_code_api_key_id
Revises: 0002_authorization_request
Create Date: 2026-05-23

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_auth_code_api_key_id"
down_revision: str | Sequence[str] | None = "0002_authorization_request"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Existing rows can't be filled in retroactively; the column is nullable
    # only for the migration window and then set NOT NULL once the new
    # /internal/issue-code path is the only writer. The table is small and
    # short-lived (auth codes expire in minutes), so this is safe.
    op.add_column(
        "oauth_authorization_code",
        sa.Column("odoo_api_key_id", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE oauth_authorization_code SET odoo_api_key_id = 0 WHERE odoo_api_key_id IS NULL")
    op.alter_column("oauth_authorization_code", "odoo_api_key_id", nullable=False)


def downgrade() -> None:
    op.drop_column("oauth_authorization_code", "odoo_api_key_id")
