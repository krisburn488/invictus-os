from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from invictus_os.schemas.settings import (
    AppSettingsResponse,
    AppSettingsUpdateRequest,
    BrandSettings,
    BusinessProfileSettings,
    ProviderSettingsStatus,
    SensitiveCredentialStatus,
)


@dataclass(frozen=True)
class OpenAIServiceConfig:
    api_key: str
    model: str
    temperature: float
    max_output_tokens: int


class SettingsServiceError(Exception):
    message = "InvictusOS could not save settings."


class SettingsStorageError(SettingsServiceError):
    message = "InvictusOS could not read or write local settings."


class LocalSettingsRepository:
    def __init__(self, storage_path: Path | None = None) -> None:
        self._storage_path = storage_path or Path(".local/app_settings.json")

    def load(self) -> dict[str, Any]:
        if not self._storage_path.exists():
            return default_settings_payload()

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise SettingsStorageError
            return merge_settings(default_settings_payload(), payload)
        except (OSError, json.JSONDecodeError) as exc:
            raise SettingsStorageError from exc

    def save(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._storage_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return payload
        except OSError as exc:
            raise SettingsStorageError from exc


class SettingsService:
    def __init__(self, repository: LocalSettingsRepository | None = None) -> None:
        self._repository = repository or LocalSettingsRepository()

    def get_settings(self) -> AppSettingsResponse:
        return build_response(self._repository.load())

    def get_openai_config(self) -> OpenAIServiceConfig:
        payload = self._repository.load()
        openai = payload["openai"]
        return OpenAIServiceConfig(
            api_key=payload["credentials"]["openai_api_key"],
            model=openai["model"],
            temperature=openai["temperature"],
            max_output_tokens=openai["max_output_tokens"],
        )

    def update_settings(self, request: AppSettingsUpdateRequest) -> AppSettingsResponse:
        current = self._repository.load()
        updated = {
            "credentials": {
                "openai_api_key": choose_secret(
                    request.openai.api_key,
                    current["credentials"]["openai_api_key"],
                ),
                "meta_app_id": choose_secret(request.meta.app_id, current["credentials"]["meta_app_id"]),
                "meta_app_secret": choose_secret(
                    request.meta.app_secret,
                    current["credentials"]["meta_app_secret"],
                ),
                "meta_access_token": choose_secret(
                    request.meta.access_token,
                    current["credentials"]["meta_access_token"],
                ),
                "higgsfield_api_key": choose_secret(
                    request.higgsfield.api_key,
                    current["credentials"]["higgsfield_api_key"],
                ),
            },
            "openai": {
                "model": request.openai.model,
                "temperature": request.openai.temperature,
                "max_output_tokens": request.openai.max_output_tokens,
            },
            "brand": json.loads(request.brand.model_dump_json()),
            "business_profile": json.loads(request.business_profile.model_dump_json()),
        }

        try:
            BrandSettings.model_validate(updated["brand"])
            BusinessProfileSettings.model_validate(updated["business_profile"])
        except ValidationError as exc:
            raise SettingsServiceError from exc

        return build_response(self._repository.save(updated))


def default_settings_payload() -> dict[str, Any]:
    return {
        "credentials": {
            "openai_api_key": "",
            "meta_app_id": "",
            "meta_app_secret": "",
            "meta_access_token": "",
            "higgsfield_api_key": "",
        },
        "openai": {
            "model": "gpt-5.5",
            "temperature": 0.7,
            "max_output_tokens": 1800,
        },
        "brand": json.loads(BrandSettings().model_dump_json()),
        "business_profile": json.loads(BusinessProfileSettings().model_dump_json()),
    }


def merge_settings(defaults: dict[str, Any], stored: dict[str, Any]) -> dict[str, Any]:
    merged = defaults.copy()
    for key, default_value in defaults.items():
        stored_value = stored.get(key)
        if isinstance(default_value, dict) and isinstance(stored_value, dict):
            merged[key] = {**default_value, **stored_value}
        elif stored_value is not None:
            merged[key] = stored_value
    return merged


def choose_secret(new_value: str | None, current_value: str) -> str:
    return new_value if new_value is not None else current_value


def build_response(payload: dict[str, Any]) -> AppSettingsResponse:
    credentials = payload["credentials"]
    return AppSettingsResponse(
        providers=ProviderSettingsStatus(
            openai_api_key=credential_status(credentials["openai_api_key"]),
            openai_model=payload["openai"]["model"],
            openai_temperature=payload["openai"]["temperature"],
            openai_max_output_tokens=payload["openai"]["max_output_tokens"],
            meta_app_id=credential_status(credentials["meta_app_id"]),
            meta_app_secret=credential_status(credentials["meta_app_secret"]),
            meta_access_token=credential_status(credentials["meta_access_token"]),
            higgsfield_api_key=credential_status(credentials["higgsfield_api_key"]),
        ),
        brand=BrandSettings.model_validate(payload["brand"]),
        business_profile=BusinessProfileSettings.model_validate(payload["business_profile"]),
    )


def credential_status(value: str) -> SensitiveCredentialStatus:
    return SensitiveCredentialStatus(
        configured=bool(value),
        masked_value=mask_secret(value) if value else None,
    )


def mask_secret(value: str) -> str:
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}****{value[-4:]}"
