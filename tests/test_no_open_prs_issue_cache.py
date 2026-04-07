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


def test_empty_cache_bypasses_etag_304_and_fetches_issues(mocker, capsys):
    """A cold start must fetch issues even when the issue ETag says 304."""
    mocker.patch.object(display_module, "_cached_top_issues", [])
    mocker.patch.object(display_module, "_issue_cache_state", {"needs_refresh": False})
    assert display_module._cached_top_issues == []

    mock_get_repos = mocker.patch(
        "src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues"
    )
    mock_get_repos.return_value = [{"name": "repo-b", "owner": "testuser", "openIssueCount": 1}]

    mocker.patch("src.gh_pr_phase_monitor.ui.display.check_issues_etag_changed", return_value=False)
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    fetched_issues = [
        {
            "title": "Fresh Issue B",
            "url": "https://github.com/testuser/repo-b/issues/5",
            "number": 5,
            "repository": {"owner": "testuser", "name": "repo-b"},
        }
    ]
    mock_get_issues.return_value = fetched_issues

    display_issues_from_repos_without_prs(None)

    mock_get_issues.assert_called_once()
    out = capsys.readouterr().out
    assert "Fresh Issue B" in out
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


def test_display_cached_top_issues_filters_repos_with_prs(mocker, capsys):
    """display_cached_top_issues must exclude issues from repos that now have open PRs.

    Scenario (skip path in iteration_runner):
    - Cache contains issues from repo-a and repo-b.
    - repos_with_prs is passed and contains repo-a (it now has an open PR).
    - Expected: repo-a's issues are NOT shown; repo-b's issues ARE shown.
    - Expected: cache is cleared entirely and needs_refresh flag is set.
    """
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
    mocker.patch.object(display_module, "_issue_cache_state", {"needs_refresh": False})

    repos_with_prs = [{"owner": "testuser", "name": "repo-a"}]
    display_cached_top_issues(repos_with_prs)

    out = capsys.readouterr().out
    # repo-b's issue should appear
    assert "Issue from repo-b" in out
    # repo-a now has a PR — its issue must NOT appear
    assert "Issue from repo-a" not in out
    # Cache must be fully cleared so the next non-skip iteration re-fetches
    assert display_module._cached_top_issues == []
    # needs_refresh flag must be set so the ETag-304 fast path is bypassed next time
    assert display_module._issue_cache_state["needs_refresh"] is True


def test_needs_refresh_flag_bypasses_etag_304(mocker, capsys):
    """ETag-304 fast path is bypassed when needs_refresh is True.

    Scenario:
    - display_cached_top_issues cleared the cache (overlap with PR repos) and set needs_refresh=True.
    - Next call to display_issues_from_repos_without_prs: ETag returns 304.
    - The 304 fast path must be skipped so a full GraphQL fetch is performed.
    - After the fetch the flag must be reset to False.
    """
    mocker.patch.object(display_module, "_cached_top_issues", [])
    mocker.patch.object(display_module, "_issue_cache_state", {"needs_refresh": True})

    mock_get_repos = mocker.patch(
        "src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues"
    )
    mock_get_repos.return_value = [{"name": "repo-b", "owner": "testuser", "openIssueCount": 1}]

    mock_etag = mocker.patch("src.gh_pr_phase_monitor.ui.display.check_issues_etag_changed")
    mock_etag.return_value = False  # Would trigger 304 fast path if flag not set

    fetched_issues = [
        {
            "title": "Fresh Issue B",
            "url": "https://github.com/testuser/repo-b/issues/5",
            "number": 5,
            "repository": {"owner": "testuser", "name": "repo-b"},
        }
    ]
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_get_issues.return_value = fetched_issues

    display_issues_from_repos_without_prs(None)

    # Full GraphQL fetch must have been performed (flag bypassed the 304 shortcut)
    mock_get_issues.assert_called_once()

    out = capsys.readouterr().out
    assert "Fresh Issue B" in out

    # Flag must be reset after the successful fetch
    assert display_module._issue_cache_state["needs_refresh"] is False
    # Cache should now contain the freshly fetched issues
    assert list(display_module._cached_top_issues) == fetched_issues


def test_display_cached_top_issues_no_filter_when_no_prs(mocker, capsys):
    """display_cached_top_issues shows all cached issues when repos_with_prs is empty."""
    cached = [
        {
            "title": "Issue from repo-a",
            "url": "https://github.com/testuser/repo-a/issues/1",
            "number": 1,
            "repository": {"owner": "testuser", "name": "repo-a"},
        },
    ]
    mocker.patch.object(display_module, "_cached_top_issues", list(cached))

    display_cached_top_issues([])

    out = capsys.readouterr().out
    assert "Issue from repo-a" in out
    # Cache should be unchanged
    assert len(display_module._cached_top_issues) == 1


def test_display_cached_top_issues_no_filter_when_repos_with_prs_not_provided(mocker, capsys):
    """display_cached_top_issues shows all cached issues when repos_with_prs is not provided."""
    cached = [
        {
            "title": "Issue from repo-a",
            "url": "https://github.com/testuser/repo-a/issues/1",
            "number": 1,
            "repository": {"owner": "testuser", "name": "repo-a"},
        },
    ]
    mocker.patch.object(display_module, "_cached_top_issues", list(cached))

    display_cached_top_issues()

    out = capsys.readouterr().out
    assert "Issue from repo-a" in out
    # Cache should be unchanged
    assert len(display_module._cached_top_issues) == 1
