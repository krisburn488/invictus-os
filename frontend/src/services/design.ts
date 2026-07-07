import type { DesignGraphicRequest, DesignGraphicResponse } from "../types/design";

type ApiDesignGraphicResponse = {
  status: "created";
  graphic_type: "single" | "carousel" | "quote";
  extracted_content: {
    headline: string;
    body_text: string;
    call_to_action: string;
  };
  message: string;
  slides: {
    id: string;
    title: string;
    width: number;
    height: number;
    svg: string;
  }[];
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function createDesignGraphic(
  request: DesignGraphicRequest,
): Promise<DesignGraphicResponse> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/design/graphics`, {
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

  if (!isApiDesignGraphicResponse(payload)) {
    throw new Error("InvictusOS received an unexpected design response.");
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
    slides: payload.slides,
  };
}

function extractErrorMessage(value: unknown) {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail: unknown }).detail;
    return typeof detail === "string" ? detail : "InvictusOS could not create the graphic.";
  }

  return "InvictusOS could not create the graphic.";
}

function isApiDesignGraphicResponse(value: unknown): value is ApiDesignGraphicResponse {
  if (!value || typeof value !== "object") {
    return false;
  }

  const response = value as Partial<ApiDesignGraphicResponse>;
  const extracted = response.extracted_content;

  return (
    response.status === "created" &&
    typeof response.graphic_type === "string" &&
    Boolean(extracted) &&
    typeof extracted?.headline === "string" &&
    typeof extracted.body_text === "string" &&
    typeof extracted.call_to_action === "string" &&
    typeof response.message === "string" &&
    Array.isArray(response.slides) &&
    response.slides.every(
      (slide) =>
        typeof slide.id === "string" &&
        typeof slide.title === "string" &&
        typeof slide.width === "number" &&
        typeof slide.height === "number" &&
        typeof slide.svg === "string",
    )
  );
}
