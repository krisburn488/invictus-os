export type Platform = "facebook" | "instagram" | "linkedin" | "all";

export type ContentType = "post" | "reel" | "carousel" | "story";

export type ContentGenerationRequest = {
  businessName: string;
  targetAudience: string;
  topic: string;
  platform: Platform;
  contentType: ContentType;
};

export type GeneratedContent = {
  post: string;
  reelScript?: string;
  caption: string;
  hashtags: string[];
  callToAction: string;
};

export type ContentGenerator = {
  generate: (request: ContentGenerationRequest) => GeneratedContent;
};
