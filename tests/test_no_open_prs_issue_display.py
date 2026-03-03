"""
Test to verify that issues are displayed when no repositories with open PRs are found

This test ensures the new behavior requested in the issue:
"Add the condition 'No repositories with open PRs found' to the conditions for displaying the latest issue."
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.colors import colorize_url
from src.gh_pr_phase_monitor.display import display_issues_from_repos_without_prs


def test_issue_url_is_colorized(capsys):
    """Issue URLs should be colorized for easier clicking"""
    url = "https://github.com/testuser/test-repo/issues/1"
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 1,
                }
            ]
            mock_get_issues.return_value = [
                {
                    "title": "Issue 1",
                    "url": url,
                    "number": 1,
                    "updatedAt": "2024-01-01T00:00:00Z",
                    "labels": [],
                    "assignees": [],
                    "repository": {"owner": "testuser", "name": "test-repo"},
                }
            ]

            display_issues_from_repos_without_prs(None)

    colored_url = colorize_url(url)
    output = capsys.readouterr().out
    assert colored_url in output


def test_display_issues_when_no_repos_with_prs():
    """
    Test that display_issues_from_repos_without_prs correctly displays issues
    when there are no repositories with open PRs
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 2,
                    }
                ]

                # Single call now returns all issues (including labeled ones for client-side filtering)
                mock_get_issues.return_value = [
                    {
                        "title": "Good first issue",
                        "url": "https://github.com/testuser/test-repo/issues/1",
                        "number": 1,
                        "updatedAt": "2024-01-01T00:00:00Z",
                        "labels": ["good first issue"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    },
                    {
                        "title": "Issue 2",
                        "url": "https://github.com/testuser/test-repo/issues/2",
                        "number": 2,
                        "updatedAt": "2024-01-02T00:00:00Z",
                        "labels": [],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    },
                ]

                mock_assign.return_value = True

                # Create config with assign_to_copilot enabled via rulesets
                config = {
                    "assign_to_copilot": {},  # Empty section provides defaults
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_good_first_old": True,  # Enable good first issue assignment
                        }
                    ],
                }

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Issues are now fetched in a single call (no duplicate assignment query)
                assert mock_get_issues.call_count == 1

                # Verify assignment was attempted
                mock_assign.assert_called_once()


def test_display_issues_when_no_repos_with_issues():
    """
    Test that display_issues_from_repos_without_prs handles the case
    when there are no repositories with issues
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        # Mock response: no repos with issues
        mock_get_repos.return_value = []

        # Call the function with empty config - should not raise an error
        display_issues_from_repos_without_prs({})

        # Verify that the function fetched repos without PRs
        mock_get_repos.assert_called_once()


def test_display_issues_handles_exceptions():
    """
    Test that display_issues_from_repos_without_prs handles exceptions gracefully
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        # Mock an exception
        mock_get_repos.side_effect = Exception("API Error")

        # Call the function with empty config - should not raise an error
        display_issues_from_repos_without_prs({})

        # Verify that the function attempted to fetch repos
        mock_get_repos.assert_called_once()


def test_display_issues_with_assign_disabled():
    """
    Test that display_issues_from_repos_without_prs does NOT attempt assignment
    when the feature is disabled
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 2,
                    }
                ]

                # Mock issue responses - only one call now for displaying issues
                mock_get_issues.side_effect = [
                    # Only call for top 10 issues
                    [
                        {
                            "title": "Issue 1",
                            "url": "https://github.com/testuser/test-repo/issues/1",
                            "number": 1,
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                        },
                    ],
                ]

                # Create config without rulesets enabling assign flags
                config = {"assign_to_copilot": {}}  # Defaults available, but no ruleset enables it

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Verify that issues were fetched only once (top 10), no assign attempt
                assert mock_get_issues.call_count == 1

                # Verify assignment was NOT attempted (no ruleset enabling it)
                mock_assign.assert_not_called()


def test_display_issues_with_custom_limit():
    """
    Test that display_issues_from_repos_without_prs respects the issue_display_limit config
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            # Mock response: repos with no PRs but with issues
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 10,
                }
            ]

            # Mock issue response - single call returns all issues; slicing is done client-side
            mock_get_issues.return_value = [
                {
                    "title": f"Issue {i}",
                    "url": f"https://github.com/testuser/test-repo/issues/{i}",
                    "number": i,
                    "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                    "author": {"login": "contributor1"},
                    "repository": {"owner": "testuser", "name": "test-repo"},
                }
                for i in range(1, 6)
            ]

            # Create config with custom issue_display_limit, no assign flags
            config = {"assign_to_copilot": {}, "issue_display_limit": 5}

            # Call the function with config
            display_issues_from_repos_without_prs(config)

            # Verify that the function fetched repos without PRs
            mock_get_repos.assert_called_once()

            # Verify that issues were fetched exactly once (no duplicate assignment query)
            assert mock_get_issues.call_count == 1


def test_display_issues_with_none_config():
    """
    Test that display_issues_from_repos_without_prs handles None config gracefully
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            # Mock response: repos with no PRs but with issues
            mock_get_repos.return_value = [
                {
                    "name": "test-repo",
                    "owner": "testuser",
                    "openIssueCount": 10,
                }
            ]

            # Mock issue response - single call; default limit of 10 applied client-side
            mock_get_issues.return_value = [
                {
                    "title": f"Issue {i}",
                    "url": f"https://github.com/testuser/test-repo/issues/{i}",
                    "number": i,
                    "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                    "author": {"login": "contributor1"},
                    "repository": {"owner": "testuser", "name": "test-repo"},
                }
                for i in range(1, 11)
            ]

            # Call the function with None config - should use default limit of 10
            display_issues_from_repos_without_prs(None)

            # Verify that the function fetched repos without PRs
            mock_get_repos.assert_called_once()

            # Verify that issues were fetched exactly once (no duplicate assignment query)
            assert mock_get_issues.call_count == 1


def test_display_issues_with_assign_lowest_number():
    """
    Test that display_issues_from_repos_without_prs correctly assigns the oldest issue
    when assign_old is enabled (replaces assign_lowest_number_issue)
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: repos with no PRs but with issues
                mock_get_repos.return_value = [
                    {
                        "name": "test-repo",
                        "owner": "testuser",
                        "openIssueCount": 3,
                    }
                ]

                # Single call returns all issues; client-side filtering picks the one with lowest number
                mock_get_issues.return_value = [
                    {
                        "title": "Issue with lowest number",
                        "url": "https://github.com/testuser/test-repo/issues/5",
                        "number": 5,
                        "updatedAt": "2024-01-05T00:00:00Z",
                        "labels": ["bug"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    },
                    {
                        "title": "Issue 2",
                        "url": "https://github.com/testuser/test-repo/issues/10",
                        "number": 10,
                        "updatedAt": "2024-01-10T00:00:00Z",
                        "labels": [],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    },
                ]

                mock_assign.return_value = True

                # Create config with assign_old enabled in rulesets
                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_old": True,  # Enable old issue assignment
                        }
                    ],
                }

                # Call the function with config
                display_issues_from_repos_without_prs(config)

                # Verify that the function fetched repos without PRs
                mock_get_repos.assert_called_once()

                # Issues are fetched in a single call (assignment done client-side)
                assert mock_get_issues.call_count == 1

                # Verify assignment was attempted
                mock_assign.assert_called_once()


def test_cache_skips_fetch_on_unchanged_issue_count():
    """
    Second call with the same updatedAt must NOT invoke get_issues_from_repositories again.
    This verifies the cross-iteration cache that reduces GraphQL consumption.
    """
    repo = {"name": "test-repo", "owner": "testuser", "openIssueCount": 5, "updatedAt": "2024-01-01T00:00:00Z"}
    issue_data = [
        {
            "title": "Issue 1",
            "url": "https://github.com/testuser/test-repo/issues/1",
            "number": 1,
            "updatedAt": "2024-01-01T00:00:00Z",
            "labels": [],
            "assignees": [],
            "repository": {"owner": "testuser", "name": "test-repo"},
        }
    ]

    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            mock_get_repos.return_value = [repo]
            mock_get_issues.return_value = issue_data

            # First call: cache is empty, should fetch
            display_issues_from_repos_without_prs(None)
            assert mock_get_issues.call_count == 1

            # Second call: openIssueCount unchanged, should use cache (no new fetch)
            display_issues_from_repos_without_prs(None)
            assert mock_get_issues.call_count == 1, (
                "get_issues_from_repositories should NOT be called again when openIssueCount is unchanged"
            )


def test_cache_refetches_when_issue_count_changes():
    """
    When updatedAt changes between calls, the cache must be invalidated
    and get_issues_from_repositories called again for that repo.
    This correctly handles the case where one issue is closed and another opened
    (openIssueCount stays the same, but updatedAt changes).
    """
    repo_v1 = {"name": "test-repo", "owner": "testuser", "openIssueCount": 5, "updatedAt": "2024-01-01T00:00:00Z"}
    repo_v2 = {"name": "test-repo", "owner": "testuser", "openIssueCount": 5, "updatedAt": "2024-01-02T00:00:00Z"}
    issue_data = [
        {
            "title": "Issue 1",
            "url": "https://github.com/testuser/test-repo/issues/1",
            "number": 1,
            "updatedAt": "2024-01-01T00:00:00Z",
            "labels": [],
            "assignees": [],
            "repository": {"owner": "testuser", "name": "test-repo"},
        }
    ]

    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            mock_get_issues.return_value = issue_data

            # First call: fetch for v1
            mock_get_repos.return_value = [repo_v1]
            display_issues_from_repos_without_prs(None)
            assert mock_get_issues.call_count == 1

            # Second call: openIssueCount changed → must re-fetch
            mock_get_repos.return_value = [repo_v2]
            display_issues_from_repos_without_prs(None)
            assert mock_get_issues.call_count == 2, (
                "get_issues_from_repositories must be called again when updatedAt changes"
            )


def test_cache_invalidated_after_assignment():
    """
    After a successful auto-assignment, the cache for that repo must be invalidated
    so the next iteration re-fetches fresh issue data (including updated assignees),
    ensuring assigned_issue_count stays accurate for max_llm_working_parallel enforcement.
    """
    repo = {"name": "test-repo", "owner": "testuser", "openIssueCount": 2, "updatedAt": "2024-01-01T00:00:00Z"}
    good_first_issue = {
        "title": "Good first issue",
        "url": "https://github.com/testuser/test-repo/issues/1",
        "number": 1,
        "updatedAt": "2024-01-01T00:00:00Z",
        "labels": ["good first issue"],
        "assignees": [],
        "repository": {"owner": "testuser", "name": "test-repo"},
    }
    config = {
        "assign_to_copilot": {},
        "rulesets": [{"repositories": ["test-repo"], "assign_good_first_old": True}],
    }

    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                mock_get_repos.return_value = [repo]
                mock_get_issues.return_value = [good_first_issue]
                mock_assign.return_value = True

                # First call: fetch and assign
                display_issues_from_repos_without_prs(config)
                assert mock_get_issues.call_count == 1

                # Second call: even though openIssueCount and updatedAt are unchanged, cache should have
                # been invalidated by the assignment → must re-fetch
                display_issues_from_repos_without_prs(config)
                assert mock_get_issues.call_count == 2, (
                    "Cache must be invalidated after assignment so next iteration gets fresh assignees"
                )


if __name__ == "__main__":
    test_display_issues_when_no_repos_with_prs()
    print("✓ Test 1 passed: display_issues_when_no_repos_with_prs")

    test_display_issues_when_no_repos_with_issues()
    print("✓ Test 2 passed: display_issues_when_no_repos_with_issues")

    test_display_issues_handles_exceptions()
    print("✓ Test 3 passed: display_issues_handles_exceptions")

    test_display_issues_with_assign_disabled()
    print("✓ Test 4 passed: display_issues_with_assign_disabled")

    test_display_issues_with_custom_limit()
    print("✓ Test 5 passed: display_issues_with_custom_limit")

    test_display_issues_with_none_config()
    print("✓ Test 6 passed: display_issues_with_none_config")

    test_display_issues_with_assign_lowest_number()
    print("✓ Test 7 passed: display_issues_with_assign_lowest_number")

    print("\n✅ All tests passed!")
