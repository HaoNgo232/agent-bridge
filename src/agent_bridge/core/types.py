"""Shared types and data structures for Agent Bridge."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SourceType(Enum):
    GIT = "git"
    LOCAL = "local"
    BUILTIN = "builtin"


@dataclass
class AgentRole:
    """
    Single source of truth for an agent's capabilities.
    Each converter maps these to its own format.
    """
    slug: str
    name: str
    description: str
    can_read: bool = True
    can_write: bool = False
    can_execute: bool = False
    can_search: bool = True
    can_delegate: bool = False
    allowed_commands: List[str] = field(default_factory=list)
    allowed_paths: List[str] = field(default_factory=lambda: ["**/*"])
    delegatable_agents: List[str] = field(default_factory=list)
    category: str = "subagent"
    hidden: bool = False


@dataclass
class ConversionResult:
    agents: int = 0
    skills: int = 0
    workflows: int = 0
    rules: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


@dataclass
class CapturedFile:
    """Represents a single file that can be captured from IDE config back to .agent/."""
    ide_path: Path
    agent_path: Path
    status: str  # "modified" | "new" | "unchanged"
    ide_name: str  # "cursor" | "kiro" | "copilot"


@dataclass
class SnapshotInfo:
    """Metadata about a saved snapshot."""
    name: str
    description: str
    created: str
    updated: str
    version: int
    contents: Dict[str, list]
    path: Path
    tags: Dict[str, list] = field(default_factory=dict)


@dataclass
class IDEFormat:
    """Metadata about one IDE format."""
    name: str
    display_name: str
    output_dir: str
    checkbox_label: str = ""  # For TUI display, e.g. "Cursor (.cursor/)"
    status: str = "beta"
    description: str = ""