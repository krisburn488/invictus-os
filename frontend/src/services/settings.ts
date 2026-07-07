import type { AppSettings, SettingsFormValue } from "../types/settings";

type ApiAppSettings = {
  providers: {
    openai_api_key: ApiSensitiveCredentialStatus;
    meta_app_id: ApiSensitiveCredentialStatus;
    meta_app_secret: ApiSensitiveCredentialStatus;
    meta_access_token: ApiSensitiveCredentialStatus;
    higgsfield_api_key: ApiSensitiveCredentialStatus;
  };
  brand: {
    logo: string;
    primary_color: string;
    secondary_color: string;
    accent_color: string;
    heading_font: string;
    body_font: string;
  };
  business_profile: {
    business_name: string;
    website: string;
    booking_url: string;
    office_phone: string;
    office_address: string;
    insurance_list: string[];
    default_cta: string;
    posting_schedule: string[];
  };
};

type ApiSensitiveCredentialStatus = {
  configured: boolean;
  masked_value?: string | null;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function getSettings(): Promise<AppSettings> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/settings`);
  } catch {
    throw new Error("InvictusOS could not reach the backend. Confirm the backend is running.");
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  if (!isApiAppSettings(payload)) {
    throw new Error("InvictusOS received an unexpected settings response.");
  }

  return toAppSettings(payload);
}

export async function saveSettings(value: SettingsFormValue): Promise<AppSettings> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/settings`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(toApiSettingsRequest(value)),
    });
  } catch {
    throw new Error("InvictusOS could not reach the backend. Confirm the backend is running.");
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  if (!isApiAppSettings(payload)) {
    throw new Error("InvictusOS received an unexpected settings response.");
  }

  return toAppSettings(payload);
}

function toApiSettingsRequest(value: SettingsFormValue) {
  return {
    openai: {
      api_key: value.openaiApiKey || null,
    },
    meta: {
      app_id: value.metaAppId || null,
      app_secret: value.metaAppSecret || null,
      access_token: value.metaAccessToken || null,
    },
    higgsfield: {
      api_key: value.higgsfieldApiKey || null,
    },
    brand: {
      logo: value.brand.logo,
      primary_color: value.brand.primaryColor,
      secondary_color: value.brand.secondaryColor,
      accent_color: value.brand.accentColor,
      heading_font: value.brand.headingFont,
      body_font: value.brand.bodyFont,
    },
    business_profile: {
      business_name: value.businessProfile.businessName,
      website: value.businessProfile.website,
      booking_url: value.businessProfile.bookingUrl,
      office_phone: value.businessProfile.officePhone,
      office_address: value.businessProfile.officeAddress,
      insurance_list: value.businessProfile.insuranceList,
      default_cta: value.businessProfile.defaultCta,
      posting_schedule: value.businessProfile.postingSchedule,
    },
  };
}

function toAppSettings(settings: ApiAppSettings): AppSettings {
  return {
    providers: {
      openaiApiKey: toCredentialStatus(settings.providers.openai_api_key),
      metaAppId: toCredentialStatus(settings.providers.meta_app_id),
      metaAppSecret: toCredentialStatus(settings.providers.meta_app_secret),
      metaAccessToken: toCredentialStatus(settings.providers.meta_access_token),
      higgsfieldApiKey: toCredentialStatus(settings.providers.higgsfield_api_key),
    },
    brand: {
      logo: settings.brand.logo,
      primaryColor: settings.brand.primary_color,
      secondaryColor: settings.brand.secondary_color,
      accentColor: settings.brand.accent_color,
      headingFont: settings.brand.heading_font,
      bodyFont: settings.brand.body_font,
    },
    businessProfile: {
      businessName: settings.business_profile.business_name,
      website: settings.business_profile.website,
      bookingUrl: settings.business_profile.booking_url,
      officePhone: settings.business_profile.office_phone,
      officeAddress: settings.business_profile.office_address,
      insuranceList: settings.business_profile.insurance_list,
      defaultCta: settings.business_profile.default_cta,
      postingSchedule: settings.business_profile.posting_schedule,
    },
  };
}

function toCredentialStatus(status: ApiSensitiveCredentialStatus) {
  return {
    configured: status.configured,
    maskedValue: status.masked_value ?? undefined,
  };
}

function extractErrorMessage(value: unknown) {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return "InvictusOS could not save settings. Check required fields and try again.";
    }
  }

  return "InvictusOS could not save settings.";
}

function isApiAppSettings(value: unknown): value is ApiAppSettings {
  if (!value || typeof value !== "object") {
    return false;
  }
  const settings = value as Partial<ApiAppSettings>;
  return Boolean(settings.providers && settings.brand && settings.business_profile);
}
