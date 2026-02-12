# Agent Bridge

Convert and sync AI agent knowledge to your IDE — supports multiple knowledge sources and bidirectional sync.

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

| IDE            | Output Directory | Status |
| -------------- | ---------------- | ------ |
| Cursor AI      | `.cursor/`       | Beta   |
| Kiro CLI       | `.kiro/`         | Stable |
| GitHub Copilot | `.github/`       | Beta   |
| OpenCode       | `.opencode/`     | Beta   |
| Windsurf       | `.windsurf/`     | Beta   |

## Commands

### Core Commands

```bash
agent-bridge init [--cursor|--kiro|--copilot|--all]
```

Set up agent configs for your project. Runs interactive TUI by default. Use flags to skip the TUI.

```bash
agent-bridge status
```

Show a dashboard of the current project: source content counts, vault sync status, IDE initialization state, and MCP configuration.

```bash
agent-bridge update
```

Pull latest knowledge from all registered vaults and refresh any existing IDE configs in the current project.

### Capture & Snapshot Commands

```bash
agent-bridge capture [--ide cursor|kiro|copilot] [--strategy ide_wins|agent_wins]
```

Reverse-sync: capture changes from IDE configs back to `.agent/` directory. Useful when you've edited agent files in your IDE and want to preserve those changes.

- `--ide`: Specify which IDE to capture from (default: all initialized IDEs)
- `--strategy`: Conflict resolution strategy
  - `ide_wins`: IDE changes overwrite `.agent/` files (default)
  - `agent_wins`: Skip files that haven't been modified in IDE

```bash
agent-bridge snapshot save <name> [--description "..."]
```

Save current `.agent/` state as a named snapshot for later restoration.

```bash
agent-bridge snapshot list
```

List all saved snapshots with metadata.

```bash
agent-bridge snapshot restore <name>
```

Restore `.agent/` directory from a saved snapshot.

```bash
agent-bridge snapshot delete <name>
```

Delete a saved snapshot.

### Vault Management

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

### Other Commands

```bash
agent-bridge mcp --all
```

Install MCP (Model Context Protocol) configuration to all IDEs. Use `--cursor`, `--kiro`, etc. to target specific IDEs.

```bash
agent-bridge clean --all
```

Remove generated IDE configuration directories.

```bash
agent-bridge list
```

List all supported IDE formats.

```bash
agent-bridge <ide>
```

Convert directly to a specific IDE (e.g. `agent-bridge kiro`, `agent-bridge cursor`).

## Bidirectional Sync Workflow

Agent Bridge supports full bidirectional sync between `.agent/` and IDE configs:

```bash
# 1. Initialize IDE configs from .agent/
agent-bridge init --cursor

# 2. Edit agent files in Cursor IDE
# ... make changes to .cursor/agents/orchestrator.md ...

# 3. Capture changes back to .agent/
agent-bridge capture --ide cursor

# 4. Save a snapshot before major changes
agent-bridge snapshot save "before-refactor" --description "Stable state"

# 5. Make experimental changes
# ... edit .agent/ files ...

# 6. Restore if needed
agent-bridge snapshot restore "before-refactor"
```

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

**Reverse conversion** allows capturing changes made in IDE configs back to the source `.agent/` format, enabling true bidirectional sync.

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
│   ├── init_service.py    # init command logic
│   ├── sync_service.py    # update command logic
│   ├── capture_service.py # reverse sync logic
│   └── snapshot_service.py # snapshot management
└── builtin_vault/   # Built-in starter (no external deps)
```

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/test_capture_service.py
pytest tests/test_snapshot_service.py
pytest tests/test_roundtrip.py

```

## Credits

- [Antigravity Kit](https://github.com/vudovn/antigravity-kit) by Vudovn (MIT License)
- [UI-UX Pro Max](https://github.com/nextlevelbuilder) by NextLevelBuilder (MIT License)

## License

MIT © HaoNgo232
