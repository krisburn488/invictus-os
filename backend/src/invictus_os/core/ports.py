from typing import Protocol

from invictus_os.models.agent import AgentResult, AgentTask


class Agent(Protocol):
    id: str
    name: str
    capabilities: tuple[str, ...]

    def run(self, task: AgentTask) -> AgentResult:
        """Execute a typed task and return a structured result."""
