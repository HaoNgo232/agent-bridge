import argparse
import sys
from pathlib import Path
from .utils import Colors, ask_user
from .kiro_conv import convert_kiro, copy_mcp_kiro
from .copilot_conv import convert_copilot, copy_mcp_copilot
from .opencode_conv import convert_opencode, copy_mcp_opencode
from .cursor_conv import convert_cursor, copy_mcp_cursor
from .windsurf_conv import convert_windsurf, copy_mcp_windsurf
from .kit_sync import update_kit

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
    init_parser.add_argument("--copilot", action="store_true", help="Only init Copilot")
    init_parser.add_argument("--kiro", action="store_true", help="Only init Kiro")
    init_parser.add_argument("--opencode", action="store_true", help="Only init OpenCode")
    init_parser.add_argument("--cursor", action="store_true", help="Only init Cursor")
    init_parser.add_argument("--windsurf", action="store_true", help="Only init Windsurf")
    init_parser.add_argument("--all", action="store_true", help="Init all formats (default if no flags)")
    init_parser.add_argument("--force", "-f", action="store_true", help="Force overwrite without prompt")

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
        
        # If no flags provided, set all to True
        select_all = args.all or (not args.copilot and not args.kiro and not args.opencode and not args.cursor and not args.windsurf)
        
        SOURCE_DIR = args.source

        if select_all or args.copilot:
            convert_copilot(SOURCE_DIR, "", force=args.force)
            copy_mcp_copilot(Path("."), force=args.force)
            
        if select_all or args.kiro:
            convert_kiro(SOURCE_DIR, ".kiro", force=args.force)
            copy_mcp_kiro(Path("."), force=args.force)
            
        if select_all or args.opencode:
            convert_opencode(SOURCE_DIR, "", force=args.force)
            copy_mcp_opencode(Path("."), force=args.force)
            
        if select_all or args.cursor:
            convert_cursor(SOURCE_DIR, "", force=args.force)
            copy_mcp_cursor(Path("."), force=args.force)
            
        if select_all or args.windsurf:
            convert_windsurf(SOURCE_DIR, "", force=args.force)
            copy_mcp_windsurf(Path("."), force=args.force)
            
        print(f"\n{Colors.GREEN}✅ Initialization complete!{Colors.ENDC}")

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
        print("\033[94m📂 Supported IDE Formats:\033[0m")
        print("  - \033[93mcopilot\033[0m: GitHub Copilot (.github/agents/)")
        print("  - \033[93mkiro\033[0m: Kiro CLI (.kiro/agents/)")
        print("  - \033[93mopencode\033[0m: OpenCode IDE (.opencode/agents/ + AGENTS.md)")
        print("  - \033[93mcursor\033[0m: Cursor AI (.cursor/rules/*.mdc)")
        print("  - \033[93mwindsurf\033[0m: Windsurf AI (.windsurf/rules/ + .windsurfrules)")
    elif args.format == "opencode":
        convert_opencode(args.source, "")
    elif args.format == "clean":
        import shutil
        import os
        print("\033[93m🧹 Cleaning up IDE configurations...\033[0m")
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
        print("\033[92m✅ Cleanup complete!\033[0m")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
