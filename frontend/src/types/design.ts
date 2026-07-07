import type { GeneratedContent } from "./content";

export type GraphicType = "single" | "carousel" | "quote";

export type GeneratedDesignCopy = {
  headline: string;
  bodyText: string;
  callToAction: string;
};

export type DesignGraphicRequest = {
  graphicType: GraphicType;
  content: GeneratedContent;
};

export type DesignSlide = {
  id: string;
  title: string;
  width: number;
  height: number;
  svg: string;
};

export type DesignGraphicResponse = {
  status: "created";
  graphicType: GraphicType;
  extractedContent: GeneratedDesignCopy;
  message: string;
  slides: DesignSlide[];
};
