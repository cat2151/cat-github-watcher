"""Tests for the self-update helper."""

import importlib
import os
import sys
import threading
import time
import types

import pytest

sys.modules.setdefault("mouseinfo", types.SimpleNamespace(MouseInfoWindow=lambda: None))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))
sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))
os.environ.setdefault("DISPLAY", ":0")

auto_updater = importlib.import_module("src.gh_pr_phase_monitor.monitor.auto_updater")

_THREAD_TIMEOUT = 3


@pytest.fixture(autouse=True)
def reset_module_state():
    original_last_check_time = getattr(auto_updater, "_last_check_time", 0.0)
    auto_updater._last_check_time = 0.0
    try:
        yield
    finally:
        auto_updater._last_check_time = original_last_check_time


def test_repo_root_points_to_actual_repo_root():
    """REPO_ROOT must point to the repository root (containing cat-github-watcher.py), not src/."""
    assert (auto_updater.REPO_ROOT / "cat-github-watcher.py").exists(), (
        f"REPO_ROOT ({auto_updater.REPO_ROOT}) does not contain cat-github-watcher.py. "
        "Check the number of .parent levels in the REPO_ROOT definition."
    )


def test_skips_when_interval_not_elapsed(monkeypatch):
    auto_updater._last_check_time = time.time()

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("update check should have been throttled")

    monkeypatch.setattr(auto_updater, "_get_tracking_branch", fail_if_called)

    assert auto_updater.maybe_self_update(repo_root=auto_updater.REPO_ROOT) is False


def test_get_remote_latest_sha_uses_branches_api(monkeypatch):
    """_get_remote_latest_sha はブランチAPIを使い、-F フラグなしのGETリクエストを発行することを確認。

    以前の実装は -F フラグを使用していたため、gh api がデフォルトでPOSTメソッドになり
    コミットAPIの呼び出しが失敗していた（commits エンドポイントはGETのみ対応）。
    修正後は branches/{branch} エンドポイントを使用し、GETリクエストで正しく動作する。
    """
    captured_args = []

    def fake_run_command(args, cwd=None):
        captured_args.append(args)
        result = types.SimpleNamespace(returncode=0, stdout="abc123def456\n", stderr="")
        return result

    monkeypatch.setattr(auto_updater, "_run_command", fake_run_command)

    sha = auto_updater._get_remote_latest_sha("owner", "repo", "main", auto_updater.REPO_ROOT)

    assert sha == "abc123def456"
    assert len(captured_args) == 1
    cmd = captured_args[0]
    # branches/{branch} エンドポイントを使用していること（-F フラグなし）
    assert "repos/owner/repo/branches/main" in " ".join(cmd)
    assert "-F" not in cmd
    assert "--raw-field" not in cmd


def test_get_remote_latest_sha_returns_none_on_failure(monkeypatch):
    """_get_remote_latest_sha は API 呼び出し失敗時に None を返すことを確認。"""

    def fake_run_command(args, cwd=None):
        return types.SimpleNamespace(returncode=1, stdout="", stderr="error")

    monkeypatch.setattr(auto_updater, "_run_command", fake_run_command)

    sha = auto_updater._get_remote_latest_sha("owner", "repo", "main", auto_updater.REPO_ROOT)

    assert sha is None


def test_get_remote_latest_sha_returns_none_for_null_response(monkeypatch):
    """_get_remote_latest_sha は jq が 'null' を返した場合に None を返すことを確認。"""

    def fake_run_command(args, cwd=None):
        return types.SimpleNamespace(returncode=0, stdout="null\n", stderr="")

    monkeypatch.setattr(auto_updater, "_run_command", fake_run_command)

    sha = auto_updater._get_remote_latest_sha("owner", "repo", "main", auto_updater.REPO_ROOT)

    assert sha is None


def test_skips_when_remote_matches_local(monkeypatch):
    calls = {"pulled": False, "restarted": False}

    monkeypatch.setattr(auto_updater, "_get_tracking_branch", lambda _repo: ("origin", "main"))
    monkeypatch.setattr(auto_updater, "_get_remote_repo", lambda _repo, _remote: ("owner", "repo"))
    monkeypatch.setattr(auto_updater, "_get_local_head_sha", lambda _repo: "abc")
    monkeypatch.setattr(auto_updater, "_get_remote_latest_sha", lambda *_args, **_kwargs: "abc")
    monkeypatch.setattr(auto_updater, "_is_worktree_clean", lambda _repo: True)
    monkeypatch.setattr(auto_updater, "_pull_fast_forward", lambda *_args, **_kwargs: calls.update(pulled=True) or True)
    monkeypatch.setattr(auto_updater, "restart_application", lambda: calls.update(restarted=True))

    assert auto_updater.maybe_self_update(repo_root=auto_updater.REPO_ROOT) is False
    assert calls["pulled"] is False
    assert calls["restarted"] is False


def test_skips_when_worktree_dirty(monkeypatch):
    monkeypatch.setattr(auto_updater, "_get_tracking_branch", lambda _repo: ("origin", "main"))
    monkeypatch.setattr(auto_updater, "_get_remote_repo", lambda _repo, _remote: ("owner", "repo"))
    monkeypatch.setattr(auto_updater, "_get_local_head_sha", lambda _repo: "abc")
    monkeypatch.setattr(auto_updater, "_get_remote_latest_sha", lambda *_args, **_kwargs: "def")
    monkeypatch.setattr(auto_updater, "_is_worktree_clean", lambda _repo: False)

    def fail_pull(*_args, **_kwargs):
        raise AssertionError("pull should not run when worktree is dirty")

    monkeypatch.setattr(auto_updater, "_pull_fast_forward", fail_pull)
    monkeypatch.setattr(auto_updater, "restart_application", fail_pull)

    assert auto_updater.maybe_self_update(repo_root=auto_updater.REPO_ROOT) is False


def test_updates_and_restarts_when_remote_is_newer(monkeypatch):
    calls = {"restarted": False}

    monkeypatch.setattr(auto_updater, "_get_tracking_branch", lambda _repo: ("origin", "main"))
    monkeypatch.setattr(auto_updater, "_get_remote_repo", lambda _repo, _remote: ("owner", "repo"))
    monkeypatch.setattr(auto_updater, "_get_local_head_sha", lambda _repo: "abc")
    monkeypatch.setattr(auto_updater, "_get_remote_latest_sha", lambda *_args, **_kwargs: "def")
    monkeypatch.setattr(auto_updater, "_is_worktree_clean", lambda _repo: True)
    monkeypatch.setattr(auto_updater, "_pull_fast_forward", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(auto_updater, "restart_application", lambda: calls.update(restarted=True))

    assert auto_updater.maybe_self_update(repo_root=auto_updater.REPO_ROOT) is True
    assert calls["restarted"] is True


def test_concurrent_calls_do_not_double_update(monkeypatch):
    """ロックにより maybe_self_update が並行実行されても git pull が1回しか行われないことを確認。"""
    pull_count = {"n": 0}
    start_event = threading.Event()

    def counting_pull(*_args, **_kwargs):
        pull_count["n"] += 1
        return True

    monkeypatch.setattr(auto_updater, "_get_tracking_branch", lambda _repo: ("origin", "main"))
    monkeypatch.setattr(auto_updater, "_get_remote_repo", lambda _repo, _remote: ("owner", "repo"))
    monkeypatch.setattr(auto_updater, "_get_local_head_sha", lambda _repo: "abc")
    monkeypatch.setattr(auto_updater, "_get_remote_latest_sha", lambda *_args, **_kwargs: "def")
    monkeypatch.setattr(auto_updater, "_is_worktree_clean", lambda _repo: True)
    monkeypatch.setattr(auto_updater, "_pull_fast_forward", counting_pull)
    monkeypatch.setattr(auto_updater, "restart_application", lambda: None)

    def run():
        start_event.wait()
        auto_updater.maybe_self_update(repo_root=auto_updater.REPO_ROOT)

    threads = [threading.Thread(target=run) for _ in range(5)]
    for t in threads:
        t.start()
    start_event.set()
    for t in threads:
        t.join(timeout=_THREAD_TIMEOUT)

    # ロック + インターバル再チェックにより pull は1回のみ実行される
    assert pull_count["n"] == 1


def test_run_startup_self_update_foreground_prints_and_no_update(monkeypatch, capsys):
    """run_startup_self_update_foreground() がアップデートなしの場合に起動チェックメッセージを表示することを確認。"""
    monkeypatch.setattr(auto_updater, "maybe_self_update", lambda repo_root=None: False)

    auto_updater.run_startup_self_update_foreground(repo_root=auto_updater.REPO_ROOT)

    captured = capsys.readouterr()
    assert "Auto-update" in captured.out
    assert "check complete" in captured.out


def test_run_startup_self_update_foreground_prints_and_update_applied(monkeypatch, capsys):
    """run_startup_self_update_foreground() がアップデートありの場合にチェックメッセージを表示することを確認。"""
    restarted = []
    monkeypatch.setattr(auto_updater, "_get_tracking_branch", lambda _repo: ("origin", "main"))
    monkeypatch.setattr(auto_updater, "_get_remote_repo", lambda _repo, _remote: ("owner", "repo"))
    monkeypatch.setattr(auto_updater, "_get_local_head_sha", lambda _repo: "abc")
    monkeypatch.setattr(auto_updater, "_get_remote_latest_sha", lambda *_args, **_kwargs: "def")
    monkeypatch.setattr(auto_updater, "_is_worktree_clean", lambda _repo: True)
    monkeypatch.setattr(auto_updater, "_pull_fast_forward", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(auto_updater, "restart_application", lambda: restarted.append(True))

    auto_updater.run_startup_self_update_foreground(repo_root=auto_updater.REPO_ROOT)

    captured = capsys.readouterr()
    assert "Auto-update" in captured.out
    assert "update detected" in captured.out
    assert restarted, "restart_application should have been called"


def test_run_startup_self_update_foreground_swallows_exceptions(monkeypatch, capsys):
    """run_startup_self_update_foreground() が例外をキャッチして出力し、クラッシュしないことを確認。"""

    def raise_error(repo_root=None):
        raise RuntimeError("simulated error")

    monkeypatch.setattr(auto_updater, "maybe_self_update", raise_error)

    auto_updater.run_startup_self_update_foreground(repo_root=auto_updater.REPO_ROOT)

    captured = capsys.readouterr()
    assert "Auto-update" in captured.out
    assert "failed" in captured.out
