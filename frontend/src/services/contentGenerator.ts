import type { ContentGenerationRequest, ContentGenerator, GeneratedContent } from "../types/content";

const platformLabels = {
  facebook: "Facebook",
  instagram: "Instagram",
  linkedin: "LinkedIn",
  all: "Facebook, Instagram, and LinkedIn",
};

const contentTypeLabels = {
  post: "post",
  reel: "reel",
  carousel: "carousel",
  story: "story",
};

function hashtagize(value: string) {
  return value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 3)
    .map((word) => word.replace(/[^a-zA-Z0-9]/g, ""))
    .filter(Boolean)
    .map((word) => `#${word.charAt(0).toUpperCase()}${word.slice(1)}`);
}

function buildHashtags(request: ContentGenerationRequest) {
  const businessTags = hashtagize(request.businessName);
  const topicTags = hashtagize(request.topic);
  const platformTag = request.platform === "all" ? "#SocialMedia" : `#${platformLabels[request.platform]}`;

  return Array.from(
    new Set([...businessTags, ...topicTags, platformTag, "#SmallBusiness", "#ContentMarketing"]),
  ).slice(0, 8);
}

function buildReelScript(request: ContentGenerationRequest) {
  return [
    `Hook: "If ${request.targetAudience} care about ${request.topic}, this is for you."`,
    `Scene 1: Show ${request.businessName} solving the main problem or desire around ${request.topic}.`,
    `Scene 2: Share one quick tip, benefit, or behind-the-scenes detail that feels useful right away.`,
    `Scene 3: Show the result your audience wants and keep the language simple and direct.`,
    `On-screen text: "${request.topic} made simple by ${request.businessName}."`,
    "Close: Invite viewers to comment, save, or send a message for the next step.",
  ].join("\n\n");
}

export class LocalContentGenerator implements ContentGenerator {
  generate(request: ContentGenerationRequest): GeneratedContent {
    const platform = platformLabels[request.platform];
    const contentType = contentTypeLabels[request.contentType];
    const hashtags = buildHashtags(request);

    return {
      post: [
        `${request.businessName} is helping ${request.targetAudience} make progress on ${request.topic}.`,
        `Today's ${contentType} is built for ${platform}, with a clear message: you do not need to overcomplicate the next step.`,
        `Here is the simple idea: focus on one useful action, one clear benefit, and one reason to act today.`,
        `If ${request.topic} has been on your mind, ${request.businessName} can help you move from interest to action.`,
      ].join("\n\n"),
      reelScript: request.contentType === "reel" ? buildReelScript(request) : undefined,
      caption: `${request.topic} does not have to feel complicated. ${request.businessName} helps ${request.targetAudience} take the next step with clarity and confidence.`,
      hashtags,
      callToAction: `Message ${request.businessName} today or comment "READY" to learn the next step.`,
    };
  }
}

export const contentGenerator: ContentGenerator = new LocalContentGenerator();
