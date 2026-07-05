from invictus_os.agents.registry import build_agent_registry
from invictus_os.services.agent_service import AgentService


def test_orchestrator_agent_accepts_structured_task() -> None:
    service = AgentService(registry=build_agent_registry())

    result = service.run(
        agent_id="orchestrator",
        objective="Plan a research workflow",
        context={"priority": "high"},
    )

    assert result.status == "completed"
    assert result.agent_id == "orchestrator"
    assert result.evidence["next_action"] == "resolve-workflow"
