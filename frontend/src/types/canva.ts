import type { GeneratedContent } from "./content";

export type CanvaGraphicType = "single" | "carousel" | "quote";

export type CanvaGeneratedCopy = {
  headline: string;
  bodyText: string;
  callToAction: string;
};

export type CanvaGraphicRequest = {
  graphicType: CanvaGraphicType;
  content: GeneratedContent;
};

export type CanvaDesignResult = {
  url?: string;
  thumbnailUrl?: string;
  jobId?: string;
};

export type CanvaGraphicResponse = {
  status: "created" | "in_progress" | "setup_required";
  graphicType: CanvaGraphicType;
  extractedContent: CanvaGeneratedCopy;
  message: string;
  design?: CanvaDesignResult;
};
