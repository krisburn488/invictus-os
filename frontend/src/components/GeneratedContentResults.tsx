import { Check, Copy } from "lucide-react";
import { useState } from "react";

import type { GeneratedContent } from "../types/content";

type GeneratedContentResultsProps = {
  content: GeneratedContent;
};

type CopySectionProps = {
  title: string;
  text: string;
};

function CopySection({ title, text }: CopySectionProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
    } else {
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.opacity = "0";
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
    }

    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <article className="result-section">
      <div className="result-section__header">
        <h3>{title}</h3>
        <button className="copy-button" type="button" onClick={handleCopy}>
          {copied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <p>{text}</p>
    </article>
  );
}

export function GeneratedContentResults({ content }: GeneratedContentResultsProps) {
  return (
    <section className="results-panel" aria-labelledby="results-title">
      <div className="section-heading">
        <p className="eyebrow">Draft</p>
        <h2 id="results-title">Generated content</h2>
      </div>

      <div className="result-list">
        <CopySection title="Social Media Post" text={content.post} />
        {content.reelScript ? <CopySection title="Reel Script" text={content.reelScript} /> : null}
        <CopySection title="Caption" text={content.caption} />
        <CopySection title="Hashtags" text={content.hashtags.join(" ")} />
        <CopySection title="Call To Action" text={content.callToAction} />
      </div>
    </section>
  );
}
