from invictus_os.models.agent import AgentResult, AgentTask


class OrchestratorAgent:
    id = "orchestrator"
    name = "Orchestrator Agent"
    capabilities = ("intent-analysis", "workflow-planning", "approval-routing")

    def run(self, task: AgentTask) -> AgentResult:
        objective = task.objective.strip()
        context_keys = sorted(task.context.keys())
        summary = (
            f"Objective '{objective}' accepted for orchestration with "
            f"{len(context_keys)} context fields."
        )
        return AgentResult(
            agent_id=self.id,
            status="completed",
            summary=summary,
            evidence={
                "objective": objective,
                "context_keys": context_keys,
                "next_action": "resolve-workflow",
            },
        )
