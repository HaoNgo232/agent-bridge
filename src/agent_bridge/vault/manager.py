"""
VaultManager — registry + sync orchestration.
Moved from vault.py with source abstraction integration.
"""

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .sources import BuiltinSource, GitSource, LocalSource
from .merger import merge_source_into_project, MergeStrategy, MERGE_SUBDIRS

VAULTS_CONFIG_DIR = Path.home() / ".config" / "agent-bridge"
VAULTS_CONFIG_FILE = VAULTS_CONFIG_DIR / "vaults.json"
VAULTS_CACHE_DIR = VAULTS_CONFIG_DIR / "cache"

DEFAULT_VAULT = {
    "name": "builtin-starter",
    "url": "__builtin__",
    "description": "Minimal starter vault shipped with Agent Bridge",
    "agent_subdir": ".agent",
    "enabled": True,
    "priority": 999,
}


@dataclass
class Vault:
    name: str
    url: str
    description: str = ""
    agent_subdir: str = ".agent"
    enabled: bool = True
    priority: int = 100

    @property
    def is_local(self) -> bool:
        return not self.url.startswith(("http://", "https://", "git@", "__builtin__"))

    @property
    def is_builtin(self) -> bool:
        return self.url == "__builtin__"

    @property
    def cache_path(self) -> Path:
        return VAULTS_CACHE_DIR / self.name

    def get_source(self):
        if self.is_builtin:
            return BuiltinSource()
        if self.is_local:
            return LocalSource(self.url)
        return GitSource(self.url)


class VaultManager:
    def __init__(self):
        self._vaults: List[Vault] = []
        self._load_config()

    def _load_config(self) -> None:
        if VAULTS_CONFIG_FILE.exists():
            try:
                data = json.loads(VAULTS_CONFIG_FILE.read_text(encoding="utf-8"))
                self._vaults = [Vault(**v) for v in data.get("vaults", [])]
            except (json.JSONDecodeError, TypeError, KeyError):
                self._vaults = [Vault(**DEFAULT_VAULT)]
        else:
            self._vaults = [Vault(**DEFAULT_VAULT)]

    def _save_config(self) -> None:
        VAULTS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {"vaults": [asdict(v) for v in self._vaults]}
        VAULTS_CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @property
    def vaults(self) -> List[Vault]:
        return sorted(self._vaults, key=lambda v: v.priority)

    @property
    def enabled_vaults(self) -> List[Vault]:
        return [v for v in self.vaults if v.enabled]

    def add(self, name: str, url: str, description: str = "", priority: int = 100) -> Vault:
        if any(v.name == name for v in self._vaults):
            raise ValueError(f"Vault '{name}' already exists. Remove it first.")
        vault = Vault(name=name, url=url, description=description, priority=priority)
        self._vaults.append(vault)
        self._save_config()
        return vault

    def remove(self, name: str) -> bool:
        vault = self.get(name)
        if not vault:
            return False
        self._vaults = [v for v in self._vaults if v.name != name]
        self._save_config()
        if vault.cache_path.exists():
            shutil.rmtree(vault.cache_path)
        return True

    def get(self, name: str) -> Optional[Vault]:
        for v in self._vaults:
            if v.name == name:
                return v
        return None

    def sync(self, name: str = None, verbose: bool = True) -> Dict[str, Any]:
        results = {}
        targets = [self.get(name)] if name else self.enabled_vaults
        targets = [t for t in targets if t is not None]

        for vault in targets:
            if verbose:
                print(f"  Syncing vault: {vault.name} ...")
            source = vault.get_source()
            results[vault.name] = source.sync(vault.cache_path, verbose)

        return results

    def get_vault_agent_dir(self, vault: Vault) -> Optional[Path]:
        """Get the .agent/ directory for a vault (cached or local)."""
        if vault.is_local:
            candidate = Path(vault.url).resolve() / vault.agent_subdir
        else:
            candidate = vault.cache_path / vault.agent_subdir
        return candidate if candidate.exists() else None

    def get_first_available_agent_dir(self) -> Optional[Path]:
        """Get agent dir from highest-priority vault that has content."""
        for vault in self.enabled_vaults:
            agent_dir = self.get_vault_agent_dir(vault)
            if agent_dir:
                return agent_dir
        return None

    def merge_to_project(self, project_agent_dir: Path, verbose: bool = True) -> Dict[str, int]:
        total: Dict[str, int] = {}
        for vault in self.enabled_vaults:
            source_root = self.get_vault_agent_dir(vault)
            if not source_root:
                if verbose:
                    print(f"  Skip {vault.name}: not synced")
                continue
            counts = merge_source_into_project(source_root, project_agent_dir, MergeStrategy.PROJECT_WINS)
            for key, val in counts.items():
                total[key] = total.get(key, 0) + val
        if verbose:
            print(f"  Merged: {total.get('agents', 0)} agents, {total.get('skills', 0)} skills, {total.get('workflows', 0)} workflows")
        return total

    def list_vaults(self) -> List[Dict[str, Any]]:
        result = []
        for v in self.vaults:
            info = asdict(v)
            info["cached"] = v.cache_path.exists() if not v.is_local else True
            result.append(info)
        return result