"""
Business logic cho lenh 'agent-bridge update'.

Xu ly: 1) Sync tat ca vault
       2) Merge vao project .agent/
       3) Tu dong refresh IDE config da phat hien
"""

import shutil
from pathlib import Path

from agent_bridge.core.converter import converter_registry
from agent_bridge.utils import Colors, get_master_agent_dir
from agent_bridge.vault import VaultManager
from agent_bridge.vault.merger import MergeStrategy, merge_source_into_project


def run_update(target_dir: Path, verbose: bool = True) -> None:
    """
    Logic chinh cua update.

    Args:
        target_dir: Thu muc muc tieu (vd: .agent)
        verbose: In tien trinh
    """
    vm = VaultManager()

    if verbose:
        print(f"{Colors.HEADER}Updating knowledge vaults to: {target_dir}{Colors.ENDC}")

    # Buoc 1: Sync vault
    if verbose:
        print(f"{Colors.BLUE}  Syncing vault sources...{Colors.ENDC}")
    sync_results = vm.sync(verbose=verbose)

    has_success = any(s.get("status") == "ok" for s in sync_results.values())
    if not has_success:
        if verbose:
            print(f"{Colors.RED}All vault syncs failed.{Colors.ENDC}")
            for name, stats in sync_results.items():
                print(f"  {name}: {stats.get('status', 'unknown')}")
        return

    # Buoc 2: Merge vao project
    target_path = Path(target_dir).resolve()
    if not target_path.exists() and not (Path.cwd() / ".git").exists():
        # Khong co project, cap nhat master cache
        master_path = get_master_agent_dir()
        target_path = master_path if master_path.exists() else Path.cwd() / ".agent"

    target_path.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"{Colors.BLUE}  Merging vaults into {target_path}...{Colors.ENDC}")

    vm.merge_to_project(target_path, verbose=verbose)

    # Buoc 3: Copy config files
    for vault in vm.enabled_vaults:
        source_root = vm.get_vault_agent_dir(vault)
        if not source_root:
            continue
        for config_file in ["mcp_config.json"]:
            src_conf = source_root / config_file
            dst_conf = target_path / config_file
            if src_conf.exists() and not dst_conf.exists():
                shutil.copy2(src_conf, dst_conf)
                if verbose:
                    print(f"{Colors.GREEN}    Init {config_file} from {vault.name}.{Colors.ENDC}")
            elif src_conf.exists() and verbose:
                print(f"{Colors.YELLOW}    Kept local {config_file}.{Colors.ENDC}")
        break

    if verbose:
        print(f"{Colors.GREEN}Knowledge vaults are now up to date!{Colors.ENDC}")

    # Buoc 4: Tu dong refresh IDE config
    _refresh_detected_ides(Path.cwd(), verbose)


def _refresh_detected_ides(project: Path, verbose: bool) -> None:
    """Refresh IDE config da phat hien trong project."""
    for converter in converter_registry.all():
        output_dir = project / converter.format_info.output_dir
        if output_dir.exists():
            if verbose:
                print(f"  Auto-refreshing {converter.display_name}...")
            converter.convert(project, project, verbose=verbose, force=True)
