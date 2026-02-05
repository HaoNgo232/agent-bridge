import argparse
import sys
from pathlib import Path
from .kiro_conv import convert_kiro
from .copilot_conv import convert_copilot
from .opencode_conv import convert_opencode
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
    init_parser.add_argument("--all", action="store_true", help="Init all formats (default if no flags)")

    # OpenCode Subcommand
    opencode_parser = subparsers.add_parser("opencode", help="Convert to OpenCode format")
    opencode_parser.add_argument("--source", default=".agent", help="Source directory")
 
    # Clean Subcommand
    clean_parser = subparsers.add_parser("clean", help="Remove generated IDE configuration folders")
    clean_parser.add_argument("--copilot", action="store_true", help="Clean Copilot (.github/agents, .github/skills)")
    clean_parser.add_argument("--kiro", action="store_true", help="Clean Kiro (.kiro)")
    clean_parser.add_argument("--opencode", action="store_true", help="Clean OpenCode (.opencode, AGENTS.md)")
    clean_parser.add_argument("--all", action="store_true", help="Clean all IDE formats")
 
    # List Subcommand
    subparsers.add_parser("list", help="List supported IDE formats")

    args = parser.parse_args()

    if args.format == "kiro":
        convert_kiro(args.source, args.output)
    elif args.format == "copilot":
        convert_copilot(args.source, args.output)
    elif args.format == "update" or args.format == "update-kit":
        update_kit(args.target)
    elif args.format == "init":
        print("\033[95m🚀 Initializing AI for current project...\033[0m")
        
        # If no flags provided, set all to True
        select_all = args.all or (not args.copilot and not args.kiro and not args.opencode)
        
        if select_all or args.copilot:
            convert_copilot(args.source, "")
        if select_all or args.kiro:
            convert_kiro(args.source, ".kiro")
        if select_all or args.opencode:
            convert_opencode(args.source, "")
            
        print("\033[92m✅ Initialization complete!\033[0m")
    elif args.format == "list":
        print("\033[94m📂 Supported IDE Formats:\033[0m")
        print("  - \033[93mcopilot\033[0m: GitHub Copilot (.github/agents/)")
        print("  - \033[93mkiro\033[0m: Kiro CLI (.kiro/agents/)")
        print("  - \033[93mopencode\033[0m: OpenCode IDE (.opencode/agents/ + AGENTS.md)")
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
        print("\033[92m✅ Cleanup complete!\033[0m")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
