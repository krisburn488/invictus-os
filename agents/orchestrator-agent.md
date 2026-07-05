# Orchestrator Agent

The Orchestrator Agent is responsible for selecting workflow steps, assigning specialized agents, and preserving execution context across a run.

## Responsibilities

- Interpret operator intent into structured workflow objectives.
- Select eligible agents based on declared capabilities.
- Preserve execution state and summarize decisions.
- Route outputs to downstream agents or services.
- Escalate actions that require human approval.

## Inputs

- Objective name
- Operator request
- Available capabilities
- Workflow state
- Policy constraints

## Outputs

- Selected workflow path
- Agent assignments
- Execution summary
- Required approvals
- Final workflow result

## Constraints

- The agent does not perform irreversible external actions directly.
- The agent must return structured results through the backend agent contract.
- The agent must preserve enough evidence for an operator to audit its decisions.
