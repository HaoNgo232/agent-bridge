"""Tests for snapshot CLI commands."""

import shutil
import sys

import pytest

from agent_bridge.services import snapshot_service


@pytest.fixture(autouse=True)
def _patch_snapshots_dir(tmp_path, monkeypatch):
    """Patch SNAPSHOTS_DIR to use tmp_path for isolated tests."""
    monkeypatch.setattr(snapshot_service, "SNAPSHOTS_DIR", tmp_path / "snapshots")
    return tmp_path


def test_cli_snapshot_save(tmp_project, monkeypatch):
    """
    CLI `agent-bridge snapshot save <name>` luu .agent/ thanh snapshot.
    """
    agent_dir = tmp_project / ".agent"
    assert agent_dir.exists()

    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "snapshot", "save", "cli-save-test", "--desc", "Test description"])

    from agent_bridge.cli import _main

    _main()

    info = snapshot_service.get_snapshot("cli-save-test")
    assert info is not None
    assert info.name == "cli-save-test"
    assert info.description == "Test description"
    assert (snapshot_service.SNAPSHOTS_DIR / "cli-save-test" / ".agent").exists()


def test_cli_snapshot_save_no_agent(tmp_project, monkeypatch, capsys):
    """
    CLI `snapshot save` khi khong co .agent/ in loi.
    """
    agent_dir = tmp_project / ".agent"
    shutil.rmtree(agent_dir)

    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "snapshot", "save", "no-agent"])

    from agent_bridge.cli import _main

    _main()

    out, err = capsys.readouterr()
    assert "No .agent" in (out + err) or "init" in (out + err)


def test_cli_snapshot_restore(tmp_project, monkeypatch):
    """
    CLI `agent-bridge snapshot restore <name>` khoi phuc .agent/ tu snapshot.
    """
    agent_dir = tmp_project / ".agent"
    snapshot_service.save_snapshot("restore-cli-test", agent_dir)

    # Xoa .agent de gia lap trang thai can restore
    shutil.rmtree(agent_dir)

    assert not agent_dir.exists()

    # Invoke CLI: snapshot restore restore-cli-test
    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "snapshot", "restore", "restore-cli-test"])

    from agent_bridge.cli import _main

    _main()

    assert agent_dir.exists()
    assert (agent_dir / "agents" / "orchestrator.md").exists()
    assert (agent_dir / "skills" / "clean-code" / "SKILL.md").exists()
    assert (agent_dir / "mcp_config.json").exists()


def test_cli_snapshot_restore_nonexistent(tmp_project, monkeypatch, capsys):
    """
    CLI `snapshot restore <nonexistent>` in loi va khong crash.
    """
    agent_dir = tmp_project / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.chdir(tmp_project)
    monkeypatch.setattr(sys, "argv", ["agent-bridge", "snapshot", "restore", "nonexistent"])

    from agent_bridge.cli import _main

    _main()

    out, err = capsys.readouterr()
    assert "not found" in (out + err)
