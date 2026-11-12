"""Typed application settings loaded from environment variables or `.env`.

Only development implementations exist for external providers. The `Literal`
types make it impossible to configure an unimplemented production provider.
"""

from __future__ import annotations

from functools import lru_cache
from ipaddress import IPv4Network, IPv6Network, ip_network
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .. import __version__

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
    app_version: str = __version__  # single source: sunovate_api/__init__.py
    app_env: AppEnv = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    # Non-negotiable private-data boundary. These Literal locks deliberately make
    # unsafe environment overrides fail validation instead of silently enabling
    # public discovery or outbound processing.
    # These are typed as bool so pydantic-settings can parse the string values
    # used by .env files and operating-system environments. The model validator
    # below still makes the secure values immutable at runtime.
    private_data_mode: bool = True
    public_indexing_enabled: bool = False
    external_ai_data_egress_enabled: bool = False
    external_agent_access_enabled: bool = False
    telemetry_data_egress_enabled: bool = False

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
    # Empty by default: forwarded client addresses are ignored unless the direct
    # peer belongs to one of these explicitly reviewed proxy networks.
    api_trusted_proxy_cidrs: str = ""

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
    hermes_mode: Literal["development", "hermes_agent", "disabled"] = "development"
    # Hermes Agent API server (only when HERMES_MODE=hermes_agent); loopback or private network.
    hermes_agent_base_url: str = "http://127.0.0.1:8642/v1"
    hermes_agent_api_key: str = ""
    hermes_agent_model: str = "hermes-agent"
    hermes_agent_timeout_seconds: float = Field(default=60.0, gt=0, le=300)
    # CONFIDENTIAL is never processed by Hermes, so it is not an accepted ceiling (BR-22, NFR-10).
    hermes_max_classification: Literal["PUBLIC", "INTERNAL", "RESTRICTED"] = "RESTRICTED"

    deadline_due_soon_days: int = Field(default=7, ge=1, le=60)

    @model_validator(mode="after")
    def _secure_defaults(self) -> Settings:
        if not self.private_data_mode:
            raise ValueError("PRIVATE_DATA_MODE must remain true")
        disabled_security_locks = {
            "PUBLIC_INDEXING_ENABLED": self.public_indexing_enabled,
            "EXTERNAL_AI_DATA_EGRESS_ENABLED": self.external_ai_data_egress_enabled,
            "EXTERNAL_AGENT_ACCESS_ENABLED": self.external_agent_access_enabled,
            "TELEMETRY_DATA_EGRESS_ENABLED": self.telemetry_data_egress_enabled,
        }
        unsafe_locks = [name for name, enabled in disabled_security_locks.items() if enabled]
        if unsafe_locks:
            raise ValueError(f"Security locks must remain false: {', '.join(unsafe_locks)}")
        if self.dev_auth_enabled and self.app_env not in ("development", "test"):
            # Password-less login is for local development and tests only, never staging or UAT.
            raise ValueError("DEV_AUTH_ENABLED must be false unless APP_ENV is development or test")
        if self.hermes_mode == "hermes_agent":
            from ..providers.hermes_agent import is_internal_endpoint  # noqa: PLC0415 - avoid cycle

            if not is_internal_endpoint(self.hermes_agent_base_url):
                raise ValueError("HERMES_AGENT_BASE_URL must be a loopback or private address")
            if len(self.hermes_agent_api_key) < 16:
                raise ValueError("HERMES_AGENT_API_KEY must be set (at least 16 characters)")
        if self.dev_auth_secret and len(self.dev_auth_secret) < 32:
            # A short secret makes HMAC tokens guessable (AUD-17); empty means ephemeral random.
            raise ValueError("DEV_AUTH_SECRET must be empty or at least 32 characters")
        if self.app_env == "production" and self.data_backend == "simulated":
            raise ValueError("DATA_BACKEND=simulated is not allowed when APP_ENV=production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def api_trusted_proxy_networks(self) -> tuple[IPv4Network | IPv6Network, ...]:
        networks: list[IPv4Network | IPv6Network] = []
        for raw_network in self.api_trusted_proxy_cidrs.split(","):
            candidate = raw_network.strip()
            if not candidate:
                continue
            try:
                networks.append(ip_network(candidate, strict=True))
            except ValueError as exc:
                raise ValueError(
                    "API_TRUSTED_PROXY_CIDRS must contain canonical IPv4/IPv6 CIDRs"
                ) from exc
        return tuple(networks)


@lru_cache
def get_settings() -> Settings:
    return Settings()
