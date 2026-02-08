# Agent Bridge 🚀

A bridge tool to convert and synchronize Agent/Skill knowledge from Antigravity Kit to popular IDEs and CLIs.


## 🚀 Quick Start

Copy and run this command to install the tool in one go:

```bash
git clone https://github.com/HaoNgo232/agent-bridge && cd agent-bridge && pipx install -e . --force
```

*Note: You need `pipx` installed first (`sudo apt install pipx` or `brew install pipx`).*

## 🛠️ Usage

### 1. Initialize & Update (`init`)

Navigate to your project to initialize Agent, Skill configurations, and install MCP.

**✨ NEW: Interactive Mode with TUI!**

```bash
# Interactive mode (recommended for first-time users)
agent-bridge init -i

# Original CLI mode (backward compatible)
agent-bridge init --kiro
agent-bridge init --all
```

**Smart Init Features:**
- **🎨 Interactive TUI**: Arrow keys navigation, multi-select formats
- **📁 Agent Source**: Choose project/vault/merge
- **Security**: Asks before overwriting MCP config (Default: Skip to keep your keys).
- **Update**: Asks before updating Agent/Skill (Default: Yes).
- **Interactivity**: Use `--force` or `-f` to skip all prompts.

```bash
# Initialize for all formats (CLI mode)
agent-bridge init

# Use non-interactive mode
agent-bridge init --force

# Initialize specific format
agent-bridge init --copilot
agent-bridge init --opencode
agent-bridge init --kiro
agent-bridge init --cursor
agent-bridge init --windsurf
```

### 2. MCP Management (`mcp`)

Install or update MCP configuration (`.agent/mcp_config.json`) to IDEs.

```bash
# Install MCP for all IDEs (Asks if file exists)
agent-bridge mcp --all

# Force install
agent-bridge mcp --all --force

# Install for specific IDE
agent-bridge mcp --cursor    # .cursor/mcp.json
agent-bridge mcp --opencode  # .opencode/opencode.json
agent-bridge mcp --copilot   # .vscode/mcp.json
agent-bridge mcp --kiro      # .kiro/settings/mcp.json
```

### 3. Knowledge Sync (`update`)

Sync the latest knowledge from the original Antigravity Kit repository to your machine. This command automatically refreshes configurations if the project already has IDE folders.

```bash
agent-bridge update
```

### 4. Cleanup (`clean`)

Remove generated AI configuration directories:

```bash
# Remove all configurations
agent-bridge clean --all

# Remove specific format
agent-bridge clean --copilot
agent-bridge clean --kiro
```

## 💎 Supported Formats & Features

| IDE/CLI | Status | Config Location | Key Features |
|---------|--------|-----------------|--------------|
| **Kiro CLI** | 🟢 STABLE | `.kiro/` | **Official Professional Spec**, Auto-approve MCP tools, Custom Prompts (@), Spawn Hooks |
| **GitHub Copilot** | 🟡 BETA | `.github/` | Official Agent Spec (JSON/MD), Metadata merging |
| **OpenCode IDE** | 🟡 BETA | `.opencode/` | Unified JSON settings, Skill support |
| **Cursor AI** | � STABLE | `.cursor/` | **v2.4 Spec**, Slash Commands (/), Subagents, MDC Rules |
| **Windsurf IDE** | 🟡 BETA | `.windsurf/` | Context-aware logic |

## 📂 Project Structure

- `.agent/`: Master Vault storing original knowledge.
- `src/agent_bridge/`: Core conversion logic for each IDE.
- `utils.py`: CLI interface utilities and user interaction.

---

## 🏆 Credits & Acknowledgements

This project builds upon the excellent work of:

- **Antigravity Kit** by [Vudovn](https://github.com/vudovn) (MIT License) - The core knowledge vault.
- **UI-UX Pro Max** by [NextLevelBuilder](https://github.com/nextlevelbuilder) (MIT License) - Advanced design intelligence skill.

## 📄 License

*MIT © HaoNgo232*
