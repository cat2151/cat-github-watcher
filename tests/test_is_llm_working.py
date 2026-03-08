"""
Tests for the is_llm_working() helper in phase_detector.py.

Covers:
- html_status path (1A~3A authoritative)
- legacy phase fallback (when html_status is absent)
"""

import pytest

from src.gh_pr_phase_monitor.phase.phase_detector import (
    PHASE1A_DRAFT_LLM_WORKING,
    PHASE1B_DRAFT_LLM_FINISHED_WORK,
    PHASE1B_LLM_FINISHED_WORK,
    PHASE1C_REVIEW_IN_PROGRESS,
    PHASE2A_REVIEW_COMPLETED,
    PHASE2B_LLM_ADDRESSING_FEEDBACK,
    PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
    PHASE_1,
    PHASE_2,
    PHASE_3,
    PHASE_LLM_WORKING,
    is_llm_working,
)


class TestIsLlmWorkingHtmlStatusPath:
    """When html_status is set, is_llm_working() uses only html_status."""

    @pytest.mark.parametrize(
        "html_status",
        [
            PHASE1A_DRAFT_LLM_WORKING,
            PHASE1C_REVIEW_IN_PROGRESS,
            PHASE2B_LLM_ADDRESSING_FEEDBACK,
        ],
    )
    def test_returns_true_for_working_statuses(self, html_status):
        pr = {"html_status": html_status}
        assert is_llm_working(pr) is True

    @pytest.mark.parametrize(
        "html_status",
        [
            PHASE1B_DRAFT_LLM_FINISHED_WORK,
            PHASE1B_LLM_FINISHED_WORK,
            PHASE2A_REVIEW_COMPLETED,
            PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
        ],
    )
    def test_returns_false_for_non_working_statuses(self, html_status):
        pr = {"html_status": html_status}
        assert is_llm_working(pr) is False

    def test_ignores_legacy_phase_when_html_status_present(self):
        """html_status takes priority; legacy phase is ignored."""
        pr = {"html_status": PHASE2A_REVIEW_COMPLETED, "phase": PHASE_LLM_WORKING}
        assert is_llm_working(pr) is False

    def test_phase2b_counted_as_working_even_though_legacy_phase_is_phase2(self):
        """PHASE2B maps to old PHASE_2 in determine_phase(), but is_llm_working() returns True."""
        pr = {"html_status": PHASE2B_LLM_ADDRESSING_FEEDBACK, "phase": PHASE_2}
        assert is_llm_working(pr) is True


class TestIsLlmWorkingLegacyFallback:
    """When html_status is absent or empty, is_llm_working() falls back to pr['phase']."""

    def test_returns_true_for_phase_llm_working(self):
        pr = {"phase": PHASE_LLM_WORKING}
        assert is_llm_working(pr) is True

    @pytest.mark.parametrize("phase", [PHASE_1, PHASE_2, PHASE_3])
    def test_returns_false_for_non_llm_working_phases(self, phase):
        pr = {"phase": phase}
        assert is_llm_working(pr) is False

    def test_returns_false_when_no_phase_key(self):
        pr = {}
        assert is_llm_working(pr) is False

    def test_empty_html_status_falls_back_to_phase(self):
        """Empty string html_status is falsy; should fall back to legacy phase."""
        pr = {"html_status": "", "phase": PHASE_LLM_WORKING}
        assert is_llm_working(pr) is True

    def test_none_html_status_falls_back_to_phase(self):
        """None html_status is falsy; should fall back to legacy phase."""
        pr = {"html_status": None, "phase": PHASE_LLM_WORKING}
        assert is_llm_working(pr) is True
