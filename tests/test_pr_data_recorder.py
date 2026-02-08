import json
from datetime import datetime
from pathlib import Path

import pytest

from src.gh_pr_phase_monitor.phase_detector import PHASE_LLM_WORKING
from src.gh_pr_phase_monitor.pr_data_recorder import (
    DEFAULT_SNAPSHOT_BASE_DIR,
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
    assert "commentNodes" in markdown_content


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
    assert "commentNodes" in markdown_content


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
