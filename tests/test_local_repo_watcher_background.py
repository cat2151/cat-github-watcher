"""Tests for local_repo_watcher background monitoring functions."""

from __future__ import annotations

import importlib
import os
import pathlib
import sys
import tempfile
import threading
import types
import unittest.mock as _mock

import pytest

sys.modules.setdefault("mouseinfo", types.SimpleNamespace(MouseInfoWindow=lambda: None))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))
sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))
os.environ.setdefault("DISPLAY", ":0")

local_repo_watcher = importlib.import_module("src.gh_pr_phase_monitor.monitor.local_repo_watcher")


class TestBackgroundMonitoring:
    """Tests for the background monitoring functions."""

    @pytest.fixture(autouse=True)
    def reset_background_state(self):
        """Reset all background-monitoring module state before each test."""
        with local_repo_watcher._state_lock:
            local_repo_watcher._repo_states.clear()
            local_repo_watcher._pending_lines.clear()
            local_repo_watcher._pending_needs_restart = False
        original_startup = local_repo_watcher._startup_started
        local_repo_watcher._startup_started = False
        yield
        with local_repo_watcher._state_lock:
            local_repo_watcher._repo_states.clear()
            local_repo_watcher._pending_lines.clear()
            local_repo_watcher._pending_needs_restart = False
        local_repo_watcher._startup_started = original_startup

    def test_display_pending_produces_no_output_when_empty(self, capsys):
        """display_pending_local_repo_results prints nothing when no results are pending."""
        local_repo_watcher.display_pending_local_repo_results()
        assert capsys.readouterr().out == ""

    def test_display_pending_shows_accumulated_lines(self, capsys):
        """display_pending_local_repo_results prints pending lines with header."""
        with local_repo_watcher._state_lock:
            local_repo_watcher._pending_lines.append("  [PULLABLE] myrepo  (behind 1)")
        local_repo_watcher.display_pending_local_repo_results()
        out = capsys.readouterr().out
        assert "ローカルリポジトリ状態" in out
        assert "[PULLABLE] myrepo" in out

    def test_display_pending_clears_lines_after_display(self, capsys):
        """display_pending_local_repo_results clears pending lines so they are not shown twice."""
        with local_repo_watcher._state_lock:
            local_repo_watcher._pending_lines.append("  [PULLABLE] myrepo  (behind 1)")
        local_repo_watcher.display_pending_local_repo_results()
        local_repo_watcher.display_pending_local_repo_results()  # second call should produce no output
        out = capsys.readouterr().out
        # Lines should appear only once (first call), not again in second call
        assert out.count("[PULLABLE] myrepo") == 1

    def test_start_local_repo_monitoring_only_starts_once(self, monkeypatch):
        """start_local_repo_monitoring should start the background thread only once."""
        started = []

        def fake_thread_start(self):
            started.append(True)

        monkeypatch.setattr(threading.Thread, "start", fake_thread_start)
        config = {"local_repo_watcher_base_dir": "/nonexistent"}
        local_repo_watcher.start_local_repo_monitoring(config, "user")
        local_repo_watcher.start_local_repo_monitoring(config, "user")  # second call should be no-op
        assert len(started) == 1

    def test_notify_phase3_detected_skips_nonexistent_repo(self):
        """notify_phase3_detected for a repo with no matching local dir sets state to DONE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {"local_repo_watcher_base_dir": tmpdir}
            local_repo_watcher.notify_phase3_detected("no-such-repo", config, "myuser")
        # After the call, state should be DONE (not stuck in NEEDS_CHECK)
        assert local_repo_watcher._repo_states.get("no-such-repo") == local_repo_watcher.REPO_STATE_DONE

    def test_notify_phase3_detected_skips_if_already_checking(self):
        """notify_phase3_detected is a no-op for repos already in a checking state."""
        started = []

        with local_repo_watcher._state_lock:
            local_repo_watcher._repo_states["myrepo"] = local_repo_watcher.REPO_STATE_STARTUP_CHECKING

        with _mock.patch.object(threading.Thread, "start", lambda self: started.append(True)):
            with tempfile.TemporaryDirectory() as tmpdir:
                (pathlib.Path(tmpdir) / "myrepo").mkdir()
                config = {"local_repo_watcher_base_dir": tmpdir}
                local_repo_watcher.notify_phase3_detected("myrepo", config, "myuser")

        assert len(started) == 0

    def test_background_startup_check_accumulates_pullable(self, monkeypatch):
        """_background_startup_check stores pullable results in _pending_lines."""
        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "is_target": True,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "behind": 2,
                "ahead": 0,
                "dirty": False,
                "error": None,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
            },
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            (pathlib.Path(tmpdir) / "myrepo").mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}
            local_repo_watcher._background_startup_check(config, "myuser")

        with local_repo_watcher._state_lock:
            lines = list(local_repo_watcher._pending_lines)
        assert any("PULLABLE" in line for line in lines)
        assert local_repo_watcher._repo_states.get("myrepo") == local_repo_watcher.REPO_STATE_DONE

    def test_background_startup_check_no_output_for_up_to_date(self, monkeypatch):
        """_background_startup_check produces no pending lines for up-to-date repos."""
        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "is_target": True,
                "status": local_repo_watcher.STATUS_UP_TO_DATE,
                "behind": 0,
                "ahead": 0,
                "dirty": False,
                "error": None,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            (pathlib.Path(tmpdir) / "myrepo").mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir}
            local_repo_watcher._background_startup_check(config, "myuser")

        with local_repo_watcher._state_lock:
            lines = list(local_repo_watcher._pending_lines)
        assert lines == []

    def test_notify_phase3_detected_skips_if_already_done(self):
        """notify_phase3_detected is a no-op for repos already in DONE state (no re-trigger)."""
        with local_repo_watcher._state_lock:
            local_repo_watcher._repo_states["myrepo"] = local_repo_watcher.REPO_STATE_DONE

        started = []
        with _mock.patch.object(threading.Thread, "start", lambda self: started.append(True)):
            with tempfile.TemporaryDirectory() as tmpdir:
                (pathlib.Path(tmpdir) / "myrepo").mkdir()
                config = {"local_repo_watcher_base_dir": tmpdir}
                local_repo_watcher.notify_phase3_detected("myrepo", config, "myuser")

        assert len(started) == 0

    def test_background_startup_check_recovers_state_on_exception(self, monkeypatch):
        """_background_startup_check sets DONE even when _check_repo raises an exception."""
        monkeypatch.setattr(
            local_repo_watcher, "_check_repo", lambda path, user: (_ for _ in ()).throw(RuntimeError("fetch error"))
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            (pathlib.Path(tmpdir) / "myrepo").mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir}
            local_repo_watcher._background_startup_check(config, "myuser")

        assert local_repo_watcher._repo_states.get("myrepo") == local_repo_watcher.REPO_STATE_DONE

    def test_background_single_repo_check_recovers_state_on_exception(self, monkeypatch):
        """_background_single_repo_check sets DONE even when _check_repo raises an exception."""
        monkeypatch.setattr(
            local_repo_watcher, "_check_repo", lambda path, user: (_ for _ in ()).throw(RuntimeError("fetch error"))
        )

        with local_repo_watcher._state_lock:
            local_repo_watcher._repo_states["myrepo"] = local_repo_watcher.REPO_STATE_CHECKING

        local_repo_watcher._background_single_repo_check("/some/path", "myrepo", "myuser", False)

        assert local_repo_watcher._repo_states.get("myrepo") == local_repo_watcher.REPO_STATE_DONE

    def test_display_pending_triggers_restart(self, monkeypatch):
        """display_pending_local_repo_results calls restart_application if needs_restart is set."""
        restarted = []
        monkeypatch.setattr(local_repo_watcher, "restart_application", lambda: restarted.append(True))

        with local_repo_watcher._state_lock:
            local_repo_watcher._pending_lines.append("    自分自身が更新されました。アプリケーションを再起動します...")
            local_repo_watcher._pending_needs_restart = True

        local_repo_watcher.display_pending_local_repo_results()
        assert restarted, "restart_application should have been called"
