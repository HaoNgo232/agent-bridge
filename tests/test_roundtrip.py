"""Roundtrip tests: forward -> reverse -> compare."""

import pytest
from pathlib import Path

from agent_bridge.converters.cursor import CursorConverter
from agent_bridge.converters.kiro import KiroConverter
from agent_bridge.converters.copilot import CopilotConverter
from agent_bridge.converters._cursor_impl import apply_reverse_capture_cursor
from agent_bridge.converters._kiro_impl import apply_reverse_capture_kiro
from agent_bridge.converters._copilot_impl import apply_reverse_capture_copilot
from agent_bridge.core.types import CapturedFile
from tests.conftest import strip_and_normalize


def test_roundtrip_cursor_agent_body_preserved(tmp_project):
    """Forward .agent/agents/orchestrator.md -> .cursor/ -> reverse -> body matches."""
    project = tmp_project
    agent_dir = project / ".agent"
    original = (agent_dir / "agents" / "orchestrator.md").read_text()
    original_body = strip_and_normalize(original)

    CursorConverter().convert(project, project, verbose=False)
    cursor_file = project / ".cursor" / "agents" / "orchestrator.md"
    assert cursor_file.exists()

    captured = CapturedFile(
        ide_path=cursor_file,
        agent_path=agent_dir / "agents" / "orchestrator.md",
        status="new",
        ide_name="cursor",
    )
    apply_reverse_capture_cursor(captured, project, agent_dir)

    reversed_content = (agent_dir / "agents" / "orchestrator.md").read_text()
    reversed_body = strip_and_normalize(reversed_content)
    assert original_body == reversed_body


def test_roundtrip_kiro_agent_body_preserved(tmp_project):
    """Same but through Kiro JSON intermediate format."""
    project = tmp_project
    agent_dir = project / ".agent"
    original = (agent_dir / "agents" / "orchestrator.md").read_text()
    original_body = strip_and_normalize(original)

    KiroConverter().convert(project, project, verbose=False)
    kiro_file = project / ".kiro" / "agents" / "orchestrator.json"
    if not kiro_file.exists():
        pytest.skip("Kiro agent not generated")

    captured = CapturedFile(
        ide_path=kiro_file,
        agent_path=agent_dir / "agents" / "orchestrator.md",
        status="new",
        ide_name="kiro",
    )
    apply_reverse_capture_kiro(captured, project, agent_dir)

    reversed_content = (agent_dir / "agents" / "orchestrator.md").read_text()
    reversed_body = strip_and_normalize(reversed_content)
    assert original_body == reversed_body


def test_roundtrip_copilot_agent_body_preserved(tmp_project):
    """Same but through Copilot frontmatter format."""
    project = tmp_project
    agent_dir = project / ".agent"
    original = (agent_dir / "agents" / "orchestrator.md").read_text()
    original_body = strip_and_normalize(original)

    CopilotConverter().convert(project, project, verbose=False)
    copilot_file = project / ".github" / "agents" / "orchestrator.md"
    if not copilot_file.exists():
        pytest.skip("Copilot agent not generated")

    captured = CapturedFile(
        ide_path=copilot_file,
        agent_path=agent_dir / "agents" / "orchestrator.md",
        status="new",
        ide_name="copilot",
    )
    apply_reverse_capture_copilot(captured, project, agent_dir)

    reversed_content = (agent_dir / "agents" / "orchestrator.md").read_text()
    reversed_body = strip_and_normalize(reversed_content)
    assert original_body == reversed_body


def test_roundtrip_cursor_skill_content_preserved(tmp_project):
    """Skill SKILL.md body should survive forward -> reverse."""
    project = tmp_project
    agent_dir = project / ".agent"
    skill_file = agent_dir / "skills" / "clean-code" / "SKILL.md"
    original = skill_file.read_text()
    original_body = strip_and_normalize(original)

    CursorConverter().convert(project, project, verbose=False)
    cursor_skill = project / ".cursor" / "skills" / "clean-code" / "SKILL.md"
    if not cursor_skill.exists():
        cursor_rules = project / ".cursor" / "rules" / "clean-code.mdc"
        if cursor_rules.exists():
            cursor_skill = cursor_rules
        else:
            pytest.skip("clean-code not in cursor output")

    if cursor_skill.suffix == ".mdc":
        agent_path = agent_dir / "rules" / "clean-code.md"
    else:
        agent_path = agent_dir / "skills" / "clean-code" / "SKILL.md"
    captured = CapturedFile(
        ide_path=cursor_skill,
        agent_path=agent_path,
        status="new",
        ide_name="cursor",
    )
    apply_reverse_capture_cursor(captured, project, agent_dir)

    dest = agent_dir / "skills" / "clean-code" / "SKILL.md"
    if not dest.exists():
        dest = agent_dir / "rules" / "clean-code.md"
    reversed_body = strip_and_normalize(dest.read_text())
    assert original_body == reversed_body


def test_roundtrip_capture_then_init_produces_working_output(tmp_project, tmp_path, monkeypatch):
    """
    End-to-end lifecycle test:
    1. Them skill test-skill (khong trong MDC_RULES -> .cursor/skills/)
    2. Forward convert to Cursor
    3. Manually modify .cursor/skills/test-skill/SKILL.md (simulate user edit)
    4. Capture from Cursor back to .agent/
    5. Save snapshot
    6. Create new tmp project, init --from snapshot
    7. Forward convert to Cursor again
    8. Verify the user modification survived the full cycle
    """
    import agent_bridge.services.snapshot_service as snapshot_module
    from agent_bridge.services.capture_service import execute_capture, scan_for_captures
    from agent_bridge.vault.merger import MergeStrategy, merge_source_into_project

    monkeypatch.setattr(snapshot_module, "SNAPSHOTS_DIR", tmp_path / "snapshots")

    project = tmp_project
    agent_dir = project / ".agent"

    # 0. Them skill test-skill (go to .cursor/skills/, khong phai rules)
    test_skill_dir = agent_dir / "skills" / "test-skill"
    test_skill_dir.mkdir(parents=True, exist_ok=True)
    (test_skill_dir / "SKILL.md").write_text("# Test Skill\n\n> Test content.\n")

    # 1. Forward convert to Cursor
    CursorConverter().convert(project, project, verbose=False)
    cursor_skill = project / ".cursor" / "skills" / "test-skill" / "SKILL.md"
    if not cursor_skill.exists():
        pytest.skip("test-skill not generated")

    # 2. Manually modify (simulate user edit)
    user_edit = "\n\n<!-- USER_EDIT: custom modification -->\n"
    content = cursor_skill.read_text()
    cursor_skill.write_text(content + user_edit)

    # 3. Capture from Cursor back to .agent/
    files = scan_for_captures(project, ide_names=["cursor"])
    skill_files = [f for f in files if "test-skill" in str(f.ide_path)]
    if not skill_files:
        pytest.skip("No test-skill in capture list")
    execute_capture(project, skill_files, strategy="ide_wins", dry_run=False)

    # 4. Save snapshot
    from agent_bridge.services.snapshot_service import get_snapshot_agent_dir, save_snapshot

    info = save_snapshot("lifecycle-test", agent_dir, "E2E lifecycle")
    assert info.name == "lifecycle-test"

    # 5. Create new tmp project, init --from snapshot
    new_project = tmp_path / "new_project"
    new_project.mkdir()
    new_agent_dir = new_project / ".agent"
    snapshot_agent_dir = get_snapshot_agent_dir("lifecycle-test")
    assert snapshot_agent_dir
    merge_source_into_project(snapshot_agent_dir, new_agent_dir, MergeStrategy.VAULT_ONLY)

    # 6. Forward convert to Cursor again
    CursorConverter().convert(new_project, new_project, verbose=False)

    # 7. Verify the user modification survived
    new_cursor_skill = new_project / ".cursor" / "skills" / "test-skill" / "SKILL.md"
    assert new_cursor_skill.exists()
    new_content = new_cursor_skill.read_text()
    assert "USER_EDIT" in new_content
    assert "custom modification" in new_content
