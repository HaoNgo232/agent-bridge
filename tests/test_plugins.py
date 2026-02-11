"""Tests for the external skill plugin system."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent_bridge.core.plugins import (
    Plugin,
    PluginRunner,
    check_condition,
    load_plugins,
    _check_tool_available,
)


# =============================================================================
# FIXTURES
# =============================================================================


def _create_plugins_json(tmp_path: Path, plugins_data: list) -> Path:
    """Create .agent/plugins.json in tmp_path."""
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)
    plugins_file = agent_dir / "plugins.json"
    plugins_file.write_text(
        json.dumps({"plugins": plugins_data}, indent=2),
        encoding="utf-8",
    )
    return tmp_path


def _sample_plugin_dict(**overrides) -> dict:
    """Create a sample plugin dict with sensible defaults."""
    base = {
        "name": "test-plugin",
        "description": "A test plugin",
        "homepage": "https://example.com",
        "install": {
            "requires": "npm",
            "package": "test-cli",
            "global": True,
            "commands": {
                "kiro": "test-cli init --ai kiro",
                "cursor": "test-cli init --ai cursor",
            },
        },
        "condition": {
            "file_exists": ".agent/workflows/test-plugin.md",
        },
        "prompt_before_install": False,  # Don't prompt in tests
    }
    base.update(overrides)
    return base


# =============================================================================
# LOADING TESTS
# =============================================================================


def test_load_plugins_from_valid_json(tmp_path: Path) -> None:
    source_root = _create_plugins_json(tmp_path, [_sample_plugin_dict()])
    plugins = load_plugins(source_root)

    assert len(plugins) == 1
    assert plugins[0].name == "test-plugin"
    assert plugins[0].install.requires == "npm"
    assert plugins[0].install.package == "test-cli"
    assert "kiro" in plugins[0].install.commands
    assert "cursor" in plugins[0].install.commands


def test_load_plugins_returns_empty_when_no_file(tmp_path: Path) -> None:
    plugins = load_plugins(tmp_path)
    assert plugins == []


def test_load_plugins_handles_malformed_json(tmp_path: Path) -> None:
    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir(parents=True)
    (agent_dir / "plugins.json").write_text("not valid json {{{", encoding="utf-8")
    plugins = load_plugins(tmp_path)
    assert plugins == []


def test_load_plugins_skips_entries_without_name(tmp_path: Path) -> None:
    source_root = _create_plugins_json(tmp_path, [
        {"description": "no name plugin"},
        _sample_plugin_dict(name="valid"),
    ])
    plugins = load_plugins(source_root)
    assert len(plugins) == 1
    assert plugins[0].name == "valid"


def test_load_multiple_plugins(tmp_path: Path) -> None:
    source_root = _create_plugins_json(tmp_path, [
        _sample_plugin_dict(name="plugin-a"),
        _sample_plugin_dict(name="plugin-b"),
        _sample_plugin_dict(name="plugin-c"),
    ])
    plugins = load_plugins(source_root)
    assert len(plugins) == 3
    assert [p.name for p in plugins] == ["plugin-a", "plugin-b", "plugin-c"]


# =============================================================================
# CONDITION TESTS
# =============================================================================


def test_condition_file_exists_true(tmp_path: Path) -> None:
    trigger_file = tmp_path / ".agent" / "workflows" / "test-plugin.md"
    trigger_file.parent.mkdir(parents=True)
    trigger_file.write_text("# Test", encoding="utf-8")

    plugin = Plugin.from_dict(_sample_plugin_dict())
    assert check_condition(plugin, tmp_path) is True


def test_condition_file_exists_false(tmp_path: Path) -> None:
    plugin = Plugin.from_dict(_sample_plugin_dict())
    assert check_condition(plugin, tmp_path) is False


def test_condition_always(tmp_path: Path) -> None:
    data = _sample_plugin_dict()
    data["condition"] = {"always": True}
    plugin = Plugin.from_dict(data)
    assert check_condition(plugin, tmp_path) is True


def test_condition_empty_means_always(tmp_path: Path) -> None:
    data = _sample_plugin_dict()
    data["condition"] = {}
    plugin = Plugin.from_dict(data)
    assert check_condition(plugin, tmp_path) is True


# =============================================================================
# PLUGIN RUNNER TESTS
# =============================================================================


def test_runner_skips_when_condition_not_met(tmp_path: Path) -> None:
    """Plugin should be skipped if its trigger file doesn't exist."""
    source_root = _create_plugins_json(tmp_path, [_sample_plugin_dict()])

    runner = PluginRunner(source_root)
    results = runner.run_for_ide("kiro", tmp_path, verbose=False)

    # Condition file doesn't exist → plugin not in results
    assert results == {}


def test_runner_runs_when_condition_met(tmp_path: Path) -> None:
    """Plugin should run if trigger file exists and tool is available."""
    source_root = _create_plugins_json(tmp_path, [_sample_plugin_dict()])

    # Create trigger file
    trigger = tmp_path / ".agent" / "workflows" / "test-plugin.md"
    trigger.parent.mkdir(parents=True, exist_ok=True)
    trigger.write_text("# Test", encoding="utf-8")

    with patch("agent_bridge.core.plugins._install_prerequisite", return_value=True), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        runner = PluginRunner(source_root)
        results = runner.run_for_ide("kiro", tmp_path, verbose=False, force=True)

    assert results.get("test-plugin") == "ok"
    mock_run.assert_called_once()
    # Verify the correct command was run
    call_args = mock_run.call_args
    assert "test-cli init --ai kiro" in call_args[0][0]


def test_runner_uses_correct_ide_command(tmp_path: Path) -> None:
    """Each IDE should get its own command."""
    source_root = _create_plugins_json(tmp_path, [
        _sample_plugin_dict(
            **{"condition": {"always": True}}
        ),
    ])

    with patch("agent_bridge.core.plugins._install_prerequisite", return_value=True), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        runner = PluginRunner(source_root)

        runner.run_for_ide("kiro", tmp_path, verbose=False, force=True)
        assert "kiro" in mock_run.call_args[0][0]

        mock_run.reset_mock()
        runner.run_for_ide("cursor", tmp_path, verbose=False, force=True)
        assert "cursor" in mock_run.call_args[0][0]


def test_runner_skips_unsupported_ide(tmp_path: Path) -> None:
    """Plugin without command for an IDE should be skipped."""
    data = _sample_plugin_dict()
    data["install"]["commands"] = {"kiro": "test-cli init --ai kiro"}  # Only kiro
    data["condition"] = {"always": True}

    source_root = _create_plugins_json(tmp_path, [data])

    runner = PluginRunner(source_root)
    results = runner.run_for_ide("cursor", tmp_path, verbose=False, force=True)
    assert results == {}


def test_runner_handles_command_failure(tmp_path: Path) -> None:
    """Failed commands should return error status."""
    data = _sample_plugin_dict()
    data["condition"] = {"always": True}
    source_root = _create_plugins_json(tmp_path, [data])

    with patch("agent_bridge.core.plugins._install_prerequisite", return_value=True), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="something broke")

        runner = PluginRunner(source_root)
        results = runner.run_for_ide("kiro", tmp_path, verbose=False, force=True)

    assert "error" in results.get("test-plugin", "")


def test_runner_handles_prerequisite_failure(tmp_path: Path) -> None:
    """If prerequisite install fails, plugin should report error."""
    data = _sample_plugin_dict()
    data["condition"] = {"always": True}
    source_root = _create_plugins_json(tmp_path, [data])

    with patch("agent_bridge.core.plugins._install_prerequisite", return_value=False):
        runner = PluginRunner(source_root)
        results = runner.run_for_ide("kiro", tmp_path, verbose=False, force=True)

    assert "prerequisite" in results.get("test-plugin", "")


def test_list_plugins(tmp_path: Path) -> None:
    source_root = _create_plugins_json(tmp_path, [
        _sample_plugin_dict(name="a"),
        _sample_plugin_dict(name="b"),
    ])
    runner = PluginRunner(source_root)
    all_plugins = runner.list_plugins()
    assert len(all_plugins) == 2

    kiro_only = runner.list_plugins(ide_name="kiro")
    assert len(kiro_only) == 2

    # Filter by non-existent IDE
    fake_plugins = runner.list_plugins(ide_name="nonexistent")
    assert len(fake_plugins) == 0


# =============================================================================
# PLUGIN DATA PARSING TESTS
# =============================================================================


def test_plugin_from_dict_minimal() -> None:
    plugin = Plugin.from_dict({"name": "minimal"})
    assert plugin.name == "minimal"
    assert plugin.install.requires == ""
    assert plugin.install.commands == {}
    assert plugin.condition.file_exists == ""
    assert plugin.prompt_before_install is True


def test_plugin_from_dict_full() -> None:
    data = _sample_plugin_dict()
    plugin = Plugin.from_dict(data)

    assert plugin.name == "test-plugin"
    assert plugin.description == "A test plugin"
    assert plugin.install.requires == "npm"
    assert plugin.install.package == "test-cli"
    assert plugin.install.global_install is True
    assert len(plugin.install.commands) == 2
    assert plugin.condition.file_exists == ".agent/workflows/test-plugin.md"
    assert plugin.prompt_before_install is False