import argparse
import sys
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
    init_parser = subparsers.add_parser("init", help="Initialize AI in current project (Copilot, Kiro, OpenCode)")
    init_parser.add_argument("--source", default=".agent", help="Source of knowledge")

    # OpenCode Subcommand
    opencode_parser = subparsers.add_parser("opencode", help="Convert to OpenCode format")
    opencode_parser.add_argument("--source", default=".agent", help="Source directory")

    args = parser.parse_args()

    if args.format == "kiro":
        convert_kiro(args.source, args.output)
    elif args.format == "copilot":
        convert_copilot(args.source, args.output)
    elif args.format == "update" or args.format == "update-kit":
        update_kit(args.target)
    elif args.format == "init":
        print("\033[95m🚀 Initializing AI for current project...\033[0m")
        # Try convert for all
        convert_copilot(args.source, "")
        convert_kiro(args.source, ".kiro")
        convert_opencode(args.source, "")
        print("\033[92m✅ Initialization complete!\033[0m")
    elif args.format == "opencode":
        convert_opencode(args.source, "")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
