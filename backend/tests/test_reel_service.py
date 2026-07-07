from invictus_os.schemas.content import GeneratedContentResponse
from invictus_os.schemas.reel import ReelPackageRequest
from invictus_os.services.reel_service import ReelService


def build_request(reel_format: str = "talking_head") -> ReelPackageRequest:
    return ReelPackageRequest(
        reel_format=reel_format,
        content=GeneratedContentResponse(
            post=(
                "Annual wellness visits help busy families stay proactive. "
                "Invictus Wellness makes preventive care easier to understand and act on."
            ),
            reel_script=None,
            caption="Preventive care is easier to prioritize with a simple plan.",
            hashtags=["#PreventiveCare", "#FamilyHealth"],
            call_to_action="Schedule your wellness visit today.",
        ),
    )


def test_reel_service_generates_complete_package() -> None:
    response = ReelService().create_package(build_request())

    assert response.hook
    assert response.script
    assert response.caption.endswith("Schedule your wellness visit today.")
    assert response.duration_seconds == 37
    assert len(response.storyboard) == 4
    assert len(response.on_screen_text) == 4
    assert "#PreventiveCare" in response.hashtags
    assert "Higgsfield prompt" in response.markdown


def test_reel_service_supports_all_reel_formats() -> None:
    for reel_format in ["talking_head", "ai_avatar", "b_roll"]:
        response = ReelService().create_package(build_request(reel_format))

        assert response.reel_format == reel_format
        assert len(response.storyboard) == 4
        assert all("Invictus Wellness" in scene.higgsfield_prompt for scene in response.storyboard)


def test_reel_service_generates_higgsfield_ready_scene_prompts() -> None:
    response = ReelService().create_package(build_request("b_roll"))

    first_prompt = response.storyboard[0].higgsfield_prompt

    assert "vertical 9:16" in first_prompt
    assert "cinematic healthcare B-roll video" in first_prompt
    assert "On-screen text:" in first_prompt
    assert "Voice-over:" in first_prompt
