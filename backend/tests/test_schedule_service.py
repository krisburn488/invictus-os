from datetime import UTC, datetime, timedelta

import pytest

from invictus_os.schemas.content import GeneratedContentResponse
from invictus_os.schemas.design import DesignGraphicResponse, DesignSlide, GeneratedDesignCopy
from invictus_os.schemas.reel import ReelPackageResponse, ReelStoryboardScene
from invictus_os.schemas.schedule import SchedulePostRequest
from invictus_os.services.schedule_service import LocalScheduleRepository, ScheduleService


def build_content() -> GeneratedContentResponse:
    return GeneratedContentResponse(
        post="Annual wellness visits help busy families stay proactive.",
        reel_script=None,
        caption="Preventive care is easier with a simple plan.",
        hashtags=["#PreventiveCare", "#FamilyHealth"],
        call_to_action="Schedule your wellness visit today.",
    )


def build_design() -> DesignGraphicResponse:
    return DesignGraphicResponse(
        status="created",
        graphic_type="single",
        extracted_content=GeneratedDesignCopy(
            headline="Annual wellness visits",
            body_text="Stay proactive with preventive care.",
            call_to_action="Schedule today.",
        ),
        message="Design ready.",
        slides=[DesignSlide(id="single-post", title="Single Post", svg="<svg></svg>")],
    )


def build_reel() -> ReelPackageResponse:
    scenes = [
        ReelStoryboardScene(
            scene_number=1,
            duration_seconds=37,
            visual_direction="AI avatar in a bright wellness studio.",
            on_screen_text="Annual wellness visits",
            voice_over="Annual wellness visits help busy families stay proactive.",
            higgsfield_prompt="Create a vertical 9:16 AI avatar video.",
        )
    ]
    return ReelPackageResponse(
        hook="Annual wellness visits help busy families stay proactive?",
        script="Scene 1: Annual wellness visits help busy families stay proactive.",
        storyboard=scenes,
        on_screen_text=["Annual wellness visits"],
        voice_over_script="Annual wellness visits help busy families stay proactive.",
        caption="Preventive care is easier with a simple plan.",
        hashtags=["#PreventiveCare"],
        reel_format="ai_avatar",
        duration_seconds=37,
        markdown="# Reel",
    )


def build_service(tmp_path) -> ScheduleService:
    return ScheduleService(
        repository=LocalScheduleRepository(tmp_path / "scheduled_posts.json"),
    )


def test_schedule_service_stores_scheduled_image_post(tmp_path) -> None:
    service = build_service(tmp_path)
    scheduled_for = datetime.now(UTC) + timedelta(days=1)

    post = service.schedule_post(
        SchedulePostRequest(
            platform="instagram",
            content_type="image_post",
            scheduled_for=scheduled_for,
            content=build_content(),
            design=build_design(),
        )
    )

    assert post.status == "scheduled"
    assert post.scheduled_for == scheduled_for
    assert post.caption == "Preventive care is easier with a simple plan."
    assert service.list_posts()[0].id == post.id


def test_schedule_service_stores_publish_now_reel_as_local_ready_state(tmp_path) -> None:
    service = build_service(tmp_path)

    post = service.schedule_post(
        SchedulePostRequest(
            platform="both",
            content_type="reel",
            publish_now=True,
            content=build_content(),
            reel=build_reel(),
        )
    )

    assert post.status == "ready_to_publish"
    assert post.scheduled_for is None
    assert post.post_preview.startswith("Annual wellness visits")


def test_schedule_service_stores_draft_only_carousel(tmp_path) -> None:
    service = build_service(tmp_path)
    design = build_design().model_copy(update={"graphic_type": "carousel"})

    post = service.schedule_post(
        SchedulePostRequest(
            platform="facebook",
            content_type="carousel",
            draft_only=True,
            content=build_content(),
            design=design,
        )
    )

    assert post.status == "draft"
    assert post.scheduled_for is None


def test_schedule_request_requires_matching_asset() -> None:
    with pytest.raises(ValueError, match="Create today's reel"):
        SchedulePostRequest(
            platform="instagram",
            content_type="reel",
            publish_now=True,
            content=build_content(),
        )
