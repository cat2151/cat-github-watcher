"""
Tests for phase detection with real PR scenarios and LLM statuses
"""

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase.phase_detector import (
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)


class TestDeterminePhaseRealPRs:
    """Tests for phase detection using real PR scenarios"""

    def test_phase3_from_llm_statuses_when_reviews_empty(self):
        """
        Reproduce issue: LLM statuses show reviewing → (started+finished) pairs all complete,
        but GraphQL reviews data is empty. Should detect phase3 from LLM statuses.

        Timeline from the bug report:
          1. Codex started work
          2. Codex finished work
          3. Copilot started reviewing
          4. Codex started work
          5. Codex finished work
          6. Codex started work
          7. Codex finished work
        """
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": [],
            "commentNodes": [],
            "reviewThreads": [],
            "llm_statuses": [
                "Codex started work on behalf of cat2151 February 8, 2026 23:29",
                "Codex finished work on behalf of cat2151 February 8, 2026 23:33",
                "Copilot started reviewing on behalf of cat2151 February 8, 2026 23:34",
                "Codex started work on behalf of cat2151 February 8, 2026 23:36",
                "Codex finished work on behalf of cat2151 February 8, 2026 23:37",
                "Codex started work on behalf of cat2151 February 8, 2026 23:38",
                "Codex finished work on behalf of cat2151 February 8, 2026 23:38",
            ],
        }

        assert determine_phase(pr) == PHASE_3

    def test_phase3_from_llm_statuses_when_reviewer_unknown(self):
        """
        When the latest review is by an unknown author but LLM statuses
        show reviewing followed by completed work, detect phase3.
        """
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "some-other-bot"}, "state": "COMMENTED", "body": ""},
            ],
            "latestReviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED"}],
            "commentNodes": [],
            "reviewThreads": [],
            "llm_statuses": [
                "Copilot started reviewing on behalf of cat2151",
                "Codex started work on behalf of cat2151",
                "Codex finished work on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == PHASE_3

    def test_llm_working_when_statuses_have_no_reviewing(self):
        """
        Without a reviewing event, finished work alone should not produce phase3.
        """
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": [],
            "commentNodes": [],
            "reviewThreads": [],
            "llm_statuses": [
                "Codex started work on behalf of cat2151",
                "Codex finished work on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == PHASE_LLM_WORKING

