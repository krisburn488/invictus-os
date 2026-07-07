import type { FormEvent } from "react";
import { useState } from "react";

import type { DesignGraphicResponse, DesignSlide, GraphicType } from "../types/design";
import type { GeneratedContent } from "../types/content";

type DesignGraphicWorkflowProps = {
  content: GeneratedContent | null;
  isCreating: boolean;
  result: DesignGraphicResponse | null;
  error: string | null;
  onSubmit: (graphicType: GraphicType) => void;
};

const graphicTypes: { label: string; value: GraphicType }[] = [
  { label: "Single Post", value: "single" },
  { label: "Carousel", value: "carousel" },
  { label: "Quote graphic", value: "quote" },
];

export function DesignGraphicWorkflow({
  content,
  error,
  isCreating,
  onSubmit,
  result,
}: DesignGraphicWorkflowProps) {
  const [downloadError, setDownloadError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setDownloadError(null);
    const data = new FormData(event.currentTarget);
    onSubmit(String(data.get("graphicType") ?? "single") as GraphicType);
  }

  async function handleDownload(slide: DesignSlide) {
    setDownloadError(null);

    try {
      await downloadSlideAsPng(slide);
    } catch {
      setDownloadError("InvictusOS could not download the PNG. Please try again.");
    }
  }

  return (
    <section className="generator-panel" aria-labelledby="design-title">
      <div className="section-heading">
        <p className="eyebrow">Design</p>
        <h2 id="design-title">Make graphic</h2>
      </div>

      {!content ? (
        <div className="setup-panel" role="status">
          <strong>Generate content first</strong>
          <p>Use Generate Today's Content, then return here to create a finished graphic.</p>
        </div>
      ) : (
        <form className="content-form" onSubmit={handleSubmit}>
          <label>
            <span>Graphic type</span>
            <select defaultValue="single" name="graphicType">
              {graphicTypes.map((graphicType) => (
                <option key={graphicType.value} value={graphicType.value}>
                  {graphicType.label}
                </option>
              ))}
            </select>
          </label>

          <button className="primary-button" disabled={isCreating} type="submit">
            {isCreating ? "Creating Graphic..." : "Create Canva Graphic"}
          </button>
        </form>
      )}

      {error ? (
        <section className="error-panel" role="alert">
          <strong>Graphic needs attention</strong>
          <p>{error}</p>
        </section>
      ) : null}

      {downloadError ? (
        <section className="error-panel" role="alert">
          <strong>Download needs attention</strong>
          <p>{downloadError}</p>
        </section>
      ) : null}

      {result ? (
        <section className="design-result-panel" aria-label="Generated graphic preview">
          <div className="result-section__header">
            <h3>Graphic ready</h3>
            <span>{result.slides.length} PNG{result.slides.length === 1 ? "" : "s"}</span>
          </div>
          <p>{result.message}</p>
          <div className="design-preview-grid">
            {result.slides.map((slide) => (
              <article className="design-preview-card" key={slide.id}>
                <img
                  alt={`${slide.title} preview`}
                  className="design-preview-image"
                  src={svgToDataUri(slide.svg)}
                />
                <div className="result-section__header">
                  <h4>{slide.title}</h4>
                  <button className="copy-button" onClick={() => handleDownload(slide)} type="button">
                    Download PNG
                  </button>
                </div>
              </article>
            ))}
          </div>
          <dl className="copy-preview-list">
            <div>
              <dt>Headline</dt>
              <dd>{result.extractedContent.headline}</dd>
            </div>
            <div>
              <dt>Body text</dt>
              <dd>{result.extractedContent.bodyText}</dd>
            </div>
            <div>
              <dt>Call to action</dt>
              <dd>{result.extractedContent.callToAction}</dd>
            </div>
          </dl>
        </section>
      ) : null}
    </section>
  );
}

function svgToDataUri(svg: string) {
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

async function downloadSlideAsPng(slide: DesignSlide) {
  const image = await loadSvgImage(slide.svg);
  const canvas = document.createElement("canvas");
  canvas.width = slide.width;
  canvas.height = slide.height;

  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Canvas is unavailable.");
  }

  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, slide.width, slide.height);
  context.drawImage(image, 0, 0, slide.width, slide.height);

  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((value) => {
      if (value) {
        resolve(value);
      } else {
        reject(new Error("PNG export failed."));
      }
    }, "image/png");
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${slide.id}.png`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function loadSvgImage(svg: string) {
  return new Promise<HTMLImageElement>((resolve, reject) => {
    const blob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const image = new Image();

    image.onload = () => {
      URL.revokeObjectURL(url);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("SVG preview could not be loaded."));
    };
    image.src = url;
  });
}
