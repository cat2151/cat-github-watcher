"""Git subprocess primitives for local repository monitoring."""

from __future__ import annotations

import os
import subprocess
from typing import Optional


def _run_git(args: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"  # Prevent credential prompts from blocking
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        env=env,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _is_git_repo(path: str) -> bool:
    """Return True if the directory is a git repository."""
    rc, _, _ = _run_git(["rev-parse", "--git-dir"], path)
    return rc == 0


def _get_remote_url(path: str) -> Optional[str]:
    """Return the URL of the 'origin' remote, or None."""
    rc, out, _ = _run_git(["remote", "get-url", "origin"], path)
    return out if rc == 0 and out else None


def _is_target_repo(remote_url: str, github_username: str) -> bool:
    """Return True if the remote URL belongs to the given GitHub user.

    Supports both HTTPS (https://github.com/<user>/...)
    and SSH (git@github.com:<user>/...) URL formats.
    Uses strict host matching to avoid false positives from URLs like
    'github.com.evil.com' or 'notgithub.com'.
    """
    user_low = github_username.lower()
    stripped = remote_url.strip().lower()

    # SSH format: git@github.com:<user>/...
    if stripped.startswith("git@github.com:"):
        rest = stripped[len("git@github.com:"):]
        return rest.startswith(f"{user_low}/")

    # HTTPS format: https://github.com/<user>/...
    for prefix in ("https://github.com/", "http://github.com/"):
        if stripped.startswith(prefix):
            rest = stripped[len(prefix):]
            return rest.startswith(f"{user_low}/")

    return False


def _is_dirty(path: str) -> bool:
    """Return True if the working tree has uncommitted changes."""
    rc, out, _ = _run_git(["status", "--porcelain"], path)
    return bool(out) if rc == 0 else True


def _get_current_branch(path: str) -> Optional[str]:
    """Return the current branch name, or None on failure."""
    rc, out, _ = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
    return out if rc == 0 else None


def _fetch_remote(path: str) -> tuple[bool, Optional[str]]:
    """Fetch from origin. Returns (success, error_message_or_None)."""
    rc, _, err = _run_git(["fetch", "origin", "--quiet"], path)
    if rc != 0:
        msg = f"git fetch 失敗: {err}" if err else "git fetch 失敗"
        return False, msg
    return True, None


def _get_behind_ahead(path: str, branch: str) -> tuple[int, int]:
    """Return (behind, ahead) relative to origin/<branch>, or (-1, -1) on failure."""
    tracking = f"origin/{branch}"
    rc, out, _ = _run_git(
        ["rev-list", "--left-right", "--count", f"{tracking}...HEAD"],
        path,
    )
    if rc != 0:
        return -1, -1
    parts = out.split()
    if len(parts) != 2:
        return -1, -1
    return int(parts[0]), int(parts[1])


def _pull_repo(path: str) -> tuple[bool, str]:
    """Execute git pull --ff-only. Returns (success, message).

    Should only be called for repos classified as pullable
    (dirty=False, ahead==0, behind>0).
    """
    rc, out, err = _run_git(["pull", "--ff-only"], path)
    if rc != 0:
        return False, err or "git pull 失敗"
    return True, out or "Already up to date."
