"""
CLI entry point — thin dispatcher only.

Parse args -> goi service -> in ket qua.
"""

import argparse
import sys
from pathlib import Path

from agent_bridge.utils import Colors


def main():
    try:
        _main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        sys.exit(130)


def _main():
    # Import converters de tu dang ky
    from agent_bridge import converters  # noqa: F401
    from agent_bridge.core.converter import converter_registry

    parser = argparse.ArgumentParser(
        description="Agent Bridge - Multi-format Agent Converter"
    )
    sub = parser.add_subparsers(dest="format", help="Target format")

    # --- init ---
    p_init = sub.add_parser("init", help="Initialize AI in current project")
    p_init.add_argument("--source", default=".agent", help="Source directory")
    p_init.add_argument("--force", "-f", action="store_true", help="Force overwrite")
    p_init.add_argument("--no-interactive", action="store_true", help="Disable TUI")
    p_init.add_argument("--all", action="store_true", help="Init all formats")
    for name in converter_registry.names():
        p_init.add_argument(f"--{name}", action="store_true")

    # --- update ---
    p_update = sub.add_parser("update", help="Sync vaults and refresh configs")
    p_update.add_argument("--target", default=".agent", help="Target directory")

    # --- clean ---
    p_clean = sub.add_parser("clean", help="Remove generated IDE configs")
    p_clean.add_argument("--all", action="store_true")
    for name in converter_registry.names():
        p_clean.add_argument(f"--{name}", action="store_true")

    # --- mcp ---
    p_mcp = sub.add_parser("mcp", help="Install MCP configuration")
    p_mcp.add_argument("--all", action="store_true")
    p_mcp.add_argument("--force", "-f", action="store_true")
    for name in converter_registry.names():
        p_mcp.add_argument(f"--{name}", action="store_true")

    # --- list ---
    sub.add_parser("list", help="List supported IDE formats")

    # --- vault ---
    p_vault = sub.add_parser("vault", help="Manage knowledge vaults")
    vault_sub = p_vault.add_subparsers(dest="vault_action")
    vault_sub.add_parser("list")
    p_add = vault_sub.add_parser("add")
    p_add.add_argument("name", help="Vault name")
    p_add.add_argument("url", help="Git URL or local path")
    p_add.add_argument("--description", "-d", default="")
    p_add.add_argument("--priority", "-p", type=int, default=100)
    p_remove = vault_sub.add_parser("remove")
    p_remove.add_argument("name", help="Vault name to remove")
    p_sync = vault_sub.add_parser("sync")
    p_sync.add_argument("--name", "-n", default=None, help="Specific vault to sync")

    # --- Direct convert (backward compat) ---
    for name in converter_registry.names():
        p = sub.add_parser(name, help=f"Convert to {name}")
        p.add_argument("--source", default=".agent")
        p.add_argument("--output", default="")

    args = parser.parse_args()

    if args.format == "init":
        _handle_init(args, converter_registry)
    elif args.format == "update":
        _handle_update(args)
    elif args.format == "clean":
        _handle_clean(args, converter_registry)
    elif args.format == "mcp":
        _handle_mcp(args, converter_registry)
    elif args.format == "list":
        _handle_list(converter_registry)
    elif args.format == "vault":
        _handle_vault(args)
    elif args.format in converter_registry.names():
        _handle_direct_convert(args, converter_registry)
    else:
        parser.print_help()


def _get_selected_formats(args, registry) -> list:
    """Xac dinh cac format IDE duoc chon tu CLI flags."""
    if getattr(args, "all", False):
        return registry.names()
    selected = [n for n in registry.names() if getattr(args, n, False)]
    return selected if selected else registry.names()


def _handle_init(args, registry):
    from agent_bridge.services.init_service import run_init
    from agent_bridge.tui import run_init_tui

    project_path = Path.cwd()
    agent_dir = project_path / getattr(args, "source", ".agent")

    has_flags = any(getattr(args, n, False) for n in registry.names()) or getattr(
        args, "all", False
    )
    use_tui = not has_flags and not getattr(args, "no_interactive", False) and not getattr(args, "force", False)

    if use_tui:
        print(f"{Colors.HEADER}Initializing AI for current project...{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Agent Bridge - Interactive Setup{Colors.ENDC}\n")
        success = run_init_tui(registry, project_path, agent_dir)
        if success:
            print(f"\n{Colors.GREEN}Initialization complete!{Colors.ENDC}")
    else:
        formats = _get_selected_formats(args, registry)
        source_choice = "vault" if not agent_dir.exists() else "project"
        print(f"{Colors.HEADER}Initializing AI for current project...{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Converting agents...{Colors.ENDC}\n")

        result = run_init(
            project_path,
            formats,
            source_choice,
            force=getattr(args, "force", False),
            verbose=True,
        )

        if "error" in result:
            print(f"{Colors.RED}{result['error']}{Colors.ENDC}")
        else:
            for name, conv_result in result.items():
                if conv_result and getattr(conv_result, "ok", True):
                    print(f"{Colors.GREEN}{name} format created{Colors.ENDC}")
            print(f"\n{Colors.GREEN}Initialization complete!{Colors.ENDC}")


def _handle_update(args):
    from agent_bridge.services.sync_service import run_update

    target = Path(getattr(args, "target", ".agent"))
    run_update(target)


def _handle_clean(args, registry):
    import shutil

    project = Path.cwd()
    formats = _get_selected_formats(args, registry)

    for name in formats:
        conv = registry.get(name)
        if conv:
            conv.clean(project)

    # Clean AGENTS.md (OpenCode)
    if "opencode" in formats and (project / "AGENTS.md").exists():
        (project / "AGENTS.md").unlink()

    print(f"{Colors.GREEN}Cleanup complete!{Colors.ENDC}")


def _handle_mcp(args, registry):
    project = Path.cwd()
    source = project if (project / ".agent").exists() else None

    if not source:
        print("No .agent/ found. Run 'agent-bridge init' first.")
        return

    formats = _get_selected_formats(args, registry)
    for name in formats:
        conv = registry.get(name)
        if conv:
            conv.install_mcp(source, project, force=getattr(args, "force", False))

    print(f"{Colors.GREEN}MCP configuration installed!{Colors.ENDC}")


def _handle_list(registry):
    print(f"{Colors.BLUE}Supported IDE Formats:{Colors.ENDC}")
    for conv in registry.all():
        info = conv.format_info
        print(f"  - {info.name}: {info.display_name} ({info.output_dir}/) [{info.status}]")


def _handle_vault(args):
    from agent_bridge.vault import VaultManager

    vm = VaultManager()
    action = getattr(args, "vault_action", None)

    if action == "list":
        vaults = vm.list_vaults()
        if not vaults:
            print(f"{Colors.YELLOW}No vaults registered.{Colors.ENDC}")
        else:
            print(f"{Colors.HEADER}Registered Vaults:{Colors.ENDC}\n")
            for v in vaults:
                status = f"{Colors.GREEN}*{Colors.ENDC}" if v["enabled"] else f"{Colors.RED}o{Colors.ENDC}"
                cached = "cached" if v.get("cached") else "not synced"
                print(f"  {status} {Colors.BOLD}{v['name']}{Colors.ENDC} (priority: {v['priority']}, {cached})")
                print(f"    {v['url']}")
                if v.get("description"):
                    print(f"    {Colors.CYAN}{v['description']}{Colors.ENDC}")
                print()

    elif action == "add":
        try:
            vault = vm.add(args.name, args.url, args.description, args.priority)
            print(f"{Colors.GREEN}Vault '{vault.name}' registered.{Colors.ENDC}")
            print("Run 'agent-bridge vault sync' to download it.")
        except ValueError as e:
            print(f"{Colors.RED}{e}{Colors.ENDC}")

    elif action == "remove":
        if vm.remove(args.name):
            print(f"{Colors.GREEN}Vault '{args.name}' removed.{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Vault '{args.name}' not found.{Colors.ENDC}")

    elif action == "sync":
        print(f"{Colors.HEADER}Syncing vaults...{Colors.ENDC}")
        results = vm.sync(name=getattr(args, "name", None))
        for name, stats in results.items():
            if stats.get("status") == "ok":
                print(f"  {Colors.GREEN}{name}: {stats.get('agents', 0)} agents, {stats.get('skills', 0)} skills{Colors.ENDC}")
            else:
                print(f"  {Colors.RED}{name}: {stats.get('status', 'unknown')}{Colors.ENDC}")

    else:
        print("Usage: agent-bridge vault {list|add|remove|sync}")
        print("  list              - List registered vaults")
        print("  add NAME URL      - Register a vault")
        print("  remove NAME       - Unregister a vault")
        print("  sync [--name N]   - Sync vault(s)")


def _handle_direct_convert(args, registry):
    from agent_bridge.utils import resolve_source_root

    source = resolve_source_root(getattr(args, "source", ".agent"))
    if not source:
        return

    name = args.format
    conv = registry.get(name)
    if conv:
        result = conv.convert(source, Path.cwd(), verbose=True)
        conv.install_mcp(source, Path.cwd())
        if result.ok:
            print(f"{Colors.GREEN}{name} conversion complete!{Colors.ENDC}")


if __name__ == "__main__":
    main()
