from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from invictus_os.schemas.content import GeneratedContentResponse
from invictus_os.schemas.design import DesignGraphicResponse
from invictus_os.schemas.reel import ReelPackageResponse

SchedulePlatform = Literal["facebook", "instagram", "both"]
ScheduleContentType = Literal["image_post", "carousel", "reel"]
ScheduledPostStatus = Literal["draft", "scheduled", "ready_to_publish"]


class SchedulePostRequest(BaseModel):
    platform: SchedulePlatform
    content_type: ScheduleContentType
    scheduled_for: datetime | None = None
    publish_now: bool = False
    draft_only: bool = False
    content: GeneratedContentResponse
    design: DesignGraphicResponse | None = None
    reel: ReelPackageResponse | None = None

    @model_validator(mode="after")
    def validate_schedule_mode(self) -> "SchedulePostRequest":
        if self.publish_now and self.draft_only:
            raise ValueError("Choose either publish now or draft-only, not both.")
        if not self.publish_now and not self.draft_only and self.scheduled_for is None:
            raise ValueError("Choose a date and time, publish now, or draft-only.")
        if self.content_type in {"image_post", "carousel"} and self.design is None:
            raise ValueError("Create a graphic before scheduling an image post or carousel.")
        if self.content_type == "reel" and self.reel is None:
            raise ValueError("Create today's reel before scheduling a reel.")
        return self


class ScheduledPost(BaseModel):
    id: str = Field(min_length=1)
    platform: SchedulePlatform
    content_type: ScheduleContentType
    status: ScheduledPostStatus
    scheduled_for: datetime | None = None
    created_at: datetime
    updated_at: datetime
    caption: str = Field(min_length=1)
    hashtags: list[str] = Field(min_length=1)
    post_preview: str = Field(min_length=1)
    content: GeneratedContentResponse
    design: DesignGraphicResponse | None = None
    reel: ReelPackageResponse | None = None


class ScheduledPostsResponse(BaseModel):
    posts: list[ScheduledPost]
