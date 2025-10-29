from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    
    jwt_access_secret: str = Field(..., alias="JWT_ACCESS_SECRET")
    jwt_refresh_secret: str = Field(..., alias="JWT_REFRESH_SECRET")

    access_ttl_minutes: int = Field(..., alias="ACCESS_TTL_MINUTES")
    refresh_ttl_days: int = Field(..., alias="REFRESH_TTL_DAYS")
    
    @property
    def DATABASE_URL(self) -> str:
        pwd = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{pwd}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
        
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("+psycopg2", "+asyncpg")
        
    model_config = SettingsConfigDict(
        extra = "ignore",
        env_file="src/services/auth/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
settings = Settings()