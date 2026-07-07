import type { CanvaGraphicRequest, CanvaGraphicResponse } from "../types/canva";

type ApiCanvaGraphicResponse = {
  status: "created" | "in_progress" | "setup_required";
  graphic_type: "single" | "carousel" | "quote";
  extracted_content: {
    headline: string;
    body_text: string;
    call_to_action: string;
  };
  message: string;
  design?: {
    url?: string | null;
    thumbnail_url?: string | null;
    job_id?: string | null;
  } | null;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function createCanvaGraphic(
  request: CanvaGraphicRequest,
): Promise<CanvaGraphicResponse> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/canva/graphics`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        graphic_type: request.graphicType,
        content: {
          post: request.content.post,
          reel_script: request.content.reelScript ?? null,
          caption: request.content.caption,
          hashtags: request.content.hashtags,
          call_to_action: request.content.callToAction,
        },
      }),
    });
  } catch {
    throw new Error("InvictusOS could not reach the backend. Confirm the backend is running.");
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  if (!isApiCanvaGraphicResponse(payload)) {
    throw new Error("InvictusOS received an unexpected Canva response.");
  }

  return {
    status: payload.status,
    graphicType: payload.graphic_type,
    extractedContent: {
      headline: payload.extracted_content.headline,
      bodyText: payload.extracted_content.body_text,
      callToAction: payload.extracted_content.call_to_action,
    },
    message: payload.message,
    design: payload.design
      ? {
          url: payload.design.url ?? undefined,
          thumbnailUrl: payload.design.thumbnail_url ?? undefined,
          jobId: payload.design.job_id ?? undefined,
        }
      : undefined,
  };
}

function extractErrorMessage(value: unknown) {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail: unknown }).detail;
    return typeof detail === "string" ? detail : "InvictusOS could not create the Canva graphic.";
  }

  return "InvictusOS could not create the Canva graphic.";
}

function isApiCanvaGraphicResponse(value: unknown): value is ApiCanvaGraphicResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const response = value as Partial<ApiCanvaGraphicResponse>;
  const extracted = response.extracted_content;

  return (
    typeof response.status === "string" &&
    typeof response.graphic_type === "string" &&
    Boolean(extracted) &&
    typeof extracted?.headline === "string" &&
    typeof extracted.body_text === "string" &&
    typeof extracted.call_to_action === "string" &&
    typeof response.message === "string"
  );
}
