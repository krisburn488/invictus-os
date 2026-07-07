import { CalendarClock, Clapperboard, Image, PenLine, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { ActionButton } from "../components/ActionButton";
import { ActivityFeed } from "../components/ActivityFeed";
import { ContentGeneratorForm } from "../components/ContentGeneratorForm";
import { DesignGraphicWorkflow } from "../components/DesignGraphicWorkflow";
import { GeneratedContentResults } from "../components/GeneratedContentResults";
import { StatusPanel } from "../components/StatusPanel";
import { WorkflowCard } from "../components/WorkflowCard";
import { useAgents } from "../hooks/useAgents";
import { contentGenerator } from "../services/contentGenerator";
import { createDesignGraphic } from "../services/design";
import type { ContentGenerationRequest, GeneratedContent } from "../types/content";
import type { DesignGraphicResponse, GraphicType } from "../types/design";
import type { ActivityItem, WorkflowStep } from "../types/system";

const actions = [
  {
    title: "Generate Today's Content",
    description: "Create a simple content plan for the day.",
    icon: Sparkles,
    detail: "InvictusOS drafted a daily content plan with topics, format, and priority.",
  },
  {
    title: "Create Today's Reel",
    description: "Outline a short-form video.",
    icon: Clapperboard,
    detail: "InvictusOS created a reel concept with hook, scene beats, and call to action.",
  },
  {
    title: "Make Canva Graphic",
    description: "Prepare a graphic brief.",
    icon: Image,
    detail: "InvictusOS created a finished graphic with layout and copy direction.",
  },
  {
    title: "Write Caption",
    description: "Draft social post copy.",
    icon: PenLine,
    detail: "InvictusOS wrote a concise caption with a friendly tone and clear next step.",
  },
  {
    title: "Schedule Posts",
    description: "Organize publishing order.",
    icon: CalendarClock,
    detail: "InvictusOS arranged the content queue into a simple publishing schedule.",
  },
];

const startingActivity: ActivityItem[] = [
  {
    id: "welcome",
    time: "Ready",
    title: "Dashboard loaded",
    detail: "Choose an action to start building today's content workflow.",
  },
];

const defaultContentRequest: ContentGenerationRequest = {
  businessName: "",
  targetAudience: "",
  topic: "",
  platform: "instagram",
  contentType: "post",
};

export function App() {
  const { agents, state } = useAgents();
  const [activeAction, setActiveAction] = useState("Choose a workflow action");
  const [activity, setActivity] = useState<ActivityItem[]>(startingActivity);
  const [contentRequest, setContentRequest] =
    useState<ContentGenerationRequest>(defaultContentRequest);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [contentError, setContentError] = useState<string | null>(null);
  const [isGeneratingContent, setIsGeneratingContent] = useState(false);
  const [designResult, setDesignResult] = useState<DesignGraphicResponse | null>(null);
  const [designError, setDesignError] = useState<string | null>(null);
  const [isCreatingDesignGraphic, setIsCreatingDesignGraphic] = useState(false);

  const workflowSteps = useMemo<WorkflowStep[]>(
    () =>
      actions.map((action) => ({
        name: action.title,
        status:
          activeAction === action.title
            ? "active"
            : activity.some((item) => item.title === action.title)
              ? "ready"
              : "waiting",
        statusLabel:
          activeAction === action.title
            ? "In focus"
            : activity.some((item) => item.title === action.title)
              ? "Prepared"
              : "Waiting",
      })),
    [activeAction, activity],
  );

  function handleAction(title: string, detail: string) {
    const timestamp = new Intl.DateTimeFormat("en", {
      hour: "numeric",
      minute: "2-digit",
    }).format(new Date());

    setActiveAction(title);
    setActivity((items) => [
      {
        id: `${title}-${Date.now()}`,
        time: timestamp,
        title,
        detail,
      },
      ...items.filter((item) => item.id !== "welcome"),
    ]);
  }

  function openContentGenerator() {
    setActiveAction("Generate Today's Content");
  }

  function openDesignGraphic() {
    setActiveAction("Make Canva Graphic");
    setDesignError(null);
  }

  async function handleGenerateContent(request: ContentGenerationRequest) {
    setContentRequest(request);
    setGeneratedContent(null);
    setContentError(null);
    setIsGeneratingContent(true);

    try {
      const result = await contentGenerator.generate(request);
      setGeneratedContent(result);
      handleAction(
        "Generate Today's Content",
        `Generated ${request.contentType} content for ${request.businessName} on ${request.topic}.`,
      );
    } catch (error) {
      setContentError(
        error instanceof Error
          ? error.message
          : "InvictusOS could not generate content. Please try again.",
      );
    } finally {
      setIsGeneratingContent(false);
    }
  }

  async function handleCreateDesignGraphic(graphicType: GraphicType) {
    if (!generatedContent) {
      setDesignError("Generate today's content first, then create a graphic.");
      return;
    }

    setDesignError(null);
    setDesignResult(null);
    setIsCreatingDesignGraphic(true);

    try {
      const result = await createDesignGraphic({ content: generatedContent, graphicType });
      setDesignResult(result);
      handleAction(
        "Make Canva Graphic",
        `Created ${result.slides.length} ${graphicType} graphic${
          result.slides.length === 1 ? "" : "s"
        } from today's content.`,
      );
    } catch (error) {
      setDesignError(
        error instanceof Error
          ? error.message
          : "InvictusOS could not create the graphic. Please try again.",
      );
    } finally {
      setIsCreatingDesignGraphic(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="masthead">
        <div>
          <p className="eyebrow">InvictusOS</p>
          <h1>Daily content command center.</h1>
          <p className="lede">
            A simple MVP dashboard for planning, creating, and scheduling social content with
            guided AI workflow actions.
          </p>
        </div>
        <StatusPanel state={state} />
      </section>

      <section className="dashboard-grid" aria-label="InvictusOS content dashboard">
        <section className="action-panel" aria-labelledby="actions-title">
          <div className="section-heading">
            <p className="eyebrow">Actions</p>
            <h2 id="actions-title">Start here</h2>
          </div>
          <div className="action-list">
            {actions.map((action) => (
              <ActionButton
                description={action.description}
                icon={action.icon}
                key={action.title}
                onClick={
                  action.title === "Generate Today's Content"
                    ? openContentGenerator
                    : action.title === "Make Canva Graphic"
                      ? openDesignGraphic
                    : () => handleAction(action.title, action.detail)
                }
                title={action.title}
              />
            ))}
          </div>
        </section>

        <section className="overview-panel" aria-label="Dashboard overview">
          <div className="current-focus">
            <p className="eyebrow">Current focus</p>
            <h2>{activeAction}</h2>
            <p>
              {agents.length} backend agent{agents.length === 1 ? "" : "s"} connected for
              workflow orchestration.
            </p>
          </div>
          {activeAction === "Generate Today's Content" ? (
            <ContentGeneratorForm
              initialValue={contentRequest}
              isGenerating={isGeneratingContent}
              onSubmit={handleGenerateContent}
            />
          ) : null}
          {activeAction === "Make Canva Graphic" ? (
            <DesignGraphicWorkflow
              content={generatedContent}
              error={designError}
              isCreating={isCreatingDesignGraphic}
              onSubmit={handleCreateDesignGraphic}
              result={designResult}
            />
          ) : null}
          {contentError ? (
            <section className="error-panel" role="alert">
              <strong>Content generation needs attention</strong>
              <p>{contentError}</p>
            </section>
          ) : null}
          {generatedContent ? <GeneratedContentResults content={generatedContent} /> : null}
          <WorkflowCard steps={workflowSteps} />
          <ActivityFeed items={activity} />
        </section>
      </section>
    </main>
  );
}
