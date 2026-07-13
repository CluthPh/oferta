from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import PRICE_CHANGE_MODES


class Settings(BaseSettings):
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    database_url: str = Field(default="sqlite:///data/offers.db", alias="DATABASE_URL")
    admin_api_key: str = Field(default="", alias="ADMIN_API_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    app_env: str = Field(default="development", alias="APP_ENV")
    headless: bool = Field(default=True, alias="HEADLESS")
    dry_run: bool = Field(default=True, alias="DRY_RUN")
    post_without_affiliate_link: bool = Field(
        default=False,
        alias="POST_WITHOUT_AFFILIATE_LINK",
    )
    mercadolivre_access_token: str = Field(default="", alias="MERCADOLIVRE_ACCESS_TOKEN")
    mercadolivre_site_id: str = Field(default="MLB", alias="MERCADOLIVRE_SITE_ID")
    niches_config_path: Path = Field(default=Path("data/niches.yml"), alias="NICHES_CONFIG_PATH")
    repost_after_hours: int = Field(default=168, alias="REPOST_AFTER_HOURS")
    min_price_drop_percent: float = Field(default=3.0, alias="MIN_PRICE_DROP_PERCENT")
    price_change_mode: str = Field(default="repost", alias="PRICE_CHANGE_MODE")
    http_timeout_seconds: float = Field(default=20.0, alias="HTTP_TIMEOUT_SECONDS")
    max_image_bytes: int = Field(default=8_000_000, alias="MAX_IMAGE_BYTES")
    scan_interval_minutes: int = Field(default=60, alias="SCAN_INTERVAL_MINUTES")
    run_scan_on_startup: bool = Field(default=True, alias="RUN_SCAN_ON_STARTUP")
    require_approval: bool = Field(default=False, alias="REQUIRE_APPROVAL")
    marketplace_sources: str = Field(default="mercadolivre", alias="MARKETPLACE_SOURCES")
    data_dir: Path = Path("data")
    logs_dir: Path = Path("logs")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("price_change_mode")
    @classmethod
    def validate_price_change_mode(cls, value: str) -> str:
        if value not in PRICE_CHANGE_MODES:
            allowed = ", ".join(sorted(PRICE_CHANGE_MODES))
            msg = f"PRICE_CHANGE_MODE invalido: {value}. Use um destes: {allowed}"
            raise ValueError(msg)
        return value

    @field_validator("mercadolivre_site_id")
    @classmethod
    def normalize_site_id(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("scan_interval_minutes")
    @classmethod
    def validate_scan_interval(cls, value: int) -> int:
        if value < 1:
            raise ValueError("SCAN_INTERVAL_MINUTES deve ser maior ou igual a 1")
        return value


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    return settings
