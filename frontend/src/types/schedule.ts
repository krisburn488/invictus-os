import type { GeneratedContent } from "./content";
import type { DesignGraphicResponse } from "./design";
import type { ReelPackage } from "./reel";

export type SchedulePlatform = "facebook" | "instagram" | "both";
export type ScheduleContentType = "image_post" | "carousel" | "reel";
export type ScheduledPostStatus = "draft" | "scheduled" | "ready_to_publish";

export type SchedulePostRequest = {
  platform: SchedulePlatform;
  contentType: ScheduleContentType;
  scheduledFor?: string;
  publishNow: boolean;
  draftOnly: boolean;
  content: GeneratedContent;
  design?: DesignGraphicResponse;
  reel?: ReelPackage;
};

export type ScheduledPost = {
  id: string;
  platform: SchedulePlatform;
  contentType: ScheduleContentType;
  status: ScheduledPostStatus;
  scheduledFor?: string;
  createdAt: string;
  updatedAt: string;
  caption: string;
  hashtags: string[];
  postPreview: string;
  content: GeneratedContent;
  design?: DesignGraphicResponse;
  reel?: ReelPackage;
};
