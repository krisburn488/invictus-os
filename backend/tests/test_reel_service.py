from invictus_os.schemas.content import GeneratedContentResponse
from invictus_os.schemas.reel import ReelPackageRequest
from invictus_os.services.reel_service import ReelService


class FakeOpenAIService:
    def generate_json(self, **kwargs: object) -> dict:
        user_payload = kwargs.get("user_payload")
        reel_format = user_payload.get("reel_format", "talking_head") if isinstance(user_payload, dict) else "talking_head"
        format_label = {
            "talking_head": "talking-head healthcare creator video",
            "ai_avatar": "AI avatar presenter video",
            "b_roll": "cinematic healthcare B-roll video",
        }[reel_format]
        storyboard = [
            {
                "scene_number": 1,
                "duration_seconds": 8,
                "visual_direction": "Bright healthcare opening shot.",
                "on_screen_text": "Annual wellness visits",
                "voice_over": "Annual wellness visits can help busy families stay proactive.",
                "higgsfield_prompt": (
                    f"Create a vertical 9:16 {format_label} with Invictus Wellness branding. "
                    "On-screen text: Annual wellness visits. Voice-over: Annual wellness visits can help."
                ),
            },
            {
                "scene_number": 2,
                "duration_seconds": 10,
                "visual_direction": "Clean educational explainer scene.",
                "on_screen_text": "Why it matters",
                "voice_over": "A simple visit can keep your preventive care plan on track.",
                "higgsfield_prompt": f"Create a vertical 9:16 {format_label} with Invictus Wellness branding.",
            },
            {
                "scene_number": 3,
                "duration_seconds": 10,
                "visual_direction": "Supportive care detail shot.",
                "on_screen_text": "Simple next step",
                "voice_over": "Bring your questions and review next steps with your care team.",
                "higgsfield_prompt": f"Create a vertical 9:16 {format_label} with Invictus Wellness branding.",
            },
            {
                "scene_number": 4,
                "duration_seconds": 9,
                "visual_direction": "Closing brand-safe CTA shot.",
                "on_screen_text": "Schedule today",
                "voice_over": "Schedule your wellness visit today.",
                "higgsfield_prompt": f"Create a vertical 9:16 {format_label} with Invictus Wellness branding.",
            },
        ]
        return {
            "hook": "Annual wellness visits can help busy families stay proactive.",
            "script": "Scene 1: Annual wellness visits can help busy families stay proactive.",
            "storyboard": storyboard,
            "on_screen_text": [scene["on_screen_text"] for scene in storyboard],
            "voice_over_script": " ".join(str(scene["voice_over"]) for scene in storyboard),
            "caption": "Preventive care is easier to prioritize with a simple plan. Schedule your wellness visit today.",
            "hashtags": ["#PreventiveCare", "#FamilyHealth"],
            "duration_seconds": 37,
        }


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
    response = ReelService(openai_service=FakeOpenAIService()).create_package(build_request())  # type: ignore[arg-type]

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
        response = ReelService(openai_service=FakeOpenAIService()).create_package(  # type: ignore[arg-type]
            build_request(reel_format)
        )

        assert response.reel_format == reel_format
        assert len(response.storyboard) == 4
        assert all("Invictus Wellness" in scene.higgsfield_prompt for scene in response.storyboard)


def test_reel_service_generates_higgsfield_ready_scene_prompts() -> None:
    response = ReelService(openai_service=FakeOpenAIService()).create_package(  # type: ignore[arg-type]
        build_request("b_roll")
    )

    first_prompt = response.storyboard[0].higgsfield_prompt

    assert "vertical 9:16" in first_prompt
    assert "cinematic healthcare B-roll video" in first_prompt
    assert "On-screen text:" in first_prompt
    assert "Voice-over:" in first_prompt
