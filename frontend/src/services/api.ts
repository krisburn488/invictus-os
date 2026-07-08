const defaultApiBaseUrl = "http://127.0.0.1:8000";

export function getApiBaseUrl() {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL?.trim();
  return (configuredUrl || defaultApiBaseUrl).replace(/\/+$/, "");
}
