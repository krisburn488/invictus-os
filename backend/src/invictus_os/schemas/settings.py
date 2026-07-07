from pydantic import BaseModel, Field, field_validator, model_validator


class SensitiveCredentialStatus(BaseModel):
    configured: bool = False
    masked_value: str | None = None


class ProviderCredentialUpdate(BaseModel):
    api_key: str | None = None
    app_id: str | None = None
    app_secret: str | None = None
    access_token: str | None = None

    @field_validator("api_key", "app_id", "app_secret", "access_token")
    @classmethod
    def normalize_optional_secret(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ProviderSettingsStatus(BaseModel):
    openai_api_key: SensitiveCredentialStatus
    meta_app_id: SensitiveCredentialStatus
    meta_app_secret: SensitiveCredentialStatus
    meta_access_token: SensitiveCredentialStatus
    higgsfield_api_key: SensitiveCredentialStatus


class BrandSettings(BaseModel):
    logo: str = ""
    primary_color: str = "#2f6f73"
    secondary_color: str = "#247a52"
    accent_color: str = "#d89a21"
    heading_font: str = "Inter"
    body_font: str = "Inter"

    @field_validator("primary_color", "secondary_color", "accent_color")
    @classmethod
    def validate_hex_color(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) != 7 or not stripped.startswith("#"):
            raise ValueError("Brand colors must use hex format like #2f6f73.")
        int(stripped[1:], 16)
        return stripped.lower()

    @field_validator("heading_font", "body_font", "logo")
    @classmethod
    def normalize_brand_text(cls, value: str) -> str:
        return value.strip()


class BusinessProfileSettings(BaseModel):
    business_name: str = ""
    website: str = ""
    booking_url: str = ""
    office_phone: str = ""
    office_address: str = ""
    insurance_list: list[str] = Field(default_factory=list)
    default_cta: str = ""
    posting_schedule: list[str] = Field(default_factory=list)

    @field_validator(
        "business_name",
        "website",
        "booking_url",
        "office_phone",
        "office_address",
        "default_cta",
    )
    @classmethod
    def normalize_profile_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("insurance_list", "posting_schedule")
    @classmethod
    def normalize_list_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class AppSettingsResponse(BaseModel):
    providers: ProviderSettingsStatus
    brand: BrandSettings
    business_profile: BusinessProfileSettings


class AppSettingsUpdateRequest(BaseModel):
    openai: ProviderCredentialUpdate = Field(default_factory=ProviderCredentialUpdate)
    meta: ProviderCredentialUpdate = Field(default_factory=ProviderCredentialUpdate)
    higgsfield: ProviderCredentialUpdate = Field(default_factory=ProviderCredentialUpdate)
    brand: BrandSettings = Field(default_factory=BrandSettings)
    business_profile: BusinessProfileSettings = Field(default_factory=BusinessProfileSettings)

    @model_validator(mode="after")
    def validate_required_profile_fields(self) -> "AppSettingsUpdateRequest":
        if not self.business_profile.business_name:
            raise ValueError("Business name is required.")
        if not self.business_profile.default_cta:
            raise ValueError("Default CTA is required.")
        if not self.business_profile.posting_schedule:
            raise ValueError("At least one posting schedule entry is required.")
        return self
