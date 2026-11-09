"""Application configuration loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Central settings object — all values sourced from .env or environment."""

    # A healthcare deployment often shares an environment with infrastructure
    # variables (for example CLINIC_ZIP).  Ignore unknown variables rather than
    # failing application startup because of an unrelated deployment setting.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_env: Literal['development', 'test', 'production'] = 'development'
    encrypted_storage_confirmed: bool = False
    app_secret_key: str = "dev-secret-key-change-in-production"
    app_allowed_origins: str = "http://localhost:3000"
    demo_mode: bool = False
    advanced_nlp_enabled: bool = False
    app_allowed_hosts: str = 'localhost,127.0.0.1,::1'
    outbound_webhooks_enabled: bool = False
    referral_webhook_url: str = ''
    webhook_allowed_hosts: str = ''

    # JWT
    jwt_secret_key: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8
    # WorkOS public application identifiers. No WorkOS API secret is needed to verify JWTs.
    workos_client_id: str = ""
    workos_organization_id: str = ""
    workos_issuer: str = "https://api.workos.com"
    workos_access_permission: str = "omnimatch:access"
    workos_admin_permission: str = "omnimatch:admin"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "clinical_trials"

    # ClinicalTrials.gov
    clinicaltrials_api_base: str = "https://clinicaltrials.gov/api/v2/studies"
    clinicaltrials_sync_page_size: int = 100
    clinicaltrials_max_studies: int = 1000

    # Whisper
    whisper_model: str = "base"

    # Scheduler
    sync_cron_hour: int = 2
    sync_cron_minute: int = 0

    # SQLite
    sqlite_db_path: str = "./omni_match.db"

    # NEW FEATURE 7: End-of-day digest webhook (optional — leave blank to disable)
    digest_webhook_url: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated origins string into a list."""
        return [o.strip() for o in self.app_allowed_origins.split(",")]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip().lower() for host in self.app_allowed_hosts.split(',') if host.strip()]


settings = Settings()
