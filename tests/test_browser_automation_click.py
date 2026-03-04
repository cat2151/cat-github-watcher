"""Tests for _click_button_with_image, _get_screenshot_path, and _save_debug_info"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestClickButtonWithImage:
    """Tests for _click_button_with_image helper function"""

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_returns_false_when_screenshot_not_found(self, mock_get_path):
        """Test that function returns False when screenshot is not found"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        mock_get_path.return_value = None

        result = _click_button_with_image("test_button", {})

        assert result is False

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_returns_false_when_button_not_on_screen(self, mock_get_path):
        """Test that function returns False when button is not found on screen"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        # Need to mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.return_value = None  # Button not found

            result = _click_button_with_image("test_button", {})

            assert result is False

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    def test_skips_search_when_user_cancelled(self, monkeypatch):
        """User cancellation should skip button search and debug capture"""
        from src.gh_pr_phase_monitor.browser import button_clicker as bc

        monkeypatch.setattr(bc, "_user_cancelled_notification", True)
        with (
            patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui,
            patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path") as mock_get_path,
            patch("src.gh_pr_phase_monitor.browser.button_clicker._save_debug_info") as mock_save_debug,
        ):
            mock_get_path.return_value = Path("/tmp/test_button.png")

            from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

            result = _click_button_with_image("test_button", {})

            assert result is False
            mock_pyautogui.locateOnScreen.assert_not_called()
            mock_save_debug.assert_not_called()

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._maybe_maximize_window")
    @patch("src.gh_pr_phase_monitor.browser.button_clicker.time.sleep")
    def test_retries_after_maximize_when_not_found_first(self, mock_sleep, mock_maximize, mock_get_path):
        """Test that a maximize retry is attempted before falling back"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_maximize.return_value = True
            mock_location = MagicMock()
            mock_pyautogui.locateOnScreen.side_effect = [None, mock_location, mock_location]
            mock_pyautogui.center.return_value = (10, 20)

            result = _click_button_with_image("test_button", {})

            assert result is True
            assert mock_pyautogui.locateOnScreen.call_count == 3
            mock_maximize.assert_called_once()
            mock_pyautogui.click.assert_called_once_with((10, 20))

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    @patch("src.gh_pr_phase_monitor.browser.window_manager._maximize_window")
    @patch("src.gh_pr_phase_monitor.browser.button_clicker.time.sleep")
    def test_skip_maximize_when_config_disabled(self, mock_sleep, mock_maximize, mock_get_path):
        """Test that maximize retry can be disabled via config"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.return_value = None

            with (
                patch("src.gh_pr_phase_monitor.browser.button_clicker._click_button_with_ocr", return_value=False),
                patch("src.gh_pr_phase_monitor.browser.button_clicker._save_debug_info"),
            ):
                result = _click_button_with_image("test_button", {"maximize_on_first_fail": False})

        assert result is False
        mock_maximize.assert_not_called()
        assert mock_pyautogui.locateOnScreen.call_count == 1

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_clicks_button_when_found(self, mock_get_path):
        """Test that function clicks button when found on screen"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        # Need to mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_location = MagicMock()
            mock_pyautogui.locateOnScreen.return_value = mock_location
            mock_pyautogui.center.return_value = (100, 200)

            result = _click_button_with_image("test_button", {})

            assert result is True
            mock_pyautogui.click.assert_called_once_with((100, 200))

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._maybe_maximize_window", return_value=False)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker.time.sleep")
    def test_polls_until_max_attempts_with_interval(self, mock_sleep, mock_maximize, mock_get_path):
        """Polling should repeat locate attempts and sleep between them."""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        mock_get_path.return_value = Path("/tmp/test_button.png")

        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_location = MagicMock()
            mock_pyautogui.locateOnScreen.side_effect = [None, None, mock_location, mock_location]
            mock_pyautogui.center.return_value = (5, 5)

            result = _click_button_with_image(
                "test_button",
                {},
                max_attempts=3,
                poll_interval=0.1,
                pre_click_delay=0.0,
            )

            assert result is True
            assert mock_pyautogui.locateOnScreen.call_count == 4
            sleep_args = [call.args[0] for call in mock_sleep.call_args_list]
            assert sleep_args == [0.1, 0.1]

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._maybe_maximize_window", return_value=False)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker.time.sleep")
    def test_reverifies_before_click_with_pre_click_delay(self, mock_sleep, mock_maximize, mock_get_path):
        """Button is re-verified before clicking and pre_click_delay sleep is honored."""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        mock_get_path.return_value = Path("/tmp/test_button.png")

        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            first_location = MagicMock(name="first")
            second_location = MagicMock(name="second")
            mock_pyautogui.locateOnScreen.side_effect = [first_location, second_location]
            mock_pyautogui.center.return_value = (7, 8)

            result = _click_button_with_image(
                "test_button",
                {},
                max_attempts=1,
                poll_interval=0.0,
                pre_click_delay=0.25,
            )

            assert result is True
            assert mock_pyautogui.locateOnScreen.call_count == 2  # initial find + final verification
            mock_pyautogui.click.assert_called_once_with((7, 8))
            # pre_click_delay=0.25 should cause exactly one sleep call
            mock_sleep.assert_called_once_with(0.25)

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._maybe_maximize_window", return_value=False)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker.time.sleep")
    def test_reverifies_before_click_no_delay_when_zero(self, mock_sleep, mock_maximize, mock_get_path):
        """No sleep is taken when pre_click_delay=0."""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        mock_get_path.return_value = Path("/tmp/test_button.png")

        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            first_location = MagicMock(name="first")
            second_location = MagicMock(name="second")
            mock_pyautogui.locateOnScreen.side_effect = [first_location, second_location]
            mock_pyautogui.center.return_value = (7, 8)

            result = _click_button_with_image(
                "test_button",
                {},
                max_attempts=1,
                poll_interval=0.0,
                pre_click_delay=0.0,
            )

            assert result is True
            mock_pyautogui.click.assert_called_once_with((7, 8))
            mock_sleep.assert_not_called()


class TestGetScreenshotPath:
    """Tests for _get_screenshot_path helper function"""

    def test_returns_none_when_file_not_exists(self, tmp_path):
        """Test that function returns None when screenshot file doesn't exist"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _get_screenshot_path

        config = {"screenshot_dir": str(tmp_path)}

        result = _get_screenshot_path("nonexistent_button", config)

        assert result is None

    def test_finds_png_file(self, tmp_path):
        """Test that function finds PNG file"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _get_screenshot_path

        # Create a dummy PNG file
        screenshot_file = tmp_path / "test_button.png"
        screenshot_file.touch()

        config = {"screenshot_dir": str(tmp_path)}

        result = _get_screenshot_path("test_button", config)

        assert result == screenshot_file

    def test_uses_default_screenshot_dir(self, tmp_path, monkeypatch):
        """Test that function uses default screenshots directory"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _get_screenshot_path

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Create screenshots directory and file
        screenshots_dir = tmp_path / "screenshots"
        screenshots_dir.mkdir()
        screenshot_file = screenshots_dir / "test_button.png"
        screenshot_file.touch()

        config = {}  # No screenshot_dir specified, should use default "screenshots"

        result = _get_screenshot_path("test_button", config)

        assert result == screenshot_file


class TestSaveDebugInfo:
    """Tests for _save_debug_info helper function"""

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_saves_debug_screenshot_on_failure(self, mock_get_path, tmp_path):
        """Test that debug screenshot is saved when button is not found"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _save_debug_info

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            config = {"debug_dir": str(tmp_path)}
            _save_debug_info("test_button", 0.8, config)

            # Verify screenshot was taken and saved
            mock_pyautogui.screenshot.assert_called_once()
            mock_screenshot.save.assert_called_once()

            # Check that saved path is in the debug directory
            save_call_args = mock_screenshot.save.call_args[0][0]
            assert str(tmp_path) in save_call_args
            assert "test_button_fail" in save_call_args
            assert save_call_args.endswith(".png")

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_saves_debug_json_on_failure(self, mock_get_path, tmp_path):
        """Test that debug JSON is saved when button is not found"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _save_debug_info

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            config = {"debug_dir": str(tmp_path)}
            _save_debug_info("test_button", 0.8, config)

            # Check that JSON file was created
            json_files = list(tmp_path.glob("test_button_fail_*.json"))
            assert len(json_files) == 1

            # Verify JSON content
            with open(json_files[0], "r") as f:
                debug_info = json.load(f)

            assert debug_info["button_name"] == "test_button"
            assert debug_info["confidence"] == 0.8
            assert "timestamp" in debug_info
            assert "screenshot_path" in debug_info
            assert "template_screenshot" in debug_info

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_creates_debug_dir_if_not_exists(self, mock_get_path, tmp_path):
        """Test that debug directory is created if it doesn't exist"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _save_debug_info

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            # Use a non-existent subdirectory
            debug_dir = tmp_path / "new_debug_dir"
            assert not debug_dir.exists()

            config = {"debug_dir": str(debug_dir)}
            _save_debug_info("test_button", 0.8, config)

            # Verify directory was created
            assert debug_dir.exists()
            assert debug_dir.is_dir()

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", False)
    def test_does_nothing_when_pyautogui_unavailable(self, tmp_path):
        """Test that function does nothing when PyAutoGUI is not available"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _save_debug_info

        config = {"debug_dir": str(tmp_path)}
        _save_debug_info("test_button", 0.8, config)

        # No files should be created
        assert len(list(tmp_path.glob("*"))) == 0

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_uses_default_debug_dir(self, mock_get_path, tmp_path, monkeypatch):
        """Test that function uses default debug_screenshots directory"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _save_debug_info

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot
            mock_get_path.return_value = Path("/tmp/test_button.png")

            config = {}  # No debug_dir specified, should use default "debug_screenshots"
            _save_debug_info("test_button", 0.8, config)

            # Verify default directory was created
            default_debug_dir = tmp_path / "debug_screenshots"
            assert default_debug_dir.exists()
            assert default_debug_dir.is_dir()

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_click_button_calls_save_debug_info_on_failure(self, mock_get_path, tmp_path):
        """Test that _click_button_with_image calls _save_debug_info when button not found"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        # Mock pyautogui module
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.return_value = None  # Button not found
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot

            config = {"debug_dir": str(tmp_path)}
            result = _click_button_with_image("test_button", config)

            # Should return False
            assert result is False

            # Verify debug info was saved
            json_files = list(tmp_path.glob("test_button_fail_*.json"))
            assert len(json_files) == 1

    @patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
    @patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
    def test_click_button_saves_debug_info_on_exception(self, mock_get_path, tmp_path):
        """Test that _click_button_with_image saves debug info when exception occurs"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        # Mock pyautogui module to raise exception
        with patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui") as mock_pyautogui:
            mock_get_path.return_value = Path("/tmp/test_button.png")
            mock_pyautogui.locateOnScreen.side_effect = Exception("Test exception")
            mock_screenshot = MagicMock()
            mock_pyautogui.screenshot.return_value = mock_screenshot

            config = {"debug_dir": str(tmp_path)}
            result = _click_button_with_image("test_button", config)

            # Should return False
            assert result is False

            # Verify that debug info is saved when exception occurs in locateOnScreen
            json_files = list(tmp_path.glob("test_button_fail_*.json"))
            assert len(json_files) == 1
