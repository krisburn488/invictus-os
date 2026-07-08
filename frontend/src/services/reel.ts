import type { ReelPackage, ReelPackageRequest } from "../types/reel";
import { getApiBaseUrl } from "./api";

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

const apiBaseUrl = getApiBaseUrl();

export async function createTodayReel(request: ReelPackageRequest): Promise<ReelPackage> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/reels/today`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        reel_format: request.reelFormat,
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

  if (!isApiReelPackage(payload)) {
    throw new Error("InvictusOS received an unexpected reel response.");
  }

  return {
    hook: payload.hook,
    script: payload.script,
    storyboard: payload.storyboard.map((scene) => ({
      sceneNumber: scene.scene_number,
      durationSeconds: scene.duration_seconds,
      visualDirection: scene.visual_direction,
      onScreenText: scene.on_screen_text,
      voiceOver: scene.voice_over,
      higgsfieldPrompt: scene.higgsfield_prompt,
    })),
    onScreenText: payload.on_screen_text,
    voiceOverScript: payload.voice_over_script,
    caption: payload.caption,
    hashtags: payload.hashtags,
    reelFormat: payload.reel_format,
    durationSeconds: payload.duration_seconds,
    markdown: payload.markdown,
  };
}

function extractErrorMessage(value: unknown) {
  if (value && typeof value === "object" && "detail" in value) {
    const detail = (value as { detail: unknown }).detail;
    return typeof detail === "string" ? detail : "InvictusOS could not create today's reel.";
  }

  return "InvictusOS could not create today's reel.";
}

function isApiReelPackage(value: unknown): value is ApiReelPackage {
  if (!value || typeof value !== "object") {
    return false;
  }

  const response = value as Partial<ApiReelPackage>;

  return (
    typeof response.hook === "string" &&
    typeof response.script === "string" &&
    Array.isArray(response.storyboard) &&
    response.storyboard.every(
      (scene) =>
        typeof scene.scene_number === "number" &&
        typeof scene.duration_seconds === "number" &&
        typeof scene.visual_direction === "string" &&
        typeof scene.on_screen_text === "string" &&
        typeof scene.voice_over === "string" &&
        typeof scene.higgsfield_prompt === "string",
    ) &&
    Array.isArray(response.on_screen_text) &&
    typeof response.voice_over_script === "string" &&
    typeof response.caption === "string" &&
    Array.isArray(response.hashtags) &&
    typeof response.reel_format === "string" &&
    typeof response.duration_seconds === "number" &&
    typeof response.markdown === "string"
  );
}
