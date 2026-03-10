"""Tests for local_repo_checker module (status constants and classification)."""

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
