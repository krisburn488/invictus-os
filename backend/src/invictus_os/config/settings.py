from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    application_name: str = "InvictusOS"
    application_version: str = "0.1.0"
    environment: str = "local"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "INVICTUS_OPENAI_API_KEY"),
    )
    openai_model: str = "gpt-5.5"
    openai_timeout_seconds: float = 30.0

    model_config = SettingsConfigDict(env_prefix="INVICTUS_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
