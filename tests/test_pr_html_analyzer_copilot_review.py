"""
Tests for Copilot review-related behaviour in pr_html_analyzer.

Covers:
- _copilot_review_has_no_inline_comments() helper
- Detection of 'Copilot reviewed' events and the PHASE2A → PHASE3A upgrade logic
"""

from src.gh_pr_phase_monitor.phase.html.llm_status_extractor import _extract_llm_statuses
from src.gh_pr_phase_monitor.phase.html.pr_html_analyzer import (
    PHASE2A_REVIEW_COMPLETED,
    PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
    _copilot_review_has_no_inline_comments,
    analyze_pr_html,
)


class TestCopilotReviewHasNoInlineComments:
    """Tests for _copilot_review_has_no_inline_comments helper."""

    # Minimal TimelineItem-body block that represents the Copilot reviewer with no inline comments.
    _REVIEWER_BLOCK_NO_COMMENTS = (
        '<div class="TimelineItem-body">'
        '<a data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer">Copilot</a>'
        " reviewed"
        "<p>Copilot reviewed 3 out of 3 changed files and generated no comments.</p>"
        "</div>"
    )

    def test_returns_true_for_generated_no_comments(self):
        assert _copilot_review_has_no_inline_comments(self._REVIEWER_BLOCK_NO_COMMENTS) is True

    def test_returns_true_for_generated_zero_comments(self):
        html = (
            '<div class="TimelineItem-body">'
            '<a data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer">Copilot</a>'
            " reviewed"
            "<p>Copilot reviewed files and generated 0 comments.</p>"
            "</div>"
        )
        assert _copilot_review_has_no_inline_comments(html) is True

    def test_returns_true_case_insensitive(self):
        html = (
            '<div class="TimelineItem-body">'
            '<a data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer">Copilot</a>'
            " reviewed"
            "<p>Generated No Comments.</p>"
            "</div>"
        )
        assert _copilot_review_has_no_inline_comments(html) is True

    def test_returns_false_for_generated_n_comments(self):
        """When there are actual inline review comments, return False."""
        html = (
            '<div class="TimelineItem-body">'
            '<a data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer">Copilot</a>'
            " reviewed"
            "<p>Copilot reviewed 2 files and generated 3 comments.</p>"
            "</div>"
        )
        assert _copilot_review_has_no_inline_comments(html) is False

    def test_returns_false_when_phrase_in_separate_unrelated_block(self):
        """'generated no comments' in a non-reviewer block must not trigger True.

        This is the key false-positive guard: a user comment quoting the phrase must
        NOT cause a PHASE2A → PHASE3A upgrade.
        """
        html = (
            # Copilot reviewer block — no "generated no comments" here
            '<div class="TimelineItem-body">'
            '<a data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer">Copilot</a>'
            " reviewed"
            "</div>"
            # Unrelated user comment that happens to contain the phrase
            '<div class="TimelineItem-body">'
            "<p>The CI pipeline generated no comments from the linter.</p>"
            "</div>"
        )
        assert _copilot_review_has_no_inline_comments(html) is False

    def test_returns_false_when_pattern_absent(self):
        """When the pattern is not found at all, return False (conservative default)."""
        html = (
            '<div class="TimelineItem-body">'
            '<a data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer">Copilot</a>'
            " reviewed"
            "</div>"
        )
        assert _copilot_review_has_no_inline_comments(html) is False

    def test_returns_false_for_empty_html(self):
        assert _copilot_review_has_no_inline_comments("") is False


class TestCopilotReviewedExtraction:
    """Tests for detection of Copilot 'reviewed' events in TimelineItem-body blocks."""

    _REVIEWED_HTML = """
          <div class="TimelineItem-body d-flex flex-column flex-md-row flex-justify-start">
            <div class="flex-auto flex-md-self-center">
              <strong>
                  <a class="author Link--primary text-bold css-overflow-wrap-anywhere" data-hovercard-type="copilot" data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer" href="/apps/copilot-pull-request-reviewer">Copilot</a>
<span class="Label Label--secondary">AI</span>

              </strong>

              reviewed
            </div>
          </div>
    """

    # Reviewer block that includes the "generated no comments" summary inside the same
    # TimelineItem-body div — matching the actual GitHub PR HTML structure.
    _REVIEWED_HTML_NO_COMMENTS = (
        '<div class="TimelineItem-body d-flex flex-column flex-md-row flex-justify-start">'
        '<div class="flex-auto flex-md-self-center">'
        "<strong>"
        '<a class="author Link--primary text-bold css-overflow-wrap-anywhere"'
        ' data-hovercard-type="copilot"'
        ' data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer"'
        ' href="/apps/copilot-pull-request-reviewer">Copilot</a>'
        '<span class="Label Label--secondary">AI</span>'
        "</strong>"
        "reviewed"
        "<p>Copilot reviewed 3 out of 3 changed files in this pull request"
        " and generated no comments.</p>"
        "</div>"
        "</div>"
    )

    def test_copilot_reviewed_extracted_from_html(self):
        """Bug fix: 'Copilot reviewed' should be extracted from TimelineItem-body blocks
        that have data-hovercard-type='copilot' even without session_id=."""
        html_markdown = ""
        statuses = _extract_llm_statuses(self._REVIEWED_HTML, html_markdown)
        assert "Copilot reviewed" in statuses

    def test_analyze_pr_html_includes_copilot_reviewed(self):
        """analyze_pr_html should include 'Copilot reviewed' in llm_statuses."""
        result = analyze_pr_html(self._REVIEWED_HTML, "https://github.com/owner/repo/pull/1")
        assert "Copilot reviewed" in result["llm_statuses"]

    def test_copilot_reviewed_leads_to_phase2a(self):
        """A 'Copilot reviewed' event with no 'generated no comments' indicator → PHASE2A (conservative fallback)."""
        result = analyze_pr_html(self._REVIEWED_HTML, "https://github.com/owner/repo/pull/1")
        assert result["status"] == PHASE2A_REVIEW_COMPLETED

    def test_copilot_reviewed_with_generated_no_comments_yields_phase3a(self):
        """Bug fix: When the Copilot reviewer's review body says 'generated no comments',
        the PR has no review feedback to address → PHASE3A.

        Real-world example: PR #386 had a review body containing
        'Copilot reviewed 3 out of 3 changed files in this pull request and generated no comments.'
        The PR was incorrectly classified as PHASE2A instead of PHASE3A.

        The "generated no comments" text must appear inside the same TimelineItem-body block
        as the copilot-pull-request-reviewer marker.
        """
        result = analyze_pr_html(self._REVIEWED_HTML_NO_COMMENTS, "https://github.com/owner/repo/pull/386")
        assert result["status"] == PHASE3A_LLM_FEEDBACK_FINISHED_WORK

    def test_copilot_reviewed_with_generated_zero_comments_yields_phase3a(self):
        """'generated 0 comments' inside the reviewer block is also treated as no inline comments → PHASE3A."""
        html = self._REVIEWED_HTML_NO_COMMENTS.replace(
            "generated no comments", "generated 0 comments"
        )
        result = analyze_pr_html(html, "https://github.com/owner/repo/pull/1")
        assert result["status"] == PHASE3A_LLM_FEEDBACK_FINISHED_WORK

    def test_copilot_reviewed_with_generated_inline_comments_stays_phase2a(self):
        """When the review body says 'generated N comments' (N >= 1), inline review
        comments exist and Copilot must address them → PHASE2A."""
        html = self._REVIEWED_HTML_NO_COMMENTS.replace(
            "generated no comments", "generated 3 comments"
        )
        result = analyze_pr_html(html, "https://github.com/owner/repo/pull/1")
        assert result["status"] == PHASE2A_REVIEW_COMPLETED

    def test_no_comments_phrase_in_unrelated_user_comment_does_not_upgrade_to_phase3a(self):
        """'generated no comments' in an unrelated user comment must NOT trigger PHASE3A.

        This guards against the false-positive: a user quoting the phrase or a CI bot
        posting a message like 'the linter generated no comments' must not be mistaken
        for the Copilot reviewer's own review body.
        """
        # _REVIEWED_HTML contains the copilot reviewer block (no "generated no comments").
        # The unrelated comment block below contains the phrase but is a different TimelineItem-body.
        user_comment_with_phrase = (
            '<div class="TimelineItem-body">'
            "<p>The CI pipeline generated no comments from the linter.</p>"
            "</div>"
        )
        html = self._REVIEWED_HTML + user_comment_with_phrase
        result = analyze_pr_html(html, "https://github.com/owner/repo/pull/1")
        assert result["status"] == PHASE2A_REVIEW_COMPLETED

    def test_copilot_reviewed_no_inline_comments_with_subsequent_work_is_phase3a(self):
        """Bug fix: when Copilot reviews with no inline comments and the coding agent
        subsequently starts and finishes work, the result must be PHASE3A, not PHASE2A/2B.

        Root cause: session_id= events (started/finished work) were extracted from
        markdown BEFORE the 'Copilot reviewed' event was extracted from the HTML timeline
        (via copilot hovercard). The markdown segment containing both the review event
        text and the first session_id= link was added as a combined status, which then
        caused incorrect phase detection when the HTML-extracted 'Copilot reviewed' was
        appended after the work events.

        The fix:
        1. HTML extraction runs first so timeline order is preserved.
        2. Markdown extraction extracts individual session_id= link texts instead of the
           combined segment text, preventing spurious combined-text review-reset events.
        """
        html = (
            # Review event timeline item (copilot reviewer — no inline comments)
            # This event is only detectable via the copilot hovercard (no session_id=).
            '<div class="TimelineItem-body d-flex flex-column flex-md-row flex-justify-start">'
            '<div class="flex-auto flex-md-self-center">'
            "<strong>"
            '<a class="author Link--primary text-bold css-overflow-wrap-anywhere"'
            ' data-hovercard-type="copilot"'
            ' data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer"'
            ' href="/apps/copilot-pull-request-reviewer">Copilot</a>'
            '<span class="Label Label--secondary">AI</span>'
            "</strong>"
            "reviewed"
            "</div>"
            "</div>"
            # Coding agent: started work — wrapped in <p> so it creates a separate
            # double-newline segment in the markdown representation, simulating the
            # realistic GitHub HTML structure that triggers the ordering bug.
            '<div class="TimelineItem-body">'
            "<p>"
            '<a href="https://copilot.github.com/task?session_id=abc123">'
            "Codex started work on behalf of cat2151 March 7, 2026 10:01"
            "</a>"
            "</p>"
            "</div>"
            # Coding agent: finished work (also wrapped in <p>)
            '<div class="TimelineItem-body">'
            "<p>"
            '<a href="https://copilot.github.com/task?session_id=abc123">'
            "Codex finished work on behalf of cat2151 March 7, 2026 10:30"
            "</a>"
            "</p>"
            "</div>"
        )
        result = analyze_pr_html(html, "https://github.com/owner/repo/pull/30")
        assert result["status"] == PHASE3A_LLM_FEEDBACK_FINISHED_WORK

    def test_short_form_duplicates_not_added_after_full_form_captured(self):
        """Bug fix: short link-text forms (e.g. 'started work', 'started reviewing') must not
        appear in llm_statuses when full-form versions are already present.

        Root cause: out-of-body session_id= links (e.g. in PR comment markdown) produced
        short-form anchor texts ('started work', 'finished work', 'started reviewing') that
        the text-pattern extractor appended after the full forms captured by the HTML-element
        extractor.  This made _is_review_still_in_progress see a new spurious review cycle
        starting after 'Copilot reviewed', incorrectly yielding PHASE1C_REVIEW_IN_PROGRESS.

        Fix: the text-pattern extractor no longer processes session_id= links at all.
        All Copilot session events are captured authoritatively by the HTML-element extractor
        from TimelineItem-body divs; out-of-body session_id= links are always duplicates.
        """
        html = (
            '<div class="TimelineItem-body">'
            '<a href="https://copilot.github.com/task?session_id=s1">'
            "Copilot started work on behalf of cat2151 March 7, 2026 14:20"
            "</a>"
            "</div>"
            '<div class="TimelineItem-body">'
            '<a href="https://copilot.github.com/task?session_id=s1">'
            "Copilot finished work on behalf of cat2151 March 7, 2026 14:24"
            "</a>"
            "</div>"
            '<div class="TimelineItem-body">'
            '<a href="https://copilot.github.com/task?session_id=s2">'
            "Copilot started reviewing on behalf of cat2151 March 7, 2026 14:26"
            "</a>"
            "</div>"
            # Copilot reviewed (via copilot hovercard, no session_id=)
            '<div class="TimelineItem-body d-flex flex-column flex-md-row flex-justify-start">'
            '<div class="flex-auto flex-md-self-center">'
            "<strong>"
            '<a class="author Link--primary text-bold css-overflow-wrap-anywhere"'
            ' data-hovercard-type="copilot"'
            ' data-hovercard-url="/copilot/hovercard?bot=copilot-pull-request-reviewer"'
            ' href="/apps/copilot-pull-request-reviewer">Copilot</a>'
            "</strong>"
            "reviewed Mar 7, 2026"
            "</div>"
            "</div>"
            # Short-form session_id= links OUTSIDE TimelineItem-body (the real-world source
            # of the bug: these appear in GitHub PR markdown but not in the timeline elements).
            # With the fix, the text-pattern extractor ignores all session_id= links,
            # so these never reach llm_statuses.
            "<p>"
            '<a href="https://copilot.github.com/task?session_id=s1">started work</a>'
            "</p>"
            "<p>"
            '<a href="https://copilot.github.com/task?session_id=s1">finished work</a>'
            "</p>"
            "<p>"
            '<a href="https://copilot.github.com/task?session_id=s2">started reviewing</a>'
            "</p>"
        )
        result = analyze_pr_html(html, "https://github.com/cat2151/smf-to-ym2151log-rust/pull/148")
        # Short-form duplicates must NOT appear in llm_statuses
        assert "started work" not in result["llm_statuses"]
        assert "finished work" not in result["llm_statuses"]
        assert "started reviewing" not in result["llm_statuses"]
        # Full forms and completion event must be present
        assert any("started work" in s and "March 7" in s for s in result["llm_statuses"])
        assert any("finished work" in s and "March 7" in s for s in result["llm_statuses"])
        assert any("started reviewing" in s and "March 7" in s for s in result["llm_statuses"])
        assert any("reviewed" in s.lower() for s in result["llm_statuses"])
        # Status must reflect that the review is COMPLETED, not still in progress
        assert result["status"] == PHASE2A_REVIEW_COMPLETED
