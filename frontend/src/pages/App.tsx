import { Activity, GitBranch, ShieldCheck } from "lucide-react";

import { StatusPanel } from "../components/StatusPanel";
import { useAgents } from "../hooks/useAgents";

export function App() {
  const { agents, state } = useAgents();

  return (
    <main className="app-shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">InvictusOS</p>
          <h1>AI operating system for governed agent workflows.</h1>
          <p className="lede">
            Coordinate specialized agents, approval gates, and auditable automation from a
            production-grade operator console.
          </p>
        </div>
        <StatusPanel state={state} />
      </section>

      <section className="metric-grid" aria-label="System capabilities">
        <article>
          <Activity aria-hidden="true" />
          <h2>Agent Runtime</h2>
          <p>{agents.length} registered agent{agents.length === 1 ? "" : "s"} available.</p>
        </article>
        <article>
          <GitBranch aria-hidden="true" />
          <h2>Workflow Layer</h2>
          <p>Structured orchestration for inspect, plan, approve, execute, and verify cycles.</p>
        </article>
        <article>
          <ShieldCheck aria-hidden="true" />
          <h2>Governance</h2>
          <p>Designed for approval gates, evidence capture, and policy-aware execution.</p>
        </article>
      </section>
    </main>
  );
}
