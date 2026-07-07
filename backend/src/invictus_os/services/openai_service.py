from __future__ import annotations

from collections.abc import Callable
import hashlib
import json
import logging
import time
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from invictus_os.services.settings_service import OpenAIServiceConfig

logger = logging.getLogger(__name__)
_GLOBAL_OPENAI_CACHE: dict[str, dict[str, Any]] = {}


class OpenAIServiceError(Exception):
    message = "InvictusOS could not generate with OpenAI right now."


class MissingOpenAIAPIKeyError(OpenAIServiceError):
    message = "OpenAI API key is missing. Add it in Settings, save, and try again."


class InvalidOpenAIAPIKeyError(OpenAIServiceError):
    message = "OpenAI rejected the API key. Check the key in Settings and try again."


class OpenAIRateLimitError(OpenAIServiceError):
    message = "OpenAI is rate limiting requests. Please wait a moment and try again."


class OpenAIQuotaError(OpenAIServiceError):
    message = (
        "OpenAI says this API key has no available quota. Check billing, plan, or project limits, "
        "then try again."
    )


class OpenAINetworkError(OpenAIServiceError):
    message = "InvictusOS could not reach OpenAI. Check your internet connection and try again."


class InvalidOpenAIResponseError(OpenAIServiceError):
    message = "OpenAI returned an unexpected response. Please try again."


class OpenAIService:
    def __init__(
        self,
        *,
        config: OpenAIServiceConfig,
        client: OpenAI | None = None,
        cache: dict[str, dict[str, Any]] | None = None,
        sleep: Callable[[float], None] = time.sleep,
        max_retries: int = 2,
    ) -> None:
        self._config = config
        self._client = client
        self._cache = cache if cache is not None else _GLOBAL_OPENAI_CACHE
        self._sleep = sleep
        self._max_retries = max_retries

    def generate_json(self, *, system_prompt: str, user_payload: dict[str, Any], cache_namespace: str) -> dict[str, Any]:
        if not self._config.api_key:
            raise MissingOpenAIAPIKeyError

        cache_key = self._cache_key(
            namespace=cache_namespace,
            system_prompt=system_prompt,
            user_payload=user_payload,
        )
        if cache_key in self._cache:
            return self._cache[cache_key]

        output_text = self._create_response(system_prompt=system_prompt, user_payload=user_payload)

        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            logger.warning("OpenAI returned invalid JSON for %s", cache_namespace)
            raise InvalidOpenAIResponseError from exc

        if not isinstance(payload, dict):
            raise InvalidOpenAIResponseError

        self._cache[cache_key] = payload
        return payload

    def _create_response(self, *, system_prompt: str, user_payload: dict[str, Any]) -> str:
        client = self._client or OpenAI(api_key=self._config.api_key, timeout=30)
        last_error: Exception | None = None
        include_temperature = True

        for attempt in range(self._max_retries + 1):
            try:
                request_kwargs: dict[str, Any] = {
                    "model": self._config.model,
                    "input": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_payload)},
                    ],
                    "max_output_tokens": self._config.max_output_tokens,
                }
                if include_temperature:
                    request_kwargs["temperature"] = self._config.temperature

                response = client.responses.create(**request_kwargs)
                output_text = getattr(response, "output_text", "")
                if not output_text:
                    raise InvalidOpenAIResponseError
                return output_text
            except AuthenticationError as exc:
                logger.warning("OpenAI authentication failed: %s", safe_error_message(exc))
                raise InvalidOpenAIAPIKeyError from exc
            except RateLimitError as exc:
                if is_quota_error(exc):
                    logger.warning("OpenAI quota error: %s", safe_error_message(exc))
                    raise OpenAIQuotaError from exc
                last_error = exc
                logger.warning("OpenAI rate limit on attempt %s: %s", attempt + 1, safe_error_message(exc))
                if attempt == self._max_retries:
                    raise OpenAIRateLimitError from exc
            except (APIConnectionError, APITimeoutError) as exc:
                last_error = exc
                logger.warning("OpenAI network error on attempt %s: %s", attempt + 1, safe_error_message(exc))
                if attempt == self._max_retries:
                    raise OpenAINetworkError from exc
            except APIStatusError as exc:
                last_error = exc
                logger.warning("OpenAI API status error on attempt %s: %s", attempt + 1, safe_error_message(exc))
                if is_unsupported_temperature_error(exc) and include_temperature:
                    include_temperature = False
                    logger.info("Retrying OpenAI request without temperature for model %s", self._config.model)
                    continue
                if attempt == self._max_retries:
                    raise OpenAIServiceError from exc
            except OpenAIError as exc:
                logger.warning("OpenAI error: %s", safe_error_message(exc))
                raise OpenAIServiceError from exc

            self._sleep(backoff_seconds(attempt))

        if last_error:
            raise OpenAIServiceError from last_error
        raise OpenAIServiceError

    def _cache_key(self, *, namespace: str, system_prompt: str, user_payload: dict[str, Any]) -> str:
        stable_payload = json.dumps(
            {
                "namespace": namespace,
                "model": self._config.model,
                "temperature": self._config.temperature,
                "max_output_tokens": self._config.max_output_tokens,
                "system": system_prompt,
                "user": user_payload,
            },
            sort_keys=True,
        )
        return hashlib.sha256(stable_payload.encode("utf-8")).hexdigest()


def backoff_seconds(attempt: int) -> float:
    return min(0.5 * (2**attempt), 4.0)


def is_quota_error(exc: RateLimitError) -> bool:
    body = getattr(exc, "body", None)
    error = body.get("error") if isinstance(body, dict) else None
    body_code = error.get("code") if isinstance(error, dict) else None
    return getattr(exc, "code", None) == "insufficient_quota" or body_code == "insufficient_quota"


def is_unsupported_temperature_error(exc: APIStatusError) -> bool:
    body = getattr(exc, "body", None)
    error = body.get("error") if isinstance(body, dict) else None
    param = error.get("param") if isinstance(error, dict) else None
    message = error.get("message") if isinstance(error, dict) else str(exc)
    rendered = str(exc)
    return (
        (param == "temperature" and "Unsupported parameter" in str(message))
        or ("Unsupported parameter" in rendered and "temperature" in rendered)
    )


def safe_error_message(exc: Exception) -> str:
    message = str(exc)
    if "sk-" not in message:
        return message
    return message.replace("sk-", "sk-***")
