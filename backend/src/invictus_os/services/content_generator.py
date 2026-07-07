from typing import Protocol

from pydantic import ValidationError

from invictus_os.schemas.content import ContentGenerationRequest, GeneratedContentResponse
from invictus_os.services.openai_service import (
    InvalidOpenAIAPIKeyError,
    InvalidOpenAIResponseError,
    MissingOpenAIAPIKeyError,
    OpenAINetworkError,
    OpenAIQuotaError,
    OpenAIRateLimitError,
    OpenAIService,
    OpenAIServiceError,
)


class ContentGenerationError(Exception):
    message = "Content could not be generated right now."


class InvalidContentResponseError(ContentGenerationError):
    message = "OpenAI returned an unexpected content response. Please try generating again."


class ContentGenerator(Protocol):
    def generate(self, request: ContentGenerationRequest) -> GeneratedContentResponse:
        raise NotImplementedError


class OpenAIContentGenerator:
    def __init__(self, *, openai_service: OpenAIService) -> None:
        self._openai = openai_service

    def generate(self, request: ContentGenerationRequest) -> GeneratedContentResponse:
        try:
            payload = self._openai.generate_json(
                system_prompt=content_system_prompt(),
                user_payload={
                    "business_name": request.business_name,
                    "target_audience": request.target_audience,
                    "topic": request.topic,
                    "platform": request.platform,
                    "content_type": request.content_type,
                },
                cache_namespace="content",
            )
            payload["post"] = stringify_content(payload.get("post"))
            payload["reel_script"] = stringify_content(payload.get("reel_script"))
            payload["caption"] = stringify_content(payload.get("caption"))
            payload["call_to_action"] = stringify_content(payload.get("call_to_action"))
            payload["headline"] = stringify_content(payload.get("headline"))
            payload["body"] = stringify_content(payload.get("body"))
            content = GeneratedContentResponse.model_validate(payload)
        except (InvalidOpenAIResponseError, ValidationError, TypeError) as exc:
            raise InvalidContentResponseError from exc
        except (
            MissingOpenAIAPIKeyError,
            InvalidOpenAIAPIKeyError,
            OpenAIRateLimitError,
            OpenAIQuotaError,
            OpenAINetworkError,
        ):
            raise
        except OpenAIServiceError as exc:
            raise ContentGenerationError from exc

        if request.content_type != "reel":
            content.reel_script = None
        elif not content.reel_script:
            raise InvalidContentResponseError

        return content


def stringify_content(value: object) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        sections = [stringify_content(item) for item in value]
        return "\n\n".join(section for section in sections if section)

    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            section = stringify_content(item)
            if section:
                title = str(key).replace("_", " ").title()
                lines.append(f"{title}: {section}")
        return "\n\n".join(lines)

    return str(value)


def content_system_prompt() -> str:
    return (
        "You generate professional healthcare marketing content for InvictusOS. "
        "Write natural, engaging, evidence-informed copy for ethical healthcare promotion. "
        "Do not invent statistics, clinical outcomes, credentials, testimonials, diagnoses, "
        "or treatment guarantees. Avoid fear-based claims and unsafe medical advice. "
        "Maintain Invictus Wellness branding: modern, warm, professional, white-space friendly, "
        "with blue and green wellness positioning. Return only valid JSON with exactly these keys: "
        "headline, body, post, reel_script, caption, hashtags, call_to_action. "
        "headline should be concise and graphic-ready. body should be a clear supporting message. "
        "post should be a complete social media post. caption should be platform-ready. "
        "hashtags must be an array of 5 to 12 relevant strings. call_to_action must be direct. "
        "If content_type is not reel, set reel_script to null. If content_type is reel, include a "
        "complete reel script with hook, scenes, on-screen text, and closing line."
    )
