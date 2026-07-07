from fastapi import APIRouter, HTTPException, status

from invictus_os.agents.registry import build_agent_registry
from invictus_os.config.settings import get_settings
from invictus_os.schemas.agent import AgentRunRequest, AgentRunResponse, AgentSummary
from invictus_os.schemas.canva import CanvaGraphicRequest, CanvaGraphicResponse
from invictus_os.schemas.content import ContentGenerationRequest, GeneratedContentResponse
from invictus_os.schemas.health import HealthResponse
from invictus_os.services.agent_service import AgentService
from invictus_os.services.canva_design import (
    CanvaAuthenticationError,
    CanvaCredentials,
    CanvaDesignError,
    CanvaDesignService,
    CanvaInvalidResponseError,
    CanvaNetworkError,
    CanvaRateLimitError,
)
from invictus_os.services.content_generator import (
    ContentGenerationError,
    InvalidContentResponseError,
    MissingOpenAIAPIKeyError,
    OpenAIContentGenerator,
    OpenAINetworkError,
    OpenAIQuotaError,
    OpenAIRateLimitError,
)

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


@router.post("/canva/graphics", response_model=CanvaGraphicResponse, tags=["canva"])
def create_canva_graphic(request: CanvaGraphicRequest) -> CanvaGraphicResponse:
    settings = get_settings()
    service = CanvaDesignService(
        credentials=CanvaCredentials(
            access_token=settings.canva_access_token,
            brand_template_id=settings.canva_brand_template_id,
            api_base_url=settings.canva_api_base_url,
            timeout_seconds=settings.canva_timeout_seconds,
            poll_attempts=settings.canva_poll_attempts,
            poll_interval_seconds=settings.canva_poll_interval_seconds,
            headline_field=settings.canva_headline_field,
            body_field=settings.canva_body_field,
            cta_field=settings.canva_cta_field,
            graphic_type_field=settings.canva_graphic_type_field,
        )
    )

    try:
        return service.create_graphic(request)
    except CanvaAuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc
    except CanvaRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=exc.message,
        ) from exc
    except CanvaNetworkError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=exc.message,
        ) from exc
    except CanvaInvalidResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc
    except CanvaDesignError as exc:
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
