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


# =============================================================================
# MDC FRONTMATTER CONFIGURATION
# =============================================================================

# Rule activation modes mapping
# 1. alwaysApply=true, globs=empty -> Always injected
# 2. alwaysApply=false, globs=pattern -> Auto-attach on file match
# 3. alwaysApply=false, globs=empty, description=text -> Agent-requested
# 4. alwaysApply=false, globs=empty, description=empty -> Manual @mention only

SKILL_ACTIVATION_MAP = {
    # Always active skills (core rules)
    "clean-code": {"alwaysApply": True, "globs": "", "description": ""},
    "behavioral-modes": {"alwaysApply": True, "globs": "", "description": ""},
    
    # Glob-based auto-attach
    "nextjs-react-expert": {
        "alwaysApply": False,
        "globs": "**/*.tsx,**/*.jsx,**/next.config.*,**/app/**/*,**/pages/**/*",
        "description": "",
    },
    "tailwind-patterns": {
        "alwaysApply": False,
        "globs": "**/*.tsx,**/*.jsx,**/*.css,**/tailwind.config.*",
        "description": "",
    },
    "typescript-patterns": {
        "alwaysApply": False,
        "globs": "**/*.ts,**/*.tsx,**/tsconfig.json",
        "description": "",
    },
    "python-patterns": {
        "alwaysApply": False,
        "globs": "**/*.py,**/pyproject.toml,**/requirements.txt",
        "description": "",
    },
    "rust-pro": {
        "alwaysApply": False,
        "globs": "**/*.rs,**/Cargo.toml",
        "description": "",
    },
    "database-design": {
        "alwaysApply": False,
        "globs": "**/*.sql,**/prisma/**/*,**/drizzle/**/*,**/migrations/**/*",
        "description": "",
    },
    "api-patterns": {
        "alwaysApply": False,
        "globs": "**/api/**/*,**/routes/**/*,**/*.controller.*,**/*.service.*",
        "description": "",
    },
    "testing-patterns": {
        "alwaysApply": False,
        "globs": "**/*.test.*,**/*.spec.*,**/__tests__/**/*,**/tests/**/*",
        "description": "",
    },
    "mobile-design": {
        "alwaysApply": False,
        "globs": "**/App.tsx,**/app.json,**/*.native.*,**/android/**/*,**/ios/**/*",
        "description": "",
    },
    "game-development": {
        "alwaysApply": False,
        "globs": "**/*.unity,**/*.cs,**/*.gd,**/godot/**/*",
        "description": "",
    },
    
    # Agent-requested (AI decides based on description)
    "architecture": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN discussing system architecture, design patterns, or making structural decisions",
    },
    "brainstorming": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN brainstorming ideas, exploring options, or creative problem solving",
    },
    "plan-writing": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN creating implementation plans, project roadmaps, or task breakdowns",
    },
    "systematic-debugging": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN debugging issues, analyzing errors, or troubleshooting problems",
    },
    "code-review-checklist": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN reviewing code, checking for issues, or ensuring quality",
    },
    "performance-profiling": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN optimizing performance, analyzing bottlenecks, or profiling code",
    },
    "security-scanner": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN checking security, auditing code, or reviewing vulnerabilities",
    },
    "seo-fundamentals": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN optimizing for SEO, improving search rankings, or meta tags",
    },
    "deployment-procedures": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN deploying applications, setting up CI/CD, or managing releases",
    },
    "documentation-templates": {
        "alwaysApply": False,
        "globs": "",
        "description": "USE WHEN writing documentation, README files, or technical guides",
    },
}

# Agent to tools/permissions mapping for Cursor
AGENT_CONFIG_MAP = {
    "frontend-specialist": {
        "description": "Frontend development specialist for React, Vue, and web technologies",
        "alwaysApply": False,
        "globs": "",
    },
    "backend-specialist": {
        "description": "Backend development specialist for APIs, databases, and server-side logic",
        "alwaysApply": False,
        "globs": "",
    },
    "orchestrator": {
        "description": "USE WHEN coordinating multiple tasks or managing complex workflows",
        "alwaysApply": False,
        "globs": "",
    },
    "project-planner": {
        "description": "USE WHEN planning projects, creating roadmaps, or breaking down tasks",
        "alwaysApply": False,
        "globs": "",
    },
    "debugger": {
        "description": "USE WHEN debugging issues, analyzing stack traces, or fixing bugs",
        "alwaysApply": False,
        "globs": "",
    },
    "security-auditor": {
        "description": "USE WHEN auditing security, reviewing vulnerabilities, or checking compliance",
        "alwaysApply": False,
        "globs": "",
    },
    "test-engineer": {
        "description": "USE WHEN writing tests, improving coverage, or setting up testing frameworks",
        "alwaysApply": False,
        "globs": "",
    },
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
    
    MDC format (NOT YAML):
    ---
    description: text
    globs: pattern1,pattern2
    alwaysApply: true
    ---
    """
    lines = ["---"]
    
    # Description - for AI to decide relevance
    lines.append(f"description: {description}")
    
    # Globs - file patterns for auto-attach
    lines.append(f"globs: {globs}")
    
    # AlwaysApply - always inject into context
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
    """Convert agent to Cursor format with MDC frontmatter."""
    try:
        content = source_path.read_text(encoding="utf-8")
        agent_slug = source_path.stem.lower()
        
        # Get activation config
        config = AGENT_CONFIG_MAP.get(agent_slug, {
            "description": f"Specialized agent for {agent_slug.replace('-', ' ')} tasks",
            "alwaysApply": False,
            "globs": "",
        })
        
        # Generate MDC frontmatter
        frontmatter = generate_mdc_frontmatter(
            description=config.get("description", ""),
            globs=config.get("globs", ""),
            always_apply=config.get("alwaysApply", False),
        )
        
        # Remove existing frontmatter
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        
        # Build output
        output = f"{frontmatter}\n\n{content_clean.strip()}\n"
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting agent {source_path.name}: {e}")
        return False


def convert_skill_to_cursor_rule(source_dir: Path, dest_path: Path) -> bool:
    """Convert skill directory to Cursor rule (.mdc file)."""
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
        config = SKILL_ACTIVATION_MAP.get(skill_name, {
            "description": f"Rules for {skill_name.replace('-', ' ')}",
            "alwaysApply": False,
            "globs": "",
        })
        
        # Generate MDC frontmatter
        frontmatter = generate_mdc_frontmatter(
            description=config.get("description", ""),
            globs=config.get("globs", ""),
            always_apply=config.get("alwaysApply", False),
        )
        
        # Remove existing frontmatter and merge additional .md files
        content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        
        # Append other .md files in the skill directory
        for md_file in sorted(source_dir.glob("*.md")):
            if md_file.name != "SKILL.md":
                additional = md_file.read_text(encoding="utf-8")
                additional_clean = re.sub(r'^---\n.*?\n---\n*', '', additional, flags=re.DOTALL)
                content_clean += f"\n\n---\n\n{additional_clean}"
        
        # Build output
        output = f"{frontmatter}\n\n{content_clean.strip()}\n"
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(output, encoding="utf-8")
        return True
    except Exception as e:
        print(f"  Error converting skill {source_dir.name}: {e}")
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
                description="",
                globs="",
                always_apply=True,  # Project instructions always apply
            )
            
            combined = "\n\n---\n\n".join(content_parts)
            output = f"{frontmatter}\n\n{combined}\n"
            
            (rules_dir / "project-instructions.mdc").write_text(output, encoding="utf-8")
            return True
        
        return False
    except Exception as e:
        print(f"  Error creating project instructions: {e}")
        return False


def convert_to_cursor(source_root: Path, dest_root: Path, verbose: bool = True) -> Dict[str, Any]:
    """
    Main conversion function for Cursor format.
    
    Args:
        source_root: Path to project root containing .agent/
        dest_root: Path to output root
        verbose: Print progress messages
    
    Returns:
        Dict with conversion statistics
    """
    stats = {"agents": 0, "rules": 0, "errors": []}
    
    agents_src = source_root / ".agent" / "agents"
    agents_dest = dest_root / ".cursor" / "agents"
    
    skills_src = source_root / ".agent" / "skills"
    rules_dest = dest_root / ".cursor" / "rules"
    
    # Convert agents
    if agents_src.exists():
        if verbose:
            print("Converting agents to Cursor format...")
        
        for agent_file in agents_src.glob("*.md"):
            dest_file = agents_dest / agent_file.name
            if convert_agent_to_cursor(agent_file, dest_file):
                stats["agents"] += 1
                if verbose:
                    print(f"  ✓ {agent_file.name}")
            else:
                stats["errors"].append(f"agent:{agent_file.name}")
    
    # Convert skills to rules (.mdc)
    if skills_src.exists():
        if verbose:
            print("Converting skills to Cursor rules (.mdc)...")
        
        for skill_dir in skills_src.iterdir():
            if skill_dir.is_dir():
                dest_file = rules_dest / f"{skill_dir.name}.mdc"
                if convert_skill_to_cursor_rule(skill_dir, dest_file):
                    stats["rules"] += 1
                    if verbose:
                        print(f"  ✓ {skill_dir.name}.mdc")
                else:
                    stats["errors"].append(f"rule:{skill_dir.name}")
    
    # Create project instructions
    if create_project_instructions(dest_root, source_root):
        if verbose:
            print("  ✓ project-instructions.mdc")
    
    if verbose:
        print(f"\nCursor conversion complete: {stats['agents']} agents, {stats['rules']} rules")
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