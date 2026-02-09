"""
Tests for PR phase detection logic

Tests cover the following scenarios:
- Phase 1: Draft PRs
- Phase 2: Copilot reviewer with comments/changes requested
- Phase 3: Copilot reviewer approved or no comments, copilot-swe-agent modifications
- LLM working: No reviews, unknown reviewers, or comments with reactions
"""

import copy
from datetime import datetime
from unittest.mock import patch

from src.gh_pr_phase_monitor import determine_phase, has_comments_with_reactions, has_unresolved_review_threads
from src.gh_pr_phase_monitor.phase_detector import (
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)
from src.gh_pr_phase_monitor.pr_data_recorder import record_reaction_snapshot, reset_snapshot_cache


class TestHasUnresolvedReviewThreads:
    """Test the has_unresolved_review_threads function"""

    def test_no_threads(self):
        """Empty threads list should return False"""
        assert has_unresolved_review_threads([]) is False

    def test_none_threads(self):
        """None threads should return False"""
        assert has_unresolved_review_threads(None) is False

    def test_all_resolved_threads(self):
        """All resolved threads should return False"""
        threads = [
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is False

    def test_unresolved_thread(self):
        """Unresolved thread should return True"""
        threads = [
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is True

    def test_mixed_resolved_unresolved(self):
        """Mix of resolved and unresolved should return True"""
        threads = [
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is True

    def test_outdated_unresolved_thread(self):
        """Outdated unresolved thread should return False (outdated doesn't need fixes)"""
        threads = [
            {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is False

    def test_multiple_unresolved_threads(self):
        """Multiple unresolved threads should return True"""
        threads = [
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is True

    def test_thread_without_comments_field(self):
        """Thread without comments field should be handled gracefully"""
        threads = [
            {"isResolved": False, "isOutdated": False},  # No comments field
        ]
        # Should still return True based on isResolved status
        assert has_unresolved_review_threads(threads) is True

    def test_mixed_threads_with_and_without_comments_field(self):
        """Mix of threads with and without comments field should work correctly"""
        threads = [
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False},  # No comments field
        ]
        # Should return True because there's an unresolved thread
        assert has_unresolved_review_threads(threads) is True


class TestHasCommentsWithReactions:
    """Test the has_comments_with_reactions function"""

    def test_no_comments(self):
        """Empty comments list should return False"""
        assert has_comments_with_reactions([]) is False

    def test_comments_without_reactions(self):
        """Comments without reactionGroups should return False"""
        comments = [
            {"body": "Test comment 1"},
            {"body": "Test comment 2"},
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_empty_reaction_groups(self):
        """Comments with empty reactionGroups should return False"""
        comments = [
            {"body": "Test comment", "reactionGroups": []},
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_zero_count_reactions(self):
        """Comments with reactionGroups but zero users should return False"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 0}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_reactions(self):
        """Comments with non-empty reactionGroups should return True"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 1}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_multiple_comments_with_reactions(self):
        """Multiple comments, one with reactions should return True"""
        comments = [
            {"body": "Test comment 1"},
            {
                "body": "Test comment 2",
                "reactionGroups": [
                    {"content": "EYES", "users": {"totalCount": 2}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_multiple_reaction_groups(self):
        """Comment with multiple reaction groups should return True"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 0}},
                    {"content": "EYES", "users": {"totalCount": 1}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_backward_compatibility_with_integer(self):
        """Integer comments (from legacy API) should return False"""
        assert has_comments_with_reactions(5) is False

    def test_backward_compatibility_with_none(self):
        """None comments should return False"""
        assert has_comments_with_reactions(None) is False


class TestDeterminePhase:
    """Test the determine_phase function"""

    def test_phase1_draft_pr(self):
        """Draft PRs with reviewRequests should be phase1"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [{"login": "user1"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase1"

    def test_llm_working_draft_pr_no_review_requests(self):
        """Draft PRs with no reviewRequests should be 'LLM working'"""
        pr = {"isDraft": True, "reviews": [], "latestReviews": [], "reviewRequests": [], "comments": []}
        assert determine_phase(pr) == "LLM working"

    def test_llm_working_no_reviews(self):
        """PRs with no reviews should be 'LLM working'"""
        pr = {"isDraft": False, "reviews": [], "latestReviews": [], "comments": []}
        assert determine_phase(pr) == "LLM working"

    def test_phase3_copilot_reviewer_commented_with_summary(self):
        """Copilot reviewer with COMMENTED state and summary body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR adds comprehensive documentation.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_approved(self):
        """Copilot reviewer with APPROVED state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED", "body": "Looks good!"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_no_body(self):
        """Copilot reviewer with no review body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED", "body": ""}],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_whitespace_only_body(self):
        """Copilot reviewer with only whitespace in body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED", "body": "   \n  \t  "}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_swe_agent(self):
        """Copilot SWE agent as latest reviewer should be phase3 when previous review had no inline comments"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good overall",  # No inline comments
                },
                {"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED", "body": "Made some improvements"},
            ],
            "latestReviews": [{"author": {"login": "copilot-swe-agent"}, "state": "COMMENTED"}],
            "commentNodes": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_llm_working_unknown_reviewer(self):
        """Unknown reviewer should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED", "body": "Some comment"}],
            "latestReviews": [{"author": {"login": "some-other-bot"}, "state": "COMMENTED"}],
            "comments": [],
        }
        assert determine_phase(pr) == "LLM working"

    def test_phase2_changes_requested(self):
        """Copilot reviewer with CHANGES_REQUESTED should be phase2"""
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
            "comments": [],
        }
        assert determine_phase(pr) == "phase2"

    def test_phase3_copilot_reviewer_dismissed(self):
        """Copilot reviewer with DISMISSED state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "DISMISSED", "body": "Review dismissed"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "DISMISSED"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_pending(self):
        """Copilot reviewer with PENDING state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {"author": {"login": "copilot-pull-request-reviewer"}, "state": "PENDING", "body": "Review pending"}
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "PENDING"}],
            "comments": [],
        }
        assert determine_phase(pr) == "phase3"

    def test_phase2_copilot_reviewer_commented_with_review_comments(self):
        """Copilot reviewer with COMMENTED state and inline review comments should be phase2"""
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
            "comments": [],
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            ],
        }

        assert determine_phase(pr) == "phase2"

    def test_phase3_copilot_reviewer_commented_without_review_comments(self):
        """Copilot reviewer with COMMENTED state but no inline review comments should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR looks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "comments": [],
            "reviewThreads": [],  # No review threads
        }

        assert determine_phase(pr) == "phase3"

    def test_llm_working_when_comments_have_reactions(self):
        """PR with comments that have reactions should be 'LLM working'"""
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
            "commentNodes": [
                {
                    "body": "Please fix this issue",
                    "reactionGroups": [
                        {"content": "EYES", "users": {"totalCount": 1}},
                    ],
                }
            ],
        }

        assert determine_phase(pr) == "LLM working"

    def test_phase2_when_comments_without_reactions(self):
        """PR with review comments but no reactions should still be phase2"""
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
            "commentNodes": [
                {"body": "Please fix this issue", "reactionGroups": []},
            ],
            "reviewThreads": [
                {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            ],
        }

        assert determine_phase(pr) == "phase2"

    def test_llm_working_phase3_scenario_with_reactions(self):
        """PR that would be phase3 but has comments with reactions should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nThis PR looks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
            "commentNodes": [
                {
                    "body": "Some comment",
                    "reactionGroups": [
                        {"content": "ROCKET", "users": {"totalCount": 1}},
                    ],
                }
            ],
        }

        assert determine_phase(pr) == "LLM working"

    def test_llm_status_finished_via_html_allows_phase3(self, tmp_path):
        """
        When reactions remain but LLM status shows finished work after starting, phase3 should apply.
        """
        reset_snapshot_cache(clear_content_cache=True)
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
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
        }

        # Initial detection still marks LLM working because reactions are present
        assert determine_phase(pr) == PHASE_LLM_WORKING

        html_content = """
        <div class="prc-PageLayout-Content-xWL-A">
            <p>LLM status: started work</p>
            <p>LLM status: finished work</p>
        </div>
        """
        current_time = datetime(2024, 1, 2, 3, 4, 5)
        snapshot_paths = record_reaction_snapshot(
            pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time, html_content=html_content
        )
        assert snapshot_paths is not None

        # After snapshot analysis, reactions are considered finished and phase3 logic applies
        assert determine_phase(pr) == PHASE_3

    def test_llm_status_started_without_finish_stays_llm_working(self, tmp_path):
        """If started work is present without a later finished work, stay in LLM working."""
        reset_snapshot_cache(clear_content_cache=True)
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
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
        }

        assert determine_phase(pr) == PHASE_LLM_WORKING

        html_content = """
        <div class="prc-PageLayout-Content-xWL-A">
            <p>LLM status: started work</p>
            <p>LLM status: reviewing changes</p>
        </div>
        """
        current_time = datetime(2024, 1, 2, 3, 4, 5)
        snapshot = record_reaction_snapshot(
            pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time, html_content=html_content
        )
        assert snapshot is not None

        # Without a finished work status after starting, remain in LLM working
        assert determine_phase(pr) == PHASE_LLM_WORKING

    def test_llm_status_reviewing_started_finished_prefers_phase3_without_cache(self):
        """
        When LLM statuses show reviewing → started → finished but the reaction cache is empty,
        phase3 should still apply.
        """
        reset_snapshot_cache(clear_content_cache=True)
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
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

    def test_finished_reaction_signature_survives_comment_reordering(self, tmp_path):
        """
        Finished reactions should remain recognized even when comment order changes (new comments added).
        """
        reset_snapshot_cache(clear_content_cache=True)
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
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
        }

        # First pass: detected as LLM working, then snapshot marks finished
        assert determine_phase(pr) == PHASE_LLM_WORKING
        html_content = """
        <div class="prc-PageLayout-Content-xWL-A">
            <p>LLM status: started work</p>
            <p>LLM status: finished work</p>
        </div>
        """
        current_time = datetime(2024, 1, 2, 3, 4, 5)
        record_reaction_snapshot(
            pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time, html_content=html_content
        )
        assert determine_phase(pr) == PHASE_3

        # Next iteration: a new comment is inserted before the reaction comment.
        # Signature should remain recognized and phase stay at phase3.
        reset_snapshot_cache()
        pr_with_new_comment = copy.deepcopy(pr)
        pr_with_new_comment["commentNodes"] = [
            {"body": "New note", "reactionGroups": []},
            *pr["commentNodes"],
        ]

        assert determine_phase(pr_with_new_comment) == PHASE_3

    def test_reaction_cache_not_cleared_when_html_missing(self, tmp_path):
        """
        If HTML fetch/markdown is unavailable, the finished-reaction cache should remain untouched.
        """
        reset_snapshot_cache(clear_content_cache=True)
        reset_comment_reaction_resolution_cache()

        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "## Pull request overview\n\nLooks good overall.",
                }
            ],
            "latestReviews": [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}],
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
        }

        html_content = """
        <div class="prc-PageLayout-Content-xWL-A">
            <p>LLM status: started work</p>
            <p>LLM status: finished work</p>
        </div>
        """
        current_time = datetime(2024, 1, 2, 3, 4, 5)
        first_snapshot = record_reaction_snapshot(
            pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time, html_content=html_content
        )
        assert first_snapshot is not None
        assert determine_phase(pr) == PHASE_3

        # Next iteration: HTML fetch fails (no markdown). Cache should stay marked finished.
        reset_snapshot_cache()
        with patch("src.gh_pr_phase_monitor.pr_data_recorder._fetch_pr_html", return_value=None):
            record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)

        assert determine_phase(pr) == PHASE_3

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
