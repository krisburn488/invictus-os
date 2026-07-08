from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    application_name: str = "InvictusOS"
    application_version: str = "0.1.0"
    environment: str = "local"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    cors_origin_regex: str | None = r"https://.*\.vercel\.app"
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "INVICTUS_OPENAI_API_KEY"),
    )
    openai_model: str = "gpt-5.5"
    openai_timeout_seconds: float = 30.0
    higgsfield_mcp_bridge_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("HIGGSFIELD_MCP_BRIDGE_URL", "INVICTUS_HIGGSFIELD_MCP_BRIDGE_URL"),
    )
    higgsfield_timeout_seconds: float = 120.0
    vercel: str | None = Field(default=None, validation_alias=AliasChoices("VERCEL"))
    storage_dir: Path | None = Field(
        default=None,
        validation_alias=AliasChoices("INVICTUS_STORAGE_DIR", "INVICTUS_DATA_DIR"),
    )

    model_config = SettingsConfigDict(env_prefix="INVICTUS_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_runtime_storage_dir() -> Path:
    settings = get_settings()
    if settings.storage_dir:
        return settings.storage_dir
    if settings.vercel:
        return Path("/tmp/invictus-os")
    return Path(".local")
