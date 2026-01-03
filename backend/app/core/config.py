from functools import lru_cache
from pathlib import Path

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # points to backend/
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
