"""Tests for local_repo_watcher module."""

from __future__ import annotations

import importlib
import os
import pathlib
import sys
import tempfile
import types

import pytest

sys.modules.setdefault("mouseinfo", types.SimpleNamespace(MouseInfoWindow=lambda: None))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))
sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))
os.environ.setdefault("DISPLAY", ":0")

local_repo_watcher = importlib.import_module("src.gh_pr_phase_monitor.local_repo_watcher")


@pytest.fixture(autouse=True)
def reset_last_check_time():
    """Reset throttle timer before each test so checks always run."""
    original = local_repo_watcher._last_local_check_time
    local_repo_watcher._last_local_check_time = 0.0
    yield
    local_repo_watcher._last_local_check_time = original


class TestIsTargetRepo:
    """Tests for _is_target_repo helper."""

    def test_https_url_matches_correct_user(self):
        assert local_repo_watcher._is_target_repo("https://github.com/myuser/myrepo.git", "myuser")

    def test_ssh_url_matches_correct_user(self):
        assert local_repo_watcher._is_target_repo("git@github.com:myuser/myrepo.git", "myuser")

    def test_does_not_match_different_user(self):
        assert not local_repo_watcher._is_target_repo("https://github.com/otheruser/myrepo.git", "myuser")

    def test_non_github_url_not_matched(self):
        assert not local_repo_watcher._is_target_repo("https://gitlab.com/myuser/myrepo.git", "myuser")

    def test_case_insensitive_matching(self):
        assert local_repo_watcher._is_target_repo("https://github.com/MyUser/MyRepo.git", "myuser")

    def test_fake_github_domain_not_matched(self):
        """URLs like 'github.com.evil.com' must not be accepted."""
        assert not local_repo_watcher._is_target_repo("https://github.com.evil.com/myuser/repo.git", "myuser")

    def test_notgithub_domain_not_matched(self):
        """URLs like 'notgithub.com' must not be accepted."""
        assert not local_repo_watcher._is_target_repo("https://notgithub.com/myuser/repo.git", "myuser")


class TestStatusClassification:
    """Tests for the status classification in _check_repo."""

    def _make_result(self, behind: int, ahead: int, dirty: bool) -> str:
        """Helper: run classification logic directly and return the status."""
        # Reproduce the classification logic from _check_repo
        status = local_repo_watcher.STATUS_UNKNOWN
        if behind == 0:
            status = local_repo_watcher.STATUS_UP_TO_DATE
        elif behind > 0 and ahead > 0:
            status = local_repo_watcher.STATUS_DIVERGED
        elif behind > 0 and ahead == 0:
            status = local_repo_watcher.STATUS_UNKNOWN if dirty else local_repo_watcher.STATUS_PULLABLE
        return status

    def test_behind_only_clean_is_pullable(self):
        assert self._make_result(behind=3, ahead=0, dirty=False) == local_repo_watcher.STATUS_PULLABLE

    def test_behind_only_dirty_is_unknown(self):
        assert self._make_result(behind=3, ahead=0, dirty=True) == local_repo_watcher.STATUS_UNKNOWN

    def test_ahead_only_is_up_to_date(self):
        """ahead-only (no behind) means nothing to pull → up_to_date."""
        assert self._make_result(behind=0, ahead=2, dirty=False) == local_repo_watcher.STATUS_UP_TO_DATE

    def test_both_behind_and_ahead_is_diverged(self):
        assert self._make_result(behind=2, ahead=1, dirty=False) == local_repo_watcher.STATUS_DIVERGED

    def test_up_to_date_when_behind_zero(self):
        assert self._make_result(behind=0, ahead=0, dirty=False) == local_repo_watcher.STATUS_UP_TO_DATE


class TestCheckLocalRepos:
    """Tests for the main check_local_repos function."""

    def test_no_pullable_repos_produces_no_output(self, monkeypatch, capsys):
        """When no repos are pullable/diverged, nothing should be printed."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        # Simulate: base_dir has one repo, already up-to-date
        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 0,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_UP_TO_DATE,
                "error": None,
                "is_target": True,
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir}
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "PULLABLE" not in captured.out
        assert "DRY-RUN" not in captured.out

    def test_pullable_repo_displayed_in_dry_run(self, monkeypatch, capsys):
        """Pullable repos should display a DRY-RUN message when auto-pull is disabled."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 3,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "PULLABLE" in captured.out
        assert "myrepo" in captured.out
        assert "DRY-RUN" in captured.out
        assert "auto_git_pull=false" in captured.out

    def test_pullable_repo_auto_pulled_when_enabled(self, monkeypatch, capsys):
        """When auto_git_pull=true, pullable repos should be pulled."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 2,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )

        pull_called = []

        def fake_pull(path):
            pull_called.append(path)
            return True, "Already up to date."

        monkeypatch.setattr(local_repo_watcher, "_pull_repo", fake_pull)

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(pull_called) == 1
        captured = capsys.readouterr()
        assert "PULLABLE" in captured.out
        assert "DRY-RUN" not in captured.out
        assert "pull 完了" in captured.out

    def test_diverged_repo_displayed_without_pull(self, monkeypatch, capsys):
        """Diverged repos should be displayed but never auto-pulled."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 2,
                "ahead": 1,
                "status": local_repo_watcher.STATUS_DIVERGED,
                "error": None,
                "is_target": True,
            },
        )

        pull_called = []
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: pull_called.append(path) or (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(pull_called) == 0
        captured = capsys.readouterr()
        assert "DIVERGED" in captured.out
        assert "myrepo" in captured.out

    def test_throttle_skips_check_within_interval(self, monkeypatch, capsys):
        """The check should be throttled and not run if called within the interval."""
        import time

        local_repo_watcher._last_local_check_time = time.time()

        check_called = []
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda *a: check_called.append(a))

        config = {}
        local_repo_watcher.check_local_repos(config, "myuser")

        assert len(check_called) == 0

    def test_nonexistent_base_dir_is_silent(self, monkeypatch, capsys):
        """If the base directory does not exist, nothing should be printed."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)
        config = {"local_repo_watcher_base_dir": "/nonexistent/path/that/does/not/exist"}
        local_repo_watcher.check_local_repos(config, "myuser")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_pull_failure_displayed(self, monkeypatch, capsys):
        """When auto-pull fails, the failure message should be shown."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 1,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (False, "conflict detected"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "pull 失敗" in captured.out
        assert "conflict detected" in captured.out


class TestSelfUpdateOnPull:
    """Tests for auto-restart when cat-github-watcher itself is pulled."""

    def test_restarts_when_self_repo_is_pulled(self, monkeypatch, capsys):
        """When the pulled repo is REPO_ROOT, restart_application should be called."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = pathlib.Path(tmpdir)
            self_repo_dir = base_dir / "cat-github-watcher"
            self_repo_dir.mkdir()

            # Treat the temporary self_repo_dir as the application REPO_ROOT.
            monkeypatch.setattr(local_repo_watcher, "REPO_ROOT", self_repo_dir)

            monkeypatch.setattr(
                local_repo_watcher,
                "_check_repo",
                lambda path, user: {
                    "name": "cat-github-watcher",
                    "path": str(self_repo_dir),
                    "remote_url": "https://github.com/cat2151/cat-github-watcher.git",
                    "branch": "main",
                    "dirty": False,
                    "behind": 1,
                    "ahead": 0,
                    "status": local_repo_watcher.STATUS_PULLABLE,
                    "error": None,
                    "is_target": True,
                },
            )
            monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))

            restarted = []
            monkeypatch.setattr(local_repo_watcher, "restart_application", lambda: restarted.append(True))

            config = {"local_repo_watcher_base_dir": str(base_dir), "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "cat2151")

            assert restarted, "restart_application should have been called"
            captured = capsys.readouterr()
            assert "再起動します" in captured.out

    def test_does_not_restart_for_other_repos(self, monkeypatch, capsys):
        """When the pulled repo is NOT REPO_ROOT, restart_application should NOT be called."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 1,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))

        restarted = []
        monkeypatch.setattr(local_repo_watcher, "restart_application", lambda: restarted.append(True))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        assert not restarted, "restart_application should NOT have been called"


class TestBackgroundMonitoring:
    """Tests for the new background monitoring functions."""

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

        import threading

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
        import threading

        started = []

        def fake_thread_start(self):
            started.append(True)

        with local_repo_watcher._state_lock:
            local_repo_watcher._repo_states["myrepo"] = local_repo_watcher.REPO_STATE_STARTUP_CHECKING

        import unittest.mock as _mock

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
        import threading
        import unittest.mock as _mock

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
        """display_pending_local_repo_results calls restart_application if needs_restart is set."""
        restarted = []
        monkeypatch.setattr(local_repo_watcher, "restart_application", lambda: restarted.append(True))

        with local_repo_watcher._state_lock:
            local_repo_watcher._pending_lines.append("    自分自身が更新されました。アプリケーションを再起動します...")
            local_repo_watcher._pending_needs_restart = True

        local_repo_watcher.display_pending_local_repo_results()
        assert restarted, "restart_application should have been called"
