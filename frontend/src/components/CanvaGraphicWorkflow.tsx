import type { FormEvent } from "react";

import type { CanvaGraphicResponse, CanvaGraphicType } from "../types/canva";
import type { GeneratedContent } from "../types/content";

type CanvaGraphicWorkflowProps = {
  content: GeneratedContent | null;
  isCreating: boolean;
  result: CanvaGraphicResponse | null;
  error: string | null;
  onSubmit: (graphicType: CanvaGraphicType) => void;
};

const graphicTypes: { label: string; value: CanvaGraphicType }[] = [
  { label: "Single graphic", value: "single" },
  { label: "Carousel", value: "carousel" },
  { label: "Quote graphic", value: "quote" },
];

export function CanvaGraphicWorkflow({
  content,
  error,
  isCreating,
  onSubmit,
  result,
}: CanvaGraphicWorkflowProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    onSubmit(String(data.get("graphicType") ?? "single") as CanvaGraphicType);
  }

  return (
    <section className="generator-panel" aria-labelledby="canva-title">
      <div className="section-heading">
        <p className="eyebrow">Canva</p>
        <h2 id="canva-title">Make graphic</h2>
      </div>

      {!content ? (
        <div className="setup-panel" role="status">
          <strong>Generate content first</strong>
          <p>Use Generate Today's Content, then return here to create a Canva graphic.</p>
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
          <strong>Canva graphic needs attention</strong>
          <p>{error}</p>
        </section>
      ) : null}

      {result ? (
        <section className="canva-result-panel" aria-label="Canva graphic result">
          <div className="result-section__header">
            <h3>{result.status === "created" ? "Canva design created" : "Canva workflow ready"}</h3>
            {result.design?.url ? (
              <a className="text-link" href={result.design.url} rel="noreferrer" target="_blank">
                Open Canva
              </a>
            ) : null}
          </div>
          <p>{result.message}</p>
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
