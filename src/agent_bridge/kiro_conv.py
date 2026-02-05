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
    
    # Use content as instructions (without frontmatter)
    instructions = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
    metadata["instructions"] = instructions.strip()
    
    return metadata


def generate_kiro_agent_json(agent_slug: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Kiro agent JSON configuration."""
    
    # Get role-specific config or default
    config = AGENT_CONFIG_MAP.get(agent_slug, DEFAULT_AGENT_CONFIG)
    
    agent_json = {
        "name": metadata.get("name") or agent_slug.replace("-", " ").title(),
        "description": metadata.get("description") or f"Specialized agent for {agent_slug.replace('-', ' ')}",
        "instructions": metadata.get("instructions", ""),
        
        # Tool configuration
        "tools": config.get("tools", DEFAULT_AGENT_CONFIG["tools"]),
        
        # Security restrictions
        "allowedCommands": config.get("allowedCommands", []),
        "allowedPaths": config.get("allowedPaths", ["**/*"]),
        
        # Auto-approve for efficiency (safe tools)
        "autoApprove": config.get("autoApprove", []),
    }
    
    # Add deny flags if present
    if config.get("denyWrite"):
        agent_json["denyTools"] = ["fs_write"]
    
    # Add delegation capability for orchestrators
    if config.get("canDelegateToAgents"):
        agent_json["canDelegateToAgents"] = config["canDelegateToAgents"]
    
    return agent_json


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================

def convert_agent_to_kiro(source_path: Path, dest_path: Path) -> bool:
    """Convert agent to Kiro JSON format with full configuration."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()
        
        metadata = extract_agent_metadata(content, source_path.name)
        agent_json = generate_kiro_agent_json(agent_slug, metadata)
        
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


def convert_to_kiro(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for Kiro CLI format.
    
    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root
        verbose: Print progress messages
    
    Returns:
        Dict with conversion statistics
    """
    stats = {"agents": 0, "skills": 0, "steering": 0, "errors": []}
    
    agents_src = source_root / ".agent" / "agents"
    agents_dest = dest_root / ".kiro" / "agents"
    
    skills_src = source_root / ".agent" / "skills"
    skills_dest = dest_root / ".kiro" / "skills"
    
    workflows_src = source_root / ".agent" / "workflows"
    steering_dest = dest_root / ".kiro" / "steering"
    
    # Convert agents to JSON
    if agents_src.exists():
        if verbose:
            print("Converting agents to Kiro JSON format...")
        
        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / f"{agent_file.stem}.json"
            if convert_agent_to_kiro(agent_file, dest_file):
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
    
    # Convert workflows to steering
    if workflows_src.exists():
        if verbose:
            print("Converting workflows to Kiro steering...")
        
        for workflow_file in workflows_src.glob("*.md"):
            dest_file = steering_dest / workflow_file.name
            if convert_workflow_to_steering(workflow_file, dest_file):
                stats["steering"] += 1
                if verbose:
                    print(f"  ✓ {workflow_file.name}")
            else:
                stats["errors"].append(f"steering:{workflow_file.name}")
    
    if verbose:
        print(f"\nKiro conversion complete: {stats['agents']} agents, {stats['skills']} skills, {stats['steering']} steering files")
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")
    
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