from invictus_os.agents.registry import AgentRegistry
from invictus_os.models.agent import AgentTask
from invictus_os.models.workflow import WorkflowRun


class WorkflowEngine:
    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    def run_single_agent_workflow(self, workflow_id: str, agent_id: str, task: AgentTask) -> WorkflowRun:
        agent = self._registry.get(agent_id)
        result = agent.run(task)
        return WorkflowRun(id=workflow_id, status=result.status, steps=[result])
