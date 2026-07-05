from typing import Literal

from pydantic import BaseModel

from invictus_os.models.agent import AgentResult


class WorkflowRun(BaseModel):
    id: str
    status: Literal["completed", "failed", "requires_approval"]
    steps: list[AgentResult]
