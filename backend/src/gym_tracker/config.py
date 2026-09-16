"""Application settings loaded from environment variables (prefix ``GYM_``) or ``.env``."""

from __future__ import annotations

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GYM_", env_file=(".env", "../.env"), extra="ignore")

    database_url: str = "postgresql+psycopg://gym:change-me@localhost:5432/gym_tracker"
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60 * 24 * 7
    cookie_secure: bool = True
    cors_origins: list[str] = ["http://localhost:5173"]
    rate_limit_enabled: bool = True
    # ``memory://`` suits a single instance; use ``redis://host:6379`` when running several.
    rate_limit_storage: str = "memory://"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # required values come from the environment
