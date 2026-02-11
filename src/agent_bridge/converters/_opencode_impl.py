"""
OpenCode Converter
Converts Antigravity Kit agents/skills to OpenCode format.

Output structure:
- .opencode/agents/*.md (agents with frontmatter: mode, tools, permission)
- .opencode/commands/*.md (custom commands)
- .opencode/skills/<skill-name>/SKILL.md
- .opencode/opencode.json (main config)
- .opencode/mcp.json (MCP configuration)

Reference: https://opencode.ai/docs/config/
           https://opencode.ai/docs/agents/
           https://opencode.ai/docs/commands/
"""

import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict

import yaml

# =============================================================================
# OPENCODE AGENT CONFIGURATION
# =============================================================================

# Agent modes
AGENT_MODES = {
    "primary": "primary",  # Main agents, switchable with Tab
    "subagent": "subagent",  # Invoked by primary agents or @mention
}

# Agent role -> configuration mapping
AGENT_CONFIG_MAP = {
    # Primary agents (main development agents)
    "orchestrator": {
        "mode": "primary",
        "description": "Orchestrates tasks and delegates to specialized agents",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"task": {"*": "allow"}},  # Can invoke any subagent
    },
    "frontend-specialist": {
        "mode": "primary",
        "description": "Frontend development with React, Vue, and web technologies",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "allow", "bash": "allow"},
    },
    "backend-specialist": {
        "mode": "primary",
        "description": "Backend development with APIs, databases, and server logic",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "allow", "bash": "allow"},
    },
    # Subagents (specialized tasks)
    "project-planner": {
        "mode": "subagent",
        "description": "Creates implementation plans and task breakdowns",
        "tools": {"write": False, "edit": False, "bash": False},
        "permission": {"edit": "deny", "bash": "deny"},
    },
    "explorer-agent": {
        "mode": "subagent",
        "description": "Explores and analyzes codebase structure",
        "tools": {"write": False, "edit": False, "bash": False},
        "permission": {"edit": "deny"},
    },
    "security-auditor": {
        "mode": "subagent",
        "description": "Audits code for security vulnerabilities",
        "tools": {"write": False, "edit": False, "bash": False},
        "permission": {"edit": "deny", "bash": "deny"},
    },
    "test-engineer": {
        "mode": "subagent",
        "description": "Writes and maintains tests",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "allow", "bash": {"*": "ask", "npm test*": "allow", "npx jest*": "allow"}},
    },
    "debugger": {
        "mode": "subagent",
        "description": "Debugs issues and analyzes errors",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "ask", "bash": "ask"},
    },
    "documentation-writer": {
        "mode": "subagent",
        "description": "Writes and maintains documentation",
        "tools": {"write": True, "edit": True, "bash": False},
        "permission": {"edit": "allow", "bash": "deny"},
    },
    "database-architect": {
        "mode": "subagent",
        "description": "Designs database schemas and migrations",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "allow", "bash": {"*": "ask", "npx prisma*": "allow"}},
    },
    "devops-engineer": {
        "mode": "subagent",
        "description": "Manages deployment and infrastructure",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "allow", "bash": "ask"},
    },
    "performance-optimizer": {
        "mode": "subagent",
        "description": "Optimizes code and application performance",
        "tools": {"write": True, "edit": True, "bash": True},
        "permission": {"edit": "ask", "bash": "ask"},
    },
    "code-archaeologist": {
        "mode": "subagent",
        "description": "Analyzes legacy code and dependencies",
        "tools": {"write": False, "edit": False, "bash": False},
        "permission": {"edit": "deny"},
        "hidden": True,  # Internal agent
    },
}

# Default config for unknown agents — enriched from central registry
from agent_bridge.core.agent_registry import get_agent_role as _get_oc_role

_DEFAULT_AGENT_CONFIG = {
    "mode": "subagent",
    "description": "",
    "tools": {"write": False, "edit": False, "bash": False},
    "permission": {"edit": "ask"},
}


def _get_opencode_config(slug: str) -> dict:
    """Get OpenCode config, falling back to central registry for description."""
    if slug in AGENT_CONFIG_MAP:
        return AGENT_CONFIG_MAP[slug].copy()
    role = _get_oc_role(slug)
    config = _DEFAULT_AGENT_CONFIG.copy()
    if role:
        config["description"] = role.description
        config["mode"] = "primary" if role.category == "primary" else "subagent"
        config["tools"] = {
            "write": role.can_write,
            "edit": role.can_write,
            "bash": role.can_execute,
        }
        config["hidden"] = role.hidden
    return config

# Command templates from workflows
WORKFLOW_TO_COMMAND_MAP = {
    "plan": {
        "description": "Create an implementation plan for a feature or task",
        "agent": "project-planner",
        "subtask": True,
    },
    "debug": {
        "description": "Debug an issue or analyze an error",
        "agent": "debugger",
        "subtask": True,
    },
    "test": {
        "description": "Run tests and analyze results",
        "agent": "test-engineer",
        "subtask": True,
    },
    "create": {
        "description": "Create new components or features",
        "agent": "frontend-specialist",
        "subtask": False,
    },
    "deploy": {
        "description": "Deploy application or manage releases",
        "agent": "devops-engineer",
        "subtask": True,
    },
    "status": {
        "description": "Check project status and health",
        "agent": "explorer-agent",
        "subtask": True,
    },
    "brainstorm": {
        "description": "Brainstorm ideas and explore options",
        "agent": "project-planner",
        "subtask": True,
    },
    "enhance": {
        "description": "Enhance or improve existing code",
        "agent": "backend-specialist",
        "subtask": False,
    },
}


# =============================================================================
# OPENCODE FORMAT HELPERS
# =============================================================================


def generate_agent_frontmatter(config: Dict[str, Any]) -> str:
    """Generate YAML frontmatter for OpenCode agent."""
    frontmatter = {}

    # Required: description
    frontmatter["description"] = config.get("description", "")

    # Required: mode
    frontmatter["mode"] = config.get("mode", "subagent")

    # Optional: tools
    if config.get("tools"):
        frontmatter["tools"] = config["tools"]

    # Optional: permission
    if config.get("permission"):
        frontmatter["permission"] = config["permission"]

    # Optional: hidden
    if config.get("hidden"):
        frontmatter["hidden"] = True

    # Optional: temperature (for creative tasks)
    if config.get("temperature"):
        frontmatter["temperature"] = config["temperature"]

    return yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)


def generate_command_frontmatter(config: Dict[str, Any]) -> str:
    """Generate YAML frontmatter for OpenCode command."""
    frontmatter = {
        "description": config.get("description", ""),
    }

    if config.get("agent"):
        frontmatter["agent"] = config["agent"]

    if config.get("subtask"):
        frontmatter["subtask"] = True

    if config.get("model"):
        frontmatter["model"] = config["model"]

    return yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================


def convert_agent_to_opencode(source_path: Path, dest_path: Path) -> bool:
    """Convert agent to OpenCode format with full frontmatter."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()

        # Get config (OpenCode-specific map → central registry fallback)
        config = _get_opencode_config(agent_slug)

        # Extract description from content if not in config
        if not config.get("description"):
            desc_match = re.search(r"(?:You are|Role:)\s*(.+?)(?:\n\n|\n#)", content, re.IGNORECASE | re.DOTALL)
            if desc_match:
                config["description"] = desc_match.group(1).strip()[:150]
            else:
                config["description"] = f"Specialized agent for {agent_slug.replace('-', ' ')}"

        # Generate frontmatter
        frontmatter = generate_agent_frontmatter(config)

        # Remove existing frontmatter
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        # Build output
        output = f"---\n{frontmatter}---\n\n{content_clean.strip()}\n"

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_workflow_to_command(source_path: Path, dest_path: Path) -> bool:
    """Convert workflow to OpenCode command."""
    try:
        content = source_path.read_text(encoding="utf-8")
        workflow_slug = source_path.stem.lower()

        # Get command config
        config = WORKFLOW_TO_COMMAND_MAP.get(
            workflow_slug,
            {
                "description": f"Run {workflow_slug} workflow",
                "subtask": True,
            },
        )

        # Extract better description from content
        desc_match = re.search(
            r"^>\s*(.+?)$|^(?:Description|Purpose)[:\s]*(.+?)(?:\n|$)", content, re.MULTILINE | re.IGNORECASE
        )
        if desc_match:
            config["description"] = (desc_match.group(1) or desc_match.group(2) or "").strip()[:150]

        # Generate frontmatter
        frontmatter = generate_command_frontmatter(config)

        # Remove existing frontmatter, use content as template
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        # Build command template
        output = f"---\n{frontmatter}---\n\n{content_clean.strip()}\n"

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def convert_skill_to_opencode(source_dir: Path, dest_dir: Path) -> bool:
    """Convert skill directory to OpenCode format."""
    try:
        skill_name = source_dir.name
        dest_skill_dir = dest_dir / skill_name
        dest_skill_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files
        for item in source_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, dest_skill_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest_skill_dir / item.name)

        return True
    except Exception as e:
        print(f"  Error converting skill {source_dir.name}: {e}")
        return False


def generate_opencode_config(source_root: Path, dest_root: Path) -> bool:
    """Generate opencode.json configuration file."""
    try:
        config = {
            "$schema": "https://opencode.ai/config.json",
            # Instructions - glob patterns for rule files
            "instructions": [
                ".opencode/skills/*/SKILL.md",
                "AGENTS.md",
                "CONTRIBUTING.md",
            ],
            # Default agent
            "default_agent": "build",
            # Compaction settings
            "compaction": {
                "auto": True,
                "prune": True,
            },
            # Permission defaults
            "permission": {
                "edit": "allow",
                "bash": "ask",
            },
        }

        dest_file = dest_root / ".opencode" / "opencode.json"
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error generating opencode.json: {e}")
        return False


def convert_to_opencode(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for OpenCode format.

    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root
        verbose: Print progress messages

    Returns:
        Dict with conversion statistics
    """
    stats = {"agents": 0, "commands": 0, "skills": 0, "errors": [], "warnings": []}

    agents_src = source_root / ".agent" / "agents"
    agents_dest = dest_root / ".opencode" / "agents"

    workflows_src = source_root / ".agent" / "workflows"
    commands_dest = dest_root / ".opencode" / "commands"

    skills_src = source_root / ".agent" / "skills"
    skills_dest = dest_root / ".opencode" / "skills"

    # Convert agents
    if agents_src.exists():
        if verbose:
            print("Converting agents to OpenCode format...")

        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / agent_file.name
            if convert_agent_to_opencode(agent_file, dest_file):
                stats["agents"] += 1
                if verbose:
                    print(f"  ✓ {agent_file.name}")
            else:
                stats["errors"].append(f"agent:{agent_file.name}")

    # Convert workflows to commands
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to OpenCode commands...")

        for workflow_file in workflows_src.glob("*.md"):
            dest_file = commands_dest / workflow_file.name
            if convert_workflow_to_command(workflow_file, dest_file):
                stats["commands"] += 1
                if verbose:
                    print(f"  ✓ /{workflow_file.stem}")
            else:
                stats["errors"].append(f"command:{workflow_file.name}")

    # Convert skills
    if skills_src.exists():
        if verbose:
            print("Converting skills to OpenCode format...")

        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                if convert_skill_to_opencode(skill_dir, skills_dest):
                    stats["skills"] += 1
                    if verbose:
                        print(f"  ✓ {skill_dir.name}")
                else:
                    stats["errors"].append(f"skill:{skill_dir.name}")

    # Generate opencode.json
    if generate_opencode_config(source_root, dest_root):
        if verbose:
            print("  ✓ opencode.json")

    # Run external skill plugins (declarative, config-driven via .agent/plugins.json)
    try:
        from agent_bridge.core.plugins import PluginRunner

        runner = PluginRunner(source_root)
        plugin_results = runner.run_for_ide("opencode", dest_root, verbose=verbose)
        for pname, pstatus in plugin_results.items():
            if pstatus == "ok":
                if verbose:
                    print(f"  ✓ Plugin '{pname}' installed")
            elif pstatus.startswith("error"):
                stats["warnings"].append(f"Plugin '{pname}': {pstatus}")
    except ImportError:
        pass

    if verbose:
        print(
            f"\nOpenCode conversion complete: {stats['agents']} agents, {stats['commands']} commands, {stats['skills']} skills"
        )
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")

    return stats


def copy_mcp_opencode(root_path: Path, force: bool = False) -> bool:
    """Tich hop MCP config vao opencode.json."""
    from agent_bridge.utils import get_master_agent_dir, load_mcp_config

    source_root = root_path if (root_path / ".agent").exists() else get_master_agent_dir().parent
    mcp_config = load_mcp_config(source_root)

    if mcp_config:
        opencode_json_path = root_path / ".opencode" / "opencode.json"
        if opencode_json_path.exists():
            try:
                config = json.loads(opencode_json_path.read_text(encoding="utf-8"))
                config["mcp"] = {}
                source_servers = mcp_config.get("mcpServers", {})
                for name, server_config in source_servers.items():
                    new_config = {}
                    if "command" in server_config:
                        cmd = server_config["command"]
                        args = server_config.get("args", [])
                        if isinstance(cmd, str):
                            new_config["command"] = [cmd] + (args if isinstance(args, list) else [])
                        elif isinstance(cmd, list):
                            new_config["command"] = cmd
                        else:
                            new_config["command"] = [str(cmd)]
                    if "env" in server_config:
                        new_config["env"] = server_config["env"]
                    new_config["type"] = server_config.get("type", "local")
                    new_config["enabled"] = server_config.get("enabled", True)
                    config["mcp"][name] = new_config
                opencode_json_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
                return True
            except Exception:
                pass
    return False
