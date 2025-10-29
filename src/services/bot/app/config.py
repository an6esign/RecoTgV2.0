from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., description="Token from BotFather")
    AUTH_SERVICE_URL: str = Field(..., description="URL of auth service for user registration")
    
    model_config = SettingsConfigDict(
        extra = "ignore",
        #env_file_encoding = "utf-8",
        #env_file="src/services/bot/.env",
    )

settings = Settings()