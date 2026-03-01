"""
Local repository monitoring module

Scans the parent directory of the current working directory for local git
repositories owned by the current GitHub user, checks if they have pullable
changes (upstream commits not yet merged), and optionally auto-pulls them.

Inspired by cat-repo-auditor/github_local_checker.py.
"""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Optional

from .auto_updater import REPO_ROOT, restart_application
from .colors import Colors

# Status constants (same classification as cat-repo-auditor)
STATUS_PULLABLE = "pullable"  # behind > 0, ahead == 0, not dirty → can pull now
STATUS_DIVERGED = "diverged"  # behind > 0 and ahead > 0 → needs manual merge
STATUS_UP_TO_DATE = "up_to_date"  # behind == 0 → already latest
STATUS_UNKNOWN = "unknown"  # fetch failed or dirty with behind > 0

# Throttle repeated git-fetch cycles to avoid excessive network calls
LOCAL_REPO_CHECK_INTERVAL_SECONDS = 300  # 5 minutes

_last_local_check_time: float = 0.0


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
        rest = stripped[len("git@github.com:") :]
        return rest.startswith(f"{user_low}/")

    # HTTPS format: https://github.com/<user>/...
    for prefix in ("https://github.com/", "http://github.com/"):
        if stripped.startswith(prefix):
            rest = stripped[len(prefix) :]
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


def check_local_repos(config: dict, github_username: str) -> None:
    """Scan local repos in the base directory, display pullable ones, and optionally pull.

    By default (dry-run), pullable repos are displayed but not pulled.
    Set ``auto_git_pull = true`` in config.toml to enable auto-pull.

    Args:
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    global _last_local_check_time

    now = time.time()
    if _last_local_check_time and now - _last_local_check_time < LOCAL_REPO_CHECK_INTERVAL_SECONDS:
        return
    _last_local_check_time = now

    base_dir_str = config.get("local_repo_watcher_base_dir", None)
    if base_dir_str:
        base_dir = Path(base_dir_str)
    else:
        base_dir = Path.cwd().parent

    if not base_dir.exists() or not base_dir.is_dir():
        return

    enable_pull = config.get("auto_git_pull", False)

    # Collect candidate directories (siblings in the base dir)
    try:
        candidates = [str(d) for d in sorted(base_dir.iterdir()) if d.is_dir() and not d.name.startswith(".")]
    except PermissionError:
        return

    if not candidates:
        return

    # Check each candidate with live progress display (same style as wait countdown)
    total = len(candidates)
    results = []
    last_msg_len = 0
    for i, d in enumerate(candidates):
        repo_name = Path(d).name
        msg = f"[{i + 1}/{total}] リポジトリ確認中: {repo_name}..."
        print(f"\r{msg}     ", end="", flush=True)
        last_msg_len = len(msg) + 5
        results.append(_check_repo(d, github_username))
    if candidates:
        print(f"\r{' ' * last_msg_len}\r", end="", flush=True)
    target_results = [r for r in results if r["is_target"]]

    pullable = [r for r in target_results if r["status"] == STATUS_PULLABLE]
    diverged = [r for r in target_results if r["status"] == STATUS_DIVERGED]

    if not pullable and not diverged:
        return

    print(f"\n{'=' * 50}")
    print("ローカルリポジトリ状態:")
    print(f"{'=' * 50}")

    for r in pullable:
        detail = f"behind {r['behind']}"
        print(f"  {Colors.GREEN}[PULLABLE]{Colors.RESET} {r['name']}  ({detail})")
        if enable_pull:
            ok, msg = _pull_repo(r["path"])
            if ok:
                print(f"    ✓ pull 完了: {r['name']}")
                if Path(r["path"]).resolve() == REPO_ROOT:
                    print("    自分自身が更新されました。アプリケーションを再起動します...")
                    restart_application()
            else:
                print(f"    ✗ pull 失敗: {r['name']}: {msg}")
        else:
            print(f"    [DRY-RUN] Would pull {r['name']} (auto_git_pull=false)")

    for r in diverged:
        detail = f"behind {r['behind']}, ahead {r['ahead']}"
        print(f"  {Colors.YELLOW}[DIVERGED]{Colors.RESET} {r['name']}  ({detail}) ⚠ 手動マージが必要")
