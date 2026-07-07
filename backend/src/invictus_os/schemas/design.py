from typing import Literal

from pydantic import BaseModel, Field

from invictus_os.schemas.content import GeneratedContentResponse

GraphicType = Literal["single", "carousel", "quote"]
DesignStatus = Literal["created"]


class GeneratedDesignCopy(BaseModel):
    headline: str = Field(min_length=1)
    body_text: str = Field(min_length=1)
    call_to_action: str = Field(min_length=1)


class DesignGraphicRequest(BaseModel):
    graphic_type: GraphicType
    content: GeneratedContentResponse


class DesignSlide(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    width: int = 1080
    height: int = 1350
    svg: str = Field(min_length=1)


class DesignGraphicResponse(BaseModel):
    status: DesignStatus
    graphic_type: GraphicType
    extracted_content: GeneratedDesignCopy
    message: str
    slides: list[DesignSlide] = Field(min_length=1)
