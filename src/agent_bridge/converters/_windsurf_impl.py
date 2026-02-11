"""
Windsurf IDE Converter
Converts Antigravity Kit agents/skills/workflows to Windsurf format.

Output structure:
- .windsurf/rules/*.md (rules with activation modes)
- .windsurf/workflows/*.md (workflow definitions)
- .windsurfrules (legacy root-level rules)
- .windsurf/mcp_config.json (MCP configuration)

Reference: https://docs.windsurf.com/windsurf/cascade/memories
Activation modes: Manual, Always On, Model Decision, Glob
"""

import re
import shutil
from pathlib import Path
from typing import Any, Dict, List

# =============================================================================
# WINDSURF RULE CONFIGURATION
# =============================================================================

# Activation modes:
# 1. "always" - Always On: rule always applied
# 2. "glob" - Glob: auto-apply when files match pattern
# 3. "model" - Model Decision: AI decides based on description
# 4. "manual" - Manual: only via @mention

SKILL_ACTIVATION_MAP = {
    # Always On rules (core guidelines)
    "clean-code": {
        "mode": "always",
        "description": "Clean code principles and best practices",
        "globs": [],
    },
    "behavioral-modes": {
        "mode": "always",
        "description": "Agent behavioral guidelines",
        "globs": [],
    },
    # Glob-based rules
    "nextjs-react-expert": {
        "mode": "glob",
        "description": "Next.js and React expert patterns",
        "globs": ["**/*.tsx", "**/*.jsx", "**/next.config.*", "**/app/**/*"],
    },
    "tailwind-patterns": {
        "mode": "glob",
        "description": "Tailwind CSS patterns and utilities",
        "globs": ["**/*.tsx", "**/*.jsx", "**/*.css", "**/tailwind.config.*"],
    },
    "python-patterns": {
        "mode": "glob",
        "description": "Python best practices and patterns",
        "globs": ["**/*.py", "**/pyproject.toml", "**/requirements.txt"],
    },
    "rust-pro": {
        "mode": "glob",
        "description": "Rust programming patterns",
        "globs": ["**/*.rs", "**/Cargo.toml"],
    },
    "database-design": {
        "mode": "glob",
        "description": "Database design and SQL patterns",
        "globs": ["**/*.sql", "**/prisma/**/*", "**/migrations/**/*"],
    },
    "testing-patterns": {
        "mode": "glob",
        "description": "Testing frameworks and patterns",
        "globs": ["**/*.test.*", "**/*.spec.*", "**/__tests__/**/*"],
    },
    "mobile-design": {
        "mode": "glob",
        "description": "Mobile development patterns",
        "globs": ["**/App.tsx", "**/app.json", "**/android/**/*", "**/ios/**/*"],
    },
    # Model Decision rules (AI decides)
    "architecture": {
        "mode": "model",
        "description": "System architecture and design patterns - use when discussing structure, patterns, or making architectural decisions",
        "globs": [],
    },
    "brainstorming": {
        "mode": "model",
        "description": "Brainstorming and ideation - use when exploring options or creative problem solving",
        "globs": [],
    },
    "plan-writing": {
        "mode": "model",
        "description": "Project planning and task breakdown - use when creating plans or roadmaps",
        "globs": [],
    },
    "systematic-debugging": {
        "mode": "model",
        "description": "Debugging methodology - use when troubleshooting issues or analyzing errors",
        "globs": [],
    },
    "performance-profiling": {
        "mode": "model",
        "description": "Performance optimization - use when profiling or improving performance",
        "globs": [],
    },
    "security-scanner": {
        "mode": "model",
        "description": "Security auditing - use when checking for vulnerabilities",
        "globs": [],
    },
    "seo-fundamentals": {
        "mode": "model",
        "description": "SEO optimization - use when improving search engine optimization",
        "globs": [],
    },
    # Manual rules (explicit @mention)
    "red-team-tactics": {
        "mode": "manual",
        "description": "Security red team tactics",
        "globs": [],
    },
    "penetration-testing": {
        "mode": "manual",
        "description": "Penetration testing methodologies",
        "globs": [],
    },
}


# =============================================================================
# RULE FORMAT HELPERS
# =============================================================================


def generate_windsurf_rule_header(name: str, mode: str, description: str, globs: List[str] = None) -> str:
    """
    Generate Windsurf rule header with activation mode.

    Format:
    # Rule Name

    **Activation:** Always On | Glob: pattern | Model Decision | Manual
    **Description:** ...

    ---
    """
    lines = [f"# {name}", ""]

    # Activation mode
    if mode == "always":
        lines.append("**Activation:** Always On")
    elif mode == "glob" and globs:
        glob_str = ", ".join(globs[:5])  # Limit displayed globs
        if len(globs) > 5:
            glob_str += f" (+{len(globs) - 5} more)"
        lines.append(f"**Activation:** Glob: `{glob_str}`")
    elif mode == "model":
        lines.append("**Activation:** Model Decision")
    else:
        lines.append("**Activation:** Manual (@mention)")

    # Description
    if description:
        lines.append(f"**Description:** {description}")

    lines.extend(["", "---", ""])

    return "\n".join(lines)


def generate_workflow_content(name: str, steps: List[str], description: str = "") -> str:
    """
    Generate Windsurf workflow markdown.

    Workflows are invoked via /workflow-name command.
    """
    lines = [
        f"# {name}",
        "",
        f"**Description:** {description}" if description else "",
        "",
        "## Steps",
        "",
    ]

    for i, step in enumerate(steps, 1):
        lines.append(f"{i}. {step}")

    lines.extend(
        [
            "",
            "---",
            "",
            "*Invoke this workflow with* `/{}` *in Cascade.*".format(name.lower().replace(" ", "-")),
        ]
    )

    return "\n".join(lines)


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================


def convert_skill_to_windsurf_rule(source_dir: Path, dest_path: Path) -> bool:
    """Convert skill to Windsurf rule with activation mode."""
    try:
        skill_name = source_dir.name

        # Find SKILL.md
        skill_file = source_dir / "SKILL.md"
        if not skill_file.exists():
            md_files = list(source_dir.glob("*.md"))
            skill_file = md_files[0] if md_files else None

        if not skill_file:
            return False

        content = skill_file.read_text(encoding="utf-8")

        # Get activation config
        config = SKILL_ACTIVATION_MAP.get(
            skill_name,
            {
                "mode": "model",
                "description": f"Rules for {skill_name.replace('-', ' ')}",
                "globs": [],
            },
        )

        # Remove existing frontmatter/header
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)
        content_clean = re.sub(r"^#\s+.+\n*", "", content_clean)  # Remove first H1

        # Generate header with activation mode
        header = generate_windsurf_rule_header(
            name=skill_name.replace("-", " ").title(),
            mode=config.get("mode", "model"),
            description=config.get("description", ""),
            globs=config.get("globs", []),
        )

        # Merge additional .md files
        for md_file in sorted(source_dir.glob("*.md")):
            if md_file.name != "SKILL.md":
                additional = md_file.read_text(encoding="utf-8")
                additional_clean = re.sub(r"^---\n.*?\n---\n*", "", additional, flags=re.DOTALL)
                content_clean += f"\n\n---\n\n{additional_clean}"

        # Windsurf has a per-rule character limit
        # See: https://docs.windsurf.com/windsurf/cascade/memories#rule-limits
        WINDSURF_RULE_MAX_CHARS = 12000
        WINDSURF_TRUNCATE_SUFFIX = "\n\n... (truncated to fit Windsurf rule limit)\n"

        output = f"{header}{content_clean.strip()}\n"
        if len(output) > WINDSURF_RULE_MAX_CHARS:
            output = output[: WINDSURF_RULE_MAX_CHARS - len(WINDSURF_TRUNCATE_SUFFIX)] + WINDSURF_TRUNCATE_SUFFIX

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting skill {source_dir.name}: {e}")
        return False


def convert_agent_to_windsurf_rule(source_path: Path, dest_path: Path) -> bool:
    """Convert agent to Windsurf rule."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()
        agent_name = agent_slug.replace("-", " ").title()

        # Remove existing frontmatter
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        # Generate header
        header = generate_windsurf_rule_header(
            name=agent_name,
            mode="model",
            description=f"Specialized agent for {agent_slug.replace('-', ' ')} tasks",
            globs=[],
        )

        WINDSURF_RULE_MAX_CHARS = 12000
        WINDSURF_TRUNCATE_SUFFIX = "\n\n... (truncated to fit Windsurf rule limit)\n"

        output = f"{header}{content_clean.strip()}\n"
        if len(output) > WINDSURF_RULE_MAX_CHARS:
            output = output[: WINDSURF_RULE_MAX_CHARS - len(WINDSURF_TRUNCATE_SUFFIX)] + WINDSURF_TRUNCATE_SUFFIX

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_workflow_to_windsurf(source_path: Path, dest_path: Path) -> bool:
    """Convert workflow to Windsurf workflow format."""
    try:
        content = source_path.read_text(encoding="utf-8")
        workflow_name = source_path.stem.replace("-", " ").title()

        # Extract steps from markdown
        steps = []
        step_matches = re.findall(r"^\d+\.\s+(.+)$", content, re.MULTILINE)
        if step_matches:
            steps = step_matches
        else:
            # Extract from headers
            header_matches = re.findall(r"^##\s+(?:Step\s+\d+[:\s]*)?(.+)$", content, re.MULTILINE)
            steps = header_matches if header_matches else ["Follow the instructions below"]

        # Extract description
        desc_match = re.search(
            r"^>\s*(.+?)$|^(?:Description|Purpose)[:\s]*(.+?)(?:\n|$)", content, re.MULTILINE | re.IGNORECASE
        )
        description = ""
        if desc_match:
            description = (desc_match.group(1) or desc_match.group(2) or "").strip()

        # Remove existing frontmatter
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        # Build workflow output
        output = generate_workflow_content(workflow_name, steps, description)
        output += f"\n\n---\n\n## Full Instructions\n\n{content_clean.strip()}\n"

        WINDSURF_RULE_MAX_CHARS = 12000
        WINDSURF_TRUNCATE_SUFFIX = "\n\n... (truncated to fit Windsurf rule limit)\n"
        if len(output) > WINDSURF_RULE_MAX_CHARS:
            output = output[: WINDSURF_RULE_MAX_CHARS - len(WINDSURF_TRUNCATE_SUFFIX)] + WINDSURF_TRUNCATE_SUFFIX

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def create_windsurfrules(dest_root: Path, source_root: Path) -> bool:
    """Create legacy .windsurfrules file from project's actual agent knowledge."""
    try:
        parts = ["# Project Rules for Windsurf", ""]

        # Pull from always-on skills first (these are the most relevant)
        skills_src = source_root / ".agent" / "skills"
        if skills_src.exists():
            for skill_name in ["clean-code", "behavioral-modes"]:
                skill_file = skills_src / skill_name / "SKILL.md"
                if skill_file.exists():
                    content = skill_file.read_text(encoding="utf-8")
                    # Strip frontmatter
                    content = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)
                    parts.append(content.strip())
                    parts.append("")

        # Add from AGENTS.md or ARCHITECTURE.md if present
        for candidate in ["AGENTS.md", ".agent/ARCHITECTURE.md"]:
            candidate_path = source_root / candidate
            if candidate_path.exists():
                content = candidate_path.read_text(encoding="utf-8")
                parts.append(content[:3000].strip())
                parts.append("")
                break

        # Enforce max size for .windsurfrules (6000 chars is reasonable for root file)
        output = "\n".join(parts)
        if len(output) > 6000:
            output = output[:5950] + "\n\n... (see .windsurf/rules/ for full details)\n"

        (dest_root / ".windsurfrules").write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error creating .windsurfrules: {e}")
        return False


def convert_to_windsurf(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for Windsurf format.

    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root
        verbose: Print progress messages

    Returns:
        Dict with conversion statistics
    """
    stats = {"rules": 0, "workflows": 0, "errors": []}

    agents_src = source_root / ".agent" / "agents"
    skills_src = source_root / ".agent" / "skills"
    workflows_src = source_root / ".agent" / "workflows"

    rules_dest = dest_root / ".windsurf" / "rules"
    workflows_dest = dest_root / ".windsurf" / "workflows"

    # Convert agents to rules
    if agents_src.exists():
        if verbose:
            print("Converting agents to Windsurf rules...")

        for agent_file in agents_src.glob("*.md"):
            dest_file = rules_dest / agent_file.name
            if convert_agent_to_windsurf_rule(agent_file, dest_file):
                stats["rules"] += 1
                if verbose:
                    print(f"  ✓ {agent_file.name}")
            else:
                stats["errors"].append(f"rule:{agent_file.name}")

    # Convert skills to rules
    if skills_src.exists():
        if verbose:
            print("Converting skills to Windsurf rules...")

        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                dest_file = rules_dest / f"{skill_dir.name}.md"
                if convert_skill_to_windsurf_rule(skill_dir, dest_file):
                    stats["rules"] += 1
                    if verbose:
                        print(f"  ✓ {skill_dir.name}.md")
                else:
                    stats["errors"].append(f"rule:{skill_dir.name}")

    # Convert workflows
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to Windsurf format...")

        for workflow_file in workflows_src.glob("*.md"):
            dest_file = workflows_dest / workflow_file.name
            if convert_workflow_to_windsurf(workflow_file, dest_file):
                stats["workflows"] += 1
                if verbose:
                    print(f"  ✓ {workflow_file.name}")
            else:
                stats["errors"].append(f"workflow:{workflow_file.name}")

    # Create legacy .windsurfrules
    if create_windsurfrules(dest_root, source_root):
        if verbose:
            print("  ✓ .windsurfrules (legacy)")

    if verbose:
        print(f"\nWindsurf conversion complete: {stats['rules']} rules, {stats['workflows']} workflows")
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")

    return stats


