from typing import Literal

from pydantic import BaseModel, Field

from invictus_os.schemas.content import GeneratedContentResponse

ReelFormat = Literal["talking_head", "ai_avatar", "b_roll"]


class ReelPackageRequest(BaseModel):
    content: GeneratedContentResponse
    reel_format: ReelFormat = "talking_head"


class ReelStoryboardScene(BaseModel):
    scene_number: int = Field(ge=1)
    duration_seconds: int = Field(ge=1)
    visual_direction: str = Field(min_length=1)
    on_screen_text: str = Field(min_length=1)
    voice_over: str = Field(min_length=1)
    higgsfield_prompt: str = Field(min_length=1)


class ReelPackageResponse(BaseModel):
    hook: str = Field(min_length=1)
    script: str = Field(min_length=1)
    storyboard: list[ReelStoryboardScene] = Field(min_length=1)
    on_screen_text: list[str] = Field(min_length=1)
    voice_over_script: str = Field(min_length=1)
    caption: str = Field(min_length=1)
    hashtags: list[str] = Field(min_length=1)
    reel_format: ReelFormat
    duration_seconds: int = Field(ge=30, le=45)
    markdown: str = Field(min_length=1)
