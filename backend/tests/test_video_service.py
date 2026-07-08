import httpx

from invictus_os.schemas.reel import ReelPackageResponse, ReelStoryboardScene
from invictus_os.services.video_service import (
    HiggsfieldMcpBridgeConfig,
    HiggsfieldMcpVideoProvider,
    build_higgsfield_video_prompt,
)


class FakeBridgeClient:
    def __init__(self, responses: list[httpx.Response | Exception]) -> None:
        self.responses = responses
        self.calls = 0

    def post(self, *_: object, **__: object) -> httpx.Response:
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def build_reel_package() -> ReelPackageResponse:
    storyboard = [
        ReelStoryboardScene(
            scene_number=1,
            duration_seconds=8,
            visual_direction="Bright healthcare opening shot.",
            on_screen_text="Annual wellness visits",
            voice_over="Annual wellness visits can help.",
            higgsfield_prompt="Create a vertical 9:16 healthcare reel.",
        )
    ]
    return ReelPackageResponse(
        hook="Annual wellness visits can help.",
        script="Scene 1: Annual wellness visits can help.",
        storyboard=storyboard,
        on_screen_text=["Annual wellness visits"],
        voice_over_script="Annual wellness visits can help.",
        caption="Preventive care starts with a visit.",
        hashtags=["#InvictusWellness"],
        reel_format="talking_head",
        duration_seconds=30,
        markdown="# Reel",
    )


def test_higgsfield_provider_reports_not_configured_without_bridge_url() -> None:
    provider = HiggsfieldMcpVideoProvider(
        config=HiggsfieldMcpBridgeConfig(bridge_url=None),
        sleep=lambda _: None,
    )

    result = provider.create_video(build_reel_package())

    assert result.status == "not_configured"
    assert result.retryable is True
    assert "Higgsfield" in str(result.error_message)


def test_higgsfield_provider_maps_completed_video_response() -> None:
    request = httpx.Request("POST", "https://bridge.example.com/higgsfield")
    client = FakeBridgeClient(
        [
            httpx.Response(
                status_code=200,
                json={
                    "job_id": "job_123",
                    "video_url": "https://cdn.example.com/reel.mp4",
                },
                request=request,
            )
        ]
    )
    provider = HiggsfieldMcpVideoProvider(
        config=HiggsfieldMcpBridgeConfig(bridge_url="https://bridge.example.com/higgsfield"),
        client=client,  # type: ignore[arg-type]
        sleep=lambda _: None,
    )

    result = provider.create_video(build_reel_package())

    assert result.status == "completed"
    assert result.video_url == "https://cdn.example.com/reel.mp4"
    assert result.download_url == "https://cdn.example.com/reel.mp4"
    assert result.job_id == "job_123"
    assert client.calls == 1


def test_higgsfield_provider_retries_transient_bridge_errors() -> None:
    request = httpx.Request("POST", "https://bridge.example.com/higgsfield")
    client = FakeBridgeClient(
        [
            httpx.ConnectError("temporary", request=request),
            httpx.Response(
                status_code=200,
                json={"url": "https://cdn.example.com/retry.mp4"},
                request=request,
            ),
        ]
    )
    provider = HiggsfieldMcpVideoProvider(
        config=HiggsfieldMcpBridgeConfig(bridge_url="https://bridge.example.com/higgsfield"),
        client=client,  # type: ignore[arg-type]
        sleep=lambda _: None,
    )

    result = provider.create_video(build_reel_package())

    assert result.status == "completed"
    assert result.video_url == "https://cdn.example.com/retry.mp4"
    assert client.calls == 2


def test_higgsfield_prompt_targets_vertical_mp4() -> None:
    prompt = build_higgsfield_video_prompt(build_reel_package())

    assert "1080x1920" in prompt
    assert "MP4" in prompt
    assert "Invictus Wellness" in prompt
