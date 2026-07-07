import type { FormEvent } from "react";
import { useMemo, useState } from "react";

import type { GeneratedContent } from "../types/content";
import type { DesignGraphicResponse } from "../types/design";
import type { ReelPackage } from "../types/reel";
import type { ScheduleContentType, SchedulePlatform, ScheduledPost } from "../types/schedule";

type ScheduleWorkflowProps = {
  content: GeneratedContent | null;
  design: DesignGraphicResponse | null;
  reel: ReelPackage | null;
  history: ScheduledPost[];
  isLoadingHistory: boolean;
  isScheduling: boolean;
  error: string | null;
  success: string | null;
  onSubmit: (request: {
    platform: SchedulePlatform;
    contentType: ScheduleContentType;
    scheduledFor?: string;
    publishNow: boolean;
    draftOnly: boolean;
  }) => void;
};

export function ScheduleWorkflow({
  content,
  design,
  error,
  history,
  isLoadingHistory,
  isScheduling,
  onSubmit,
  reel,
  success,
}: ScheduleWorkflowProps) {
  const [publishNow, setPublishNow] = useState(false);
  const [draftOnly, setDraftOnly] = useState(false);
  const [contentType, setContentType] = useState<ScheduleContentType>("image_post");

  const missingAssetMessage = useMemo(
    () => getMissingAssetMessage(contentType, design, reel),
    [contentType, design, reel],
  );

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    onSubmit({
      platform: String(data.get("platform") ?? "instagram") as SchedulePlatform,
      contentType,
      scheduledFor: String(data.get("scheduledFor") ?? "") || undefined,
      publishNow,
      draftOnly,
    });
  }

  return (
    <section className="generator-panel" aria-labelledby="schedule-title">
      <div className="section-heading">
        <p className="eyebrow">Schedule</p>
        <h2 id="schedule-title">Schedule posts</h2>
      </div>

      {!content ? (
        <div className="setup-panel" role="status">
          <strong>Generate content first</strong>
          <p>Use Generate Today's Content before scheduling posts.</p>
        </div>
      ) : (
        <>
          <section className="schedule-preview-panel" aria-label="Post preview">
            <h3>Post preview</h3>
            <p>{content.caption}</p>
            <p>{content.hashtags.join(" ")}</p>
            <dl className="copy-preview-list">
              <div>
                <dt>Graphic</dt>
                <dd>{design ? `${design.slides.length} generated slide(s) ready` : "No graphic yet"}</dd>
              </div>
              <div>
                <dt>Reel</dt>
                <dd>{reel ? `${reel.durationSeconds}s reel package ready` : "No reel package yet"}</dd>
              </div>
            </dl>
          </section>

          <form className="content-form" onSubmit={handleSubmit}>
            <div className="form-grid">
              <label>
                <span>Platform</span>
                <select defaultValue="instagram" name="platform">
                  <option value="facebook">Facebook</option>
                  <option value="instagram">Instagram</option>
                  <option value="both">Facebook and Instagram</option>
                </select>
              </label>
              <label>
                <span>Content type</span>
                <select
                  name="contentType"
                  onChange={(event) => setContentType(event.target.value as ScheduleContentType)}
                  value={contentType}
                >
                  <option value="image_post">Image post</option>
                  <option value="carousel">Carousel</option>
                  <option value="reel">Reel</option>
                </select>
              </label>
            </div>

            <label>
              <span>Date and time</span>
              <input disabled={publishNow || draftOnly} name="scheduledFor" type="datetime-local" />
            </label>

            <label className="checkbox-row">
              <input
                checked={publishNow}
                name="publishNow"
                onChange={(event) => {
                  setPublishNow(event.target.checked);
                  if (event.target.checked) {
                    setDraftOnly(false);
                  }
                }}
                type="checkbox"
              />
              <span>Publish now</span>
            </label>

            <label className="checkbox-row">
              <input
                checked={draftOnly}
                name="draftOnly"
                onChange={(event) => {
                  setDraftOnly(event.target.checked);
                  if (event.target.checked) {
                    setPublishNow(false);
                  }
                }}
                type="checkbox"
              />
              <span>Draft only</span>
            </label>

            {missingAssetMessage ? (
              <div className="setup-panel" role="status">
                <strong>Asset needed</strong>
                <p>{missingAssetMessage}</p>
              </div>
            ) : null}

            <button className="primary-button" disabled={isScheduling} type="submit">
              {isScheduling ? "Scheduling..." : "Save Schedule"}
            </button>
          </form>
        </>
      )}

      {success ? (
        <section className="success-panel" role="status">
          <strong>Schedule saved</strong>
          <p>{success}</p>
        </section>
      ) : null}

      {error ? (
        <section className="error-panel" role="alert">
          <strong>Schedule needs attention</strong>
          <p>{error}</p>
        </section>
      ) : null}

      <section className="schedule-history-panel" aria-label="Scheduled posts history">
        <div className="result-section__header">
          <h3>Scheduled posts</h3>
          <span>{history.length}</span>
        </div>
        {isLoadingHistory ? <p>Loading schedule history...</p> : null}
        {!isLoadingHistory && history.length === 0 ? (
          <p>No scheduled posts yet. Saved drafts and scheduled posts will appear here.</p>
        ) : null}
        <div className="history-list">
          {history.map((post) => (
            <article className="history-card" key={post.id}>
              <div className="result-section__header">
                <h4>{formatContentType(post.contentType)}</h4>
                <span>{formatStatus(post.status)}</span>
              </div>
              <p>{post.postPreview}</p>
              <dl className="copy-preview-list">
                <div>
                  <dt>Platform</dt>
                  <dd>{formatPlatform(post.platform)}</dd>
                </div>
                <div>
                  <dt>Time</dt>
                  <dd>{post.scheduledFor ? formatDate(post.scheduledFor) : formatStatus(post.status)}</dd>
                </div>
                <div>
                  <dt>Caption</dt>
                  <dd>{post.caption}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}

function getMissingAssetMessage(
  contentType: ScheduleContentType,
  design: DesignGraphicResponse | null,
  reel: ReelPackage | null,
) {
  if ((contentType === "image_post" || contentType === "carousel") && !design) {
    return "Create a graphic before scheduling an image post or carousel.";
  }
  if (contentType === "reel" && !reel) {
    return "Create today's reel before scheduling a reel.";
  }
  return null;
}

function formatPlatform(platform: SchedulePlatform) {
  return {
    facebook: "Facebook",
    instagram: "Instagram",
    both: "Facebook and Instagram",
  }[platform];
}

function formatContentType(contentType: ScheduleContentType) {
  return {
    image_post: "Image post",
    carousel: "Carousel",
    reel: "Reel",
  }[contentType];
}

function formatStatus(status: ScheduledPost["status"]) {
  return {
    draft: "Draft",
    scheduled: "Scheduled",
    ready_to_publish: "Ready to publish locally",
  }[status];
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
