from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "staging", "production"] = "development"
    log_level: Literal["debug", "info", "warning", "error"] = "info"

    database_url: str
    # workers * (pool_size + max_overflow) must stay under Postgres max_connections.
    # Defaults assume 4 workers * 10 conns/worker = 40 per replica.
    database_pool_size: int = 5
    database_max_overflow: int = 5

    public_base_url: str = Field(description="Public origin clients use to reach this service.")
    dashboard_base_url: str = Field(description="Origin where the consent screen is hosted.")
    odoo_internal_base_url: str
    odoo_internal_shared_secret: str

    token_signing_key: str = Field(min_length=32)
    access_token_ttl_seconds: int = 3600
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 90

    loki_push_url: str = ""
    loki_labels: str = "service=omni-mcp-server"


@lru_cache
def get_settings() -> Settings:
    # Required fields come from the environment; pydantic-settings reads them at instantiation.
    return Settings.model_validate({})
