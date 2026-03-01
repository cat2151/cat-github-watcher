"""
Tests for assign_issue_to_copilot function
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.github_client import (
    assign_issue_to_copilot,
)


class TestAssignIssueToCopilot:
    """Tests for assign_issue_to_copilot function"""

    def test_missing_url_field(self):
        """Test validation of missing URL field"""
        # Missing 'url' field
        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
        }
        assert assign_issue_to_copilot(issue) is False

    @patch("src.gh_pr_phase_monitor.issue_fetcher.assign_issue_to_copilot_automated")
    @patch("src.gh_pr_phase_monitor.issue_fetcher.is_pyautogui_available")
    def test_automated_mode_when_pyautogui_available(self, mock_pyautogui_available, mock_automated_func):
        """Test automated mode when PyAutoGUI is available"""
        mock_pyautogui_available.return_value = True
        mock_automated_func.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }
        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot(issue, config)

        assert result is True
        mock_automated_func.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123", config)

    @patch("src.gh_pr_phase_monitor.issue_fetcher.is_pyautogui_available")
    def test_fails_when_pyautogui_not_available(self, mock_pyautogui_available):
        """Test failure when PyAutoGUI is not available"""
        mock_pyautogui_available.return_value = False

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }
        config = {"assign_to_copilot": {"wait_seconds": 5}}

        result = assign_issue_to_copilot(issue, config)

        assert result is False

    @patch("src.gh_pr_phase_monitor.issue_fetcher.assign_issue_to_copilot_automated")
    @patch("src.gh_pr_phase_monitor.issue_fetcher.is_pyautogui_available")
    def test_uses_pyautogui_when_available(self, mock_pyautogui_available, mock_automated_func):
        """Test uses PyAutoGUI when available"""
        mock_pyautogui_available.return_value = True
        mock_automated_func.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }

        result = assign_issue_to_copilot(issue, None)

        assert result is True
        mock_automated_func.assert_called_once_with("https://github.com/test-owner/test-repo/issues/123", None)

    @patch("src.gh_pr_phase_monitor.issue_fetcher.assign_issue_to_copilot_automated")
    @patch("src.gh_pr_phase_monitor.issue_fetcher.is_pyautogui_available")
    def test_works_with_config(self, mock_pyautogui_available, mock_automated_func):
        """Test automation works with config"""
        mock_pyautogui_available.return_value = True
        mock_automated_func.return_value = True

        issue = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "number": 123,
            "url": "https://github.com/test-owner/test-repo/issues/123",
        }
        config = {"assign_to_copilot": {}}

        result = assign_issue_to_copilot(issue, config)

        assert result is True
        mock_automated_func.assert_called_once()
