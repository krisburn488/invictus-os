import type { FormEvent } from "react";
import { useEffect, useState } from "react";

import type { AppSettings, SettingsFormValue } from "../types/settings";

type SettingsPageProps = {
  settings: AppSettings | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  success: string | null;
  onSubmit: (value: SettingsFormValue) => void;
};

const emptyFormValue: SettingsFormValue = {
  openaiApiKey: "",
  openaiModel: "gpt-5.5",
  openaiTemperature: 0.7,
  openaiMaxOutputTokens: 1800,
  metaAppId: "",
  metaAppSecret: "",
  metaAccessToken: "",
  higgsfieldApiKey: "",
  brand: {
    logo: "",
    primaryColor: "#2f6f73",
    secondaryColor: "#247a52",
    accentColor: "#d89a21",
    headingFont: "Inter",
    bodyFont: "Inter",
  },
  businessProfile: {
    businessName: "",
    website: "",
    bookingUrl: "",
    officePhone: "",
    officeAddress: "",
    insuranceList: [],
    defaultCta: "",
    postingSchedule: [],
  },
};

export function SettingsPage({
  error,
  isLoading,
  isSaving,
  onSubmit,
  settings,
  success,
}: SettingsPageProps) {
  const [formValue, setFormValue] = useState<SettingsFormValue>(emptyFormValue);
  const [insuranceListText, setInsuranceListText] = useState("");
  const [postingScheduleText, setPostingScheduleText] = useState("");
  const [clientError, setClientError] = useState<string | null>(null);

  useEffect(() => {
    if (!settings) {
      return;
    }

    setFormValue({
      ...emptyFormValue,
      openaiModel: settings.providers.openaiModel,
      openaiTemperature: settings.providers.openaiTemperature,
      openaiMaxOutputTokens: settings.providers.openaiMaxOutputTokens,
      brand: settings.brand,
      businessProfile: settings.businessProfile,
    });
    setInsuranceListText(settings.businessProfile.insuranceList.join("\n"));
    setPostingScheduleText(settings.businessProfile.postingSchedule.join("\n"));
  }, [settings]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextValue = {
      ...formValue,
      businessProfile: {
        ...formValue.businessProfile,
        insuranceList: parseLines(insuranceListText),
        postingSchedule: parseLines(postingScheduleText),
      },
    };

    const validationError = validateSettings(nextValue);
    if (validationError) {
      setClientError(validationError);
      return;
    }

    setClientError(null);
    onSubmit(nextValue);
  }

  return (
    <section className="generator-panel" aria-labelledby="settings-title">
      <div className="section-heading">
        <p className="eyebrow">Settings</p>
        <h2 id="settings-title">Settings</h2>
      </div>

      {isLoading ? (
        <div className="setup-panel" role="status">
          <strong>Loading settings</strong>
          <p>InvictusOS is loading your local configuration.</p>
        </div>
      ) : null}

      <form className="content-form" onSubmit={handleSubmit}>
        <section className="settings-section" aria-labelledby="openai-settings-title">
          <h3 id="openai-settings-title">OpenAI</h3>
          <CredentialStatus
            label="OpenAI API key"
            maskedValue={settings?.providers.openaiApiKey.maskedValue}
          />
          <label>
            <span>OpenAI API key</span>
            <input
              autoComplete="off"
              onChange={(event) => setFormValue({ ...formValue, openaiApiKey: event.target.value })}
              placeholder={settings?.providers.openaiApiKey.configured ? "Stored securely" : "sk-..."}
              type="password"
              value={formValue.openaiApiKey}
            />
          </label>
          <div className="form-grid">
            <label>
              <span>OpenAI model</span>
              <input
                onChange={(event) => setFormValue({ ...formValue, openaiModel: event.target.value })}
                required
                value={formValue.openaiModel}
              />
            </label>
            <label>
              <span>Temperature</span>
              <input
                max="2"
                min="0"
                onChange={(event) =>
                  setFormValue({ ...formValue, openaiTemperature: Number(event.target.value) })
                }
                step="0.1"
                type="number"
                value={formValue.openaiTemperature}
              />
            </label>
          </div>
          <label>
            <span>Max output tokens</span>
            <input
              max="12000"
              min="256"
              onChange={(event) =>
                setFormValue({ ...formValue, openaiMaxOutputTokens: Number(event.target.value) })
              }
              step="100"
              type="number"
              value={formValue.openaiMaxOutputTokens}
            />
          </label>
        </section>

        <section className="settings-section" aria-labelledby="meta-settings-title">
          <h3 id="meta-settings-title">Meta</h3>
          <CredentialStatus label="Meta App ID" maskedValue={settings?.providers.metaAppId.maskedValue} />
          <CredentialStatus
            label="Meta App secret"
            maskedValue={settings?.providers.metaAppSecret.maskedValue}
          />
          <CredentialStatus
            label="Meta access token"
            maskedValue={settings?.providers.metaAccessToken.maskedValue}
          />
          <div className="form-grid">
            <label>
              <span>Meta App ID</span>
              <input
                autoComplete="off"
                onChange={(event) => setFormValue({ ...formValue, metaAppId: event.target.value })}
                placeholder={settings?.providers.metaAppId.configured ? "Stored securely" : "App ID"}
                type="password"
                value={formValue.metaAppId}
              />
            </label>
            <label>
              <span>Meta App secret</span>
              <input
                autoComplete="off"
                onChange={(event) => setFormValue({ ...formValue, metaAppSecret: event.target.value })}
                placeholder={settings?.providers.metaAppSecret.configured ? "Stored securely" : "App secret"}
                type="password"
                value={formValue.metaAppSecret}
              />
            </label>
          </div>
          <label>
            <span>Meta access token</span>
            <input
              autoComplete="off"
              onChange={(event) => setFormValue({ ...formValue, metaAccessToken: event.target.value })}
              placeholder={settings?.providers.metaAccessToken.configured ? "Stored securely" : "Access token"}
              type="password"
              value={formValue.metaAccessToken}
            />
          </label>
        </section>

        <section className="settings-section" aria-labelledby="higgsfield-settings-title">
          <h3 id="higgsfield-settings-title">Higgsfield</h3>
          <CredentialStatus
            label="Higgsfield API key"
            maskedValue={settings?.providers.higgsfieldApiKey.maskedValue}
          />
          <label>
            <span>Higgsfield credentials</span>
            <input
              autoComplete="off"
              onChange={(event) =>
                setFormValue({ ...formValue, higgsfieldApiKey: event.target.value })
              }
              placeholder={settings?.providers.higgsfieldApiKey.configured ? "Stored securely" : "API key"}
              type="password"
              value={formValue.higgsfieldApiKey}
            />
          </label>
        </section>

        <section className="settings-section" aria-labelledby="brand-settings-title">
          <h3 id="brand-settings-title">Brand</h3>
          <label>
            <span>Logo</span>
            <input
              onChange={(event) =>
                setFormValue({ ...formValue, brand: { ...formValue.brand, logo: event.target.value } })
              }
              placeholder="https://example.com/logo.png"
              value={formValue.brand.logo}
            />
          </label>
          <div className="form-grid">
            <label>
              <span>Primary color</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    brand: { ...formValue.brand, primaryColor: event.target.value },
                  })
                }
                type="color"
                value={formValue.brand.primaryColor}
              />
            </label>
            <label>
              <span>Secondary color</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    brand: { ...formValue.brand, secondaryColor: event.target.value },
                  })
                }
                type="color"
                value={formValue.brand.secondaryColor}
              />
            </label>
            <label>
              <span>Accent color</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    brand: { ...formValue.brand, accentColor: event.target.value },
                  })
                }
                type="color"
                value={formValue.brand.accentColor}
              />
            </label>
          </div>
          <div className="form-grid">
            <label>
              <span>Heading font</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    brand: { ...formValue.brand, headingFont: event.target.value },
                  })
                }
                value={formValue.brand.headingFont}
              />
            </label>
            <label>
              <span>Body font</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    brand: { ...formValue.brand, bodyFont: event.target.value },
                  })
                }
                value={formValue.brand.bodyFont}
              />
            </label>
          </div>
        </section>

        <section className="settings-section" aria-labelledby="business-settings-title">
          <h3 id="business-settings-title">Business Profile</h3>
          <label>
            <span>Business name</span>
            <input
              onChange={(event) =>
                setFormValue({
                  ...formValue,
                  businessProfile: {
                    ...formValue.businessProfile,
                    businessName: event.target.value,
                  },
                })
              }
              required
              value={formValue.businessProfile.businessName}
            />
          </label>
          <div className="form-grid">
            <label>
              <span>Website</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    businessProfile: { ...formValue.businessProfile, website: event.target.value },
                  })
                }
                value={formValue.businessProfile.website}
              />
            </label>
            <label>
              <span>Booking URL</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    businessProfile: { ...formValue.businessProfile, bookingUrl: event.target.value },
                  })
                }
                value={formValue.businessProfile.bookingUrl}
              />
            </label>
          </div>
          <div className="form-grid">
            <label>
              <span>Office phone</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    businessProfile: { ...formValue.businessProfile, officePhone: event.target.value },
                  })
                }
                value={formValue.businessProfile.officePhone}
              />
            </label>
            <label>
              <span>Office address</span>
              <input
                onChange={(event) =>
                  setFormValue({
                    ...formValue,
                    businessProfile: { ...formValue.businessProfile, officeAddress: event.target.value },
                  })
                }
                value={formValue.businessProfile.officeAddress}
              />
            </label>
          </div>
          <label>
            <span>Insurance list</span>
            <textarea
              onChange={(event) => setInsuranceListText(event.target.value)}
              rows={4}
              value={insuranceListText}
            />
          </label>
          <label>
            <span>Default CTA</span>
            <input
              onChange={(event) =>
                setFormValue({
                  ...formValue,
                  businessProfile: { ...formValue.businessProfile, defaultCta: event.target.value },
                })
              }
              required
              value={formValue.businessProfile.defaultCta}
            />
          </label>
          <label>
            <span>Posting schedule</span>
            <textarea
              onChange={(event) => setPostingScheduleText(event.target.value)}
              required
              rows={4}
              value={postingScheduleText}
            />
          </label>
        </section>

        {clientError ? (
          <section className="error-panel" role="alert">
            <strong>Settings need attention</strong>
            <p>{clientError}</p>
          </section>
        ) : null}

        {error ? (
          <section className="error-panel" role="alert">
            <strong>Settings need attention</strong>
            <p>{error}</p>
          </section>
        ) : null}

        {success ? (
          <section className="success-panel" role="status">
            <strong>Settings saved</strong>
            <p>{success}</p>
          </section>
        ) : null}

        <button className="primary-button" disabled={isSaving || isLoading} type="submit">
          {isSaving ? "Saving settings..." : "Save Settings"}
        </button>
      </form>
    </section>
  );
}

function CredentialStatus({ label, maskedValue }: { label: string; maskedValue?: string }) {
  return (
    <p className="credential-status">
      <strong>{label}</strong>
      <span>{maskedValue ? `Configured: ${maskedValue}` : "Not configured"}</span>
    </p>
  );
}

function parseLines(value: string) {
  return value
    .split(/\r?\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function validateSettings(value: SettingsFormValue) {
  if (!value.businessProfile.businessName.trim()) {
    return "Business name is required.";
  }
  if (!value.openaiModel.trim()) {
    return "OpenAI model is required.";
  }
  if (value.openaiTemperature < 0 || value.openaiTemperature > 2) {
    return "OpenAI temperature must be between 0 and 2.";
  }
  if (value.openaiMaxOutputTokens < 256) {
    return "OpenAI max output tokens must be at least 256.";
  }
  if (!value.businessProfile.defaultCta.trim()) {
    return "Default CTA is required.";
  }
  if (value.businessProfile.postingSchedule.length === 0) {
    return "At least one posting schedule entry is required.";
  }
  return null;
}
