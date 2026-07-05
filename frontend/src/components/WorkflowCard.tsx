import type { WorkflowStep } from "../types/system";

type WorkflowCardProps = {
  steps: WorkflowStep[];
};

export function WorkflowCard({ steps }: WorkflowCardProps) {
  return (
    <section className="workflow-card" aria-labelledby="workflow-title">
      <div className="section-heading">
        <p className="eyebrow">Workflow</p>
        <h2 id="workflow-title">Content pipeline</h2>
      </div>
      <div className="workflow-steps">
        {steps.map((step) => (
          <div className={`workflow-step workflow-step--${step.status}`} key={step.name}>
            <span aria-hidden="true" />
            <div>
              <strong>{step.name}</strong>
              <p>{step.statusLabel}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
