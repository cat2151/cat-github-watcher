"""
Tests for LLM status-based phase detection (HTML snapshot analysis)
"""

from datetime import datetime

from src.gh_pr_phase_monitor import determine_phase
from src.gh_pr_phase_monitor.phase.phase_detector import (
    PHASE_3,
    PHASE_LLM_WORKING,
    reset_comment_reaction_resolution_cache,
)
from src.gh_pr_phase_monitor.phase.legacy.pr_data_recorder import record_reaction_snapshot, reset_snapshot_cache


class TestDeterminePhaseWithLLMStatus:
    """Tests for phase detection using LLM HTML status snapshots"""

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

