"""
Kit Sync Module — thin wrapper over VaultManager for the `update` command.
"""

import shutil
from pathlib import Path

from .utils import Colors, get_master_agent_dir


def check_and_refresh_project(source_dir: str):
    """Detects existing IDE formats and refreshes them."""
    from .copilot_conv import convert_copilot
    from .cursor_conv import convert_cursor
    from .kiro_conv import convert_kiro
    from .opencode_conv import convert_opencode
    from .windsurf_conv import convert_windsurf

    cwd = Path.cwd()

    if (cwd / ".github" / "agents").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing Copilot...{Colors.ENDC}")
        convert_copilot(source_dir, "")

    if (cwd / ".kiro" / "agents").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing Kiro...{Colors.ENDC}")
        convert_kiro(source_dir, ".kiro")

    if (cwd / ".opencode" / "agents").exists() or (cwd / "AGENTS.md").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing OpenCode...{Colors.ENDC}")
        convert_opencode(source_dir, "")

    if (cwd / ".cursor" / "rules").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing Cursor...{Colors.ENDC}")
        convert_cursor(source_dir, "")

    if (cwd / ".windsurf" / "rules").exists():
        print(f"{Colors.YELLOW}🔄 Auto-refreshing Windsurf...{Colors.ENDC}")
        convert_windsurf(source_dir, "")


def update_kit(target_dir: str):
    """Sync latest knowledge from all registered vaults."""
    target_path = Path(target_dir).resolve()
    master_path = get_master_agent_dir()

    if not Path(target_dir).exists() and not Path(".git").exists():
        print(f"{Colors.YELLOW}🔔 Local .agent not found, updating Master Copy...{Colors.ENDC}")
        target_path = master_path

    print(f"{Colors.HEADER}🔄 Updating knowledge vaults to: {target_path}{Colors.ENDC}")

    from .vault import VaultManager

    vm = VaultManager()

    # Sync all vaults
    print(f"{Colors.BLUE}  📥 Syncing vault sources...{Colors.ENDC}")
    sync_results = vm.sync()

    has_success = any(s["status"] == "ok" for s in sync_results.values())
    if not has_success:
        print(f"{Colors.RED}❌ All vault syncs failed.{Colors.ENDC}")
        for name, stats in sync_results.items():
            print(f"  {name}: {stats['status']}")
        return

    # Merge into project .agent/
    print(f"{Colors.BLUE}  📂 Merging vaults into {target_path}...{Colors.ENDC}")
    target_path.mkdir(parents=True, exist_ok=True)
    vm.merge_to_project(target_path)

    # Sync config files from primary vault
    for vault in vm.enabled_vaults:
        source_root = vm.get_vault_agent_dir(vault)
        if not source_root:
            continue
        for config_file in ["mcp_config.json"]:
            src_conf = source_root / config_file
            dst_conf = target_path / config_file
            if src_conf.exists() and not dst_conf.exists():
                shutil.copy2(src_conf, dst_conf)
                print(f"{Colors.GREEN}    ✅ Init {config_file} from {vault.name}.{Colors.ENDC}")
            elif src_conf.exists():
                print(f"{Colors.YELLOW}    🔒 Kept local {config_file}.{Colors.ENDC}")
        break  # Only first available vault for configs

    print(f"{Colors.GREEN}✨ Knowledge vaults are now up to date!{Colors.ENDC}")
    check_and_refresh_project(str(target_path))