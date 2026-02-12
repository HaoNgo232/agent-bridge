"""Tests for snapshot_service."""

import pytest
from pathlib import Path

from agent_bridge.services import snapshot_service


@pytest.fixture(autouse=True)
def patch_snapshots_dir(tmp_path, monkeypatch):
    """Patch SNAPSHOTS_DIR to use tmp_path for isolated tests."""
    monkeypatch.setattr(snapshot_service, "SNAPSHOTS_DIR", tmp_path / "snapshots")
    return tmp_path


def test_save_snapshot(tmp_project):
    """Verify snapshot dir created with manifest.json and .agent/ copy."""
    agent_dir = tmp_project / ".agent"
    info = snapshot_service.save_snapshot("my-snapshot", agent_dir, "Test description")

    assert info.name == "my-snapshot"
    assert info.description == "Test description"
    assert info.version == 1

    snapshot_path = snapshot_service.SNAPSHOTS_DIR / "my-snapshot"
    assert snapshot_path.exists()
    assert (snapshot_path / "manifest.json").exists()
    assert (snapshot_path / ".agent").exists()

    manifest = snapshot_path / "manifest.json"
    data = __import__("json").loads(manifest.read_text())
    assert data["name"] == "my-snapshot"
    assert data["description"] == "Test description"
    assert data["version"] == 1

    agent_copy = snapshot_path / ".agent"
    assert (agent_copy / "agents" / "orchestrator.md").exists()
    assert (agent_copy / "skills" / "clean-code" / "SKILL.md").exists()
    assert (agent_copy / "mcp_config.json").exists()


def test_save_snapshot_version_bump(tmp_project):
    """Save same name twice -> version should increment."""
    agent_dir = tmp_project / ".agent"
    info1 = snapshot_service.save_snapshot("flutter-v2", agent_dir)
    assert info1.version == 1

    info2 = snapshot_service.save_snapshot("flutter-v2", agent_dir)
    assert info2.version == 2
    assert info2.name == "flutter-v2"


def test_list_snapshots_empty():
    """Empty snapshots dir -> empty list."""
    result = snapshot_service.list_snapshots()
    assert result == []


def test_list_snapshots_sorted_by_date(tmp_project):
    """Multiple snapshots -> newest first (last saved = first in list)."""
    agent_dir = tmp_project / ".agent"
    snapshot_service.save_snapshot("old", agent_dir)
    snapshot_service.save_snapshot("new", agent_dir)
    snapshot_service.save_snapshot("mid", agent_dir)

    result = snapshot_service.list_snapshots()
    names = [s.name for s in result]
    assert set(names) == {"old", "new", "mid"}
    assert len(result) == 3
    assert result[0].name == "mid"


def test_delete_snapshot(tmp_project):
    """Delete -> dir removed, not in list."""
    agent_dir = tmp_project / ".agent"
    snapshot_service.save_snapshot("to-delete", agent_dir)
    assert snapshot_service.get_snapshot("to-delete") is not None

    ok = snapshot_service.delete_snapshot("to-delete")
    assert ok is True
    assert snapshot_service.get_snapshot("to-delete") is None
    assert not (snapshot_service.SNAPSHOTS_DIR / "to-delete").exists()


def test_delete_snapshot_nonexistent():
    """Delete nonexistent -> False."""
    ok = snapshot_service.delete_snapshot("does-not-exist")
    assert ok is False


def test_get_snapshot_agent_dir(tmp_project):
    """Returns valid Path to .agent/ inside snapshot."""
    agent_dir = tmp_project / ".agent"
    snapshot_service.save_snapshot("valid", agent_dir)

    path = snapshot_service.get_snapshot_agent_dir("valid")
    assert path is not None
    assert path.exists()
    assert path.name == ".agent"
    assert (path / "agents" / "orchestrator.md").exists()


def test_get_snapshot_agent_dir_nonexistent():
    """Nonexistent snapshot -> None."""
    assert snapshot_service.get_snapshot_agent_dir("nonexistent") is None


def test_snapshot_contents_accurate(tmp_project):
    """manifest.json contents field matches actual files."""
    agent_dir = tmp_project / ".agent"
    info = snapshot_service.save_snapshot("contents-test", agent_dir)

    assert "orchestrator" in info.contents["agents"]
    assert "frontend-specialist" in info.contents["agents"]
    assert "clean-code" in info.contents["skills"]
    assert "plan" in info.contents["workflows"]
    assert "global" in info.contents["rules"]


def test_restore_snapshot(tmp_project):
    """Restore snapshot writes .agent/ contents to target dir."""
    agent_dir = tmp_project / ".agent"
    snapshot_service.save_snapshot("restore-test", agent_dir)

    restore_dir = tmp_project / "restored" / ".agent"
    restore_dir.parent.mkdir(parents=True, exist_ok=True)
    ok = snapshot_service.restore_snapshot(restore_dir, "restore-test")

    assert ok is True
    assert (restore_dir / "agents" / "orchestrator.md").exists()
    assert (restore_dir / "skills" / "clean-code" / "SKILL.md").exists()
    assert (restore_dir / "mcp_config.json").exists()


def test_restore_snapshot_nonexistent(tmp_project):
    """Restore nonexistent snapshot returns False."""
    agent_dir = tmp_project / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    ok = snapshot_service.restore_snapshot(agent_dir, "nonexistent")
    assert ok is False
