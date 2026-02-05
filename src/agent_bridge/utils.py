import yaml
import sys
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def ask_user(question: str, default: bool = True) -> bool:
    """
    Prompts the user with a yes/no question.
    """
    choices = " [Y/n]: " if default else " [y/N]: "
    while True:
        print(f"{Colors.YELLOW}❓ {question}{choices}{Colors.ENDC}", end='', flush=True)
        choice = input().lower()
        if not choice:
            return default
        if choice in ['y', 'yes']:
            return True
        if choice in ['n', 'no']:
            return False

def get_master_agent_dir() -> Path:
    """Returns the .agent directory inside the agent-bridge project."""
    return Path(__file__).resolve().parent.parent.parent / ".agent"


# =============================================================================
# MCP CONFIGURATION
# =============================================================================

def load_mcp_config(source_root: Path) -> Optional[Dict[str, Any]]:
    """Load MCP configuration from .agent/mcp_config.json."""
    mcp_file = source_root / ".agent" / "mcp_config.json"
    if mcp_file.exists():
        try:
            return json.loads(mcp_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def write_mcp_config(dest_path: Path, config: Dict[str, Any]) -> bool:
    """Write MCP configuration to destination."""
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except Exception as e:
        print(f"  Error writing MCP config: {e}")
        return False


def install_mcp_for_ide(source_root: Path, dest_root: Path, ide: str) -> bool:
    """
    Install MCP configuration for specific IDE.
    
    IDE destinations:
    - copilot: .vscode/mcp.json
    - cursor: .cursor/mcp.json
    - windsurf: .windsurf/mcp_config.json
    - opencode: .opencode/mcp.json
    - kiro: .kiro/settings/mcp.json
    """
    mcp_config = load_mcp_config(source_root)
    if not mcp_config:
        print("  No MCP configuration found in .agent/mcp_config.json")
        return False
    
    dest_paths = {
        "copilot": dest_root / ".vscode" / "mcp.json",
        "cursor": dest_root / ".cursor" / "mcp.json",
        "windsurf": dest_root / ".windsurf" / "mcp_config.json",
        "opencode": dest_root / ".opencode" / "mcp.json",
        "kiro": dest_root / ".kiro" / "settings" / "mcp.json",
    }
    
    dest_path = dest_paths.get(ide.lower())
    if not dest_path:
        print(f"  Unknown IDE: {ide}")
        return False
    
    return write_mcp_config(dest_path, mcp_config)


# =============================================================================
# INTERACTIVE PROMPTS
# =============================================================================

def confirm_overwrite(path: Path, default: bool = False) -> bool:
    """Ask user to confirm overwriting existing file."""
    if not path.exists():
        return True
    
    default_str = "Y/n" if default else "y/N"
    try:
        response = input(f"  File {path} exists. Overwrite? [{default_str}]: ").strip().lower()
        if not response:
            return default
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def print_header(text: str) -> None:
    """Print formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"  ✓ {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"  ✗ {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"  ℹ {text}")


# =============================================================================
# FILE UTILITIES
# =============================================================================

def safe_copy(src: Path, dest: Path, overwrite: bool = True) -> bool:
    """Safely copy file or directory."""
    try:
        if dest.exists() and not overwrite:
            return False
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        
        return True
    except Exception as e:
        print(f"  Error copying {src} to {dest}: {e}")
        return False


def safe_remove(path: Path) -> bool:
    """Safely remove file or directory."""
    try:
        if not path.exists():
            return True
        
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        
        return True
    except Exception as e:
        print(f"  Error removing {path}: {e}")
        return False


def ensure_dir(path: Path) -> bool:
    """Ensure directory exists."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"  Error creating directory {path}: {e}")
        return False


# =============================================================================
# CONTENT UTILITIES
# =============================================================================

def extract_yaml_frontmatter(content: str) -> tuple[Optional[Dict], str]:
    """Extract YAML frontmatter from markdown content."""
    import re
    
    match = re.match(r'^---\n(.*?)\n---\n*', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = content[match.end():]
            return frontmatter, body
        except yaml.YAMLError:
            pass
    
    return None, content


def add_yaml_frontmatter(content: str, frontmatter: Dict) -> str:
    """Add or replace YAML frontmatter in markdown content."""
    import re
    
    # Remove existing frontmatter
    content_clean = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
    
    # Generate new frontmatter
    fm_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    return f"---\n{fm_str}---\n\n{content_clean.strip()}\n"


def truncate_content(content: str, max_length: int, suffix: str = "\n\n... (truncated)\n") -> str:
    """Truncate content to max length with suffix."""
    if len(content) <= max_length:
        return content
    
    return content[:max_length - len(suffix)] + suffix