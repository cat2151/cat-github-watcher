import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor.phase_detector import PHASE_LLM_WORKING
from src.gh_pr_phase_monitor.pr_data_recorder import (
    DEFAULT_SNAPSHOT_BASE_DIR,
    _escape_newlines,
    _fetch_pr_html,
    _html_to_simple_markdown,
    _json_to_markdown,
    _reset_snapshot_cache,
    record_reaction_snapshot,
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
def reset_snapshot_cache():
    _reset_snapshot_cache()
    yield
    _reset_snapshot_cache()


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
    assert snapshot_dir.name.startswith("octocat_hello-world_PR123_20240102_030405")

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


def test_record_reaction_snapshot_skips_when_no_reactions(tmp_path):
    pr = _sample_pr()
    pr["commentNodes"] = []
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)
    assert result is None
    assert not list(tmp_path.iterdir())


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


def test_html_to_simple_markdown():
    """Test HTML to markdown conversion"""
    html = """
    <html>
    <head><title>Test</title></head>
    <body>
        <h1>Main Title</h1>
        <h2>Subtitle</h2>
        <p>This is a <strong>bold</strong> paragraph with a <a href="https://example.com">link</a>.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <pre>code block</pre>
        <script>alert('test');</script>
    </body>
    </html>
    """
    result = _html_to_simple_markdown(html)

    assert "# Main Title" in result
    assert "## Subtitle" in result
    assert "**bold**" in result
    assert "[link](https://example.com)" in result
    assert "- Item 1" in result
    assert "- Item 2" in result
    assert "```" in result
    assert "code block" in result
    assert "alert('test')" not in result  # Script should be removed


def test_html_to_simple_markdown_empty():
    """Test HTML to markdown with empty input"""
    assert _html_to_simple_markdown("") == ""
    assert _html_to_simple_markdown(None) == ""


def test_fetch_pr_html_mocked():
    """Test HTML fetching with mock"""
    mock_html = "<html><body><h1>Test PR</h1></body></html>"

    with patch("src.gh_pr_phase_monitor.pr_data_recorder.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_html

        result = _fetch_pr_html("https://github.com/test/repo/pull/123")
        assert result == mock_html


def test_fetch_pr_html_failure():
    """Test HTML fetching failure handling"""
    with patch("src.gh_pr_phase_monitor.pr_data_recorder.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""

        result = _fetch_pr_html("https://github.com/test/repo/pull/123")
        assert result is None


def test_save_pr_snapshot_with_html(tmp_path):
    """Test that save_pr_snapshot saves HTML and markdown when curl succeeds"""
    mock_html = "<html><body><h1>Test PR Page</h1><p>Some content</p></body></html>"
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    with patch("src.gh_pr_phase_monitor.pr_data_recorder.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_html

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

        # Verify HTML content
        html_content = result["html_path"].read_text(encoding="utf-8")
        assert html_content == mock_html

        # Verify HTML markdown conversion
        html_md_content = result["html_md_path"].read_text(encoding="utf-8")
        assert "# Test PR Page" in html_md_content
        assert "Some content" in html_md_content


def test_save_pr_snapshot_without_html_when_fetch_fails(tmp_path):
    """Test that save_pr_snapshot works even when HTML fetch fails"""
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    with patch("src.gh_pr_phase_monitor.pr_data_recorder.subprocess.run") as mock_run:
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

    with patch("src.gh_pr_phase_monitor.pr_data_recorder.subprocess.run") as mock_run:
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


def test_json_to_markdown_simple_dict():
    """Test JSON to markdown conversion for simple dictionary"""
    data = {"name": "test", "value": 42, "enabled": True, "empty": None}
    result = _json_to_markdown(data)

    assert "- **name**: test" in result
    assert "- **value**: 42" in result
    assert "- **enabled**: True" in result
    assert "- **empty**: null" in result


def test_escape_newlines():
    """Test the newline escape helper function"""
    assert _escape_newlines("Line 1\nLine 2") == "Line 1\\nLine 2"
    assert _escape_newlines("Line 1\r\nLine 2") == "Line 1\\r\\nLine 2"
    assert _escape_newlines("No newlines") == "No newlines"
    assert _escape_newlines("") == ""
    assert _escape_newlines("\n\r") == "\\n\\r"


def test_json_to_markdown_nested_dict():
    """Test JSON to markdown conversion for nested dictionary"""
    data = {"user": {"login": "octocat", "id": 123}, "settings": {}}
    result = _json_to_markdown(data)

    assert "- **user**:" in result
    assert "  - **login**: octocat" in result
    assert "  - **id**: 123" in result
    assert "- **settings**: {}" in result


def test_json_to_markdown_list():
    """Test JSON to markdown conversion for lists"""
    data = {"items": [1, 2, 3], "empty_list": []}
    result = _json_to_markdown(data)

    assert "- **items**: (3 items)" in result
    assert "  - [1]: 1" in result
    assert "  - [2]: 2" in result
    assert "  - [3]: 3" in result
    assert "- **empty_list**: []" in result


def test_json_to_markdown_list_of_dicts():
    """Test JSON to markdown conversion for list of dictionaries"""
    data = {
        "comments": [
            {"body": "First comment", "author": "user1"},
            {"body": "Second comment", "author": "user2"},
        ],
    }
    result = _json_to_markdown(data)

    assert "- **comments**: (2 items)" in result
    assert "  - [1]:" in result
    assert "    - **body**: First comment" in result
    assert "    - **author**: user1" in result
    assert "  - [2]:" in result
    assert "    - **body**: Second comment" in result
    assert "    - **author**: user2" in result


def test_json_to_markdown_escapes_newlines():
    """Test that JSON to markdown properly escapes newlines in strings"""
    data = {"text": "Line 1\nLine 2\r\nLine 3", "number": 42}
    result = _json_to_markdown(data)

    assert "- **text**: Line 1\\nLine 2\\r\\nLine 3" in result
    assert "- **number**: 42" in result


def test_json_to_markdown_complex_structure():
    """Test JSON to markdown with complex nested structure"""
    data = {
        "title": "Test PR",
        "author": {"login": "octocat"},
        "reviews": [{"state": "APPROVED", "author": {"login": "reviewer1"}}],
        "commentNodes": [],
    }
    result = _json_to_markdown(data)

    assert "- **title**: Test PR" in result
    assert "- **author**:" in result
    assert "  - **login**: octocat" in result
    assert "- **reviews**: (1 items)" in result
    assert "  - [1]:" in result
    assert "    - **state**: APPROVED" in result
    assert "    - **author**:" in result
    assert "      - **login**: reviewer1" in result
    assert "- **commentNodes**: []" in result


def test_save_pr_snapshot_markdown_contains_formatted_data(tmp_path):
    """Test that markdown snapshot contains formatted markdown instead of raw JSON"""
    current_time = datetime(2024, 1, 2, 3, 4, 5)
    result = save_pr_snapshot(
        _sample_pr(),
        reason="comment_reactions_detected",
        base_dir=tmp_path,
        current_time=current_time,
        fetch_html=False,
    )

    markdown_content = result["markdown_path"].read_text(encoding="utf-8")

    # Should contain markdown-formatted data, not JSON syntax
    assert "- **title**: Test PR" in markdown_content
    assert "- **url**: https://github.com/octocat/hello-world/pull/123" in markdown_content
    assert "- **author**:" in markdown_content
    assert "  - **login**: octocat" in markdown_content

    # Should NOT contain JSON syntax markers
    assert '"title":' not in markdown_content
    assert '"author": {' not in markdown_content
    assert "```json" not in markdown_content
