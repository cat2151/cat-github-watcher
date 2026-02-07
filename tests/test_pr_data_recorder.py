import json
from datetime import datetime

from src.gh_pr_phase_monitor.phase_detector import PHASE_LLM_WORKING
from src.gh_pr_phase_monitor.pr_data_recorder import record_reaction_snapshot, save_pr_snapshot


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


def test_record_reaction_snapshot_respects_phase_and_reactions(tmp_path):
    pr = _sample_pr()
    current_time = datetime(2024, 1, 2, 3, 4, 5)

    result = record_reaction_snapshot(pr, phase="phase3", base_dir=tmp_path, current_time=current_time)
    assert result is None
    assert not list(tmp_path.iterdir())

    result = record_reaction_snapshot(pr, phase=PHASE_LLM_WORKING, base_dir=tmp_path, current_time=current_time)
    assert result is not None
    assert result["markdown_path"].exists()
