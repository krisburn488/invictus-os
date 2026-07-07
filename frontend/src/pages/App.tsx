import { CalendarClock, Clapperboard, Image, PenLine, Settings, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";

import { ActionButton } from "../components/ActionButton";
import { ActivityFeed } from "../components/ActivityFeed";
import { ContentGeneratorForm } from "../components/ContentGeneratorForm";
import { DesignGraphicWorkflow } from "../components/DesignGraphicWorkflow";
import { GeneratedContentResults } from "../components/GeneratedContentResults";
import { ReelWorkflow } from "../components/ReelWorkflow";
import { ScheduleWorkflow } from "../components/ScheduleWorkflow";
import { SettingsPage } from "../components/SettingsPage";
import { StatusPanel } from "../components/StatusPanel";
import { WorkflowCard } from "../components/WorkflowCard";
import { useAgents } from "../hooks/useAgents";
import { contentGenerator } from "../services/contentGenerator";
import { createDesignGraphic } from "../services/design";
import { createTodayReel } from "../services/reel";
import { listScheduledPosts, schedulePost } from "../services/schedule";
import { getSettings, saveSettings } from "../services/settings";
import type { ContentGenerationRequest, GeneratedContent } from "../types/content";
import type { DesignGraphicResponse, GraphicType } from "../types/design";
import type { ReelFormat, ReelPackage } from "../types/reel";
import type { ScheduleContentType, SchedulePlatform, ScheduledPost } from "../types/schedule";
import type { AppSettings, SettingsFormValue } from "../types/settings";
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
  {
    title: "Settings",
    description: "Configure providers and brand profile.",
    icon: Settings,
    detail: "InvictusOS opened local settings for provider, brand, and business profile configuration.",
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
  const [reelResult, setReelResult] = useState<ReelPackage | null>(null);
  const [reelError, setReelError] = useState<string | null>(null);
  const [isCreatingReel, setIsCreatingReel] = useState(false);
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [scheduleSuccess, setScheduleSuccess] = useState<string | null>(null);
  const [isScheduling, setIsScheduling] = useState(false);
  const [isLoadingSchedule, setIsLoadingSchedule] = useState(false);
  const [appSettings, setAppSettings] = useState<AppSettings | null>(null);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);
  const [isLoadingSettings, setIsLoadingSettings] = useState(false);
  const [isSavingSettings, setIsSavingSettings] = useState(false);

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

  function openReelWorkflow() {
    setActiveAction("Create Today's Reel");
    setReelError(null);
  }

  function openScheduleWorkflow() {
    setActiveAction("Schedule Posts");
    setScheduleError(null);
    void loadScheduledPosts();
  }

  function openSettingsPage() {
    setActiveAction("Settings");
    setSettingsError(null);
    setSettingsSuccess(null);
    void loadSettings();
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

  async function handleCreateReel(reelFormat: ReelFormat) {
    if (!generatedContent) {
      setReelError("Generate today's content first, then create a reel.");
      return;
    }

    setReelError(null);
    setReelResult(null);
    setIsCreatingReel(true);

    try {
      const result = await createTodayReel({ content: generatedContent, reelFormat });
      setReelResult(result);
      handleAction(
        "Create Today's Reel",
        `Created a ${result.durationSeconds}-second ${formatReelLabel(reelFormat)} reel package.`,
      );
    } catch (error) {
      setReelError(
        error instanceof Error
          ? error.message
          : "InvictusOS could not create today's reel. Please try again.",
      );
    } finally {
      setIsCreatingReel(false);
    }
  }

  async function loadScheduledPosts() {
    setIsLoadingSchedule(true);
    try {
      setScheduledPosts(await listScheduledPosts());
    } catch (error) {
      setScheduleError(
        error instanceof Error
          ? error.message
          : "InvictusOS could not load scheduled posts. Please try again.",
      );
    } finally {
      setIsLoadingSchedule(false);
    }
  }

  async function handleSchedulePost(request: {
    platform: SchedulePlatform;
    contentType: ScheduleContentType;
    scheduledFor?: string;
    publishNow: boolean;
    draftOnly: boolean;
  }) {
    if (!generatedContent) {
      setScheduleError("Generate today's content before scheduling posts.");
      return;
    }

    setScheduleError(null);
    setScheduleSuccess(null);
    setIsScheduling(true);

    try {
      const result = await schedulePost({
        ...request,
        content: generatedContent,
        design: designResult ?? undefined,
        reel: reelResult ?? undefined,
      });
      setScheduledPosts((posts) => [result, ...posts.filter((post) => post.id !== result.id)]);
      setScheduleSuccess(`Saved ${formatScheduleStatus(result.status)} for ${formatPlatform(result.platform)}.`);
      handleAction("Schedule Posts", `Saved ${formatContentType(result.contentType)} to local schedule history.`);
    } catch (error) {
      setScheduleError(
        error instanceof Error
          ? error.message
          : "InvictusOS could not schedule the post. Please try again.",
      );
    } finally {
      setIsScheduling(false);
    }
  }

  async function loadSettings() {
    setIsLoadingSettings(true);
    try {
      setAppSettings(await getSettings());
    } catch (error) {
      setSettingsError(
        error instanceof Error ? error.message : "InvictusOS could not load settings. Please try again.",
      );
    } finally {
      setIsLoadingSettings(false);
    }
  }

  async function handleSaveSettings(value: SettingsFormValue) {
    setSettingsError(null);
    setSettingsSuccess(null);
    setIsSavingSettings(true);

    try {
      const result = await saveSettings(value);
      setAppSettings(result);
      setSettingsSuccess("Local settings were saved.");
      handleAction("Settings", "Updated local provider, brand, and business profile settings.");
    } catch (error) {
      setSettingsError(
        error instanceof Error ? error.message : "InvictusOS could not save settings. Please try again.",
      );
    } finally {
      setIsSavingSettings(false);
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
                    : action.title === "Create Today's Reel"
                      ? openReelWorkflow
                    : action.title === "Make Canva Graphic"
                      ? openDesignGraphic
                    : action.title === "Schedule Posts"
                      ? openScheduleWorkflow
                    : action.title === "Settings"
                      ? openSettingsPage
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
          {activeAction === "Create Today's Reel" ? (
            <ReelWorkflow
              content={generatedContent}
              error={reelError}
              isCreating={isCreatingReel}
              onSubmit={handleCreateReel}
              result={reelResult}
            />
          ) : null}
          {activeAction === "Schedule Posts" ? (
            <ScheduleWorkflow
              content={generatedContent}
              design={designResult}
              error={scheduleError}
              history={scheduledPosts}
              isLoadingHistory={isLoadingSchedule}
              isScheduling={isScheduling}
              onSubmit={handleSchedulePost}
              reel={reelResult}
              success={scheduleSuccess}
            />
          ) : null}
          {activeAction === "Settings" ? (
            <SettingsPage
              error={settingsError}
              isLoading={isLoadingSettings}
              isSaving={isSavingSettings}
              onSubmit={handleSaveSettings}
              settings={appSettings}
              success={settingsSuccess}
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

function formatReelLabel(reelFormat: ReelFormat) {
  return {
    talking_head: "talking head",
    ai_avatar: "AI avatar",
    b_roll: "B-roll",
  }[reelFormat];
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
    image_post: "image post",
    carousel: "carousel",
    reel: "reel",
  }[contentType];
}

function formatScheduleStatus(status: ScheduledPost["status"]) {
  return {
    draft: "a draft",
    scheduled: "a scheduled post",
    ready_to_publish: "a local publish-now post",
  }[status];
}
