"""Edge case tests for Kiro reverse conversion."""

import pytest
from pathlib import Path

from agent_bridge.converters._kiro_impl import apply_reverse_capture_kiro
from agent_bridge.core.types import CapturedFile


def test_kiro_agent_invalid_json_returns_false(tmp_path):
    """Invalid JSON in .kiro/agents/*.json -> apply_reverse_capture_kiro returns False."""
    kiro_agents = tmp_path / ".kiro" / "agents"
    kiro_agents.mkdir(parents=True)
    (kiro_agents / "broken.json").write_text("{ invalid json }")

    agent_dir = tmp_path / ".agent"
    agent_dir.mkdir(parents=True)
    (agent_dir / "agents").mkdir(exist_ok=True)

    captured = CapturedFile(
        ide_path=kiro_agents / "broken.json",
        agent_path=agent_dir / "agents" / "broken.md",
        status="new",
        ide_name="kiro",
    )
    result = apply_reverse_capture_kiro(captured, tmp_path, agent_dir)
    assert result is False
