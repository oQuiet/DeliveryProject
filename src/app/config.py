from functools import lru_cache
from pathlib import Path

from pydantic import AmqpDsn, Field, MongoDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, case_sensitive=False)

    POSTGRES_HOST: str  # type: ignore[call-arg]
    POSTGRES_PORT: str  # type: ignore[call-arg]
    POSTGRES_USER: str  # type: ignore[call-arg]
    POSTGRES_PASSWORD: str  # type: ignore[call-arg]
    POSTGRES_DB: str  # type: ignore[call-arg]

    REDIS_URL: RedisDsn  # type: ignore[call-arg]
    MONGO_URL: MongoDsn  # type: ignore[call-arg]
    MONGO_DB_NAME: str  # type: ignore[call-arg]
    RABBIT_URL: AmqpDsn  # type: ignore[call-arg]
    CURRENCY_URL: str  # type: ignore[call-arg]

    DEBUG: bool  # type: ignore[call-arg]
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 5

    CORS_ORIGINS: list[str] = ["*"]

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
