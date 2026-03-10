"""Tests for local_repo_git module (git URL matching and primitives)."""

from __future__ import annotations

import importlib
import os
import sys
import types

sys.modules.setdefault("mouseinfo", types.SimpleNamespace(MouseInfoWindow=lambda: None))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))
sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))
os.environ.setdefault("DISPLAY", ":0")

local_repo_watcher = importlib.import_module("src.gh_pr_phase_monitor.monitor.local_repo_watcher")


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
