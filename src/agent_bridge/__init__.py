"""
Agent Bridge - Multi-format Agent/Skill converter for popular IDEs.

Converts Antigravity Kit agent configurations to:
- Kiro CLI (.kiro/)
- GitHub Copilot (.github/)
- Cursor AI (.cursor/)
- OpenCode IDE (.opencode/)
- Windsurf IDE (.windsurf/)
"""

__version__ = "0.1.0"

__all__ = [
    "cli",
    "kiro_conv",
    "copilot_conv",
    "cursor_conv",
    "opencode_conv",
    "windsurf_conv",
    "kit_sync",
    "utils",
]