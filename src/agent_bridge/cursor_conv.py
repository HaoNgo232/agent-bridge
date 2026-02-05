"""
Cursor AI Converter
Converts Antigravity Kit agents/skills to Cursor format.

Output structure:
- .cursor/agents/*.md (agent files)
- .cursor/rules/*.mdc (rules with MDC frontmatter)
- .cursor/skills/*.md (merged skill files)
- .cursor/mcp.json (MCP configuration)

Reference: https://cursor.com/docs/context/rules
MDC Format: description, globs, alwaysApply frontmatter
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import os
import re
import shutil
from .utils import Colors, ask_user, get_master_agent_dir, install_mcp_for_ide

import yaml

CREDIT_LINE = "\n\n---\nBuilt with ❤️ from [Antigravity Kit](https://github.com/vudovn/antigravity-kit) & UXUI ProMax MIT © Vudovn\n"


# =============================================================================
# MDC FRONTMATTER CONFIGURATION
# =============================================================================

# MDC RULES: Auto-activation based on file matching (Globs)
MDC_RULES_CONFIG = {
    "clean-code": {"alwaysApply": True, "globs": "", "description": "Core coding standards"},
    "behavioral-modes": {"alwaysApply": True, "globs": "", "description": "Agent behavioral guidelines"},
    "nextjs-react-expert": {
        "alwaysApply": False,
        "globs": "**/*.tsx,**/*.jsx,**/next.config.*,**/app/**/*,**/pages/**/*",
        "description": "Next.js and React expertise",
    },
    "tailwind-patterns": {
        "alwaysApply": False,
        "globs": "**/*.tsx,**/*.jsx,**/*.css,**/tailwind.config.*",
        "description": "Tailwind CSS styling patterns",
    },
    "typescript-patterns": {
        "alwaysApply": False,
        "globs": "**/*.ts,**/*.tsx,**/tsconfig.json",
        "description": "TypeScript language standards",
    },
    "python-patterns": {
        "alwaysApply": False,
        "globs": "**/*.py,**/pyproject.toml,**/requirements.txt",
        "description": "Python code style and patterns",
    },
    "database-design": {
        "alwaysApply": False,
        "globs": "**/*.sql,**/prisma/**/*,**/drizzle/**/*,**/migrations/**/*",
        "description": "Database schema and SQL patterns",
    },
    "testing-patterns": {
        "alwaysApply": False,
        "globs": "**/*.test.*,**/*.spec.*,**/__tests__/**/*,**/tests/**/*",
        "description": "Testing frameworks and patterns",
    },
    "mobile-design": {
        "alwaysApply": False,
        "globs": "**/App.tsx,**/app.json,**/*.native.*,**/android/**/*,**/ios/**/*",
        "description": "Mobile development for iOS/Android",
    },
}

# CURSOR SKILLS: On-demand toolkits invokable via slash commands (e.g., /plan)
# Map skill name to command/description
SKILLS_TOOLKIT_MAP = {
    "architecture": "discuss system architecture and design patterns",
    "brainstorming": "explore ideas and creative solutions",
    "plan-writing": "create implementation plans and roadmaps",
    "systematic-debugging": "debug issues and analyze errors",
    "code-review-checklist": "review code and ensure quality",
    "performance-profiling": "optimize performance and find bottlenecks",
    "security-scanner": "audit code for vulnerabilities",
    "seo-fundamentals": "optimize for search engines",
}

# CUSTOM SUBAGENTS: Specialized personas
AGENT_CONFIG_MAP = {
    "frontend-specialist": "Specialist for frontend development (React, Next.js, UI/UX)",
    "backend-specialist": "Specialist for backend systems (APIs, DBs, Server logic)",
    "orchestrator": "High-level coordinator for complex, multi-step tasks",
    "project-planner": "Specialist for architecture and technical planning",
    "debugger": "Specialist for root cause analysis and bug fixing",
}


# =============================================================================
# MDC FORMAT HELPERS
# =============================================================================

def generate_mdc_frontmatter(
    description: str = "",
    globs: str = "",
    always_apply: bool = False
) -> str:
    """
    Generate MDC frontmatter for Cursor rules.
    """
    lines = ["---"]
    lines.append(f"description: {description}")
    lines.append(f"globs: {globs}")
    lines.append(f"alwaysApply: {str(always_apply).lower()}")
    lines.append("---")
    return "\n".join(lines)


def extract_metadata_from_content(content: str) -> Dict[str, Any]:
    """Extract metadata from markdown content."""
    metadata = {"name": "", "description": ""}
    
    # Check existing frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if fm_match:
        try:
            existing = yaml.safe_load(fm_match.group(1))
            if existing:
                metadata.update(existing)
        except:
            pass
    
    # Extract from H1
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match and not metadata.get("name"):
        metadata["name"] = h1_match.group(1).strip()
    
    # Extract description from first paragraph after H1
    desc_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n#)', content, re.DOTALL)
    if desc_match and not metadata.get("description"):
        metadata["description"] = desc_match.group(1).strip()[:200]
    
    return metadata


# =============================================================================
# CONVERSION FUNCTIONS
# =============================================================================

def convert_agent_to_cursor(source_path: Path, dest_path: Path) -> bool:
    """Convert agent to Cursor Subagent markdown format."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()
        agent_name = agent_slug.replace("-", " ").title()
        
        # Cursor Subagents frontmatter
        description = AGENT_CONFIG_MAP.get(agent_slug, f"Specialized assistant for {agent_name} activities")
        
        lines = ["---"]
        lines.append(f"name: {agent_name}")
        lines.append(f"description: {description}")
        lines.append("---")
        
        # Remove existing frontmatter from content
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        
        output = "\n".join(lines) + f"\n\n{content_clean.strip()}{CREDIT_LINE}"
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_skill_to_cursor(source_dir: Path, rules_dest: Path, skills_dest: Path) -> bool:
    """Convert skill to either MDC Rule or Cursor Skill folder."""
    try:
        skill_name = source_dir.name
        skill_file = source_dir / "SKILL.md"
        if not skill_file.exists(): return False
        
        content = skill_file.read_text(encoding="utf-8")
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)

        # Merge additional .md files
        for md_file in sorted(source_dir.glob("*.md")):
            if md_file.name != "SKILL.md":
                additional = md_file.read_text(encoding="utf-8")
                additional_clean = re.sub(r'^---\n.*?\n---\n*', '', additional, flags=re.DOTALL)
                content_clean += f"\n\n---\n\n{additional_clean}"

        # OPTION A: Convert to MDC Rule (Auto-attach)
        if skill_name in MDC_RULES_CONFIG:
            config = MDC_RULES_CONFIG[skill_name]
            frontmatter = generate_mdc_frontmatter(
                description=config["description"],
                globs=config["globs"],
                always_apply=config["alwaysApply"]
            )
            rules_dest.mkdir(parents=True, exist_ok=True)
            dest_file = rules_dest / f"{skill_name}.mdc"
            dest_file.write_text(f"{frontmatter}\n\n{content_clean}{CREDIT_LINE}", encoding="utf-8")
            return True

        # OPTION B: Convert to Cursor Skill (On-demand/Slash command)
        skill_folder = skills_dest / skill_name
        skill_folder.mkdir(parents=True, exist_ok=True)
        
        description = SKILLS_TOOLKIT_MAP.get(skill_name, f"Expert toolkit for {skill_name}")
        
        skill_header = f"---\nname: {skill_name}\ndescription: {description}\n---\n\n"
        (skill_folder / "SKILL.md").write_text(f"{skill_header}{content_clean}{CREDIT_LINE}", encoding="utf-8")
        
        # Copy other files to skill folder as resources
        for item in source_dir.iterdir():
            if item.name != "SKILL.md":
                if item.is_file(): shutil.copy2(item, skill_folder / item.name)
                elif item.is_dir(): shutil.copytree(item, skill_folder / item.name, dirs_exist_ok=True)
                
        return True
    except Exception as e:
        print(f"  Error converting skill {source_dir.name}: {e}")
        return False


def convert_workflow_to_cursor_skill(source_path: Path, skills_dest: Path) -> bool:
    """Convert a workflow to a Cursor Skill (slash command)."""
    try:
        content = source_path.read_text(encoding="utf-8")
        name = source_path.stem
        
        # Extract metadata
        metadata = extract_metadata_from_content(content)
        description = metadata.get("description") or f"Execute workflow for {name}"
        
        skill_folder = skills_dest / name
        skill_folder.mkdir(parents=True, exist_ok=True)
        
        # Normalize content for Cursor Skill
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        
        header = f"---\nname: {name}\ndescription: {description}\n---\n\n"
        (skill_folder / "SKILL.md").write_text(f"{header}{content_clean}{CREDIT_LINE}", encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting workflow {source_path.name}: {e}")
        return False


def create_project_instructions(dest_root: Path, source_root: Path) -> bool:
    """Create .cursor/rules/project-instructions.mdc from AGENTS.md or similar."""
    try:
        rules_dir = dest_root / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Look for project instructions
        instruction_sources = [
            source_root / "AGENTS.md",
            source_root / ".agent" / "ARCHITECTURE.md",
            source_root / "CONTRIBUTING.md",
        ]
        
        content_parts = []
        for src in instruction_sources:
            if src.exists():
                content_parts.append(src.read_text(encoding="utf-8"))
        
        if content_parts:
            frontmatter = generate_mdc_frontmatter(
                description="Project-specific instructions and architecture guidelines",
                globs="",
                always_apply=True,  # Project instructions always apply
            )
            
            combined = "\n\n---\n\n".join(content_parts)
            output = f"{frontmatter}\n\n{combined}{CREDIT_LINE}"
            
            (rules_dir / "project-instructions.mdc").write_text(output, encoding="utf-8")
            return True
        
        return False
    except Exception as e:
        print(f"  Error creating project instructions: {e}")
        return False


def convert_to_cursor(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for Cursor v2.4+ format.
    """
    stats = {"agents": 0, "rules": 0, "skills": 0, "workflows": 0, "errors": []}
    
    # Define paths
    agents_src = source_root / ".agent" / "agents"
    skills_src = source_root / ".agent" / "skills"
    workflows_src = source_root / ".agent" / "workflows"
    
    rules_dest = dest_root / ".cursor" / "rules"
    agents_dest = dest_root / ".cursor" / "agents"
    skills_dest = dest_root / ".cursor" / "skills"
    
    # CLEANUP: Remove old generated folders to prevent ghost files
    for path in [rules_dest, agents_dest, skills_dest]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    
    # 1. Convert Agents (Personas)
    if agents_src.exists():
        if verbose: print("Converting Agents to Cursor Subagents...")
        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / agent_file.name
            if convert_agent_to_cursor(agent_file, dest_file):
                stats["agents"] += 1
            else: stats["errors"].append(f"agent:{agent_file.name}")
    
    # 2. Convert Skills (Auto-rules or Slash-commands)
    if skills_src.exists():
        if verbose: print("Converting Skills to Cursor Rules/Skills...")
        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                if convert_skill_to_cursor(skill_dir, rules_dest, skills_dest):
                    stats["skills"] += 1
                else: stats["errors"].append(f"skill:{skill_dir.name}")

    # 3. Convert Workflows (Slash-commands)
    if workflows_src.exists():
        if verbose: print("Converting Workflows to Cursor Commands...")
        for workflow_file in workflows_src.glob("*.md"):
            if convert_workflow_to_cursor_skill(workflow_file, skills_dest):
                stats["workflows"] += 1
            else: stats["errors"].append(f"workflow:{workflow_file.name}")
    
    # 4. Create Project Instructions (Always-on MDC)
    if create_project_instructions(dest_root, source_root):
        if verbose: print("  ✓ project-instructions.mdc created")
    
    if verbose:
        print(f"\nCursor v2.4 conversion complete!")
        print(f"  - Agents: {stats['agents']}")
        print(f"  - Rules (MDC): {len(list(rules_dest.glob('*.mdc'))) if rules_dest.exists() else 0}")
        print(f"  - Commands/Skills: {stats['skills'] + stats['workflows']}")
        if stats["errors"]:
            print(f"  Errors: {len(stats['errors'])}")
    
    return stats


# =============================================================================
# CLI ENTRY POINTS
# =============================================================================

def convert_cursor(source_dir: str, output_dir: str, force: bool = False):
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

    # Confirmation for Cursor Overwrite
    cursor_dir = Path(".cursor").resolve()
    if cursor_dir.exists() and not force:
        if not ask_user(f"Found existing '.cursor'. Update agents & rules?", default=True):
             print(f"{Colors.YELLOW}⏭️  Skipping Cursor update.{Colors.ENDC}")
             return

    print(f"{Colors.HEADER}🏗️  Converting to Cursor Format (Professional Spec)...{Colors.ENDC}")
    convert_to_cursor(source_root, Path("."), verbose=True)
    print(f"{Colors.GREEN}✅ Cursor conversion complete!{Colors.ENDC}")

def copy_mcp_cursor(root_path: Path, force: bool = False):
    """Bridge for CLI compatibility."""
    dest_file = root_path / ".cursor" / "mcp.json"
    if dest_file.exists() and not force:
        if not ask_user(f"Found existing '{dest_file}'. Overwrite MCP config?", default=False):
            print(f"{Colors.YELLOW}🔒 Kept existing Cursor MCP config.{Colors.ENDC}")
            return
    
    source_root = root_path if (root_path / ".agent").exists() else get_master_agent_dir().parent
    if install_mcp_for_ide(source_root, root_path, "cursor"):
        print(f"{Colors.BLUE}  🔌 Integrated MCP config into Cursor (.cursor/mcp.json).{Colors.ENDC}")

def init_cursor(project_path: Path = None) -> bool:
    # Existing user function...
    """Initialize Cursor configuration in project."""
    project_path = project_path or Path.cwd()
    
    if not (project_path / ".agent").exists():
        print("Error: .agent directory not found. Run 'agent-bridge update' first.")
        return False
    
    stats = convert_to_cursor(project_path, project_path)
    return len(stats["errors"]) == 0


def clean_cursor(project_path: Path = None) -> bool:
    """Remove Cursor configuration from project."""
    project_path = project_path or Path.cwd()
    
    paths_to_remove = [
        project_path / ".cursor" / "agents",
        project_path / ".cursor" / "rules",
        project_path / ".cursor" / "skills",
    ]
    
    for path in paths_to_remove:
        if path.exists():
            shutil.rmtree(path)
            print(f"  Removed {path}")
    
    return True