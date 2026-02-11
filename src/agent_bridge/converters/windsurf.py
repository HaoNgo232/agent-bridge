"""
Windsurf converter — chuyen doi .agent/ sang dang .windsurf/rules, workflows.
"""

import shutil
from pathlib import Path

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat
from agent_bridge.converters._windsurf_impl import convert_to_windsurf


class WindsurfConverter(BaseConverter):
    """Converter cho Windsurf IDE format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="windsurf",
            display_name="Windsurf AI",
            output_dir=".windsurf",
            checkbox_label="Windsurf (.windsurf/)",
            status="beta",
        )

    def convert(
        self,
        source_root: Path,
        dest_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> ConversionResult:
        stats = convert_to_windsurf(source_root, dest_root, verbose)
        return ConversionResult(
            agents=0,
            skills=0,
            workflows=stats.get("workflows", 0),
            rules=stats.get("rules", 0),
            errors=stats.get("errors", []),
        )

    def install_mcp(
        self, source_root: Path, dest_root: Path, force: bool = False
    ) -> bool:
        from agent_bridge.utils import install_mcp_for_ide

        return install_mcp_for_ide(source_root, dest_root, "windsurf")

    def clean(self, project_path: Path) -> bool:
        for sub in ["rules", "workflows"]:
            p = project_path / ".windsurf" / sub
            if p.exists():
                shutil.rmtree(p)
        legacy = project_path / ".windsurfrules"
        if legacy.exists():
            legacy.unlink()
        return True


converter_registry.register(WindsurfConverter)
