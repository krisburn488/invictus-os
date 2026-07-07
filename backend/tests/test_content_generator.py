import pytest

from invictus_os.schemas.content import ContentGenerationRequest
from invictus_os.services.content_generator import InvalidContentResponseError, OpenAIContentGenerator
from invictus_os.services.openai_service import MissingOpenAIAPIKeyError


class FakeOpenAIService:
    def __init__(self, payload: dict | None = None, error: Exception | None = None) -> None:
        self.payload = payload or {}
        self.error = error

    def generate_json(self, **_: object) -> dict:
        if self.error:
            raise self.error
        return self.payload


def build_request(content_type: str = "post") -> ContentGenerationRequest:
    return ContentGenerationRequest(
        business_name="Invictus Health",
        target_audience="busy families looking for preventive care",
        topic="annual wellness visits",
        platform="instagram",
        content_type=content_type,  # type: ignore[arg-type]
    )


def test_openai_content_generator_returns_valid_content() -> None:
    provider = OpenAIContentGenerator(
        openai_service=FakeOpenAIService(
            {
                "headline": "Annual wellness visits",
                "body": "Preventive care made simple.",
                "post": "Annual wellness visits help families stay proactive.",
                "reel_script": None,
                "caption": "Make preventive care easier to prioritize.",
                "hashtags": ["#PreventiveCare", "#FamilyHealth"],
                "call_to_action": "Schedule a wellness visit today.",
            }
        )  # type: ignore[arg-type]
    )

    content = provider.generate(build_request())

    assert content.headline == "Annual wellness visits"
    assert content.body == "Preventive care made simple."
    assert content.post == "Annual wellness visits help families stay proactive."
    assert content.reel_script is None
    assert content.hashtags == ["#PreventiveCare", "#FamilyHealth"]


def test_openai_content_generator_requires_reel_script_for_reels() -> None:
    provider = OpenAIContentGenerator(
        openai_service=FakeOpenAIService(
            {
                "headline": "Annual wellness visits",
                "body": "Preventive care made simple.",
                "post": "A short post.",
                "reel_script": None,
                "caption": "A caption.",
                "hashtags": ["#Health"],
                "call_to_action": "Book today.",
            }
        )  # type: ignore[arg-type]
    )

    with pytest.raises(InvalidContentResponseError):
        provider.generate(build_request(content_type="reel"))


def test_openai_content_generator_normalizes_structured_reel_scripts() -> None:
    provider = OpenAIContentGenerator(
        openai_service=FakeOpenAIService(
            {
                "headline": "Annual wellness visits",
                "body": "Preventive care made simple.",
                "post": "A complete post.",
                "reel_script": {
                    "hook": "Annual visits can feel simple.",
                    "scenes": [
                        "Show a family arriving for a wellness visit.",
                        "Share one preventive care benefit.",
                    ],
                    "closing_line": "Schedule with Invictus Health.",
                },
                "caption": "A caption.",
                "hashtags": ["#PreventiveCare", "#WellnessVisit"],
                "call_to_action": "Book today.",
            }
        )  # type: ignore[arg-type]
    )

    content = provider.generate(build_request(content_type="reel"))

    assert content.reel_script is not None
    assert "Hook: Annual visits can feel simple." in content.reel_script
    assert "Scenes: Show a family arriving" in content.reel_script
    assert "Closing Line: Schedule with Invictus Health." in content.reel_script


def test_openai_content_generator_reports_missing_api_key() -> None:
    provider = OpenAIContentGenerator(
        openai_service=FakeOpenAIService(error=MissingOpenAIAPIKeyError())  # type: ignore[arg-type]
    )

    with pytest.raises(MissingOpenAIAPIKeyError):
        provider.generate(build_request())


def test_openai_content_generator_reports_invalid_payload() -> None:
    provider = OpenAIContentGenerator(
        openai_service=FakeOpenAIService({"post": "Missing required fields."})  # type: ignore[arg-type]
    )

    with pytest.raises(InvalidContentResponseError):
        provider.generate(build_request())
