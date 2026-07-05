import type { LoadState } from "../types/system";

type StatusPanelProps = {
  state: LoadState;
};

export function StatusPanel({ state }: StatusPanelProps) {
  const label = state === "ready" ? "API connected" : state === "loading" ? "Connecting" : "Degraded";

  return (
    <aside className="status-panel" aria-label="System status">
      <span className={`status-dot status-dot--${state}`} />
      <div>
        <h2>{label}</h2>
        <p>Operator console is configured for the FastAPI backend.</p>
      </div>
    </aside>
  );
}
