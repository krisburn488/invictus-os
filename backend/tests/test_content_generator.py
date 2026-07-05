import json

import httpx
import pytest
from openai import RateLimitError
from pydantic import BaseModel

from invictus_os.schemas.content import ContentGenerationRequest
from invictus_os.services.content_generator import (
    InvalidContentResponseError,
    MissingOpenAIAPIKeyError,
    OpenAIContentGenerator,
    OpenAIQuotaError,
    OpenAIRateLimitError,
)


class FakeResponse(BaseModel):
    output_text: str


class FakeResponses:
    def __init__(self, output_text: str | None = None, error: Exception | None = None) -> None:
        self.output_text = output_text
        self.error = error

    def create(self, **_: object) -> FakeResponse:
        if self.error:
            raise self.error

        return FakeResponse(output_text=self.output_text or "")


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def build_request(content_type: str = "post") -> ContentGenerationRequest:
    return ContentGenerationRequest(
        business_name="Invictus Health",
        target_audience="busy families looking for preventive care",
        topic="annual wellness visits",
        platform="instagram",
        content_type=content_type,  # type: ignore[arg-type]
    )


def build_rate_limit_error(*, code: str | None = None) -> RateLimitError:
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    response = httpx.Response(status_code=429, request=request)
    body = {"error": {"code": code}} if code else None
    return RateLimitError("rate limited", response=response, body=body)


def test_openai_content_generator_returns_valid_content() -> None:
    provider = OpenAIContentGenerator(
        api_key="test-key",
        model="gpt-5.5",
        timeout_seconds=30,
        client=FakeClient(
            FakeResponses(
                json.dumps(
                    {
                        "post": "Annual wellness visits help families stay proactive.",
                        "reel_script": None,
                        "caption": "Make preventive care easier to prioritize.",
                        "hashtags": ["#PreventiveCare", "#FamilyHealth"],
                        "call_to_action": "Schedule a wellness visit today.",
                    }
                )
            )
        ),  # type: ignore[arg-type]
    )

    content = provider.generate(build_request())

    assert content.post == "Annual wellness visits help families stay proactive."
    assert content.reel_script is None
    assert content.hashtags == ["#PreventiveCare", "#FamilyHealth"]


def test_openai_content_generator_requires_reel_script_for_reels() -> None:
    provider = OpenAIContentGenerator(
        api_key="test-key",
        model="gpt-5.5",
        timeout_seconds=30,
        client=FakeClient(
            FakeResponses(
                json.dumps(
                    {
                        "post": "A short post.",
                        "reel_script": None,
                        "caption": "A caption.",
                        "hashtags": ["#Health"],
                        "call_to_action": "Book today.",
                    }
                )
            )
        ),  # type: ignore[arg-type]
    )

    with pytest.raises(InvalidContentResponseError):
        provider.generate(build_request(content_type="reel"))


def test_openai_content_generator_normalizes_structured_reel_scripts() -> None:
    provider = OpenAIContentGenerator(
        api_key="test-key",
        model="gpt-5.5",
        timeout_seconds=30,
        client=FakeClient(
            FakeResponses(
                json.dumps(
                    {
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
                )
            )
        ),  # type: ignore[arg-type]
    )

    content = provider.generate(build_request(content_type="reel"))

    assert content.reel_script is not None
    assert "Hook: Annual visits can feel simple." in content.reel_script
    assert "Scenes: Show a family arriving" in content.reel_script
    assert "Closing Line: Schedule with Invictus Health." in content.reel_script


def test_openai_content_generator_reports_missing_api_key() -> None:
    provider = OpenAIContentGenerator(api_key=None, model="gpt-5.5", timeout_seconds=30)

    with pytest.raises(MissingOpenAIAPIKeyError):
        provider.generate(build_request())


def test_openai_content_generator_reports_invalid_json() -> None:
    provider = OpenAIContentGenerator(
        api_key="test-key",
        model="gpt-5.5",
        timeout_seconds=30,
        client=FakeClient(FakeResponses("not json")),  # type: ignore[arg-type]
    )

    with pytest.raises(InvalidContentResponseError):
        provider.generate(build_request())


def test_openai_content_generator_reports_rate_limits() -> None:
    provider = OpenAIContentGenerator(
        api_key="test-key",
        model="gpt-5.5",
        timeout_seconds=30,
        client=FakeClient(FakeResponses(error=build_rate_limit_error())),  # type: ignore[arg-type]
    )

    with pytest.raises(OpenAIRateLimitError):
        provider.generate(build_request())


def test_openai_content_generator_reports_quota_errors() -> None:
    provider = OpenAIContentGenerator(
        api_key="test-key",
        model="gpt-5.5",
        timeout_seconds=30,
        client=FakeClient(
            FakeResponses(error=build_rate_limit_error(code="insufficient_quota"))
        ),  # type: ignore[arg-type]
    )

    with pytest.raises(OpenAIQuotaError):
        provider.generate(build_request())
