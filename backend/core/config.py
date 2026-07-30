"""Centralized application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Security
    secret_key: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./assets.db"

    # CORS
    cors_origins: str = "http://localhost:5173"

    # AI Audit
    use_mock_mode: bool = True
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
