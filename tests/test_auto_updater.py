"""Tests for the self-update helper."""

import importlib
import os
import sys
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

auto_updater = importlib.import_module("src.gh_pr_phase_monitor.auto_updater")


@pytest.fixture(autouse=True)
def reset_last_check_time():
    original_last_check_time = getattr(auto_updater, "_last_check_time", 0.0)
    auto_updater._last_check_time = 0.0
    try:
        yield
    finally:
        auto_updater._last_check_time = original_last_check_time


def test_skips_when_interval_not_elapsed(monkeypatch):
    auto_updater._last_check_time = time.time()

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("update check should have been throttled")

    monkeypatch.setattr(auto_updater, "_get_tracking_branch", fail_if_called)

    assert auto_updater.maybe_self_update(repo_root=auto_updater.REPO_ROOT) is False


def test_skips_when_remote_matches_local(monkeypatch):
    calls = {"pulled": False, "restarted": False}

    monkeypatch.setattr(auto_updater, "_get_tracking_branch", lambda _repo: ("origin", "main"))
    monkeypatch.setattr(auto_updater, "_get_remote_repo", lambda _repo, _remote: ("owner", "repo"))
    monkeypatch.setattr(auto_updater, "_get_local_head_sha", lambda _repo: "abc")
    monkeypatch.setattr(auto_updater, "_get_remote_latest_sha", lambda *_args, **_kwargs: "abc")
    monkeypatch.setattr(auto_updater, "_is_worktree_clean", lambda _repo: True)
    monkeypatch.setattr(
        auto_updater, "_pull_fast_forward", lambda *_args, **_kwargs: calls.update(pulled=True) or True
    )
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
