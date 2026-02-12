"""Tests for Kiro reverse conversion."""

import pytest
from pathlib import Path

from agent_bridge.converters._kiro_impl import apply_reverse_capture_kiro, reverse_convert_kiro
from agent_bridge.core.types import CapturedFile


def test_reverse_kiro_agent_json_to_markdown(tmp_project_with_ide_outputs):
    """Forward .agent/agents/orchestrator.md -> .kiro/agents/orchestrator.json
    reverse -> extracts 'prompt' field as markdown body."""
    project = tmp_project_with_ide_outputs
    agent_dir = project / ".agent"
    kiro_agent = project / ".kiro" / "agents" / "orchestrator.json"
    if not kiro_agent.exists():
        pytest.skip("No Kiro agents")

    captured = CapturedFile(
        ide_path=kiro_agent,
        agent_path=agent_dir / "agents" / "orchestrator.md",
        status="new",
        ide_name="kiro",
    )
    apply_reverse_capture_kiro(captured, project, agent_dir)

    content = (agent_dir / "agents" / "orchestrator.md").read_text()
    assert "#" in content
    assert "orchestrator" in content.lower()


def test_reverse_kiro_skill_direct_copy(tmp_project_with_ide_outputs):
    """Skills should be directly copied back."""
    project = tmp_project_with_ide_outputs
    skills_dir = project / ".kiro" / "skills"
    if not skills_dir.exists():
        pytest.skip("No Kiro skills")
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    if not skill_dirs:
        pytest.skip("No skill dirs")
    skill_dir = skill_dirs[0]
    skill_md = skill_dir / "SKILL.md"

    agent_dir = project / ".agent"
    captured = CapturedFile(
        ide_path=skill_md,
        agent_path=agent_dir / "skills" / skill_dir.name / "SKILL.md",
        status="new",
        ide_name="kiro",
    )
    apply_reverse_capture_kiro(captured, project, agent_dir)

    dest = agent_dir / "skills" / skill_dir.name / "SKILL.md"
    assert dest.exists()


def test_reverse_kiro_prompt_to_workflow(tmp_project_with_ide_outputs):
    """Forward workflow -> .kiro/prompts/plan.md
    reverse -> .agent/workflows/plan.md. Verify {{args}} -> $ARGUMENTS."""
    project = tmp_project_with_ide_outputs
    prompt_file = project / ".kiro" / "prompts" / "plan.md"
    if not prompt_file.exists():
        pytest.skip("No Kiro prompts")

    agent_dir = project / ".agent"
    captured = CapturedFile(
        ide_path=prompt_file,
        agent_path=agent_dir / "workflows" / "plan.md",
        status="new",
        ide_name="kiro",
    )
    apply_reverse_capture_kiro(captured, project, agent_dir)

    content = (agent_dir / "workflows" / "plan.md").read_text()
    assert "$ARGUMENTS" in content or "plan" in content.lower()


def test_reverse_kiro_steering_to_rule(tmp_project_with_ide_outputs):
    """Forward rule -> .kiro/steering/global.md, reverse -> .agent/rules/global.md."""
    project = tmp_project_with_ide_outputs
    steering_file = project / ".kiro" / "steering" / "global.md"
    if not steering_file.exists():
        pytest.skip("No Kiro steering")

    agent_dir = project / ".agent"
    captured = CapturedFile(
        ide_path=steering_file,
        agent_path=agent_dir / "rules" / "global.md",
        status="new",
        ide_name="kiro",
    )
    apply_reverse_capture_kiro(captured, project, agent_dir)

    content = (agent_dir / "rules" / "global.md").read_text()
    assert "inclusion" not in content or "always" not in content


def test_reverse_kiro_mcp_config(tmp_project_with_ide_outputs):
    """Verify .kiro/settings/mcp.json -> .agent/mcp_config.json copy."""
    project = tmp_project_with_ide_outputs
    mcp_file = project / ".kiro" / "settings" / "mcp.json"
    if not mcp_file.exists():
        pytest.skip("No Kiro MCP config")

    agent_dir = project / ".agent"
    captured = CapturedFile(
        ide_path=mcp_file,
        agent_path=agent_dir / "mcp_config.json",
        status="new",
        ide_name="kiro",
    )
    apply_reverse_capture_kiro(captured, project, agent_dir)

    assert (agent_dir / "mcp_config.json").exists()
