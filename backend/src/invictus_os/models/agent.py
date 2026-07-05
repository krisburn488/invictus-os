from typing import Literal

from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    objective: str = Field(min_length=1)
    context: dict[str, object] = Field(default_factory=dict)


class AgentResult(BaseModel):
    agent_id: str
    status: Literal["completed", "failed", "requires_approval"]
    summary: str
    evidence: dict[str, object] = Field(default_factory=dict)
