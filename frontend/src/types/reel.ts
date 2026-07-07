import type { GeneratedContent } from "./content";

export type ReelFormat = "talking_head" | "ai_avatar" | "b_roll";

export type ReelPackageRequest = {
  content: GeneratedContent;
  reelFormat: ReelFormat;
};

export type ReelStoryboardScene = {
  sceneNumber: number;
  durationSeconds: number;
  visualDirection: string;
  onScreenText: string;
  voiceOver: string;
  higgsfieldPrompt: string;
};

export type ReelPackage = {
  hook: string;
  script: string;
  storyboard: ReelStoryboardScene[];
  onScreenText: string[];
  voiceOverScript: string;
  caption: string;
  hashtags: string[];
  reelFormat: ReelFormat;
  durationSeconds: number;
  markdown: string;
};
