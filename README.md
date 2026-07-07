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
- **AI generation:** OpenAI Responses API using `gpt-5.5` by default
- **Design automation:** Canva Connect APIs with Brand Template Autofill
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
cp .env.example .env
```

Edit `backend/.env` and replace `sk-your-api-key-here` with your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-real-api-key
INVICTUS_OPENAI_MODEL=gpt-5.5
INVICTUS_OPENAI_TIMEOUT_SECONDS=30
```

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

### Canva Setup

The `Make Canva Graphic` workflow uses the official Canva Connect APIs. In production it creates a
design from a reusable Canva Brand Template using the Autofill API.

Add these values to `backend/.env`:

```bash
CANVA_ACCESS_TOKEN=your-canva-oauth-access-token
CANVA_BRAND_TEMPLATE_ID=your-canva-brand-template-id
INVICTUS_CANVA_HEADLINE_FIELD=HEADLINE
INVICTUS_CANVA_BODY_FIELD=BODY_TEXT
INVICTUS_CANVA_CTA_FIELD=CALL_TO_ACTION
INVICTUS_CANVA_GRAPHIC_TYPE_FIELD=GRAPHIC_TYPE
```

The Canva Brand Template should be a 1080x1350 portrait social graphic with autofill text fields
matching those names. The template should encode the reusable visual system: modern healthcare
branding, clean typography, strong hierarchy, and mobile-first composition for Instagram and
Facebook.

If Canva credentials are not configured, the dashboard shows a setup message instead of crashing.
