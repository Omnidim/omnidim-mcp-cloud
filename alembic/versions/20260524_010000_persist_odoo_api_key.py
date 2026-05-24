"""persist plaintext odoo api_key for proxying

Revision ID: 0004_persist_odoo_api_key
Revises: 0003_auth_code_api_key_id
Create Date: 2026-05-24

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


def downgrade() -> None:
    op.drop_column("oauth_access_token", "odoo_api_key_value")
    op.drop_column("oauth_authorization_code", "odoo_api_key_value")
