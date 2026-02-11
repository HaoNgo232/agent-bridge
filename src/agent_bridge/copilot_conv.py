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
# TOOL MAPPINGS - Copilot Built-in Tools
# =============================================================================
# Reference: https://code.visualstudio.com/docs/copilot/agents/agent-tools

# Agent role -> Copilot built-in tools mapping
# VS Code Copilot format: tools now use toolset prefixes
# Reference: https://code.visualstudio.com/docs/copilot/agents/agent-tools
AGENT_TOOLS_MAP = {
    # Planning & Research agents (read-only)
    "project-planner": ["search/codebase", "web/fetch", "web/githubRepo", "search/usages"],
    "explorer-agent": ["search/codebase", "web/fetch", "search/usages"],
    "code-archaeologist": ["search/codebase", "search/usages"],
    "product-manager": ["search/codebase", "web/fetch"],
    "product-owner": ["search/codebase", "web/fetch"],
    
    # Security & Review agents (read-only + limited execution)
    "security-auditor": ["search/codebase", "web/fetch", "search/usages"],
    "penetration-tester": ["search/codebase", "web/fetch", "read/terminalLastCommand"],
    
    # Implementation agents (full access)
    "frontend-specialist": ["search/codebase", "edit/editFiles", "web/fetch", "search/usages", "read/terminalLastCommand"],
    "backend-specialist": ["search/codebase", "edit/editFiles", "web/fetch", "search/usages", "read/terminalLastCommand"],
    "database-architect": ["search/codebase", "edit/editFiles", "web/fetch", "search/usages", "read/terminalLastCommand"],
    "mobile-developer": ["search/codebase", "edit/editFiles", "web/fetch", "search/usages", "read/terminalLastCommand"],
    "game-developer": ["search/codebase", "edit/editFiles", "web/fetch", "search/usages", "read/terminalLastCommand"],
    
    # Testing & QA agents
    "test-engineer": ["search/codebase", "edit/editFiles", "search/usages", "read/terminalLastCommand"],
    "qa-automation-engineer": ["search/codebase", "edit/editFiles", "search/usages", "read/terminalLastCommand"],
    
    # DevOps & Performance agents
    "devops-engineer": ["search/codebase", "edit/editFiles", "web/fetch", "read/terminalLastCommand"],
    "performance-optimizer": ["search/codebase", "edit/editFiles", "search/usages", "read/terminalLastCommand"],
    
    # Documentation & Content agents
    "documentation-writer": ["search/codebase", "edit/editFiles", "web/fetch"],
    "seo-specialist": ["search/codebase", "edit/editFiles", "web/fetch"],
    
    # Orchestration agents (can delegate to subagents)
    "orchestrator": ["search/codebase", "web/fetch", "search/usages"],
    "debugger": ["search/codebase", "edit/editFiles", "search/usages", "read/terminalLastCommand"],
}

# Agents that can invoke subagents
AGENT_SUBAGENTS_MAP = {
    "orchestrator": ["*"],  # Can invoke any agent
    "project-planner": ["*"],  # Can invoke any agent
    "debugger": ["backend-specialist", "frontend-specialist", "test-engineer"],
}

# Handoffs - workflow transitions between agents
# Note: 'model' field is optional and omitted for flexibility
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

    # Required: description (keep reasonable length, not artificially limited)
    description = metadata.get("description") or metadata.get("role", "")
    if not description:
        description = f"Specialized agent for {agent_slug.replace('-', ' ')} tasks"
    # Keep description under 500 chars for readability
    frontmatter["description"] = description[:500] if len(description) > 500 else description

    # Tools based on agent role (Copilot built-in tools with toolset prefix)
    tools = AGENT_TOOLS_MAP.get(agent_slug, ["search/codebase", "edit/editFiles", "web/fetch"])

    # Subagents configuration (agents field)
    subagents = AGENT_SUBAGENTS_MAP.get(agent_slug)
    if subagents:
        # Copilot spec: if `agents` is set, `agent` tool must be available.
        if "agent" not in tools:
            tools = [*tools, "agent"]
        frontmatter["agents"] = subagents

    frontmatter["tools"] = tools

    # Handoffs for workflow agents
    handoffs = AGENT_HANDOFFS_MAP.get(agent_slug)
    if handoffs:
        frontmatter["handoffs"] = handoffs

    # User-invokable (show in dropdown)
    # Hide internal/utility agents from picker
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
    """
    Convert a skill directory to Copilot Agent Skills format.
    
    Spec: https://agentskills.io/
    - name: lowercase + hyphens, max 64 chars (required)
    - description: what + when to use, max 1024 chars (required)
    """
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

            # Extract existing frontmatter if present
            existing_meta = {}
            frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
            if frontmatter_match:
                try:
                    existing_meta = yaml.safe_load(frontmatter_match.group(1)) or {}
                    content = content[frontmatter_match.end():]
                except yaml.YAMLError:
                    pass

            # Validate and normalize name (required, max 64 chars, lowercase + hyphens)
            normalized_name = existing_meta.get("name") or skill_name
            normalized_name = re.sub(r"[^a-z0-9-]", "-", normalized_name.lower())
            normalized_name = re.sub(r"-+", "-", normalized_name).strip("-")
            if len(normalized_name) > 64:
                normalized_name = normalized_name[:64].rstrip("-")

            # Extract or generate description (required, max 1024 chars)
            # Must describe WHAT + WHEN to use
            skill_description = existing_meta.get("description")
            if not skill_description:
                # Try to extract from content
                desc_match = re.search(r"^(?:>|Description:|Purpose:)\s*(.+?)$", content, re.MULTILINE | re.IGNORECASE)
                skill_description = (
                    desc_match.group(1).strip()
                    if desc_match
                    else f"Skill for {skill_name.replace('-', ' ')}. Use when working with related tasks."
                )
            
            # Validate description length
            if len(skill_description) > 1024:
                skill_description = skill_description[:1021] + "..."

            # Validate required fields
            if not normalized_name or not skill_description:
                print(f"  ⚠ Skill {skill_name}: missing required fields (name or description)")
                return False

            frontmatter = {
                "name": normalized_name,
                "description": skill_description,
            }

            output = f"---\n{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)}---\n\n{content.strip()}\n"

            (dest_skill_dir / "SKILL.md").write_text(output, encoding="utf-8")

        # Copy additional resources (scripts, examples, references)
        SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
        for item in source_dir.iterdir():
            if item.is_dir():
                if item.name not in SKIP_DIRS and not item.name.startswith("."):
                    shutil.copytree(item, dest_skill_dir / item.name, dirs_exist_ok=True)
            elif item.name != "SKILL.md" and item.suffix in (".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh"):
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
    stats = {"agents": 0, "skills": 0, "workflows": 0, "rules": 0, "errors": []}

    agents_src = source_root / ".agent" / "agents"
    agents_dest = dest_root / ".github" / "agents"

    skills_src = source_root / ".agent" / "skills"
    skills_dest = dest_root / ".github" / "skills"

    workflows_src = source_root / ".agent" / "workflows"
    workflows_dest = dest_root / ".github" / "prompts"

    rules_src = source_root / ".agent" / "rules"
    rules_dest = dest_root / ".github" / "instructions"

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

    # Convert workflows to prompt files
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to Copilot prompt files...")

        for workflow_file in workflows_src.glob("*.md"):
            dest_file = workflows_dest / workflow_file.name.replace(".md", ".prompt.md")
            if convert_workflow_to_prompt(workflow_file, dest_file):
                stats["workflows"] += 1
                if verbose:
                    print(f"  ✓ {workflow_file.name}")
            else:
                stats["errors"].append(f"workflow:{workflow_file.name}")

    # Convert rules to instructions
    if rules_src.exists():
        if verbose:
            print("Converting rules to Copilot instructions...")

        for rule_file in rules_src.glob("*.md"):
            dest_file = rules_dest / rule_file.name.replace(".md", ".instructions.md")
            if convert_rule_to_instruction(rule_file, dest_file):
                stats["rules"] += 1
                if verbose:
                    print(f"  ✓ {rule_file.name}")
            else:
                stats["errors"].append(f"rule:{rule_file.name}")

    if verbose:
        print(f"\nCopilot conversion complete:")
        print(f"  {stats['agents']} agents, {stats['skills']} skills")
        print(f"  {stats['workflows']} workflows, {stats['rules']} rules")
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")

    return stats


def convert_workflow_to_prompt(source_path: Path, dest_path: Path) -> bool:
    """
    Convert workflow to Copilot prompt file (.prompt.md).
    
    Spec: https://code.visualstudio.com/docs/copilot/customization/prompt-files
    - name: prompt name (optional, defaults to filename)
    - description: short description (optional)
    - agent: ask/agent/plan or custom agent name (optional)
    - model: language model (optional)
    - tools: list of tool names (optional)
    - argument-hint: hint text for chat input (optional)
    """
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        content = source_path.read_text(encoding="utf-8")

        # Extract existing frontmatter
        existing_meta = {}
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if frontmatter_match:
            try:
                existing_meta = yaml.safe_load(frontmatter_match.group(1)) or {}
                content = content[frontmatter_match.end():]
            except yaml.YAMLError:
                pass

        # Extract workflow name from filename (e.g., "brainstorm.md" -> "brainstorm")
        workflow_name = source_path.stem

        # Build frontmatter for prompt file
        frontmatter = {}
        
        # Name (optional, defaults to filename without extension)
        if "name" in existing_meta:
            frontmatter["name"] = existing_meta["name"]
        
        # Description (optional)
        if "description" in existing_meta:
            frontmatter["description"] = existing_meta["description"]
        elif desc_match := re.search(r"^##?\s*Purpose\s*\n\n(.+?)(?:\n\n|\n##)", content, re.DOTALL):
            frontmatter["description"] = desc_match.group(1).strip()[:200]
        
        # Agent (optional: ask/agent/plan or custom agent)
        if "agent" in existing_meta:
            frontmatter["agent"] = existing_meta["agent"]
        
        # Model (optional)
        if "model" in existing_meta:
            frontmatter["model"] = existing_meta["model"]
        
        # Tools (optional)
        if "tools" in existing_meta:
            frontmatter["tools"] = existing_meta["tools"]
        
        # Argument hint (optional)
        if "argument-hint" in existing_meta:
            frontmatter["argument-hint"] = existing_meta["argument-hint"]

        # Write prompt file
        if frontmatter:
            output = f"---\n{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)}---\n\n{content.strip()}\n"
        else:
            output = content.strip() + "\n"

        dest_path.write_text(output, encoding="utf-8")
        return True

    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def convert_rule_to_instruction(source_path: Path, dest_path: Path) -> bool:
    """
    Convert rule to Copilot instruction file (.instructions.md).
    
    Spec: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
    - name: display name (optional, defaults to filename)
    - description: short description (optional)
    - applyTo: glob pattern for file matching (optional, e.g., "**/*.py")
    """
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        content = source_path.read_text(encoding="utf-8")

        # Extract existing frontmatter
        existing_meta = {}
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if frontmatter_match:
            try:
                existing_meta = yaml.safe_load(frontmatter_match.group(1)) or {}
                content = content[frontmatter_match.end():]
            except yaml.YAMLError:
                pass

        # Build frontmatter for instruction file
        frontmatter = {}
        
        # Name (optional)
        if "name" in existing_meta:
            frontmatter["name"] = existing_meta["name"]
        
        # Description (optional)
        if "description" in existing_meta:
            frontmatter["description"] = existing_meta["description"]
        
        # ApplyTo (optional, glob pattern)
        if "applyTo" in existing_meta:
            frontmatter["applyTo"] = existing_meta["applyTo"]
        elif "trigger" in existing_meta:
            # Convert trigger to applyTo
            trigger = existing_meta["trigger"]
            if trigger == "always_on":
                frontmatter["applyTo"] = "**"
            elif isinstance(trigger, str) and "*" in trigger:
                frontmatter["applyTo"] = trigger

        # Write instruction file
        if frontmatter:
            output = f"---\n{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)}---\n\n{content.strip()}\n"
        else:
            output = content.strip() + "\n"

        dest_path.write_text(output, encoding="utf-8")
        return True

    except Exception as e:
        print(f"  Error converting rule {source_path.name}: {e}")
        return False


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
