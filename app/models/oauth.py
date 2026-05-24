from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class OAuthClient(Base, TimestampMixin):
    __tablename__ = "oauth_client"

    client_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_secret_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    redirect_uris: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    grant_types: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    response_types: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False, default="")
    token_endpoint_auth_method: Mapped[str] = mapped_column(String(32), nullable=False)
    software_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    software_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    software_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    registration_access_token_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class AuthorizationCode(Base, TimestampMixin):
    __tablename__ = "oauth_authorization_code"
    __table_args__ = (
        CheckConstraint("code_challenge_method = 'S256'", name="ck_pkce_method"),
    )

    code_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("oauth_client.client_id"), nullable=False, index=True
    )
    odoo_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    odoo_api_key_id: Mapped[int] = mapped_column(Integer, nullable=False)
    odoo_api_key_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    redirect_uri: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    code_challenge: Mapped[str] = mapped_column(Text, nullable=False)
    code_challenge_method: Mapped[str] = mapped_column(String(16), nullable=False)
    resource: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuthorizationRequest(Base, TimestampMixin):
    __tablename__ = "oauth_authorization_request"
    __table_args__ = (
        CheckConstraint("code_challenge_method = 'S256'", name="ck_authreq_pkce_method"),
    )

    request_id_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("oauth_client.client_id"), nullable=False, index=True
    )
    redirect_uri: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_challenge: Mapped[str] = mapped_column(Text, nullable=False)
    code_challenge_method: Mapped[str] = mapped_column(String(16), nullable=False)
    resource: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccessToken(Base, TimestampMixin):
    __tablename__ = "oauth_access_token"

    token_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("oauth_client.client_id"), nullable=False, index=True
    )
    odoo_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    odoo_api_key_id: Mapped[int] = mapped_column(Integer, nullable=False)
    odoo_api_key_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    grant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "oauth_refresh_token"

    token_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    client_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("oauth_client.client_id"), nullable=False, index=True
    )
    odoo_user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    grant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_hash: Mapped[str | None] = mapped_column(Text, nullable=True)


Index("ix_oauth_access_token_grant_id_revoked", AccessToken.grant_id, AccessToken.revoked_at)
Index(
    "ix_oauth_refresh_token_grant_id_consumed", RefreshToken.grant_id, RefreshToken.consumed_at
)
