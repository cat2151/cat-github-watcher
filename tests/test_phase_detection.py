"""
Tests for PR phase detection logic

Tests cover the following scenarios:
- Phase 1: Draft PRs
- Phase 2: Copilot reviewer with comments/changes requested
- Phase 3: Copilot reviewer approved or no comments, copilot-swe-agent modifications
- LLM working: No reviews, unknown reviewers, or comments with reactions
"""

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase_detector import _phase_from_llm_statuses


class TestPhaseFromLlmStatuses:
    """Tests for the _phase_from_llm_statuses helper, which is the primary detection method."""

    def test_returns_none_when_no_reviewing_event(self):
        """Without a reviewing event, cannot determine phase2/3."""
        assert _phase_from_llm_statuses([]) is None
        assert _phase_from_llm_statuses(["started work", "finished work"]) is None

    def test_returns_phase3_when_reviewing_then_started_then_finished(self):
        """reviewing → started work → finished work = phase3."""
        statuses = ["started reviewing", "started work", "finished work"]
        assert _phase_from_llm_statuses(statuses) == "phase3"

    def test_returns_phase3_real_world_pattern(self):
        """Real-world PR#167 pattern: initial work → reviewing → addressing work → phase3."""
        statuses = [
            "Copilot started work on behalf of cat2151",
            "Copilot finished work on behalf of cat2151",
            "Copilot started reviewing on behalf of cat2151",
            "Copilot started work on behalf of cat2151",
            "Copilot finished work on behalf of cat2151",
        ]
        assert _phase_from_llm_statuses(statuses) == "phase3"

    def test_returns_phase2_when_reviewing_only(self):
        """Reviewing event occurred but no subsequent work started → phase2 (waiting for Copilot)."""
        statuses = ["started work", "finished work", "started reviewing"]
        assert _phase_from_llm_statuses(statuses) == "phase2"

    def test_returns_phase2_when_reviewing_then_started_but_not_finished(self):
        """reviewing → started work but NOT finished → phase2 (Copilot still addressing)."""
        statuses = ["started reviewing", "started work"]
        assert _phase_from_llm_statuses(statuses) == "phase2"

    def test_returns_phase2_not_phase3_when_finished_before_reviewing_only(self):
        """'finished work' that precedes reviewing must NOT count as post-review completion.

        Before the reviewer comment fix, ["started reviewing", "finished work"] could incorrectly
        return PHASE_3 because last_finished_idx > review_idx was satisfied even without a
        'started work' after reviewing.
        """
        statuses = ["started reviewing", "finished work"]
        assert _phase_from_llm_statuses(statuses) == "phase2"

    def test_returns_phase2_not_phase3_when_started_before_reviewing_and_finished_after(self):
        """'started work' before reviewing + 'finished work' after must NOT count as post-review cycle.

        Before the reviewer comment fix, ["started work", "started reviewing", "finished work"]
        could incorrectly return PHASE_3 because last_finished_idx > review_idx was satisfied
        even though 'started work' came before 'reviewing'.
        """
        statuses = ["started work", "started reviewing", "finished work"]
        assert _phase_from_llm_statuses(statuses) == "phase2"


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

    def test_phase1_draft_pr_no_review_requests_but_llm_finished(self):
        """Draft PRs with no reviewRequests but llm_statuses showing finished work should be phase1.

        Scenario: copilot-swe-agent creates a Draft PR without setting review requests,
        but has finished its work (llm_statuses shows started work then finished work).
        The watcher should detect this as phase1 to trigger mark-ready-for-review action.
        This matches the real scenario from cat-repo-auditor/pull/19.
        """
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [],
            "comments": [],
            "llm_statuses": [
                "started work",
                "finished work",
            ],
        }
        assert determine_phase(pr) == "phase1"

    def test_llm_working_draft_pr_no_review_requests_llm_still_working(self):
        """Draft PRs with no reviewRequests and llm_statuses showing started but not finished should be LLM working."""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": [],
            "reviewRequests": [],
            "comments": [],
            "llm_statuses": [
                "started work",
            ],
        }
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

    def test_phase3_copilot_reviewer_commented_with_unresolved_threads_but_llm_statuses_indicate_phase3(self):
        """Copilot reviewer with COMMENTED + unresolved review threads, but llm_statuses show reviewing→started→finished → phase3

        This is the real-world scenario where:
        1. copilot-pull-request-reviewer reviews and leaves inline comments (unresolved threads remain in GraphQL)
        2. copilot-swe-agent addresses the feedback (started work → finished work after reviewing)
        3. The GraphQL reviewThreads still show isResolved: False (not explicitly resolved)
        4. But llm_statuses from HTML correctly show the full cycle: reviewing→started work→finished work
        The llm_statuses signal should take precedence over unresolved GraphQL threads.
        """
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
                {"isResolved": False, "isOutdated": False},
            ],
            "llm_statuses": [
                "Copilot started work on behalf of cat2151",
                "Copilot finished work on behalf of cat2151",
                "Copilot started reviewing on behalf of cat2151",
                "Copilot started work on behalf of cat2151",
                "Copilot finished work on behalf of cat2151",
            ],
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

    def test_phase2_from_llm_statuses_overrides_graphql(self):
        """llm_statuses showing reviewing-in-progress returns phase2 even without GraphQL review threads.

        This validates the unified approach: llm_statuses is checked first for non-draft PRs.
        When llm_statuses shows reviewing occurred but work not yet complete → phase2,
        regardless of what GraphQL reviewThreads say.
        """
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
            "reviewThreads": [],  # No unresolved threads (GraphQL would say phase3)
            "llm_statuses": [
                "Copilot started reviewing on behalf of cat2151",
                "Copilot started work on behalf of cat2151",
                # No "finished work" yet → still addressing → phase2
            ],
        }

        assert determine_phase(pr) == "phase2"

    def test_phase2_from_llm_statuses_when_no_graphql_reviews(self):
        """llm_statuses showing reviewing → phase2 even when GraphQL has no review data yet.

        GraphQL might not yet have the review, but HTML shows reviewing started.
        The unified approach returns phase2 based on llm_statuses instead of LLM working.
        """
        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": [],
            "comments": [],
            "llm_statuses": [
                "Copilot started reviewing on behalf of cat2151",
            ],
        }

        assert determine_phase(pr) == "phase2"

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
