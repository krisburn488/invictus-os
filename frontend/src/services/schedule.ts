import type { DesignGraphicResponse } from "../types/design";
import type { ReelPackage } from "../types/reel";
import type { SchedulePostRequest, ScheduledPost } from "../types/schedule";

type ApiScheduledPost = {
  id: string;
  platform: "facebook" | "instagram" | "both";
  content_type: "image_post" | "carousel" | "reel";
  status: "draft" | "scheduled" | "ready_to_publish";
  scheduled_for?: string | null;
  created_at: string;
  updated_at: string;
  caption: string;
  hashtags: string[];
  post_preview: string;
  content: {
    post: string;
    reel_script?: string | null;
    caption: string;
    hashtags: string[];
    call_to_action: string;
  };
  design?: ApiDesignGraphicResponse | null;
  reel?: ApiReelPackage | null;
};

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

type ApiReelPackage = {
  hook: string;
  script: string;
  storyboard: {
    scene_number: number;
    duration_seconds: number;
    visual_direction: string;
    on_screen_text: string;
    voice_over: string;
    higgsfield_prompt: string;
  }[];
  on_screen_text: string[];
  voice_over_script: string;
  caption: string;
  hashtags: string[];
  reel_format: "talking_head" | "ai_avatar" | "b_roll";
  duration_seconds: number;
  markdown: string;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function listScheduledPosts(): Promise<ScheduledPost[]> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/schedule/posts`);
  } catch {
    throw new Error("InvictusOS could not reach the backend. Confirm the backend is running.");
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  if (!payload || typeof payload !== "object" || !Array.isArray((payload as { posts?: unknown }).posts)) {
    throw new Error("InvictusOS received an unexpected schedule history response.");
  }

  return (payload as { posts: ApiScheduledPost[] }).posts.map(toScheduledPost);
}

export async function schedulePost(request: SchedulePostRequest): Promise<ScheduledPost> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/schedule/posts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(toApiScheduleRequest(request)),
    });
  } catch {
    throw new Error("InvictusOS could not reach the backend. Confirm the backend is running.");
  }

  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload));
  }

  if (!isApiScheduledPost(payload)) {
    throw new Error("InvictusOS received an unexpected scheduled post response.");
  }

  return toScheduledPost(payload);
}

function toApiScheduleRequest(request: SchedulePostRequest) {
  return {
    platform: request.platform,
    content_type: request.contentType,
    scheduled_for: request.scheduledFor ?? null,
    publish_now: request.publishNow,
    draft_only: request.draftOnly,
    content: {
      post: request.content.post,
      reel_script: request.content.reelScript ?? null,
      caption: request.content.caption,
      hashtags: request.content.hashtags,
      call_to_action: request.content.callToAction,
    },
    design: request.design ? toApiDesign(request.design) : null,
    reel: request.reel ? toApiReel(request.reel) : null,
  };
}

function toScheduledPost(post: ApiScheduledPost): ScheduledPost {
  return {
    id: post.id,
    platform: post.platform,
    contentType: post.content_type,
    status: post.status,
    scheduledFor: post.scheduled_for ?? undefined,
    createdAt: post.created_at,
    updatedAt: post.updated_at,
    caption: post.caption,
    hashtags: post.hashtags,
    postPreview: post.post_preview,
    content: {
      post: post.content.post,
      reelScript: post.content.reel_script ?? undefined,
      caption: post.content.caption,
      hashtags: post.content.hashtags,
      callToAction: post.content.call_to_action,
    },
    design: post.design ? toDesign(post.design) : undefined,
    reel: post.reel ? toReel(post.reel) : undefined,
  };
}

function toApiDesign(design: DesignGraphicResponse): ApiDesignGraphicResponse {
  return {
    status: design.status,
    graphic_type: design.graphicType,
    extracted_content: {
      headline: design.extractedContent.headline,
      body_text: design.extractedContent.bodyText,
      call_to_action: design.extractedContent.callToAction,
    },
    message: design.message,
    slides: design.slides,
  };
}

function toDesign(design: ApiDesignGraphicResponse): DesignGraphicResponse {
  return {
    status: design.status,
    graphicType: design.graphic_type,
    extractedContent: {
      headline: design.extracted_content.headline,
      bodyText: design.extracted_content.body_text,
      callToAction: design.extracted_content.call_to_action,
    },
    message: design.message,
    slides: design.slides,
  };
}

function toApiReel(reel: ReelPackage): ApiReelPackage {
  return {
    hook: reel.hook,
    script: reel.script,
    storyboard: reel.storyboard.map((scene) => ({
      scene_number: scene.sceneNumber,
      duration_seconds: scene.durationSeconds,
      visual_direction: scene.visualDirection,
      on_screen_text: scene.onScreenText,
      voice_over: scene.voiceOver,
      higgsfield_prompt: scene.higgsfieldPrompt,
    })),
    on_screen_text: reel.onScreenText,
    voice_over_script: reel.voiceOverScript,
    caption: reel.caption,
    hashtags: reel.hashtags,
    reel_format: reel.reelFormat,
    duration_seconds: reel.durationSeconds,
    markdown: reel.markdown,
  };
}

function toReel(reel: ApiReelPackage): ReelPackage {
  return {
    hook: reel.hook,
    script: reel.script,
    storyboard: reel.storyboard.map((scene) => ({
      sceneNumber: scene.scene_number,
      durationSeconds: scene.duration_seconds,
      visualDirection: scene.visual_direction,
      onScreenText: scene.on_screen_text,
      voiceOver: scene.voice_over,
      higgsfieldPrompt: scene.higgsfield_prompt,
    })),
    onScreenText: reel.on_screen_text,
    voiceOverScript: reel.voice_over_script,
    caption: reel.caption,
    hashtags: reel.hashtags,
    reelFormat: reel.reel_format,
    durationSeconds: reel.duration_seconds,
    markdown: reel.markdown,
  };
}

function extractErrorMessage(value: unknown) {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return "InvictusOS could not schedule the post. Check the selected assets and timing.";
    }
  }

  return "InvictusOS could not schedule the post.";
}

function isApiScheduledPost(value: unknown): value is ApiScheduledPost {
  if (!value || typeof value !== "object") {
    return false;
  }

  const post = value as Partial<ApiScheduledPost>;
  return (
    typeof post.id === "string" &&
    typeof post.platform === "string" &&
    typeof post.content_type === "string" &&
    typeof post.status === "string" &&
    typeof post.caption === "string" &&
    Array.isArray(post.hashtags) &&
    typeof post.post_preview === "string" &&
    Boolean(post.content)
  );
}
