# InvictusOS

InvictusOS is a long-term AI operating system architecture for coordinating specialized agents, deterministic workflows, and human-controlled automation. The project is designed around clear boundaries: agents reason and propose actions, workflows orchestrate repeatable processes, services integrate with external systems, and the API exposes controlled capabilities to the interface.

## Vision

InvictusOS exists to become a dependable command layer for high-leverage work. Its goal is not a single chatbot, but an operating system for AI-assisted execution: durable memory, agent specialization, auditable workflows, user approval gates, and interfaces that make complex automation understandable.

The product direction favors reliability over novelty. Every agent should have a defined role, bounded inputs, explicit outputs, and measurable behavior. Every workflow should be observable, resumable, and safe to run in production environments.

## Architecture

The repository follows Clean Architecture principles:

- **Core** contains business rules, ports, and orchestration contracts that do not depend on frameworks.
- **Agents** implement role-specific capabilities behind stable interfaces.
- **Workflows** coordinate agents and services into repeatable execution plans.
- **Services** adapt infrastructure, model providers, storage, search, notifications, and integrations.
- **API** exposes application capabilities through FastAPI routers.
- **Schemas** define external request and response boundaries.
- **Models** define internal domain objects.
- **Frontend** provides the operator console using React and TypeScript.

Dependencies point inward. Frameworks and infrastructure can change without rewriting the core agent and workflow model.

## Technology Stack

- **Backend:** Python 3.12, FastAPI, Pydantic Settings, Uvicorn
- **Frontend:** React 18, TypeScript, Vite
- **AI generation:** OpenAI Responses API using the model configured in Settings, `gpt-5.5` by default
- **Design automation:** Internal AI-assisted graphic generator with SVG-to-PNG export
- **Architecture:** Clean Architecture, typed ports, modular agents, explicit workflow definitions
- **Quality:** Ruff, Pytest, strict TypeScript, production-oriented configuration

## Folder Structure

```text
.
├── agents/                  # Repository-level agent manifests and operating contracts
├── prompts/                 # Versioned system and agent prompt assets
├── workflows/               # Repository-level workflow definitions
├── assets/                  # Shared brand and product assets
├── config/                  # Environment-neutral configuration templates
├── frontend/                # React + TypeScript operator console
├── backend/                 # FastAPI application and domain architecture
└── docs/                    # Architecture and operating documentation
```

Backend package layout:

```text
backend/src/invictus_os/
├── api/        # FastAPI routers and HTTP dependencies
├── core/       # Framework-independent contracts and use cases
├── agents/     # Agent implementations and registry
├── workflows/  # Workflow orchestration
├── services/   # Infrastructure adapters
├── models/     # Domain models
├── schemas/    # API schemas
├── config/     # Runtime settings
└── utilities/  # Cross-cutting helpers
```

Frontend source layout:

```text
frontend/src/
├── components/ # Reusable interface components
├── pages/      # Route-level pages
├── hooks/      # Stateful UI hooks
├── services/   # API clients and integration code
├── types/      # Shared TypeScript contracts
├── assets/     # Frontend-specific assets
└── styles/     # Global styling
```

## Agent System Philosophy

Agents in InvictusOS are modular operators, not hidden scripts. Each agent declares:

- a stable identifier
- a purpose
- explicit capabilities
- accepted task shape
- structured result shape
- operational constraints

The backend registry resolves agents by identifier and executes them through a common interface. This makes agents testable, replaceable, and composable inside workflows. Long-term, agents should emit traces, confidence signals, cost metadata, and policy decisions for every run.

## Adding New Agents

1. Define the agent contract in `backend/src/invictus_os/agents/`.
2. Implement the `Agent` protocol from `backend/src/invictus_os/core/ports.py`.
3. Register the implementation in `backend/src/invictus_os/agents/registry.py`.
4. Add a repository-level manifest under `agents/` describing purpose, inputs, outputs, and constraints.
5. Add or update prompts under `prompts/` when the agent depends on language-model instructions.
6. Add workflow coverage when the agent participates in orchestration.
7. Add tests for the agent behavior and failure handling.

## Development Standards

- Keep domain logic independent of FastAPI, React, databases, and model vendors.
- Keep model provider integrations behind modular service interfaces so providers can be replaced.
- Store API keys and secrets in environment variables only. Never commit real secrets.
- Prefer typed request and response objects over unstructured dictionaries.
- Treat prompts as versioned product assets.
- Make automation auditable: every workflow should expose status, decisions, and results.
- Avoid implicit side effects. External actions should be represented as services and governed by policy.
- Keep UI states explicit: loading, success, empty, degraded, and failure states should be intentional.
- Changes should include focused tests when behavior is added or modified.

## Long-Term Roadmap

- Durable workflow execution with resumable state
- Persistent memory and retrieval with access controls
- Agent evaluation harness and regression scoring
- Human approval gates for sensitive operations
- Multi-agent planning with execution tracing
- Secure integration adapters for GitHub, local files, cloud services, and communication tools
- Policy engine for permissions, risk scoring, and action governance
- Observability for cost, latency, model usage, and workflow outcomes
- Desktop-grade operator console for monitoring and directing AI work

## Future Automation Goals

InvictusOS should eventually coordinate end-to-end work across software delivery, research, operations, and personal productivity. Automation will be introduced behind explicit contracts: inspect, plan, approve, execute, verify, and record. The system should be able to explain what happened, why it happened, which agent performed it, and what evidence supports the outcome.

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

OpenAI configuration is managed inside the dashboard, not `backend/.env`. Start the backend and
frontend, open `Settings`, then configure:

- OpenAI API key
- OpenAI model, such as `gpt-5.5`
- Temperature for models that support it
- Max output tokens

Then start the backend:

```bash
uvicorn invictus_os.api.app:create_app --factory --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The dashboard calls the FastAPI backend at `http://127.0.0.1:8000` by default. To point the
frontend at a different backend, set `VITE_API_BASE_URL`.

## Vercel Deployment

InvictusOS can be deployed as two separate Vercel projects from the same repository:

- **invictus-os-frontend:** set the Vercel project root directory to `frontend`
- **invictus-os-backend:** set the Vercel project root directory to `backend`

The repository root is not a production Vercel project. Deploy only the `frontend` and `backend`
directories as separate projects. Full click-by-click instructions are in
[`docs/vercel-deployment.md`](docs/vercel-deployment.md).

The frontend is a Vite app and reads the backend URL from `VITE_API_BASE_URL`. In the frontend
Vercel project, set `VITE_API_BASE_URL` to the deployed backend project URL, for example:

```text
https://your-backend-project.vercel.app
```

The frontend project includes `frontend/vercel.json`, so Vercel can detect the Vite build when the
project root is set to `frontend`. It builds with `npm run build` and serves `frontend/dist`.

The backend allows localhost origins and Vercel app domains by default. For a custom frontend domain,
set `INVICTUS_CORS_ORIGINS` in the backend Vercel project to a JSON list of allowed origins:

```text
["https://your-frontend-domain.com","https://your-frontend-project.vercel.app"]
```

In the backend Vercel project, set `OPENAI_API_KEY` to the OpenAI project key used for generation.
The dashboard Settings page can still store a local key during development, but Vercel production
should use environment variables for secrets.

To return completed AI-generated MP4 reels, set `HIGGSFIELD_MCP_BRIDGE_URL` on the backend project
to a server-side bridge that can invoke the connected Higgsfield MCP `generate_video` tool. Without
that bridge, Invictus OS still generates the reel package and shows a retryable video setup message.

The backend is a FastAPI app. Its Vercel entrypoint is declared in `backend/pyproject.toml` as:

```toml
[tool.vercel]
entrypoint = "src.invictus_os.api.app:app"
```

This tells Vercel how to find the FastAPI `app` instance when `backend` is deployed as its own
project root.

### Graphic Generation

The `Make Canva Graphic` workflow uses the generated content from `Generate Today's Content` and
creates finished 1080x1350 Instagram/Facebook graphics internally. It extracts the headline, body
text, and call to action, then generates previewable SVG slides that the dashboard exports as PNGs.

Supported formats:

- Single Post
- Carousel
- Quote Graphic

The design system is built around Invictus Wellness branding: white backgrounds, blue and green
accents, professional typography, strong hierarchy, and mobile-first composition. The backend design
service is provider-neutral so a future Canva, Figma, or image-model provider can be added behind
the same service boundary.

### Local Scheduling

The `Schedule Posts` workflow is a local scheduling system. It stores drafts, scheduled posts, and
publish-now records in `backend/.local/scheduled_posts.json`, which is intentionally ignored by git.

The scheduler can attach the content generated in the dashboard, generated graphic packages, captions,
hashtags, and reel packages. It supports Facebook, Instagram, or both; image posts, carousels, and
reels; scheduled date/time; publish-now records; and draft-only records.

Meta publishing is not connected yet. The backend exposes a provider-neutral `ScheduleService` so a
future Meta publishing adapter can be added without rewriting the dashboard workflow.

### Local Settings

The `Settings` page stores local provider, brand, and business profile configuration in
`backend/.local/app_settings.json`, which is intentionally ignored by git.

Settings currently include OpenAI, Meta, and Higgsfield credential fields; brand logo, colors, and
fonts; and the business profile fields used by future automation: business name, website, booking
URL, office phone, office address, accepted insurance list, default CTA, and posting schedule.

Sensitive values are write-only from the dashboard. The API stores them locally but only returns
configured status plus masked values, so API keys and app secrets are not sent back to the browser
after saving. Meta and Higgsfield credentials are stored for future integrations and are not used
for publishing yet.

OpenAI generation for content, graphic specifications, and reel packages reads credentials and model
settings from this local Settings store. If no OpenAI key is configured, the dashboard shows a
friendly setup message instead of crashing.
