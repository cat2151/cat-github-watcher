"""Tests for browser cooldown, window activation, and window-activation integration"""

from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.browser_automation import (
    assign_issue_to_copilot_automated,
    merge_pr_automated,
)

class TestBrowserCooldown:
    """Tests for browser cooldown functionality"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba
        from src.gh_pr_phase_monitor import browser_cooldown as bc

        bc._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_assign_respects_cooldown(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that assign_issue_to_copilot_automated respects cooldown"""
        # Mock click function to succeed
        mock_click.return_value = True

        # First call - should succeed
        mock_time.return_value = 0.0
        config = {"assign_to_copilot": {"wait_seconds": 1, "button_delay": 1}}

        result1 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)
        assert result1 is True

        # Second call immediately after - should fail due to cooldown
        mock_time.return_value = 1.0  # Only 1 second passed
        result2 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/2", config)
        assert result2 is False

        # Third call after cooldown - should succeed
        mock_time.return_value = 61.0  # 61 seconds passed since first call
        result3 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/3", config)
        assert result3 is True

        # Verify browser was only opened twice (first and third calls)
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_merge_respects_cooldown(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that merge_pr_automated respects cooldown"""
        # Mock click function to succeed
        mock_click.return_value = True

        # First call - should succeed
        mock_time.return_value = 0.0
        config = {"phase3_merge": {"wait_seconds": 1, "button_delay": 1}}

        result1 = merge_pr_automated("https://github.com/test/repo/pull/1", config)
        assert result1 is True

        # Second call immediately after - should fail due to cooldown
        mock_time.return_value = 1.0  # Only 1 second passed
        result2 = merge_pr_automated("https://github.com/test/repo/pull/2", config)
        assert result2 is False

        # Third call after cooldown - should succeed
        mock_time.return_value = 61.0  # 61 seconds passed since first call
        result3 = merge_pr_automated("https://github.com/test/repo/pull/3", config)
        assert result3 is True

        # Verify browser was only opened twice (first and third calls)
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_cooldown_applies_across_assign_and_merge(self, mock_time, mock_sleep, mock_click, mock_webbrowser):
        """Test that cooldown is shared between assign and merge operations"""
        # Mock click function to succeed
        mock_click.return_value = True

        # First call - assign (should succeed)
        mock_time.return_value = 0.0
        config = {"assign_to_copilot": {"wait_seconds": 1}, "phase3_merge": {"wait_seconds": 1}}

        result1 = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)
        assert result1 is True

        # Second call - merge immediately after (should fail due to cooldown)
        mock_time.return_value = 1.0  # Only 1 second passed
        result2 = merge_pr_automated("https://github.com/test/repo/pull/1", config)
        assert result2 is False

        # Third call - merge after cooldown (should succeed)
        mock_time.return_value = 61.0  # 61 seconds passed since first call
        result3 = merge_pr_automated("https://github.com/test/repo/pull/2", config)
        assert result3 is True

        # Verify browser was only opened twice
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_can_open_browser_when_no_previous_open(self, mock_time):
        """Test that _can_open_browser returns True when no previous browser was opened"""
        from src.gh_pr_phase_monitor.browser_automation import _can_open_browser

        result = _can_open_browser()
        assert result is True

    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_can_open_browser_respects_cooldown(self, mock_time):
        """Test that _can_open_browser respects the 60-second cooldown"""
        from src.gh_pr_phase_monitor.browser_automation import _can_open_browser, _record_browser_open

        # Record a browser open at time 0
        mock_time.return_value = 0.0
        _record_browser_open()

        # Check at time 30 - should not be able to open
        mock_time.return_value = 30.0
        assert _can_open_browser() is False

        # Check at time 59 - still should not be able to open
        mock_time.return_value = 59.0
        assert _can_open_browser() is False

        # Check at time 60 - should be able to open
        mock_time.return_value = 60.0
        assert _can_open_browser() is True

        # Check at time 61 - should be able to open
        mock_time.return_value = 61.0
        assert _can_open_browser() is True

    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_get_remaining_cooldown(self, mock_time):
        """Test that _get_remaining_cooldown returns correct remaining time"""
        from src.gh_pr_phase_monitor.browser_automation import _get_remaining_cooldown, _record_browser_open

        # When no browser has been opened, remaining should be 0
        remaining = _get_remaining_cooldown()
        assert remaining == 0.0

        # Record a browser open at time 0
        mock_time.return_value = 0.0
        _record_browser_open()

        # At time 30, remaining should be 30
        mock_time.return_value = 30.0
        remaining = _get_remaining_cooldown()
        assert remaining == 30.0

        # At time 61, remaining should be 0
        mock_time.return_value = 61.0
        remaining = _get_remaining_cooldown()
        assert remaining == 0.0


class TestActivateWindowByTitle:
    """Tests for _activate_window_by_title function"""

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", False)
    def test_exits_when_pygetwindow_unavailable_and_window_title_configured(self):
        """Test that function exits with error when PyGetWindow is not available but window_title is configured"""
        import pytest

        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        with pytest.raises(SystemExit) as exc_info:
            _activate_window_by_title("Test Window", {})

        assert exc_info.value.code == 1

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_returns_false_when_window_title_is_none(self, mock_gw):
        """Test that function returns False when window_title is None"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        result = _activate_window_by_title(None, {})
        assert result is False

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_returns_false_when_window_title_is_empty(self, mock_gw):
        """Test that function returns False when window_title is empty string"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        result = _activate_window_by_title("", {})
        assert result is False

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_activates_matching_window(self, mock_gw):
        """Test that function activates a window matching the title"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        # Create mock windows
        mock_window_1 = MagicMock()
        mock_window_1.title = "GitHub - Issues"
        mock_window_1.isMinimized = False

        mock_window_2 = MagicMock()
        mock_window_2.title = "Google Chrome"
        mock_window_2.isMinimized = False

        mock_gw.getAllWindows.return_value = [mock_window_1, mock_window_2]

        result = _activate_window_by_title("GitHub", {})

        assert result is True
        mock_window_1.activate.assert_called_once()
        mock_window_2.activate.assert_not_called()

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_restores_minimized_window_before_activating(self, mock_gw):
        """Test that function restores a minimized window before activating"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        # Create mock minimized window
        mock_window = MagicMock()
        mock_window.title = "GitHub - Pull Request"
        mock_window.isMinimized = True

        mock_gw.getAllWindows.return_value = [mock_window]

        result = _activate_window_by_title("GitHub", {})

        assert result is True
        mock_window.restore.assert_called_once()
        mock_window.activate.assert_called_once()

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_returns_false_when_no_matching_window_found(self, mock_gw):
        """Test that function returns False when no window matches the title"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        # Create mock windows with different titles
        mock_window = MagicMock()
        mock_window.title = "Google Chrome"

        mock_gw.getAllWindows.return_value = [mock_window]

        result = _activate_window_by_title("GitHub", {})

        assert result is False
        mock_window.activate.assert_not_called()

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_handles_exception_gracefully(self, mock_gw):
        """Test that function handles exceptions gracefully"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        # Mock getAllWindows to raise an exception
        mock_gw.getAllWindows.side_effect = Exception("Test exception")

        result = _activate_window_by_title("GitHub", {})

        assert result is False

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_case_insensitive_matching(self, mock_gw):
        """Test that window title matching is case-insensitive"""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        # Create mock window with different case
        mock_window = MagicMock()
        mock_window.title = "GITHUB - Issues"
        mock_window.isMinimized = False

        mock_gw.getAllWindows.return_value = [mock_window]

        result = _activate_window_by_title("github", {})

        assert result is True
        mock_window.activate.assert_called_once()

    @patch("src.gh_pr_phase_monitor.window_manager.PYGETWINDOW_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.window_manager.gw")
    def test_skips_search_when_active_window_matches(self, mock_gw):
        """Return early when the active window already matches the title."""
        from src.gh_pr_phase_monitor.browser_automation import _activate_window_by_title

        active_window = MagicMock()
        active_window.title = "GitHub - notifications"
        mock_gw.getActiveWindow.return_value = active_window

        result = _activate_window_by_title("github", {})

        assert result is True
        mock_gw.getAllWindows.assert_not_called()


class TestAssignWithWindowActivation:
    """Tests for assign_issue_to_copilot_automated with window activation"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba
        from src.gh_pr_phase_monitor import browser_cooldown as bc

        bc._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._activate_window_by_title")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_calls_window_activation_when_window_title_configured(
        self, mock_sleep, mock_activate, mock_click, mock_webbrowser
    ):
        """Test that window activation is called when window_title is configured"""
        mock_click.return_value = True
        mock_activate.return_value = True
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5, "window_title": "GitHub"}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        assert result is True
        mock_activate.assert_called_once()
        activate_args = mock_activate.call_args[0]
        assert activate_args[0] == "GitHub"
        assert activate_args[1]["window_title"] == "GitHub"

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._activate_window_by_title")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_skips_window_activation_when_window_title_not_configured(
        self, mock_sleep, mock_activate, mock_click, mock_webbrowser
    ):
        """Test that window activation is skipped when window_title is not configured"""
        mock_click.return_value = True
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        assert result is True
        mock_activate.assert_not_called()


class TestMergeWithWindowActivation:
    """Tests for merge_pr_automated with window activation"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_cooldown as bc

        bc._last_browser_open_time = None

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._activate_window_by_title")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_calls_window_activation_when_window_title_configured(
        self, mock_sleep, mock_activate, mock_click, mock_webbrowser
    ):
        """Test that window activation is called when window_title is configured"""
        mock_click.return_value = True
        mock_activate.return_value = True
        mock_webbrowser.open.return_value = True

        config = {"phase3_merge": {"wait_seconds": 5, "window_title": "GitHub"}}

        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        assert result is True
        mock_activate.assert_called_once()
        activate_args = mock_activate.call_args[0]
        assert activate_args[0] == "GitHub"
        assert activate_args[1]["window_title"] == "GitHub"

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._activate_window_by_title")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_skips_window_activation_when_window_title_not_configured(
        self, mock_sleep, mock_activate, mock_click, mock_webbrowser
    ):
        """Test that window activation is skipped when window_title is not configured"""
        mock_click.return_value = True
        mock_webbrowser.open.return_value = True

        config = {"phase3_merge": {"wait_seconds": 5}}

        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        assert result is True
        mock_activate.assert_not_called()


