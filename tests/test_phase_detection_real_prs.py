"""
Tests for phase detection with real PR scenarios and LLM statuses
"""

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase_detector import (
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)


class TestDeterminePhaseRealPRs:
    """Tests for phase detection using real PR scenarios"""

    def test_backward_compatibility_with_integer_comments(self):
        """PR with integer comments (legacy API) should work correctly"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files in this pull request and generated 1 comment.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": 5,  # Legacy API returns integer
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            ],
        }

        assert determine_phase(pr) == "phase2"

    def test_phase3_when_copilot_swe_agent_after_commented_review(self):
        """When copilot-swe-agent posts after copilot-pull-request-reviewer with COMMENTED review, should be phase3.
        COMMENTED indicates suggestions rather than blocking changes, so even one swe-agent review indicates completion."""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files in this pull request and generated 3 comments.",
                },
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": "Addressed the comments"},
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            ],
        }

        # Should be phase3 because reviewer used COMMENTED (suggestions only), not CHANGES_REQUESTED
        assert determine_phase(pr) == "phase3"

    def test_phase2_when_copilot_swe_agent_after_changes_requested(self):
        """When copilot-swe-agent posts after copilot-pull-request-reviewer with CHANGES_REQUESTED, should be phase2 not phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please address these issues",
                },
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": "Addressing the issues"},
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
        }

        # Should be phase2 because there are unresolved CHANGES_REQUESTED from copilot-pull-request-reviewer
        assert determine_phase(pr) == "phase2"

    def test_phase3_when_copilot_swe_agent_after_resolved_reviews(self):
        """When copilot-pull-request-reviewer posts multiple reviews and most recent has no issues, should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED",
                    "body": "Please address these issues",
                },
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": "Addressing the issues"},
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good now",  # No inline comments
                },
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": "Made final improvements"},
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
            "reviewThreads": [],  # All threads resolved
        }

        # Should be phase3 because the most recent review from copilot-pull-request-reviewer has no issues
        assert determine_phase(pr) == "phase3"

    def test_real_pr_74_scenario(self):
        """Real scenario from PR #74: review body without 'generated N comments' but has unresolved threads"""
        # This is the actual data from PR cat2151/cat-oscilloscope#74
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nこのPRは、デバッグ波形表示の視認性を向上させるため...",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "commentNodes": [],
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            ],
        }

        # Should be phase2 because there are 7 unresolved review threads
        # even though the review body doesn't contain "generated N comments" text
        assert determine_phase(pr) == "phase2"

    def test_phase3_copilot_swe_agent_with_old_unresolved_threads_but_new_reviewer_commented(self):
        """
        Re-review scenario: When copilot-swe-agent is latest reviewer with old unresolved threads,
        but a subsequent copilot-pull-request-reviewer review has COMMENTED state (no CHANGES_REQUESTED).
        This indicates the reviewer is satisfied after re-reviewing, so it should be phase3.
        """
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 2 out of 2 changed files and generated 3 comments.",
                },
                {
                    "author": {"login": "copilot-swe-agent"},
                    "state": "COMMENTED",
                    "body": "Working on addressing the review comments",
                },
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good now!",
                },
                {
                    "author": {"login": "copilot-swe-agent"},
                    "state": "COMMENTED",
                    "body": "Made final changes",
                },
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
            # Old threads from first review that are technically still unresolved
            # but don't need attention because latest copilot-pull-request-reviewer review
            # doesn't have CHANGES_REQUESTED
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            ],
        }

        # Should be phase3 because the most recent copilot-pull-request-reviewer review (review #3)
        # has state COMMENTED (not CHANGES_REQUESTED), indicating acceptance
        assert determine_phase(pr) == "phase3"

    def test_phase3_real_pr_26_pattern_multiple_swe_agent_reviews(self):
        """
        Real scenario from PR wavlpf#26: 1 copilot-pull-request-reviewer review with COMMENTED state
        followed by multiple copilot-swe-agent reviews (6 in real case) with unresolved threads.
        No re-review from reviewer, but multiple swe-agent reviews indicate completion.
        Should be phase3 because reviewer used COMMENTED (suggestions only) and swe-agent completed work.
        """
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Copilot reviewed 4 out of 4 changed files and generated 7 comments.",
                },
                # 6 swe-agent reviews posted simultaneously (as in real PR #26)
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": ""},
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": ""},
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": ""},
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": ""},
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": ""},
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": ""},
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
            # Real PR #26 had 7 threads: 6 outdated, 1 not outdated (test coverage suggestion)
            "reviewThreads": [
                {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 2}},
                {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 2}},
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},  # Test coverage suggestion
                {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 2}},
                {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 2}},
                {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 2}},
                {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 2}},
            ],
        }

        # Should be phase3 because:
        # 1. Reviewer used COMMENTED (not CHANGES_REQUESTED) - suggestions only
        # 2. Multiple swe-agent reviews (6) indicate completion
        # 3. Only 1 non-outdated thread remains (test coverage suggestion - non-blocking)
        assert determine_phase(pr) == "phase3"

    def test_phase3_real_pr_61_pattern_single_swe_agent_review_commented(self):
        """
        Real scenario from PR 61: 1 copilot-pull-request-reviewer review with COMMENTED state
        followed by 1 copilot-swe-agent review responding to the review comment.
        Should be phase3 because reviewer used COMMENTED (suggestions only), not CHANGES_REQUESTED.
        With COMMENTED, even a single swe-agent review indicates the agent has addressed the feedback.
        """
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR improves the visibility...",
                },
                {
                    "author": {"login": "copilot-swe-agent"},
                    "state": "COMMENTED",
                    "body": "",  # Real PR 61 has empty body
                },
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
            # 1 unresolved thread with 2 comments (reviewer comment + swe-agent response)
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 2}},
            ],
        }

        # Should be phase3 because:
        # 1. Reviewer used COMMENTED (not CHANGES_REQUESTED) - suggestions only
        # 2. Swe-agent posted a review responding to the feedback
        # 3. With COMMENTED state, even one swe-agent review indicates completion
        assert determine_phase(pr) == "phase3"

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

    def test_llm_working_when_statuses_show_started_without_finish_after_reviewing(self):
        """
        If LLM statuses show reviewing but the last started work has no finished work,
        remain in LLM working.
        """
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": [],
            "commentNodes": [],
            "reviewThreads": [],
            "llm_statuses": [
                "Copilot started reviewing on behalf of cat2151",
                "Codex started work on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == PHASE_LLM_WORKING

    def test_llm_working_when_reviewing_after_finished_work(self):
        """
        If reviewing occurs after the last finished work (e.g., finished → reviewing),
        this should NOT be detected as phase3 — still actively reviewing.
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
                "Copilot started reviewing on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == PHASE_LLM_WORKING

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
