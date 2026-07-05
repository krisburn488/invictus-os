from invictus_os.agents.registry import AgentRegistry
from invictus_os.models.agent import AgentResult, AgentTask


class AgentService:
    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    def list_agents(self):
        return self._registry.list()

    def run(self, agent_id: str, objective: str, context: dict[str, object]) -> AgentResult:
        agent = self._registry.get(agent_id)
        return agent.run(AgentTask(objective=objective, context=context))
