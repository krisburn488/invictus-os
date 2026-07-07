import httpx

from invictus_os.schemas.canva import CanvaGraphicRequest
from invictus_os.schemas.content import GeneratedContentResponse
from invictus_os.services.canva_design import (
    CanvaCredentials,
    CanvaDesignService,
    extract_canva_copy,
)


def build_credentials(
    *,
    access_token: str | None = "canva-token",
    brand_template_id: str | None = "template-id",
) -> CanvaCredentials:
    return CanvaCredentials(
        access_token=access_token,
        brand_template_id=brand_template_id,
        api_base_url="https://api.canva.test/rest/v1",
        timeout_seconds=30,
        poll_attempts=1,
        poll_interval_seconds=0,
        headline_field="HEADLINE",
        body_field="BODY_TEXT",
        cta_field="CALL_TO_ACTION",
        graphic_type_field="GRAPHIC_TYPE",
    )


def build_request() -> CanvaGraphicRequest:
    return CanvaGraphicRequest(
        graphic_type="single",
        content=GeneratedContentResponse(
            post=(
                "Annual wellness visits help busy families stay proactive. "
                "Invictus Health keeps preventive care simple, clear, and supportive."
            ),
            reel_script=None,
            caption="Preventive care is easier to prioritize with a simple plan.",
            hashtags=["#PreventiveCare", "#FamilyHealth"],
            call_to_action="Schedule your wellness visit today.",
        ),
    )


def test_canva_design_service_reports_missing_credentials() -> None:
    service = CanvaDesignService(
        credentials=build_credentials(access_token=None, brand_template_id=None)
    )

    response = service.create_graphic(build_request())

    assert response.status == "setup_required"
    assert "CANVA_ACCESS_TOKEN" in response.message
    assert response.extracted_content.headline.startswith("Annual wellness visits")


def test_canva_copy_extraction_uses_generated_content() -> None:
    extracted = extract_canva_copy(build_request())

    assert extracted.headline == "Annual wellness visits help busy families stay proactive."
    assert "Invictus Health keeps preventive care" in extracted.body_text
    assert extracted.call_to_action == "Schedule your wellness visit today."


def test_canva_design_service_creates_autofill_job() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer canva-token"
        assert request.url.path == "/rest/v1/autofills"

        return httpx.Response(
            status_code=200,
            json={
                "job": {
                    "id": "job-123",
                    "status": "success",
                    "result": {
                        "type": "create_design",
                        "design": {
                            "url": "https://www.canva.com/design/example/edit",
                            "thumbnail": {
                                "url": "https://export-download.canva.com/example.png"
                            },
                        },
                    },
                }
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    service = CanvaDesignService(credentials=build_credentials(), client=client)

    response = service.create_graphic(build_request())

    assert response.status == "created"
    assert response.design is not None
    assert response.design.job_id == "job-123"
    assert response.design.url == "https://www.canva.com/design/example/edit"
