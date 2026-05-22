from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

GrantType = Literal["authorization_code", "refresh_token"]
ResponseType = Literal["code"]
TokenAuthMethod = Literal["none", "client_secret_basic", "client_secret_post"]


def _is_allowed_redirect(uri: str) -> bool:
    parsed = urlparse(uri)
    if parsed.fragment:
        return False
    if parsed.username or parsed.password:
        return False
    if not parsed.hostname:
        return False
    if parsed.scheme == "https":
        return True
    if parsed.scheme == "http":
        return parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    return False


class ClientRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    redirect_uris: Annotated[list[str], Field(min_length=1)]
    client_name: str | None = None
    grant_types: list[GrantType] = ["authorization_code", "refresh_token"]
    response_types: Annotated[list[ResponseType], Field(min_length=1)] = ["code"]
    token_endpoint_auth_method: TokenAuthMethod = "none"
    scope: str | None = None
    software_id: str | None = None
    software_version: str | None = None
    software_statement: str | None = None

    @field_validator("redirect_uris")
    @classmethod
    def _validate_redirect_uris(cls, value: list[str]) -> list[str]:
        for uri in value:
            if not _is_allowed_redirect(uri):
                raise ValueError(f"redirect_uri must use https or be loopback http: {uri}")
        return value

    @field_validator("software_statement")
    @classmethod
    def _reject_software_statement(cls, value: str | None) -> str | None:
        # Per RFC 7591 §3.1.1 we MUST validate the JWT signature against a
        # trusted issuer before accepting. Until trusted-issuer config exists
        # we reject the field outright rather than silently persisting an
        # unverified blob.
        if value is not None:
            raise ValueError("software_statement is not currently accepted by this server")
        return value

    @model_validator(mode="after")
    def _check_grant_response_consistency(self) -> "ClientRegistrationRequest":
        gt = set(self.grant_types)
        rt = set(self.response_types)
        if "authorization_code" in gt and "code" not in rt:
            raise ValueError(
                "response_types must include 'code' when grant_types includes 'authorization_code'"
            )
        if "code" in rt and "authorization_code" not in gt:
            raise ValueError(
                "grant_types must include 'authorization_code' when response_types includes 'code'"
            )
        if "refresh_token" in gt and "authorization_code" not in gt:
            raise ValueError("refresh_token grant requires authorization_code grant")
        return self


class ClientRegistrationResponse(BaseModel):
    client_id: str
    client_id_issued_at: int
    redirect_uris: list[str]
    grant_types: list[str]
    response_types: list[str]
    token_endpoint_auth_method: str
    client_name: str
    scope: str | None = None
    software_id: str | None = None
    software_version: str | None = None
    client_secret: str | None = None
    # RFC 7591 §3.2.1: when client_secret is issued, this field is REQUIRED
    # and a value of `0` means the secret does not expire. Absent when no
    # secret is issued (public clients).
    client_secret_expires_at: int | None = None
