"""
TUI interactive cho agent-bridge init.

Chuyen tat ca prompt questionary tu cli.py vao day.
"""

from pathlib import Path

import questionary
from questionary import Separator, Style

from agent_bridge.utils import Colors

# Cau hinh style cho Questionary
CUSTOM_STYLE = Style(
    [
        ("qmark", "fg:#00d4ff bold"),
        ("question", "bold"),
        ("answer", "fg:#00d4ff bold"),
        ("pointer", "fg:#00d4ff bold"),
        ("highlighted", "fg:#00d4ff bold bg:default"),
        ("selected", "fg:#00d4ff bold bg:default"),
        ("checkbox", "fg:#888888"),
        ("checkbox-selected", "fg:#00d4ff bold"),
    ]
)


def run_init_tui(registry, project_path: Path, agent_dir: Path) -> bool:
    """
    Luong init interactive day du.

    Returns:
        True neu thanh cong, False neu huy
    """
    from agent_bridge.services.init_service import run_init

    # 1. Chon nguon
    has_local_agent = agent_dir.exists()
    if has_local_agent:
        source_choice = questionary.select(
            "Agent source:",
            choices=[
                questionary.Choice("Use project agents (.agent/)", value="project"),
                questionary.Choice("Merge vault + project (project wins)", value="merge"),
                questionary.Choice("Replace with vault agents", value="vault"),
                Separator(),
                questionary.Choice("Add your own vault first...", value="add_vault"),
            ],
            style=CUSTOM_STYLE,
        ).ask()
    else:
        source_choice = questionary.select(
            "No .agent/ found locally. Choose a source:",
            choices=[
                questionary.Choice("Use default vault (builtin)", value="vault"),
                questionary.Choice("Add your own vault...", value="add_vault"),
            ],
            style=CUSTOM_STYLE,
        ).ask()

    if not source_choice:
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return False

    if source_choice == "add_vault":
        source_choice = _tui_add_vault(has_local_agent)
        if not source_choice:
            return False

    # 2. Xu ly vault neu can
    if source_choice in ("vault", "merge"):
        from agent_bridge.vault import VaultManager

        vm = VaultManager()
        if not vm.enabled_vaults:
            print(f"\n  {Colors.YELLOW}No vaults registered yet.{Colors.ENDC}")
            add_vault = questionary.confirm(
                "Add a vault source now?", default=True, style=CUSTOM_STYLE
            ).ask()

            if add_vault:
                vault_url = questionary.text(
                    "Git URL or local path:",
                    default="https://github.com/vudovn/antigravity-kit",
                    style=CUSTOM_STYLE,
                ).ask()

                if vault_url:
                    vault_name = questionary.text(
                        "Vault name:",
                        default=vault_url.rstrip("/").split("/")[-1].replace(".git", ""),
                        style=CUSTOM_STYLE,
                    ).ask()

                    if vault_name:
                        try:
                            vm.add(vault_name, vault_url)
                            print(f"  {Colors.GREEN}Vault '{vault_name}' registered. Syncing...{Colors.ENDC}")
                            vm.sync(name=vault_name)
                        except ValueError as e:
                            print(f"  {Colors.YELLOW}{e}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}Cannot proceed without vault. Cancelled.{Colors.ENDC}")
                return False

    # 3. Chon format
    choices = [
        questionary.Choice(conv.checkbox_label, value=conv.name)
        for conv in registry.all()
    ]
    format_choices = questionary.checkbox(
        "Select target IDE formats:",
        choices=choices,
        style=CUSTOM_STYLE,
        instruction="Space=toggle, Enter=confirm",
    ).ask()

    if not format_choices:
        print(f"\n{Colors.YELLOW}No format selected. Use Space to toggle, then Enter.{Colors.ENDC}")
        return False

    selected_names = list(format_choices)

    # 4. Xac nhan
    print(f"\n  Source:  {Colors.CYAN}{source_choice}{Colors.ENDC}")
    print(f"  Target:  {Colors.CYAN}{', '.join(selected_names)}{Colors.ENDC}")

    confirm = questionary.confirm("Proceed?", default=True, style=CUSTOM_STYLE).ask()

    if not confirm:
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return False

    # 5. Chay init
    run_init(project_path, selected_names, source_choice, force=False, verbose=True)
    return True


def _tui_add_vault(has_local_agent: bool) -> str | None:
    """TUI flow them vault custom. Tra ve source_choice hoac None neu huy."""
    from agent_bridge.vault import VaultManager

    print(f"\n{Colors.CYAN}  Add a Knowledge Vault{Colors.ENDC}\n")

    vault_url = questionary.text(
        "Git URL or local path:",
        instruction="(e.g. https://github.com/yourorg/ai-agents or /path/to/local)",
        style=CUSTOM_STYLE,
    ).ask()

    if not vault_url:
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return None

    default_name = vault_url.rstrip("/").split("/")[-1].replace(".git", "")
    vault_name = questionary.text(
        "Vault name (unique ID):",
        default=default_name,
        style=CUSTOM_STYLE,
    ).ask()

    if not vault_name:
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return None

    vault_desc = (
        questionary.text("Description (optional):", default="", style=CUSTOM_STYLE).ask()
        or ""
    )

    vault_priority = questionary.text(
        "Priority (lower = higher, default 100):",
        default="100",
        style=CUSTOM_STYLE,
    ).ask()
    try:
        priority = int(vault_priority)
    except (ValueError, TypeError):
        priority = 100

    vm = VaultManager()
    try:
        vm.add(vault_name, vault_url, vault_desc, priority)
        print(f"\n  {Colors.GREEN}Vault '{vault_name}' registered.{Colors.ENDC}")
    except ValueError as e:
        print(f"  {Colors.YELLOW}{e}{Colors.ENDC}")

    print(f"  {Colors.CYAN}Syncing vault...{Colors.ENDC}")
    results = vm.sync(name=vault_name)
    vault_result = results.get(vault_name, {})
    if vault_result.get("status") == "ok":
        print(
            f"  {Colors.GREEN}Synced: {vault_result.get('agents', 0)} agents, {vault_result.get('skills', 0)} skills{Colors.ENDC}\n"
        )
    else:
        print(f"  {Colors.RED}Sync issue: {vault_result.get('status', 'unknown')}{Colors.ENDC}")
        print(f"  {Colors.YELLOW}Continuing anyway — retry with 'agent-bridge vault sync'{Colors.ENDC}\n")

    if has_local_agent:
        return questionary.select(
            "How to use this vault with your project?",
            choices=[
                questionary.Choice("Merge vault + project (project wins)", value="merge"),
                questionary.Choice("Replace project agents with vault", value="vault"),
                questionary.Choice("Keep project agents only", value="project"),
            ],
            style=CUSTOM_STYLE,
        ).ask()
    return "vault"
