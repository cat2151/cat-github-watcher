"""
Tests for LLM status-based phase detection (HTML snapshot analysis)
"""

import copy
from datetime import datetime
from unittest.mock import patch

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase_detector import (
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)
from src.gh_pr_phase_monitor.pr_data_recorder import record_reaction_snapshot, reset_snapshot_cache


class TestDeterminePhaseWithLLMStatus:
    """Tests for phase detection using LLM HTML status snapshots"""

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
