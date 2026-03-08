"""
Tests for posting comments to PRs when phase2 is detected
"""

import json
import subprocess
from pathlib import Path

import pytest

from src.gh_pr_phase_monitor import (
    get_current_user,
    get_existing_comments,
    has_copilot_apply_comment,
    mark_pr_ready,
    post_phase2_comment,
)


class TestGetExistingComments:
    """Test the get_existing_comments function"""

    def test_get_comments_success(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_fetcher.subprocess.run")
        """Test successful retrieval of comments"""
        mock_run.return_value = mocker.MagicMock(returncode=0, stdout=json.dumps({"comments": [{"body": "Test comment"}]}))

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/tmp/test-repo")

        result = get_existing_comments(pr_url, repo_dir)

        assert len(result) == 1
        assert result[0]["body"] == "Test comment"

    def test_get_comments_failure(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_fetcher.subprocess.run")
        """Test handling of failure to retrieve comments"""
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "view"])

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = get_existing_comments(pr_url, repo_dir)

        assert result == []


class TestHasCopilotApplyComment:
    """Test the has_copilot_apply_comment function"""

    def test_comment_exists(self):
        """Test detection when comment exists"""
        comments = [
            {"body": "Some other comment"},
            {"body": "@copilot apply changes based on the comments"},
            {"body": "Another comment"},
        ]

        assert has_copilot_apply_comment(comments) is True

    def test_comment_does_not_exist(self):
        """Test detection when comment does not exist"""
        comments = [{"body": "Some other comment"}, {"body": "Another comment"}]

        assert has_copilot_apply_comment(comments) is False

    def test_comment_exists_for_claude_agent(self):
        """Test detection for Claude agent mention"""
        comments = [{"body": "@claude[agent] apply changes based on the comments"}]

        assert has_copilot_apply_comment(comments, "@claude[agent]") is True

    def test_empty_comments(self, mocker):
        """Test with empty comment list"""
        assert has_copilot_apply_comment([]) is False


class TestGetCurrentUser:
    """Test the get_current_user function"""

    def test_get_current_user_success(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.github_auth.subprocess.run")
        """Test successful retrieval of current user"""
        # Reset cache before test
        from src.gh_pr_phase_monitor.github import github_auth

        github_auth._current_user_cache = None

        mock_run.return_value = mocker.MagicMock(returncode=0, stdout="testuser\n")

        result = get_current_user()

        assert result == "testuser"
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd == ["gh", "api", "user", "--jq", ".login"]

    def test_get_current_user_failure(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.github_auth.subprocess.run")
        """Test handling of failure to retrieve current user"""
        # Reset cache before test
        from src.gh_pr_phase_monitor.github import github_auth

        github_auth._current_user_cache = None

        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "api", "user"])

        with pytest.raises(RuntimeError, match="Failed to retrieve current GitHub user"):
            get_current_user()

    def test_get_current_user_uses_cache(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.github_auth.subprocess.run")
        """Test that get_current_user uses cached value on subsequent calls"""
        # Reset cache before test
        from src.gh_pr_phase_monitor.github import github_auth

        github_auth._current_user_cache = None

        mock_run.return_value = mocker.MagicMock(returncode=0, stdout="testuser\n")

        # First call should execute subprocess
        result1 = get_current_user()
        assert result1 == "testuser"
        assert mock_run.call_count == 1

        # Second call should use cache, no additional subprocess call
        result2 = get_current_user()
        assert result2 == "testuser"
        assert mock_run.call_count == 1  # Still only called once

    def test_get_current_user_does_not_cache_failures(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.github_auth.subprocess.run")
        """Test that authentication failures are not cached, allowing retries"""
        # Reset cache before test
        from src.gh_pr_phase_monitor.github import github_auth

        github_auth._current_user_cache = None

        # First call fails
        mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["gh", "api", "user"])
        with pytest.raises(RuntimeError):
            get_current_user()
        assert mock_run.call_count == 1

        # Second call should retry (not use cached failure)
        mock_run.side_effect = None
        mock_run.return_value = mocker.MagicMock(returncode=0, stdout="testuser\n")
        result2 = get_current_user()
        assert result2 == "testuser"
        assert mock_run.call_count == 2  # Called twice, allowing retry


class TestPostPhase2Comment:
    """Test the post_phase2_comment function"""

    def test_post_comment_success(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Test successful comment posting"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": [{"author": {"login": "copilot"}}]}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is True
        assert mock_run.call_count == 1

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "gh"
        assert cmd[1] == "pr"
        assert cmd[2] == "comment"
        assert cmd[3] == "https://github.com/user/repo/pull/123"
        assert cmd[4] == "--body"
        assert "@copilot apply changes" in cmd[5]
        assert "this pull request" in cmd[5]

    def test_post_comment_skips_if_exists(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Test that comment posting is skipped if comment already exists"""
        mock_get_comments.return_value = [{"body": "@copilot apply changes based on the comments"}]

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is None
        mock_run.assert_not_called()

    def test_post_comment_failure(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Test failed comment posting"""
        mock_get_comments.return_value = []
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        error.stderr = "Error: PR not found"
        mock_run.side_effect = error

        pr = {"url": "https://github.com/user/repo/pull/999", "reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is False

    def test_post_comment_with_correct_cwd(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Test that comment posting works without requiring working directory"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": []}
        repo_dir = Path("/custom/repo/path")

        post_phase2_comment(pr, repo_dir)

        # Verify that subprocess.run was called without cwd parameter
        call_kwargs = mock_run.call_args[1]
        assert "cwd" not in call_kwargs

    def test_post_comment_no_url(self, mocker):
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Test handling of PR without URL"""
        mock_get_comments.return_value = []

        pr = {"reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is False

    def test_post_comment_handles_missing_stderr(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Test that missing stderr is handled gracefully"""
        mock_get_comments.return_value = []
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "comment"])
        # Don't set stderr attribute
        mock_run.side_effect = error

        pr = {"url": "https://github.com/user/repo/pull/999", "reviews": []}
        repo_dir = Path("/tmp/test-repo")

        result = post_phase2_comment(pr, repo_dir)

        assert result is False

    def test_post_comment_avoids_false_positive_claude_substring(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Ensure human users with claude substring still use copilot mention"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "author": {"login": "john-claude-smith"}, "reviews": []}

        result = post_phase2_comment(pr, None)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert cmd[5].startswith("@copilot apply changes")

    def test_post_comment_uses_configured_agent_name(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Ensure configured agent mention overrides defaults"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "author": {"login": "some-user"}, "reviews": []}
        config = {"coding_agent": {"agent_name": "@codex[agent]"}}

        result = post_phase2_comment(pr, None, config)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert cmd[5].startswith("@codex[agent] apply changes")

    def test_post_comment_handles_malformed_coding_agent_string(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Gracefully handle string coding_agent config by falling back to detection"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "author": {"login": "openai-code-agent"}, "reviews": []}
        config = {"coding_agent": "@codex[agent]"}

        result = post_phase2_comment(pr, None, config)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert cmd[5].startswith("@codex[agent] apply changes")

    def test_post_comment_handles_malformed_coding_agent_list(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Gracefully handle list coding_agent config by falling back to default"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "author": {"login": "human-user"}, "reviews": []}
        config = {"coding_agent": ["@codex[agent]"]}

        result = post_phase2_comment(pr, None, config)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert cmd[5].startswith("@copilot apply changes")

    def test_post_comment_skips_when_custom_agent_comment_exists(self, mocker):
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Ensure existing custom agent comment prevents duplicate posting"""
        mock_get_comments.return_value = [{"body": "@custom-agent apply changes based on the comments"}]

        pr = {"url": "https://github.com/user/repo/pull/123", "reviews": []}
        config = {"coding_agent": {"agent_name": "@custom-agent"}}

        result = post_phase2_comment(pr, None, config)

        assert result is None

    def test_post_comment_avoids_false_positive_codex_substring(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Ensure human users with codex substring still use copilot mention"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "author": {"login": "codex123"}, "reviews": []}

        result = post_phase2_comment(pr, None)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert cmd[5].startswith("@copilot apply changes")

    def test_post_comment_uses_openai_code_agent(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Ensure openai-code-agent PR uses codex mention"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {"url": "https://github.com/user/repo/pull/123", "author": {"login": "openai-code-agent"}, "reviews": []}

        result = post_phase2_comment(pr, None)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "@codex[agent] apply changes" in cmd[5]

    def test_post_comment_uses_anthropic_code_agent(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        """Ensure anthropic-code-agent PR uses claude mention"""
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "author": {"login": "anthropic-code-agent"},
            "reviews": [],
        }

        result = post_phase2_comment(pr, None)

        assert result is True
        cmd = mock_run.call_args[0][0]
        assert "@claude[agent] apply changes" in cmd[5]

    def test_post_comment_blocked_by_safety_check_when_button_absent(self, mocker):
        """Safety check: comment must NOT be sent when has_implement_suggestions_button is False."""
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "reviews": [],
            "has_implement_suggestions_button": False,
        }

        result = post_phase2_comment(pr, None)

        assert result is None
        mock_run.assert_not_called()

    def test_post_comment_allowed_when_button_present(self, mocker):
        """Safety check passes: comment sent when has_implement_suggestions_button is True."""
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "reviews": [],
            "has_implement_suggestions_button": True,
        }

        result = post_phase2_comment(pr, None)

        assert result is True
        mock_run.assert_called_once()

    def test_post_comment_skips_safety_check_when_key_absent(self, mocker):
        """When has_implement_suggestions_button key is missing (HTML not analyzed), comment is allowed."""
        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.subprocess.run")
        mock_get_comments = mocker.patch("src.gh_pr_phase_monitor.github.comment_manager.get_existing_comments")
        mock_get_comments.return_value = []
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr = {
            "url": "https://github.com/user/repo/pull/123",
            "reviews": [],
            # key intentionally absent
        }

        result = post_phase2_comment(pr, None)

        assert result is True
        mock_run.assert_called_once()


class TestMarkPRReady:
    """Test the mark_pr_ready function"""

    def test_mark_pr_ready_success(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.actions.pr_actions.subprocess.run")
        """Test successful marking of PR as ready for review"""
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/tmp/test-repo")

        result = mark_pr_ready(pr_url, repo_dir)

        assert result is True
        assert mock_run.call_count == 1

        # Verify command arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd == ["gh", "pr", "ready", "https://github.com/user/repo/pull/123"]

    def test_mark_pr_ready_failure(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.actions.pr_actions.subprocess.run")
        """Test failed marking of PR as ready"""
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "ready"])
        error.stderr = "Error: PR not found or not a draft"
        mock_run.side_effect = error

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = mark_pr_ready(pr_url, repo_dir)

        assert result is False

    def test_mark_pr_ready_with_correct_cwd(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.actions.pr_actions.subprocess.run")
        """Test that PR ready marking works without requiring working directory"""
        mock_run.return_value = mocker.MagicMock(returncode=0)

        pr_url = "https://github.com/user/repo/pull/123"
        repo_dir = Path("/custom/repo/path")

        mark_pr_ready(pr_url, repo_dir)

        # Verify that subprocess.run was called without cwd parameter
        call_kwargs = mock_run.call_args[1]
        assert "cwd" not in call_kwargs

    def test_mark_pr_ready_handles_missing_stderr(self, mocker):
        mock_run = mocker.patch("src.gh_pr_phase_monitor.actions.pr_actions.subprocess.run")
        """Test that missing stderr is handled gracefully"""
        error = subprocess.CalledProcessError(returncode=1, cmd=["gh", "pr", "ready"])
        # Don't set stderr attribute
        mock_run.side_effect = error

        pr_url = "https://github.com/user/repo/pull/999"
        repo_dir = Path("/tmp/test-repo")

        result = mark_pr_ready(pr_url, repo_dir)

        assert result is False
