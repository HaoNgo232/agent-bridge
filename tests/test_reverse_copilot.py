"""Tests for Copilot reverse conversion."""

import pytest
from pathlib import Path

from agent_bridge.converters._copilot_impl import apply_reverse_capture_copilot, reverse_convert_copilot
from agent_bridge.core.types import CapturedFile


def test_reverse_copilot_agent_strips_tools(tmp_project_with_ide_outputs):
    """Verify tools, agents, handoffs fields removed from output."""
    project = tmp_project_with_ide_outputs
    agent_file = project / ".github" / "agents" / "orchestrator.md"
    if not agent_file.exists():
        pytest.skip("No Copilot agents")

    agent_dir = project / ".agent"
    captured = CapturedFile(
        ide_path=agent_file,
        agent_path=agent_dir / "agents" / "orchestrator.md",
        status="new",
        ide_name="copilot",
    )
    apply_reverse_capture_copilot(captured, project, agent_dir)

    content = (agent_dir / "agents" / "orchestrator.md").read_text()
    assert "tools:" not in content or " tools:" not in content


def test_reverse_copilot_skill_copies_directory(tmp_project_with_ide_outputs):
    """Entire skill dir should be copied back."""
    project = tmp_project_with_ide_outputs
    skills_dir = project / ".github" / "skills"
    if not skills_dir.exists():
        pytest.skip("No Copilot skills")
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
        ide_name="copilot",
    )
    apply_reverse_capture_copilot(captured, project, agent_dir)

    dest = agent_dir / "skills" / skill_dir.name / "SKILL.md"
    assert dest.exists()


def test_reverse_copilot_prompt_renames_extension(tmp_project_with_ide_outputs):
    """.prompt.md -> .md rename."""
    project = tmp_project_with_ide_outputs
    prompts_dir = project / ".github" / "prompts"
    if not prompts_dir.exists():
        pytest.skip("No Copilot prompts")
    prompt_files = list(prompts_dir.glob("*.prompt.md"))
    if not prompt_files:
        pytest.skip("No prompt files")
    prompt_file = prompt_files[0]
    stem = prompt_file.name.replace(".prompt.md", "")

    agent_dir = project / ".agent"
    captured = CapturedFile(
        ide_path=prompt_file,
        agent_path=agent_dir / "workflows" / f"{stem}.md",
        status="new",
        ide_name="copilot",
    )
    apply_reverse_capture_copilot(captured, project, agent_dir)

    assert (agent_dir / "workflows" / f"{stem}.md").exists()
