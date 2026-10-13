"""Application configuration loaded from environment variables via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object — all values sourced from .env or environment."""

    # A healthcare deployment often shares an environment with infrastructure
    # variables (for example CLINIC_ZIP).  Ignore unknown variables rather than
    # failing application startup because of an unrelated deployment setting.
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_env: str = "development"
    app_secret_key: str = "dev-secret-key-change-in-production"
    app_allowed_origins: str = "http://localhost:3000"

    # JWT
    jwt_secret_key: str = "dev-jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8

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


settings = Settings()
