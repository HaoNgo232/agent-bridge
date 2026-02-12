"""
Capture service — scan IDE configs va reverse-convert ve .agent/.

Luong: scan -> xac dinh status (modified/new/unchanged) -> execute capture -> ghi file.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent_bridge.core.types import CapturedFile
from agent_bridge.core.converter import converter_registry

# Chi ho tro 3 IDE: cursor, kiro, copilot
CAPTURE_IDES = ["cursor", "kiro", "copilot"]

BRIDGE_META_FILE = ".agent/.bridge-meta.json"


def _load_bridge_meta(project_path: Path) -> Optional[Dict[str, Any]]:
    """Doc .agent/.bridge-meta.json neu ton tai."""
    meta_path = project_path / BRIDGE_META_FILE
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _get_ide_mtime(path: Path) -> Optional[float]:
    """Lay mtime cua file. None neu khong ton tai."""
    try:
        return path.stat().st_mtime if path.exists() else None
    except OSError:
        return None


def _determine_status(
    captured: CapturedFile, meta: Optional[Dict[str, Any]], project_path: Path
) -> str:
    """
    Xac dinh status: modified | new | unchanged.

    - new: ide_path khong co trong meta.file_map
    - modified: ide_path trong meta va ide mtime > generated_at timestamp
    - unchanged: ide_path trong meta va khong modified
    """
    if not meta or "file_map" not in meta:
        return "new"

    file_map = meta.get("file_map", {})
    try:
        ide_str = str(captured.ide_path.relative_to(project_path)).replace("\\", "/")
    except ValueError:
        return "new"

    if ide_str not in file_map:
        return "new"

    ide_mtime = _get_ide_mtime(captured.ide_path)
    if ide_mtime is None:
        return "new"

    # So sanh voi generated_at timestamp thay vi agent file mtime
    generated_at_str = meta.get("generated_at")
    if generated_at_str:
        from datetime import datetime, timezone
        try:
            generated_ts = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00")).timestamp()
            if ide_mtime > generated_ts:
                return "modified"
        except (ValueError, OSError):
            pass

    return "unchanged"


def scan_for_captures(
    project_path: Path,
    ide_names: Optional[List[str]] = None,
) -> List[CapturedFile]:
    """
    Quet tat ca thu muc IDE, tra ve danh sach file co the capture voi status.

    Args:
        project_path: Duong dan project root
        ide_names: Chi quet cac IDE nay (None = tat ca)

    Returns:
        List CapturedFile voi status da cap nhat (modified/new/unchanged)
    """
    agent_dir = project_path / ".agent"
    ide_names = ide_names or CAPTURE_IDES
    meta = _load_bridge_meta(project_path)

    result: List[CapturedFile] = []

    for name in ide_names:
        converter = converter_registry.get(name)
        if not converter:
            continue
        try:
            files = converter.reverse_convert(project_path, agent_dir, verbose=False)
            for cf in files:
                cf.status = _determine_status(cf, meta, project_path)
                result.append(cf)
        except Exception:
            continue

    return result


def _get_apply_reverse(ide_name: str):
    """Lay apply_reverse function cho IDE."""
    if ide_name == "cursor":
        from agent_bridge.converters._cursor_impl import apply_reverse_capture_cursor
        return apply_reverse_capture_cursor
    if ide_name == "kiro":
        from agent_bridge.converters._kiro_impl import apply_reverse_capture_kiro
        return apply_reverse_capture_kiro
    if ide_name == "copilot":
        from agent_bridge.converters._copilot_impl import apply_reverse_capture_copilot
        return apply_reverse_capture_copilot
    return None


def execute_capture(
    project_path: Path,
    files: List[CapturedFile],
    strategy: str = "ask",
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Thuc hien capture: ghi cac file da chon vao .agent/.

    Args:
        project_path: Duong dan project root
        files: Danh sach CapturedFile da chon
        strategy: ide_wins | agent_wins | ask (ask khong dung trong non-interactive)
        dry_run: True = khong ghi, chi hien thi

    Returns:
        Dict voi counts: captured, skipped, errors
    """
    agent_dir = project_path / ".agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    counts = {"captured": 0, "skipped": 0, "errors": 0}

    if dry_run:
        return {"dry_run": True, "would_capture": len(files), **counts}

    for cf in files:
        # Strategy: agent_wins → skip if agent file exists and unchanged
        if strategy == "agent_wins":
            if cf.status == "unchanged":
                counts["skipped"] += 1
                continue
            agent_path = agent_dir / cf.agent_path.relative_to(project_path / ".agent") if cf.agent_path else None
            if agent_path and agent_path.exists():
                counts["skipped"] += 1
                continue

        apply_fn = _get_apply_reverse(cf.ide_name)
        if not apply_fn:
            counts["errors"] += 1
            continue
        try:
            ok = apply_fn(cf, project_path, agent_dir)
            if ok:
                counts["captured"] += 1
            else:
                counts["skipped"] += 1
        except Exception:
            counts["errors"] += 1

    return counts
