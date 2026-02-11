"""
Cursor AI converter — chuyen doi .agent/ sang dang .cursor/agents, rules, skills.
"""

import shutil
from pathlib import Path

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat
from agent_bridge.cursor_conv import convert_to_cursor


class CursorConverter(BaseConverter):
    """Converter cho Cursor AI format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="cursor",
            display_name="Cursor AI",
            output_dir=".cursor",
            checkbox_label="Cursor (.cursor/)",
            status="beta",
        )

    def convert(
        self,
        source_root: Path,
        dest_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> ConversionResult:
        stats = convert_to_cursor(source_root, dest_root, verbose)
        return ConversionResult(
            agents=stats.get("agents", 0),
            skills=stats.get("skills", 0),
            workflows=stats.get("workflows", 0),
            rules=stats.get("rules", 0),
            errors=stats.get("errors", []),
            warnings=stats.get("warnings", []),
        )

    def install_mcp(
        self, source_root: Path, dest_root: Path, force: bool = False
    ) -> bool:
        from agent_bridge.utils import install_mcp_for_ide

        return install_mcp_for_ide(source_root, dest_root, "cursor")

    def clean(self, project_path: Path) -> bool:
        for sub in ["agents", "rules", "skills"]:
            p = project_path / ".cursor" / sub
            if p.exists():
                shutil.rmtree(p)
        return True


converter_registry.register(CursorConverter)
