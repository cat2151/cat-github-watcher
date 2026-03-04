"""
Path and naming utilities for PR phase snapshots.
"""

import re
from datetime import datetime
from typing import Any, Optional


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


def _build_snapshot_dir_name(pr: dict) -> str:
    """Build snapshot directory name like owner_repo_PR123 (no timestamp)."""
    repo_info = pr.get("repository") or {}
    owner = _sanitize_component(repo_info.get("owner", "unknown"))
    name = _sanitize_component(repo_info.get("name", "unknown"))
    pr_number = _extract_pr_number(pr.get("url", ""))
    return f"{owner}_{name}_PR{pr_number}"
