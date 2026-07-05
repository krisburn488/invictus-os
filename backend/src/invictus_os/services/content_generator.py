import json
from typing import Protocol

from openai import APIConnectionError, APITimeoutError, OpenAI, OpenAIError, RateLimitError
from pydantic import ValidationError

from invictus_os.schemas.content import ContentGenerationRequest, GeneratedContentResponse


class ContentGenerationError(Exception):
    message = "Content could not be generated right now."


class MissingOpenAIAPIKeyError(ContentGenerationError):
    message = "OpenAI API key is missing. Add OPENAI_API_KEY to backend/.env and restart the backend."


class OpenAIRateLimitError(ContentGenerationError):
    message = "OpenAI is rate limiting requests. Please wait a moment and try again."


class OpenAIQuotaError(ContentGenerationError):
    message = (
        "OpenAI says this API key has no available quota. Check your OpenAI billing, plan, "
        "or project limits, then try again."
    )


class OpenAINetworkError(ContentGenerationError):
    message = "InvictusOS could not reach OpenAI. Check your internet connection and try again."


class InvalidContentResponseError(ContentGenerationError):
    message = "OpenAI returned an unexpected response. Please try generating the content again."


class ContentGenerator(Protocol):
    def generate(self, request: ContentGenerationRequest) -> GeneratedContentResponse:
        raise NotImplementedError


def is_quota_error(exc: RateLimitError) -> bool:
    body = getattr(exc, "body", None)
    error = body.get("error") if isinstance(body, dict) else None
    body_code = error.get("code") if isinstance(error, dict) else None
    return getattr(exc, "code", None) == "insufficient_quota" or body_code == "insufficient_quota"


class OpenAIContentGenerator:
    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        timeout_seconds: float,
        client: OpenAI | None = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._client = client

    def generate(self, request: ContentGenerationRequest) -> GeneratedContentResponse:
        if not self._api_key:
            raise MissingOpenAIAPIKeyError

        client = self._client or OpenAI(api_key=self._api_key, timeout=self._timeout_seconds)

        try:
            response = client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "system",
                        "content": self._system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "business_name": request.business_name,
                                "target_audience": request.target_audience,
                                "topic": request.topic,
                                "platform": request.platform,
                                "content_type": request.content_type,
                            }
                        ),
                    },
                ],
            )
        except RateLimitError as exc:
            if is_quota_error(exc):
                raise OpenAIQuotaError from exc
            raise OpenAIRateLimitError from exc
        except (APIConnectionError, APITimeoutError) as exc:
            raise OpenAINetworkError from exc
        except OpenAIError as exc:
            raise ContentGenerationError from exc

        return self._parse_response(response.output_text, request.content_type)

    def _parse_response(self, output_text: str, content_type: str) -> GeneratedContentResponse:
        try:
            payload = json.loads(output_text)
            content = GeneratedContentResponse.model_validate(payload)
        except (json.JSONDecodeError, TypeError, ValidationError) as exc:
            raise InvalidContentResponseError from exc

        if content_type != "reel":
            content.reel_script = None
        elif not content.reel_script:
            raise InvalidContentResponseError

        return content

    def _system_prompt(self) -> str:
        return (
            "You generate professional healthcare marketing content for InvictusOS. "
            "Write natural, engaging, evidence-informed copy for ethical healthcare promotion. "
            "Do not invent statistics, clinical outcomes, credentials, testimonials, diagnoses, "
            "or treatment guarantees. Avoid fear-based claims and unsafe medical advice. "
            "Use clear, warm language appropriate for healthcare organizations and wellness "
            "businesses. Return only valid JSON with exactly these keys: post, reel_script, "
            "caption, hashtags, call_to_action. The hashtags value must be an array of strings. "
            "If content_type is not reel, set reel_script to null. If content_type is reel, "
            "include a complete reel script with hook, scenes, on-screen text, and closing line."
        )
