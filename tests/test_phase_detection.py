"""Tests for PR phase detection logic"""
from gh_pr_phase_monitor import determine_phase


class TestDeterminePhase:
    """Test the determine_phase function"""

    def test_phase1_draft_pr(self):
        """Draft PRs should be phase1"""
        pr = {
            "isDraft": True,
            "reviews": [],
            "latestReviews": []
        }
        assert determine_phase(pr) == "phase1"

    def test_llm_working_no_reviews(self):
        """PRs with no reviews should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [],
            "latestReviews": []
        }
        assert determine_phase(pr) == "LLM working"

    def test_phase2_copilot_reviewer_with_comments(self):
        """Copilot reviewer with comments should be phase2"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Please fix these issues:\n- Issue 1\n- Issue 2"
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED"
                }
            ]
        }
        assert determine_phase(pr) == "phase2"

    def test_phase3_copilot_reviewer_approved(self):
        """Copilot reviewer with APPROVED state should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED",
                    "body": "Looks good!"
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "APPROVED"
                }
            ]
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_no_body(self):
        """Copilot reviewer with no review body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": ""
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED"
                }
            ]
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_reviewer_whitespace_only_body(self):
        """Copilot reviewer with only whitespace in body should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "   \n  \t  "
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED"
                }
            ]
        }
        assert determine_phase(pr) == "phase3"

    def test_phase3_copilot_swe_agent(self):
        """Copilot SWE agent as latest reviewer should be phase3"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "COMMENTED",
                    "body": "Please fix issues"
                },
                {
                    "author": {"login": "copilot-swe-agent"},
                    "state": "COMMENTED",
                    "body": "Fixed the issues"
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-swe-agent"},
                    "state": "COMMENTED"
                }
            ]
        }
        assert determine_phase(pr) == "phase3"

    def test_llm_working_unknown_reviewer(self):
        """Unknown reviewer should be 'LLM working'"""
        pr = {
            "isDraft": False,
            "reviews": [
                {
                    "author": {"login": "some-other-bot"},
                    "state": "COMMENTED",
                    "body": "Some comment"
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "some-other-bot"},
                    "state": "COMMENTED"
                }
            ]
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
                    "body": "Please address these issues"
                }
            ],
            "latestReviews": [
                {
                    "author": {"login": "copilot-pull-request-reviewer"},
                    "state": "CHANGES_REQUESTED"
                }
            ]
        }
        assert determine_phase(pr) == "phase2"
