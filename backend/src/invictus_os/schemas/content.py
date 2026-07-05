from typing import Literal

from pydantic import BaseModel, Field

Platform = Literal["facebook", "instagram", "linkedin", "all"]
ContentType = Literal["post", "reel", "carousel", "story"]


class ContentGenerationRequest(BaseModel):
    business_name: str = Field(min_length=1, max_length=120)
    target_audience: str = Field(min_length=1, max_length=240)
    topic: str = Field(min_length=1, max_length=500)
    platform: Platform
    content_type: ContentType


class GeneratedContentResponse(BaseModel):
    post: str = Field(min_length=1)
    reel_script: str | None = None
    caption: str = Field(min_length=1)
    hashtags: list[str] = Field(min_length=1, max_length=12)
    call_to_action: str = Field(min_length=1)
