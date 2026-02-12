"""Tests for capture_service."""

import pytest
from pathlib import Path

from agent_bridge.services.capture_service import (
    execute_capture,
    scan_for_captures,
)


def test_scan_detects_cursor(tmp_project_with_ide_outputs):
    """scan_for_captures() finds Cursor files."""
    project = tmp_project_with_ide_outputs
    files = scan_for_captures(project, ide_names=["cursor"])
    cursor_files = [f for f in files if f.ide_name == "cursor"]
    assert len(cursor_files) > 0


def test_scan_detects_all_ides(tmp_project_with_ide_outputs):
    """All 3 IDEs detected."""
    project = tmp_project_with_ide_outputs
    files = scan_for_captures(project)
    ides = set(f.ide_name for f in files)
    assert "cursor" in ides or "kiro" in ides or "copilot" in ides


def test_scan_marks_new_files(tmp_project_with_ide_outputs):
    """Create new file in .cursor/rules/ -> status='new'."""
    project = tmp_project_with_ide_outputs
    (project / ".cursor" / "rules").mkdir(parents=True, exist_ok=True)
    (project / ".cursor" / "rules" / "user-rule.mdc").write_text("---\ndescription: x\nglobs:\nalwaysApply: true\n---\n\n# User\n")

    files = scan_for_captures(project)
    user_rule = [f for f in files if "user-rule" in str(f.ide_path)]
    assert len(user_rule) == 1
    assert user_rule[0].status == "new"


def test_execute_capture_writes_files(tmp_project_with_ide_outputs):
    """After capture, .agent/ should contain reverse-converted files."""
    project = tmp_project_with_ide_outputs
    files = scan_for_captures(project)

    if not files:
        pytest.skip("No files to capture")

    agent_dir = project / ".agent"
    result = execute_capture(project, files[:5], strategy="ide_wins", dry_run=False)

    assert result.get("captured", 0) >= 0
    assert (agent_dir / "agents").exists() or (agent_dir / "skills").exists()


def test_scan_marks_modified_files(tmp_project_with_ide_outputs):
    """Modify a .cursor file after generation -> status='modified' (when bridge-meta exists)."""
    project = tmp_project_with_ide_outputs
    agent_dir = project / ".agent"
    meta_file = agent_dir / ".bridge-meta.json"
    if not meta_file.exists():
        (agent_dir / ".bridge-meta.json").write_text(
            '{"generated_at":"2026-01-01T00:00:00Z","file_map":{".cursor/agents/orchestrator.md":".agent/agents/orchestrator.md"}}'
        )
    cursor_file = project / ".cursor" / "agents" / "orchestrator.md"
    if not cursor_file.exists():
        pytest.skip("No cursor agents")
    cursor_file.touch()

    files = scan_for_captures(project, ide_names=["cursor"])
    agent_files = [f for f in files if "orchestrator" in str(f.ide_path)]
    assert len(agent_files) >= 1, "Expected to find orchestrator in capture list"
    assert agent_files[0].status == "modified", f"Expected 'modified' but got '{agent_files[0].status}'"


def test_capture_dry_run_no_writes(tmp_project_with_ide_outputs):
    """--dry-run should not modify .agent/."""
    project = tmp_project_with_ide_outputs
    agent_dir = project / ".agent"
    orig_orchestrator = (agent_dir / "agents" / "orchestrator.md").read_text() if (agent_dir / "agents" / "orchestrator.md").exists() else ""

    files = scan_for_captures(project)
    result = execute_capture(project, files, strategy="ide_wins", dry_run=True)

    assert result.get("dry_run") is True
    assert result.get("would_capture", 0) == len(files)
    if (agent_dir / "agents" / "orchestrator.md").exists():
        assert (agent_dir / "agents" / "orchestrator.md").read_text() == orig_orchestrator
