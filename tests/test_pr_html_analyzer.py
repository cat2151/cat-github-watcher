"""
Tests for pr_html_analyzer module
"""

import json

from src.gh_pr_phase_monitor.phase.html.llm_status_extractor import _extract_llm_statuses
from src.gh_pr_phase_monitor.phase.html.pr_html_analyzer import (
    PHASE1A_DRAFT_LLM_WORKING,
    PHASE1B_DRAFT_LLM_FINISHED_WORK,
    PHASE1B_LLM_FINISHED_WORK,
    PHASE1C_REVIEW_IN_PROGRESS,
    PHASE2A_REVIEW_COMPLETED,
    PHASE2B_LLM_ADDRESSING_FEEDBACK,
    PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
    _copilot_review_has_no_inline_comments,
    _determine_html_status,
    _is_draft_from_html,
    _is_review_still_in_progress,
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

    def test_detects_data_status_draft(self):
        html = '<span class="prc-StateLabel-StateLabel-Iawzp flex-self-start" data-size="medium" data-status="draft"><svg>...</svg>Draft</span>'
        assert _is_draft_from_html(html) is True

    def test_detects_state_json_draft(self):
        html = '<script type="application/json">{"state":"DRAFT","title":"WIP: Fix bug"}</script>'
        assert _is_draft_from_html(html) is True

    def test_detects_octicon_git_pull_request_draft(self):
        html = '<svg class="octicon octicon-git-pull-request-draft" aria-hidden="true"></svg>'
        assert _is_draft_from_html(html) is True

    def test_draft_pr_with_data_status_and_started_work_is_phase1a(self):
        """Bug fix: Draft PR using data-status='draft' (GitHub's current HTML format) with
        only 'started work' status must be PHASE1A, not PHASE1C.

        This test also ensures that the 'started work' status is actually extracted as an
        LLM status (non-empty llm_statuses) by using a TimelineItem-body with a session_id
        attribute, matching the extractor's expectations.
        """
        html = (
            '<span data-status="draft">Draft</span>'
            '<div class="TimelineItem-body">'
            '<a href="https://copilot.github.com/task?session_id=123">'
            'Copilot started work on behalf of cat2151 March 7, 2026 10:01'
            '</a>'
            '</div>'
        )
        result = analyze_pr_html(html, "https://github.com/owner/repo/pull/375")
        assert result["is_draft"] is True
        # Ensure that the 'started work' status was actually extracted as an LLM status.
        assert result.get("llm_statuses")
        assert any("started work" in status for status in result["llm_statuses"])
        assert result["status"] == PHASE1A_DRAFT_LLM_WORKING

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

    def test_phase1b_not_draft_finished_no_reviewing(self):
        """Non-draft PR with started→finished work but no reviewing event → PHASE1B_LLM_FINISHED_WORK (not PHASE1C).

        Bug fix: 'Latest LLM status: Copilot finished work' on a non-draft PR with no reviewing
        was incorrectly classified as PHASE1C_REVIEW_IN_PROGRESS.
        If there is no 'started reviewing' and a 'started work' → 'finished work' pair is present, 1B is confirmed.
        Note: PHASE1B_LLM_FINISHED_WORK (not PHASE1B_DRAFT_LLM_FINISHED_WORK) is returned for non-draft PRs
        to avoid triggering 'gh pr ready' on a PR that is already not draft.
        """
        statuses = ["Copilot started work on behalf of cat2151", "Copilot finished work on behalf of cat2151"]
        assert _determine_html_status(statuses, is_draft=False) == PHASE1B_LLM_FINISHED_WORK

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
            PHASE1B_LLM_FINISHED_WORK,
            PHASE1C_REVIEW_IN_PROGRESS,
            PHASE2A_REVIEW_COMPLETED,
            PHASE2B_LLM_ADDRESSING_FEEDBACK,
            PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
        }
        assert result["status"] in valid_phases


class TestIsReviewStillInProgress:
    def test_returns_false_for_empty_statuses(self):
        assert _is_review_still_in_progress([]) is False

    def test_returns_false_for_no_reviewing_event(self):
        assert _is_review_still_in_progress(["started work", "finished work"]) is False

    def test_returns_true_for_started_reviewing_only(self):
        """Bug case: 'started reviewing' without 'finished reviewing' → review in progress."""
        statuses = ["Copilot started reviewing on behalf of cat2151 March 5, 2026 23:29"]
        assert _is_review_still_in_progress(statuses) is True

    def test_returns_false_for_finished_reviewing(self):
        statuses = ["Copilot started reviewing on behalf of cat2151", "Copilot finished reviewing on behalf of cat2151"]
        assert _is_review_still_in_progress(statuses) is False

    def test_returns_false_for_plain_reviewing(self):
        """Plain 'reviewing' (no started/finished prefix) is treated as completed."""
        assert _is_review_still_in_progress(["reviewing something"]) is False

    def test_returns_false_when_plain_reviewing_follows_started_reviewing(self):
        """started reviewing → plain reviewing → treat as completed (not still in progress)."""
        statuses = ["Copilot started reviewing", "reviewing something"]
        assert _is_review_still_in_progress(statuses) is False

    def test_returns_true_when_new_started_reviewing_after_finished(self):
        """New 'started reviewing' after a previous 'finished reviewing' → still in progress."""
        statuses = [
            "Copilot started reviewing first",
            "Copilot finished reviewing first",
            "Copilot started reviewing second",
        ]
        assert _is_review_still_in_progress(statuses) is True

    def test_returns_false_when_finished_reviewing_follows_started(self):
        statuses = [
            "Copilot started reviewing",
            "Copilot finished reviewing",
        ]
        assert _is_review_still_in_progress(statuses) is False


class TestPhase1cReviewInProgress:
    def test_started_reviewing_only_returns_phase1c(self):
        """Bug fix: 'started reviewing' without 'finished reviewing' → PHASE1C, not PHASE2A."""
        statuses = ["Copilot started reviewing on behalf of cat2151 March 5, 2026 23:29"]
        assert _determine_html_status(statuses, is_draft=False) == PHASE1C_REVIEW_IN_PROGRESS

    def test_issue_example_returns_phase1c(self):
        """Exact scenario from the bug report: started work, finished work, then started reviewing."""
        statuses = [
            "Copilot started work on behalf of cat2151 March 5, 2026 23:18",
            "Copilot finished work on behalf of cat2151 March 5, 2026 23:24",
            "Copilot started reviewing on behalf of cat2151 March 5, 2026 23:29",
        ]
        assert _determine_html_status(statuses, is_draft=False) == PHASE1C_REVIEW_IN_PROGRESS

    def test_started_and_finished_reviewing_returns_phase2a(self):
        """Once 'finished reviewing' is present, it should be PHASE2A (review done, no work yet)."""
        statuses = [
            "Copilot started reviewing on behalf of cat2151",
            "Copilot finished reviewing on behalf of cat2151",
        ]
        assert _determine_html_status(statuses, is_draft=False) == PHASE2A_REVIEW_COMPLETED

    def test_started_reviewing_then_started_work_returns_phase2b(self):
        """started reviewing → finished reviewing → started work → PHASE2B."""
        statuses = [
            "Copilot started reviewing",
            "Copilot finished reviewing",
            "Copilot started work on feedback",
        ]
        assert _determine_html_status(statuses, is_draft=False) == PHASE2B_LLM_ADDRESSING_FEEDBACK


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
