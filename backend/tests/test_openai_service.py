import json

import httpx
import pytest
from openai import APIConnectionError, AuthenticationError
from pydantic import BaseModel

from invictus_os.services.openai_service import (
    InvalidOpenAIAPIKeyError,
    MissingOpenAIAPIKeyError,
    OpenAIService,
)
from invictus_os.services.settings_service import OpenAIServiceConfig


class FakeResponse(BaseModel):
    output_text: str


class FakeResponses:
    def __init__(self, outputs: list[str], errors: list[Exception] | None = None) -> None:
        self.outputs = outputs
        self.errors = errors or []
        self.calls = 0

    def create(self, **_: object) -> FakeResponse:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return FakeResponse(output_text=self.outputs.pop(0))


class FakeClient:
    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def build_config(api_key: str = "sk-test-key") -> OpenAIServiceConfig:
    return OpenAIServiceConfig(
        api_key=api_key,
        model="gpt-5.5",
        temperature=0.7,
        max_output_tokens=1800,
    )


def test_openai_service_caches_identical_requests() -> None:
    responses = FakeResponses([json.dumps({"value": "generated"})])
    service = OpenAIService(
        config=build_config(),
        client=FakeClient(responses),  # type: ignore[arg-type]
        cache={},
        sleep=lambda _: None,
    )

    first = service.generate_json(system_prompt="system", user_payload={"topic": "x"}, cache_namespace="test")
    second = service.generate_json(system_prompt="system", user_payload={"topic": "x"}, cache_namespace="test")

    assert first == {"value": "generated"}
    assert second == {"value": "generated"}
    assert responses.calls == 1


def test_openai_service_retries_network_errors() -> None:
    responses = FakeResponses(
        [json.dumps({"value": "generated"})],
        errors=[APIConnectionError(request=httpx.Request("POST", "https://api.openai.com/v1/responses"))],
    )
    service = OpenAIService(
        config=build_config(),
        client=FakeClient(responses),  # type: ignore[arg-type]
        cache={},
        sleep=lambda _: None,
    )

    result = service.generate_json(system_prompt="system", user_payload={"topic": "x"}, cache_namespace="test")

    assert result == {"value": "generated"}
    assert responses.calls == 2


def test_openai_service_requires_api_key() -> None:
    service = OpenAIService(config=build_config(api_key=""), sleep=lambda _: None)

    with pytest.raises(MissingOpenAIAPIKeyError):
        service.generate_json(system_prompt="system", user_payload={"topic": "x"}, cache_namespace="test")


def test_openai_service_reports_invalid_api_key() -> None:
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    response = httpx.Response(status_code=401, request=request)
    auth_error = AuthenticationError("invalid api key", response=response, body={"error": {}})
    responses = FakeResponses([], errors=[auth_error])
    service = OpenAIService(
        config=build_config(),
        client=FakeClient(responses),  # type: ignore[arg-type]
        cache={},
        sleep=lambda _: None,
    )

    with pytest.raises(InvalidOpenAIAPIKeyError):
        service.generate_json(system_prompt="system", user_payload={"topic": "x"}, cache_namespace="test")
