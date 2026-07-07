from fastapi import APIRouter, HTTPException, status

from invictus_os.agents.registry import build_agent_registry
from invictus_os.schemas.agent import AgentRunRequest, AgentRunResponse, AgentSummary
from invictus_os.schemas.content import ContentGenerationRequest, GeneratedContentResponse
from invictus_os.schemas.design import DesignGraphicRequest, DesignGraphicResponse
from invictus_os.schemas.health import HealthResponse
from invictus_os.schemas.reel import ReelPackageRequest, ReelPackageResponse
from invictus_os.schemas.schedule import SchedulePostRequest, ScheduledPost, ScheduledPostsResponse
from invictus_os.schemas.settings import AppSettingsResponse, AppSettingsUpdateRequest
from invictus_os.services.agent_service import AgentService
from invictus_os.services.content_generator import (
    ContentGenerationError,
    InvalidContentResponseError,
    OpenAIContentGenerator,
)
from invictus_os.services.design_service import DesignService, DesignServiceError
from invictus_os.services.openai_service import (
    InvalidOpenAIAPIKeyError,
    MissingOpenAIAPIKeyError,
    OpenAINetworkError,
    OpenAIQuotaError,
    OpenAIRateLimitError,
    OpenAIService,
)
from invictus_os.services.reel_service import ReelService, ReelServiceError
from invictus_os.services.schedule_service import ScheduleService, ScheduleServiceError
from invictus_os.services.settings_service import SettingsService, SettingsServiceError

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
    generator = OpenAIContentGenerator(openai_service=build_openai_service())

    try:
        return generator.generate(request)
    except MissingOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except InvalidOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc
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
    service = DesignService(openai_service=build_openai_service())
    try:
        return service.create_graphic(request)
    except MissingOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except InvalidOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc
    except OpenAIRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=exc.message) from exc
    except OpenAIQuotaError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=exc.message) from exc
    except OpenAINetworkError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except DesignServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.post("/reels/today", response_model=ReelPackageResponse, tags=["reels"])
def create_today_reel(request: ReelPackageRequest) -> ReelPackageResponse:
    service = ReelService(openai_service=build_openai_service())
    try:
        return service.create_package(request)
    except MissingOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except InvalidOpenAIAPIKeyError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc
    except OpenAIRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=exc.message) from exc
    except OpenAIQuotaError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=exc.message) from exc
    except OpenAINetworkError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message) from exc
    except ReelServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.get("/schedule/posts", response_model=ScheduledPostsResponse, tags=["schedule"])
def list_scheduled_posts() -> ScheduledPostsResponse:
    service = ScheduleService()
    try:
        return ScheduledPostsResponse(posts=service.list_posts())
    except ScheduleServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.post("/schedule/posts", response_model=ScheduledPost, tags=["schedule"])
def schedule_post(request: SchedulePostRequest) -> ScheduledPost:
    service = ScheduleService()
    try:
        return service.schedule_post(request)
    except ScheduleServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.get("/settings", response_model=AppSettingsResponse, tags=["settings"])
def get_app_settings() -> AppSettingsResponse:
    service = SettingsService()
    try:
        return service.get_settings()
    except SettingsServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.put("/settings", response_model=AppSettingsResponse, tags=["settings"])
def update_app_settings(request: AppSettingsUpdateRequest) -> AppSettingsResponse:
    service = SettingsService()
    try:
        return service.update_settings(request)
    except SettingsServiceError as exc:
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


def build_openai_service() -> OpenAIService:
    settings_service = SettingsService()
    return OpenAIService(config=settings_service.get_openai_config())
