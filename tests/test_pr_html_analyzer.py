"""
Tests for pr_html_analyzer module
"""

import json

from src.gh_pr_phase_monitor.pr_html_analyzer import (
    PHASE1A_DRAFT_LLM_WORKING,
    PHASE1B_DRAFT_LLM_FINISHED_WORK,
    PHASE1C_REVIEW_IN_PROGRESS,
    PHASE2A_REVIEW_COMPLETED,
    PHASE2B_LLM_ADDRESSING_FEEDBACK,
    PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
    _determine_html_status,
    _is_draft_from_html,
    analyze_pr_html,
    save_analysis_json,
)


class TestIsDraftFromHtml:
    def test_detects_draft_state_class(self):
        html = '<span class="State State--draft">Draft</span>'
        assert _is_draft_from_html(html) is True

    def test_detects_draft_aria_label(self):
        html = '<span aria-label="Draft Pull Request">...</span>'
        assert _is_draft_from_html(html) is True

    def test_detects_draft_span_text(self):
        html = "<div><span>Draft</span></div>"
        assert _is_draft_from_html(html) is True

    def test_detects_data_state_draft(self):
        html = '<div data-state="draft">...</div>'
        assert _is_draft_from_html(html) is True

    def test_returns_false_for_open_pr(self):
        html = "<span>Open</span><div>Some PR content</div>"
        assert _is_draft_from_html(html) is False

    def test_returns_false_for_empty_html(self):
        assert _is_draft_from_html("") is False


class TestDetermineHtmlStatus:
    def test_phase1a_draft_no_statuses(self):
        """Draft PR with no LLM statuses → PHASE1A"""
        assert _determine_html_status([], is_draft=True) == PHASE1A_DRAFT_LLM_WORKING

    def test_phase1a_draft_started_only(self):
        """Draft PR with started-work only → PHASE1A"""
        assert _determine_html_status(["started work on something"], is_draft=True) == PHASE1A_DRAFT_LLM_WORKING

    def test_phase1b_draft_finished(self):
        """Draft PR with started then finished → PHASE1B"""
        statuses = ["started work on something", "finished work on something"]
        assert _determine_html_status(statuses, is_draft=True) == PHASE1B_DRAFT_LLM_FINISHED_WORK

    def test_phase1c_not_draft_no_reviewing(self):
        """Non-draft PR with no reviewing event → PHASE1C"""
        assert _determine_html_status([], is_draft=False) == PHASE1C_REVIEW_IN_PROGRESS

    def test_phase1c_not_draft_with_started_only(self):
        """Non-draft PR with started but no reviewing → PHASE1C"""
        assert _determine_html_status(["started work"], is_draft=False) == PHASE1C_REVIEW_IN_PROGRESS

    def test_phase2a_reviewing_only(self):
        """reviewing event but no started after → PHASE2A"""
        statuses = ["started work", "finished work", "reviewing something"]
        assert _determine_html_status(statuses, is_draft=False) == PHASE2A_REVIEW_COMPLETED

    def test_phase2b_reviewing_then_started(self):
        """reviewing then started (no finished after) → PHASE2B"""
        statuses = ["reviewing something", "started work on feedback"]
        assert _determine_html_status(statuses, is_draft=False) == PHASE2B_LLM_ADDRESSING_FEEDBACK

    def test_phase3a_reviewing_started_finished(self):
        """reviewing → started → finished → PHASE3A"""
        statuses = ["reviewing something", "started work on feedback", "finished work on feedback"]
        assert _determine_html_status(statuses, is_draft=False) == PHASE3A_LLM_FEEDBACK_FINISHED_WORK

    def test_phase3a_multiple_review_cycles(self):
        """Multiple review cycles, last cycle finished → PHASE3A"""
        statuses = [
            "started work",
            "finished work",
            "reviewing first",
            "started work on first feedback",
            "finished work on first feedback",
        ]
        assert _determine_html_status(statuses, is_draft=False) == PHASE3A_LLM_FEEDBACK_FINISHED_WORK

    def test_phase2b_second_review_started_not_finished(self):
        """Second review cycle started but not finished → PHASE2B"""
        statuses = [
            "reviewing first",
            "started work on first feedback",
            "finished work on first feedback",
            "reviewing second",
            "started work on second feedback",
        ]
        assert _determine_html_status(statuses, is_draft=False) == PHASE2B_LLM_ADDRESSING_FEEDBACK

    def test_phase2b_new_started_after_finished_within_same_cycle(self):
        """reviewing → started → finished → started (no finished) → PHASE2B, not PHASE3A.

        Edge case: a new started-work event after finished-work within the same reviewing cycle
        means Copilot is still working (phase2b), not done (phase3a).
        This was a bug in the previous implementation which incorrectly returned PHASE3A.
        """
        statuses = [
            "reviewing",
            "started work on feedback",
            "finished work on feedback",
            "started work again",  # new cycle started, no matching finished
        ]
        assert _determine_html_status(statuses, is_draft=False) == PHASE2B_LLM_ADDRESSING_FEEDBACK

    def test_returns_dict_with_required_keys(self):
        html = "<html><body>Some PR content</body></html>"
        result = analyze_pr_html(html, "https://github.com/owner/repo/pull/1")
        assert "pr_url" in result
        assert "is_draft" in result
        assert "llm_statuses" in result
        assert "status" in result

    def test_pr_url_preserved(self):
        html = "<html><body></body></html>"
        url = "https://github.com/owner/repo/pull/42"
        result = analyze_pr_html(html, url)
        assert result["pr_url"] == url

    def test_draft_pr_detected(self):
        html = '<span class="State State--draft">Draft</span>'
        result = analyze_pr_html(html)
        assert result["is_draft"] is True

    def test_non_draft_pr(self):
        html = "<html><body><span>Open</span></body></html>"
        result = analyze_pr_html(html)
        assert result["is_draft"] is False

    def test_llm_statuses_is_list(self):
        html = "<html><body></body></html>"
        result = analyze_pr_html(html)
        assert isinstance(result["llm_statuses"], list)

    def test_status_is_valid_phase(self):
        html = "<html><body></body></html>"
        result = analyze_pr_html(html)
        valid_phases = {
            PHASE1A_DRAFT_LLM_WORKING,
            PHASE1B_DRAFT_LLM_FINISHED_WORK,
            PHASE1C_REVIEW_IN_PROGRESS,
            PHASE2A_REVIEW_COMPLETED,
            PHASE2B_LLM_ADDRESSING_FEEDBACK,
            PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
        }
        assert result["status"] in valid_phases


class TestSaveAnalysisJson:
    def test_saves_json_with_correct_filename(self, tmp_path):
        html_path = tmp_path / "repo_123.html"
        analysis = {
            "pr_url": "https://github.com/o/repo/pull/123",
            "is_draft": False,
            "llm_statuses": [],
            "status": PHASE1C_REVIEW_IN_PROGRESS,
        }
        result = save_analysis_json(analysis, html_path)
        assert result == tmp_path / "repo_123.json"
        assert result.exists()

    def test_json_content_is_correct(self, tmp_path):
        html_path = tmp_path / "repo_1.html"
        analysis = {
            "pr_url": "https://github.com/o/repo/pull/1",
            "is_draft": True,
            "llm_statuses": ["started work"],
            "status": PHASE1A_DRAFT_LLM_WORKING,
        }
        save_analysis_json(analysis, html_path)
        json_path = tmp_path / "repo_1.json"
        loaded = json.loads(json_path.read_text(encoding="utf-8"))
        assert loaded == analysis

    def test_json_is_valid_json(self, tmp_path):
        html_path = tmp_path / "repo_5.html"
        analysis = {
            "pr_url": "https://github.com/o/r/pull/5",
            "is_draft": False,
            "llm_statuses": ["reviewing", "started work", "finished work"],
            "status": PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
        }
        save_analysis_json(analysis, html_path)
        json_path = tmp_path / "repo_5.json"
        # Should not raise
        json.loads(json_path.read_text(encoding="utf-8"))
