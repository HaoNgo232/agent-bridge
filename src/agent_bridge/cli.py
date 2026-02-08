import argparse
import shutil
import sys
from pathlib import Path

import questionary
from questionary import Separator, Style

from .copilot_conv import convert_copilot, copy_mcp_copilot
from .cursor_conv import convert_cursor, copy_mcp_cursor
from .kiro_conv import convert_kiro, copy_mcp_kiro
from .kit_sync import update_kit
from .opencode_conv import convert_opencode, copy_mcp_opencode
from .utils import Colors
from .windsurf_conv import convert_windsurf, copy_mcp_windsurf

# Cấu hình phong cách tùy chỉnh cho Questionary (loại bỏ triệt để nền màu xanh)
CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#00d4ff bold"),  # Dấu hỏi
        ("question", "bold"),  # Nội dung câu hỏi
        ("answer", "fg:#00d4ff bold"),  # Câu trả lời đã chọn
        ("pointer", "fg:#00d4ff bold"),  # Con trỏ mũi tên (>)
        ("highlighted", "fg:#00d4ff bold bg:default"),  # Tùy chọn đang được trỏ tới (ép buộc nền mặc định)
        ("selected", "fg:#00d4ff bold bg:default"),  # Tùy chọn đã được chọn (ép buộc nền mặc định)
        ("checkbox", "fg:#888888"),  # Checkbox chưa chọn
        ("checkbox-selected", "fg:#00d4ff bold"),  # Checkbox đã chọn
    ]
)


def _tui_add_vault(has_local_agent: bool) -> str:
    """Interactive TUI flow for adding a custom vault. Returns source_choice or None to cancel."""
    from .vault import VaultManager

    print(f"\n{Colors.CYAN}  Add a Knowledge Vault{Colors.ENDC}\n")

    # Vault URL
    vault_url = questionary.text(
        "Git URL or local path:",
        instruction="(e.g. https://github.com/yourorg/ai-agents or /path/to/local)",
        style=CUSTOM_STYLE,
    ).ask()

    if not vault_url:
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return None

    # Auto-suggest name from URL
    default_name = vault_url.rstrip("/").split("/")[-1].replace(".git", "")
    vault_name = questionary.text(
        "Vault name (unique ID):",
        default=default_name,
        style=CUSTOM_STYLE,
    ).ask()

    if not vault_name:
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return None

    # Optional description
    vault_desc = (
        questionary.text(
            "Description (optional):",
            default="",
            style=CUSTOM_STYLE,
        ).ask()
        or ""
    )

    # Priority
    vault_priority = questionary.text(
        "Priority (lower = higher, default 100):",
        default="100",
        style=CUSTOM_STYLE,
    ).ask()
    try:
        priority = int(vault_priority)
    except (ValueError, TypeError):
        priority = 100

    # Register + Sync
    vm = VaultManager()
    try:
        vm.add(vault_name, vault_url, vault_desc, priority)
        print(f"\n  {Colors.GREEN}Vault '{vault_name}' registered.{Colors.ENDC}")
    except ValueError as e:
        print(f"  {Colors.YELLOW}{e}{Colors.ENDC}")
        # Vault already exists — still usable, continue

    print(f"  {Colors.CYAN}Syncing vault...{Colors.ENDC}")
    results = vm.sync(name=vault_name)
    vault_result = results.get(vault_name, {})
    if vault_result.get("status") == "ok":
        print(
            f"  {Colors.GREEN}Synced: {vault_result.get('agents', 0)} agents, {vault_result.get('skills', 0)} skills{Colors.ENDC}\n"
        )
    else:
        print(f"  {Colors.RED}Sync issue: {vault_result.get('status', 'unknown')}{Colors.ENDC}")
        print(f"  {Colors.YELLOW}Continuing anyway — you can retry with 'agent-bridge vault sync'{Colors.ENDC}\n")

    # Now ask how to use it
    if has_local_agent:
        return questionary.select(
            "How to use this vault with your project?",
            choices=[
                questionary.Choice("Merge vault + project (project wins)", value="merge"),
                questionary.Choice("Replace project agents with vault", value="vault"),
                questionary.Choice("Keep project agents only", value="project"),
            ],
            style=CUSTOM_STYLE,
        ).ask()
    else:
        return "vault"


def _get_vault_agent_dir() -> Path:
    """Lấy đường dẫn thư mục agent từ bộ nhớ đệm của vault chính."""
    try:
        from .vault import VaultManager

        vm = VaultManager()
        for vault in vm.enabled_vaults:
            if vault.is_local:
                source = Path(vault.url).resolve() / vault.agent_subdir
            else:
                source = vault.cache_path / vault.agent_subdir
            if source.exists():
                return source
    except ImportError:
        pass

    # Fallback to legacy master dir
    from .utils import get_master_agent_dir

    master = get_master_agent_dir()
    if master.exists():
        return master
    return None


def _fetch_vault_to_project(agent_dir: Path, overwrite: bool = False):
    """Sao chép các agent từ vault vào thư mục .agent/ của dự án."""
    vault_source = _get_vault_agent_dir()
    if not vault_source or not vault_source.exists():
        print(f"{Colors.YELLOW}Vault not synced yet. Running sync...{Colors.ENDC}")
        try:
            from .vault import VaultManager

            vm = VaultManager()
            vm.sync()
            vault_source = _get_vault_agent_dir()
        except Exception as e:
            print(f"{Colors.RED}Vault sync failed: {e}{Colors.ENDC}")
            return

    if not vault_source or not vault_source.exists():
        print(f"{Colors.RED}No vault source available.{Colors.ENDC}")
        return

    if agent_dir.exists() and overwrite:
        shutil.rmtree(agent_dir)

    if not agent_dir.exists():
        shutil.copytree(vault_source, agent_dir)
        print(f"{Colors.GREEN}Vault copied to .agent/{Colors.ENDC}")
    else:
        print(f"{Colors.YELLOW}.agent/ already exists, skipping copy.{Colors.ENDC}")


def _merge_vault_to_project(agent_dir: Path):
    """Hợp nhất các agent từ vault vào .agent/ hiện có của dự án (tệp dự án được ưu tiên)."""
    vault_source = _get_vault_agent_dir()
    if not vault_source or not vault_source.exists():
        print(f"{Colors.YELLOW}No vault to merge from. Run 'agent-bridge vault sync' first.{Colors.ENDC}")
        return

    for subdir in ["agents", "skills", "workflows"]:
        src = vault_source / subdir
        dst = agent_dir / subdir
        if not src.exists():
            continue
        dst.mkdir(parents=True, exist_ok=True)

        for item in src.iterdir():
            dest_item = dst / item.name
            if dest_item.exists():
                continue  # Project files win
            if item.is_dir():
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)

    print(f"{Colors.GREEN}Vault merged into .agent/{Colors.ENDC}")


def main():
    """Điểm vào chính của ứng dụng."""
    try:
        _main_inner()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        sys.exit(130)


def _main_inner():
    """Hàm xử lý logic chính cho CLI."""
    parser = argparse.ArgumentParser(description="Agent Bridge - Multi-format Agent Converter")
    subparsers = parser.add_subparsers(dest="format", help="Target format")

    # Kiro Subcommand
    kiro_parser = subparsers.add_parser("kiro", help="Convert to Kiro format")
    kiro_parser.add_argument("--source", default=".agent", help="Source directory")
    kiro_parser.add_argument("--output", default=".kiro", help="Output directory")

    # Copilot Subcommand
    copilot_parser = subparsers.add_parser("copilot", help="Convert to GitHub Copilot format")
    copilot_parser.add_argument("--source", default=".agent", help="Source directory")
    copilot_parser.add_argument("--output", default=".github/copilot-instructions.md", help="Output file path")

    # Update Subcommand
    update_parser = subparsers.add_parser("update", help="Clone latest from repo and refresh local configs")
    update_parser.add_argument("--target", default=".agent", help="Target directory to update")

    # Init Subcommand
    init_parser = subparsers.add_parser("init", help="Initialize AI in current project")
    init_parser.add_argument("--source", default=".agent", help="Source of knowledge")
    init_parser.add_argument("--copilot", action="store_true", help="Only init Copilot (disables TUI)")
    init_parser.add_argument("--kiro", action="store_true", help="Only init Kiro (disables TUI)")
    init_parser.add_argument("--opencode", action="store_true", help="Only init OpenCode (disables TUI)")
    init_parser.add_argument("--cursor", action="store_true", help="Only init Cursor (disables TUI)")
    init_parser.add_argument("--windsurf", action="store_true", help="Only init Windsurf (disables TUI)")
    init_parser.add_argument("--all", action="store_true", help="Init all formats (disables TUI)")
    init_parser.add_argument("--force", "-f", action="store_true", help="Force overwrite without prompt")
    init_parser.add_argument("--no-interactive", action="store_true", help="Disable interactive TUI mode")

    # OpenCode Subcommand
    opencode_parser = subparsers.add_parser("opencode", help="Convert to OpenCode format")
    opencode_parser.add_argument("--source", default=".agent", help="Source directory")

    # Clean Subcommand
    clean_parser = subparsers.add_parser("clean", help="Remove generated IDE configuration folders")
    clean_parser.add_argument("--copilot", action="store_true", help="Clean Copilot")
    clean_parser.add_argument("--kiro", action="store_true", help="Clean Kiro")
    clean_parser.add_argument("--opencode", action="store_true", help="Clean OpenCode")
    clean_parser.add_argument("--cursor", action="store_true", help="Clean Cursor")
    clean_parser.add_argument("--windsurf", action="store_true", help="Clean Windsurf")
    clean_parser.add_argument("--all", action="store_true", help="Clean all IDE formats")

    # List Subcommand
    subparsers.add_parser("list", help="List supported IDE formats")

    # Vault Subcommand
    vault_parser = subparsers.add_parser("vault", help="Manage knowledge vault sources")
    vault_sub = vault_parser.add_subparsers(dest="vault_action", help="Vault action")

    vault_sub.add_parser("list", help="List registered vaults")

    vault_add_parser = vault_sub.add_parser("add", help="Register a new vault source")
    vault_add_parser.add_argument("name", help="Vault name (unique identifier)")
    vault_add_parser.add_argument("url", help="Git URL or local path to vault")
    vault_add_parser.add_argument("--description", "-d", default="", help="Vault description")
    vault_add_parser.add_argument("--priority", "-p", type=int, default=100, help="Priority (lower = higher)")

    vault_remove_parser = vault_sub.add_parser("remove", help="Unregister a vault")
    vault_remove_parser.add_argument("name", help="Vault name to remove")

    vault_sync_parser = vault_sub.add_parser("sync", help="Sync vault(s) from source")
    vault_sync_parser.add_argument("--name", "-n", default=None, help="Specific vault to sync (default: all)")

    # MCP Subcommand
    mcp_parser = subparsers.add_parser("mcp", help="Install MCP configuration manually")
    mcp_parser.add_argument("--cursor", action="store_true", help="Install to Cursor (.cursor/mcp.json)")
    mcp_parser.add_argument("--windsurf", action="store_true", help="Install to Windsurf (.windsurf/mcp_config.json)")
    mcp_parser.add_argument("--opencode", action="store_true", help="Install to OpenCode (.opencode/mcp.json)")
    mcp_parser.add_argument("--copilot", action="store_true", help="Install to GitHub Copilot (.vscode/mcp.json)")
    mcp_parser.add_argument("--kiro", action="store_true", help="Install to Kiro (.kiro/settings/mcp.json)")
    mcp_parser.add_argument("--all", action="store_true", help="Install to ALL supported IDEs")
    mcp_parser.add_argument("--force", "-f", action="store_true", help="Force overwrite without prompt")

    args = parser.parse_args()

    # --- DISPATCH COMMANDS ---
    if args.format == "init":
        print(f"{Colors.HEADER}🚀 Initializing AI for current project...{Colors.ENDC}")

        SOURCE_DIR = args.source
        project_path = Path.cwd()
        agent_dir = project_path / SOURCE_DIR

        # Determine if we should use interactive mode
        # TUI is DEFAULT unless:
        # 1. User specified format flags (--kiro, --cursor, etc.)
        # 2. User used --no-interactive
        # 3. User used --force (implies non-interactive)
        has_format_flags = args.copilot or args.kiro or args.opencode or args.cursor or args.windsurf or args.all
        use_interactive = not has_format_flags and not args.no_interactive and not args.force

        # Interactive mode with Questionary (DEFAULT)
        if use_interactive:
            print(f"\n{Colors.CYAN}Agent Bridge - Interactive Setup{Colors.ENDC}\n")

            # 1. Agent source selection
            has_local_agent = agent_dir.exists()

            if has_local_agent:
                source_choice = questionary.select(
                    "Agent source:",
                    choices=[
                        questionary.Choice("Use project agents (.agent/)", value="project"),
                        questionary.Choice("Merge vault + project (project wins)", value="merge"),
                        questionary.Choice("Replace with vault agents", value="vault"),
                        Separator(),
                        questionary.Choice("Add your own vault first...", value="add_vault"),
                    ],
                    style=CUSTOM_STYLE,
                ).ask()
            else:
                source_choice = questionary.select(
                    "No .agent/ found locally. Choose a source:",
                    choices=[
                        questionary.Choice("Use default vault (Antigravity Kit)", value="vault"),
                        questionary.Choice("Add your own vault...", value="add_vault"),
                    ],
                    style=CUSTOM_STYLE,
                ).ask()

            if not source_choice:
                print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
                return

            # 1b. Handle "Add your own vault" flow
            if source_choice == "add_vault":
                source_choice = _tui_add_vault(has_local_agent)
                if not source_choice:
                    return

            # 2. Format selection (multi-select with sensible defaults) offer to add one
            if source_choice in ("vault", "merge"):
                try:
                    from .vault import VaultManager

                    vm = VaultManager()
                    if not vm.enabled_vaults:
                        print(f"\n  {Colors.YELLOW}No vaults registered yet.{Colors.ENDC}")
                        add_vault = questionary.confirm(
                            "Add a vault source now?", default=True, style=CUSTOM_STYLE
                        ).ask()

                        if add_vault:
                            vault_url = questionary.text(
                                "Git URL or local path:",
                                default="https://github.com/vudovn/antigravity-kit",
                                style=CUSTOM_STYLE,
                            ).ask()

                            if vault_url:
                                vault_name = questionary.text(
                                    "Vault name:",
                                    default=vault_url.rstrip("/").split("/")[-1].replace(".git", ""),
                                    style=CUSTOM_STYLE,
                                ).ask()

                                if vault_name:
                                    try:
                                        vm.add(vault_name, vault_url)
                                        print(
                                            f"  {Colors.GREEN}Vault '{vault_name}' registered. Syncing...{Colors.ENDC}"
                                        )
                                        vm.sync(name=vault_name)
                                    except ValueError as e:
                                        print(f"  {Colors.YELLOW}{e}{Colors.ENDC}")
                        else:
                            print(f"{Colors.YELLOW}Cannot proceed without vault. Cancelled.{Colors.ENDC}")
                            return
                except ImportError:
                    pass

            # 2. Format selection (multi-select with sensible defaults)
            format_choices = questionary.checkbox(
                "Select target IDE formats:",
                choices=[
                    questionary.Choice("Cursor (.cursor/)", checked=False),
                    questionary.Choice("Kiro (.kiro/)"),
                    questionary.Choice("Copilot (.github/)"),
                    questionary.Choice("OpenCode (.opencode/)"),
                    questionary.Choice("Windsurf (.windsurf/)"),
                ],
                style=CUSTOM_STYLE,
                instruction="Space=toggle, Enter=confirm",
            ).ask()

            if not format_choices:
                print(f"\n{Colors.YELLOW}No format selected. Use Space to toggle, then Enter.{Colors.ENDC}")
                return

            # Map choices to format flags
            formats = {
                "kiro": "Kiro (.kiro/)" in format_choices,
                "cursor": "Cursor (.cursor/)" in format_choices,
                "copilot": "Copilot (.github/)" in format_choices,
                "opencode": "OpenCode (.opencode/)" in format_choices,
                "windsurf": "Windsurf (.windsurf/)" in format_choices,
            }

            selected_names = [k for k, v in formats.items() if v]

            # 3. Confirmation
            print(f"\n  Source:  {Colors.CYAN}{source_choice}{Colors.ENDC}")
            print(f"  Target:  {Colors.CYAN}{', '.join(selected_names)}{Colors.ENDC}")

            confirm = questionary.confirm("Proceed?", default=True, style=CUSTOM_STYLE).ask()

            if not confirm:
                print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
                return

            # Handle source choice using VaultManager
            if source_choice == "vault" or (source_choice == "merge" and not agent_dir.exists()):
                _fetch_vault_to_project(agent_dir, overwrite=(source_choice == "vault"))
            elif source_choice == "merge":
                _merge_vault_to_project(agent_dir)

            # Final check: do we actually have .agent now?
            if not agent_dir.exists():
                print(f"{Colors.RED}No agent source available. Run 'agent-bridge vault sync' first.{Colors.ENDC}")
                return

        else:
            # CLI mode (when flags are provided)
            select_all = args.all or (
                not args.copilot and not args.kiro and not args.opencode and not args.cursor and not args.windsurf
            )
            formats = {
                "kiro": select_all or args.kiro,
                "cursor": select_all or args.cursor,
                "copilot": select_all or args.copilot,
                "opencode": select_all or args.opencode,
                "windsurf": select_all or args.windsurf,
            }

        # Convert to selected formats
        print(f"\n{Colors.CYAN}🔄 Converting agents...{Colors.ENDC}\n")

        if formats["copilot"]:
            convert_copilot(SOURCE_DIR, "", force=args.force)
            copy_mcp_copilot(Path("."), force=args.force)
            print(f"{Colors.GREEN}✅ Copilot format created{Colors.ENDC}")

        if formats["kiro"]:
            convert_kiro(SOURCE_DIR, ".kiro", force=args.force)
            copy_mcp_kiro(Path("."), force=args.force)
            print(f"{Colors.GREEN}✅ Kiro format created{Colors.ENDC}")

        if formats["opencode"]:
            convert_opencode(SOURCE_DIR, "", force=args.force)
            copy_mcp_opencode(Path("."), force=args.force)
            print(f"{Colors.GREEN}✅ OpenCode format created{Colors.ENDC}")

        if formats["cursor"]:
            convert_cursor(SOURCE_DIR, "", force=args.force)
            copy_mcp_cursor(Path("."), force=args.force)
            print(f"{Colors.GREEN}✅ Cursor format created{Colors.ENDC}")

        if formats["windsurf"]:
            convert_windsurf(SOURCE_DIR, "", force=args.force)
            copy_mcp_windsurf(Path("."), force=args.force)
            print(f"{Colors.GREEN}✅ Windsurf format created{Colors.ENDC}")

        print(f"\n{Colors.GREEN}🎉 Initialization complete!{Colors.ENDC}")

    elif args.format == "mcp":
        print(f"{Colors.HEADER}⚙️ Installing MCP configuration...{Colors.ENDC}")
        install_all = args.all or (
            not args.cursor and not args.windsurf and not args.opencode and not args.copilot and not args.kiro
        )

        if install_all or args.cursor:
            copy_mcp_cursor(Path("."), force=args.force)
        if install_all or args.windsurf:
            copy_mcp_windsurf(Path("."), force=args.force)
        if install_all or args.opencode:
            copy_mcp_opencode(Path("."), force=args.force)
        if install_all or args.copilot:
            copy_mcp_copilot(Path("."), force=args.force)
        if install_all or args.kiro:
            copy_mcp_kiro(Path("."), force=args.force)
        print(f"{Colors.GREEN}✅ MCP configuration installed!{Colors.ENDC}")
    elif args.format == "list":
        print(f"{Colors.BLUE}📂 Supported IDE Formats:{Colors.ENDC}")
        print(f"  - {Colors.YELLOW}copilot{Colors.ENDC}: GitHub Copilot (.github/agents/)")
        print(f"  - {Colors.YELLOW}kiro{Colors.ENDC}: Kiro CLI (.kiro/agents/)")
        print(f"  - {Colors.YELLOW}opencode{Colors.ENDC}: OpenCode IDE (.opencode/agents/ + AGENTS.md)")
        print(f"  - {Colors.YELLOW}cursor{Colors.ENDC}: Cursor AI (.cursor/rules/*.mdc)")
        print(f"  - {Colors.YELLOW}windsurf{Colors.ENDC}: Windsurf AI (.windsurf/rules/ + .windsurfrules)")
    elif args.format == "kiro":
        convert_kiro(args.source, args.output)
    elif args.format == "copilot":
        convert_copilot(args.source, args.output)
    elif args.format == "cursor":
        convert_cursor(args.source, "")
    elif args.format == "windsurf":
        convert_windsurf(args.source, "")
    elif args.format == "update":
        update_kit(args.target)
    elif args.format == "opencode":
        convert_opencode(args.source, "")
    elif args.format == "vault":
        from .vault import VaultManager

        vm = VaultManager()

        if args.vault_action == "list":
            vaults = vm.list_vaults()
            if not vaults:
                print(f"{Colors.YELLOW}No vaults registered.{Colors.ENDC}")
            else:
                print(f"{Colors.HEADER}📦 Registered Vaults:{Colors.ENDC}\n")
                for v in vaults:
                    status = f"{Colors.GREEN}●{Colors.ENDC}" if v["enabled"] else f"{Colors.RED}○{Colors.ENDC}"
                    cached = "cached" if v.get("cached") else "not synced"
                    print(f"  {status} {Colors.BOLD}{v['name']}{Colors.ENDC} (priority: {v['priority']}, {cached})")
                    print(f"    {v['url']}")
                    if v.get("description"):
                        print(f"    {Colors.CYAN}{v['description']}{Colors.ENDC}")
                    print()

        elif args.vault_action == "add":
            try:
                vault = vm.add(args.name, args.url, args.description, args.priority)
                print(f"{Colors.GREEN}✅ Vault '{vault.name}' registered.{Colors.ENDC}")
                print("   Run 'agent-bridge vault sync' to download it.")
            except ValueError as e:
                print(f"{Colors.RED}❌ {e}{Colors.ENDC}")

        elif args.vault_action == "remove":
            if vm.remove(args.name):
                print(f"{Colors.GREEN}✅ Vault '{args.name}' removed.{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Vault '{args.name}' not found.{Colors.ENDC}")

        elif args.vault_action == "sync":
            print(f"{Colors.HEADER}🔄 Syncing vaults...{Colors.ENDC}")
            results = vm.sync(name=args.name)
            for name, stats in results.items():
                if stats["status"] == "ok":
                    print(f"  {Colors.GREEN}✅ {name}: {stats['agents']} agents, {stats['skills']} skills{Colors.ENDC}")
                else:
                    print(f"  {Colors.RED}❌ {name}: {stats['status']}{Colors.ENDC}")

        else:
            vault_parser.print_help()

    elif args.format == "clean":
        import os

        print(f"{Colors.YELLOW}🧹 Cleaning up IDE configurations...{Colors.ENDC}")
        clean_all = args.all or (
            not args.copilot and not args.kiro and not args.opencode and not args.cursor and not args.windsurf
        )

        if clean_all or args.copilot:
            github_agents = Path(".github/agents")
            github_skills = Path(".github/skills")
            if github_agents.exists():
                shutil.rmtree(github_agents)
                print("  🗑️  Removed .github/agents")
            if github_skills.exists():
                shutil.rmtree(github_skills)
                print("  🗑️  Removed .github/skills")

        if clean_all or args.kiro:
            if Path(".kiro").exists():
                shutil.rmtree(".kiro")
                print("  🗑️  Removed .kiro")

        if clean_all or args.opencode:
            if Path(".opencode").exists():
                shutil.rmtree(".opencode")
                print("  🗑️  Removed .opencode")
            if Path("AGENTS.md").exists():
                os.remove("AGENTS.md")
                print("  🗑️  Removed AGENTS.md")

        if clean_all or args.cursor:
            if Path(".cursor").exists():
                shutil.rmtree(".cursor")
                print("  🗑️  Removed .cursor")

        if clean_all or args.windsurf:
            if Path(".windsurf").exists():
                shutil.rmtree(".windsurf")
                print("  🗑️  Removed .windsurf")
            if Path(".windsurfrules").exists():
                os.remove(".windsurfrules")
                print("  🗑️  Removed .windsurfrules")
        print(f"{Colors.GREEN}✅ Cleanup complete!{Colors.ENDC}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
