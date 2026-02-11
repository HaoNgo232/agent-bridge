"""
GitHub Copilot converter — chuyen doi .agent/ sang dang .github/agents va .github/skills.

Output: .github/agents/*.md, .github/skills/<skill>/SKILL.md,
.github/prompts/*.prompt.md, .github/instructions/*.instructions.md
"""

import shutil
from pathlib import Path

from agent_bridge.core.converter import BaseConverter, converter_registry
from agent_bridge.core.types import ConversionResult, IDEFormat

# Re-export cho tests va backward compatibility
from agent_bridge.converters._copilot_impl import (
    AGENT_SUBAGENTS_MAP,
    _role_to_copilot_tools,
    convert_rule_to_instruction,
    convert_skill_to_copilot,
    convert_to_copilot,
    convert_workflow_to_prompt,
    generate_copilot_frontmatter,
)


class CopilotConverter(BaseConverter):
    """Converter cho GitHub Copilot format."""

    @property
    def format_info(self) -> IDEFormat:
        return IDEFormat(
            name="copilot",
            display_name="GitHub Copilot",
            output_dir=".github",
            checkbox_label="Copilot (.github/)",
            status="beta",
        )

    def convert(
        self,
        source_root: Path,
        dest_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> ConversionResult:
        stats = convert_to_copilot(source_root, dest_root, verbose)
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

        return install_mcp_for_ide(source_root, dest_root, "copilot")

    def clean(self, project_path: Path) -> bool:
        for sub in ["agents", "skills", "prompts", "instructions"]:
            p = project_path / ".github" / sub
            if p.exists():
                shutil.rmtree(p)
        return True


converter_registry.register(CopilotConverter)
