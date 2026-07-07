from html import escape
import re
import textwrap

from invictus_os.schemas.design import (
    DesignGraphicRequest,
    DesignGraphicResponse,
    DesignSlide,
    GeneratedDesignCopy,
    GraphicType,
)
from invictus_os.services.openai_service import InvalidOpenAIResponseError, OpenAIService, OpenAIServiceError


class DesignServiceError(Exception):
    message = "InvictusOS could not create the design."


class DesignService:
    def __init__(self, *, openai_service: OpenAIService) -> None:
        self._openai = openai_service

    def create_graphic(self, request: DesignGraphicRequest) -> DesignGraphicResponse:
        extracted_content = self.extract_design_copy(request)
        slides = build_design_slides(request.graphic_type, extracted_content)

        return DesignGraphicResponse(
            status="created",
            graphic_type=request.graphic_type,
            extracted_content=extracted_content,
            message="InvictusOS created a finished 1080x1350 graphic ready for PNG download.",
            slides=slides,
        )

    def extract_design_copy(self, request: DesignGraphicRequest) -> GeneratedDesignCopy:
        try:
            payload = self._openai.generate_json(
                system_prompt=design_system_prompt(),
                user_payload={
                    "graphic_type": request.graphic_type,
                    "content": request.content.model_dump(mode="json"),
                    "brand": "Invictus Wellness",
                    "dimensions": "1080x1350 portrait",
                },
                cache_namespace="design",
            )
            return GeneratedDesignCopy.model_validate(
                {
                    "headline": stringify_design_value(payload.get("headline")),
                    "body_text": stringify_design_value(payload.get("body_text") or payload.get("body")),
                    "call_to_action": stringify_design_value(
                        payload.get("call_to_action") or request.content.call_to_action
                    ),
                }
            )
        except (InvalidOpenAIResponseError, OpenAIServiceError, ValueError, TypeError) as exc:
            raise DesignServiceError from exc


def extract_design_copy(request: DesignGraphicRequest) -> GeneratedDesignCopy:
    content = request.content
    headline = extract_headline(content.post, content.caption, request.graphic_type)
    body = extract_body_text(content.post, content.caption, request.graphic_type)

    return GeneratedDesignCopy(
        headline=headline,
        body_text=body,
        call_to_action=truncate(clean_text(content.call_to_action), 140),
    )


def stringify_design_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return truncate(clean_text(value), 420)
    return truncate(clean_text(str(value)), 420)


def design_system_prompt() -> str:
    return (
        "You create structured graphic specifications for InvictusOS social graphics. "
        "Use the provided generated content and produce concise copy for a finished "
        "1080x1350 Instagram/Facebook graphic. Maintain Invictus Wellness branding: modern "
        "healthcare aesthetic, white backgrounds, blue and green accents, professional "
        "typography, strong hierarchy, mobile-first. Do not invent clinical claims. "
        "Return only valid JSON with exactly these keys: headline, body_text, call_to_action. "
        "headline should fit a mobile graphic. body_text should support the headline in one "
        "or two short sentences. call_to_action should be direct and action oriented."
    )


def extract_headline(post: str, caption: str, graphic_type: GraphicType) -> str:
    if graphic_type == "quote":
        quoted = re.findall(r'"([^"]+)"', post)
        if quoted:
            return truncate(clean_text(quoted[0]), 96)

    first_sentence = re.split(r"(?<=[.!?])\s+", clean_text(post), maxsplit=1)[0]
    if len(first_sentence) < 24:
        first_sentence = clean_text(caption) or first_sentence

    return truncate(first_sentence, 96)


def extract_body_text(post: str, caption: str, graphic_type: GraphicType) -> str:
    source = caption if graphic_type == "quote" else post
    paragraphs = [clean_text(part) for part in source.split("\n") if clean_text(part)]
    body = " ".join(paragraphs[1:] or paragraphs)
    return truncate(body or clean_text(caption), 420)


def build_design_slides(
    graphic_type: GraphicType,
    content: GeneratedDesignCopy,
) -> list[DesignSlide]:
    if graphic_type == "carousel":
        return [
            create_slide(
                slide_id="carousel-cover",
                title="Carousel Cover",
                eyebrow="Invictus Wellness",
                headline=content.headline,
                body=content.body_text,
                cta=content.call_to_action,
                variant="cover",
                page_label="01 / 03",
            ),
            create_slide(
                slide_id="carousel-detail",
                title="Carousel Detail",
                eyebrow="Care guidance",
                headline="What to know today",
                body=content.body_text,
                cta=content.call_to_action,
                variant="detail",
                page_label="02 / 03",
            ),
            create_slide(
                slide_id="carousel-action",
                title="Carousel Action",
                eyebrow="Next step",
                headline=content.call_to_action,
                body="Save this reminder and share it with someone who is ready to take a practical step toward better everyday wellness.",
                cta="Invictus Wellness",
                variant="action",
                page_label="03 / 03",
            ),
        ]

    if graphic_type == "quote":
        return [
            create_slide(
                slide_id="quote-graphic",
                title="Quote Graphic",
                eyebrow="Invictus Wellness",
                headline=content.headline,
                body=content.body_text,
                cta=content.call_to_action,
                variant="quote",
                page_label="Quote",
            )
        ]

    return [
        create_slide(
            slide_id="single-post",
            title="Single Post",
            eyebrow="Invictus Wellness",
            headline=content.headline,
            body=content.body_text,
            cta=content.call_to_action,
            variant="cover",
            page_label="Social Post",
        )
    ]


def create_slide(
    *,
    slide_id: str,
    title: str,
    eyebrow: str,
    headline: str,
    body: str,
    cta: str,
    variant: str,
    page_label: str,
) -> DesignSlide:
    svg = render_svg(
        eyebrow=eyebrow,
        headline=headline,
        body=body,
        cta=cta,
        variant=variant,
        page_label=page_label,
    )
    return DesignSlide(id=slide_id, title=title, svg=svg)


def render_svg(
    *,
    eyebrow: str,
    headline: str,
    body: str,
    cta: str,
    variant: str,
    page_label: str,
) -> str:
    headline_lines = wrap_svg_text(headline, width=19, max_lines=4)
    body_lines = wrap_svg_text(body, width=35, max_lines=6)
    cta_lines = wrap_svg_text(cta, width=30, max_lines=2)

    accent = {
        "cover": "#2f6f73",
        "detail": "#247a52",
        "action": "#24585c",
        "quote": "#2f6f73",
    }.get(variant, "#2f6f73")
    secondary = "#9fc7bd" if variant != "action" else "#b8d9ce"
    quote_mark = (
        '<text x="95" y="320" fill="#d9eee8" font-size="220" '
        'font-family="Georgia, serif" font-weight="700">“</text>'
        if variant == "quote"
        else ""
    )

    headline_svg = svg_text_lines(
        headline_lines,
        x=92,
        y=430 if variant == "quote" else 350,
        font_size=78 if variant == "quote" else 72,
        line_height=90 if variant == "quote" else 84,
        weight=800,
        fill="#101820",
    )
    body_svg = svg_text_lines(
        body_lines,
        x=98,
        y=760 if variant == "quote" else 690,
        font_size=34,
        line_height=48,
        weight=500,
        fill="#425047",
    )
    cta_svg = svg_text_lines(
        cta_lines,
        x=112,
        y=1118,
        font_size=34,
        line_height=44,
        weight=800,
        fill="#ffffff",
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350" role="img" aria-label="{escape(headline)}">
  <rect width="1080" height="1350" fill="#ffffff"/>
  <rect x="0" y="0" width="1080" height="22" fill="{accent}"/>
  <circle cx="910" cy="160" r="126" fill="{secondary}" opacity="0.42"/>
  <circle cx="987" cy="248" r="68" fill="#eaf6f2"/>
  <rect x="72" y="82" width="936" height="1186" rx="34" fill="#ffffff" stroke="#d8e7e1" stroke-width="3"/>
  <rect x="92" y="102" width="188" height="12" rx="6" fill="{accent}"/>
  <text x="92" y="180" fill="#5d6b5a" font-size="28" font-family="Inter, Arial, sans-serif" font-weight="800" letter-spacing="2">{escape(eyebrow.upper())}</text>
  <text x="858" y="180" fill="#5d6b5a" font-size="24" font-family="Inter, Arial, sans-serif" font-weight="800" text-anchor="middle">{escape(page_label)}</text>
  {quote_mark}
  {headline_svg}
  <rect x="96" y="620" width="160" height="10" rx="5" fill="{accent}" opacity="0.85"/>
  {body_svg}
  <rect x="92" y="1060" width="896" height="154" rx="28" fill="{accent}"/>
  {cta_svg}
  <text x="92" y="1248" fill="#5d6b5a" font-size="24" font-family="Inter, Arial, sans-serif" font-weight="700">invictus wellness</text>
  <circle cx="944" cy="1236" r="24" fill="{accent}"/>
  <path d="M932 1236h24M944 1224v24" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>
</svg>"""


def svg_text_lines(
    lines: list[str],
    *,
    x: int,
    y: int,
    font_size: int,
    line_height: int,
    weight: int,
    fill: str,
) -> str:
    return "\n  ".join(
        (
            f'<text x="{x}" y="{y + index * line_height}" fill="{fill}" '
            f'font-size="{font_size}" font-family="Inter, Arial, sans-serif" '
            f'font-weight="{weight}">{escape(line)}</text>'
        )
        for index, line in enumerate(lines)
    )


def wrap_svg_text(value: str, *, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(clean_text(value), width=width, break_long_words=False)
    if len(lines) <= max_lines:
        return lines or [""]

    visible = lines[:max_lines]
    visible[-1] = truncate(visible[-1], max(8, width - 1))
    return visible


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."
