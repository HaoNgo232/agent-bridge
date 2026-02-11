"""
Vault source strategies (Strategy pattern).
Each source knows how to sync/validate itself.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import subprocess
from typing import Dict, Any


class VaultSource(ABC):
    @abstractmethod
    def sync(self, cache_dir: Path, verbose: bool = True) -> Dict[str, Any]: ...

    @abstractmethod
    def validate(self) -> bool: ...

    @staticmethod
    def _count_content(agent_dir: Path) -> Dict[str, int]:
        agents_dir = agent_dir / "agents"
        skills_dir = agent_dir / "skills"
        return {
            "agents": len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0,
            "skills": sum(1 for d in skills_dir.iterdir() if d.is_dir()) if skills_dir.exists() else 0,
        }


class GitSource(VaultSource):
    def __init__(self, url: str):
        self.url = url

    def sync(self, cache_dir: Path, verbose: bool = True) -> Dict[str, Any]:
        stats: Dict[str, Any] = {"status": "ok", "agents": 0, "skills": 0}
        try:
            if cache_dir.exists() and (cache_dir / ".git").exists():
                subprocess.run(["git", "-C", str(cache_dir), "pull", "--ff-only"], check=True, capture_output=True)
            else:
                cache_dir.parent.mkdir(parents=True, exist_ok=True)
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                subprocess.run(["git", "clone", "--depth", "1", self.url, str(cache_dir)], check=True, capture_output=True)

            for subdir_name in [".agent", "."]:
                agent_dir = cache_dir / subdir_name
                if (agent_dir / "agents").exists() or (agent_dir / "skills").exists():
                    stats.update(self._count_content(agent_dir))
                    break
        except subprocess.CalledProcessError as e:
            stats["status"] = f"error: {e.stderr.decode().strip()}"
        except Exception as e:
            stats["status"] = f"error: {e}"
        return stats

    def validate(self) -> bool:
        try:
            result = subprocess.run(["git", "ls-remote", "--exit-code", self.url], capture_output=True, timeout=15)
            return result.returncode == 0
        except Exception:
            return False


class LocalSource(VaultSource):
    def __init__(self, path: str):
        self.path = Path(path).resolve()

    def sync(self, cache_dir: Path, verbose: bool = True) -> Dict[str, Any]:
        stats: Dict[str, Any] = {"status": "ok", "agents": 0, "skills": 0}
        agent_dir = self.path / ".agent"
        if not agent_dir.exists():
            if (self.path / "agents").exists():
                agent_dir = self.path
            else:
                stats["status"] = f"error: {agent_dir} not found"
                return stats
        stats.update(self._count_content(agent_dir))
        return stats

    def validate(self) -> bool:
        return self.path.exists()


class BuiltinSource(VaultSource):
    """Built-in starter vault shipped with the package — no external deps."""

    def __init__(self):
        self.source_dir = Path(__file__).parent.parent / "builtin_vault"

    def sync(self, cache_dir: Path, verbose: bool = True) -> Dict[str, Any]:
        stats: Dict[str, Any] = {"status": "ok", "agents": 0, "skills": 0}
        if not self.source_dir.exists():
            stats["status"] = "error: builtin vault not found in package"
            return stats
        try:
            cache_dir.parent.mkdir(parents=True, exist_ok=True)
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
            shutil.copytree(self.source_dir, cache_dir)
            agent_dir = cache_dir / ".agent" if (cache_dir / ".agent").exists() else cache_dir
            stats.update(self._count_content(agent_dir))
        except Exception as e:
            stats["status"] = f"error: {e}"
        return stats

    def validate(self) -> bool:
        return self.source_dir.exists()