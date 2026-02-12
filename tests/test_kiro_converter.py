"""Tests for Kiro converter."""

import pytest
import json
from pathlib import Path
from agent_bridge.converters.kiro import KiroConverter


def test_convert_agent_creates_json(tmp_project):
    """Verify .kiro/agents/*.json created."""
    converter = KiroConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    
    agent_file = dest_root / ".kiro" / "agents" / "orchestrator.json"
    assert agent_file.exists()


def test_agent_json_has_required_fields(tmp_project):
    """Verify name, description, prompt, tools, allowedTools."""
    converter = KiroConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    agent_file = dest_root / ".kiro" / "agents" / "orchestrator.json"
    config = json.loads(agent_file.read_text())
    
    assert "name" in config
    assert "description" in config
    assert "prompt" in config
    assert "tools" in config
    assert "allowedTools" in config


def test_convert_skill_copies_directory(tmp_project):
    """Verify full skill dir copied."""
    converter = KiroConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    skill_file = dest_root / ".kiro" / "skills" / "clean-code" / "SKILL.md"
    assert skill_file.exists()
    
    content = skill_file.read_text()
    assert "Clean Code" in content


def test_convert_workflow_to_prompt(tmp_project):
    """Verify .kiro/prompts/ files with frontmatter."""
    converter = KiroConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    # Workflows go to both steering/ and prompts/
    prompt_file = dest_root / ".kiro" / "prompts" / "plan.md"
    assert prompt_file.exists()
    
    content = prompt_file.read_text()
    assert "---\n" in content  # Has frontmatter


def test_convert_to_kiro_full(tmp_project):
    """End-to-end with tmp_project."""
    converter = KiroConverter()
    source_root = tmp_project
    dest_root = tmp_project
    
    result = converter.convert(source_root, dest_root, verbose=False)
    
    assert result.ok is True
    assert result.agents == 2
    assert result.skills == 1
    # Kiro converts workflows to both prompts/ and steering/, so count may be 2
    assert result.workflows >= 1
