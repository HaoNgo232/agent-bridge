"""
Kiro CLI converter — chuyen doi .agent/ sang dang .kiro/agents, skills, prompts, steering.
"""

import shutil
from pathlib import Path
from typing import List

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import CapturedFile, ConversionResult, IDEFormat
from agent_bridge.converters._kiro_impl import convert_to_kiro, reverse_convert_kiro


class KiroConverter(BaseConverter):
    """Converter cho Kiro CLI format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="kiro",
            display_name="Kiro CLI",
            output_dir=".kiro",
            checkbox_label="Kiro (.kiro/)",
            status="beta",
        )

    def convert(
        self,
        source_root: Path,
        dest_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> ConversionResult:
        stats = convert_to_kiro(source_root, dest_root, verbose)
        return ConversionResult(
            agents=stats.get("agents", 0),
            skills=stats.get("skills", 0),
            workflows=stats.get("prompts", 0) + stats.get("steering", 0),
            errors=stats.get("errors", []),
            warnings=stats.get("warnings", []),
        )

    def install_mcp(
        self, source_root: Path, dest_root: Path, force: bool = False
    ) -> bool:
        from agent_bridge.utils import install_mcp_for_ide

        return install_mcp_for_ide(source_root, dest_root, "kiro")

    def clean(self, project_path: Path) -> bool:
        paths = [
            project_path / ".kiro" / "agents",
            project_path / ".kiro" / "skills",
            project_path / ".kiro" / "steering",
            project_path / ".kiro" / "prompts",
        ]
        for p in paths:
            if p.exists():
                shutil.rmtree(p)
        return True

    def reverse_convert(
        self,
        project_path: Path,
        agent_dir: Path,
        verbose: bool = True,
    ) -> List[CapturedFile]:
        """Reverse-convert .kiro/ files back to .agent/ format."""
        return reverse_convert_kiro(project_path, agent_dir, verbose)


converter_registry.register(KiroConverter)
