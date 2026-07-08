import type { FormEvent } from "react";
import { useEffect, useState } from "react";

import type { GeneratedContent } from "../types/content";
import type { ReelFormat, ReelPackage } from "../types/reel";

type ReelWorkflowProps = {
  content: GeneratedContent | null;
  isCreating: boolean;
  result: ReelPackage | null;
  error: string | null;
  onSubmit: (reelFormat: ReelFormat) => void;
  onRetry: () => void;
};

const reelFormats: { label: string; value: ReelFormat }[] = [
  { label: "Talking head", value: "talking_head" },
  { label: "AI avatar", value: "ai_avatar" },
  { label: "B-roll", value: "b_roll" },
];

const progressSteps = ["Writing Script...", "Creating Voice-over...", "Generating Video...", "Finalizing..."];

export function ReelWorkflow({ content, error, isCreating, onRetry, onSubmit, result }: ReelWorkflowProps) {
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [activeProgressStep, setActiveProgressStep] = useState(0);

  useEffect(() => {
    if (!isCreating) {
      setActiveProgressStep(0);
      return undefined;
    }

    const intervalId = window.setInterval(() => {
      setActiveProgressStep((step) => Math.min(step + 1, progressSteps.length - 1));
    }, 1800);

    return () => window.clearInterval(intervalId);
  }, [isCreating]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setDownloadError(null);
    const data = new FormData(event.currentTarget);
    onSubmit(String(data.get("reelFormat") ?? "talking_head") as ReelFormat);
  }

  function handleJsonDownload() {
    if (!result) {
      return;
    }
    try {
      downloadTextFile("today-reel-package.json", JSON.stringify(result, null, 2), "application/json");
    } catch {
      setDownloadError("InvictusOS could not download the JSON package. Please try again.");
    }
  }

  function handleMarkdownDownload() {
    if (!result) {
      return;
    }
    try {
      downloadTextFile("today-reel-package.md", result.markdown, "text/markdown");
    } catch {
      setDownloadError("InvictusOS could not download the Markdown package. Please try again.");
    }
  }

  function handleVideoDownload() {
    const downloadUrl = result?.video?.downloadUrl ?? result?.video?.videoUrl;
    if (!downloadUrl) {
      setDownloadError("InvictusOS could not find a video download URL. Please retry video generation.");
      return;
    }

    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = "today-reel-video.mp4";
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  return (
    <section className="generator-panel" aria-labelledby="reel-title">
      <div className="section-heading">
        <p className="eyebrow">Reel</p>
        <h2 id="reel-title">Create today's reel</h2>
      </div>

      {!content ? (
        <div className="setup-panel" role="status">
          <strong>Generate content first</strong>
          <p>Use Generate Today's Content, then return here to create a reel package.</p>
        </div>
      ) : (
        <form className="content-form" onSubmit={handleSubmit}>
          <label>
            <span>Reel format</span>
            <select defaultValue="talking_head" name="reelFormat">
              {reelFormats.map((format) => (
                <option key={format.value} value={format.value}>
                  {format.label}
                </option>
              ))}
            </select>
          </label>

          <button className="primary-button" disabled={isCreating} type="submit">
            {isCreating ? "Creating Reel..." : "Create Reel Package"}
          </button>
        </form>
      )}

      {isCreating ? (
        <section className="reel-progress-panel" aria-label="Video generation progress" role="status">
          {progressSteps.map((step, index) => (
            <div
              className={`reel-progress-step${index <= activeProgressStep ? " reel-progress-step--active" : ""}`}
              key={step}
            >
              <span>{index + 1}</span>
              <p>{step}</p>
            </div>
          ))}
        </section>
      ) : null}

      {error ? (
        <section className="error-panel" role="alert">
          <strong>Reel needs attention</strong>
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
        <section className="reel-result-panel" aria-label="Reel package preview">
          <div className="result-section__header">
            <h3>Reel package ready</h3>
            <span>{result.durationSeconds}s</span>
          </div>
          <div className="download-actions">
            <button className="copy-button" onClick={handleJsonDownload} type="button">
              Download JSON
            </button>
            <button className="copy-button" onClick={handleMarkdownDownload} type="button">
              Download Markdown
            </button>
            {result.video?.status === "completed" ? (
              <button className="copy-button" onClick={handleVideoDownload} type="button">
                Download Video
              </button>
            ) : null}
          </div>

          {result.video?.status === "completed" && result.video.videoUrl ? (
            <section className="reel-video-preview" aria-label="Generated video preview">
              <video controls playsInline poster="" src={result.video.videoUrl}>
                <track kind="captions" />
              </video>
              <p>
                MP4 generated by {result.video.provider} at {result.video.width}x{result.video.height}.
              </p>
            </section>
          ) : null}

          {result.video && result.video.status !== "completed" ? (
            <section className="setup-panel" role="status">
              <strong>Video generation needs setup</strong>
              <p>
                {result.video.errorMessage ??
                  "InvictusOS created the reel package, but the video provider did not return an MP4."}
              </p>
              {result.video.retryable ? (
                <button className="copy-button" disabled={isCreating} onClick={onRetry} type="button">
                  Retry Video
                </button>
              ) : null}
            </section>
          ) : null}

          <div className="reel-preview-grid">
            <section className="reel-preview-card">
              <h4>Hook</h4>
              <p>{result.hook}</p>
            </section>
            <section className="reel-preview-card">
              <h4>Voice-over</h4>
              <p>{result.voiceOverScript}</p>
            </section>
            <section className="reel-preview-card">
              <h4>Caption</h4>
              <p>{result.caption}</p>
            </section>
          </div>

          <section className="reel-preview-card">
            <h4>Storyboard and Higgsfield prompts</h4>
            <div className="scene-list">
              {result.storyboard.map((scene) => (
                <article className="scene-card" key={scene.sceneNumber}>
                  <div className="result-section__header">
                    <h5>Scene {scene.sceneNumber}</h5>
                    <span>{scene.durationSeconds}s</span>
                  </div>
                  <dl className="copy-preview-list">
                    <div>
                      <dt>Visual</dt>
                      <dd>{scene.visualDirection}</dd>
                    </div>
                    <div>
                      <dt>On-screen text</dt>
                      <dd>{scene.onScreenText}</dd>
                    </div>
                    <div>
                      <dt>Voice-over</dt>
                      <dd>{scene.voiceOver}</dd>
                    </div>
                    <div>
                      <dt>Higgsfield prompt</dt>
                      <dd>{scene.higgsfieldPrompt}</dd>
                    </div>
                  </dl>
                </article>
              ))}
            </div>
          </section>

          <section className="reel-preview-card">
            <h4>Hashtags</h4>
            <p>{result.hashtags.join(" ")}</p>
          </section>
        </section>
      ) : null}
    </section>
  );
}

function downloadTextFile(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
