from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    DB_HOST: str  # type: ignore[call-arg]
    DB_PORT: int  # type: ignore[call-arg]
    DB_USER: str  # type: ignore[call-arg]
    DB_PASS: str  # type: ignore[call-arg]
    DB_NAME: str  # type: ignore[call-arg]
    REDIS_URL: str  # type: ignore[call-arg]
    RABBIT_URL: str  # type: ignore[call-arg]

    DEBUG: bool  # type: ignore[call-arg]
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    LOG_LEVEL: str  # type: ignore[call-arg]
    MAX_RETRIES: int = 5
    CURRENCY_URL: str  # type: ignore[call-arg]

    CORS_ORIGINS: list[str] = ["*"]

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
