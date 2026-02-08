import yaml
import sys
import json
import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure module logger
logger = logging.getLogger("agent_bridge")

# ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def ask_user(question: str, default: bool = True) -> bool:
    """
    Prompts the user with a yes/no question.
    """
    choices = " [Y/n]: " if default else " [y/N]: "
    while True:
        print(f"{Colors.YELLOW}❓ {question}{choices}{Colors.ENDC}", end='', flush=True)
        choice = input().strip().lower()
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

def validate_path_within_project(path: Path, project_root: Path = None) -> bool:
    """
    Validate that a path stays within the project root.
    Prevents path traversal attacks (e.g., ../../etc/passwd).
    """
    project_root = project_root or Path.cwd()
    try:
        resolved = path.resolve()
        project_resolved = project_root.resolve()
        return str(resolved).startswith(str(project_resolved))
    except (OSError, ValueError):
        return False

def safe_read_text(path: Path, encoding: str = "utf-8") -> Optional[str]:
    """
    Safely read text file with encoding fallback.
    Returns None if file cannot be read.
    """
    for enc in [encoding, "utf-8-sig", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except (OSError, IOError) as e:
            print(f"  Error reading {path}: {e}")
            return None
    print(f"  Error: Could not decode {path} with any known encoding")
    return None


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
# COMMON CONVERTER HELPERS
# =============================================================================

_RE_FRONTMATTER_STRIP = re.compile(r'^---\n.*?\n---\n*', re.DOTALL)
_RE_H1 = re.compile(r'^#\s+(.+)$', re.MULTILINE)


def strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content."""
    return _RE_FRONTMATTER_STRIP.sub('', content)


def resolve_source_root(source_dir: str) -> Optional[Path]:
    """
    Resolve source root containing .agent/ directory.
    Returns None if no source found.
    """
    root_path = Path(source_dir).resolve()
    
    if root_path.name == ".agent":
        return root_path.parent
    elif (root_path / ".agent").exists():
        return root_path
    else:
        master_path = get_master_agent_dir()
        if master_path.exists():
            print(f"{Colors.YELLOW}🔔 Local .agent not found, using Master Vault: {master_path}{Colors.ENDC}")
            return master_path.parent
    
    print(f"{Colors.RED}❌ Error: No agent knowledge source found.{Colors.ENDC}")
    return None


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