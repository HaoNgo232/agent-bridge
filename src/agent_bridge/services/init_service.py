"""
Business logic cho lenh 'agent-bridge init'.

Xu ly: 1) Chuan bi .agent/ (tu vault, project, merge, hoac snapshot)
       2) Chay cac converter da chon
       3) Cai dat MCP config
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_bridge.core.converter import converter_registry
from agent_bridge.vault import VaultManager
from agent_bridge.vault.merger import MergeStrategy, merge_source_into_project


def run_init(
    project_path: Path,
    format_names: List[str],
    source_choice: str,
    force: bool = False,
    verbose: bool = True,
    snapshot_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Logic chinh cua init.

    Args:
        project_path: Duong dan project root
        format_names: Danh sach IDE (vd: ["cursor", "kiro"])
        source_choice: "project" | "vault" | "merge"
        force: Ghi de khong hoi
        verbose: In tien trinh

    Returns:
        Dict ket qua: {"error": ...} hoac {format_name: ConversionResult}
    """
    agent_dir = project_path / ".agent"
    source_root = project_path

    # Buoc 1: Xu ly nguon
    if source_choice == "snapshot" and snapshot_name:
        from agent_bridge.services.snapshot_service import get_snapshot_agent_dir

        snapshot_dir = get_snapshot_agent_dir(snapshot_name)
        if not snapshot_dir:
            return {"error": f"Snapshot '{snapshot_name}' not found"}
        merge_source_into_project(snapshot_dir, agent_dir, MergeStrategy.VAULT_ONLY)
    elif source_choice == "vault":
        _fetch_vault(agent_dir, overwrite=True)
    elif source_choice == "merge":
        _fetch_vault(agent_dir, overwrite=False)

    if not agent_dir.exists():
        return {"error": "No .agent/ directory available"}

    # Buoc 2: Chay converter
    results: Dict[str, Any] = {}
    for name in format_names:
        converter = converter_registry.get(name)
        if converter:
            result = converter.convert(
                source_root, project_path, verbose=verbose, force=force
            )
            converter.install_mcp(source_root, project_path, force=force)
            results[name] = result

    # Buoc 3: Ghi .bridge-meta.json de track generated files (cho capture)
    _write_bridge_meta(project_path, format_names)

    return results


def _write_bridge_meta(project_path: Path, format_names: List[str]) -> None:
    """Ghi .agent/.bridge-meta.json de track cac file da generate."""
    from datetime import datetime, timezone

    import json

    agent_dir = project_path / ".agent"
    if not agent_dir.exists():
        return

    file_map: Dict[str, str] = {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if "cursor" in format_names:
        cursor_root = project_path / ".cursor"
        if cursor_root.exists():
            agents_dir = cursor_root / "agents"
            if agents_dir.exists():
                for f in agents_dir.glob("*.md"):
                    file_map[f".cursor/agents/{f.name}"] = f".agent/agents/{f.name}"
            rules_dir = cursor_root / "rules"
            if rules_dir.exists():
                from agent_bridge.converters._cursor_impl import _parse_mdc_frontmatter

                for f in rules_dir.glob("*.mdc"):
                    if f.name == "project-instructions.mdc":
                        continue
                    try:
                        fm, _ = _parse_mdc_frontmatter(f.read_text(encoding="utf-8"))
                        always_apply = fm.get("alwaysApply", False)
                        globs = fm.get("globs", "").strip()
                        if always_apply and not globs:
                            file_map[f".cursor/rules/{f.name}"] = f".agent/rules/{f.stem}.md"
                        else:
                            file_map[f".cursor/rules/{f.name}"] = f".agent/skills/{f.stem}/SKILL.md"
                    except (OSError, TypeError):
                        file_map[f".cursor/rules/{f.name}"] = f".agent/skills/{f.stem}/SKILL.md"
            skills_dir = cursor_root / "skills"
            if skills_dir.exists():
                for d in skills_dir.iterdir():
                    if d.is_dir() and (d / "SKILL.md").exists():
                        file_map[f".cursor/skills/{d.name}/SKILL.md"] = f".agent/skills/{d.name}/SKILL.md"

    if "kiro" in format_names:
        kiro_root = project_path / ".kiro"
        if kiro_root.exists():
            agents_dir = kiro_root / "agents"
            if agents_dir.exists():
                for f in agents_dir.glob("*.json"):
                    file_map[f".kiro/agents/{f.name}"] = f".agent/agents/{f.stem}.md"
            skills_dir = kiro_root / "skills"
            if skills_dir.exists():
                for d in skills_dir.iterdir():
                    if d.is_dir() and (d / "SKILL.md").exists():
                        file_map[f".kiro/skills/{d.name}/SKILL.md"] = f".agent/skills/{d.name}/SKILL.md"
            prompts_dir = kiro_root / "prompts"
            if prompts_dir.exists():
                for f in prompts_dir.glob("*.md"):
                    file_map[f".kiro/prompts/{f.name}"] = f".agent/workflows/{f.name}"
            steering_dir = kiro_root / "steering"
            if steering_dir.exists():
                for f in steering_dir.glob("*.md"):
                    file_map[f".kiro/steering/{f.name}"] = f".agent/rules/{f.name}"
            if (kiro_root / "settings" / "mcp.json").exists():
                file_map[".kiro/settings/mcp.json"] = ".agent/mcp_config.json"

    if "copilot" in format_names:
        github_root = project_path / ".github"
        if github_root.exists():
            agents_dir = github_root / "agents"
            if agents_dir.exists():
                for f in agents_dir.glob("*.md"):
                    file_map[f".github/agents/{f.name}"] = f".agent/agents/{f.name}"
            skills_dir = github_root / "skills"
            if skills_dir.exists():
                for d in skills_dir.iterdir():
                    if d.is_dir() and (d / "SKILL.md").exists():
                        file_map[f".github/skills/{d.name}/SKILL.md"] = f".agent/skills/{d.name}/SKILL.md"
            prompts_dir = github_root / "prompts"
            if prompts_dir.exists():
                for f in prompts_dir.glob("*.prompt.md"):
                    stem = f.name.replace(".prompt.md", "")
                    file_map[f".github/prompts/{f.name}"] = f".agent/workflows/{stem}.md"
            instructions_dir = github_root / "instructions"
            if instructions_dir.exists():
                for f in instructions_dir.glob("*.instructions.md"):
                    stem = f.name.replace(".instructions.md", "")
                    file_map[f".github/instructions/{f.name}"] = f".agent/rules/{stem}.md"

    meta = {
        "generated_at": now,
        "generated_for": format_names,
        "file_map": file_map,
    }
    meta_path = agent_dir / ".bridge-meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _fetch_vault(agent_dir: Path, overwrite: bool) -> None:
    """Lay noi dung vault vao agent_dir."""
    vm = VaultManager()
    vault_source = _ensure_vault_synced(vm)
    if not vault_source:
        return

    if vault_source.resolve() == agent_dir.resolve():
        return

    strategy = MergeStrategy.VAULT_ONLY if overwrite else MergeStrategy.PROJECT_WINS
    merge_source_into_project(vault_source, agent_dir, strategy)


def _ensure_vault_synced(vm: VaultManager) -> Path | None:
    """Dam bao it nhat mot vault da sync, tra ve .agent/ dir."""
    agent_dir = vm.get_first_available_agent_dir()
    if agent_dir:
        return agent_dir

    vm.sync(verbose=True)
    return vm.get_first_available_agent_dir()
