"""
Tests for fetch_pr_html and save_pr_snapshot with HTML content
"""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor.llm_status_extractor import _extract_llm_statuses
from src.gh_pr_phase_monitor.phase_detector import (
    PHASE_LLM_WORKING,
    comment_reactions_marked_finished,
    reset_comment_reaction_resolution_cache,
)
from src.gh_pr_phase_monitor.pr_data_recorder import (
    record_reaction_snapshot,
    reset_snapshot_cache,
    save_pr_snapshot,
)
from src.gh_pr_phase_monitor.pr_html_fetcher import _fetch_pr_html, _html_to_simple_markdown


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

def test_fetch_pr_html_mocked():
    """Test HTML fetching with mock"""
    mock_html = "<html><body><h1>Test PR</h1></body></html>"

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_html + "\n200"

        result = _fetch_pr_html("https://github.com/test/repo/pull/123")
        assert result == mock_html


def test_fetch_pr_html_failure():
    """Test HTML fetching failure handling"""
    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""

        result = _fetch_pr_html("https://github.com/test/repo/pull/123")
        assert result is None


def test_fetch_pr_html_non_2xx_returns_none():
    """Test that HTTP non-2xx responses return None"""
    error_html = "<html><body>Not Found</body></html>"

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = error_html + "\n404"

        result = _fetch_pr_html("https://github.com/test/repo/pull/123")
        assert result is None


def test_save_pr_snapshot_with_html(tmp_path):
    """Test that save_pr_snapshot saves HTML, markdown, and LLM statuses when curl succeeds"""
    mock_html = """
    <html>
    <body>
        <div class="prc-PageLayout-Content-xWL-A">
            <h1>Test PR Page</h1>
            <p>Some content</p>
            <h2>LLM status</h2>
            <ul>
                <li>comment</li>
                <li>finished</li>
            </ul>
        </div>
    </body>
    </html>
    """
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_html + "\n200"

        result = save_pr_snapshot(
            _sample_pr(),
            reason="comment_reactions_detected",
            base_dir=tmp_path,
            current_time=current_time,
        )

        # Verify all files were created
        assert result["snapshot_dir"].is_dir()
        assert result["raw_path"].exists()
        assert result["markdown_path"].exists()
        assert "html_path" in result
        assert result["html_path"].exists()
        assert "html_md_path" in result
        assert result["html_md_path"].exists()
        assert "llm_status_path" in result
        assert result["llm_status_path"].exists()
        assert result["llm_statuses"] == ["comment", "finished"]

        # Verify HTML content
        html_content = result["html_path"].read_text(encoding="utf-8")
        assert html_content == mock_html

        # Verify HTML markdown conversion
        html_md_content = result["html_md_path"].read_text(encoding="utf-8")
        assert "# Test PR Page" in html_md_content
        assert "Some content" in html_md_content
        assert "LLM status: comment, finished" in html_md_content


def test_save_pr_snapshot_extracts_llm_statuses_from_html(tmp_path):
    """LLM statuses should be parsed from HTML/markdown and saved alongside snapshots"""
    html = """
    <html>
    <body>
        <div class="prc-PageLayout-Content-xWL-A">
            <h2>LLM status</h2>
            <ul>
                <li>comment</li>
                <li>finished</li>
            </ul>
        </div>
    </body>
    </html>
    """
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = save_pr_snapshot(
        _sample_pr(),
        reason="comment_reactions_detected",
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html,
    )

    status_path = result["llm_status_path"]
    assert status_path.exists()
    status_data = json.loads(status_path.read_text(encoding="utf-8"))
    assert status_data["llm_statuses"] == ["comment", "finished"]
    assert result["llm_statuses"] == ["comment", "finished"]


def test_save_pr_snapshot_extracts_llm_statuses_from_attributes(tmp_path):
    """LLM statuses should be parsed from raw HTML attributes when no visible text exists"""
    html = """
    <html>
    <body>
        <div class="prc-PageLayout-Content-xWL-A">
            <span aria-label="LLM status: finished, comment"></span>
        </div>
    </body>
    </html>
    """
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = save_pr_snapshot(
        _sample_pr(),
        reason="comment_reactions_detected",
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html,
    )

    status_path = result["llm_status_path"]
    assert status_path.exists()
    status_data = json.loads(status_path.read_text(encoding="utf-8"))
    assert status_data["llm_statuses"] == ["finished, comment"]
    assert result["llm_statuses"] == ["finished, comment"]


def test_save_pr_snapshot_extracts_llm_statuses_from_timeline_events(tmp_path):
    """LLM statuses should be parsed from Copilot session timeline entries"""
    html = """
    <html>
    <body>
        <div class="prc-PageLayout-Content-xWL-A">
            <div class="TimelineItem-body">
                <strong>Codex</strong>
                <a title="View session" class="Link--secondary" href="https://github.com/example/agents/pull/22?session_id=aaa">started work</a>
                on behalf of <a href="/cat2151">cat2151</a>
                <relative-time datetime="2024-05-01T00:00:00Z">9 minutes ago</relative-time>
                <a href="https://github.com/example/agents/pull/22?session_id=aaa">View session</a>
            </div>
            <div class="TimelineItem-body">
                <strong>Codex</strong>
                <a title="View session" class="Link--secondary" href="https://github.com/example/tasks/pull/PR_123?session_id=bbb">finished work</a>
                on behalf of <a href="/cat2151">cat2151</a>
                <relative-time datetime="2024-05-01T00:00:00Z">5 minutes ago</relative-time>
            </div>
            <div class="TimelineItem-body">
                <strong>Copilot</strong>
                <a title="View session" class="Link--secondary" href="https://github.com/example/agents/pull/22?session_id=ccc">started reviewing</a>
                on behalf of <a href="/cat2151">cat2151</a>
            </div>
            <div class="TimelineItem-body">
                <span class="author">cat2151</span>
                commented
                <relative-time datetime="2024-05-01T00:00:00Z">10 minutes ago</relative-time>
                <div class="comment-body">
                    <p>@codex[agent] apply changes based on the comments in this pull request</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = save_pr_snapshot(
        _sample_pr(),
        reason="comment_reactions_detected",
        base_dir=tmp_path,
        current_time=current_time,
        html_content=html,
    )

    status_path = result["llm_status_path"]
    assert status_path.exists()
    status_data = json.loads(status_path.read_text(encoding="utf-8"))
    assert status_data["llm_statuses"] == [
        "Codex started work on behalf of cat2151 9 minutes ago",
        "Codex finished work on behalf of cat2151 5 minutes ago",
        "Copilot started reviewing on behalf of cat2151",
    ]
    assert result["llm_statuses"] == [
        "Codex started work on behalf of cat2151 9 minutes ago",
        "Codex finished work on behalf of cat2151 5 minutes ago",
        "Copilot started reviewing on behalf of cat2151",
    ]


def test_extract_llm_statuses_filters_noise_and_keeps_timeline():
    """Timeline bodies with session IDs should be kept while nav noise is dropped."""
    html = """
    <html>
    <body>
        <div class="TimelineItem-body">
            <strong>Codex</strong>
            <a title="View session" href="https://github.com/example/agents/pull/91?session_id=aaa">started work</a>
            on behalf of <a href="/cat2151">cat2151</a>
            <relative-time datetime="2026-02-08T11:59:00Z">11:59</relative-time>
        </div>
        <div class="TimelineItem-body">
            <strong>Codex</strong>
            <a title="View session" href="https://github.com/example/agents/pull/91?session_id=bbb">finished work</a>
            on behalf of <a href="/cat2151">cat2151</a>
            <relative-time datetime="2026-02-08T12:09:00Z">12:09</relative-time>
        </div>
        <div class="TimelineItem-body">
            <strong>Copilot</strong>
            <a title="View session" href="https://github.com/example/agents/pull/91?session_id=ccc">started reviewing</a>
            on behalf of <a href="/cat2151">cat2151</a>
            <relative-time datetime="2026-02-08T12:10:00Z">12:10</relative-time>
        </div>
        <div class="TimelineItem-body">
            Sign up for free to join this conversation on GitHub. Already have an account? Sign in to comment
        </div>
        <div class="TimelineItem-body">
            Uh oh! There was an error while loading. <a href="https://example.com/reload">Please reload this page</a>.
        </div>
    </body>
    </html>
    """
    html_md = _html_to_simple_markdown(html)

    statuses = _extract_llm_statuses(html, html_md)

    assert statuses == [
        "Codex started work on behalf of cat2151 11:59",
        "Codex finished work on behalf of cat2151 12:09",
        "Copilot started reviewing on behalf of cat2151 12:10",
    ]


def test_save_pr_snapshot_without_html_when_fetch_fails(tmp_path):
    """Test that save_pr_snapshot works even when HTML fetch fails"""
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""

        result = save_pr_snapshot(
            _sample_pr(),
            reason="comment_reactions_detected",
            base_dir=tmp_path,
            current_time=current_time,
        )

        # Verify basic files were created
        assert result["snapshot_dir"].is_dir()
        assert result["raw_path"].exists()
        assert result["markdown_path"].exists()

        # Verify HTML files were not created
        assert "html_path" not in result
        assert "html_md_path" not in result


def test_save_pr_snapshot_with_fetch_html_disabled(tmp_path):
    """Test that save_pr_snapshot skips HTML fetch when fetch_html=False"""
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        result = save_pr_snapshot(
            _sample_pr(),
            reason="comment_reactions_detected",
            base_dir=tmp_path,
            current_time=current_time,
            fetch_html=False,
        )

        # Verify subprocess.run was never called
        mock_run.assert_not_called()

        # Verify basic files were created
        assert result["snapshot_dir"].is_dir()
        assert result["raw_path"].exists()
        assert result["markdown_path"].exists()

        # Verify HTML files were not created
        assert "html_path" not in result
        assert "html_md_path" not in result


