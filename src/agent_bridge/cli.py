import argparse
import sys
import shutil
from pathlib import Path
import questionary
from questionary import Style, Separator
from .utils import Colors, ask_user
from .kiro_conv import convert_kiro, copy_mcp_kiro
from .copilot_conv import convert_copilot, copy_mcp_copilot
from .opencode_conv import convert_opencode, copy_mcp_opencode
from .cursor_conv import convert_cursor, copy_mcp_cursor
from .windsurf_conv import convert_windsurf, copy_mcp_windsurf
from .kit_sync import update_kit

# Questionary custom style (no background at all)
CUSTOM_STYLE = Style([
    ('qmark', 'fg:#00d4ff bold'),       # Question mark
    ('question', 'bold'),                # Question text
    ('answer', 'fg:#00d4ff bold'),      # Selected answer
    ('pointer', 'fg:#00d4ff bold'),     # Arrow pointer (>)
    ('highlighted', 'fg:#00d4ff'),      # Highlighted option (NO background)
    ('selected', 'fg:#00d4ff'),         # Selected checkbox (NO background)
    ('checkbox', 'fg:#888888'),         # Unselected checkbox (gray)
    ('checkbox-selected', 'fg:#00d4ff bold'), # Selected checkbox (cyan)
])

def main():
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
            print(f"\n{Colors.CYAN}🚀 Agent Bridge - Interactive Setup{Colors.ENDC}\n")
            
            # 1. Agent source selection
            source_choice = questionary.select(
                "Where should we get the agents from?",
                choices=[
                    questionary.Choice("📁 Use agents from current project (.agent/)", value="project"),
                    questionary.Choice("📦 Use fresh agents from vault", value="vault"),
                    questionary.Choice("🔄 Merge both (project overrides vault)", value="merge"),
                ],
                style=CUSTOM_STYLE
            ).ask()
            
            if not source_choice:
                print(f"{Colors.YELLOW}❌ Cancelled{Colors.ENDC}")
                return
            
            # 2. Format selection (multi-select)
            format_choices = questionary.checkbox(
                "Select output formats to convert:",
                choices=[
                    questionary.Choice("Kiro CLI (.kiro/)"),  # No checked=True
                    questionary.Choice("Cursor IDE (.cursor/)"),
                    questionary.Choice("GitHub Copilot (.github/)"),
                    questionary.Choice("OpenCode IDE (.opencode/)"),
                    questionary.Choice("Windsurf IDE (.windsurf/)"),
                ],
                style=CUSTOM_STYLE,
                instruction="(Use Space to select, Enter to confirm)"
            ).ask()
            
            if not format_choices:
                print(f"\n{Colors.YELLOW}⚠️  No format selected. Please select at least one format.{Colors.ENDC}")
                print(f"{Colors.CYAN}💡 Tip: Use Space to select, then press Enter{Colors.ENDC}\n")
                # Don't exit, let user try again by re-running
                return
            
            # Map choices to format flags
            formats = {
                "kiro": "Kiro CLI (.kiro/)" in format_choices,
                "cursor": "Cursor IDE (.cursor/)" in format_choices,
                "copilot": "GitHub Copilot (.github/)" in format_choices,
                "opencode": "OpenCode IDE (.opencode/)" in format_choices,
                "windsurf": "Windsurf IDE (.windsurf/)" in format_choices,
            }
            
            # 3. Confirmation
            print(f"\n{Colors.BOLD}Summary:{Colors.ENDC}")
            print(f"  Source: {Colors.CYAN}{source_choice}{Colors.ENDC}")
            print(f"  Formats: {Colors.CYAN}{', '.join([k for k, v in formats.items() if v])}{Colors.ENDC}")
            
            confirm = questionary.confirm(
                "\nProceed with conversion?",
                default=True,
                style=CUSTOM_STYLE
            ).ask()
            
            if not confirm:
                print(f"{Colors.YELLOW}❌ Cancelled{Colors.ENDC}")
                return
            
            # Handle source choice
            if source_choice == "vault" or not agent_dir.exists():
                if not agent_dir.exists():
                    print(f"{Colors.YELLOW}📦 Copying vault to project...{Colors.ENDC}")
                    vault_dir = Path(__file__).parent / ".agent"
                    shutil.copytree(vault_dir, agent_dir)
                    print(f"{Colors.GREEN}✅ Vault copied successfully{Colors.ENDC}")
                elif source_choice == "vault":
                    overwrite = questionary.confirm(
                        "⚠️  .agent/ already exists. Overwrite with vault?",
                        default=False,
                        style=CUSTOM_STYLE
                    ).ask()
                    if overwrite:
                        shutil.rmtree(agent_dir)
                        vault_dir = Path(__file__).parent / ".agent"
                        shutil.copytree(vault_dir, agent_dir)
                        print(f"{Colors.GREEN}✅ Vault refreshed{Colors.ENDC}")
            
            elif source_choice == "merge":
                print(f"{Colors.YELLOW}🔄 Merging vault with project agents...{Colors.ENDC}")
                vault_dir = Path(__file__).parent / ".agent"
                
                # Merge agents
                for agent_file in (vault_dir / "agents").glob("*.md"):
                    target = agent_dir / "agents" / agent_file.name
                    if not target.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(agent_file, target)
                
                # Merge skills
                for skill_dir in (vault_dir / "skills").iterdir():
                    if skill_dir.is_dir():
                        target = agent_dir / "skills" / skill_dir.name
                        if not target.exists():
                            shutil.copytree(skill_dir, target)
                
                print(f"{Colors.GREEN}✅ Merge complete{Colors.ENDC}")
            
        else:
            # CLI mode (when flags are provided)
            select_all = args.all or (not args.copilot and not args.kiro and not args.opencode and not args.cursor and not args.windsurf)
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
        install_all = args.all or (not args.cursor and not args.windsurf and not args.opencode and not args.copilot and not args.kiro)

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
    elif args.format == "clean":
        import os
        print(f"{Colors.YELLOW}🧹 Cleaning up IDE configurations...{Colors.ENDC}")
        clean_all = args.all or (not args.copilot and not args.kiro and not args.opencode)
        
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
