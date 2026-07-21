from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    REDIS_URL: str
    RABBIT_URL: str

    DEBUG: bool
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=50)
    LOG_LEVEL: str
    MAX_RETRIES: int = 5

    CORS_ORIGINS: list[str] = ["*"]

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
@lru_cache
def get_settings() -> Settings:
    return Settings() # pyright: ignore[reportCallIssue]
