"""Tests for browser automation module"""

from unittest.mock import ANY, MagicMock, patch

from src.gh_pr_phase_monitor.browser_automation import (
    assign_issue_to_copilot_automated,
    is_pyautogui_available,
    merge_pr_automated,
)


class TestIsPyAutoGUIAvailable:
    """Tests for is_pyautogui_available function"""

    def test_returns_bool(self):
        """Test that function returns correct availability status"""
        # This will be True or False depending on whether PyAutoGUI is installed
        result = is_pyautogui_available()
        assert isinstance(result, bool)


class TestNotificationTheme:
    """Tests for splash/notification theming"""

    def test_dark_mode_uses_dark_background_and_palette(self, monkeypatch):
        from src.gh_pr_phase_monitor import notification_window as nw

        monkeypatch.setattr(nw, "_is_dark_mode_enabled", lambda: True)
        monkeypatch.setattr(nw.Colors, "BLUE", "\033[38;2;10;20;30m")

        theme = nw._get_notification_theme()

        assert theme["background"] == "#111111"
        assert theme["text"] == "#0a141e"
        assert theme["accent"] == "#0a141e"

    def test_light_mode_uses_configured_palette(self, monkeypatch):
        from src.gh_pr_phase_monitor import notification_window as nw

        monkeypatch.setattr(nw, "_is_dark_mode_enabled", lambda: False)
        monkeypatch.setattr(nw.Colors, "BLUE", "\033[1;94m")

        theme = nw._get_notification_theme()

        assert theme["background"] == "#ffffff"
        assert theme["text"] == "#5555ff"
        assert theme["accent"] == "#5555ff"

    def test_light_mode_supports_standard_palette_codes(self, monkeypatch):
        from src.gh_pr_phase_monitor import notification_window as nw

        monkeypatch.setattr(nw, "_is_dark_mode_enabled", lambda: False)
        monkeypatch.setattr(nw.Colors, "BLUE", "\033[32m")

        theme = nw._get_notification_theme()

        assert theme["accent"] == "#00ff00"


class TestNotificationWindow:
    """Tests for NotificationWindow behavior"""

    def test_user_close_shows_cancel_dialog(self, monkeypatch):
        from src.gh_pr_phase_monitor import notification_window as nw

        fake_root = MagicMock()
        fake_root.quit = MagicMock()
        fake_root.destroy = MagicMock()

        monkeypatch.setattr(nw, "messagebox", MagicMock())

        window = nw.NotificationWindow("msg", 100, 100, 0, 0, cancel_message="auto assignを中断します")
        window.root = fake_root

        window._on_user_close()

        nw.messagebox.showinfo.assert_called_once_with("auto assign", "auto assignを中断します", parent=fake_root)
        assert window.closed_by_user is True


class TestAssignIssueToCopilotAutomated:
    """Tests for assign_issue_to_copilot_automated function"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba
        from src.gh_pr_phase_monitor import browser_cooldown as bc

        bc._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", False)
    def test_returns_false_when_pyautogui_unavailable(self):
        """Test that function returns False when PyAutoGUI is not available"""
        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", {})
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_successful_assignment(self, mock_sleep, mock_click, mock_webbrowser):
        """Test successful assignment flow"""
        # Mock successful button clicks
        mock_click.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should succeed
        assert result is True

        # Verify browser was opened with autoraise parameter
        mock_webbrowser.open.assert_called_once()
        call_args = mock_webbrowser.open.call_args
        assert call_args[0][0] == "https://github.com/test/repo/issues/1"
        assert "autoraise" in call_args[1]  # autoraise parameter should be present

        # Verify two button clicks were attempted
        assert mock_click.call_count == 2
        call_args_list = [call[0][0] for call in mock_click.call_args_list]
        assert "assign_to_copilot" in call_args_list
        assert "assign" in call_args_list

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._start_button_notification")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_shows_notification_when_automation_runs(self, mock_sleep, mock_start, mock_webbrowser, mock_click):
        """Notification window should be shown during button automation"""
        mock_click.return_value = True
        mock_webbrowser.open.return_value = True
        mock_start.return_value = MagicMock(close=MagicMock())

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", {})

        assert result is True
        mock_start.assert_called_once()
        mock_start.return_value.close.assert_called_once()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._wait_with_cancellation", return_value=False)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._get_active_window_title")
    @patch("src.gh_pr_phase_monitor.browser_automation._start_button_notification")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_updates_notification_with_search_status(
        self, mock_sleep, mock_start, mock_get_title, mock_click, mock_webbrowser, mock_wait
    ):
        """Splash window should reflect active window and search status."""
        mock_click.return_value = True
        mock_webbrowser.open.return_value = True
        notification = MagicMock(close=MagicMock())
        mock_start.return_value = notification
        mock_get_title.return_value = "issue\nタブ"

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", {})

        assert result is True
        messages = [call.args[0] for call in notification.update_message.call_args_list]
        assert any("active window titleは、issue タブ です" in msg for msg in messages)
        assert any("Assign to Copilotボタンを探索中です…" in msg for msg in messages)
        assert any("Assign to Copilotボタンを発見しました。クリックします" in msg for msg in messages)
        assert any(
            "緑のAssignボタンを発見しました。クリックしました。自動assignを正常終了します" in msg for msg in messages
        )

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._start_button_notification")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_skips_when_notification_closed_by_user(self, mock_sleep, mock_start, mock_click, mock_webbrowser):
        """If the notification window is closed, automation should be skipped safely"""
        mock_webbrowser.open.return_value = True
        mock_notification = MagicMock(close=MagicMock(), closed_by_user=True)
        mock_start.return_value = mock_notification

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", {})

        assert result is False
        mock_click.assert_not_called()
        mock_start.assert_called_once()
        mock_notification.close.assert_called_once()

    @patch("src.gh_pr_phase_monitor.browser_automation._log_error")
    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation._start_button_notification")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_logs_and_returns_false_on_unexpected_error(
        self, mock_sleep, mock_start, mock_click, mock_webbrowser, mock_log_error
    ):
        """Unexpected automation errors should be logged and surfaced as False without raising."""
        mock_webbrowser.open.return_value = True
        mock_start.return_value = MagicMock(close=MagicMock(), closed_by_user=False)
        mock_click.side_effect = RuntimeError("boom")

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", {})

        assert result is False
        mock_log_error.assert_called_once()
        assert "https://github.com/test/repo/issues/1" in mock_log_error.call_args[0][0]
        mock_start.return_value.close.assert_called_once()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_handles_invalid_wait_seconds_string(self, mock_click, mock_webbrowser):
        """Test that function handles invalid wait_seconds (string) gracefully"""
        mock_click.return_value = False

        config = {"assign_to_copilot": {"wait_seconds": "invalid"}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should use default value and fail (because buttons not found)
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._wait_with_cancellation", return_value=False)
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_handles_negative_wait_seconds(self, mock_click, mock_wait, mock_webbrowser):
        """Test that function handles negative wait_seconds gracefully"""
        mock_click.return_value = False

        config = {"assign_to_copilot": {"wait_seconds": -5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should use default value (2) instead of -5
        assert result is False
        mock_wait.assert_called_once_with(2, ANY)

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_accepts_valid_wait_seconds(self, mock_click, mock_webbrowser):
        """Test that function accepts valid wait_seconds"""
        mock_click.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        assert result is True

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_handles_float_wait_seconds(self, mock_click, mock_webbrowser):
        """Test that function converts float wait_seconds to int"""
        mock_click.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 5.7}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should convert to int (5)
        assert result is True

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_fails_if_first_button_not_found(self, mock_click, mock_webbrowser):
        """Test that function fails if first button is not found"""

        def click_side_effect(button_name, config, **kwargs):
            if button_name == "assign_to_copilot":
                return False  # First button not found
            return True

        mock_click.side_effect = click_side_effect

        config = {"assign_to_copilot": {"wait_seconds": 1}}

        result = assign_issue_to_copilot_automated("https://github.com/test/repo/issues/1", config)

        # Should fail
        assert result is False
        assert mock_click.call_count == 1  # Only tried first button

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_same_issue_url_not_attempted_twice(self, mock_click, mock_webbrowser):
        """Test that assignment is only attempted once per issue URL"""
        mock_click.return_value = False  # Simulate button not found
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 1}}
        issue_url = "https://github.com/test/repo/issues/123"

        # First attempt - should try to assign (and fail to find button)
        result1 = assign_issue_to_copilot_automated(issue_url, config)
        assert result1 is False
        assert mock_webbrowser.open.call_count == 1

        # Second attempt with same URL - should skip (already attempted)
        result2 = assign_issue_to_copilot_automated(issue_url, config)
        assert result2 is False
        # Browser should NOT be opened a second time
        assert mock_webbrowser.open.call_count == 1

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_issue_url_can_be_retried_after_24_hours(
        self, mock_time, mock_cooldown_time, mock_sleep, mock_click, mock_webbrowser
    ):
        """Test that issue URL can be retried after 24 hours"""
        mock_click.return_value = False  # Simulate button not found
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 1}}
        issue_url = "https://github.com/test/repo/issues/123"

        # First attempt at time 0
        mock_time.return_value = 0.0
        mock_cooldown_time.return_value = 0.0
        result1 = assign_issue_to_copilot_automated(issue_url, config)
        assert result1 is False
        assert mock_webbrowser.open.call_count == 1

        # Second attempt after 12 hours - should skip (not enough time)
        mock_time.return_value = 12 * 3600  # 12 hours
        mock_cooldown_time.return_value = 12 * 3600
        result2 = assign_issue_to_copilot_automated(issue_url, config)
        assert result2 is False
        assert mock_webbrowser.open.call_count == 1  # Still 1 (not opened again)

        # Third attempt after 25 hours - should retry (more than 24 hours)
        mock_time.return_value = 25 * 3600  # 25 hours
        mock_cooldown_time.return_value = 25 * 3600
        result3 = assign_issue_to_copilot_automated(issue_url, config)
        assert result3 is False
        assert mock_webbrowser.open.call_count == 2  # Now 2 (opened again)

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.time")
    def test_different_issue_urls_are_tracked_separately(
        self, mock_time, mock_cooldown_time, mock_sleep, mock_click, mock_webbrowser
    ):
        """Test that different issue URLs can each be attempted once"""
        mock_click.return_value = True  # Simulate success
        mock_webbrowser.open.return_value = True

        config = {"assign_to_copilot": {"wait_seconds": 1}}
        issue_url_1 = "https://github.com/test/repo/issues/123"
        issue_url_2 = "https://github.com/test/repo/issues/456"

        # First issue - should succeed
        mock_time.return_value = 0.0
        mock_cooldown_time.return_value = 0.0
        result1 = assign_issue_to_copilot_automated(issue_url_1, config)
        assert result1 is True

        # Second issue - should also succeed (different URL)
        # Advance time past cooldown (61 seconds)
        mock_time.return_value = 61.0
        mock_cooldown_time.return_value = 61.0
        result2 = assign_issue_to_copilot_automated(issue_url_2, config)
        assert result2 is True

        # Browser should be opened twice (once for each URL)
        assert mock_webbrowser.open.call_count == 2


class TestMergePrAutomated:
    """Tests for merge_pr_automated function"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_automation as ba
        from src.gh_pr_phase_monitor import browser_cooldown as bc

        bc._last_browser_open_time = None
        ba._issue_assign_attempted.clear()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", False)
    def test_returns_false_when_pyautogui_unavailable(self):
        """Test that function returns False when PyAutoGUI is not available"""
        result = merge_pr_automated("https://github.com/test/repo/pull/1", {})
        assert result is False

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_clicks_delete_branch_button_after_merge(self, mock_sleep, mock_click, mock_webbrowser):
        """Test that function attempts to click Delete branch button after merge"""
        # Mock click function to succeed for all buttons
        mock_click.return_value = True

        config = {"phase3_merge": {"wait_seconds": 1}}

        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        # Should succeed
        assert result is True

        # Verify the three button clicks: merge_pull_request, confirm_merge, delete_branch
        assert mock_click.call_count == 3
        call_args_list = [call[0][0] for call in mock_click.call_args_list]
        assert "merge_pull_request" in call_args_list
        assert "confirm_merge" in call_args_list
        assert "delete_branch" in call_args_list

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._start_button_notification")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_shows_notification_for_merge_automation(self, mock_sleep, mock_start, mock_webbrowser, mock_click):
        """Notification window should be shown during merge automation"""
        mock_click.return_value = True
        mock_webbrowser.open.return_value = True
        mock_start.return_value = MagicMock(close=MagicMock())

        result = merge_pr_automated("https://github.com/test/repo/pull/1", {})

        assert result is True
        mock_start.assert_called_once()
        mock_start.return_value.close.assert_called_once()

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    @patch("src.gh_pr_phase_monitor.browser_automation.time.sleep")
    def test_succeeds_even_if_delete_branch_button_not_found(self, mock_sleep, mock_click, mock_webbrowser):
        """Test that function succeeds even if Delete branch button is not found"""

        def click_side_effect(button_name, config, **kwargs):
            if button_name == "delete_branch":
                return False  # Button not found
            return True

        mock_click.side_effect = click_side_effect

        config = {"phase3_merge": {"wait_seconds": 1}}

        result = merge_pr_automated("https://github.com/test/repo/pull/1", config)

        # Should still succeed (merge was successful, branch deletion is optional)
        assert result is True
        assert mock_click.call_count == 3

    @patch("src.gh_pr_phase_monitor.browser_automation.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser_automation._start_button_notification")
    @patch("src.gh_pr_phase_monitor.browser_automation._wait_with_cancellation")
    @patch("src.gh_pr_phase_monitor.browser_automation.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_automation._click_button_with_image")
    def test_merge_aborts_when_notification_closed(
        self, mock_click, mock_webbrowser, mock_wait, mock_start_notification
    ):
        """If the notification is closed, merge automation should abort early"""
        mock_webbrowser.open.return_value = True
        mock_start_notification.return_value = MagicMock()
        mock_wait.return_value = True  # Simulate user close during initial wait

        result = merge_pr_automated("https://github.com/test/repo/pull/1", {})

        assert result is False
        mock_click.assert_not_called()
