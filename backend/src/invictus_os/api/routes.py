from fastapi import APIRouter, HTTPException, status

from invictus_os.agents.registry import build_agent_registry
from invictus_os.schemas.agent import AgentRunRequest, AgentRunResponse, AgentSummary
from invictus_os.schemas.health import HealthResponse
from invictus_os.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService(registry=build_agent_registry())


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="invictus-os-api")


@router.get("/agents", response_model=list[AgentSummary], tags=["agents"])
def list_agents() -> list[AgentSummary]:
    return [
        AgentSummary(id=agent.id, name=agent.name, capabilities=agent.capabilities)
        for agent in agent_service.list_agents()
    ]


@router.post("/agents/{agent_id}/runs", response_model=AgentRunResponse, tags=["agents"])
def run_agent(agent_id: str, request: AgentRunRequest) -> AgentRunResponse:
    try:
        result = agent_service.run(agent_id=agent_id, objective=request.objective, context=request.context)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' is not registered.",
        ) from exc

    return AgentRunResponse(
        agent_id=result.agent_id,
        status=result.status,
        summary=result.summary,
        evidence=result.evidence,
    )
