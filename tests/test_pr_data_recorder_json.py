"""
Tests for json_to_markdown, escape_newlines, and snapshot iteration behavior
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor.phase_detector import (
    PHASE_LLM_WORKING,
)
from src.gh_pr_phase_monitor.pr_data_recorder import (
    record_reaction_snapshot,
    reset_snapshot_cache,
    save_pr_snapshot,
)
from src.gh_pr_phase_monitor.snapshot_markdown import _escape_newlines, _json_to_markdown


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


def test_multiple_snapshots_same_directory(tmp_path):
    """Test that multiple snapshots of the same PR go into the same directory"""
    pr = _sample_pr()
    time1 = datetime(2024, 1, 2, 3, 4, 5)
    time2 = datetime(2024, 1, 2, 4, 5, 6)

    result1 = save_pr_snapshot(pr, reason="first_snapshot", base_dir=tmp_path, current_time=time1, fetch_html=False)
    result2 = save_pr_snapshot(pr, reason="second_snapshot", base_dir=tmp_path, current_time=time2, fetch_html=False)

    # Both snapshots should be in the same directory
    assert result1["snapshot_dir"] == result2["snapshot_dir"]
    assert result1["snapshot_dir"].name == "octocat_hello-world_PR123"

    # But the files should be different (different timestamps)
    assert result1["raw_path"].name == "20240102_030405_raw.json"
    assert result2["raw_path"].name == "20240102_040506_raw.json"
    assert result1["markdown_path"].name == "20240102_030405_summary.md"
    assert result2["markdown_path"].name == "20240102_040506_summary.md"

    # Both files should exist
    assert result1["raw_path"].exists()
    assert result2["raw_path"].exists()
    assert result1["markdown_path"].exists()
    assert result2["markdown_path"].exists()

    # The directory should contain at least these 4 files (2 raw, 2 markdown)
    files_in_dir = set(result1["snapshot_dir"].iterdir())
    expected_files = {
        result1["raw_path"],
        result2["raw_path"],
        result1["markdown_path"],
        result2["markdown_path"],
    }
    assert expected_files.issubset(files_in_dir)


def test_record_reaction_snapshot_across_iterations(tmp_path):
    """Test content-based deduplication across iterations"""
    pr = _sample_pr()
    time1 = datetime(2024, 1, 2, 3, 4, 5)
    time2 = datetime(2024, 1, 2, 3, 5, 10)
    time3 = datetime(2024, 1, 2, 3, 10, 15)

    # Mock HTML fetching to return deterministic content
    mock_html = "<html><body><h1>Test PR</h1></body></html>"

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_html + "\n200"

        # First iteration - should record snapshot
        result1 = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=time1)
        assert result1 is not None
        assert result1["markdown_path"].exists()

        # Same iteration - should NOT record (once flag)
        result2 = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=time1)
        assert result2 is None

        # Simulate new iteration by resetting cache
        reset_snapshot_cache()

        # New iteration with SAME content - should NOT record (content unchanged)
        result3 = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=time2)
        assert result3 is None

        # Modify PR content
        pr["title"] = "Modified Test PR"

        # Simulate another new iteration
        reset_snapshot_cache()

        # New iteration with CHANGED content - should record new snapshot
        result4 = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=time3)
        assert result4 is not None
        assert result4["markdown_path"].exists()

        # Verify both snapshots are in the same directory but have different timestamps
        assert result1["snapshot_dir"] == result4["snapshot_dir"]
        assert result1["markdown_path"].name == "20240102_030405_summary.md"
        assert result4["markdown_path"].name == "20240102_031015_summary.md"

        # Both files should exist
        assert result1["markdown_path"].exists()
        assert result4["markdown_path"].exists()

        # Only 2 snapshots should have been created (not 3)
        snapshot_files = [f for f in result1["snapshot_dir"].iterdir() if f.name.endswith("_summary.md")]
        assert len(snapshot_files) == 2


def test_record_reaction_snapshot_html_tag_changes_ignored(tmp_path):
    """Test that HTML tag changes without content changes don't create duplicate snapshots"""
    pr = _sample_pr()
    time1 = datetime(2024, 1, 2, 3, 4, 5)
    time2 = datetime(2024, 1, 2, 3, 5, 10)

    # Mock HTML with identical content but different HTML tags (e.g., session IDs, timestamps)
    mock_html_1 = """
    <html data-session="abc123" data-timestamp="1234567890">
    <body>
        <div class="prc-PageLayout-Content-xWL-A">
            <h1>Test PR</h1>
            <p>This is the PR content that matters</p>
        </div>
    </body>
    </html>
    """

    mock_html_2 = """
    <html data-session="xyz789" data-timestamp="9876543210">
    <body>
        <div class="prc-PageLayout-Content-xWL-A">
            <h1>Test PR</h1>
            <p>This is the PR content that matters</p>
        </div>
    </body>
    </html>
    """

    with patch("src.gh_pr_phase_monitor.pr_html_fetcher.subprocess.run") as mock_run:
        # First iteration - should record snapshot
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = mock_html_1 + "\n200"

        result1 = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=time1)
        assert result1 is not None
        assert result1["markdown_path"].exists()

        # Simulate new iteration by resetting cache
        reset_snapshot_cache()

        # Second iteration with different HTML tags but SAME content - should NOT record
        mock_run.return_value.stdout = mock_html_2 + "\n200"

        result2 = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=time2)
        assert result2 is None

        # Only 1 snapshot should have been created
        snapshot_files = [f for f in result1["snapshot_dir"].iterdir() if f.name.endswith("_summary.md")]
        assert len(snapshot_files) == 1
