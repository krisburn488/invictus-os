import json

import pytest

from invictus_os.schemas.settings import AppSettingsUpdateRequest, BrandSettings, BusinessProfileSettings
from invictus_os.config.settings import get_runtime_storage_dir
from invictus_os.config.settings import get_settings as get_runtime_settings
from invictus_os.services.settings_service import LocalSettingsRepository, SettingsService


def build_service(tmp_path) -> SettingsService:
    return SettingsService(repository=LocalSettingsRepository(tmp_path / "app_settings.json"))


def build_request(**overrides) -> AppSettingsUpdateRequest:
    payload = {
        "openai": {"api_key": "sk-test-openai-key"},
        "meta": {
            "app_id": "meta-app-id",
            "app_secret": "meta-app-secret",
            "access_token": "meta-access-token",
        },
        "higgsfield": {"api_key": "higgsfield-key"},
        "brand": BrandSettings(
            logo="https://example.com/logo.png",
            primary_color="#2f6f73",
            secondary_color="#247a52",
            accent_color="#d89a21",
            heading_font="Inter",
            body_font="Inter",
        ),
        "business_profile": BusinessProfileSettings(
            business_name="Invictus Wellness",
            website="https://example.com",
            booking_url="https://example.com/book",
            office_phone="555-0100",
            office_address="100 Wellness Way",
            insurance_list=["Aetna", "Blue Cross"],
            default_cta="Schedule your consultation.",
            posting_schedule=["Monday 9:00 AM", "Wednesday 1:00 PM"],
        ),
    }
    payload.update(overrides)
    return AppSettingsUpdateRequest.model_validate(payload)


def test_settings_service_saves_profile_and_masks_credentials(tmp_path) -> None:
    service = build_service(tmp_path)

    settings = service.update_settings(build_request())

    assert settings.business_profile.business_name == "Invictus Wellness"
    assert settings.business_profile.insurance_list == ["Aetna", "Blue Cross"]
    assert settings.providers.openai_api_key.configured is True
    assert settings.providers.openai_api_key.masked_value == "sk-t****-key"
    assert settings.providers.meta_app_secret.configured is True
    assert settings.providers.higgsfield_api_key.masked_value == "higg****-key"


def test_settings_service_preserves_existing_credentials_when_update_omits_them(tmp_path) -> None:
    storage_path = tmp_path / "app_settings.json"
    service = SettingsService(repository=LocalSettingsRepository(storage_path))
    service.update_settings(build_request())

    updated = service.update_settings(
        build_request(
            openai={},
            meta={},
            higgsfield={},
            business_profile=BusinessProfileSettings(
                business_name="Updated Clinic",
                default_cta="Book online today.",
                posting_schedule=["Friday 10:00 AM"],
            ),
        )
    )

    assert updated.business_profile.business_name == "Updated Clinic"
    assert updated.providers.openai_api_key.configured is True
    assert json.loads(storage_path.read_text(encoding="utf-8"))["credentials"]["openai_api_key"] == (
        "sk-test-openai-key"
    )


def test_settings_update_requires_business_name() -> None:
    with pytest.raises(ValueError, match="Business name is required"):
        build_request(
            business_profile=BusinessProfileSettings(
                business_name="",
                default_cta="Schedule today.",
                posting_schedule=["Monday 9:00 AM"],
            )
        )


def test_settings_update_requires_posting_schedule() -> None:
    with pytest.raises(ValueError, match="At least one posting schedule"):
        build_request(
            business_profile=BusinessProfileSettings(
                business_name="Invictus Wellness",
                default_cta="Schedule today.",
                posting_schedule=[],
            )
        )


def test_settings_service_reads_openai_key_from_environment(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-vercel-env-key")
    monkeypatch.setenv("INVICTUS_OPENAI_MODEL", "gpt-5.5")
    get_runtime_settings.cache_clear()

    service = build_service(tmp_path)

    settings = service.get_settings()
    config = service.get_openai_config()

    assert settings.providers.openai_api_key.configured is True
    assert settings.providers.openai_api_key.masked_value == "sk-v****-key"
    assert config.api_key == "sk-vercel-env-key"
    assert config.model == "gpt-5.5"

    get_runtime_settings.cache_clear()


def test_runtime_storage_uses_writable_tmp_directory_on_vercel(monkeypatch) -> None:
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("INVICTUS_STORAGE_DIR", raising=False)
    monkeypatch.delenv("INVICTUS_DATA_DIR", raising=False)
    get_runtime_settings.cache_clear()

    assert str(get_runtime_storage_dir()) == "/tmp/invictus-os"

    get_runtime_settings.cache_clear()
