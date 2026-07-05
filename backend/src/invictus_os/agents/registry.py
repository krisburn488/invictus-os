from invictus_os.agents.orchestrator import OrchestratorAgent
from invictus_os.core.ports import Agent


class AgentRegistry:
    def __init__(self, agents: list[Agent]) -> None:
        self._agents = {agent.id: agent for agent in agents}

    def get(self, agent_id: str) -> Agent:
        return self._agents[agent_id]

    def list(self) -> list[Agent]:
        return list(self._agents.values())


def build_agent_registry() -> AgentRegistry:
    return AgentRegistry(agents=[OrchestratorAgent()])
