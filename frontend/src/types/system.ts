export type LoadState = "loading" | "ready" | "error";

export type AgentSummary = {
  id: string;
  name: string;
  capabilities: string[];
};
