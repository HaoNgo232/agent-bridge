"""
Vault Management Module

Manages multiple agent/skill knowledge sources (vaults).
Supports: local directories, git repos, and registry.

Vault config stored in: ~/.config/agent-bridge/vaults.json
"""

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

VAULTS_CONFIG_DIR = Path.home() / ".config" / "agent-bridge"
VAULTS_CONFIG_FILE = VAULTS_CONFIG_DIR / "vaults.json"
VAULTS_CACHE_DIR = VAULTS_CONFIG_DIR / "cache"

# Default vault (backward compatible)
DEFAULT_VAULT = {
    "name": "antigravity-kit",
    "url": "https://github.com/vudovn/antigravity-kit",
    "description": "Core agent knowledge vault by Vudovn",
    "agent_subdir": ".agent",
    "enabled": True,
}


@dataclass
class Vault:
    """Represents a single vault source."""

    name: str
    url: str  # Git URL or local path
    description: str = ""
    agent_subdir: str = ".agent"  # Subdirectory within repo containing agents/skills
    enabled: bool = True
    priority: int = 100  # Lower = higher priority for merge conflicts

    @property
    def is_local(self) -> bool:
        return not self.url.startswith(("http://", "https://", "git@"))

    @property
    def cache_path(self) -> Path:
        return VAULTS_CACHE_DIR / self.name


class VaultManager:
    """Manages vault registry and synchronization."""

    def __init__(self):
        self._vaults: List[Vault] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load vaults from config file, or initialize with defaults."""
        if VAULTS_CONFIG_FILE.exists():
            try:
                data = json.loads(VAULTS_CONFIG_FILE.read_text(encoding="utf-8"))
                self._vaults = [Vault(**v) for v in data.get("vaults", [])]
            except (json.JSONDecodeError, TypeError, KeyError):
                self._vaults = [Vault(**DEFAULT_VAULT)]
        else:
            self._vaults = [Vault(**DEFAULT_VAULT)]

    def _save_config(self) -> None:
        """Persist vault config to disk."""
        VAULTS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {"vaults": [asdict(v) for v in self._vaults]}
        VAULTS_CONFIG_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @property
    def vaults(self) -> List[Vault]:
        return sorted(self._vaults, key=lambda v: v.priority)

    @property
    def enabled_vaults(self) -> List[Vault]:
        return [v for v in self.vaults if v.enabled]

    def add(self, name: str, url: str, description: str = "", priority: int = 100) -> Vault:
        """Register a new vault source."""
        # Check for duplicate names
        if any(v.name == name for v in self._vaults):
            raise ValueError(f"Vault '{name}' already exists. Use 'vault update' or remove first.")

        vault = Vault(
            name=name,
            url=url,
            description=description,
            priority=priority,
        )
        self._vaults.append(vault)
        self._save_config()
        return vault

    def remove(self, name: str) -> bool:
        """Unregister a vault and clean its cache."""
        vault = self.get(name)
        if not vault:
            return False

        self._vaults = [v for v in self._vaults if v.name != name]
        self._save_config()

        # Clean cache
        if vault.cache_path.exists():
            shutil.rmtree(vault.cache_path)

        return True

    def get(self, name: str) -> Optional[Vault]:
        """Get vault by name."""
        for v in self._vaults:
            if v.name == name:
                return v
        return None

    def sync(self, name: str = None, verbose: bool = True) -> Dict[str, Any]:
        """
        Sync one or all vaults from their sources.

        Returns dict with stats per vault.
        """
        results = {}
        targets = [self.get(name)] if name else self.enabled_vaults
        targets = [t for t in targets if t is not None]

        for vault in targets:
            if verbose:
                print(f"  Syncing vault: {vault.name} ...")

            if vault.is_local:
                results[vault.name] = self._sync_local(vault, verbose)
            else:
                results[vault.name] = self._sync_git(vault, verbose)

        return results

    def _sync_git(self, vault: Vault, verbose: bool) -> Dict[str, Any]:
        """Clone/pull a git-based vault into cache."""
        stats = {"status": "ok", "agents": 0, "skills": 0}
        cache_dir = vault.cache_path

        try:
            if cache_dir.exists() and (cache_dir / ".git").exists():
                # Pull latest
                subprocess.run(
                    ["git", "-C", str(cache_dir), "pull", "--ff-only"],
                    check=True,
                    capture_output=True,
                )
            else:
                # Fresh clone
                cache_dir.parent.mkdir(parents=True, exist_ok=True)
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                subprocess.run(
                    ["git", "clone", "--depth", "1", vault.url, str(cache_dir)],
                    check=True,
                    capture_output=True,
                )

            agent_dir = cache_dir / vault.agent_subdir
            if agent_dir.exists():
                agents_dir = agent_dir / "agents"
                skills_dir = agent_dir / "skills"
                stats["agents"] = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
                stats["skills"] = sum(1 for d in skills_dir.iterdir() if d.is_dir()) if skills_dir.exists() else 0

            if verbose:
                print(f"    OK: {stats['agents']} agents, {stats['skills']} skills")

        except subprocess.CalledProcessError as e:
            stats["status"] = f"error: {e.stderr.decode().strip()}"
            if verbose:
                print(f"    FAIL: {stats['status']}")
        except Exception as e:
            stats["status"] = f"error: {e}"

        return stats

    def _sync_local(self, vault: Vault, verbose: bool) -> Dict[str, Any]:
        """Validate a local vault path."""
        stats = {"status": "ok", "agents": 0, "skills": 0}
        local_path = Path(vault.url).resolve()
        agent_dir = local_path / vault.agent_subdir

        if not agent_dir.exists():
            stats["status"] = f"error: {agent_dir} not found"
        else:
            agents_dir = agent_dir / "agents"
            skills_dir = agent_dir / "skills"
            stats["agents"] = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0
            stats["skills"] = sum(1 for d in skills_dir.iterdir() if d.is_dir()) if skills_dir.exists() else 0

        if verbose:
            print(f"    Local: {stats['agents']} agents, {stats['skills']} skills")

        return stats

    def merge_to_project(self, project_agent_dir: Path, verbose: bool = True) -> Dict[str, int]:
        """
        Merge all enabled vaults into project's .agent/ directory.

        Priority: lower number wins on conflict.
        Project's own files always take highest priority (never overwritten).
        """
        counts = {"agents": 0, "skills": 0, "workflows": 0}

        for vault in self.enabled_vaults:
            if vault.is_local:
                source_root = Path(vault.url).resolve() / vault.agent_subdir
            else:
                source_root = vault.cache_path / vault.agent_subdir

            if not source_root.exists():
                if verbose:
                    print(f"  Skip {vault.name}: source not found (run 'agent-bridge vault sync' first)")
                continue

            for subdir in ["agents", "skills", "workflows"]:
                src = source_root / subdir
                dst = project_agent_dir / subdir
                if not src.exists():
                    continue

                dst.mkdir(parents=True, exist_ok=True)

                for item in src.iterdir():
                    dest_item = dst / item.name
                    # Never overwrite existing project files
                    if dest_item.exists():
                        continue

                    if item.is_dir():
                        shutil.copytree(item, dest_item)
                    else:
                        shutil.copy2(item, dest_item)

                    counts[subdir] = counts.get(subdir, 0) + 1

        if verbose:
            print(f"  Merged: {counts['agents']} agents, {counts['skills']} skills, {counts['workflows']} workflows")

        return counts

    def list_vaults(self) -> List[Dict[str, Any]]:
        """Return vault info for display."""
        result = []
        for v in self.vaults:
            info = asdict(v)
            info["cached"] = v.cache_path.exists() if not v.is_local else True
            result.append(info)
        return result
