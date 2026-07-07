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
    canva_access_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CANVA_ACCESS_TOKEN", "INVICTUS_CANVA_ACCESS_TOKEN"),
    )
    canva_brand_template_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "CANVA_BRAND_TEMPLATE_ID",
            "INVICTUS_CANVA_BRAND_TEMPLATE_ID",
        ),
    )
    canva_api_base_url: str = "https://api.canva.com/rest/v1"
    canva_timeout_seconds: float = 30.0
    canva_poll_attempts: int = 5
    canva_poll_interval_seconds: float = 1.0
    canva_headline_field: str = "HEADLINE"
    canva_body_field: str = "BODY_TEXT"
    canva_cta_field: str = "CALL_TO_ACTION"
    canva_graphic_type_field: str = "GRAPHIC_TYPE"

    model_config = SettingsConfigDict(env_prefix="INVICTUS_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
