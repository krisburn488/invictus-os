export type SensitiveCredentialStatus = {
  configured: boolean;
  maskedValue?: string;
};

export type ProviderSettingsStatus = {
  openaiApiKey: SensitiveCredentialStatus;
  openaiModel: string;
  openaiTemperature: number;
  openaiMaxOutputTokens: number;
  metaAppId: SensitiveCredentialStatus;
  metaAppSecret: SensitiveCredentialStatus;
  metaAccessToken: SensitiveCredentialStatus;
  higgsfieldApiKey: SensitiveCredentialStatus;
};

export type BrandSettings = {
  logo: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  headingFont: string;
  bodyFont: string;
};

export type BusinessProfileSettings = {
  businessName: string;
  website: string;
  bookingUrl: string;
  officePhone: string;
  officeAddress: string;
  insuranceList: string[];
  defaultCta: string;
  postingSchedule: string[];
};

export type AppSettings = {
  providers: ProviderSettingsStatus;
  brand: BrandSettings;
  businessProfile: BusinessProfileSettings;
};

export type SettingsFormValue = {
  openaiApiKey: string;
  openaiModel: string;
  openaiTemperature: number;
  openaiMaxOutputTokens: number;
  metaAppId: string;
  metaAppSecret: string;
  metaAccessToken: string;
  higgsfieldApiKey: string;
  brand: BrandSettings;
  businessProfile: BusinessProfileSettings;
};
