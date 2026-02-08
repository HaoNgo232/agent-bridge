# Agent Bridge

Convert and sync AI agent knowledge to your IDE — supports multiple knowledge sources.

## Install

```bash
pip install git+https://github.com/HaoNgo232/agent-bridge
```

## Quick Start

```bash
cd your-project

# Interactive setup (recommended)
agent-bridge init

# Or specify your IDE directly
agent-bridge init --cursor
```

The interactive mode walks you through selecting knowledge sources and target IDE formats.

## Supported IDEs

| IDE | Output Directory | Status |
| --- | --- | --- |
| Cursor AI | `.cursor/` | Beta |
| Kiro CLI | `.kiro/` | Stable |
| GitHub Copilot | `.github/` | Beta |
| OpenCode | `.opencode/` | Beta |
| Windsurf | `.windsurf/` | Beta |

## Commands

```bash
agent-bridge init
```

Set up agent configs for your project. Runs interactive TUI by default. Use flags like `--cursor`, `--kiro`, or `--all` to skip the TUI.

```bash
agent-bridge update
```

Pull latest knowledge from all registered vaults and refresh any existing IDE configs in the current project.

```bash
agent-bridge mcp --all
```

Install MCP (Model Context Protocol) configuration to all IDEs. Use `--cursor`, `--kiro`, etc. to target specific IDEs.

```bash
agent-bridge clean --all
```

Remove generated IDE configuration directories.

```bash
agent-bridge vault list
```

Show all registered knowledge vaults.

```bash
agent-bridge vault add <name> <url>
```

Register a new vault (git repo or local path).

```bash
agent-bridge vault remove <name>
```

Unregister a vault.

```bash
agent-bridge vault sync
```

Download and update all registered vaults.

## Knowledge Vaults

Agent Bridge ships with [Antigravity Kit](https://github.com/vudovn/antigravity-kit) as the default vault, but you can register any git repo or local directory that follows the `.agent/` structure:

```bash
# Add your team's private vault
agent-bridge vault add my-team git@github.com:myorg/ai-agents.git

# Add a local directory
agent-bridge vault add local-agents /path/to/my-agents

# Sync all vaults
agent-bridge vault sync

# Now init will merge knowledge from all vaults
agent-bridge init --cursor
```

### Vault Structure

A vault is any directory containing:

```text
.agent/
├── agents/          # Agent personality files (*.md)
├── skills/          # Skill directories with SKILL.md
├── workflows/       # Workflow templates (*.md)
└── mcp_config.json  # MCP server configuration
```

When multiple vaults are registered, files are merged with project-local files taking priority, followed by vaults in priority order (lower number = higher priority).

## How It Works

Agent Bridge reads markdown-based agent definitions from `.agent/` and converts them to each IDE's native format — JSON configs for Kiro, MDC rules for Cursor, frontmatter-annotated markdown for Copilot, etc. MCP configurations are copied to each IDE's expected location.

## Project Structure

```text
src/agent_bridge/
├── cli.py           # CLI entry point and argument parsing
├── vault.py         # Multi-source vault management
├── kit_sync.py      # Knowledge synchronization
├── kiro_conv.py     # Kiro format converter
├── cursor_conv.py   # Cursor format converter
├── copilot_conv.py  # GitHub Copilot converter
├── opencode_conv.py # OpenCode converter
├── windsurf_conv.py # Windsurf converter
└── utils.py         # Shared utilities
```

## Credits

- [Antigravity Kit](https://github.com/vudovn/antigravity-kit) by Vudovn (MIT License)
- [UI-UX Pro Max](https://github.com/nextlevelbuilder) by NextLevelBuilder (MIT License)

## License

MIT © HaoNgo232
