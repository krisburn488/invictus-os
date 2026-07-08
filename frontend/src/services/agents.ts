import type { AgentSummary } from "../types/system";
import { getApiBaseUrl } from "./api";

const apiBaseUrl = getApiBaseUrl();

export async function fetchAgents(): Promise<AgentSummary[]> {
  const response = await fetch(`${apiBaseUrl}/agents`);

  if (!response.ok) {
    throw new Error(`Failed to fetch agents: ${response.status}`);
  }

  return response.json() as Promise<AgentSummary[]>;
}
