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
    p_init.add_argument("--from", dest="from_snapshot", metavar="SNAPSHOT", help="Initialize from saved snapshot")
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

    # --- capture ---
    p_capture = sub.add_parser("capture", help="Reverse-convert IDE configs back to .agent/")
    p_capture.add_argument("--cursor", action="store_true", help="Only capture from Cursor")
    p_capture.add_argument("--kiro", action="store_true", help="Only capture from Kiro")
    p_capture.add_argument("--copilot", action="store_true", help="Only capture from Copilot")
    p_capture.add_argument("--all", action="store_true", help="Capture from all detected IDEs")
    p_capture.add_argument("--dry-run", action="store_true", help="Show what would be captured, don't write")
    p_capture.add_argument("--strategy", choices=["ide_wins", "agent_wins", "ask"], default="ask", help="Conflict resolution strategy")

    # --- snapshot ---
    p_snapshot = sub.add_parser("snapshot", help="Save/manage .agent/ snapshots")
    snap_sub = p_snapshot.add_subparsers(dest="snapshot_action")
    p_snap_save = snap_sub.add_parser("save", help="Save current .agent/ as snapshot")
    p_snap_save.add_argument("name", help="Snapshot name")
    p_snap_save.add_argument("--desc", "-d", dest="description", default="", help="Description")
    p_snap_save.add_argument("--tag", "-t", action="append", dest="tags", help="Tag (format: key:value)")
    p_snap_list = snap_sub.add_parser("list")
    p_snap_info = snap_sub.add_parser("info")
    p_snap_info.add_argument("name", help="Snapshot name")
    p_snap_delete = snap_sub.add_parser("delete")
    p_snap_delete.add_argument("name", help="Snapshot name")
    p_snap_restore = snap_sub.add_parser("restore", help="Restore .agent/ from snapshot")
    p_snap_restore.add_argument("name", help="Snapshot name")

    # --- list ---
    sub.add_parser("list", help="List supported IDE formats")

    # --- status ---
    p_status = sub.add_parser("status", help="Show project status dashboard")
    p_status.add_argument("--json", action="store_true", help="Output as JSON")

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
    elif args.format == "capture":
        _handle_capture(args)
    elif args.format == "snapshot":
        _handle_snapshot(args)
    elif args.format == "update":
        _handle_update(args)
    elif args.format == "clean":
        _handle_clean(args, converter_registry)
    elif args.format == "mcp":
        _handle_mcp(args, converter_registry)
    elif args.format == "list":
        _handle_list(converter_registry)
    elif args.format == "status":
        _handle_status(args)
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

    from_snapshot = getattr(args, "from_snapshot", None)

    if use_tui and not from_snapshot:
        print(f"{Colors.HEADER}Initializing AI for current project...{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Agent Bridge - Interactive Setup{Colors.ENDC}\n")
        success = run_init_tui(registry, project_path, agent_dir)
        if success:
            print(f"\n{Colors.GREEN}Initialization complete!{Colors.ENDC}")
    else:
        formats = _get_selected_formats(args, registry)
        if from_snapshot:
            source_choice = "snapshot"
            snapshot_name = from_snapshot
        else:
            source_choice = "vault" if not agent_dir.exists() else "project"
            snapshot_name = None
        print(f"{Colors.HEADER}Initializing AI for current project...{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Converting agents...{Colors.ENDC}\n")

        result = run_init(
            project_path,
            formats,
            source_choice,
            force=getattr(args, "force", False),
            verbose=True,
            snapshot_name=snapshot_name,
        )

        if "error" in result:
            print(f"{Colors.RED}{result['error']}{Colors.ENDC}")
        else:
            for name, conv_result in result.items():
                if conv_result and getattr(conv_result, "ok", True):
                    print(f"{Colors.GREEN}{name} format created{Colors.ENDC}")
            print(f"\n{Colors.GREEN}Initialization complete!{Colors.ENDC}")


def _handle_capture(args):
    from agent_bridge.services.capture_service import execute_capture, scan_for_captures
    from agent_bridge.tui import run_capture_tui

    project_path = Path.cwd()
    has_flags = getattr(args, "cursor", False) or getattr(args, "kiro", False) or getattr(args, "copilot", False) or getattr(args, "all", False)

    ide_names = None
    if has_flags:
        if getattr(args, "all", False):
            ide_names = ["cursor", "kiro", "copilot"]
        else:
            ide_names = [n for n in ["cursor", "kiro", "copilot"] if getattr(args, n, False)]

    files = scan_for_captures(project_path, ide_names=ide_names)
    if not files:
        print(f"{Colors.YELLOW}No IDE configs found to capture.{Colors.ENDC}")
        return

    dry_run = getattr(args, "dry_run", False)
    strategy = getattr(args, "strategy", "ask")

    if not has_flags or strategy == "ask":
        success = run_capture_tui(project_path, files, strategy, dry_run)
        if success:
            print(f"\n{Colors.GREEN}Capture complete!{Colors.ENDC}")
    else:
        result = execute_capture(project_path, files, strategy=strategy, dry_run=dry_run)
        if dry_run:
            print(f"{Colors.CYAN}Would capture {result.get('would_capture', 0)} files.{Colors.ENDC}")
        else:
            print(f"{Colors.GREEN}Captured: {result.get('captured', 0)} files.{Colors.ENDC}")


def _handle_snapshot(args):
    from agent_bridge.services.snapshot_service import (
        delete_snapshot,
        get_snapshot,
        list_snapshots,
        restore_snapshot,
        save_snapshot,
    )

    action = getattr(args, "snapshot_action", None)
    project_path = Path.cwd()
    agent_dir = project_path / ".agent"

    if action == "save":
        if not agent_dir.exists():
            print(f"{Colors.RED}No .agent/ found. Run 'agent-bridge init' first.{Colors.ENDC}")
            return
        tags = {}
        for t in getattr(args, "tags", None) or []:
            if ":" in t:
                k, _, v = t.partition(":")
                tags[k.strip()] = [x.strip() for x in v.split(",")]
        info = save_snapshot(args.name, agent_dir, getattr(args, "description", ""), tags)
        print(f"{Colors.GREEN}Snapshot '{info.name}' saved (v{info.version}).{Colors.ENDC}")
    elif action == "list":
        snapshots = list_snapshots()
        if not snapshots:
            print(f"{Colors.YELLOW}No snapshots found.{Colors.ENDC}")
        else:
            print(f"{Colors.HEADER}Saved Snapshots:{Colors.ENDC}\n")
            for s in snapshots:
                print(f"  {Colors.BOLD}{s.name}{Colors.ENDC} (v{s.version}) - {s.description or '(no description)'}")
                print(f"    Created: {s.created}")
                print()
    elif action == "info":
        name = getattr(args, "name", None)
        if not name:
            print(f"{Colors.RED}Usage: agent-bridge snapshot info <name>{Colors.ENDC}")
            return
        info = get_snapshot(name)
        if not info:
            print(f"{Colors.RED}Snapshot '{name}' not found.{Colors.ENDC}")
        else:
            print(f"{Colors.HEADER}Snapshot: {info.name}{Colors.ENDC}")
            print(f"  Description: {info.description}")
            print(f"  Version: {info.version}")
            print(f"  Created: {info.created}")
            print(f"  Updated: {info.updated}")
            print(f"  Contents: {info.contents}")
    elif action == "delete":
        name = getattr(args, "name", None)
        if not name:
            print(f"{Colors.RED}Usage: agent-bridge snapshot delete <name>{Colors.ENDC}")
            return
        if delete_snapshot(name):
            print(f"{Colors.GREEN}Snapshot '{name}' deleted.{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Snapshot '{name}' not found.{Colors.ENDC}")
    elif action == "restore":
        name = getattr(args, "name", None)
        if not name:
            print(f"{Colors.RED}Usage: agent-bridge snapshot restore <name>{Colors.ENDC}")
            return
        if restore_snapshot(agent_dir, name):
            print(f"{Colors.GREEN}Restored .agent/ from snapshot '{name}'.{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Snapshot '{name}' not found.{Colors.ENDC}")
    else:
        print("Usage: agent-bridge snapshot {save|list|info|delete|restore}")


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


def _handle_status(args):
    from agent_bridge.services.status_service import collect_status
    from agent_bridge.services.status_display import display_status
    import json as json_mod

    status = collect_status(Path.cwd())

    if getattr(args, "json", False):
        # Output machine-readable JSON (for scripts/CI)
        from dataclasses import asdict
        print(json_mod.dumps(asdict(status), indent=2, default=str))
    else:
        display_status(status)


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
