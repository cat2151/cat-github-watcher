"""
Tests for PR title fix functionality
"""

import subprocess
from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.comment_manager import (
    has_pr_title_fix_comment,
    has_problematic_pr_title,
    post_pr_title_fix_comment,
)


class TestHasProblematicPRTitle:
    """Test the has_problematic_pr_title function"""

    def test_addressing_pr_comments_exact_match(self):
        """Should detect 'Addressing PR comments'"""
        assert has_problematic_pr_title("Addressing PR comments") is True

    def test_addressing_pr_comments_case_insensitive(self):
        """Should detect case-insensitive variations"""
        assert has_problematic_pr_title("ADDRESSING PR COMMENTS") is True
        assert has_problematic_pr_title("addressing pr comments") is True
        assert has_problematic_pr_title("Addressing Pr Comments") is True

    def test_address_pr_comments_variation(self):
        """Should detect 'Address PR comments' variation"""
        assert has_problematic_pr_title("Address PR comments") is True
        assert has_problematic_pr_title("address pr comments") is True

    def test_pr_review_in_title(self):
        """Should detect titles containing 'PR review'"""
        assert (
            has_problematic_pr_title("Fix PR review comments: Tone.js vendoring, SMF parser, and optimizations") is True
        )
        assert has_problematic_pr_title("Update based on PR review") is True
        assert has_problematic_pr_title("Changes from pr review") is True

    def test_normal_title_not_detected(self):
        """Should not detect normal PR titles"""
        assert has_problematic_pr_title("Add new feature for user authentication") is False
        assert has_problematic_pr_title("Fix bug in payment processing") is False
        assert has_problematic_pr_title("Refactor database queries") is False

    def test_empty_title(self):
        """Should handle empty title"""
        assert has_problematic_pr_title("") is False
        assert has_problematic_pr_title(None) is False

    def test_title_with_review_but_not_pr_review(self):
        """Should not false positive on 'review' without 'PR'"""
        assert has_problematic_pr_title("Add code review checklist") is False
        assert has_problematic_pr_title("Review implementation") is False

    def test_title_with_pr_but_not_pr_review(self):
        """Should not false positive on 'PR' without 'review' or 'comments'"""
        assert has_problematic_pr_title("Add PR template") is False
        assert has_problematic_pr_title("Update PR workflow") is False


class TestHasPRTitleFixComment:
    """Test the has_pr_title_fix_comment function"""

    def test_comment_exists_for_claude(self):
        """Should detect existing fix comment for Claude agent"""
        comments = [
            {"body": "Some other comment"},
            {"body": "@claude[agent]\n- PR titleとPR冒頭を、以下の方針で修正してください：\n    - これまでの課題："},
        ]
        assert has_pr_title_fix_comment(comments) is True

    def test_comment_exists_for_codex(self):
        """Should detect existing fix comment for Codex agent"""
        comments = [
            {"body": "@codex[agent]\n- PR titleとPR冒頭を、以下の方針で修正してください：\n    - これまでの課題："}
        ]
        assert has_pr_title_fix_comment(comments) is True

    def test_comment_does_not_exist(self):
        """Should not detect when comment doesn't exist"""
        comments = [
            {"body": "Some comment"},
            {"body": "@claude[agent] apply changes"},
        ]
        assert has_pr_title_fix_comment(comments) is False

    def test_different_agent_mention_still_detected(self):
        """Should detect comment regardless of which agent mention is used"""
        comments = [
            {"body": "@claude[agent]\n- PR titleとPR冒頭を、以下の方針で修正してください：\n    - これまでの課題："}
        ]
        # Should be detected even with different agent mention - we only check marker text
        assert has_pr_title_fix_comment(comments) is True

    def test_empty_comments(self):
        """Should handle empty comment list"""
        assert has_pr_title_fix_comment([]) is False


class TestPostPRTitleFixComment:
    """Test the post_pr_title_fix_comment function"""

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_success_for_claude_agent(self, mock_run, mock_get_comments):
        """Should post comment successfully for Claude agent"""
        mock_get_comments.return_value = []
        mock_run.return_value = MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "title": "Addressing PR comments",
            "author": {"login": "anthropic-code-agent"},
        }

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is True
        assert mock_run.call_count == 1

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "pr"
        assert cmd[2] == "comment"
        assert cmd[3] == "https://github.com/user/repo/pull/123"
        assert cmd[4] == "--body"
        # Check for Claude mention
        assert "@claude[agent]" in cmd[5]
        assert "PR titleとPR冒頭を、以下の方針で修正してください：" in cmd[5]

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_success_for_codex_agent(self, mock_run, mock_get_comments):
        """Should post comment successfully for Codex agent"""
        mock_get_comments.return_value = []
        mock_run.return_value = MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/456",
            "title": "Fix PR review comments: various fixes",
            "author": {"login": "openai-code-agent"},
        }

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is True
        cmd = mock_run.call_args[0][0]
        # Check for Codex mention
        assert "@codex[agent]" in cmd[5]

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_skips_if_exists(self, mock_run, mock_get_comments):
        """Should skip posting if comment already exists"""
        mock_get_comments.return_value = [
            {"body": "@claude[agent]\n- PR titleとPR冒頭を、以下の方針で修正してください：\n    - これまでの課題："}
        ]

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "title": "Addressing PR comments",
            "author": {"login": "anthropic-code-agent"},
        }

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is None
        mock_run.assert_not_called()

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_failure(self, mock_run, mock_get_comments):
        """Should handle comment posting failure"""
        mock_get_comments.return_value = []
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        error.stderr = "Error: Failed to post comment"
        mock_run.side_effect = error

        pr = {
            "url": "https://github.com/user/repo/pull/999",
            "title": "Addressing PR comments",
            "author": {"login": "anthropic-code-agent"},
        }

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is False

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    def test_post_comment_no_url(self, mock_get_comments):
        """Should return False when PR has no URL"""
        mock_get_comments.return_value = []

        pr = {"title": "Addressing PR comments", "author": {"login": "anthropic-code-agent"}}

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is False

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_uses_configured_agent_name(self, mock_run, mock_get_comments):
        """Should use configured agent name override"""
        mock_get_comments.return_value = []
        mock_run.return_value = MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "title": "Addressing PR comments",
            "author": {"login": "some-user"},
        }
        config = {"coding_agent": {"agent_name": "@custom-agent"}}

        result = post_pr_title_fix_comment(pr, None, config)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "@custom-agent" in cmd[5]

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_handles_missing_stderr(self, mock_run, mock_get_comments):
        """Should handle missing stderr gracefully"""
        mock_get_comments.return_value = []
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        # Don't set stderr attribute
        mock_run.side_effect = error

        pr = {
            "url": "https://github.com/user/repo/pull/999",
            "title": "Addressing PR comments",
            "author": {"login": "anthropic-code-agent"},
        }

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is False

    @patch("src.gh_pr_phase_monitor.comment_manager.get_existing_comments")
    @patch("src.gh_pr_phase_monitor.comment_manager.subprocess.run")
    def test_post_comment_fallback_to_copilot(self, mock_run, mock_get_comments):
        """Should fall back to @copilot for unknown authors"""
        mock_get_comments.return_value = []
        mock_run.return_value = MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "title": "Addressing PR comments",
            "author": {"login": "human-user"},
        }

        result = post_pr_title_fix_comment(pr, None, None)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "@copilot" in cmd[5]
