import type { ContentGenerationRequest, ContentType, Platform } from "../types/content";

type ContentGeneratorFormProps = {
  initialValue: ContentGenerationRequest;
  onSubmit: (request: ContentGenerationRequest) => void;
};

const platforms: { label: string; value: Platform }[] = [
  { label: "Facebook", value: "facebook" },
  { label: "Instagram", value: "instagram" },
  { label: "LinkedIn", value: "linkedin" },
  { label: "All platforms", value: "all" },
];

const contentTypes: { label: string; value: ContentType }[] = [
  { label: "Post", value: "post" },
  { label: "Reel", value: "reel" },
  { label: "Carousel", value: "carousel" },
  { label: "Story", value: "story" },
];

export function ContentGeneratorForm({ initialValue, onSubmit }: ContentGeneratorFormProps) {
  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    onSubmit({
      businessName: String(data.get("businessName") ?? "").trim(),
      targetAudience: String(data.get("targetAudience") ?? "").trim(),
      topic: String(data.get("topic") ?? "").trim(),
      platform: String(data.get("platform") ?? "instagram") as Platform,
      contentType: String(data.get("contentType") ?? "post") as ContentType,
    });
  }

  return (
    <section className="generator-panel" aria-labelledby="generator-title">
      <div className="section-heading">
        <p className="eyebrow">Generate</p>
        <h2 id="generator-title">Today's content</h2>
      </div>

      <form className="content-form" onSubmit={handleSubmit}>
        <label>
          <span>Business name</span>
          <input
            defaultValue={initialValue.businessName}
            name="businessName"
            placeholder="Example: Bright Side Bakery"
            required
            type="text"
          />
        </label>

        <label>
          <span>Target audience</span>
          <input
            defaultValue={initialValue.targetAudience}
            name="targetAudience"
            placeholder="Example: busy parents in Austin"
            required
            type="text"
          />
        </label>

        <label>
          <span>Topic</span>
          <textarea
            defaultValue={initialValue.topic}
            name="topic"
            placeholder="Example: new weekend brunch menu"
            required
            rows={3}
          />
        </label>

        <div className="form-grid">
          <label>
            <span>Platform</span>
            <select defaultValue={initialValue.platform} name="platform">
              {platforms.map((platform) => (
                <option key={platform.value} value={platform.value}>
                  {platform.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Content type</span>
            <select defaultValue={initialValue.contentType} name="contentType">
              {contentTypes.map((contentType) => (
                <option key={contentType.value} value={contentType.value}>
                  {contentType.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <button className="primary-button" type="submit">
          Generate Content
        </button>
      </form>
    </section>
  );
}
