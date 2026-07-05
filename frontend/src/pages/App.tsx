import { CalendarClock, Clapperboard, Image, PenLine, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { ActionButton } from "../components/ActionButton";
import { ActivityFeed } from "../components/ActivityFeed";
import { ContentGeneratorForm } from "../components/ContentGeneratorForm";
import { GeneratedContentResults } from "../components/GeneratedContentResults";
import { StatusPanel } from "../components/StatusPanel";
import { WorkflowCard } from "../components/WorkflowCard";
import { useAgents } from "../hooks/useAgents";
import { contentGenerator } from "../services/contentGenerator";
import type { ContentGenerationRequest, GeneratedContent } from "../types/content";
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
    detail: "InvictusOS prepared a Canva-ready graphic brief with layout and copy direction.",
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

  function handleGenerateContent(request: ContentGenerationRequest) {
    const result = contentGenerator.generate(request);
    setContentRequest(request);
    setGeneratedContent(result);
    handleAction(
      "Generate Today's Content",
      `Generated ${request.contentType} content for ${request.businessName} on ${request.topic}.`,
    );
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
              onSubmit={handleGenerateContent}
            />
          ) : null}
          {generatedContent ? <GeneratedContentResults content={generatedContent} /> : null}
          <WorkflowCard steps={workflowSteps} />
          <ActivityFeed items={activity} />
        </section>
      </section>
    </main>
  );
}
