"""Self-update utility using gh CLI and git."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Tuple

from ..core.colors import Colors

UPDATE_CHECK_INTERVAL_SECONDS = 60
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

_last_check_time: float = 0.0
_update_lock = threading.Lock()
_REMOTE_PATTERN = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")


def _debug_self_update_log(message: str) -> None:
    """Print debug-only startup/update diagnostics with a human-readable timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[auto-update debug {timestamp}] {message}", flush=True)


def _format_command(args: list[str]) -> str:
    """Format a command for human-readable debug logging."""
    return " ".join(shlex.quote(arg) for arg in args)


def _compact_output(value: str) -> str:
    """Convert command output to a single-line debug-friendly string."""
    stripped = value.strip()
    return stripped.replace("\n", "\\n") if stripped else "-"


def _sha_lookup_status(returncode: int, sha: str | None) -> str:
    """Classify the result of a SHA lookup for debug logs."""
    if returncode != 0:
        return "command_failed"
    if not sha:
        return "empty_response"
    return "success"


def _is_rate_limit_error(*messages: str) -> bool:
    """Detect likely API rate limit failures from command output."""
    combined = " ".join(messages).lower()
    return "rate limit" in combined or "secondary rate limit" in combined


def _run_command(args: list[str], cwd: Path | str | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and return the completed process without raising on error."""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        check=False,
    )


def _parse_remote_url(remote_url: str) -> Optional[Tuple[str, str]]:
    """Parse a GitHub remote URL into (owner, repo)."""
    match = _REMOTE_PATTERN.search(remote_url.strip())
    if not match:
        return None
    return match.group("owner"), match.group("repo")


def _get_tracking_branch(repo_root: Path) -> Optional[Tuple[str, str]]:
    """Return (remote, branch) for the current upstream if configured."""
    result = _run_command(["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if result.returncode != 0:
        return None

    ref = result.stdout.strip()
    if "/" not in ref:
        return None
    remote, branch = ref.split("/", 1)
    if not remote or not branch:
        return None
    return remote, branch


def _get_remote_repo(repo_root: Path, remote_name: str) -> Optional[Tuple[str, str]]:
    """Return (owner, repo) for the given remote using its URL."""
    result = _run_command(["git", "-C", str(repo_root), "remote", "get-url", remote_name])
    if result.returncode != 0:
        return None
    parsed = _parse_remote_url(result.stdout)
    return parsed


def _get_local_head_sha(repo_root: Path, phase: str = "current") -> Optional[str]:
    """Return the current HEAD SHA."""
    args = ["git", "-C", str(repo_root), "rev-parse", "HEAD"]
    result = _run_command(args)
    sha = result.stdout.strip() or None if result.returncode == 0 else None
    _debug_self_update_log(
        "local hash取得 "
        f"phase={phase} result={_sha_lookup_status(result.returncode, sha)} "
        f"working_dir={repo_root} source=git command={_format_command(args)} "
        f"returncode={result.returncode} hash={sha or '-'} "
        f"stdout={_compact_output(result.stdout)} stderr={_compact_output(result.stderr)}"
    )
    return sha


def _get_remote_latest_sha(owner: str, repo: str, branch: str, cwd: Path, phase: str = "current") -> Optional[str]:
    """Fetch the latest SHA for the remote branch via gh api."""
    endpoint = f"repos/{owner}/{repo}/branches/{branch}"
    args = ["gh", "api", endpoint, "--jq", ".commit.sha"]
    result = _run_command(args, cwd=cwd)
    sha = result.stdout.strip()
    resolved_sha = sha if result.returncode == 0 and sha and sha != "null" else None
    _debug_self_update_log(
        "remote hash取得 "
        f"phase={phase} result={_sha_lookup_status(result.returncode, resolved_sha)} "
        f"working_dir={cwd} source=gh-api endpoint={endpoint} jq=.commit.sha "
        f"command={_format_command(args)} returncode={result.returncode} "
        f"hash={resolved_sha or '-'} rate_limit_detected={'yes' if _is_rate_limit_error(result.stderr, result.stdout) else 'no'} "
        f"stdout={_compact_output(result.stdout)} stderr={_compact_output(result.stderr)}"
    )
    return resolved_sha


def _is_worktree_clean(repo_root: Path) -> bool:
    """Check if the worktree has no local modifications."""
    result = _run_command(["git", "-C", str(repo_root), "status", "--porcelain"])
    return result.returncode == 0 and not result.stdout.strip()


def _pull_fast_forward(repo_root: Path, remote_name: str, branch: str) -> bool:
    """Attempt a fast-forward pull; return True on success."""
    args = ["git", "-C", str(repo_root), "pull", "--ff-only", remote_name, branch]
    result = _run_command(args)
    _debug_self_update_log(
        "git pull実行結果 "
        f"working_dir={repo_root} source=git command={_format_command(args)} "
        f"returncode={result.returncode} stdout={_compact_output(result.stdout)} stderr={_compact_output(result.stderr)}"
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        print(f"Auto-update skipped: git pull failed ({message}).")
        return False
    return True


def restart_application() -> None:
    """Restart the current Python process with the same arguments."""
    os.chdir(REPO_ROOT)
    os.execv(sys.executable, [sys.executable] + sys.argv)


def maybe_self_update(repo_root: Path | None = None) -> bool:
    """Check for repository updates and restart the app if new commits are available."""
    global _last_check_time

    # ロック取得前に簡易チェックしてロック競合を最小化
    now = time.time()
    if _last_check_time and now - _last_check_time < UPDATE_CHECK_INTERVAL_SECONDS:
        return False

    with _update_lock:
        # 別スレッドがロック待ち中に実行した可能性があるため再チェック
        now = time.time()
        if _last_check_time and now - _last_check_time < UPDATE_CHECK_INTERVAL_SECONDS:
            return False
        _last_check_time = now

        repo_root = repo_root or REPO_ROOT
        tracking = _get_tracking_branch(repo_root)
        if not tracking:
            return False
        remote_name, branch = tracking

        remote_repo = _get_remote_repo(repo_root, remote_name)
        if not remote_repo:
            return False
        owner, repo = remote_repo

        local_sha = _get_local_head_sha(repo_root, phase="before-pull")
        if not local_sha:
            return False

        remote_sha = _get_remote_latest_sha(owner, repo, branch, repo_root, phase="before-pull")
        if not remote_sha or remote_sha == local_sha:
            return False

        _debug_self_update_log(
            "update検知した "
            f"local_hash={local_sha} remote_hash={remote_sha} branch={remote_name}/{branch} "
            "local_source=git_rev_parse_HEAD remote_source=gh_api_branches_endpoint"
        )

        if not _is_worktree_clean(repo_root):
            print("Auto-update skipped: local changes detected.")
            return False

        if not _pull_fast_forward(repo_root, remote_name, branch):
            return False

        updated_local_sha = _get_local_head_sha(repo_root, phase="after-pull")
        _debug_self_update_log(
            f"pullした remote={remote_name} branch={branch} local_hash_after_pull={updated_local_sha or '-'}"
        )
        print(f"{Colors.GREEN}Auto-update: update detected! Restarting application to apply the latest code...{Colors.RESET}", flush=True)
        _debug_self_update_log(
            f"再起動する local_hash_before_pull={local_sha} remote_hash_before_pull={remote_sha} "
            f"local_hash_after_pull={updated_local_sha or '-'}"
        )
        restart_application()
        return True


def run_startup_self_update_foreground(repo_root: Path | None = None) -> None:
    """起動時の自動アップデートをメインスレッドで明示的にprintしながら実行する。

    ユーザーが起動直後にアップデートの状況を把握できるよう、主要なステップを標準出力に出力する。
    更新が見つかった場合は maybe_self_update() 内でアプリを再起動する。
    """
    _debug_self_update_log("起動した")
    print("Auto-update: checking for updates...", flush=True)
    try:
        updated = maybe_self_update(repo_root=repo_root)
        if not updated:
            print("Auto-update: check complete (no update applied).", flush=True)
    except Exception as e:
        print(f"Auto-update: check failed: {e}", flush=True)
