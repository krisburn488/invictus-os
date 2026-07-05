# InvictusOS Architecture

InvictusOS uses a layered architecture where the domain model remains independent from HTTP, UI, storage, model providers, and external integrations.

## Layers

- **Interface layer:** FastAPI routers and React pages.
- **Application layer:** Use cases that coordinate agents, workflows, and services.
- **Domain layer:** Agent contracts, workflow contracts, domain models, and policies.
- **Infrastructure layer:** Service adapters for model providers, persistence, tools, and external APIs.

## Agent Execution Flow

1. A client submits a structured task request through the API.
2. The API validates the request with Pydantic schemas.
3. The application service resolves an agent from the registry.
4. The agent runs against a typed task object.
5. The result is returned as a typed response with status and evidence.

## Workflow Execution Flow

Workflows compose agents into repeatable operating procedures. Early workflow execution is in-process and deterministic. The architecture leaves room for durable workflow engines, queues, and distributed workers without changing the public agent contract.
