"""
Tests for open_browser cooldown functionality in pr_actions
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestOpenBrowserCooldown:
    """Test open_browser cooldown functionality"""

    def setup_method(self):
        """Reset cooldown state before each test"""
        from src.gh_pr_phase_monitor import browser_cooldown as bc

        bc._last_browser_open_time = None
        pr_actions._browser_opened.clear()

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_open_browser_returns_true_on_success(self, mock_time, mock_webbrowser):
        """Test that open_browser returns True when browser is opened"""
        from src.gh_pr_phase_monitor.pr_actions import open_browser

        mock_time.return_value = 0.0

        result = open_browser("https://github.com/test/repo/pull/1")

        assert result is True
        mock_webbrowser.open.assert_called_once()

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_open_browser_respects_cooldown(self, mock_time, mock_webbrowser):
        """Test that open_browser respects the 60-second cooldown"""
        from src.gh_pr_phase_monitor.pr_actions import open_browser

        # First call - should succeed
        mock_time.return_value = 0.0
        result1 = open_browser("https://github.com/test/repo/pull/1")
        assert result1 is True

        # Second call immediately after - should fail
        mock_time.return_value = 1.0
        result2 = open_browser("https://github.com/test/repo/pull/2")
        assert result2 is False

        # Third call after cooldown - should succeed
        mock_time.return_value = 61.0
        result3 = open_browser("https://github.com/test/repo/pull/3")
        assert result3 is True

        # Verify browser was only opened twice
        assert mock_webbrowser.open.call_count == 2

    @patch("src.gh_pr_phase_monitor.pr_actions.webbrowser")
    @patch("src.gh_pr_phase_monitor.browser_cooldown.time.time")
    def test_process_pr_phase3_respects_cooldown(self, mock_time, mock_webbrowser):
        """Test that process_pr respects cooldown when opening browser for phase3"""
        pr_actions._browser_opened.clear()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED",
                    "body": "LGTM",
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED",
                }
            ],
            "reviewRequests": [],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
            "llm_statuses": ["Copilot started reviewing", "Copilot started work", "Copilot finished work"],
        }

        # First PR - should open browser
        mock_time.return_value = 0.0
        process_pr(pr, None)
        assert mock_webbrowser.open.call_count == 1

        # Clear the tracking but keep the cooldown
        pr_actions._browser_opened.clear()

        # Second PR immediately after - should not open browser due to cooldown
        pr2 = pr.copy()
        pr2["url"] = "https://github.com/test-owner/test-repo/pull/2"
        mock_time.return_value = 1.0
        process_pr(pr2, None)
        # Still only 1 call because cooldown prevented the second open
        assert mock_webbrowser.open.call_count == 1

        # Third PR after cooldown - should open browser
        pr3 = pr.copy()
        pr3["url"] = "https://github.com/test-owner/test-repo/pull/3"
        mock_time.return_value = 61.0
        process_pr(pr3, None)
        assert mock_webbrowser.open.call_count == 2
