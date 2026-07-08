import type { ContentGenerationRequest, ContentGenerator, GeneratedContent } from "../types/content";
import { getApiBaseUrl } from "./api";

type ApiGeneratedContent = {
  headline?: string | null;
  body?: string | null;
  post: string;
  reel_script: string | null;
  caption: string;
  hashtags: string[];
  call_to_action: string;
};

const apiBaseUrl = getApiBaseUrl();

function toApiRequest(request: ContentGenerationRequest) {
  return {
    business_name: request.businessName,
    target_audience: request.targetAudience,
    topic: request.topic,
    platform: request.platform,
    content_type: request.contentType,
  };
}

function toGeneratedContent(content: ApiGeneratedContent): GeneratedContent {
  return {
    headline: content.headline ?? undefined,
    body: content.body ?? undefined,
    post: content.post,
    reelScript: content.reel_script ?? undefined,
    caption: content.caption,
    hashtags: content.hashtags,
    callToAction: content.call_to_action,
  };
}

function isApiGeneratedContent(value: unknown): value is ApiGeneratedContent {
  if (!value || typeof value !== "object") {
    return false;
  }

  const content = value as Partial<ApiGeneratedContent>;

  return (
    typeof content.post === "string" &&
    (typeof content.reel_script === "string" || content.reel_script === null) &&
    typeof content.caption === "string" &&
    Array.isArray(content.hashtags) &&
    content.hashtags.every((hashtag) => typeof hashtag === "string") &&
    typeof content.call_to_action === "string"
  );
}

function extractErrorMessage(value: unknown) {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail: unknown }).detail;
    return typeof detail === "string" ? detail : "InvictusOS could not generate content.";
  }

  return "InvictusOS could not generate content.";
}

export class OpenAIContentGenerator implements ContentGenerator {
  async generate(request: ContentGenerationRequest): Promise<GeneratedContent> {
    let response: Response;

    try {
      response = await fetch(`${apiBaseUrl}/content/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(toApiRequest(request)),
      });
    } catch {
      throw new Error("InvictusOS could not reach the backend. Confirm the backend is running.");
    }

    const payload: unknown = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(extractErrorMessage(payload));
    }

    if (!isApiGeneratedContent(payload)) {
      throw new Error("InvictusOS received an unexpected content response.");
    }

    return toGeneratedContent(payload);
  }
}

export const contentGenerator: ContentGenerator = new OpenAIContentGenerator();
