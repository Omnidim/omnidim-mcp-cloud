from collections.abc import Sequence

from alembic import op

revision: str = "0006_grant_browser_id_index"
down_revision: str | Sequence[str] | None = "0005_grant_browser_id"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEX = "ix_oauth_access_token_browser_id_hash"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {INDEX}")
        op.execute(
            f"CREATE INDEX CONCURRENTLY {INDEX} ON oauth_access_token (browser_id_hash) "
            "WHERE browser_id_hash IS NOT NULL"
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {INDEX}")
