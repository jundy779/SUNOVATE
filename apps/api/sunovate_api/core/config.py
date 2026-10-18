"""Typed application settings loaded from environment variables or `.env`.

Only development implementations exist for external providers. The `Literal`
types make it impossible to configure an unimplemented production provider.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnv = Literal["development", "test", "staging", "production"]
# Runtime data backends: in-memory SIMULATED_DATA store or PostgreSQL (ADR-015, PROPOSED).
DataBackendName = Literal["simulated", "postgres"]

# Repository-root `.env` first, then `apps/api/.env` (later files override earlier ones).
_ROOT_ENV = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_ROOT_ENV, ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "SUNOVATE API"
    app_version: str = "0.1.0"
    app_env: AppEnv = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    # Non-negotiable private-data boundary. These Literal locks deliberately make
    # unsafe environment overrides fail validation instead of silently enabling
    # public discovery or outbound processing.
    private_data_mode: Literal[True] = True
    public_indexing_enabled: Literal[False] = False
    external_ai_data_egress_enabled: Literal[False] = False
    external_agent_access_enabled: Literal[False] = False
    telemetry_data_egress_enabled: Literal[False] = False

    # Single-host API controls (ADR-019). Reverse proxy controls remain mandatory
    # for an approved deployment and must not trust arbitrary forwarded headers.
    api_max_request_bytes: int = Field(default=3_145_728, ge=65_536, le=52_428_800)
    api_body_read_timeout_seconds: int = Field(default=15, ge=1, le=60)
    api_rate_limit_window_seconds: int = Field(default=60, ge=10, le=3_600)
    api_rate_limit_max_keys: int = Field(default=10_000, ge=100, le=100_000)
    api_global_rate_limit: int = Field(default=600, ge=10, le=100_000)
    api_default_rate_limit: int = Field(default=180, ge=1, le=100_000)
    api_login_rate_limit: int = Field(default=20, ge=1, le=10_000)
    api_savi_rate_limit: int = Field(default=60, ge=1, le=10_000)
    api_search_rate_limit: int = Field(default=120, ge=1, le=10_000)
    api_ingestion_rate_limit: int = Field(default=20, ge=1, le=10_000)

    # Runtime data backend. `postgres` uses DATABASE_URL (validated by db/urls.py at startup).
    data_backend: DataBackendName = "simulated"
    database_url: str = "postgresql+asyncpg://sunovate:sunovate_local@localhost:5432/sunovate"

    dev_auth_enabled: bool = True
    # Empty secret => an ephemeral random secret is generated per process.
    dev_auth_secret: str = ""
    dev_auth_token_ttl_minutes: int = Field(default=480, ge=5, le=1440)
    cors_origins: str = "http://localhost:3000"

    document_provider: Literal["local"] = "local"
    local_storage_path: str = "./infrastructure/local/documents"
    identity_provider: Literal["development"] = "development"
    notification_provider: Literal["disabled"] = "disabled"
    ai_provider: Literal["development_extractive", "disabled"] = "development_extractive"
    embedding_provider: Literal["disabled"] = "disabled"
    hermes_mode: Literal["development", "disabled"] = "development"
    hermes_max_classification: Literal["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"] = (
        "RESTRICTED"
    )

    deadline_due_soon_days: int = Field(default=7, ge=1, le=60)

    @model_validator(mode="after")
    def _secure_defaults(self) -> Settings:
        if self.app_env == "production":
            if self.dev_auth_enabled:
                raise ValueError("DEV_AUTH_ENABLED must be false when APP_ENV=production")
            if self.data_backend == "simulated":
                raise ValueError("DATA_BACKEND=simulated is not allowed when APP_ENV=production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
