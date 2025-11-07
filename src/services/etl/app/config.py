from __future__ import annotations
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field,AliasChoices


class Settings(BaseSettings):
    DATABASE_URL: str = Field(validation_alias=AliasChoices("DATABASE_URL"))

    # читаем из TG_API_ID ИЛИ API_ID
    TG_API_ID: int  = Field(validation_alias=AliasChoices("TG_API_ID", "API_ID"))
    TG_API_HASH: str = Field(validation_alias=AliasChoices("TG_API_HASH", "API_HASH"))

    TG_SESSION: str = Field(validation_alias=AliasChoices("TG_SESSION", "TG_SESSION_PATH"))

    BACKFILL_LIMIT: int = 300
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        assert self.POSTGRES_DB and self.POSTGRES_USER and self.POSTGRES_PASSWORD, \
            "Either DATABASE_URL or POSTGRES_* must be provided."
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def tg_session_path(self) -> str:
        return f"{self.TG_SESSION_DIR}/{self.TG_SESSION_NAME}"


settings = Settings()

# совместимость, если где-то ждут settings.DATABASE_URL
if not settings.DATABASE_URL:
    object.__setattr__(settings, "DATABASE_URL", settings.database_url)
