from invictus_os.schemas.design import DesignGraphicRequest
from invictus_os.schemas.content import GeneratedContentResponse
from invictus_os.services.design_service import DesignService, extract_design_copy


class FakeOpenAIService:
    def generate_json(self, **kwargs: object) -> dict:
        user_payload = kwargs.get("user_payload")
        content = user_payload.get("content", {}) if isinstance(user_payload, dict) else {}
        return {
            "headline": content.get("headline")
            or content.get("post")
            or "Annual wellness visits help busy families stay proactive.",
            "body_text": content.get("body")
            or "Invictus Wellness makes preventive care easier to understand and act on.",
            "call_to_action": content.get("call_to_action") or "Schedule your annual wellness visit today.",
        }


def build_request(graphic_type: str = "single") -> DesignGraphicRequest:
    return DesignGraphicRequest(
        graphic_type=graphic_type,
        content=GeneratedContentResponse(
            post=(
                "Annual wellness visits help busy families stay proactive. "
                "Invictus Wellness makes preventive care easier to understand and act on."
            ),
            reel_script=None,
            caption="A simple annual visit can keep your family health plan on track.",
            hashtags=["#PreventiveCare", "#FamilyHealth"],
            call_to_action="Schedule your annual wellness visit today.",
        ),
    )


def test_design_service_generates_single_graphic() -> None:
    service = DesignService(openai_service=FakeOpenAIService())  # type: ignore[arg-type]

    response = service.create_graphic(build_request())

    assert response.status == "created"
    assert response.graphic_type == "single"
    assert len(response.slides) == 1
    assert response.slides[0].width == 1080
    assert response.slides[0].height == 1350
    assert response.slides[0].svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "INVICTUS WELLNESS" in response.slides[0].svg


def test_design_service_generates_carousel_slides() -> None:
    service = DesignService(openai_service=FakeOpenAIService())  # type: ignore[arg-type]

    response = service.create_graphic(build_request("carousel"))

    assert response.status == "created"
    assert response.graphic_type == "carousel"
    assert [slide.id for slide in response.slides] == [
        "carousel-cover",
        "carousel-detail",
        "carousel-action",
    ]


def test_design_copy_extraction_uses_generated_content() -> None:
    extracted = extract_design_copy(build_request())

    assert extracted.headline == "Annual wellness visits help busy families stay proactive."
    assert "preventive care" in extracted.body_text
    assert extracted.call_to_action == "Schedule your annual wellness visit today."


def test_design_service_escapes_svg_text() -> None:
    request = DesignGraphicRequest(
        graphic_type="quote",
        content=GeneratedContentResponse(
            post='"Use <care> & prevention wisely."',
            reel_script=None,
            caption="Care guidance with symbols.",
            hashtags=["#Wellness"],
            call_to_action="Book <today> & feel ready.",
        ),
    )

    response = DesignService(openai_service=FakeOpenAIService()).create_graphic(request)  # type: ignore[arg-type]

    assert "Use &lt;care&gt; &amp; prevention wisely." in response.slides[0].svg
    assert "Book &lt;today&gt; &amp; feel ready." in response.slides[0].svg
