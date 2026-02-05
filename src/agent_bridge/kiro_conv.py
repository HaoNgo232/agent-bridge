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

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import os
import re
import shutil
import subprocess
from .utils import Colors, ask_user, get_master_agent_dir, install_mcp_for_ide

import yaml


# =============================================================================
# KIRO AGENT CONFIGURATION
# =============================================================================

# Tool permissions mapping
KIRO_TOOLS = [
    "fs_read",      # Read files
    "fs_write",     # Write files
    "fs_list",      # List directory
    "bash",         # Execute shell commands
    "web_search",   # Web search
    "web_fetch",    # Fetch URLs
    "code_search",  # Search code
    "use_mcp",      # Use MCP tools
]

# Agent role -> configuration mapping
AGENT_CONFIG_MAP = {
    "frontend-specialist": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search"],
        "allowedCommands": [
            "npm *", "npx *", "yarn *", "pnpm *",
            "node *", "tsc *", "eslint *", "prettier *",
            "git status", "git diff *", "git log *",
        ],
        "allowedPaths": ["src/**", "components/**", "pages/**", "app/**", "public/**", "styles/**"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "backend-specialist": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search"],
        "allowedCommands": [
            "npm *", "node *", "python *", "pip *",
            "docker *", "docker-compose *",
            "git status", "git diff *", "git log *",
            "curl *", "wget *",
        ],
        "allowedPaths": ["src/**", "api/**", "server/**", "lib/**", "services/**"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "database-architect": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search"],
        "allowedCommands": [
            "npx prisma *", "npx drizzle-kit *",
            "psql *", "mysql *", "sqlite3 *",
            "git status", "git diff *",
        ],
        "allowedPaths": ["prisma/**", "drizzle/**", "migrations/**", "db/**", "schema/**"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "security-auditor": {
        "tools": ["fs_read", "fs_list", "code_search", "web_search"],
        "allowedCommands": [
            "npm audit", "yarn audit",
            "git log *", "git diff *",
            "grep *", "find *",
        ],
        "allowedPaths": ["**/*"],  # Read-only access to all
        "autoApprove": ["fs_read", "fs_list", "code_search"],
        "denyWrite": True,  # Custom flag to prevent writes
    },
    "test-engineer": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search"],
        "allowedCommands": [
            "npm test *", "npm run test *", "npx jest *", "npx vitest *",
            "npx playwright *", "npx cypress *",
            "python -m pytest *",
            "git status", "git diff *",
        ],
        "allowedPaths": ["tests/**", "test/**", "__tests__/**", "*.test.*", "*.spec.*"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "devops-engineer": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search"],
        "allowedCommands": [
            "docker *", "docker-compose *",
            "kubectl *", "helm *",
            "terraform *", "aws *", "gcloud *", "az *",
            "git *",
        ],
        "allowedPaths": [".github/**", "docker/**", "k8s/**", "terraform/**", "infra/**"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "documentation-writer": {
        "tools": ["fs_read", "fs_write", "fs_list", "code_search", "web_search"],
        "allowedCommands": [
            "git status", "git log *",
            "npx typedoc *", "npx jsdoc *",
        ],
        "allowedPaths": ["docs/**", "*.md", "README*", "CHANGELOG*", "*.mdx"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "explorer-agent": {
        "tools": ["fs_read", "fs_list", "code_search", "web_search"],
        "allowedCommands": [
            "git log *", "git status",
            "find *", "grep *", "tree *",
            "cat *", "head *", "tail *",
        ],
        "allowedPaths": ["**/*"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
        "denyWrite": True,
    },
    "project-planner": {
        "tools": ["fs_read", "fs_list", "code_search", "web_search"],
        "allowedCommands": [
            "git log *", "git status",
            "find *", "tree *",
        ],
        "allowedPaths": ["**/*"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
        "canDelegateToAgents": ["*"],  # Can invoke any agent
    },
    "orchestrator": {
        "tools": ["fs_read", "fs_list", "code_search"],
        "allowedCommands": ["git status", "git log *"],
        "allowedPaths": ["**/*"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
        "canDelegateToAgents": ["*"],
    },
    "debugger": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search"],
        "allowedCommands": [
            "node --inspect *", "python -m pdb *",
            "npm run *", "node *",
            "git diff *", "git log *", "git blame *",
        ],
        "allowedPaths": ["**/*"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
    "performance-optimizer": {
        "tools": ["fs_read", "fs_write", "fs_list", "bash", "code_search", "web_fetch"],
        "allowedCommands": [
            "npx lighthouse *", "npm run build *",
            "node --prof *", "python -m cProfile *",
        ],
        "allowedPaths": ["**/*"],
        "autoApprove": ["fs_read", "fs_list", "code_search"],
    },
}

# Default config for unknown agents
DEFAULT_AGENT_CONFIG = {
    "tools": ["fs_read", "fs_list", "code_search"],
    "allowedCommands": ["git status", "git log *"],
    "allowedPaths": ["**/*"],
    "autoApprove": ["fs_read", "fs_list"],
}


# =============================================================================
# METADATA EXTRACTION
# =============================================================================

def extract_agent_metadata(content: str, filename: str) -> Dict[str, Any]:
    """Extract metadata from agent markdown content."""
    metadata = {"name": "", "description": "", "instructions": ""}
    
    # Check existing frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if fm_match:
        try:
            existing = yaml.safe_load(fm_match.group(1))
            if existing:
                metadata.update(existing)
        except:
            pass
    
    # Extract name from H1
    name_match = re.search(r'^#\s+(.+?)(?:\s*[-–—]\s*(.+))?$', content, re.MULTILINE)
    if name_match:
        metadata["name"] = name_match.group(1).strip()
        if name_match.group(2):
            metadata["description"] = name_match.group(2).strip()
    
    # Fallback name
    if not metadata["name"]:
        metadata["name"] = filename.replace('.md', '').replace('-', ' ').title()
    
    # Extract description from content
    if not metadata.get("description"):
        desc_match = re.search(r'(?:You are|Role:|Description:)\s*(.+?)(?:\n\n|\n#)', 
                               content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            metadata["description"] = desc_match.group(1).strip()[:200]
    
    # Use content as prompt (without frontmatter)
    prompt = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
    metadata["prompt"] = prompt.strip()
    
    return metadata


def generate_kiro_agent_json(agent_slug: str, metadata: Dict[str, Any], mcp_server_names: List[str] = None) -> Dict[str, Any]:
    """Generate professional Kiro agent JSON following the latest official spec."""
    
    # Get role-specific config or default
    config = AGENT_CONFIG_MAP.get(agent_slug, DEFAULT_AGENT_CONFIG)
    
    # Tool normalization (Internal -> Kiro Standard)
    TOOL_MAP = {
        "fs_read": "read",
        "fs_write": "write",
        "fs_list": "list",
        "bash": "shell",
        "web_search": "search",
        "code_search": "code_search"
    }
    
    # Normalize base tools and auto-approve tools
    original_tools = config.get("tools", DEFAULT_AGENT_CONFIG["tools"])
    base_tools = [TOOL_MAP.get(t, t) for t in original_tools]
    
    original_auto = config.get("autoApprove", DEFAULT_AGENT_CONFIG["autoApprove"])
    allowed_tools = [TOOL_MAP.get(t, t) for t in original_auto]
    
    # Auto-trust MCP servers (Official Spec: @server/*)
    if mcp_server_names:
        for mcp in mcp_server_names:
            trust_pattern = f"@{mcp}/*"
            if trust_pattern not in allowed_tools:
                allowed_tools.append(trust_pattern)

    agent_json = {
        "name": metadata.get("name") or agent_slug.replace("-", " ").title(),
        "description": metadata.get("description") or f"Specialized agent for {agent_slug.replace('-', ' ')}",
        "prompt": metadata.get("prompt", ""),
        
        # Tools allowed for the agent
        "tools": base_tools,
        
        # Tools allowed without prompting (Auto-approve)
        "allowedTools": allowed_tools,
        
        # Integration with MCP
        "includeMcpJson": True,
        
        # Persistent knowledge (Steering & Skills)
        "resources": [
            "file://.kiro/steering/**/*.md",
            "file://.kiro/skills/**/SKILL.md"
        ],
        
        # Lifecycle Hooks
        "hooks": {
            "agentSpawn": [
                {
                    "command": "git status --short 2>/dev/null || true",
                    "timeout_ms": 3000
                }
            ]
        }
    }
    
    # Build toolsSettings for granular control (Official Spec)
    tools_settings = {}
    
    # 1. Shell settings
    if "shell" in base_tools and config.get("allowedCommands"):
        tools_settings["shell"] = {
            "allowedCommands": config["allowedCommands"],
            "autoAllowReadonly": True
        }
    
    # 2. File Read settings
    if "read" in base_tools and config.get("allowedPaths"):
        tools_settings["read"] = {
            "allowedPaths": config["allowedPaths"],
            "autoAllowReadonly": True
        }
        
    # 3. File Write settings
    if "write" in base_tools and config.get("allowedPaths"):
        tools_settings["write"] = {
            "allowedPaths": config["allowedPaths"]
        }

    if tools_settings:
        agent_json["toolsSettings"] = tools_settings
    
    # Optional: Map model if present in metadata
    if metadata.get("model"):
        agent_json["model"] = metadata["model"]
    elif config.get("model"):
        agent_json["model"] = config["model"]
        
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
        dest_path.write_text(
            json.dumps(agent_json, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
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
        workflow_name = source_path.stem.lower()
        
        # Extract existing frontmatter for description
        description = "Custom workflow prompt"
        fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if fm_match:
            try:
                fm_data = yaml.safe_load(fm_match.group(1))
                if isinstance(fm_data, dict) and fm_data.get("description"):
                    description = fm_data["description"]
            except: pass
            
        # Build Kiro Prompt frontmatter
        prompt_fm = {
            "description": description,
            "arguments": [
                {
                    "name": "args",
                    "description": "Arguments for the workflow",
                    "required": False
                }
            ]
        }
        
        # If content has $ARGUMENTS, it's a good sign it needs args
        has_args = "$ARGUMENTS" in content
        if not has_args:
            prompt_fm["arguments"] = []
            
        # Clean content (remove old frontmatter)
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        
        # Replace $ARGUMENTS with {{args}} for Kiro template syntax
        content_final = content_clean.replace("$ARGUMENTS", "{{args}}").strip()
        
        # Build final output
        output = f"---\n{yaml.dump(prompt_fm, sort_keys=False)}---\n\n{content_final}\n"
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting prompt {source_path.name}: {e}")
        return False


def convert_workflow_to_steering(source_path: Path, dest_path: Path) -> bool:

    """Convert workflow to Kiro steering file."""
    try:
        content = source_path.read_text(encoding="utf-8")
        
        # Remove frontmatter if exists
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content_clean, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def copy_rules_to_steering(source_dir: Path, dest_dir: Path) -> bool:
    """
    Copy rules files vào Kiro steering directory.
    
    Theo Kiro spec, rules (như GEMINI.md) phải được đặt trong .kiro/steering/
    vì steering là nơi chứa "persistent knowledge about your project".
    
    Args:
        source_dir: Thư mục rules nguồn (.agent/rules)
        dest_dir: Thư mục steering đích (.kiro/steering)
    
    Returns:
        True nếu thành công, False nếu có lỗi
    """
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for item in source_dir.iterdir():
            if item.is_file() and item.suffix == '.md':
                dest_item = dest_dir / item.name
                shutil.copy2(item, dest_item)
        
        return True
    except Exception as e:
        print(f"  Error copying rules to steering: {e}")
        return False


def copy_architecture_to_steering(source_file: Path, dest_dir: Path) -> bool:
    """
    Copy ARCHITECTURE.md vào Kiro steering directory.
    
    Theo Kiro spec, architecture docs phải được đặt trong .kiro/steering/
    vì đây là project knowledge/conventions.
    
    Args:
        source_file: File ARCHITECTURE.md nguồn
        dest_dir: Thư mục steering đích (.kiro/steering)
    
    Returns:
        True nếu thành công, False nếu có lỗi
    """
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / source_file.name
        shutil.copy2(source_file, dest_file)
        return True
    except Exception as e:
        print(f"  Error copying ARCHITECTURE.md to steering: {e}")
        return False


def copy_mcp_config(source_file: Path, dest_file: Path) -> bool:
    """
    Copy MCP config file vào Kiro settings.
    
    Args:
        source_file: File mcp_config.json nguồn
        dest_file: File mcp.json đích (trong .kiro/settings/)
    
    Returns:
        True nếu thành công, False nếu có lỗi
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
    
    Skill ui-ux-pro-max có CLI riêng:
    https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
    
    Nếu uipro CLI chưa có, tự động install: npm install -g uipro-cli
    Sau đó chạy: uipro init --ai kiro
    
    Args:
        project_root: Project root directory (nơi chạy uipro init)
        verbose: Print progress messages
    
    Returns:
        True nếu thành công, False nếu có lỗi
    """
    try:
        # Check xem uipro CLI đã được install chưa
        check_result = subprocess.run(
            ["uipro", "--version"],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        # Nếu chưa có, auto-install
        if check_result.returncode != 0:
            if verbose:
                print(f"  📦 uipro CLI not found, installing globally...")
            
            # Chạy npm install -g uipro-cli
            install_result = subprocess.run(
                ["npm", "install", "-g", "uipro-cli"],
                capture_output=True,
                text=True
            )
            
            if install_result.returncode != 0:
                if verbose:
                    print(f"  ⚠️  Failed to install uipro-cli: {install_result.stderr}")
                    print(f"  💡 Try manually: npm install -g uipro-cli")
                return False
            
            if verbose:
                print(f"  ✓ uipro-cli installed successfully")
        
        if verbose:
            print(f"  📥 Installing ui-ux-pro-max via uipro CLI...")
        
        # Chạy uipro init --ai kiro
        result = subprocess.run(
            ["uipro", "init", "--ai", "kiro"],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        if result.returncode != 0:
            if verbose:
                print(f"  ⚠️  uipro init failed: {result.stderr}")
            return False
        
        if verbose:
            print(f"  ✓ ui-ux-pro-max installed via uipro CLI")
        
        return True
        
    except FileNotFoundError as e:
        if verbose:
            if "npm" in str(e):
                print(f"  ⚠️  npm not found. Please install Node.js first.")
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
    
    Converts theo Kiro official spec (https://kiro.dev/docs/cli/):
    - agents/ → .kiro/agents/ (JSON format)
    - skills/ → .kiro/skills/ (full copy)
    - workflows/ → .kiro/steering/ (remove frontmatter)
    - rules/ → .kiro/steering/ (GEMINI.md và các rules khác)
    - ARCHITECTURE.md → .kiro/steering/ (project knowledge)
    - mcp_config.json → .kiro/settings/mcp.json
    
    NOTE: scripts/ và .shared/ KHÔNG được convert vì không thuộc Kiro spec.
    
    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root
        verbose: Print progress messages
    
    Returns:
        Dict with conversion statistics
    """
    stats = {
        "agents": 0, 
        "skills": 0, 
        "steering": 0,
        "mcp": 0,
        "warnings": [],
        "errors": []
    }
    
    # Define source và destination paths
    agent_root = source_root / ".agent"
    kiro_root = dest_root / ".kiro"
    
    agents_src = agent_root / "agents"
    agents_dest = kiro_root / "agents"
    
    skills_src = agent_root / "skills"
    skills_dest = kiro_root / "skills"
    
    workflows_src = agent_root / "workflows"
    steering_dest = kiro_root / "steering"
    
    rules_src = agent_root / "rules"
    architecture_src = agent_root / "ARCHITECTURE.md"
    
    mcp_src = agent_root / "mcp_config.json"
    mcp_dest = kiro_root / "settings" / "mcp.json"
    
    # Components không thuộc Kiro spec
    scripts_src = agent_root / "scripts"
    shared_src = agent_root / ".shared"
    
    # Load MCP config to get server names for auto-trust
    mcp_server_names = []
    if mcp_src.exists():
        try:
            mcp_data = json.loads(mcp_src.read_text(encoding="utf-8"))
            mcp_server_names = list(mcp_data.get("mcpServers", {}).keys())
        except: pass

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
    
    # Convert workflows to Prompts (theo Kiro spec)
    prompts_dest = dest_root / ".kiro" / "prompts"
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to prompts...")
        
        for workflow_file in workflows_src.glob("*.md"):
            dest_file = prompts_dest / workflow_file.name
            if convert_workflow_to_prompt(workflow_file, dest_file):
                stats["steering"] += 1 # Count as steering/prompt
                if verbose:
                    print(f"  ✓ @{workflow_file.stem}")
            else:
                stats["errors"].append(f"prompt:{workflow_file.name}")

    # Convert workflows to steering (backup/knowledge)
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to steering...")
        
        for workflow_file in workflows_src.glob("*.md"):
            dest_file = steering_dest / workflow_file.name
            if convert_workflow_to_steering(workflow_file, dest_file):
                stats["steering"] += 1
                if verbose:
                    print(f"  ✓ {workflow_file.name}")
            else:
                stats["errors"].append(f"steering:{workflow_file.name}")
    
    # Copy rules to steering (theo Kiro spec)
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
    
    # Copy ARCHITECTURE.md to steering (theo Kiro spec)
    if architecture_src.exists():
        if verbose:
            print("Copying ARCHITECTURE.md to steering...")
        
        if copy_architecture_to_steering(architecture_src, steering_dest):
            stats["steering"] += 1
            if verbose:
                print(f"  ✓ ARCHITECTURE.md → steering/")
        else:
            stats["errors"].append("architecture:copy_failed")
    
    # Copy MCP config
    if mcp_src.exists():
        if verbose:
            print("Copying MCP configuration...")
        
        if copy_mcp_config(mcp_src, mcp_dest):
            stats["mcp"] = 1
            if verbose:
                print(f"  ✓ MCP config → settings/mcp.json")
        else:
            stats["errors"].append("mcp:copy_failed")
    
    # Install ui-ux-pro-max skill via uipro CLI (nếu có workflow)
    ui_ux_workflow = workflows_src / "ui-ux-pro-max.md" if workflows_src.exists() else None
    if ui_ux_workflow and ui_ux_workflow.exists():
        if verbose:
            print("Installing ui-ux-pro-max skill...")
        
        if fetch_external_skill_resources(source_root, verbose):
            # CLI sẽ tự động tạo .kiro/skills/ui-ux-pro-max/
            pass
        else:
            stats["warnings"].append("ui-ux-pro-max install failed (install uipro CLI: npm install -g uipro-cli)")

    
    # Warnings cho components không được convert
    if scripts_src.exists():
        stats["warnings"].append("scripts/ not converted (not part of Kiro spec)")
    
    if shared_src.exists():
        stats["warnings"].append(".shared/ not converted (use external repos like ui-ux-pro-max)")

    
    # Final summary
    if verbose:
        print(f"\n{Colors.GREEN}✨ Kiro conversion complete (Official Spec):{Colors.ENDC}")
        print(f"  • {stats['agents']} agents")
        print(f"  • {stats['skills']} skills")
        print(f"  • {stats['steering']} steering files (workflows + rules + architecture)")
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



# =============================================================================
# CLI ENTRY POINTS
# =============================================================================

def convert_kiro(source_dir: str, output_dir: str, force: bool = False):
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
            print(f"{Colors.RED}❌ Error: No source tri thức found.{Colors.ENDC}")
            return

    # Confirmation for Kiro Overwrite
    if (Path(".").resolve() / ".kiro").exists() and not force:
        if not ask_user(f"Found existing '.kiro'. Update agents & workflows?", default=True):
             print(f"{Colors.YELLOW}⏭️  Skipping Kiro update.{Colors.ENDC}")
             return

    print(f"{Colors.HEADER}🏗️  Converting to Kiro Format (Professional Spec)...{Colors.ENDC}")
    convert_to_kiro(source_root, Path("."), verbose=True)
    print(f"{Colors.GREEN}✅ Kiro conversion complete!{Colors.ENDC}")

def copy_mcp_kiro(root_path: Path, force: bool = False):
    """Bridge for CLI compatibility."""
    dest_file = root_path / ".kiro" / "settings" / "mcp.json"
    if dest_file.exists() and not force:
        if not ask_user(f"Found existing '{dest_file}'. Overwrite MCP config?", default=False):
            print(f"{Colors.YELLOW}🔒 Kept existing Kiro MCP config.{Colors.ENDC}")
            return
    
    source_root = root_path if (root_path / ".agent").exists() else get_master_agent_dir().parent
    if install_mcp_for_ide(source_root, root_path, "kiro"):
        print(f"{Colors.BLUE}  🔌 Integrated MCP config into Kiro settings.{Colors.ENDC}")

def init_kiro(project_path: Path = None) -> bool:
    # Existing user function...
    """Initialize Kiro configuration in project."""
    project_path = project_path or Path.cwd()
    
    if not (project_path / ".agent").exists():
        print("Error: .agent directory not found. Run 'agent-bridge update' first.")
        return False
    
    stats = convert_to_kiro(project_path, project_path)
    return len(stats["errors"]) == 0


def clean_kiro(project_path: Path = None) -> bool:
    """Remove Kiro configuration from project."""
    project_path = project_path or Path.cwd()
    
    paths_to_remove = [
        project_path / ".kiro" / "agents",
        project_path / ".kiro" / "skills",
        project_path / ".kiro" / "steering",
    ]
    
    for path in paths_to_remove:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed {path}")
    
    return True