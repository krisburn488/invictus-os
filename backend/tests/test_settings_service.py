import json

import pytest

from invictus_os.schemas.settings import AppSettingsUpdateRequest, BrandSettings, BusinessProfileSettings
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
