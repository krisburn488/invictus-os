import re

from pydantic import ValidationError

from invictus_os.schemas.reel import (
    ReelFormat,
    ReelPackageRequest,
    ReelPackageResponse,
    ReelStoryboardScene,
)
from invictus_os.services.openai_service import InvalidOpenAIResponseError, OpenAIService, OpenAIServiceError


class ReelServiceError(Exception):
    message = "InvictusOS could not create today's reel package."


class ReelService:
    def __init__(self, *, openai_service: OpenAIService) -> None:
        self._openai = openai_service

    def create_package(self, request: ReelPackageRequest) -> ReelPackageResponse:
        try:
            payload = self._openai.generate_json(
                system_prompt=reel_system_prompt(),
                user_payload={
                    "reel_format": request.reel_format,
                    "content": request.content.model_dump(mode="json"),
                    "duration_requirement": "30 to 45 seconds",
                    "brand": "Invictus Wellness",
                },
                cache_namespace="reel",
            )
            storyboard = [
                ReelStoryboardScene.model_validate(scene)
                for scene in payload.get("storyboard", [])
            ]
            hook = clean_text(str(payload.get("hook", "")))
            script = clean_text(str(payload.get("script", "")))
            voice_over_script = clean_text(str(payload.get("voice_over_script", "")))
            caption = clean_text(str(payload.get("caption", "")))
            hashtags = normalize_hashtags(payload.get("hashtags", []))
            duration_seconds = int(payload.get("duration_seconds") or sum(scene.duration_seconds for scene in storyboard))
            on_screen_text = payload.get("on_screen_text") or [scene.on_screen_text for scene in storyboard]
            on_screen_text = [clean_text(str(item)) for item in on_screen_text if clean_text(str(item))]
        except (InvalidOpenAIResponseError, OpenAIServiceError, ValidationError, TypeError, ValueError) as exc:
            raise ReelServiceError from exc

        markdown = build_markdown(
            hook=hook,
            script=script,
            storyboard=storyboard,
            on_screen_text=on_screen_text,
            voice_over_script=voice_over_script,
            caption=caption,
            hashtags=hashtags,
            reel_format=request.reel_format,
            duration_seconds=duration_seconds,
        )

        try:
            return ReelPackageResponse(
                hook=hook,
                script=script,
                storyboard=storyboard,
                on_screen_text=on_screen_text,
                voice_over_script=voice_over_script,
                caption=caption,
                hashtags=hashtags,
                reel_format=request.reel_format,
                duration_seconds=duration_seconds,
                markdown=markdown,
            )
        except ValidationError as exc:
            raise ReelServiceError from exc


def reel_system_prompt() -> str:
    return (
        "You create complete healthcare social media reel packages for InvictusOS. "
        "Generate a professional 30 to 45 second reel using the provided content. "
        "Maintain Invictus Wellness branding: modern healthcare aesthetic, white backgrounds, "
        "blue and green accents, clean typography, warm trustworthy tone, mobile-first 9:16 framing. "
        "Do not invent clinical statistics, outcomes, testimonials, or medical guarantees. "
        "Return only valid JSON with exactly these keys: hook, script, storyboard, on_screen_text, "
        "voice_over_script, caption, hashtags, duration_seconds. storyboard must contain 4 scenes. "
        "Each storyboard scene must include scene_number, duration_seconds, visual_direction, "
        "on_screen_text, voice_over, and higgsfield_prompt. Each Higgsfield prompt must be ready "
        "for vertical 9:16 video generation and mention Invictus Wellness visual branding. "
        "duration_seconds must be between 30 and 45."
    )


def build_hook(post: str, caption: str) -> str:
    source = clean_text(post) or clean_text(caption)
    first_sentence = re.split(r"(?<=[.!?])\s+", source, maxsplit=1)[0]
    first_sentence = first_sentence.rstrip(".!?")
    return truncate(f"{first_sentence}?", 96)


def build_key_message(post: str) -> str:
    sentences = split_sentences(post)
    if len(sentences) > 1:
        return truncate(sentences[1], 160)
    return truncate(sentences[0], 160)


def build_proof_point(caption: str, post: str) -> str:
    source = clean_text(caption) or clean_text(post)
    return truncate(source, 160)


def build_storyboard(
    *,
    reel_format: ReelFormat,
    hook: str,
    key_message: str,
    proof_point: str,
    action: str,
) -> list[ReelStoryboardScene]:
    visual_templates = {
        "talking_head": [
            "Clinician or wellness guide speaks directly to camera in a bright modern healthcare office.",
            "Medium close-up with calm hand gestures and subtle blue-green brand accents in the background.",
            "Cut to friendly direct-to-camera delivery with a concise practical takeaway.",
            "Confident closing shot, soft daylight, clear space for captions and CTA.",
        ],
        "ai_avatar": [
            "Professional AI avatar presenter in a clean white studio with blue-green wellness accents.",
            "AI avatar shifts to an educational explainer pose beside simple healthcare icons.",
            "AI avatar delivers a reassuring practical tip with a calm, trustworthy expression.",
            "AI avatar closes with a direct call to action and polished brand-safe framing.",
        ],
        "b_roll": [
            "Bright lifestyle B-roll of a person preparing for a wellness visit, clean healthcare setting.",
            "B-roll montage of calendar reminders, intake forms, and welcoming clinic details.",
            "Close-up B-roll of supportive care moments, hands taking notes, warm natural light.",
            "Final B-roll hero shot with clear negative space for call-to-action text.",
        ],
    }

    beats = [
        (1, 8, hook, hook),
        (2, 10, "Why it matters", key_message),
        (3, 10, "Simple next step", proof_point),
        (4, 9, "Take action today", action),
    ]
    scenes: list[ReelStoryboardScene] = []

    for index, duration, on_screen_text, voice_over in beats:
        visual_direction = visual_templates[reel_format][index - 1]
        scenes.append(
            ReelStoryboardScene(
                scene_number=index,
                duration_seconds=duration,
                visual_direction=visual_direction,
                on_screen_text=truncate(on_screen_text, 72),
                voice_over=truncate(voice_over, 220),
                higgsfield_prompt=build_higgsfield_prompt(
                    reel_format=reel_format,
                    visual_direction=visual_direction,
                    on_screen_text=on_screen_text,
                    voice_over=voice_over,
                ),
            )
        )

    return scenes


def build_higgsfield_prompt(
    *,
    reel_format: ReelFormat,
    visual_direction: str,
    on_screen_text: str,
    voice_over: str,
) -> str:
    format_instruction = {
        "talking_head": "talking-head healthcare creator video",
        "ai_avatar": "AI avatar presenter video",
        "b_roll": "cinematic healthcare B-roll video",
    }[reel_format]
    return (
        f"Create a vertical 9:16 {format_instruction}. {visual_direction} "
        "Use Invictus Wellness branding with white backgrounds, blue and green accents, "
        "professional typography, natural light, clean composition, and mobile-first framing. "
        f"On-screen text: \"{clean_text(on_screen_text)}\". "
        f"Voice-over: \"{clean_text(voice_over)}\"."
    )


def build_script(storyboard: list[ReelStoryboardScene]) -> str:
    return "\n\n".join(
        f"Scene {scene.scene_number} ({scene.duration_seconds}s): {scene.voice_over}"
        for scene in storyboard
    )


def build_caption(caption: str, action: str) -> str:
    caption_text = clean_text(caption)
    if action.lower() in caption_text.lower():
        return caption_text
    return f"{caption_text} {action}".strip()


def build_markdown(
    *,
    hook: str,
    script: str,
    storyboard: list[ReelStoryboardScene],
    on_screen_text: list[str],
    voice_over_script: str,
    caption: str,
    hashtags: list[str],
    reel_format: ReelFormat,
    duration_seconds: int,
) -> str:
    scene_sections = "\n\n".join(
        (
            f"### Scene {scene.scene_number} ({scene.duration_seconds}s)\n"
            f"- Visual: {scene.visual_direction}\n"
            f"- On-screen text: {scene.on_screen_text}\n"
            f"- Voice-over: {scene.voice_over}\n"
            f"- Higgsfield prompt: {scene.higgsfield_prompt}"
        )
        for scene in storyboard
    )
    text_lines = "\n".join(f"- {line}" for line in on_screen_text)
    hashtag_line = " ".join(hashtags)

    return (
        "# Today's Reel Package\n\n"
        f"- Format: {format_label(reel_format)}\n"
        f"- Duration: {duration_seconds} seconds\n\n"
        f"## Hook\n{hook}\n\n"
        f"## 30-45 Second Script\n{script}\n\n"
        f"## Storyboard\n{scene_sections}\n\n"
        f"## On-Screen Text\n{text_lines}\n\n"
        f"## Voice-Over Script\n{voice_over_script}\n\n"
        f"## Caption\n{caption}\n\n"
        f"## Hashtags\n{hashtag_line}\n"
    )


def normalize_hashtags(hashtags: object) -> list[str]:
    if not isinstance(hashtags, list):
        hashtags = []
    normalized = []
    for hashtag in hashtags[:12]:
        value = clean_text(hashtag)
        if not value:
            continue
        normalized.append(value if value.startswith("#") else f"#{value}")
    return normalized or ["#InvictusWellness"]


def split_sentences(value: str) -> list[str]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", clean_text(value)) if part.strip()]
    return sentences or [clean_text(value)]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def format_label(reel_format: ReelFormat) -> str:
    return {
        "talking_head": "Talking head",
        "ai_avatar": "AI avatar",
        "b_roll": "B-roll",
    }[reel_format]
