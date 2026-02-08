"""
GitHub Copilot Converter
Converts Antigravity Kit agents/skills to GitHub Copilot format.

Output structure:
- .github/agents/*.md (agent profiles with YAML frontmatter)
- .github/skills/<skill-name>/SKILL.md

Reference: https://docs.github.com/en/copilot/reference/custom-agents-configuration
"""

import re
import shutil
from pathlib import Path
from typing import Any, Dict

import yaml

from .utils import Colors, ask_user, get_master_agent_dir, install_mcp_for_ide

# =============================================================================
# TOOL MAPPINGS
# =============================================================================

# Tool alias mapping theo Copilot spec
COPILOT_TOOL_ALIASES = {
    # Primary aliases
    "execute": ["shell", "bash", "powershell"],
    "read": ["read", "notebookread"],
    "edit": ["edit", "multiedit", "write", "notebookedit"],
    "search": ["grep", "glob", "search"],
    "agent": ["custom-agent", "task"],
    "web": ["websearch", "webfetch", "fetch"],
    "todo": ["todowrite"],
}

# Agent role -> tools mapping
AGENT_TOOLS_MAP = {
    "frontend-specialist": ["read", "edit", "search", "execute"],
    "backend-specialist": ["read", "edit", "search", "execute"],
    "database-architect": ["read", "edit", "search", "execute"],
    "security-auditor": ["read", "search"],  # Read-only for security review
    "test-engineer": ["read", "edit", "search", "execute"],
    "devops-engineer": ["read", "edit", "search", "execute"],
    "documentation-writer": ["read", "edit", "search"],
    "explorer-agent": ["read", "search"],  # Read-only explorer
    "project-planner": ["read", "search", "agent"],  # Can delegate
    "orchestrator": ["read", "search", "agent"],  # Orchestrates agents
    "debugger": ["read", "edit", "search", "execute"],
    "performance-optimizer": ["read", "edit", "search", "execute"],
    "code-archaeologist": ["read", "search"],
    "product-manager": ["read", "search"],
    "product-owner": ["read", "search"],
    "seo-specialist": ["read", "edit", "search"],
    "game-developer": ["read", "edit", "search", "execute"],
    "mobile-developer": ["read", "edit", "search", "execute"],
    "penetration-tester": ["read", "search", "execute"],
    "qa-automation-engineer": ["read", "edit", "search", "execute"],
}

# Handoffs - workflow transitions between agents
AGENT_HANDOFFS_MAP = {
    "project-planner": [
        {
            "label": "Start Implementation",
            "agent": "orchestrator",
            "prompt": "Implement the plan outlined above following the task breakdown.",
            "send": False,
        },
        {
            "label": "Security Review",
            "agent": "security-auditor",
            "prompt": "Review the security aspects of this implementation plan.",
            "send": False,
        },
    ],
    "orchestrator": [
        {
            "label": "Frontend Tasks",
            "agent": "frontend-specialist",
            "prompt": "Implement the frontend components as specified.",
            "send": False,
        },
        {
            "label": "Backend Tasks",
            "agent": "backend-specialist",
            "prompt": "Implement the backend services as specified.",
            "send": False,
        },
        {
            "label": "Database Setup",
            "agent": "database-architect",
            "prompt": "Design and implement the database schema.",
            "send": False,
        },
        {
            "label": "Write Tests",
            "agent": "test-engineer",
            "prompt": "Write tests for the implemented features.",
            "send": False,
        },
    ],
    "explorer-agent": [
        {
            "label": "Create Plan",
            "agent": "project-planner",
            "prompt": "Create an implementation plan based on this codebase analysis.",
            "send": False,
        },
    ],
    "security-auditor": [
        {
            "label": "Fix Security Issues",
            "agent": "backend-specialist",
            "prompt": "Fix the security vulnerabilities identified in the audit.",
            "send": False,
        },
    ],
    "test-engineer": [
        {
            "label": "Fix Failing Tests",
            "agent": "backend-specialist",
            "prompt": "Fix the code to make the failing tests pass.",
            "send": False,
        },
    ],
    "debugger": [
        {
            "label": "Implement Fix",
            "agent": "backend-specialist",
            "prompt": "Implement the fix for the identified bug.",
            "send": False,
        },
    ],
}


# =============================================================================
# METADATA EXTRACTION
# =============================================================================

# Pre-compiled regex patterns for performance
_RE_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_RE_H1_NAME = re.compile(r"^#\s+(.+?)(?:\s*[-–—]\s*(.+))?$", re.MULTILINE)
_RE_ROLE_PATTERNS = [
    re.compile(r"(?:You are|Role:|##\s*Role)[:\s]*(.+?)(?:\n\n|\n##|\n#\s)", re.IGNORECASE | re.DOTALL),
    re.compile(r"(?:Purpose|Mission)[:\s]*(.+?)(?:\n\n|\n##)", re.IGNORECASE | re.DOTALL),
    re.compile(r"^>\s*(.+?)$", re.MULTILINE),
]
_RE_SKILL_PATTERNS = [
    re.compile(r"skills?[:\s]+\[([^\]]+)\]", re.IGNORECASE),
    re.compile(r"`([a-z][a-z0-9\-]+)`\s*skill", re.IGNORECASE),
    re.compile(r"uses?\s+(?:the\s+)?`([a-z][a-z0-9\-]+)`", re.IGNORECASE),
]


def extract_agent_metadata(content: str, filename: str) -> Dict[str, Any]:
    """Extract metadata from agent markdown content."""
    metadata = {
        "name": "",
        "description": "",
        "role": "",
        "skills": [],
    }

    # Check for existing YAML frontmatter
    fm_match = _RE_FRONTMATTER.match(content)
    if fm_match:
        try:
            existing = yaml.safe_load(fm_match.group(1))
            if existing:
                # Merge logic - ensure lists remain lists even if YAML has comma-separated strings
                for key, value in existing.items():
                    if key in ["skills", "tools"] and isinstance(value, str):
                        # Convert "a, b, c" to ["a", "b", "c"]
                        metadata[key] = [s.strip() for s in value.split(",")]
                    else:
                        metadata[key] = value
        except yaml.YAMLError:
            pass

    # Extract name from first H1 heading
    name_match = _RE_H1_NAME.search(content)
    if name_match:
        metadata["name"] = name_match.group(1).strip()
        if name_match.group(2) and not metadata.get("description"):
            metadata["description"] = name_match.group(2).strip()

    # Fallback name from filename
    if not metadata["name"]:
        metadata["name"] = filename.replace(".md", "").replace("-", " ").title()

    # Extract role description
    for pattern in _RE_ROLE_PATTERNS:
        role_match = pattern.search(content)
        if role_match and not metadata.get("role"):
            metadata["role"] = role_match.group(1).strip()[:300]
            break

    # Extract skill references
    for pattern in _RE_SKILL_PATTERNS:
        for match in pattern.finditer(content):
            skills_str = match.group(1)
            for skill in re.split(r"[,\s]+", skills_str):
                skill = skill.strip().strip("`\"'")
                if skill and skill not in metadata["skills"]:
                    metadata["skills"].append(skill)

    return metadata


def generate_copilot_frontmatter(agent_slug: str, metadata: Dict[str, Any]) -> str:
    """Generate YAML frontmatter for Copilot agent profile."""

    frontmatter: Dict[str, Any] = {}

    # Required: name
    frontmatter["name"] = metadata.get("name") or agent_slug.replace("-", " ").title()

    # Required: description (max 150 chars for display)
    description = metadata.get("description") or metadata.get("role", "")
    if not description:
        description = f"Specialized agent for {agent_slug.replace('-', ' ')} tasks"
    frontmatter["description"] = description[:150]

    # Tools based on agent role
    tools = AGENT_TOOLS_MAP.get(agent_slug, ["read", "edit", "search"])
    frontmatter["tools"] = tools

    # Handoffs for workflow agents
    handoffs = AGENT_HANDOFFS_MAP.get(agent_slug)
    if handoffs:
        frontmatter["handoffs"] = handoffs

    # Subagents configuration for orchestrator-type agents
    if agent_slug in ["orchestrator", "project-planner"]:
        frontmatter["agents"] = ["*"]  # Allow invoking any agent as subagent

    # User-invokable (show in dropdown)
    # Hide internal/utility agents
    if agent_slug in ["code-archaeologist"]:
        frontmatter["user-invokable"] = False

    return yaml.dump(
        frontmatter,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================


def convert_agent_to_copilot(source_path: Path, dest_path: Path) -> bool:
    """Convert a single agent file to Copilot format with full frontmatter."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()

        metadata = extract_agent_metadata(content, source_path.name)
        frontmatter = generate_copilot_frontmatter(agent_slug, metadata)

        # Remove existing frontmatter from content
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        # Build output with new frontmatter
        # Copilot spec: prompt (body after frontmatter) max 30,000 characters
        COPILOT_PROMPT_MAX_CHARS = 30000
        body = content_clean.strip()
        if len(body) > COPILOT_PROMPT_MAX_CHARS:
            truncate_suffix = "\n\n... (truncated to fit Copilot 30K char limit)\n"
            body = body[: COPILOT_PROMPT_MAX_CHARS - len(truncate_suffix)] + truncate_suffix

        output = f"---\n{frontmatter}---\n\n{body}\n"

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_skill_to_copilot(source_dir: Path, dest_dir: Path) -> bool:
    """Convert a skill directory to Copilot format."""
    try:
        skill_name = source_dir.name
        dest_skill_dir = dest_dir / skill_name
        dest_skill_dir.mkdir(parents=True, exist_ok=True)

        # Find main skill file
        skill_file = source_dir / "SKILL.md"
        if not skill_file.exists():
            md_files = list(source_dir.glob("*.md"))
            skill_file = md_files[0] if md_files else None

        if skill_file and skill_file.exists():
            content = skill_file.read_text(encoding="utf-8")

            # Extract skill title (unused, removed for linting)
            # title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)

            # Generate skill frontmatter (Agent Skills spec: name must be lowercase + hyphens)
            normalized_name = re.sub(r"[^a-z0-9-]", "-", skill_name.lower())[:64].strip("-")

            # Try to extract description from content
            desc_match = re.search(r"^(?:>|Description:|Purpose:)\s*(.+?)$", content, re.MULTILINE | re.IGNORECASE)
            skill_description = (
                desc_match.group(1).strip()[:1024]
                if desc_match
                else f"Skill documentation for {skill_name.replace('-', ' ')}"
            )

            frontmatter = {
                "name": normalized_name,
                "description": skill_description,
            }

            # Remove existing frontmatter
            content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

            output = f"---\n{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)}---\n\n{content_clean.strip()}\n"

            (dest_skill_dir / "SKILL.md").write_text(output, encoding="utf-8")

        # Copy additional markdown files and safe subdirectories
        SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
        for item in source_dir.iterdir():
            if item.is_dir():
                if item.name not in SKIP_DIRS and not item.name.startswith("."):
                    shutil.copytree(item, dest_skill_dir / item.name, dirs_exist_ok=True)
            elif item.name != "SKILL.md" and item.suffix in (".md", ".txt", ".json", ".yaml", ".yml"):
                shutil.copy2(item, dest_skill_dir / item.name)

        return True
    except Exception as e:
        print(f"  Error converting skill {source_dir.name}: {e}")
        return False


def convert_to_copilot(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for GitHub Copilot format.

    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root (usually same as source_root)
        verbose: Print progress messages

    Returns:
        Dict with conversion statistics
    """
    stats = {"agents": 0, "skills": 0, "errors": []}

    agents_src = source_root / ".agent" / "agents"
    agents_dest = dest_root / ".github" / "agents"

    skills_src = source_root / ".agent" / "skills"
    skills_dest = dest_root / ".github" / "skills"

    # Convert agents
    if agents_src.exists():
        if verbose:
            print("Converting agents to Copilot format...")

        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / agent_file.name
            if convert_agent_to_copilot(agent_file, dest_file):
                stats["agents"] += 1
                if verbose:
                    print(f"  ✓ {agent_file.name}")
            else:
                stats["errors"].append(f"agent:{agent_file.name}")

    # Convert skills
    if skills_src.exists():
        if verbose:
            print("Converting skills to Copilot format...")

        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                if convert_skill_to_copilot(skill_dir, skills_dest):
                    stats["skills"] += 1
                    if verbose:
                        print(f"  ✓ {skill_dir.name}")
                else:
                    stats["errors"].append(f"skill:{skill_dir.name}")

    if verbose:
        print(f"\nCopilot conversion complete: {stats['agents']} agents, {stats['skills']} skills")
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")

    return stats


# =============================================================================
# CLI ENTRY POINT
# =============================================================================


def convert_copilot(source_dir: str, output_unused: str, force: bool = False):
    """Bridge for CLI compatibility."""
    root_path = Path(source_dir).resolve()

    # Check for .agent in local or master
    if root_path.name == ".agent":
        source_root = root_path.parent
    elif (root_path / ".agent").exists():
        source_root = root_path
    else:
        master_path = get_master_agent_dir()
        if master_path.exists():
            print(f"{Colors.YELLOW}🔔 Local .agent not found, using Master Vault: {master_path}{Colors.ENDC}")
            source_root = master_path.parent
        else:
            print(f"{Colors.RED}❌ Error: No agent source found. Run 'agent-bridge update' first.{Colors.ENDC}")
            return

    # Confirmation for Copilot Overwrite
    github_dir = Path(".github").resolve()
    if github_dir.exists() and not force:
        if not ask_user("Found existing '.github'. Update agents & skills?", default=True):
            print(f"{Colors.YELLOW}⏭️  Skipping Copilot update.{Colors.ENDC}")
            return

    print(f"{Colors.HEADER}🏗️  Converting to Copilot Official Format (Professional Spec)...{Colors.ENDC}")
    convert_to_copilot(source_root, Path("."), verbose=True)
    print(f"{Colors.GREEN}✅ Copilot conversion complete!{Colors.ENDC}")


def copy_mcp_copilot(root_path: Path, force: bool = False):
    """Bridge for CLI compatibility."""
    dest_file = root_path / ".vscode" / "mcp.json"
    if dest_file.exists() and not force:
        if not ask_user(f"Found existing '{dest_file}'. Overwrite MCP config?", default=False):
            print(f"{Colors.YELLOW}🔒 Kept existing Copilot MCP config.{Colors.ENDC}")
            return

    source_root = root_path if (root_path / ".agent").exists() else get_master_agent_dir().parent
    if install_mcp_for_ide(source_root, root_path, "copilot"):
        print(f"{Colors.BLUE}  🔌 Integrated MCP config into Copilot (.vscode).{Colors.ENDC}")


def init_copilot(project_path: Path = None) -> bool:
    # Existing user function...
    """Initialize Copilot configuration in project."""
    project_path = project_path or Path.cwd()

    if not (project_path / ".agent").exists():
        print("Error: .agent directory not found. Run 'agent-bridge update' first.")
        return False

    stats = convert_to_copilot(project_path, project_path)
    return len(stats["errors"]) == 0


def clean_copilot(project_path: Path = None) -> bool:
    """Remove Copilot configuration from project."""
    project_path = project_path or Path.cwd()

    paths_to_remove = [
        project_path / ".github" / "agents",
        project_path / ".github" / "skills",
    ]

    for path in paths_to_remove:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed {path}")

    return True
