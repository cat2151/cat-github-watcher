"""
Tests for cache-related behavior of display_issues_from_repos_without_prs
"""

import src.gh_pr_phase_monitor.ui.display as display_module
from src.gh_pr_phase_monitor.ui.display import display_cached_top_issues, display_issues_from_repos_without_prs


def test_display_cached_top_issues_empty(mocker, capsys):
    """display_cached_top_issues outputs nothing when cache is empty"""
    mocker.patch.object(display_module, "_cached_top_issues", [])
    display_cached_top_issues()
    out = capsys.readouterr().out
    assert out == ""


def test_display_cached_top_issues_shows_cached_data(mocker, capsys):
    """display_cached_top_issues displays the cached issues without calling get_issues_from_repositories"""
    mocker.patch.object(display_module, "_cached_top_issues", [
        {
            "title": "Cached Issue 1",
            "url": "https://github.com/testuser/test-repo/issues/10",
            "number": 10,
        },
        {
            "title": "Cached Issue 2",
            "url": "https://github.com/testuser/test-repo/issues/20",
            "number": 20,
        },
    ])
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    display_cached_top_issues()
    out = capsys.readouterr().out
    assert "Cached Issue 1" in out
    assert "Cached Issue 2" in out
    assert "#10" in out
    assert "#20" in out
    # Confirm no API calls were made
    mock_get_issues.assert_not_called()


def test_display_issues_populates_cache(mocker):
    """display_issues_from_repos_without_prs populates _cached_top_issues after fetching"""
    mocker.patch.object(display_module, "_cached_top_issues", [])
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mocker.patch("src.gh_pr_phase_monitor.ui.display.check_issues_etag_changed", return_value=True)
    mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]
    fetched_issues = [
        {"title": "Issue A", "url": "https://github.com/testuser/test-repo/issues/1", "number": 1},
    ]
    mock_get_issues.return_value = fetched_issues
    display_issues_from_repos_without_prs(None)
    assert list(display_module._cached_top_issues) == fetched_issues


def test_etag_304_filters_cache_when_repo_gains_pr(mocker, capsys):
    """Regression: ETag 304 path must not display cached issues from repos that now have open PRs.

    Scenario:
    - Cache contains issues from repo-a (no PR) and repo-b (no PR).
    - A PR is opened for repo-a, so get_repositories_with_no_prs_and_open_issues returns only [repo-b].
    - ETag check returns False (304, no change in repo-b's issues).
    - Expected: only repo-b's issues are shown; repo-a's issues are excluded from the display.
    """
    # Pre-populate the cache with issues from two repos (one of which will gain a PR)
    stale_cache = [
        {
            "title": "Issue from repo-a",
            "url": "https://github.com/testuser/repo-a/issues/1",
            "number": 1,
            "repository": {"owner": "testuser", "name": "repo-a"},
        },
        {
            "title": "Issue from repo-b",
            "url": "https://github.com/testuser/repo-b/issues/2",
            "number": 2,
            "repository": {"owner": "testuser", "name": "repo-b"},
        },
    ]
    mocker.patch.object(display_module, "_cached_top_issues", list(stale_cache))

    # repo-a now has a PR → only repo-b is in repos_with_issues
    mock_get_repos = mocker.patch(
        "src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues"
    )
    mock_get_repos.return_value = [{"name": "repo-b", "owner": "testuser", "openIssueCount": 1}]

    # ETag check returns False (304 — no change in repo-b)
    mock_etag = mocker.patch("src.gh_pr_phase_monitor.ui.display.check_issues_etag_changed")
    mock_etag.return_value = False

    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")

    display_issues_from_repos_without_prs(None)

    # 304 path must not make any GraphQL fetch
    mock_get_issues.assert_not_called()

    out = capsys.readouterr().out
    # repo-b's issue should appear
    assert "Issue from repo-b" in out
    # repo-a now has a PR — its cached issue must NOT appear
    assert "Issue from repo-a" not in out
    # Cache should have been updated to remove repo-a's issues and keep repo-b's
    assert all(i.get("repository", {}).get("name") != "repo-a" for i in display_module._cached_top_issues)
    assert any(i.get("repository", {}).get("name") == "repo-b" for i in display_module._cached_top_issues)
