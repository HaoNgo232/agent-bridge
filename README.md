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

```bash
agent-bridge list
```

List all supported IDE formats.

```bash
agent-bridge <ide>
```

Convert directly to a specific IDE (e.g. `agent-bridge kiro`, `agent-bridge cursor`).

## Knowledge Vaults

Agent Bridge ships with a built-in starter vault (no external deps, works offline). You can also register any git repo or local directory that follows the `.agent/` structure:

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
├── cli.py           # CLI entry point (thin dispatcher)
├── tui.py           # Interactive TUI for init
├── utils.py         # Shared utilities
├── core/            # Core types and registry
│   ├── types.py         # AgentRole, ConversionResult, IDEFormat
│   ├── agent_registry.py # Central agent role definitions
│   └── converter.py     # BaseConverter + ConverterRegistry
├── converters/      # IDE-specific converters (self-register)
│   ├── copilot.py, cursor.py, kiro.py, opencode.py, windsurf.py
│   └── _*_impl.py       # Conversion logic (internal)
├── vault/           # Multi-source vault management
│   ├── manager.py   # VaultManager
│   ├── sources.py   # GitSource, LocalSource, BuiltinSource
│   └── merger.py    # Merge strategies
├── services/        # Business logic
│   ├── init_service.py  # init command logic
│   └── sync_service.py  # update command logic
└── builtin_vault/   # Built-in starter (no external deps)
```

## Credits

- [Antigravity Kit](https://github.com/vudovn/antigravity-kit) by Vudovn (MIT License)
- [UI-UX Pro Max](https://github.com/nextlevelbuilder) by NextLevelBuilder (MIT License)

## License

MIT © HaoNgo232
