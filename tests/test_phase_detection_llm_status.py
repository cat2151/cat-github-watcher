"""
Tests for LLM status-based phase detection (HTML snapshot analysis)
"""

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase.phase_detector import (
    PHASE_2,
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)


class TestDeterminePhaseWithLLMStatus:
    """Tests for phase detection using LLM statuses extracted from HTML"""

    def test_no_reviewing_event_in_llm_statuses_returns_llm_working(self):
        """When llm_statuses has no reviewing event, phase is LLM working."""
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "commentNodes": [],
            "repository": {"owner": "owner", "name": "repo"},
            "url": "https://github.com/owner/repo/pull/123",
            "title": "Test PR",
            "author": {"login": "octocat"},
            "llm_statuses": ["started work"],
        }

        assert determine_phase(pr) == PHASE_LLM_WORKING

    def test_reviewing_started_without_finish_returns_phase2(self):
        """When reviewing occurred but finished work has not followed, phase is 2."""
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "commentNodes": [],
            "repository": {"owner": "owner", "name": "repo"},
            "url": "https://github.com/owner/repo/pull/124",
            "title": "Test PR",
            "author": {"login": "octocat"},
            "llm_statuses": [
                "Copilot started reviewing on behalf of cat2151",
                "Codex started work on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == PHASE_2

    def test_reviewing_started_finished_returns_phase3(self):
        """When reviewing → started work → finished work all present, phase is 3."""
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "commentNodes": [],
            "repository": {"owner": "owner", "name": "repo"},
            "url": "https://github.com/owner/repo/pull/456",
            "title": "Test PR",
            "author": {"login": "octocat"},
            "llm_statuses": [
                "Copilot started reviewing on behalf of cat2151",
                "Codex started work on behalf of cat2151",
                "Codex finished work on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == PHASE_3

