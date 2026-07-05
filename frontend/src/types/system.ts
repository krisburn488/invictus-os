export type LoadState = "loading" | "ready" | "error";

export type AgentSummary = {
  id: string;
  name: string;
  capabilities: string[];
};

export type ActivityItem = {
  id: string;
  time: string;
  title: string;
  detail: string;
};

export type WorkflowStep = {
  name: string;
  status: "ready" | "active" | "waiting";
  statusLabel: string;
};
