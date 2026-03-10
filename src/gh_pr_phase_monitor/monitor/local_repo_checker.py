"""Repository status classification for local repository monitoring."""

from __future__ import annotations

from pathlib import Path

from .local_repo_git import (
    _fetch_remote,
    _get_behind_ahead,
    _get_current_branch,
    _get_remote_url,
    _is_dirty,
    _is_git_repo,
    _is_target_repo,
)

# Status constants (same classification as cat-repo-auditor)
STATUS_PULLABLE = "pullable"  # behind > 0, ahead == 0, not dirty → can pull now
STATUS_DIVERGED = "diverged"  # behind > 0 and ahead > 0 → needs manual merge
STATUS_UP_TO_DATE = "up_to_date"  # behind == 0 → already latest
STATUS_UNKNOWN = "unknown"  # fetch failed or dirty with behind > 0


def _check_repo(path: str, github_username: str) -> dict:
    """Fetch and classify a single repository.

    Returns a dict with keys:
        name, path, remote_url, branch, dirty, behind, ahead, status, error, is_target
    """
    p = Path(path)
    result: dict = {
        "name": p.name,
        "path": path,
        "remote_url": None,
        "branch": None,
        "dirty": False,
        "behind": None,
        "ahead": None,
        "status": STATUS_UNKNOWN,
        "error": None,
        "is_target": False,
    }

    if not _is_git_repo(path):
        return result

    remote_url = _get_remote_url(path)
    result["remote_url"] = remote_url
    if not remote_url:
        return result

    if not _is_target_repo(remote_url, github_username):
        return result

    result["is_target"] = True

    fetch_ok, fetch_err = _fetch_remote(path)
    if not fetch_ok:
        result["error"] = fetch_err
        return result

    branch = _get_current_branch(path)
    result["branch"] = branch
    if not branch:
        result["error"] = "ブランチ取得失敗"
        return result

    dirty = _is_dirty(path)
    result["dirty"] = dirty

    behind, ahead = _get_behind_ahead(path, branch)
    if behind == -1:
        result["error"] = f"origin/{branch} との比較失敗"
        return result

    result["behind"] = behind
    result["ahead"] = ahead

    # Classify status (same logic as cat-repo-auditor)
    if behind == 0:
        result["status"] = STATUS_UP_TO_DATE
    elif behind > 0 and ahead > 0:
        result["status"] = STATUS_DIVERGED
    elif behind > 0 and ahead == 0:
        if dirty:
            result["status"] = STATUS_UNKNOWN  # want to pull but dirty
        else:
            result["status"] = STATUS_PULLABLE
    else:
        # Fallback for any unexpected combination not covered above
        # (e.g. if _get_behind_ahead returns values outside [0, +inf)).
        # Treat conservatively as unknown rather than risking incorrect action.
        result["status"] = STATUS_UNKNOWN

    return result
