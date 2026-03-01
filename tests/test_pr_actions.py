"""
Tests for PR actions including browser opening behavior
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor import pr_actions
from src.gh_pr_phase_monitor.colors import colorize_url
from src.gh_pr_phase_monitor.phase_detector import PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING
from src.gh_pr_phase_monitor.pr_actions import process_pr


class TestProcessPR:
    """Test the process_pr function"""

    def setup_method(self):
        """Clear the browser opened and notification tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()

    def test_browser_not_opened_for_phase1(self):
        """Browser should not open for phase1"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {"enable_execution_phase1_to_phase2": True}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser,
            patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready,
        ):
            mock_ready.return_value = True
            process_pr(pr, config)
            # Browser should not be called for phase1
            mock_browser.assert_not_called()

    def test_browser_not_opened_for_phase2(self):
        """Browser should not open for phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please address these issues",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {"enable_execution_phase2_to_phase3": True}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser,
            patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment,
        ):
            mock_comment.return_value = True
            process_pr(pr, config)
            # Browser should not be called for phase2
            mock_browser.assert_not_called()

    def test_browser_opened_for_phase3(self):
        """Browser should open for phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            config = {}
            process_pr(pr, config)
            # Browser should be called for phase3 with URL and config
            mock_browser.assert_called_once_with("https://github.com/test-owner/test-repo/pull/1", config)

    def test_browser_not_opened_for_llm_working(self):
        """Browser should not open for 'LLM working' phase"""
        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": [],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            process_pr(pr, {})
            # Browser should not be called for LLM working
            mock_browser.assert_not_called()

    def test_author_hidden_by_default(self, capsys):
        """Author login should be hidden when display_pr_author is not enabled"""
        pr = {
            "author": {"login": "phase2-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Phase2 PR",
            "url": "https://github.com/test-owner/test-repo/pull/2",
        }

        process_pr(pr, {}, phase=PHASE_2)
        output = capsys.readouterr().out
        assert "Author:" not in output

    def test_author_displayed_for_phase2(self, capsys):
        """Author login should be printed for phase2 when enabled"""
        pr = {
            "author": {"login": "phase2-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Phase2 PR",
            "url": "https://github.com/test-owner/test-repo/pull/2",
        }

        process_pr(pr, {"display_pr_author": True}, phase=PHASE_2)
        output = capsys.readouterr().out
        assert "Author: phase2-author" in output

    def test_author_displayed_for_phase3(self, capsys):
        """Author login should be printed for phase3 when enabled"""
        pr = {
            "author": {"login": "phase3-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Phase3 PR",
            "url": "https://github.com/test-owner/test-repo/pull/3",
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            mock_browser.return_value = True
            process_pr(pr, {"display_pr_author": True}, phase=PHASE_3)

        output = capsys.readouterr().out
        assert "Author: phase3-author" in output

    def test_author_displayed_for_phase1(self, capsys):
        """Author login should be printed for phase1 when enabled"""
        pr = {
            "author": {"login": "phase1-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Phase1 PR",
            "url": "https://github.com/test-owner/test-repo/pull/4",
        }

        process_pr(pr, {"display_pr_author": True}, phase=PHASE_1)
        output = capsys.readouterr().out
        assert "Author: phase1-author" in output

    def test_author_displayed_for_llm_working(self, capsys):
        """Author login should be printed for LLM working when enabled"""
        pr = {
            "author": {"login": "llm-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "LLM PR",
            "url": "https://github.com/test-owner/test-repo/pull/5",
        }

        process_pr(pr, {"display_pr_author": True}, phase=PHASE_LLM_WORKING)
        output = capsys.readouterr().out
        assert "Author: llm-author" in output

    def test_process_pr_colors_url(self, capsys):
        """PR URL should be colorized for better visibility"""
        url = "https://github.com/test-owner/test-repo/pull/2"
        pr = {
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Colored URL PR",
            "url": url,
        }

        process_pr(pr, {}, phase=PHASE_1)
        output = capsys.readouterr().out
        colored_url = colorize_url(url)
        assert f"URL: {colored_url}" in output

    def test_llm_working_progress_displayed(self, capsys):
        """LLM working output should describe completed phases"""
        pr = {
            "author": {"login": "llm-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "LLM PR",
            "url": "https://github.com/test-owner/test-repo/pull/5",
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED",
                    "body": "Looks good!",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
        }

        process_pr(pr, {}, phase=PHASE_LLM_WORKING)
        output = capsys.readouterr().out
        assert "Phase 2 completed, LLM working" in output

    def test_llm_working_shows_latest_status(self, capsys):
        """LLM working output should include the latest LLM status"""
        pr = {
            "author": {"login": "llm-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "LLM PR",
            "url": "https://github.com/test-owner/test-repo/pull/6",
            "llm_statuses": ["started work on files", "finished work on feedback"],
        }

        process_pr(pr, {}, phase=PHASE_LLM_WORKING)
        output = capsys.readouterr().out
        assert "Latest LLM status: finished work on feedback" in output

    def test_llm_working_lists_statuses_when_progress_completed(self, capsys):
        """LLM working should list captured statuses when progress label shows completion"""
        pr = {
            "author": {"login": "llm-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "LLM PR",
            "url": "https://github.com/test-owner/test-repo/pull/6",
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "needs work",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
            "llm_statuses": ["started work on files", "finished work items"],
        }

        process_pr(pr, {"display_llm_status_timeline": True}, phase=PHASE_LLM_WORKING)
        output = capsys.readouterr().out
        assert "LLM status timeline" in output
        assert "1. started work on files" in output
        assert "2. finished work items" in output

    def test_llm_working_timeline_hidden_by_default(self, capsys):
        """LLM status timeline should not render unless enabled in config"""
        pr = {
            "author": {"login": "llm-author"},
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "LLM PR",
            "url": "https://github.com/test-owner/test-repo/pull/6",
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "needs work",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
            "llm_statuses": ["started work on files", "finished work items"],
        }

        process_pr(pr, {}, phase=PHASE_LLM_WORKING)
        output = capsys.readouterr().out
        assert "LLM status timeline" not in output

    def test_browser_opened_only_once_for_phase3(self):
        """Browser should open only once for phase3, even if called multiple times"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }

        with patch("src.gh_pr_phase_monitor.pr_actions.open_browser") as mock_browser:
            # First call should open browser
            process_pr(pr, {})
            assert mock_browser.call_count == 1

            # Second call should not open browser again
            process_pr(pr, {})
            assert mock_browser.call_count == 1

            # Third call should still not open browser
            process_pr(pr, {})
            assert mock_browser.call_count == 1


class TestPhase3Notifications:
    """Test notification behavior for phase3"""

    def setup_method(self):
        """Clear tracking before each test"""
        pr_actions._browser_opened.clear()
        pr_actions._notifications_sent.clear()

    def test_notification_sent_when_enabled(self):
        """Notification should be sent when enabled in config"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "ntfy": {"enabled": True, "topic": "test-topic", "message": "PR ready: {url}"},
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            mock_notify.return_value = True
            process_pr(pr, config)
            # Notification should be sent
            mock_notify.assert_called_once_with(config, "https://github.com/test-owner/test-repo/pull/1", "Test PR")

    def test_notification_not_sent_when_disabled(self):
        """Notification should not be sent when disabled in config"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {"ntfy": {"enabled": False, "topic": "test-topic"}}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            process_pr(pr, config)
            # Notification should not be sent
            mock_notify.assert_not_called()

    def test_notification_not_sent_when_no_config(self):
        """Notification should not be sent when ntfy not in config"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {}

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            process_pr(pr, config)
            # Notification should not be sent
            mock_notify.assert_not_called()

    def test_notification_sent_only_once(self):
        """Notification should be sent only once per PR"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "ntfy": {"enabled": True, "topic": "test-topic", "message": "PR ready: {url}"},
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
        ):
            mock_notify.return_value = True
            # First call should send notification
            process_pr(pr, config)
            assert mock_notify.call_count == 1

            # Second call should not send notification again
            process_pr(pr, config)
            assert mock_notify.call_count == 1

            # Third call should still not send notification
            process_pr(pr, config)
            assert mock_notify.call_count == 1

    def test_notification_not_sent_for_phase1(self):
        """Notification should not be sent for phase1"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "enable_execution_phase1_to_phase2": True,
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
            patch("src.gh_pr_phase_monitor.pr_actions.mark_pr_ready") as mock_ready,
        ):
            mock_ready.return_value = True
            process_pr(pr, config)
            # Notification should not be sent for phase1
            mock_notify.assert_not_called()

    def test_notification_not_sent_for_phase2(self):
        """Notification should not be sent for phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please fix",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "CHANGES_REQUESTED"}],
            "repository": {"name": "test-repo", "owner": "test-owner"},
            "title": "Test PR",
            "url": "https://github.com/test-owner/test-repo/pull/1",
        }
        config = {
            "ntfy": {"enabled": True, "topic": "test-topic"},
            "enable_execution_phase2_to_phase3": True,
        }

        with (
            patch("src.gh_pr_phase_monitor.pr_actions.open_browser"),
            patch("src.gh_pr_phase_monitor.pr_actions.send_phase3_notification") as mock_notify,
            patch("src.gh_pr_phase_monitor.pr_actions.post_phase2_comment") as mock_comment,
        ):
            mock_comment.return_value = True
            process_pr(pr, config)
            # Notification should not be sent for phase2
            mock_notify.assert_not_called()


