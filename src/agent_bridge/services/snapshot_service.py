"""
Snapshot CRUD service — luu, list, xoa, lay thong tin snapshot.

Snapshot luu tai ~/.config/agent-bridge/snapshots/<name>/
  - manifest.json: metadata
  - .agent/: full copy of .agent/ directory
"""

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_bridge.core.types import SnapshotInfo
from agent_bridge.vault.manager import VAULTS_CONFIG_DIR

SNAPSHOTS_DIR = VAULTS_CONFIG_DIR / "snapshots"

# Subdirectories trong .agent/ de build manifest contents
AGENT_SUBDIRS = ["agents", "skills", "workflows", "rules"]


def _collect_contents(agent_dir: Path) -> Dict[str, List[str]]:
    """
    Thu thap danh sach file/dir trong .agent/ de ghi vao manifest.contents.

    Returns:
        Dict voi keys: agents, skills, workflows, rules; values la list ten (stem/name)
    """
    contents: Dict[str, List[str]] = {
        "agents": [],
        "skills": [],
        "workflows": [],
        "rules": [],
    }
    for subdir in AGENT_SUBDIRS:
        src = agent_dir / subdir
        if not src.exists():
            continue
        if subdir == "skills":
            contents[subdir] = [d.name for d in src.iterdir() if d.is_dir()]
        else:
            contents[subdir] = [f.stem for f in src.glob("*.md")]
    return contents


def _load_manifest(snapshot_path: Path) -> Optional[Dict[str, Any]]:
    """Doc manifest.json. Tra ve None neu loi."""
    manifest_file = snapshot_path / "manifest.json"
    if not manifest_file.exists():
        return None
    try:
        return json.loads(manifest_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_snapshot(
    name: str,
    agent_dir: Path,
    description: str = "",
    tags: Optional[Dict[str, list]] = None,
) -> SnapshotInfo:
    """
    Copy .agent/ vao snapshots dir voi manifest.

    Neu ten da ton tai: tang version, update timestamp, replace content.

    Args:
        name: Ten snapshot (slug, unique)
        agent_dir: Duong dan den .agent/ cua project
        description: Mo ta snapshot
        tags: Dict tags (vd: {"frameworks": ["flutter"], "languages": ["dart"]})

    Returns:
        SnapshotInfo cua snapshot vua luu
    """
    tags = tags or {}
    normalized_name = _normalize_snapshot_name(name)
    snapshot_path = SNAPSHOTS_DIR / normalized_name
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    contents = _collect_contents(agent_dir)

    existing = _load_manifest(snapshot_path)
    if existing:
        version = existing.get("version", 1) + 1
        created = existing.get("created", now)
    else:
        version = 1
        created = now

    if snapshot_path.exists():
        shutil.rmtree(snapshot_path, ignore_errors=True)
    snapshot_path.mkdir(parents=True, exist_ok=True)
    agent_dest = snapshot_path / ".agent"
    shutil.copytree(agent_dir, agent_dest)

    manifest = {
        "name": normalized_name,
        "description": description,
        "created": created,
        "updated": now,
        "version": version,
        "source": {
            "project": str(agent_dir.parent),
            "ides_captured_from": [],
        },
        "contents": contents,
        "tags": tags,
    }
    (snapshot_path / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return SnapshotInfo(
        name=normalized_name,
        description=description,
        created=created,
        updated=now,
        version=version,
        contents=contents,
        path=snapshot_path,
        tags=tags,
    )


def _normalize_snapshot_name(name: str) -> str:
    """Chuan hoa ten snapshot: lowercase, thay khoang trang/filename unsafe bang hyphen."""
    return re.sub(r"[^a-z0-9_-]", "-", name.lower().strip()).strip("-") or "unnamed"


def list_snapshots() -> List[SnapshotInfo]:
    """
    Liet ke tat ca snapshot, sap xep theo ngay tao (moi nhat truoc).

    Returns:
        List SnapshotInfo, newest first
    """
    if not SNAPSHOTS_DIR.exists():
        return []
    result: List[SnapshotInfo] = []
    for item in SNAPSHOTS_DIR.iterdir():
        if item.is_dir():
            info = get_snapshot(item.name)
            if info:
                result.append(info)
    result.sort(key=lambda s: s.created, reverse=True)
    return result


def get_snapshot(name: str) -> Optional[SnapshotInfo]:
    """
    Lay thong tin snapshot theo ten.

    Returns:
        SnapshotInfo hoac None neu khong ton tai
    """
    normalized = _normalize_snapshot_name(name)
    snapshot_path = SNAPSHOTS_DIR / normalized
    manifest = _load_manifest(snapshot_path)
    if not manifest:
        return None
    return SnapshotInfo(
        name=manifest.get("name", normalized),
        description=manifest.get("description", ""),
        created=manifest.get("created", ""),
        updated=manifest.get("updated", ""),
        version=manifest.get("version", 1),
        contents=manifest.get("contents", {}),
        path=snapshot_path,
        tags=manifest.get("tags", {}),
    )


def delete_snapshot(name: str) -> bool:
    """
    Xoa snapshot.

    Returns:
        True neu thanh cong, False neu khong ton tai
    """
    normalized = _normalize_snapshot_name(name)
    snapshot_path = SNAPSHOTS_DIR / normalized
    if not snapshot_path.exists():
        return False
    shutil.rmtree(snapshot_path)
    return True


def get_snapshot_agent_dir(name: str) -> Optional[Path]:
    """
    Tra ve duong dan den .agent/ trong snapshot.

    Dung cho init --from snapshot va merger.

    Returns:
        Path den .agent/ hoac None neu khong ton tai
    """
    info = get_snapshot(name)
    if not info:
        return None
    agent_dir = info.path / ".agent"
    return agent_dir if agent_dir.exists() else None


def restore_snapshot(agent_dir: Path, name: str) -> bool:
    """
    Restore .agent/ directory tu snapshot.

    Ghi de toan bo noi dung agent_dir voi noi dung snapshot.

    Args:
        agent_dir: Duong dan den .agent/ cua project (target)
        name: Ten snapshot

    Returns:
        True neu thanh cong, False neu snapshot khong ton tai
    """
    snapshot_agent = get_snapshot_agent_dir(name)
    if not snapshot_agent:
        return False
    if agent_dir.exists():
        shutil.rmtree(agent_dir)
    shutil.copytree(snapshot_agent, agent_dir)
    return True
