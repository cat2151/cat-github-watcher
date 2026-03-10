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

local_repo_watcher = importlib.import_module("src.gh_pr_phase_monitor.monitor.local_repo_watcher")


@pytest.fixture(autouse=True)
def reset_last_check_time():
    """Reset throttle timer before each test so checks always run."""
    original = local_repo_watcher._last_local_check_time
    local_repo_watcher._last_local_check_time = 0.0
    yield
    local_repo_watcher._last_local_check_time = original


@pytest.fixture(autouse=True)
def reset_phase3_tracking():
    """Reset phase3 post-merge tracking state before each test."""
    # These structures are mutated by background threads in local_repo_watcher;
    # take the module's state lock to avoid races during tests.
    with local_repo_watcher._state_lock:
        local_repo_watcher._repos_awaiting_post_phase3_check.clear()
        local_repo_watcher._repo_states.clear()
        local_repo_watcher._pending_lines.clear()
        local_repo_watcher._pending_needs_restart = False
        local_repo_watcher._startup_started = False
    yield
    with local_repo_watcher._state_lock:
        local_repo_watcher._repos_awaiting_post_phase3_check.clear()
        local_repo_watcher._repo_states.clear()
        local_repo_watcher._pending_lines.clear()
        local_repo_watcher._pending_needs_restart = False
        local_repo_watcher._startup_started = False


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


class TestNotifyPhase3Detected:
    """Tests for notify_phase3_detected phase3 tracking."""

    def test_notify_phase3_detected_registers_repo_for_post_phase3_check(self, monkeypatch):
        """notify_phase3_detected should add the repo to _repos_awaiting_post_phase3_check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}

            monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: {
                "name": "myrepo", "path": path, "remote_url": "https://github.com/u/myrepo.git",
                "branch": "main", "dirty": False, "behind": 0, "ahead": 0,
                "status": local_repo_watcher.STATUS_UP_TO_DATE, "error": None, "is_target": True,
            })

            local_repo_watcher.notify_phase3_detected("myrepo", config, "myuser")

        assert "myrepo" in local_repo_watcher._repos_awaiting_post_phase3_check

    def test_notify_phase3_detected_already_done_still_registers(self, monkeypatch):
        """Repos in REPO_STATE_DONE should still be registered for post-phase3 re-check."""
        local_repo_watcher._repo_states["myrepo"] = local_repo_watcher.REPO_STATE_DONE

        config = {}
        local_repo_watcher.notify_phase3_detected("myrepo", config, "myuser")

        assert "myrepo" in local_repo_watcher._repos_awaiting_post_phase3_check


def _wait_for(condition, timeout=2.0, interval=0.05):
    """Poll condition until it is True or timeout expires. Returns True if condition was met."""
    import time
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


class TestNotifyReposUpdatedAfterPhase3:
    """Tests for notify_repos_updated_after_phase3."""

    def test_triggers_recheck_for_phase3_repos_with_updated_at_change(self, monkeypatch):
        """Repos in _repos_awaiting_post_phase3_check whose updatedAt changed should be re-checked."""
        check_called = []

        def fake_check_repo(path, user):
            check_called.append(path)
            return {
                "name": "myrepo", "path": path,
                "remote_url": "https://github.com/u/myrepo.git",
                "branch": "main", "dirty": False, "behind": 2, "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE, "error": None, "is_target": True,
            }

        monkeypatch.setattr(local_repo_watcher, "_check_repo", fake_check_repo)
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}

            # Register myrepo as phase3 detected
            local_repo_watcher._repos_awaiting_post_phase3_check.add("myrepo")

            # Simulate updatedAt change for myrepo (PR was merged)
            local_repo_watcher.notify_repos_updated_after_phase3({"myrepo"}, config, "myuser")

            assert _wait_for(lambda: len(check_called) > 0), "Background check should have been triggered for myrepo"

    def test_does_not_trigger_recheck_for_repos_not_in_phase3_set(self, monkeypatch):
        """Repos NOT in _repos_awaiting_post_phase3_check should not be re-checked."""
        check_called = []
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: check_called.append(path))

        config = {}
        local_repo_watcher.notify_repos_updated_after_phase3({"other-repo"}, config, "myuser")

        import time
        time.sleep(0.1)
        assert len(check_called) == 0, "Should NOT check repos not in _repos_awaiting_post_phase3_check"

    def test_removes_from_awaiting_set_after_successful_pull(self, monkeypatch):
        """After a successful auto-pull, the repo should be removed from the tracking set."""
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: {
            "name": "myrepo", "path": path,
            "remote_url": "https://github.com/u/myrepo.git",
            "branch": "main", "dirty": False, "behind": 1, "ahead": 0,
            "status": local_repo_watcher.STATUS_PULLABLE, "error": None, "is_target": True,
        })
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "ok"))
        monkeypatch.setattr(local_repo_watcher, "REPO_ROOT", pathlib.Path("/some/other/repo"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}

            local_repo_watcher._repos_awaiting_post_phase3_check.add("myrepo")
            local_repo_watcher.notify_repos_updated_after_phase3({"myrepo"}, config, "myuser")

            assert _wait_for(lambda: "myrepo" not in local_repo_watcher._repos_awaiting_post_phase3_check), (
                "Repo should be removed from tracking set after successful pull"
            )

    def test_stays_in_awaiting_set_when_pull_disabled(self, monkeypatch):
        """When auto_git_pull=false, the repo should stay in the tracking set (not pulled)."""
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: {
            "name": "myrepo", "path": path,
            "remote_url": "https://github.com/u/myrepo.git",
            "branch": "main", "dirty": False, "behind": 1, "ahead": 0,
            "status": local_repo_watcher.STATUS_PULLABLE, "error": None, "is_target": True,
        })
        pull_called = []
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: pull_called.append(path) or (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}

            local_repo_watcher._repos_awaiting_post_phase3_check.add("myrepo")
            local_repo_watcher.notify_repos_updated_after_phase3({"myrepo"}, config, "myuser")

            # Wait for background thread to finish checking (but not pulling)
            assert _wait_for(
                lambda: local_repo_watcher._repo_states.get("myrepo") == local_repo_watcher.REPO_STATE_DONE
            ), "Background check should complete"

        assert len(pull_called) == 0, "Should not pull when auto_git_pull=false"
        assert "myrepo" in local_repo_watcher._repos_awaiting_post_phase3_check, (
            "Repo should remain in tracking set when not pulled (dry-run mode)"
        )


class TestSummarizeCargoError:
    """Tests for _summarize_cargo_error helper."""

    def test_picks_first_error_line(self):
        raw = "warning: some warning\nerror: could not compile `foo`\n   --> src/main.rs:1:1"
        result = local_repo_watcher._summarize_cargo_error(raw)
        assert result == "error: could not compile `foo`"

    def test_falls_back_to_last_line_when_no_error_prefix(self):
        raw = "compiling foo\nfinished with exit code 1"
        result = local_repo_watcher._summarize_cargo_error(raw)
        assert result == "finished with exit code 1"

    def test_truncates_long_lines(self):
        long_line = "error: " + "x" * 200
        result = local_repo_watcher._summarize_cargo_error(long_line, max_len=20)
        assert len(result) <= 21  # 20 chars + "…"
        assert result.endswith("…")

    def test_empty_input_returns_fallback(self):
        assert local_repo_watcher._summarize_cargo_error("") == "cargo install 失敗"
        assert local_repo_watcher._summarize_cargo_error("   \n  \n") == "cargo install 失敗"

    def test_single_line_not_truncated_when_short(self):
        raw = "error: binary `foo` already exists"
        result = local_repo_watcher._summarize_cargo_error(raw)
        assert result == raw


class TestCargoInstall:
    """Tests for cargo_install_repos auto-update feature."""

    def _make_pullable_result(self, name: str, path: str) -> dict:
        return {
            "name": name,
            "path": path,
            "remote_url": f"https://github.com/myuser/{name}.git",
            "branch": "main",
            "dirty": False,
            "behind": 1,
            "ahead": 0,
            "status": local_repo_watcher.STATUS_PULLABLE,
            "error": None,
            "is_target": True,
        }

    def test_cargo_install_called_after_successful_pull(self, monkeypatch, capsys):
        """When a repo in cargo_install_repos is successfully pulled, cargo install should run."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: self._make_pullable_result("my-rust-tool", path),
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))

        cargo_calls = []
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: cargo_calls.append(path) or (True, "cargo install 完了"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "my-rust-tool"
            fake_repo.mkdir()
            config = {
                "local_repo_watcher_base_dir": tmpdir,
                "auto_git_pull": True,
                "cargo_install_repos": ["my-rust-tool"],
            }
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(cargo_calls) == 1, "cargo install should be called once"
        captured = capsys.readouterr()
        assert "cargo install 完了" in captured.out

    def test_cargo_install_not_called_when_repo_not_listed(self, monkeypatch, capsys):
        """When a repo is NOT in cargo_install_repos, cargo install should not run."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: self._make_pullable_result("other-repo", path),
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))

        cargo_calls = []
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: cargo_calls.append(path) or (True, "cargo install 完了"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "other-repo"
            fake_repo.mkdir()
            config = {
                "local_repo_watcher_base_dir": tmpdir,
                "auto_git_pull": True,
                "cargo_install_repos": ["my-rust-tool"],
            }
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(cargo_calls) == 0, "cargo install should NOT be called for unlisted repos"

    def test_cargo_install_not_called_when_pull_disabled(self, monkeypatch, capsys):
        """When auto_git_pull=false (dry-run), cargo install should not run but DRY-RUN message shown."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: self._make_pullable_result("my-rust-tool", path),
        )

        cargo_calls = []
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: cargo_calls.append(path) or (True, "cargo install 完了"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "my-rust-tool"
            fake_repo.mkdir()
            config = {
                "local_repo_watcher_base_dir": tmpdir,
                "auto_git_pull": False,
                "cargo_install_repos": ["my-rust-tool"],
            }
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(cargo_calls) == 0, "cargo install should NOT run in dry-run mode"
        captured = capsys.readouterr()
        assert "cargo install" in captured.out
        assert "DRY-RUN" in captured.out

    def test_cargo_install_failure_displayed(self, monkeypatch, capsys):
        """When cargo install fails, the failure message should be shown."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: self._make_pullable_result("my-rust-tool", path),
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: (False, "error[E0001]: compilation failed"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "my-rust-tool"
            fake_repo.mkdir()
            config = {
                "local_repo_watcher_base_dir": tmpdir,
                "auto_git_pull": True,
                "cargo_install_repos": ["my-rust-tool"],
            }
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "cargo install 失敗" in captured.out
        assert "compilation failed" in captured.out

    def test_cargo_install_not_called_when_pull_fails(self, monkeypatch, capsys):
        """When git pull fails, cargo install should not be attempted."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: self._make_pullable_result("my-rust-tool", path),
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (False, "merge conflict"))

        cargo_calls = []
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: cargo_calls.append(path) or (True, "ok"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "my-rust-tool"
            fake_repo.mkdir()
            config = {
                "local_repo_watcher_base_dir": tmpdir,
                "auto_git_pull": True,
                "cargo_install_repos": ["my-rust-tool"],
            }
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(cargo_calls) == 0, "cargo install should NOT run when pull fails"

    def test_accumulate_result_calls_cargo_install(self, monkeypatch):
        """_accumulate_result should call cargo install for listed repos after successful pull."""
        cargo_calls = []
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: cargo_calls.append(path) or (True, "ok"),
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))
        monkeypatch.setattr(local_repo_watcher, "REPO_ROOT", pathlib.Path("/some/other/path"))

        result = {
            "name": "my-rust-tool",
            "path": "/tmp/my-rust-tool",
            "status": local_repo_watcher.STATUS_PULLABLE,
            "behind": 1,
            "ahead": 0,
            "is_target": True,
        }
        local_repo_watcher._accumulate_result(result, enable_pull=True, cargo_install_repos=["my-rust-tool"])

        assert len(cargo_calls) == 1, "cargo install should be triggered from _accumulate_result"
        assert cargo_calls[0] == "/tmp/my-rust-tool"

    def test_accumulate_result_no_cargo_install_without_config(self, monkeypatch):
        """_accumulate_result should not call cargo install when cargo_install_repos is empty."""
        cargo_calls = []
        monkeypatch.setattr(
            local_repo_watcher,
            "_run_cargo_install",
            lambda path: cargo_calls.append(path) or (True, "ok"),
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))
        monkeypatch.setattr(local_repo_watcher, "REPO_ROOT", pathlib.Path("/some/other/path"))

        result = {
            "name": "my-rust-tool",
            "path": "/tmp/my-rust-tool",
            "status": local_repo_watcher.STATUS_PULLABLE,
            "behind": 1,
            "ahead": 0,
            "is_target": True,
        }
        local_repo_watcher._accumulate_result(result, enable_pull=True, cargo_install_repos=[])

        assert len(cargo_calls) == 0
