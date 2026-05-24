"""authorization_request table

Revision ID: 0002_authorization_request
Revises: 0001_initial
Create Date: 2026-05-23

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_authorization_request"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oauth_authorization_request",
        sa.Column("request_id_hash", sa.Text(), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(64),
            sa.ForeignKey("oauth_client.client_id"),
            nullable=False,
        ),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=True),
        sa.Column("code_challenge", sa.Text(), nullable=False),
        sa.Column("code_challenge_method", sa.String(16), nullable=False),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("code_challenge_method = 'S256'", name="ck_authreq_pkce_method"),
    )
    op.create_index(
        "ix_oauth_authorization_request_client_id",
        "oauth_authorization_request",
        ["client_id"],
    )
    op.create_index(
        "ix_oauth_authorization_request_expires_at",
        "oauth_authorization_request",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_table("oauth_authorization_request")
