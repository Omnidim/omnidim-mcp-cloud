"""initial oauth tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-23

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "oauth_client",
        sa.Column("client_id", sa.String(64), primary_key=True),
        sa.Column("client_secret_hash", sa.Text(), nullable=True),
        sa.Column("client_name", sa.String(255), nullable=False),
        sa.Column("redirect_uris", sa.JSON(), nullable=False),
        sa.Column("grant_types", sa.JSON(), nullable=False),
        sa.Column("response_types", sa.JSON(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False, server_default=""),
        sa.Column("token_endpoint_auth_method", sa.String(32), nullable=False),
        sa.Column("software_id", sa.String(255), nullable=True),
        sa.Column("software_version", sa.String(64), nullable=True),
        sa.Column("software_statement", sa.Text(), nullable=True),
        sa.Column("registration_access_token_hash", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "oauth_authorization_code",
        sa.Column("code_hash", sa.Text(), primary_key=True),
        sa.Column("client_id", sa.String(64), sa.ForeignKey("oauth_client.client_id"), nullable=False),
        sa.Column("odoo_user_id", sa.Integer(), nullable=False),
        sa.Column("redirect_uri", sa.Text(), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("code_challenge", sa.Text(), nullable=False),
        sa.Column("code_challenge_method", sa.String(16), nullable=False),
        sa.Column("resource", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("code_challenge_method = 'S256'", name="ck_pkce_method"),
    )
    op.create_index(
        "ix_oauth_authorization_code_client_id",
        "oauth_authorization_code",
        ["client_id"],
    )
    op.create_index(
        "ix_oauth_authorization_code_odoo_user_id",
        "oauth_authorization_code",
        ["odoo_user_id"],
    )
    op.create_index(
        "ix_oauth_authorization_code_expires_at",
        "oauth_authorization_code",
        ["expires_at"],
    )

    op.create_table(
        "oauth_access_token",
        sa.Column("token_hash", sa.Text(), primary_key=True),
        sa.Column("client_id", sa.String(64), sa.ForeignKey("oauth_client.client_id"), nullable=False),
        sa.Column("odoo_user_id", sa.Integer(), nullable=False),
        sa.Column("odoo_api_key_id", sa.Integer(), nullable=False),
        sa.Column("grant_id", sa.String(64), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_oauth_access_token_client_id", "oauth_access_token", ["client_id"])
    op.create_index("ix_oauth_access_token_odoo_user_id", "oauth_access_token", ["odoo_user_id"])
    op.create_index("ix_oauth_access_token_grant_id", "oauth_access_token", ["grant_id"])
    op.create_index("ix_oauth_access_token_expires_at", "oauth_access_token", ["expires_at"])
    op.create_index(
        "ix_oauth_access_token_grant_id_revoked",
        "oauth_access_token",
        ["grant_id", "revoked_at"],
    )

    op.create_table(
        "oauth_refresh_token",
        sa.Column("token_hash", sa.Text(), primary_key=True),
        sa.Column("client_id", sa.String(64), sa.ForeignKey("oauth_client.client_id"), nullable=False),
        sa.Column("odoo_user_id", sa.Integer(), nullable=False),
        sa.Column("grant_id", sa.String(64), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replaced_by_hash", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_oauth_refresh_token_client_id", "oauth_refresh_token", ["client_id"])
    op.create_index("ix_oauth_refresh_token_odoo_user_id", "oauth_refresh_token", ["odoo_user_id"])
    op.create_index("ix_oauth_refresh_token_grant_id", "oauth_refresh_token", ["grant_id"])
    op.create_index("ix_oauth_refresh_token_expires_at", "oauth_refresh_token", ["expires_at"])
    op.create_index(
        "ix_oauth_refresh_token_grant_id_consumed",
        "oauth_refresh_token",
        ["grant_id", "consumed_at"],
    )


def downgrade() -> None:
    op.drop_table("oauth_refresh_token")
    op.drop_table("oauth_access_token")
    op.drop_table("oauth_authorization_code")
    op.drop_table("oauth_client")
