# Agent Bridge - AI Agent Documentation

> **Purpose**: This file helps AI agents understand the Agent Bridge project structure, capabilities, and how to work with it effectively.

## 🎯 Project Overview

**Agent Bridge** is a universal converter that transforms AI agent knowledge from the `.agent/` format (Antigravity Kit) into multiple IDE-specific formats.

### What It Does

- **Converts** agent definitions, skills, and workflows
- **Supports** 5 IDE formats: Kiro CLI, Cursor, GitHub Copilot, OpenCode, Windsurf
- **Syncs** knowledge from multiple vault sources
- **Provides** interactive TUI for easy setup

### Key Features

1. **Multi-Format Support**: One source → 5 IDE formats
2. **Interactive TUI**: User-friendly setup with Questionary
3. **Vault System**: Manage multiple knowledge sources
4. **MCP Integration**: Model Context Protocol support
5. **Lint & Quality**: Ruff linter + automated checks

## 📁 Project Structure

```text
agent-bridge/
├── src/agent_bridge/          # Core package
│   ├── cli.py                 # CLI entry point (TUI)
│   ├── kiro_conv.py           # Kiro format converter
│   ├── cursor_conv.py         # Cursor format converter
│   ├── copilot_conv.py        # GitHub Copilot converter
│   ├── opencode_conv.py       # OpenCode converter
│   ├── windsurf_conv.py       # Windsurf converter
│   ├── vault.py               # Vault management
│   ├── kit_sync.py            # Knowledge sync
│   └── utils.py               # Shared utilities
├── .agent/                    # Embedded vault (Antigravity Kit)
├── scripts/                   # Helper scripts
│   ├── quick-check.sh         # Setup + lint check
│   └── pre-commit.sh          # Git pre-commit hook
├── tests/                     # Test suite
├── Makefile                   # Dev commands
└── pyproject.toml             # Package config

```

## 🔧 Core Modules

### 1. CLI (`cli.py`)

**Purpose**: Interactive command-line interface with TUI

**Key Functions**:

- `main()`: Entry point, handles all subcommands
- Interactive mode with Questionary (default)
- CLI mode with flags (backward compatible)

**Commands**:

```bash
agent-bridge init          # Interactive TUI (default)
agent-bridge init --kiro   # CLI mode
agent-bridge update        # Sync vaults
agent-bridge vault list    # List vaults
agent-bridge clean --all   # Remove configs
```

### 2. Converters

Each converter transforms `.agent/` to IDE-specific format:

| Converter | Output | Format |
| --- | --- | --- |
| `kiro_conv.py` | `.kiro/` | JSON agents + MD steering |
| `cursor_conv.py` | `.cursor/` | MDC rules + agents |
| `copilot_conv.py` | `.github/` | MD with frontmatter |
| `opencode_conv.py` | `.opencode/` | MD agents + skills |
| `windsurf_conv.py` | `.windsurf/` | MD rules + workflows |

**Common Pattern**:

```python
def convert_X(source_root, dest_root, verbose=True):
    # 1. Read from .agent/
    # 2. Transform to IDE format
    # 3. Write to destination
    # 4. Return stats
```

### 3. Vault System (`vault.py`)

**Purpose**: Manage multiple knowledge sources

**Key Classes**:

- `Vault`: Represents a knowledge source (git repo or local path)
- `VaultManager`: Manages multiple vaults, handles merging

**Features**:

- Git repo cloning/pulling
- Local path support
- Priority-based merging
- Config persistence

### 4. Utils (`utils.py`)

**Shared Utilities**:

- YAML frontmatter extraction
- MCP config handling
- File operations
- Color output

## 🎨 Interactive TUI

**Technology**: Questionary (Python prompt library)

**Flow**:

```text
1. Agent Source Selection
   ├─ Use project .agent/
   ├─ Use vault (fresh)
   └─ Merge both

2. Format Selection (multi-select)
   ├─ Kiro CLI
   ├─ Cursor IDE
   ├─ GitHub Copilot
   ├─ OpenCode IDE
   └─ Windsurf IDE

3. Confirmation
   └─ Show summary → Proceed?

4. Conversion
   └─ Convert to selected formats

5. Complete
   └─ Show success message
```

**Style**: Custom cyan theme, no background highlights

## 🧪 Development

### Setup

```bash
# Quick setup (recommended)
make setup

# Or manual
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Lint & Format

```bash
make lint      # Check code quality
make format    # Auto-fix + format
make check     # Run all checks
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Test specific converter
python -m pytest tests/test_converters.py::test_kiro_conversion
```

## 📚 Key Concepts

### 1. Agent Format (`.agent/`)

Standard structure:

```text
.agent/
├── agents/          # Agent personas (*.md)
├── skills/          # Skill modules (*/SKILL.md)
├── workflows/       # Slash commands (*.md)
├── rules/           # Global rules (*.md)
├── scripts/         # Helper scripts (*.py)
└── mcp_config.json  # MCP configuration
```

### 2. Conversion Logic

**Priority Order**:

1. Project `.agent/` (highest)
2. Custom vaults
3. Embedded vault (lowest)

**Merge Strategy**:

- Files with same name → Project wins
- New files → Added from vault
- MCP config → User choice (default: skip)

### 3. MCP (Model Context Protocol)

**What**: Protocol for AI tools to access context

**Where**: `.agent/mcp_config.json`

**Copied To**:

- Kiro: `.kiro/settings/mcp.json`
- Cursor: `.cursor/mcp.json`
- Copilot: `.vscode/mcp.json`
- OpenCode: `.opencode/mcp.json`
- Windsurf: `.windsurf/mcp_config.json`

## 🎯 Common Tasks

### Task 1: Add New IDE Support

1. Create `new_ide_conv.py`
2. Implement `convert_new_ide(source, dest, verbose)`
3. Add to `cli.py` init command
4. Update README

### Task 2: Fix Conversion Bug

1. Identify affected converter
2. Add test case in `tests/test_converters.py`
3. Fix converter logic
4. Run `make check`

### Task 3: Add New Feature

1. Check if it affects all converters
2. Update `utils.py` if shared logic
3. Update each converter if format-specific
4. Add tests
5. Update docs

## 🐛 Debugging

### Common Issues

**Issue**: TUI not showing

- **Cause**: Terminal doesn't support ANSI colors
- **Fix**: Use CLI mode with flags

**Issue**: Conversion fails

- **Cause**: Invalid `.agent/` structure
- **Fix**: Check `.agent/` has required files

**Issue**: MCP not copied

- **Cause**: User declined overwrite
- **Fix**: Use `--force` flag or delete existing MCP file

### Debug Mode

```bash
# Verbose output
agent-bridge init --kiro --verbose

# Check vault status
agent-bridge vault list

# Test conversion
python -c "from agent_bridge.kiro_conv import convert_kiro; convert_kiro('.', '.kiro', verbose=True)"
```

## 📊 Statistics

| Metric | Value |
| --- | --- |
| **Converters** | 5 (Kiro, Cursor, Copilot, OpenCode, Windsurf) |
| **Agents** | 20 (from Antigravity Kit) |
| **Skills** | 39 (from Antigravity Kit) |
| **Workflows** | 11 (slash commands) |
| **Lines of Code** | ~3,500 (Python) |
| **Dependencies** | 4 (PyYAML, click, rich, questionary) |

## 🔗 Related Files

- `README.md`: User documentation
- `QUICK_CHECK.md`: Setup script docs
- `LINT_SETUP.md`: Linting configuration
- `llms.txt`: LLM indexing file
- `pyproject.toml`: Package configuration

## 🎓 Learning Resources

### For AI Agents

1. **Start Here**: Read `README.md` for user perspective
2. **Understand Structure**: Review `.agent/` format
3. **Study Converters**: Pick one converter, understand its logic
4. **Test Changes**: Use `make check` before committing

### For Humans

1. **Quick Start**: Run `agent-bridge init -i`
2. **Explore**: Check generated files in `.kiro/`, `.cursor/`, etc.
3. **Customize**: Modify `.agent/` and run `agent-bridge update`
4. **Contribute**: See `CONTRIBUTING.md` (if exists)

## 🚀 Future Enhancements

- [ ] Support for more IDEs (VS Code, JetBrains)
- [ ] Web UI for configuration
- [ ] Cloud vault hosting
- [ ] Auto-sync on file changes
- [ ] Plugin system for custom converters

---

**Last Updated**: 2026-02-08
**Version**: 1.0.0
**Maintainer**: HaoNgo232
