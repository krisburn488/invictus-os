from typing import Literal

from pydantic import BaseModel, Field

from invictus_os.schemas.content import GeneratedContentResponse

CanvaGraphicType = Literal["single", "carousel", "quote"]
CanvaDesignStatus = Literal["created", "in_progress", "setup_required"]


class CanvaGeneratedCopy(BaseModel):
    headline: str = Field(min_length=1)
    body_text: str = Field(min_length=1)
    call_to_action: str = Field(min_length=1)


class CanvaGraphicRequest(BaseModel):
    graphic_type: CanvaGraphicType
    content: GeneratedContentResponse


class CanvaDesignResult(BaseModel):
    url: str | None = None
    thumbnail_url: str | None = None
    job_id: str | None = None


class CanvaGraphicResponse(BaseModel):
    status: CanvaDesignStatus
    graphic_type: CanvaGraphicType
    extracted_content: CanvaGeneratedCopy
    message: str
    design: CanvaDesignResult | None = None
