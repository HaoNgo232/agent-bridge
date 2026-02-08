"""
Kit Sync Module

Syncs knowledge from vault sources to local .agent/ directory.
Uses VaultManager for multi-source support.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from .utils import Colors, get_master_agent_dir

# Legacy constant kept for backward compatibility
KIT_REPO_URL = "https://github.com/vudovn/antigravity-kit"


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
    """
    Sync latest knowledge from all registered vaults.

    Steps:
    1. Sync all enabled vaults (git pull / clone)
    2. Merge into target .agent/ directory (project-local or master)
    3. Auto-refresh any detected IDE formats
    """
    target_path = Path(target_dir).resolve()
    master_path = get_master_agent_dir()

    if not Path(target_dir).exists() and not Path(".git").exists():
        print(f"{Colors.YELLOW}🔔 Local .agent not found, updating Master Copy instead...{Colors.ENDC}")
        target_path = master_path

    print(f"{Colors.HEADER}🔄 Updating knowledge vaults to: {target_path}{Colors.ENDC}")

    try:
        from .vault import VaultManager

        vm = VaultManager()

        # Step 1: Sync all vaults
        print(f"{Colors.BLUE}  📥 Syncing vault sources...{Colors.ENDC}")
        sync_results = vm.sync()

        has_success = any(s["status"] == "ok" for s in sync_results.values())
        if not has_success:
            print(f"{Colors.RED}❌ All vault syncs failed. Falling back to legacy method.{Colors.ENDC}")
            _legacy_update(target_path)
            return

        # Step 2: Merge into project .agent/
        print(f"{Colors.BLUE}  📂 Merging vaults into {target_path}...{Colors.ENDC}")
        target_path.mkdir(parents=True, exist_ok=True)
        vm.merge_to_project(target_path)

        # Step 3: Sync config files from primary vault
        _sync_config_files(vm, target_path)

        print(f"{Colors.GREEN}✨ Knowledge vaults are now up to date!{Colors.ENDC}")

        # Step 4: Auto-refresh IDE formats
        check_and_refresh_project(str(target_path))

    except ImportError:
        # Fallback if vault module not available
        print(f"{Colors.YELLOW}⚠️  VaultManager not available, using legacy sync...{Colors.ENDC}")
        _legacy_update(target_path)


def _sync_config_files(vm, target_path: Path):
    """Sync config files (mcp_config.json etc.) from primary vault."""
    for vault in vm.enabled_vaults:
        if vault.is_local:
            source_root = Path(vault.url).resolve() / vault.agent_subdir
        else:
            source_root = vault.cache_path / vault.agent_subdir

        if not source_root.exists():
            continue

        for config_file in ["mcp_config.json"]:
            src_conf = source_root / config_file
            dst_conf = target_path / config_file

            if src_conf.exists() and not dst_conf.exists():
                shutil.copy2(src_conf, dst_conf)
                print(f"{Colors.GREEN}    ✅ Init {config_file} from {vault.name}.{Colors.ENDC}")
            elif src_conf.exists():
                print(f"{Colors.YELLOW}    🔒 Kept local {config_file} (User Override).{Colors.ENDC}")

        # Only use first available vault for configs
        break


def _legacy_update(target_path: Path):
    """Legacy update method using direct git clone (backward compatibility)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        try:
            print(f"{Colors.BLUE}  📥 Cloning repository...{Colors.ENDC}")
            subprocess.run(
                ["git", "clone", "--depth", "1", KIT_REPO_URL, str(tmp_path)],
                check=True,
                capture_output=True,
            )

            repo_agent_dir = tmp_path / ".agent"
            if not repo_agent_dir.exists():
                repo_agent_dir = tmp_path

            print(f"{Colors.BLUE}  📂 Syncing agents and skills...{Colors.ENDC}")

            for sub in ["agents", "skills", "workflows"]:
                src = repo_agent_dir / sub
                dst = target_path / sub

                if src.exists():
                    if not dst.exists():
                        dst.mkdir(parents=True)

                    for item in src.iterdir():
                        dest_item = dst / item.name
                        if item.is_dir():
                            if dest_item.exists():
                                shutil.rmtree(dest_item)
                            shutil.copytree(item, dest_item)
                        else:
                            shutil.copy2(item, dest_item)
                    print(f"{Colors.GREEN}    ✅ Sync {sub} complete.{Colors.ENDC}")

            for config_file in ["mcp_config.json"]:
                src_conf = repo_agent_dir / config_file
                dst_conf = target_path / config_file

                if src_conf.exists():
                    if not dst_conf.exists():
                        shutil.copy2(src_conf, dst_conf)
                        print(f"{Colors.GREEN}    ✅ Init {config_file} from Kit.{Colors.ENDC}")
                    else:
                        print(f"{Colors.YELLOW}    🔒 Kept local {config_file} (User Override).{Colors.ENDC}")

            print(f"{Colors.GREEN}✨ Antigravity Kit is now up to date!{Colors.ENDC}")
            check_and_refresh_project(str(target_path))

        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Failed to clone repository: {e.stderr.decode()}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error during sync: {e}{Colors.ENDC}")
