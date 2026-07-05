import type { AgentSummary } from "../types/system";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchAgents(): Promise<AgentSummary[]> {
  const response = await fetch(`${API_BASE_URL}/agents`);

  if (!response.ok) {
    throw new Error(`Failed to fetch agents: ${response.status}`);
  }

  return response.json() as Promise<AgentSummary[]>;
}
