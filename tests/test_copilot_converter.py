"""Tests for Copilot converter."""

import pytest
from pathlib import Path
from agent_bridge.converters.copilot import CopilotConverter


def test_convert_agent_creates_frontmatter(tmp_project):
    """Convert an agent file, verify YAML frontmatter with name, description, tools."""
    converter = CopilotConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    
    agent_file = dest_root / ".github" / "agents" / "orchestrator.md"
    assert agent_file.exists()
    
    content = agent_file.read_text()
    assert content.startswith("---\n")
    assert "name:" in content
    assert "description:" in content
    assert "tools:" in content


def test_convert_agent_preserves_body(tmp_project):
    """Verify markdown body is preserved after frontmatter."""
    converter = CopilotConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    agent_file = dest_root / ".github" / "agents" / "orchestrator.md"
    content = agent_file.read_text()
    
    # Body should be preserved
    assert "You are the orchestrator agent" in content


def test_convert_skill_creates_skill_dir(tmp_project):
    """Verify SKILL.md is created in dest."""
    converter = CopilotConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    skill_file = dest_root / ".github" / "skills" / "clean-code" / "SKILL.md"
    assert skill_file.exists()
    
    content = skill_file.read_text()
    assert "Clean Code" in content


def test_convert_workflow_creates_prompt_file(tmp_project):
    """Verify .prompt.md extension."""
    converter = CopilotConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    prompt_file = dest_root / ".github" / "prompts" / "plan.prompt.md"
    assert prompt_file.exists()


def test_convert_to_copilot_full(tmp_project):
    """End-to-end with tmp_project, verify all expected files exist."""
    converter = CopilotConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    assert result.agents == 2
    assert result.skills == 1
    assert result.workflows == 1


def test_copilot_truncation(tmp_project):
    """Create agent with >30000 chars, verify truncation."""
    # Create large agent file
    large_content = "# Large Agent\n\n" + ("x" * 35000)
    agent_file = tmp_project / ".agent" / "agents" / "large.md"
    agent_file.write_text(large_content)
    
    converter = CopilotConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    output_file = dest_root / ".github" / "agents" / "large.md"
    assert output_file.exists()
    
    content = output_file.read_text()
    # Should be truncated (allow small overhead for frontmatter)
    assert len(content) < 35000
    assert "(truncated)" in content or len(content) <= 31000  # Allow frontmatter overhead
