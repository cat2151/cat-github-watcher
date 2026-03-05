import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor.phase.phase_detector import (
    PHASE_1,
    PHASE_LLM_WORKING,
    comment_reactions_marked_finished,
    determine_phase,
    reset_comment_reaction_resolution_cache,
)
from src.gh_pr_phase_monitor.phase.pr_data_recorder import (
    DEFAULT_SNAPSHOT_BASE_DIR,
    record_reaction_snapshot,
    reset_snapshot_cache,
    save_pr_snapshot,
)


def _sample_pr():
    return {
        "title": "Test PR",
        "url": "https://github.com/octocat/hello-world/pull/123",
        "author": {"login": "octocat"},
        "repository": {"owner": "octocat", "name": "hello-world"},
        "reviews": [{"state": "COMMENTED"}, {"state": "APPROVED"}],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [
            {
                "body": "Look into this",
                "reactionGroups": [
                    {"content": "EYES", "users": {"totalCount": 1}},
                    {"content": "ROCKET", "users": {"totalCount": 0}},
                ],
            }
        ],
        "reviewThreads": [{"isResolved": False, "isOutdated": False}],
    }


@pytest.fixture(autouse=True)
def reset_snapshot_cache_fixture():
    reset_snapshot_cache(clear_content_cache=True)
    yield
    reset_snapshot_cache(clear_content_cache=True)


def test_save_pr_snapshot_writes_json_and_markdown(tmp_path):
    current_time = datetime(2024, 1, 2, 3, 4, 5)
    result = save_pr_snapshot(
        _sample_pr(),
        reason="comment_reactions_detected",
        base_dir=tmp_path,
        current_time=current_time,
    )

    snapshot_dir = result["snapshot_dir"]
    raw_path = result["raw_path"]
    markdown_path = result["markdown_path"]

    assert snapshot_dir.is_dir()
    assert raw_path.exists()
    assert markdown_path.exists()
    # Directory name should NOT include timestamp
    assert snapshot_dir.name == "octocat_hello-world_PR123"
    # File names should include timestamp
    assert raw_path.name == "20240102_030405_raw.json"
    assert markdown_path.name == "20240102_030405_summary.md"

    saved_pr = json.loads(raw_path.read_text(encoding="utf-8"))
    assert saved_pr["url"].endswith("/pull/123")

    markdown_content = markdown_path.read_text(encoding="utf-8")
    assert "comment_reactions_detected" in markdown_content
    assert "Comment 1: EYES x1" in markdown_content
    assert "- **commentNodes**:" in markdown_content


def test_record_reaction_snapshot_respects_phase_and_reactions(tmp_path):
    pr = _sample_pr()
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = record_reaction_snapshot(pr, phase="phase3", base_dir=tmp_path, current_time=current_time)
    assert result is None
    assert not list(tmp_path.iterdir())

    result = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)
    assert result is not None
    assert result["markdown_path"].exists()


def test_record_reaction_snapshot_saves_html_to_logs_for_non_llm_working_phase(tmp_path):
    """非PHASE_LLM_WORKINGのopenなPRもlogs/prに保存されることを確認する。"""
    pr = _sample_pr()
    pr_url = pr["url"]

    with patch("src.gh_pr_phase_monitor.phase.pr_data_recorder._fetch_pr_html") as mock_fetch:
        with patch("src.gh_pr_phase_monitor.phase.pr_data_recorder.save_html_to_logs") as mock_save:
            mock_fetch.return_value = "<html><body>PR page</body></html>"
            result = record_reaction_snapshot(
                pr, phase="phase1", base_dir=tmp_path, current_time=datetime(2024, 1, 2, 3, 4, 5),
                html_content=None,
            )
            assert result is None
            mock_fetch.assert_called_once_with(pr_url)
            mock_save.assert_called_once()
            assert mock_save.call_args[0][1] == pr_url


def test_record_reaction_snapshot_saves_html_to_logs_using_html_content_for_non_llm_working(tmp_path):
    """html_content が与えられた場合はネットワーク取得なしでlogs/prに保存されることを確認する。"""
    pr = _sample_pr()
    pre_fetched = "<html><body>Pre-fetched PR page</body></html>"

    with patch("src.gh_pr_phase_monitor.phase.pr_data_recorder._fetch_pr_html") as mock_fetch:
        with patch("src.gh_pr_phase_monitor.phase.pr_data_recorder.save_html_to_logs") as mock_save:
            result = record_reaction_snapshot(
                pr, phase="phase2", base_dir=tmp_path, current_time=datetime(2024, 1, 2, 3, 4, 5),
                html_content=pre_fetched,
            )
            assert result is None
            mock_fetch.assert_not_called()
            mock_save.assert_called_once()
            call_args = mock_save.call_args
            assert call_args[0][0] == pre_fetched
            assert call_args[0][1] == pr["url"]


def test_record_reaction_snapshot_sets_llm_statuses_on_pr(tmp_path):
    pr = _sample_pr()
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    html_content = '<div data-llm-status="finished work items"></div>'

    result = record_reaction_snapshot(
        pr,
        phase=PHASE_LLM_WORKING,
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html_content,
    )

    assert result is not None
    assert pr.get("llm_statuses") == ["finished work items"]


def test_record_reaction_snapshot_can_skip_disk_writes(tmp_path):
    pr = _sample_pr()
    current_time = datetime(2024, 1, 2, 3, 4, 5)
    html_content = (
        '<div data-llm-status="started work on updates"></div><div data-llm-status="finished work items"></div>'
    )

    reset_comment_reaction_resolution_cache()
    try:
        result = record_reaction_snapshot(
            pr,
            phase=PHASE_LLM_WORKING,
            base_dir=tmp_path,
            current_time=current_time,
            html_content=html_content,
            enable_snapshots=False,
        )
        assert result is None
        assert pr.get("llm_statuses") == ["started work on updates", "finished work items"]
        assert not any(tmp_path.iterdir())
        assert comment_reactions_marked_finished(pr, pr["commentNodes"]) is True
    finally:
        reset_comment_reaction_resolution_cache()


def test_record_reaction_snapshot_skips_when_no_reactions(tmp_path):
    pr = _sample_pr()
    pr["commentNodes"] = []
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)
    assert result is None
    assert not list(tmp_path.iterdir())


def test_draft_pr_without_review_requests_fetches_llm_statuses(tmp_path):
    """Draft PRs with no review requests should have llm_statuses populated even without reactions.

    The PR timeline always contains both 'started work' and 'finished work' events when
    Copilot has finished.  Without this fix the tool never fetches the PR HTML (because
    there are no comment reactions) so llm_statuses stays empty and the PR is
    misclassified as LLM working instead of phase1.  Regression for #266.
    """
    html_with_both = """
    <html><body>
        <div class="prc-PageLayout-Content-xWL-A">
            <div class="TimelineItem-body">
                <strong>Copilot</strong>
                <a title="View session" href="https://github.com/cat2151/cat-repo-auditor/agents/pull/19?session_id=abc">started work</a>
                on behalf of <a href="/cat2151">cat2151</a>
            </div>
            <div class="TimelineItem-body">
                <strong>Copilot</strong>
                <a title="View session" href="https://github.com/copilot/tasks/pull/PR_xxx?session_id=abc">finished work</a>
                on behalf of <a href="/cat2151">cat2151</a>
            </div>
        </div>
    </body></html>
    """
    pr = {
        "isDraft": True,
        "reviews": [],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [],
        "title": "Fix: permissions",
        "url": "https://github.com/cat2151/cat-repo-auditor/pull/19",
        "repository": {"owner": "cat2151", "name": "cat-repo-auditor"},
    }
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = record_reaction_snapshot(
        pr,
        phase=PHASE_LLM_WORKING,
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html_with_both,
    )
    assert result is None  # no snapshot saved (no reactions)
    assert not list(tmp_path.iterdir())  # no files written
    # But llm_statuses must be populated from the HTML
    assert pr.get("llm_statuses") is not None
    assert any("started work" in s.lower() for s in pr["llm_statuses"])
    assert any("finished work" in s.lower() for s in pr["llm_statuses"])
    # The resulting phase decision must be phase1, not LLM working
    assert determine_phase(pr) == PHASE_1


def test_draft_pr_without_review_requests_refetches_when_only_started_cached(tmp_path):
    """Draft PR: if cache has only 'started work', re-fetch HTML on next iteration.

    Regression test for issue #266 (re-occurrence): After the first iteration
    caches only "started work" (because "finished work" hadn't appeared yet),
    subsequent iterations were reusing the stale cache and never discovering
    "finished work".  The fix: only use the cache when it already contains a
    "finished" signal (i.e., llm_working_from_statuses returns False); otherwise
    re-fetch to check for updates.
    """
    html_only_started = """
    <html><body>
        <div class="prc-PageLayout-Content-xWL-A">
            <div class="TimelineItem-body">
                <strong>Copilot</strong>
                <a title="View session" href="https://github.com/cat2151/voicevox-playground/agents/pull/126?session_id=abc">started work</a>
                on behalf of <a href="/cat2151">cat2151</a>
            </div>
        </div>
    </body></html>
    """
    html_with_finished = """
    <html><body>
        <div class="prc-PageLayout-Content-xWL-A">
            <div class="TimelineItem-body">
                <strong>Copilot</strong>
                <a title="View session" href="https://github.com/cat2151/voicevox-playground/agents/pull/126?session_id=abc">started work</a>
                on behalf of <a href="/cat2151">cat2151</a>
            </div>
            <div class="TimelineItem-body">
                <strong>Copilot</strong>
                <!-- Note: 'finished work' uses github.com/copilot/tasks/... domain intentionally;
                     this matches the real GitHub HTML where 'finished work' links differ from
                     'started work' links (verified via curl of the actual PR page). -->
                <a title="View session" href="https://github.com/copilot/tasks/pull/PR_kwDORNCauM7HHgMY?session_id=abc">finished work</a>
                on behalf of <a href="/cat2151">cat2151</a>
            </div>
        </div>
    </body></html>
    """
    pr = {
        "isDraft": True,
        "reviews": [],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [],
        "title": "Show user-friendly VOICEVOX server connection messages instead of raw Failed to fetch",
        "url": "https://github.com/cat2151/voicevox-playground/pull/126",
        "repository": {"owner": "cat2151", "name": "voicevox-playground"},
    }
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    # First iteration: only "started work" is available
    record_reaction_snapshot(
        pr,
        phase=PHASE_LLM_WORKING,
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html_only_started,
    )
    assert any("started work" in s.lower() for s in (pr.get("llm_statuses") or []))
    assert not any("finished work" in s.lower() for s in (pr.get("llm_statuses") or []))
    assert determine_phase(pr) == PHASE_LLM_WORKING

    # Reset per-iteration flag (simulates start of next monitoring iteration)
    reset_snapshot_cache(clear_content_cache=False)

    # Second iteration: "finished work" is now available in HTML
    pr2 = {k: v for k, v in pr.items() if k != "llm_statuses"}  # fresh PR dict (no llm_statuses pre-set)
    record_reaction_snapshot(
        pr2,
        phase=PHASE_LLM_WORKING,
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html_with_finished,
    )
    # Must detect "finished work" even though cache had "started work" only
    assert any("finished work" in s.lower() for s in (pr2.get("llm_statuses") or [])), (
        "Second iteration should detect 'finished work' from HTML, not use stale 'started work' cache"
    )
    assert determine_phase(pr2) == PHASE_1


def test_record_reaction_snapshot_deduplicates_per_pr(tmp_path):
    pr = _sample_pr()
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    first = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)
    second = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)

    assert first is not None
    assert second is None
    snapshot_dirs = [p for p in tmp_path.iterdir() if p.is_dir()]
    assert len(snapshot_dirs) == 1


def test_markdown_filters_zero_reaction_comments_and_renders_body(tmp_path):
    pr = _sample_pr()
    pr["commentNodes"].append(
        {
            "body": "No reactions here",
            "reactionGroups": [
                {"content": "THUMBS_UP", "users": {"totalCount": 0}},
            ],
        }
    )
    pr["body"] = "Line1\nLine2"
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = save_pr_snapshot(pr, reason="comment_reactions_detected", base_dir=tmp_path, current_time=current_time)

    markdown_content = result["markdown_path"].read_text(encoding="utf-8")
    assert "THUMBS_UP" not in markdown_content
    assert "Line1\nLine2" in markdown_content
    assert "- **commentNodes**:" in markdown_content


def test_snapshot_not_rewritten_when_unchanged(tmp_path):
    pr = _sample_pr()
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = save_pr_snapshot(pr, reason="comment_reactions_detected", base_dir=tmp_path, current_time=current_time)
    raw_path = result["raw_path"]
    markdown_path = result["markdown_path"]

    raw_mtime = raw_path.stat().st_mtime_ns
    markdown_mtime = markdown_path.stat().st_mtime_ns

    result_second = save_pr_snapshot(
        pr, reason="comment_reactions_detected", base_dir=tmp_path, current_time=current_time
    )

    assert result_second["raw_path"] == raw_path
    assert result_second["markdown_path"] == markdown_path
    assert raw_path.stat().st_mtime_ns == raw_mtime
    assert markdown_path.stat().st_mtime_ns == markdown_mtime


def test_default_snapshot_dir():
    assert DEFAULT_SNAPSHOT_BASE_DIR == Path("pr_phase_snapshots")
