from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., description="Token from BotFather")
    AUTH_SERVICE_URL: str = Field(..., description="Base URL of auth service")

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",            # можешь поменять путь если нужно
        env_file_encoding="utf-8",
    )

settings = Settings()
