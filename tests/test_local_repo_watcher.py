"""Tests for local_repo_watcher module."""

from __future__ import annotations

import importlib
import pathlib
import tempfile

import pytest

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
