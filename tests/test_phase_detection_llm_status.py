"""
Tests for LLM status-based phase detection (HTML snapshot analysis)
"""

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase.phase_detector import (
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)


class TestDeterminePhaseWithLLMStatus:
    """Tests for phase detection using LLM HTML status snapshots"""

    def test_llm_status_started_without_finish_stays_llm_working(self):
        """If started work is present without a later finished work, stay in LLM working."""
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "commentNodes": [
                {
                    "body": "Working on it",
                    "reactionGroups": [
                        {"content": "EYES", "users": {"totalCount": 1}},
                    ],
                }
            ],
            "reviewThreads": [],
            "repository": {"owner": "owner", "name": "repo"},
            "url": "https://github.com/owner/repo/pull/123",
            "title": "Test PR",
            "author": {"login": "octocat"},
            "llm_statuses": ["started work", "reviewing changes"],
        }

        # started work without finished work → LLM working
        assert determine_phase(pr) == PHASE_LLM_WORKING

    def test_llm_status_reviewing_started_finished_prefers_phase3_without_cache(self):
        """
        When LLM statuses show reviewing → started → finished but the reaction cache is empty,
        phase3 should still apply.
        """
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "commentNodes": [
                {
                    "body": "Working on it",
                    "reactionGroups": [
                        {"content": "EYES", "users": {"totalCount": 1}},
                    ],
                }
            ],
            "reviewThreads": [],
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

