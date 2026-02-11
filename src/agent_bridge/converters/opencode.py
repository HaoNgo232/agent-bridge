"""
OpenCode converter — chuyen doi .agent/ sang dang .opencode/agents, commands, skills.
"""

import shutil
from pathlib import Path

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat
from agent_bridge.converters._opencode_impl import convert_to_opencode, copy_mcp_opencode


class OpenCodeConverter(BaseConverter):
    """Converter cho OpenCode IDE format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="opencode",
            display_name="OpenCode IDE",
            output_dir=".opencode",
            checkbox_label="OpenCode (.opencode/)",
            status="beta",
        )

    def convert(
        self,
        source_root: Path,
        dest_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> ConversionResult:
        stats = convert_to_opencode(source_root, dest_root, verbose)
        return ConversionResult(
            agents=stats.get("agents", 0),
            skills=stats.get("skills", 0),
            workflows=stats.get("commands", 0),
            errors=stats.get("errors", []),
        )

    def install_mcp(
        self, source_root: Path, dest_root: Path, force: bool = False
    ) -> bool:
        return copy_mcp_opencode(dest_root, force)

    def clean(self, project_path: Path) -> bool:
        for sub in ["agents", "commands", "skills"]:
            p = project_path / ".opencode" / sub
            if p.exists():
                shutil.rmtree(p)
        config_file = project_path / ".opencode" / "opencode.json"
        if config_file.exists():
            config_file.unlink()
        return True


converter_registry.register(OpenCodeConverter)
