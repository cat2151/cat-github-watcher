"""
Utilities for capturing PR snapshots to aid debugging of phase detection.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .phase_detector import PHASE_LLM_WORKING, has_comments_with_reactions

# Snapshots are stored next to existing screenshots for easy discovery
DEFAULT_SNAPSHOT_BASE_DIR = Path("screenshots") / "pr_phase_snapshots"
_recorded_snapshots: Set[str] = set()


def _sanitize_component(value: Any) -> str:
    """Sanitize a path component by replacing unsafe characters."""
    text = str(value) if value is not None else "unknown"
    text = text.strip() or "unknown"
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)


def _extract_pr_number(pr_url: str) -> str:
    """Extract PR number from URL if possible."""
    match = re.search(r"/pull/(\d+)", pr_url or "")
    if match:
        return match.group(1)
    return "unknown"


def _format_timestamp(current_time: Optional[datetime] = None) -> str:
    """Format timestamp for filenames."""
    return (current_time or datetime.now()).strftime("%Y%m%d_%H%M%S")


def _build_snapshot_prefix(pr: Dict[str, Any], current_time: Optional[datetime]) -> str:
    """Build snapshot prefix like owner_repo_PR123_20260102_030405."""
    repo_info = pr.get("repository") or {}
    owner = _sanitize_component(repo_info.get("owner", "unknown"))
    name = _sanitize_component(repo_info.get("name", "unknown"))
    pr_number = _extract_pr_number(pr.get("url", ""))
    timestamp_str = _format_timestamp(current_time)
    return f"{owner}_{name}_PR{pr_number}_{timestamp_str}"


def _summarize_reactions(comment_nodes: Any) -> List[str]:
    """Return human-readable summaries of reaction groups."""
    summaries: List[str] = []
    if not isinstance(comment_nodes, list):
        return summaries

    for idx, comment in enumerate(comment_nodes, start=1):
        for group in comment.get("reactionGroups") or []:
            count = (group.get("users") or {}).get("totalCount", 0)
            if count:
                content = group.get("content", "UNKNOWN")
                summaries.append(f"Comment {idx}: {content} x{count}")

    return summaries


def _summarize_review_threads(review_threads: Any) -> str:
    """Summarize unresolved review threads."""
    if not isinstance(review_threads, list):
        return "n/a"

    unresolved = sum(
        1 for thread in review_threads if not thread.get("isResolved", False) and not thread.get("isOutdated", False)
    )
    return f"{unresolved} unresolved"


def _build_markdown(
    pr: Dict[str, Any], reason: str, timestamp_str: str, reactions_summary: List[str], snapshot_prefix: str
) -> str:
    """Build human-readable markdown representation of the snapshot."""
    repo_info = pr.get("repository") or {}
    owner = repo_info.get("owner", "unknown")
    name = repo_info.get("name", "unknown")
    url = pr.get("url", "unknown")
    pr_number = _extract_pr_number(url)
    title = pr.get("title", "")
    author = (pr.get("author") or {}).get("login", "unknown")
    reviews = pr.get("reviews") or []
    latest_review = reviews[-1] if reviews else {}
    review_threads = pr.get("reviewThreads")

    lines = [
        f"# PR snapshot {owner}/{name} #{pr_number}",
        "",
        f"- Timestamp: {timestamp_str}",
        f"- Snapshot prefix: {snapshot_prefix}",
        f"- URL: {url}",
        f"- Title: {title}",
        f"- Author: {author}",
        f"- Phase decision: {PHASE_LLM_WORKING}",
        f"- Reason: {reason}",
        "",
        "## Reviews",
        f"- Review count: {len(reviews)}",
        f"- Latest review state: {latest_review.get('state', 'unknown') or 'unknown'}",
        "",
        "## Review threads",
        f"- { _summarize_review_threads(review_threads) }",
        "",
        "## Comment reactions",
    ]

    if reactions_summary:
        lines.extend(f"- {item}" for item in reactions_summary)
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Raw snapshot")
    lines.append(f"- Saved at: {timestamp_str}")

    return "\n".join(lines)


def save_pr_snapshot(
    pr: Dict[str, Any],
    reason: str,
    base_dir: Optional[Path] = None,
    current_time: Optional[datetime] = None,
) -> Dict[str, Path]:
    """Save raw PR data and markdown summary to disk.

    Args:
        pr: PR data dictionary.
        reason: Reason for capturing the snapshot.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.

    Returns:
        Paths for the saved snapshot directory and files.
    """
    effective_time = current_time if current_time is not None else datetime.now()

    base_path = Path(base_dir) if base_dir is not None else DEFAULT_SNAPSHOT_BASE_DIR
    base_path = base_path.expanduser().resolve()

    snapshot_prefix = _build_snapshot_prefix(pr, effective_time)
    snapshot_dir = base_path / snapshot_prefix
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    raw_path = snapshot_dir / f"{snapshot_prefix}_raw.json"
    markdown_path = snapshot_dir / f"{snapshot_prefix}_summary.md"
    timestamp_str = _format_timestamp(effective_time)
    reactions_summary = _summarize_reactions(pr.get("commentNodes", pr.get("comments", [])))

    with raw_path.open("w", encoding="utf-8") as raw_file:
        json.dump(pr, raw_file, ensure_ascii=False, indent=2)

    markdown_content = _build_markdown(pr, reason, timestamp_str, reactions_summary, snapshot_prefix)
    markdown_path.write_text(markdown_content, encoding="utf-8")

    return {
        "snapshot_dir": snapshot_dir,
        "raw_path": raw_path,
        "markdown_path": markdown_path,
    }


def record_reaction_snapshot(
    pr: Dict[str, Any],
    phase: str,
    base_dir: Optional[Path] = None,
    current_time: Optional[datetime] = None,
) -> Optional[Dict[str, Path]]:
    """Record a snapshot when comment reactions force LLM working detection.

    Args:
        pr: PR data dictionary.
        phase: Detected phase for the PR.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.

    Returns:
        Paths for created snapshot files, or None when no snapshot is recorded.
    """
    if phase != PHASE_LLM_WORKING:
        return None

    comment_nodes = pr.get("commentNodes", pr.get("comments", []))
    if not has_comments_with_reactions(comment_nodes):
        return None

    pr_key = pr.get("url") or _build_snapshot_prefix(pr, current_time)
    if pr_key in _recorded_snapshots:
        return None

    snapshot_paths = save_pr_snapshot(
        pr,
        reason="comment_reactions_detected",
        base_dir=base_dir,
        current_time=current_time,
    )
    _recorded_snapshots.add(pr_key)
    return snapshot_paths


def _reset_snapshot_cache() -> None:
    """Test helper to clear recorded snapshot cache."""
    _recorded_snapshots.clear()
