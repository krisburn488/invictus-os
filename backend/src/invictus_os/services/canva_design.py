import re
import time

import httpx

from invictus_os.schemas.canva import (
    CanvaDesignResult,
    CanvaGeneratedCopy,
    CanvaGraphicRequest,
    CanvaGraphicResponse,
    CanvaGraphicType,
)


class CanvaDesignError(Exception):
    message = "InvictusOS could not create the Canva design."


class CanvaAuthenticationError(CanvaDesignError):
    message = "Canva rejected the configured access token. Reconnect Canva and try again."


class CanvaRateLimitError(CanvaDesignError):
    message = "Canva is rate limiting requests. Please wait a moment and try again."


class CanvaNetworkError(CanvaDesignError):
    message = "InvictusOS could not reach Canva. Check your connection and try again."


class CanvaInvalidResponseError(CanvaDesignError):
    message = "Canva returned an unexpected response. Please try again."


class CanvaCredentials:
    def __init__(
        self,
        *,
        access_token: str | None,
        brand_template_id: str | None,
        api_base_url: str,
        timeout_seconds: float,
        poll_attempts: int,
        poll_interval_seconds: float,
        headline_field: str,
        body_field: str,
        cta_field: str,
        graphic_type_field: str,
    ) -> None:
        self.access_token = access_token
        self.brand_template_id = brand_template_id
        self.api_base_url = api_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.poll_attempts = poll_attempts
        self.poll_interval_seconds = poll_interval_seconds
        self.headline_field = headline_field
        self.body_field = body_field
        self.cta_field = cta_field
        self.graphic_type_field = graphic_type_field

    @property
    def is_configured(self) -> bool:
        return bool(self.access_token and self.brand_template_id)


class CanvaDesignService:
    def __init__(
        self,
        *,
        credentials: CanvaCredentials,
        client: httpx.Client | None = None,
    ) -> None:
        self._credentials = credentials
        self._client = client

    def create_graphic(self, request: CanvaGraphicRequest) -> CanvaGraphicResponse:
        extracted_content = extract_canva_copy(request)

        if not self._credentials.is_configured:
            return CanvaGraphicResponse(
                status="setup_required",
                graphic_type=request.graphic_type,
                extracted_content=extracted_content,
                message=(
                    "Canva is not connected yet. Add CANVA_ACCESS_TOKEN and "
                    "CANVA_BRAND_TEMPLATE_ID to backend/.env, then restart the backend."
                ),
            )

        job = self._create_autofill_job(request.graphic_type, extracted_content)
        job_id = str(job.get("id", ""))
        status = str(job.get("status", ""))

        if not job_id:
            raise CanvaInvalidResponseError

        if status == "success":
            return self._build_success_response(request.graphic_type, extracted_content, job)
        if status == "failed":
            raise CanvaDesignError

        final_job = self._poll_autofill_job(job_id)

        if str(final_job.get("status", "")) == "success":
            return self._build_success_response(request.graphic_type, extracted_content, final_job)
        if str(final_job.get("status", "")) == "failed":
            raise CanvaDesignError

        return CanvaGraphicResponse(
            status="in_progress",
            graphic_type=request.graphic_type,
            extracted_content=extracted_content,
            message="Canva accepted the design request and is still generating the design.",
            design=CanvaDesignResult(job_id=job_id),
        )

    def _create_autofill_job(
        self,
        graphic_type: CanvaGraphicType,
        copy: CanvaGeneratedCopy,
    ) -> dict[str, object]:
        response = self._request(
            "POST",
            "/autofills",
            json={
                "brand_template_id": self._credentials.brand_template_id,
                "data": {
                    self._credentials.headline_field: {"type": "text", "text": copy.headline},
                    self._credentials.body_field: {"type": "text", "text": copy.body_text},
                    self._credentials.cta_field: {"type": "text", "text": copy.call_to_action},
                    self._credentials.graphic_type_field: {
                        "type": "text",
                        "text": graphic_type_label(graphic_type),
                    },
                },
            },
        )
        job = response.get("job")
        if not isinstance(job, dict):
            raise CanvaInvalidResponseError
        return job

    def _poll_autofill_job(self, job_id: str) -> dict[str, object]:
        job: dict[str, object] = {"id": job_id, "status": "in_progress"}

        for _ in range(self._credentials.poll_attempts):
            time.sleep(self._credentials.poll_interval_seconds)
            response = self._request("GET", f"/autofills/{job_id}")
            next_job = response.get("job")
            if not isinstance(next_job, dict):
                raise CanvaInvalidResponseError

            job = next_job
            if str(job.get("status", "")) in {"success", "failed"}:
                return job

        return job

    def _request(self, method: str, path: str, **kwargs: object) -> dict[str, object]:
        client = self._client or httpx.Client(timeout=self._credentials.timeout_seconds)
        should_close = self._client is None

        try:
            response = client.request(
                method,
                f"{self._credentials.api_base_url}{path}",
                headers={"Authorization": f"Bearer {self._credentials.access_token}"},
                **kwargs,
            )
        except httpx.RequestError as exc:
            raise CanvaNetworkError from exc
        finally:
            if should_close:
                client.close()

        if response.status_code in {401, 403}:
            raise CanvaAuthenticationError
        if response.status_code == 429:
            raise CanvaRateLimitError
        if response.status_code >= 400:
            raise CanvaDesignError

        payload = response.json()
        if not isinstance(payload, dict):
            raise CanvaInvalidResponseError
        return payload

    def _build_success_response(
        self,
        graphic_type: CanvaGraphicType,
        extracted_content: CanvaGeneratedCopy,
        job: dict[str, object],
    ) -> CanvaGraphicResponse:
        result = job.get("result")
        result_dict = result if isinstance(result, dict) else {}
        design = result_dict.get("design")
        design_dict = design if isinstance(design, dict) else {}
        thumbnail = design_dict.get("thumbnail")
        thumbnail_dict = thumbnail if isinstance(thumbnail, dict) else {}

        return CanvaGraphicResponse(
            status="created",
            graphic_type=graphic_type,
            extracted_content=extracted_content,
            message="Canva created the design successfully.",
            design=CanvaDesignResult(
                url=optional_string(design_dict.get("url")),
                thumbnail_url=optional_string(thumbnail_dict.get("url")),
                job_id=optional_string(job.get("id")),
            ),
        )


def extract_canva_copy(request: CanvaGraphicRequest) -> CanvaGeneratedCopy:
    content = request.content
    headline = extract_headline(content.post, content.caption, request.graphic_type)
    body = extract_body_text(content.post, content.caption, request.graphic_type)

    return CanvaGeneratedCopy(
        headline=headline,
        body_text=body,
        call_to_action=truncate(clean_text(content.call_to_action), 140),
    )


def extract_headline(post: str, caption: str, graphic_type: CanvaGraphicType) -> str:
    if graphic_type == "quote":
        quoted = re.findall(r'"([^"]+)"', post)
        if quoted:
            return truncate(clean_text(quoted[0]), 96)

    first_sentence = re.split(r"(?<=[.!?])\s+", clean_text(post), maxsplit=1)[0]
    if len(first_sentence) < 24:
        first_sentence = clean_text(caption) or first_sentence

    return truncate(first_sentence, 96)


def extract_body_text(post: str, caption: str, graphic_type: CanvaGraphicType) -> str:
    source = caption if graphic_type == "quote" else post
    paragraphs = [clean_text(part) for part in source.split("\n") if clean_text(part)]
    body = " ".join(paragraphs[1:] or paragraphs)
    return truncate(body or clean_text(caption), 420)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def graphic_type_label(graphic_type: CanvaGraphicType) -> str:
    labels = {
        "single": "Single 1080x1350 healthcare social graphic",
        "carousel": "1080x1350 healthcare carousel cover",
        "quote": "1080x1350 healthcare quote graphic",
    }
    return labels[graphic_type]


def optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None
