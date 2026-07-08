from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from collections.abc import Callable
from typing import Protocol

import httpx

from invictus_os.schemas.reel import ReelPackageResponse, ReelVideoResult

logger = logging.getLogger(__name__)


class VideoGenerationProvider(Protocol):
    def create_video(self, reel_package: ReelPackageResponse) -> ReelVideoResult:
        """Generate a social video for a completed reel package."""


class VideoGenerationError(Exception):
    message = "InvictusOS could not generate the reel video."


@dataclass(frozen=True)
class HiggsfieldMcpBridgeConfig:
    bridge_url: str | None
    timeout_seconds: float = 120.0
    max_retries: int = 2


class HiggsfieldMcpVideoProvider:
    provider_name = "higgsfield"

    def __init__(
        self,
        *,
        config: HiggsfieldMcpBridgeConfig,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._client = client
        self._sleep = sleep

    def create_video(self, reel_package: ReelPackageResponse) -> ReelVideoResult:
        if not self._config.bridge_url:
            return ReelVideoResult(
                status="not_configured",
                provider=self.provider_name,
                error_message=(
                    "Higgsfield video generation is not configured for this deployment. "
                    "Connect a server-side Higgsfield MCP bridge and retry."
                ),
                retryable=True,
            )

        try:
            payload = self._request_video(reel_package)
            video_url = extract_video_url(payload)
            return ReelVideoResult(
                status="completed",
                provider=self.provider_name,
                width=1080,
                height=1920,
                video_url=video_url,
                download_url=str(payload.get("download_url") or video_url),
                job_id=str(payload.get("job_id") or payload.get("id") or "") or None,
                retryable=False,
            )
        except VideoGenerationError as exc:
            logger.warning("Higgsfield video generation failed: %s", safe_message(exc))
            return ReelVideoResult(
                status="failed",
                provider=self.provider_name,
                error_message=exc.message,
                retryable=True,
            )

    def _request_video(self, reel_package: ReelPackageResponse) -> dict:
        request_payload = {
            "tool": "higgsfield.generate_video",
            "params": {
                "model": "kling3_0_turbo",
                "prompt": build_higgsfield_video_prompt(reel_package),
                "aspect_ratio": "9:16",
                "width": 1080,
                "height": 1920,
                "duration": reel_package.duration_seconds,
                "script": reel_package.voice_over_script,
                "storyboard": [scene.model_dump(mode="json") for scene in reel_package.storyboard],
                "output_format": "mp4",
            },
        }
        last_error: Exception | None = None

        for attempt in range(self._config.max_retries + 1):
            try:
                client = self._client or httpx.Client(timeout=self._config.timeout_seconds)
                response = client.post(self._config.bridge_url, json=request_payload)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise VideoGenerationError
                return payload
            except (httpx.HTTPError, ValueError, VideoGenerationError) as exc:
                last_error = exc
                if attempt == self._config.max_retries:
                    raise VideoGenerationError from exc
                self._sleep(min(1.0 * (2**attempt), 8.0))

        raise VideoGenerationError from last_error


def build_higgsfield_video_prompt(reel_package: ReelPackageResponse) -> str:
    scene_prompts = "\n".join(
        f"Scene {scene.scene_number}: {scene.higgsfield_prompt}" for scene in reel_package.storyboard
    )
    return (
        "Create a finished vertical 1080x1920 MP4 social media reel for Invictus Wellness. "
        "Use modern healthcare branding, white backgrounds, blue and green accents, clean typography, "
        "strong hierarchy, mobile-first composition, natural light, and professional pacing. "
        "Include synchronized voice-over and tasteful on-screen text. "
        f"Hook: {reel_package.hook}\n"
        f"Voice-over script: {reel_package.voice_over_script}\n"
        f"{scene_prompts}"
    )


def extract_video_url(payload: dict) -> str:
    candidates = [
        payload.get("video_url"),
        payload.get("mp4_url"),
        payload.get("download_url"),
        payload.get("url"),
    ]
    results = payload.get("results")
    if isinstance(results, list):
        for result in results:
            if isinstance(result, dict):
                candidates.extend(
                    [
                        result.get("video_url"),
                        result.get("mp4_url"),
                        result.get("download_url"),
                        result.get("url"),
                    ]
                )

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.startswith("https://"):
            return candidate

    raise VideoGenerationError


def safe_message(exc: Exception) -> str:
    message = str(exc)
    return message.replace("sk-", "sk-***")
