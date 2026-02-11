"""
Kiro CLI Converter
Converts Antigravity Kit agents/skills to Kiro CLI format.

Output structure:
- .kiro/agents/*.json (agent configurations with full options)
- .kiro/skills/<skill-name>/SKILL.md
- .kiro/steering/*.md (workflow/hook files)
- .kiro/settings/mcp.json (MCP configuration)

Reference: https://kiro.dev/docs/cli/custom-agents/configuration-reference/
"""

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List

import yaml

from agent_bridge.utils import Colors

# =============================================================================
# KIRO AGENT CONFIGURATION
# =============================================================================

# Danh sach built-in tools cua Kiro CLI (theo official spec)
# Ref: https://kiro.dev/docs/cli/reference/built-in-tools
KIRO_BUILT_IN_TOOLS = [
    "read",       # Doc file
    "write",      # Ghi file
    "shell",      # Thuc thi lenh shell
    "search",     # Tim kiem code trong project
    "knowledge",  # Truy cap knowledge base
]

# Map ten tool noi bo (Antigravity Kit) sang ten Kiro built-in
INTERNAL_TO_KIRO_TOOL_MAP = {
    "fs_read": "read",
    "fs_write": "write",
    "fs_list": "read",       # Kiro khong co "list" rieng, dung "read" thay the
    "bash": "shell",
    "code_search": "search",
    "web_search": "search",  # Web search khong phai built-in, fallback sang search
    "web_fetch": "shell",    # Khong co built-in, dung shell (curl/wget) thay the
    "use_mcp": None,         # Khong can map, MCP tools dung @server pattern
}

# =============================================================================
# KIRO CONFIG FROM CENTRAL REGISTRY
# =============================================================================
# Instead of a duplicate AGENT_CONFIG_MAP, we derive Kiro config from
# the central AgentRole definitions in core/agent_registry.py.

from agent_bridge.core.agent_registry import get_agent_role


def _role_to_kiro_config(slug: str) -> dict:
    """Derive Kiro tool/permission config from central AgentRole."""
    role = get_agent_role(slug)
    if not role:
        return {
            "tools": ["read", "search"],
            "allowedCommands": ["git status", "git log *"],
            "allowedPaths": ["**/*"],
        }

    tools = []
    if role.can_read:
        tools.append("read")
    if role.can_write:
        tools.append("write")
    if role.can_execute:
        tools.append("shell")
    if role.can_search:
        tools.append("search")
    # Documentation/planning agents get knowledge tool
    if role.slug in ("documentation-writer", "explorer-agent", "project-planner", "orchestrator"):
        tools.append("knowledge")

    config = {
        "tools": tools,
        "allowedCommands": role.allowed_commands or ["git status", "git log *"],
        "allowedPaths": role.allowed_paths,
    }

    # Read-only agents
    if not role.can_write:
        config["denyWrite"] = True

    return config


# =============================================================================
# METADATA EXTRACTION
# =============================================================================


def extract_agent_metadata(content: str, filename: str) -> Dict[str, Any]:
    """Extract metadata from agent markdown content."""
    metadata = {"name": "", "description": "", "instructions": ""}

    # Check existing frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if fm_match:
        try:
            existing = yaml.safe_load(fm_match.group(1))
            if existing and isinstance(existing, dict):
                metadata.update(existing)
        except (yaml.YAMLError, ValueError, TypeError):
            pass

    # Extract name from H1
    name_match = re.search(r"^#\s+(.+?)(?:\s*[-–—]\s*(.+))?$", content, re.MULTILINE)
    if name_match:
        metadata["name"] = name_match.group(1).strip()
        if name_match.group(2):
            metadata["description"] = name_match.group(2).strip()

    # Fallback name
    if not metadata["name"]:
        metadata["name"] = filename.replace(".md", "").replace("-", " ").title()

    # Extract description from content
    if not metadata.get("description"):
        desc_match = re.search(
            r"(?:You are|Role:|Description:)\s*(.+?)(?:\n\n|\n#)", content, re.IGNORECASE | re.DOTALL
        )
        if desc_match:
            metadata["description"] = desc_match.group(1).strip()[:200]

    # Use content as prompt (without frontmatter)
    prompt = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)
    metadata["prompt"] = prompt.strip()

    return metadata


def generate_kiro_agent_json(
    agent_slug: str, metadata: Dict[str, Any], mcp_server_names: List[str] = None
) -> Dict[str, Any]:
    """
    Tao JSON cau hinh agent theo Kiro CLI official spec.

    Ref: https://kiro.dev/docs/cli/custom-agents/configuration-reference

    Cac truong chinh:
    - tools: danh sach tools agent co the su dung
    - allowedTools: tools duoc AUTO-APPROVE (khong can xac nhan nguoi dung)
    - toolsSettings: cai dat chi tiet cho tung tool (allowedCommands, allowedPaths)
    - includeMcpJson: cho phep load MCP servers tu config files
    - hooks: lifecycle hooks (agentSpawn, userPromptSubmit, ...)
    - resources: file:// URIs cho knowledge base
    - model: model su dung ("inherit" = ke thua tu project config)

    Args:
        agent_slug: ten agent dang slug (vd: "frontend-specialist")
        metadata: metadata trich xuat tu agent markdown
        mcp_server_names: danh sach ten MCP servers de auto-trust

    Returns:
        Dict cau hinh agent JSON theo Kiro spec
    """
    # Derive config from central agent registry
    config = _role_to_kiro_config(agent_slug)

    # Lay danh sach tools (da dung ten Kiro built-in truc tiep)
    # Fallback cho truong hop config khong co tools (khong xay ra khi dung _role_to_kiro_config)
    base_tools = list(config.get("tools", ["read", "search"]))

    # Them MCP servers vao danh sach tools (Kiro spec: @server_name)
    if mcp_server_names:
        for mcp in mcp_server_names:
            mcp_tool_ref = f"@{mcp}"
            if mcp_tool_ref not in base_tools:
                base_tools.append(mcp_tool_ref)

    # === ALLOWED TOOLS (Auto-approve) ===
    # Auto-approve TOAN BO tools ma agent duoc cung cap (built-in + MCP)
    # Nguoi dung khong can xac nhan thu cong - dung git de rollback neu can
    allowed_tools = list(base_tools)

    # Them wildcard pattern cho MCP servers de auto-approve moi tool cua server
    if mcp_server_names:
        for mcp in mcp_server_names:
            trust_pattern = f"@{mcp}/*"
            if trust_pattern not in allowed_tools:
                allowed_tools.append(trust_pattern)

    # === XAY DUNG AGENT JSON ===
    agent_json = {
        "name": metadata.get("name") or agent_slug.replace("-", " ").title(),
        "description": metadata.get("description") or f"Specialized agent for {agent_slug.replace('-', ' ')}",
        "prompt": metadata.get("prompt", ""),
        # Tools agent co the su dung (Kiro spec: tools)
        "tools": base_tools,
        # Tools duoc auto-approve - KHONG can xac nhan (Kiro spec: allowedTools)
        "allowedTools": allowed_tools,
        # Load MCP servers tu .kiro/settings/mcp.json va global config
        "includeMcpJson": True,
        # Knowledge files (Kiro spec: resources voi file:// URIs)
        "resources": ["file://.kiro/steering/**/*.md", "file://.kiro/skills/**/SKILL.md"],
        # Lifecycle hooks - chay lenh khi agent khoi dong
        "hooks": {
            "agentSpawn": [
                {
                    "command": "git status --short 2>/dev/null || true",
                    "timeout_ms": 3000,
                }
            ]
        },
    }

    # === TOOLS SETTINGS (cai dat chi tiet cho tung tool) ===
    tools_settings = {}

    # Shell: gioi han cac lenh duoc phep chay
    if "shell" in base_tools and config.get("allowedCommands"):
        tools_settings["shell"] = {
            "allowedCommands": config["allowedCommands"],
            "autoAllowReadonly": True,
        }

    # Read: gioi han cac duong dan duoc phep doc
    if "read" in base_tools and config.get("allowedPaths"):
        tools_settings["read"] = {
            "allowedPaths": config["allowedPaths"],
            "autoAllowReadonly": True,
        }

    # Write: gioi han cac duong dan duoc phep ghi (chi khi agent co quyen write)
    if "write" in base_tools and config.get("allowedPaths") and not config.get("denyWrite"):
        tools_settings["write"] = {"allowedPaths": config["allowedPaths"]}

    if tools_settings:
        agent_json["toolsSettings"] = tools_settings

    # === MODEL ===
    # "inherit" = ke thua model tu project config, cho phep override theo agent
    if metadata.get("model"):
        agent_json["model"] = metadata["model"]
    elif config.get("model"):
        agent_json["model"] = config["model"]
    else:
        agent_json["model"] = "inherit"

    return agent_json


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================


def convert_agent_to_kiro(source_path: Path, dest_path: Path, mcp_server_names: List[str] = None) -> bool:
    """Convert agent to Kiro JSON format with full configuration."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()

        metadata = extract_agent_metadata(content, source_path.name)
        agent_json = generate_kiro_agent_json(agent_slug, metadata, mcp_server_names)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(json.dumps(agent_json, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_skill_to_kiro(source_dir: Path, dest_dir: Path) -> bool:
    """Convert skill directory to Kiro format."""
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


def convert_workflow_to_prompt(source_path: Path, dest_path: Path) -> bool:
    """
    Convert workflow to Kiro Prompt format.
    Kiro Prompts require YAML frontmatter with description and arguments.
    """
    try:
        content = source_path.read_text(encoding="utf-8")
        source_path.stem.lower()

        # Extract existing frontmatter for description
        description = "Custom workflow prompt"
        fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        if fm_match:
            try:
                fm_data = yaml.safe_load(fm_match.group(1))
                if isinstance(fm_data, dict) and fm_data.get("description"):
                    description = fm_data["description"]
            except (yaml.YAMLError, ValueError, TypeError):
                pass

        # Build Kiro Prompt frontmatter
        prompt_fm = {
            "description": description,
            "arguments": [{"name": "args", "description": "Arguments for the workflow", "required": False}],
        }

        # If content has $ARGUMENTS, it's a good sign it needs args
        has_args = "$ARGUMENTS" in content
        if not has_args:
            prompt_fm["arguments"] = []

        # Clean content (remove old frontmatter)
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        # Replace $ARGUMENTS with {{args}} for Kiro template syntax
        content_final = content_clean.replace("$ARGUMENTS", "{{args}}").strip()

        # Build final output
        fm_yaml = yaml.dump(prompt_fm, sort_keys=False).rstrip("\n")
        output = f"---\n{fm_yaml}\n---\n\n{content_final}\n"

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting prompt {source_path.name}: {e}")
        return False


def convert_workflow_to_steering(source_path: Path, dest_path: Path) -> bool:
    """Convert workflow to Kiro steering file with proper inclusion frontmatter."""
    try:
        content = source_path.read_text(encoding="utf-8")

        # Remove frontmatter if exists
        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL).strip()

        # Kiro steering files require inclusion frontmatter
        # Default to 'always' for workflow-derived steering
        steering_frontmatter = "---\ninclusion: always\n---\n\n"

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(f"{steering_frontmatter}{content_clean}\n", encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def copy_rules_to_steering(source_dir: Path, dest_dir: Path) -> bool:
    """
    Copy rules files into Kiro steering directory with proper frontmatter.

    Per Kiro spec, steering files need inclusion frontmatter to control
    when they are loaded. Rules are treated as 'always' inclusion by default.

    Args:
        source_dir: Source rules directory (.agent/rules)
        dest_dir: Destination steering directory (.kiro/steering)

    Returns:
        True on success, False on error
    """
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)

        STEERING_FRONTMATTER = "---\ninclusion: always\n---\n\n"

        for item in source_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                dest_item = dest_dir / item.name
                content = item.read_text(encoding="utf-8")

                # Check if content already has frontmatter
                has_fm = re.match(r"^---\n", content)
                if has_fm:
                    # Check if it already has inclusion field
                    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
                    if fm_match and "inclusion" in fm_match.group(1):
                        # Already has proper steering frontmatter, copy as-is
                        dest_item.write_text(content, encoding="utf-8")
                    else:
                        # Has frontmatter but no inclusion — strip and add proper one
                        content_clean = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)
                        dest_item.write_text(f"{STEERING_FRONTMATTER}{content_clean}", encoding="utf-8")
                else:
                    # No frontmatter at all — add steering frontmatter
                    dest_item.write_text(f"{STEERING_FRONTMATTER}{content}", encoding="utf-8")

        return True
    except Exception as e:
        print(f"  Error copying rules to steering: {e}")
        return False


def copy_architecture_to_steering(source_file: Path, dest_dir: Path) -> bool:
    """
    Copy ARCHITECTURE.md into Kiro steering directory with inclusion frontmatter.

    Per Kiro spec, architecture docs belong in .kiro/steering/
    as project knowledge/conventions. They use 'always' inclusion.

    Args:
        source_file: Source ARCHITECTURE.md file
        dest_dir: Destination steering directory (.kiro/steering)

    Returns:
        True on success, False on error
    """
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / source_file.name

        content = source_file.read_text(encoding="utf-8")

        # Add steering frontmatter if not present
        if not re.match(r"^---\n.*?inclusion.*?\n---", content, re.DOTALL):
            content = f"---\ninclusion: always\n---\n\n{content}"

        dest_file.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error copying ARCHITECTURE.md to steering: {e}")
        return False


def copy_mcp_config(source_file: Path, dest_file: Path) -> bool:
    """
    Copy MCP config file into Kiro settings.

    Args:
        source_file: Source mcp_config.json file
        dest_file: Destination mcp.json (in .kiro/settings/)

    Returns:
        True on success, False on error
    """
    try:
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, dest_file)
        return True
    except Exception as e:
        print(f"  Error copying MCP config: {e}")
        return False


def fetch_external_skill_resources(project_root: Path, verbose: bool = True) -> bool:
    """
    Install ui-ux-pro-max skill resources using uipro CLI.

    See: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

    If uipro CLI is not installed, prompts before auto-installing globally.
    Then runs: uipro init --ai kiro

    Args:
        project_root: Project root directory
        verbose: Print progress messages

    Returns:
        True on success, False on error
    """
    try:
        # Check if uipro CLI is installed
        check_result = subprocess.run(["uipro", "--version"], capture_output=True, text=True, cwd=str(project_root))

        # If not found, auto-install
        if check_result.returncode != 0:
            if verbose:
                print("  📦 uipro CLI not found, installing globally...")

            # Install globally via npm
            install_result = subprocess.run(["npm", "install", "-g", "uipro-cli"], capture_output=True, text=True)

            if install_result.returncode != 0:
                if verbose:
                    print(f"  ⚠️  Failed to install uipro-cli: {install_result.stderr}")
                    print("  💡 Try manually: npm install -g uipro-cli")
                return False

            if verbose:
                print("  ✓ uipro-cli installed successfully")

        if verbose:
            print("  📥 Installing ui-ux-pro-max via uipro CLI...")

        # Run uipro init for Kiro
        result = subprocess.run(
            ["uipro", "init", "--ai", "kiro"], capture_output=True, text=True, cwd=str(project_root)
        )

        if result.returncode != 0:
            if verbose:
                print(f"  ⚠️  uipro init failed: {result.stderr}")
            return False

        if verbose:
            print("  ✓ ui-ux-pro-max installed via uipro CLI")

        return True

    except FileNotFoundError as e:
        if verbose:
            if "npm" in str(e):
                print("  ⚠️  npm not found. Please install Node.js first.")
            else:
                print(f"  ⚠️  Command not found: {e}")
        return False
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Error installing ui-ux-pro-max: {e}")
        return False


def convert_to_kiro(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for Kiro CLI format.

    Converts per Kiro official spec (https://kiro.dev/docs/cli/):
    - agents/ -> .kiro/agents/ (JSON format)
    - skills/ -> .kiro/skills/ (full copy)
    - workflows/ -> .kiro/prompts/ (custom commands via @)
    - rules/ -> .kiro/steering/ (system prompts)
    - mcp_config.json -> .kiro/settings/mcp.json

    NOTE: scripts/, .shared/, ARCHITECTURE.md are NOT converted (not part of Kiro spec).

    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root
        verbose: Print progress messages

    Returns:
        Dict with conversion statistics
    """
    stats = {"agents": 0, "skills": 0, "prompts": 0, "steering": 0, "mcp": 0, "warnings": [], "errors": []}

    # Define source and destination paths
    agent_root = source_root / ".agent"
    kiro_root = dest_root / ".kiro"

    agents_src = agent_root / "agents"
    agents_dest = kiro_root / "agents"

    skills_src = agent_root / "skills"
    skills_dest = kiro_root / "skills"

    workflows_src = agent_root / "workflows"
    steering_dest = kiro_root / "steering"

    rules_src = agent_root / "rules"
    agent_root / "ARCHITECTURE.md"

    mcp_src = agent_root / "mcp_config.json"
    mcp_dest = kiro_root / "settings" / "mcp.json"

    # Components not part of Kiro spec (skipped)
    scripts_src = agent_root / "scripts"
    shared_src = agent_root / ".shared"

    # Load MCP config to get server names for auto-trust
    mcp_server_names = []
    if mcp_src.exists():
        try:
            mcp_data = json.loads(mcp_src.read_text(encoding="utf-8"))
            mcp_server_names = list(mcp_data.get("mcpServers", {}).keys())
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            if verbose:
                print(f"  Warning: Could not parse MCP config: {e}")

    # Convert agents to JSON
    if agents_src.exists():
        if verbose:
            print("Converting agents to Kiro JSON format...")

        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / f"{agent_file.stem}.json"
            if convert_agent_to_kiro(agent_file, dest_file, mcp_server_names):
                stats["agents"] += 1
                if verbose:
                    print(f"  ✓ {agent_file.stem}.json")
            else:
                stats["errors"].append(f"agent:{agent_file.name}")

    # Convert skills
    if skills_src.exists():
        if verbose:
            print("Converting skills to Kiro format...")

        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                if convert_skill_to_kiro(skill_dir, skills_dest):
                    stats["skills"] += 1
                    if verbose:
                        print(f"  ✓ {skill_dir.name}")
                else:
                    stats["errors"].append(f"skill:{skill_dir.name}")

    # Convert workflows to Prompts (per Kiro spec)
    prompts_dest = dest_root / ".kiro" / "prompts"
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to prompts...")

        for workflow_file in workflows_src.glob("*.md"):
            dest_file = prompts_dest / workflow_file.name
            if convert_workflow_to_prompt(workflow_file, dest_file):
                stats["prompts"] += 1
                if verbose:
                    print(f"  ✓ @{workflow_file.stem}")
            else:
                stats["errors"].append(f"prompt:{workflow_file.name}")

    # Copy rules to steering (per Kiro spec)
    if rules_src.exists():
        if verbose:
            print("Copying rules to steering...")

        if copy_rules_to_steering(rules_src, steering_dest):
            rule_count = len(list(rules_src.glob("*.md")))
            stats["steering"] += rule_count
            if verbose:
                print(f"  ✓ {rule_count} rule file(s) → steering/")
        else:
            stats["errors"].append("rules:copy_failed")

    # Copy MCP config
    if mcp_src.exists():
        if verbose:
            print("Copying MCP configuration...")

        if copy_mcp_config(mcp_src, mcp_dest):
            stats["mcp"] = 1
            if verbose:
                print("  ✓ MCP config → settings/mcp.json")
        else:
            stats["errors"].append("mcp:copy_failed")

    # Run external skill plugins (declarative, config-driven via .agent/plugins.json)
    try:
        from agent_bridge.core.plugins import PluginRunner

        runner = PluginRunner(source_root)
        plugin_results = runner.run_for_ide("kiro", dest_root, verbose=verbose)
        for pname, pstatus in plugin_results.items():
            if pstatus == "ok":
                if verbose:
                    print(f"  ✓ Plugin '{pname}' installed")
            elif pstatus.startswith("error"):
                stats["warnings"].append(f"Plugin '{pname}': {pstatus}")
    except ImportError:
        # Fallback: legacy hardcoded ui-ux-pro-max
        ui_ux_workflow = workflows_src / "ui-ux-pro-max.md" if workflows_src.exists() else None
        if ui_ux_workflow and ui_ux_workflow.exists():
            if verbose:
                print("Installing ui-ux-pro-max skill...")
            if fetch_external_skill_resources(source_root, verbose):
                pass
            else:
                stats["warnings"].append(
                    "ui-ux-pro-max install failed (install uipro CLI: npm install -g uipro-cli)"
                )

    # Warnings for components not converted
    if scripts_src.exists():
        stats["warnings"].append("scripts/ not converted (not part of Kiro spec)")

    if shared_src.exists():
        stats["warnings"].append(".shared/ not converted (use external repos like ui-ux-pro-max)")

    # Final summary
    if verbose:
        print(f"\n{Colors.GREEN}✨ Kiro conversion complete (Official Spec):{Colors.ENDC}")
        print(f"  • {stats['agents']} agents")
        print(f"  • {stats['skills']} skills")
        print(f"  • {stats['prompts']} prompts (@workflows)")
        print(f"  • {stats['steering']} steering files (system prompts)")
        print(f"  • {stats['mcp']} MCP config")

        if stats["warnings"]:
            print(f"\n{Colors.YELLOW}⚠️  Warnings:{Colors.ENDC}")
            for warning in stats["warnings"]:
                print(f"    - {warning}")

        if stats["errors"]:
            print(f"\n{Colors.RED}  ⚠️  Errors: {len(stats['errors'])}{Colors.ENDC}")
            for error in stats["errors"]:
                print(f"    - {error}")

    return stats


