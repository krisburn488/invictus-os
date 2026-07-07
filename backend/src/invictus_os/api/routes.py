from fastapi import APIRouter, HTTPException, status

from invictus_os.agents.registry import build_agent_registry
from invictus_os.config.settings import get_settings
from invictus_os.schemas.agent import AgentRunRequest, AgentRunResponse, AgentSummary
from invictus_os.schemas.content import ContentGenerationRequest, GeneratedContentResponse
from invictus_os.schemas.design import DesignGraphicRequest, DesignGraphicResponse
from invictus_os.schemas.health import HealthResponse
from invictus_os.services.agent_service import AgentService
from invictus_os.services.content_generator import (
    ContentGenerationError,
    InvalidContentResponseError,
    MissingOpenAIAPIKeyError,
    OpenAIContentGenerator,
    OpenAINetworkError,
    OpenAIQuotaError,
    OpenAIRateLimitError,
)
from invictus_os.services.design_service import DesignService, DesignServiceError

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


@router.post("/content/generate", response_model=GeneratedContentResponse, tags=["content"])
def generate_content(request: ContentGenerationRequest) -> GeneratedContentResponse:
    settings = get_settings()
    generator = OpenAIContentGenerator(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )

    try:
        return generator.generate(request)
    except MissingOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except OpenAIRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=exc.message,
        ) from exc
    except OpenAIQuotaError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=exc.message,
        ) from exc
    except OpenAINetworkError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
    except InvalidContentResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc
    except ContentGenerationError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.post("/design/graphics", response_model=DesignGraphicResponse, tags=["design"])
def create_design_graphic(request: DesignGraphicRequest) -> DesignGraphicResponse:
    service = DesignService()
    try:
        return service.create_graphic(request)
    except DesignServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


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
