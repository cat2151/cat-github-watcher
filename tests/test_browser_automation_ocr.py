"""Tests for OCR fallback and enhanced debug info"""

import json
from pathlib import Path


class TestOCRFallback:
    """Tests for OCR-based button detection fallback"""

    def test_ocr_returns_false_when_pytesseract_unavailable(self, mocker):
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYTESSERACT_AVAILABLE", False)
        """Test that OCR detection returns False when pytesseract is not available"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_ocr

        result = _click_button_with_ocr("assign_to_copilot", {})
        assert result is False

    def test_ocr_returns_false_when_pyautogui_unavailable(self, mocker):
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", False)
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYTESSERACT_AVAILABLE", True)
        """Test that OCR detection returns False when PyAutoGUI is not available"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_ocr

        result = _click_button_with_ocr("assign_to_copilot", {})
        assert result is False

    def test_ocr_respects_enable_ocr_detection_false(self, mocker):
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYTESSERACT_AVAILABLE", True)
        """Test that OCR detection is skipped when disabled in config"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_ocr

        config = {"enable_ocr_detection": False}
        result = _click_button_with_ocr("assign_to_copilot", config)
        assert result is False

    def test_ocr_finds_and_clicks_button(self, mocker):
        mock_pytesseract = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.pytesseract")
        mock_pyautogui = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui")
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYTESSERACT_AVAILABLE", True)
        """Test that OCR detection finds and clicks button by text"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_ocr

        # Mock screenshot
        mock_screenshot = mocker.MagicMock()
        mock_screenshot.width = 1920
        mock_screenshot.height = 1080
        mock_pyautogui.screenshot.return_value = mock_screenshot

        # Mock OCR data - simulate finding "Assign to Copilot" text
        mock_pytesseract.image_to_data.return_value = {
            "text": ["", "Assign", "to", "Copilot", ""],
            "left": [0, 100, 150, 200, 0],
            "top": [0, 50, 50, 50, 0],
            "width": [0, 40, 20, 50, 0],
            "height": [0, 20, 20, 20, 0],
        }
        mock_pytesseract.Output.DICT = 0

        result = _click_button_with_ocr("assign_to_copilot", {})

        assert result is True
        # Verify click was called (center of the found region with padding)
        mock_pyautogui.click.assert_called_once()


class TestEnhancedDebugInfo:
    """Tests for enhanced debug information with candidate detection"""

    def test_fallback_to_ocr_when_image_not_found(self, mocker):
        mock_ocr = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker._click_button_with_ocr")
        mock_save_debug = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker._save_debug_info")
        mock_get_path = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
        """Test that function falls back to OCR when image recognition fails"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        mock_pyautogui = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui")
        mock_get_path.return_value = Path("/tmp/test_button.png")
        mock_pyautogui.locateOnScreen.return_value = None  # Image not found
        mock_ocr.return_value = True  # OCR succeeds

        result = _click_button_with_image("test_button", {})

        # Should try OCR fallback
        assert result is True
        mock_ocr.assert_called_once_with("test_button", {})
        mock_save_debug.assert_called_once()

    def test_returns_false_when_all_methods_fail(self, mocker):
        mock_ocr = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker._click_button_with_ocr")
        mock_save_debug = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker._save_debug_info")
        mock_get_path = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker._get_screenshot_path")
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
        """Test that function returns False when both image and OCR fail"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _click_button_with_image

        mock_pyautogui = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui")
        mock_get_path.return_value = Path("/tmp/test_button.png")
        mock_pyautogui.locateOnScreen.return_value = None  # Image not found
        mock_ocr.return_value = False  # OCR also fails

        result = _click_button_with_image("test_button", {})

        # Should fail
        assert result is False
        mock_ocr.assert_called_once()
        mock_save_debug.assert_called_once()

    def test_save_debug_info_saves_candidates(self, mocker, tmp_path):
        mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.PYAUTOGUI_AVAILABLE", True)
        """Test that debug info includes candidate locations"""
        from src.gh_pr_phase_monitor.browser.browser_automation import _save_debug_info

        config = {"debug_dir": str(tmp_path)}

        # Create a dummy template
        template_dir = tmp_path / "screenshots"
        template_dir.mkdir()
        template_path = template_dir / "test_button.png"
        template_path.write_text("dummy")

        config["screenshot_dir"] = str(template_dir)

        mock_pyautogui = mocker.patch("src.gh_pr_phase_monitor.browser.button_clicker.pyautogui")
        # Mock screenshot
        mock_screenshot = mocker.MagicMock()
        mock_pyautogui.screenshot.return_value = mock_screenshot

        # Mock locateAllOnScreen to return some candidates
        mock_location = mocker.MagicMock()
        mock_location.left = 100
        mock_location.top = 50
        mock_location.width = 200
        mock_location.height = 30
        mock_pyautogui.locateAllOnScreen.return_value = [mock_location]

        _save_debug_info("test_button", 0.8, config)

        # Check that JSON file was created
        json_files = list(tmp_path.glob("test_button_fail_*.json"))
        assert len(json_files) == 1

        # Check that JSON contains candidate information
        with open(json_files[0], encoding="utf-8") as f:
            debug_data = json.load(f)

        assert "candidates_found" in debug_data
        assert "candidates" in debug_data
