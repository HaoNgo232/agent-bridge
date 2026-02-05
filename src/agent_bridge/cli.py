import argparse
import sys
from pathlib import Path
from .kiro_conv import convert_kiro
from .copilot_conv import convert_copilot
from .opencode_conv import convert_opencode
from .cursor_conv import convert_cursor
from .windsurf_conv import convert_windsurf
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

    args = parser.parse_args()
    
    # --- DISPATCH COMMANDS ---
    if args.format == "init":
        from .copilot_conv import convert_copilot
        from .kiro_conv import convert_kiro
        from .opencode_conv import convert_opencode
        from .cursor_conv import convert_cursor
        from .windsurf_conv import convert_windsurf

        if args.all:
            convert_copilot(SOURCE_DIR, "")
            convert_kiro(SOURCE_DIR, ".kiro")
            convert_opencode(SOURCE_DIR, "")
            convert_cursor(SOURCE_DIR, "")
            convert_windsurf(SOURCE_DIR, "")
        else:
            if args.copilot: convert_copilot(SOURCE_DIR, "")
            if args.kiro: convert_kiro(SOURCE_DIR, ".kiro")
            if args.opencode: convert_opencode(SOURCE_DIR, "")
            if args.cursor: convert_cursor(SOURCE_DIR, "")
            if args.windsurf: convert_windsurf(SOURCE_DIR, "")
            
        print(f"\n{Colors.GREEN}✅ Initialization complete!{Colors.ENDC}")

    elif args.format == "mcp":
        from .cursor_conv import copy_mcp_cursor
        from .windsurf_conv import copy_mcp_windsurf
        from .opencode_conv import copy_mcp_opencode
        from .copilot_conv import copy_mcp_copilot
        from .kiro_conv import copy_mcp_kiro
        
        print("\033[95m⚙️ Installing MCP configuration...\033[0m")
        install_all = args.all or (not args.cursor and not args.windsurf and not args.opencode and not args.copilot and not args.kiro)

        if install_all or args.cursor:
            copy_mcp_cursor(Path("."))
        if install_all or args.windsurf:
            copy_mcp_windsurf(Path("."))
        if install_all or args.opencode:
            copy_mcp_opencode(Path("."))
        if install_all or args.copilot:
            copy_mcp_copilot(Path("."))
        if install_all or args.kiro:
            copy_mcp_kiro(Path("."))
        print("\033[92m✅ MCP configuration installed!\033[0m")
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
