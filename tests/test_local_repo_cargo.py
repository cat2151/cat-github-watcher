"""Tests for local_repo_cargo module (_summarize_cargo_error and cargo install feature)."""

from __future__ import annotations

import importlib
import os
import pathlib
import sys
import tempfile
import types

sys.modules.setdefault("mouseinfo", types.SimpleNamespace(MouseInfoWindow=lambda: None))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))
sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))
os.environ.setdefault("DISPLAY", ":0")

local_repo_watcher = importlib.import_module("src.gh_pr_phase_monitor.monitor.local_repo_watcher")


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
