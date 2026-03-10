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
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..core.colors import Colors
from .auto_updater import REPO_ROOT, restart_application

# Status constants (same classification as cat-repo-auditor)
STATUS_PULLABLE = "pullable"  # behind > 0, ahead == 0, not dirty → can pull now
STATUS_DIVERGED = "diverged"  # behind > 0 and ahead > 0 → needs manual merge
STATUS_UP_TO_DATE = "up_to_date"  # behind == 0 → already latest
STATUS_UNKNOWN = "unknown"  # fetch failed or dirty with behind > 0

# Throttle repeated git-fetch cycles to avoid excessive network calls
LOCAL_REPO_CHECK_INTERVAL_SECONDS = 300  # 5 minutes

_last_local_check_time: float = 0.0

# Per-repo state constants for background check tracking
REPO_STATE_STARTUP_CHECKING = "startup_checking"  # 起動時検査中
REPO_STATE_DONE = "done"  # 起動後検査完了
REPO_STATE_NEEDS_CHECK = "needs_check"  # 起動後検査が必要（phase3検知）
REPO_STATE_CHECKING = "checking"  # 起動後検査中

# Module-level state for background monitoring
_repo_states: Dict[str, str] = {}  # repo_name -> state
_pending_lines: List[str] = []  # 表示待ち行（次のintervalで一括表示）
_pending_needs_restart: bool = False  # 自己更新による再起動フラグ
_state_lock = threading.Lock()
_startup_started: bool = False  # 起動時検査を開始済みか

# Repos that reached phase3A and are awaiting post-merge pullable re-check.
# When updatedAt changes for these repos (e.g. user merged the PR), we trigger
# a new pullable check even though there are no open PRs.
_repos_awaiting_post_phase3_check: Set[str] = set()


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


def _run_cargo_install(path: str) -> tuple[bool, str]:
    """Run `cargo install --force --path <path>`. Returns (success, message)."""
    try:
        result = subprocess.run(
            ["cargo", "install", "--force", "--path", path],
            cwd=path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or "cargo install 失敗"
            return False, err
        return True, result.stderr.strip() or "cargo install 完了"
    except FileNotFoundError:
        return False, "cargo コマンドが見つかりません (PATH を確認してください)"
    except subprocess.TimeoutExpired:
        return False, "cargo install がタイムアウトしました"


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
    cargo_install_repos = config.get("cargo_install_repos", [])

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
    max_msg_len = 0
    for i, d in enumerate(candidates):
        repo_name = Path(d).name
        msg = f"[{i + 1}/{total}] リポジトリ確認中: {repo_name}..."
        if len(msg) > max_msg_len:
            max_msg_len = len(msg)
        padding = max_msg_len - len(msg)
        print(f"\r{msg}{' ' * padding}", end="", flush=True)
        results.append(_check_repo(d, github_username))
    if candidates:
        print(f"\r{' ' * max_msg_len}\r", end="", flush=True)
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
                if cargo_install_repos and r["name"] in cargo_install_repos:
                    cargo_ok, cargo_msg = _run_cargo_install(r["path"])
                    if cargo_ok:
                        print(f"    ✓ cargo install 完了: {r['name']}")
                    else:
                        print(f"    ✗ cargo install 失敗: {r['name']}: {cargo_msg}")
                if Path(r["path"]).resolve() == REPO_ROOT:
                    print("    自分自身が更新されました。アプリケーションを再起動します...")
                    restart_application()
            else:
                print(f"    ✗ pull 失敗: {r['name']}: {msg}")
        else:
            print(f"    [DRY-RUN] Would pull {r['name']} (auto_git_pull=false)")
            if cargo_install_repos and r["name"] in cargo_install_repos:
                print(f"    [DRY-RUN] Would run cargo install --force: {r['name']} (auto_git_pull=false)")

    for r in diverged:
        detail = f"behind {r['behind']}, ahead {r['ahead']}"
        print(f"  {Colors.YELLOW}[DIVERGED]{Colors.RESET} {r['name']}  ({detail}) ⚠ 手動マージが必要")


def _get_base_dir(config: dict) -> Optional[Path]:
    """Return the base directory for local repo scanning, or None if not valid."""
    base_dir_str = config.get("local_repo_watcher_base_dir", None)
    base_dir = Path(base_dir_str) if base_dir_str else Path.cwd().parent
    if not base_dir.exists() or not base_dir.is_dir():
        return None
    return base_dir


def _accumulate_result(result: dict, enable_pull: bool, cargo_install_repos: List[str] | None = None) -> None:
    """Process a single repo check result: pull if needed, accumulate display lines.

    Must be called with _state_lock NOT held (since _pull_repo may block).
    Acquires _state_lock to append to _pending_lines / set _pending_needs_restart.
    """
    global _pending_needs_restart

    if not result["is_target"]:
        return
    if result["status"] not in (STATUS_PULLABLE, STATUS_DIVERGED):
        return

    lines: List[str] = []
    needs_restart = False
    pulled_successfully = False

    if result["status"] == STATUS_PULLABLE:
        detail = f"behind {result['behind']}"
        lines.append(f"  {Colors.GREEN}[PULLABLE]{Colors.RESET} {result['name']}  ({detail})")
        if enable_pull:
            ok, msg = _pull_repo(result["path"])
            if ok:
                lines.append(f"    ✓ pull 完了: {result['name']}")
                pulled_successfully = True
                if Path(result["path"]).resolve() == REPO_ROOT:
                    lines.append("    自分自身が更新されました。アプリケーションを再起動します...")
                    needs_restart = True
                if cargo_install_repos and result["name"] in cargo_install_repos:
                    cargo_ok, cargo_msg = _run_cargo_install(result["path"])
                    if cargo_ok:
                        lines.append(f"    ✓ cargo install 完了: {result['name']}")
                    else:
                        lines.append(f"    ✗ cargo install 失敗: {result['name']}: {cargo_msg}")
            else:
                lines.append(f"    ✗ pull 失敗: {result['name']}: {msg}")
        else:
            lines.append(f"    [DRY-RUN] Would pull {result['name']} (auto_git_pull=false)")
            if cargo_install_repos and result["name"] in cargo_install_repos:
                lines.append(f"    [DRY-RUN] Would run cargo install --force: {result['name']} (auto_git_pull=false)")
    else:  # STATUS_DIVERGED
        detail = f"behind {result['behind']}, ahead {result['ahead']}"
        lines.append(f"  {Colors.YELLOW}[DIVERGED]{Colors.RESET} {result['name']}  ({detail}) ⚠ 手動マージが必要")

    with _state_lock:
        _pending_lines.extend(lines)
        if needs_restart:
            _pending_needs_restart = True
        if pulled_successfully:
            _repos_awaiting_post_phase3_check.discard(result["name"])


def _background_startup_check(config: dict, github_username: str) -> None:
    """Background thread: check all repos in base_dir and accumulate results.

    各リポジトリの状態を STARTUP_CHECKING → DONE に更新しながら順次検査する。
    """
    base_dir = _get_base_dir(config)
    if base_dir is None:
        return

    enable_pull = config.get("auto_git_pull", False)
    cargo_install_repos = config.get("cargo_install_repos", [])

    try:
        candidates = [str(d) for d in sorted(base_dir.iterdir()) if d.is_dir() and not d.name.startswith(".")]
    except PermissionError:
        return

    if not candidates:
        return

    # Mark all candidates as STARTUP_CHECKING before any check begins
    with _state_lock:
        for d in candidates:
            _repo_states[Path(d).name] = REPO_STATE_STARTUP_CHECKING

    for d in candidates:
        repo_name = Path(d).name
        try:
            result = _check_repo(d, github_username)
            _accumulate_result(result, enable_pull, cargo_install_repos)
        except Exception:
            pass
        finally:
            with _state_lock:
                _repo_states[repo_name] = REPO_STATE_DONE


def _background_single_repo_check(repo_path: str, repo_name: str, github_username: str, enable_pull: bool, cargo_install_repos: List[str] | None = None) -> None:
    """Background thread: check a single repo and accumulate result.

    phase3検知時に呼び出される。検査後に状態を DONE に更新する。
    """
    try:
        result = _check_repo(repo_path, github_username)
        _accumulate_result(result, enable_pull, cargo_install_repos)
    except Exception:
        pass
    finally:
        with _state_lock:
            _repo_states[repo_name] = REPO_STATE_DONE


def start_local_repo_monitoring(config: dict, github_username: str) -> None:
    """アプリ起動時に全リポジトリ検査をバックグラウンドで開始する。

    1回のみ実行される。メインループをブロックしない。
    検査結果は次のintervalで display_pending_local_repo_results() により表示される。

    Args:
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    global _startup_started
    with _state_lock:
        if _startup_started:
            return
        _startup_started = True

    t = threading.Thread(
        target=_background_startup_check,
        args=(config, github_username),
        daemon=True,
    )
    t.start()


def notify_phase3_detected(repo_name: str, config: dict, github_username: str) -> None:
    """phase3を検知したリポジトリのpullable検査をバックグラウンドで開始する。

    既に検査中・待機中のリポジトリは重複して開始しない。
    検査結果は次のintervalで display_pending_local_repo_results() により表示される。

    Args:
        repo_name: GitHub リポジトリ名（ローカルディレクトリ名と一致）。
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    with _state_lock:
        # Track this repo for post-merge auto-pull re-check regardless of current state
        _repos_awaiting_post_phase3_check.add(repo_name)
        current_state = _repo_states.get(repo_name)
        if current_state in (REPO_STATE_STARTUP_CHECKING, REPO_STATE_NEEDS_CHECK, REPO_STATE_CHECKING, REPO_STATE_DONE):
            return  # 既に検査済み・検査中または待機中
        _repo_states[repo_name] = REPO_STATE_NEEDS_CHECK

    base_dir = _get_base_dir(config)
    if base_dir is None:
        with _state_lock:
            _repo_states[repo_name] = REPO_STATE_DONE
        return

    repo_path = str(base_dir / repo_name)
    if not Path(repo_path).is_dir():
        with _state_lock:
            _repo_states[repo_name] = REPO_STATE_DONE
        return

    enable_pull = config.get("auto_git_pull", False)
    cargo_install_repos = config.get("cargo_install_repos", [])

    with _state_lock:
        _repo_states[repo_name] = REPO_STATE_CHECKING

    t = threading.Thread(
        target=_background_single_repo_check,
        args=(repo_path, repo_name, github_username, enable_pull, cargo_install_repos),
        daemon=True,
    )
    t.start()


def notify_repos_updated_after_phase3(changed_repo_names: Set[str], config: dict, github_username: str) -> None:
    """phase3A済みリポジトリのupdatedAtが変化したらpullable検査を再トリガーする。

    PRをmerge/closeした後にupdatedAtが変化したリポジトリについて、
    open PRが0件でも自動pullが行われるようにするための仕組み。

    phase3Aを検知済みのリポジトリが changed_repo_names に含まれる場合、
    そのリポジトリのpullable検査を再度バックグラウンドで開始する。

    Args:
        changed_repo_names: updatedAt が変化したリポジトリ名の集合。
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    with _state_lock:
        repos_to_recheck: List[str] = []
        for repo_name in changed_repo_names:
            if repo_name not in _repos_awaiting_post_phase3_check:
                continue
            current_state = _repo_states.get(repo_name)
            # CHECKING系状態のときは状態を消さず、再チェックもスキップする
            if current_state in (REPO_STATE_STARTUP_CHECKING, REPO_STATE_CHECKING):
                continue
            # DONE のときだけ状態をリセットして再チェックを許可する
            if current_state == REPO_STATE_DONE:
                _repo_states.pop(repo_name, None)
            repos_to_recheck.append(repo_name)

    # Call notify_phase3_detected outside the lock to avoid deadlock
    for repo_name in repos_to_recheck:
        print(f"  phase3A済みリポジトリのupdatedAt変化を検知: {repo_name} → pullable再確認")
        notify_phase3_detected(repo_name, config, github_username)


def display_pending_local_repo_results() -> None:
    """バックグラウンド検査の蓄積結果を表示し、クリアする。

    メインループの各イテレーションで呼び出す。
    表示するものがなければ何も出力しない。
    自己更新（REPO_ROOT の pull 完了）が検出された場合はアプリを再起動する。
    """
    global _pending_needs_restart

    with _state_lock:
        lines = list(_pending_lines)
        _pending_lines.clear()
        needs_restart = _pending_needs_restart
        _pending_needs_restart = False

    if not lines:
        return

    print(f"\n{'=' * 50}")
    print("ローカルリポジトリ状態:")
    print(f"{'=' * 50}")
    for line in lines:
        print(line)

    if needs_restart:
        restart_application()
