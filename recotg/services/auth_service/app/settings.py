from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "recotg_db"
    POSTGRES_USER: str = "recotg"
    POSTGRES_PASS: str = "recopassword"
    
    @property
    def DATABASE_URL(self) -> str:
        pwd = quote_plus(self.POSTGRES_PASS)
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{pwd}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_USER}"
        )
        
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
settings = Settings()