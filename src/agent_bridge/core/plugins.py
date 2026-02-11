"""
External Skill Plugin System.

Reads plugin declarations from .agent/plugins.json and installs them
for each target IDE. Replaces hardcoded external skill logic.

Design goals:
- Declarative: plugins defined in JSON, not in Python code
- Per-IDE commands: each IDE can have its own install command
- Conditional: only install if trigger condition is met
- Safe: asks user before installing global packages
- Extensible: add new plugins by editing plugins.json, zero code changes

Usage in converters:
    from agent_bridge.core.plugins import PluginRunner
    runner = PluginRunner(source_root)
    runner.run_for_ide("kiro", project_root, verbose=True)
"""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import Colors


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class PluginInstallConfig:
    """How to install a plugin's prerequisite CLI tool."""
    requires: str = ""           # "npm" | "pip" | "cargo" | "" (none)
    package: str = ""            # Package name to install (e.g. "uipro-cli")
    global_install: bool = True  # Install globally or locally
    commands: Dict[str, str] = field(default_factory=dict)  # ide_name -> shell command


@dataclass
class PluginCondition:
    """When to trigger plugin installation."""
    file_exists: str = ""        # Path relative to source_root
    always: bool = False         # Always install


@dataclass
class Plugin:
    """One external skill plugin declaration."""
    name: str
    description: str = ""
    homepage: str = ""
    install: PluginInstallConfig = field(default_factory=PluginInstallConfig)
    condition: PluginCondition = field(default_factory=PluginCondition)
    prompt_before_install: bool = True  # Ask user before installing

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Plugin":
        """Parse plugin from JSON dict."""
        install_data = data.get("install", {})
        condition_data = data.get("condition", {})

        install_config = PluginInstallConfig(
            requires=install_data.get("requires", ""),
            package=install_data.get("package", ""),
            global_install=install_data.get("global", True),
            commands=install_data.get("commands", {}),
        )

        condition = PluginCondition(
            file_exists=condition_data.get("file_exists", ""),
            always=condition_data.get("always", False),
        )

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            homepage=data.get("homepage", ""),
            install=install_config,
            condition=condition,
            prompt_before_install=data.get("prompt_before_install", True),
        )


# =============================================================================
# PLUGIN LOADER
# =============================================================================


def load_plugins(source_root: Path) -> List[Plugin]:
    """
    Load plugin declarations from .agent/plugins.json.

    Args:
        source_root: Project root or vault root containing .agent/

    Returns:
        List of Plugin objects. Empty list if no plugins.json found.
    """
    plugins_file = source_root / ".agent" / "plugins.json"
    if not plugins_file.exists():
        return []

    try:
        data = json.loads(plugins_file.read_text(encoding="utf-8"))
        plugins_list = data.get("plugins", [])
        return [Plugin.from_dict(p) for p in plugins_list if p.get("name")]
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        print(f"  {Colors.YELLOW}Warning: Could not parse plugins.json: {e}{Colors.ENDC}")
        return []


# =============================================================================
# CONDITION CHECKER
# =============================================================================


def check_condition(plugin: Plugin, source_root: Path) -> bool:
    """Check if plugin's install condition is met."""
    cond = plugin.condition

    if cond.always:
        return True

    if cond.file_exists:
        target_path = source_root / cond.file_exists
        return target_path.exists()

    # No condition specified = always install
    return True


# =============================================================================
# PREREQUISITE INSTALLER
# =============================================================================


# Map of package manager -> install command template
_INSTALL_TEMPLATES = {
    "npm": {
        "global": ["npm", "install", "-g", "{package}"],
        "local": ["npm", "install", "--save-dev", "{package}"],
        "check": ["{package}", "--version"],
    },
    "pip": {
        "global": ["pip", "install", "{package}"],
        "local": ["pip", "install", "{package}"],
        "check": ["{package}", "--version"],
    },
    "cargo": {
        "global": ["cargo", "install", "{package}"],
        "local": ["cargo", "install", "{package}"],
        "check": ["{package}", "--version"],
    },
}


def _check_tool_available(tool_name: str) -> bool:
    """Check if a CLI tool is available on PATH."""
    return shutil.which(tool_name) is not None


def _check_package_manager_available(pm: str) -> bool:
    """Check if the required package manager is available."""
    return shutil.which(pm) is not None


def _install_prerequisite(plugin: Plugin, verbose: bool = True) -> bool:
    """
    Install plugin's prerequisite CLI tool if not already available.

    Returns True if tool is available (already installed or just installed).
    Returns False if installation failed.
    """
    install = plugin.install

    if not install.requires or not install.package:
        return True  # No prerequisite needed

    # Check if tool already installed
    # The tool name is typically the package name or derived from it
    tool_name = install.package.replace("-cli", "").replace("_cli", "")
    # Also check the package name itself
    for candidate in [tool_name, install.package]:
        if _check_tool_available(candidate):
            if verbose:
                print(f"    {Colors.GREEN}✓ {candidate} already installed{Colors.ENDC}")
            return True

    # Check package manager
    if not _check_package_manager_available(install.requires):
        if verbose:
            print(f"    {Colors.RED}✗ {install.requires} not found. "
                  f"Install {install.requires} first.{Colors.ENDC}")
        return False

    # Build install command
    templates = _INSTALL_TEMPLATES.get(install.requires)
    if not templates:
        if verbose:
            print(f"    {Colors.RED}✗ Unknown package manager: {install.requires}{Colors.ENDC}")
        return False

    scope = "global" if install.global_install else "local"
    cmd = [arg.replace("{package}", install.package) for arg in templates[scope]]

    if verbose:
        print(f"    {Colors.CYAN}Installing {install.package} ({scope})...{Colors.ENDC}")
        print(f"    $ {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            if verbose:
                print(f"    {Colors.GREEN}✓ {install.package} installed{Colors.ENDC}")
            return True
        else:
            if verbose:
                print(f"    {Colors.RED}✗ Install failed: {result.stderr.strip()}{Colors.ENDC}")
                print(f"    {Colors.YELLOW}Try manually: {' '.join(cmd)}{Colors.ENDC}")
            return False
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"    {Colors.RED}✗ Install timed out (120s){Colors.ENDC}")
        return False
    except FileNotFoundError:
        if verbose:
            print(f"    {Colors.RED}✗ {cmd[0]} not found{Colors.ENDC}")
        return False


# =============================================================================
# PLUGIN RUNNER
# =============================================================================


class PluginRunner:
    """
    Runs external skill plugins for a specific IDE.

    Usage:
        runner = PluginRunner(source_root)
        results = runner.run_for_ide("kiro", project_root)
    """

    def __init__(self, source_root: Path):
        """
        Args:
            source_root: Path containing .agent/ with plugins.json
        """
        self.source_root = source_root
        self.plugins = load_plugins(source_root)

    def run_for_ide(
        self,
        ide_name: str,
        project_root: Path,
        verbose: bool = True,
        force: bool = False,
    ) -> Dict[str, str]:
        """
        Run all applicable plugins for the given IDE.

        Args:
            ide_name: Target IDE (e.g. "kiro", "cursor", "copilot")
            project_root: Project directory to run commands in
            verbose: Print progress
            force: Skip user confirmation prompts

        Returns:
            Dict of plugin_name -> "ok" | "skipped" | "error: ..."
        """
        results: Dict[str, str] = {}

        if not self.plugins:
            return results

        applicable = [
            p for p in self.plugins
            if ide_name in p.install.commands and check_condition(p, self.source_root)
        ]

        if not applicable:
            return results

        if verbose:
            print(f"\n  {Colors.CYAN}External skill plugins ({len(applicable)} found):{Colors.ENDC}")

        for plugin in applicable:
            result = self._run_single(plugin, ide_name, project_root, verbose, force)
            results[plugin.name] = result

        return results

    def _run_single(
        self,
        plugin: Plugin,
        ide_name: str,
        project_root: Path,
        verbose: bool,
        force: bool,
    ) -> str:
        """Run a single plugin. Returns status string."""
        if verbose:
            print(f"\n    {Colors.BOLD}Plugin: {plugin.name}{Colors.ENDC}")
            if plugin.description:
                print(f"    {plugin.description}")

        # Ask user permission (unless --force)
        if plugin.prompt_before_install and not force:
            if not _ask_install_permission(plugin):
                if verbose:
                    print(f"    {Colors.YELLOW}Skipped by user{Colors.ENDC}")
                return "skipped"

        # Install prerequisite
        if not _install_prerequisite(plugin, verbose):
            return "error: prerequisite install failed"

        # Run IDE-specific command
        command_str = plugin.install.commands.get(ide_name)
        if not command_str:
            return "skipped"

        if verbose:
            print(f"    {Colors.CYAN}Running: {command_str}{Colors.ENDC}")

        try:
            result = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=180,
            )

            if result.returncode == 0:
                if verbose:
                    print(f"    {Colors.GREEN}✓ {plugin.name} installed for {ide_name}{Colors.ENDC}")
                return "ok"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                if verbose:
                    print(f"    {Colors.RED}✗ Failed: {error_msg[:200]}{Colors.ENDC}")
                return f"error: {error_msg[:200]}"

        except subprocess.TimeoutExpired:
            if verbose:
                print(f"    {Colors.RED}✗ Command timed out (180s){Colors.ENDC}")
            return "error: timeout"
        except Exception as e:
            if verbose:
                print(f"    {Colors.RED}✗ Error: {e}{Colors.ENDC}")
            return f"error: {e}"

    def list_plugins(self, ide_name: str = None) -> List[Dict[str, Any]]:
        """List plugins, optionally filtered by IDE support."""
        result = []
        for p in self.plugins:
            info = {
                "name": p.name,
                "description": p.description,
                "homepage": p.homepage,
                "supported_ides": list(p.install.commands.keys()),
                "requires": p.install.requires,
                "package": p.install.package,
            }
            if ide_name is None or ide_name in p.install.commands:
                result.append(info)
        return result


# =============================================================================
# USER PROMPT
# =============================================================================


def _ask_install_permission(plugin: Plugin) -> bool:
    """Ask user for permission to install a plugin."""
    install = plugin.install

    print()
    print(f"    {Colors.YELLOW}Plugin '{plugin.name}' wants to install:{Colors.ENDC}")

    if install.package:
        scope = "globally" if install.global_install else "locally"
        print(f"      Package: {install.package} (via {install.requires}, {scope})")

    if plugin.homepage:
        print(f"      Info: {plugin.homepage}")

    # Try questionary first, fall back to simple input
    try:
        import questionary
        answer = questionary.confirm(
            "    Proceed with installation?",
            default=True,
        ).ask()
        return answer if answer is not None else False
    except ImportError:
        pass

    # Fallback: simple y/n
    try:
        choice = input(f"    {Colors.YELLOW}Install? [Y/n]: {Colors.ENDC}").strip().lower()
        return choice in ("", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False