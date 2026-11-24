from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_grant_browser_id"
down_revision: str | Sequence[str] | None = "0004_persist_odoo_api_key"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "oauth_authorization_code",
        sa.Column("browser_id_hash", sa.Text(), nullable=True),
    )
    op.add_column(
        "oauth_access_token",
        sa.Column("browser_id_hash", sa.Text(), nullable=True),
    )
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_oauth_access_token_browser_id_hash",
            "oauth_access_token",
            ["browser_id_hash"],
            postgresql_where=sa.text("browser_id_hash IS NOT NULL"),
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_oauth_access_token_browser_id_hash",
            table_name="oauth_access_token",
            postgresql_concurrently=True,
        )
    op.drop_column("oauth_access_token", "browser_id_hash")
    op.drop_column("oauth_authorization_code", "browser_id_hash")
