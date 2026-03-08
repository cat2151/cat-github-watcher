"""
Test to verify that issues are displayed when no repositories with open PRs are found

This test ensures the new behavior requested in the issue:
"Add the condition 'No repositories with open PRs found' to the conditions for displaying the latest issue."
"""


from src.gh_pr_phase_monitor.core.colors import colorize_url
from src.gh_pr_phase_monitor.ui.display import display_issues_from_repos_without_prs


def test_issue_url_is_colorized(mocker, capsys):
    """Issue URLs should be colorized for easier clicking"""
    url = "https://github.com/testuser/test-repo/issues/1"
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
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
        }
    ]

    display_issues_from_repos_without_prs(None)

    colored_url = colorize_url(url)
    output = capsys.readouterr().out
    assert colored_url in output


def test_display_issues_when_no_repos_with_prs(mocker):
    """
    Test that display_issues_from_repos_without_prs correctly displays issues
    when there are no repositories with open PRs
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_assign = mocker.patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 2,
        }
    ]

    # Mock good first issue response
    mock_get_issues.side_effect = [
        # First call: top 10 issues (used for detection/display)
        [
            {
                "title": "Issue 1",
                "url": "https://github.com/testuser/test-repo/issues/1",
                "number": 1,
                "updatedAt": "2024-01-01T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
            {
                "title": "Issue 2",
                "url": "https://github.com/testuser/test-repo/issues/2",
                "number": 2,
                "updatedAt": "2024-01-02T00:00:00Z",
                "author": {"login": "contributor2"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
        ],
        # Second call: good first issue for assignment
        [
            {
                "title": "Good first issue",
                "url": "https://github.com/testuser/test-repo/issues/1",
                "number": 1,
                "updatedAt": "2024-01-01T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
                "labels": ["good first issue"],
            }
        ],
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

    # Verify that issues were fetched twice (good first issue + top 10)
    assert mock_get_issues.call_count == 2

    # Verify first call was for top issues (used for detection/display)
    first_call = mock_get_issues.call_args_list[0]
    assert first_call[1]["limit"] == 10

    # Verify second call was for good first issue assignment (with sort_by_number=True)
    second_call = mock_get_issues.call_args_list[1]
    assert second_call[1]["limit"] == 1
    assert second_call[1]["labels"] == ["good first issue"]
    assert second_call[1]["sort_by_number"] is True

    # Verify assignment was attempted
    mock_assign.assert_called_once()


def test_display_issues_when_no_repos_with_issues(mocker):
    """
    Test that display_issues_from_repos_without_prs handles the case
    when there are no repositories with issues
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    # Mock response: no repos with issues
    mock_get_repos.return_value = []

    # Call the function with empty config - should not raise an error
    display_issues_from_repos_without_prs({})

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()


def test_display_issues_handles_exceptions(mocker):
    """
    Test that display_issues_from_repos_without_prs handles exceptions gracefully
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    # Mock an exception
    mock_get_repos.side_effect = Exception("API Error")

    # Call the function with empty config - should not raise an error
    display_issues_from_repos_without_prs({})

    # Verify that the function attempted to fetch repos
    mock_get_repos.assert_called_once()


def test_display_issues_with_assign_disabled(mocker):
    """
    Test that display_issues_from_repos_without_prs does NOT attempt assignment
    when the feature is disabled
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_assign = mocker.patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot")
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


def test_display_issues_with_custom_limit(mocker):
    """
    Test that display_issues_from_repos_without_prs respects the issue_display_limit config
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 10,
        }
    ]

    # Mock issue response - only display issues call
    mock_get_issues.side_effect = [
        # Only call: top N issues with custom limit
        [
            {
                "title": f"Issue {i}",
                "url": f"https://github.com/testuser/test-repo/issues/{i}",
                "number": i,
                "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            }
            for i in range(1, 6)
        ],
    ]

    # Create config with custom issue_display_limit, no assign flags
    config = {"assign_to_copilot": {}, "issue_display_limit": 5}

    # Call the function with config
    display_issues_from_repos_without_prs(config)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched once (top N only, no auto-assign)
    assert mock_get_issues.call_count == 1
    # Check the call used the custom limit
    call = mock_get_issues.call_args_list[0]
    assert call[1]["limit"] == 5


def test_display_issues_with_none_config(mocker):
    """
    Test that display_issues_from_repos_without_prs handles None config gracefully
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 10,
        }
    ]

    # Mock issue response - only display issues
    mock_get_issues.side_effect = [
        # Only call: top 10 issues
        [
            {
                "title": f"Issue {i}",
                "url": f"https://github.com/testuser/test-repo/issues/{i}",
                "number": i,
                "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            }
            for i in range(1, 11)
        ],
    ]

    # Call the function with None config - should use default limit of 10
    display_issues_from_repos_without_prs(None)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched once (top 10 only, no assign)
    assert mock_get_issues.call_count == 1
    # Check the call used the default limit of 10
    call = mock_get_issues.call_args_list[0]
    assert call[1]["limit"] == 10


def test_display_issues_with_assign_lowest_number(mocker):
    """
    Test that display_issues_from_repos_without_prs correctly assigns the oldest issue
    when assign_old is enabled (replaces assign_lowest_number_issue)
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_assign = mocker.patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 3,
        }
    ]

    # Mock lowest number issue response
    mock_get_issues.side_effect = [
        # First call: top 10 issues for display/detection
        [
            {
                "title": "Issue 1",
                "url": "https://github.com/testuser/test-repo/issues/5",
                "number": 5,
                "updatedAt": "2024-01-05T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
            {
                "title": "Issue 2",
                "url": "https://github.com/testuser/test-repo/issues/10",
                "number": 10,
                "updatedAt": "2024-01-10T00:00:00Z",
                "author": {"login": "contributor2"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
        ],
        # Second call: oldest issue
        [
            {
                "title": "Issue with lowest number",
                "url": "https://github.com/testuser/test-repo/issues/5",
                "number": 5,
                "updatedAt": "2024-01-05T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
                "labels": ["bug"],
            }
        ],
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

    # Verify that issues were fetched twice (oldest issue + top 10)
    assert mock_get_issues.call_count == 2

    # Verify first call was for top issues (display/detection)
    first_call = mock_get_issues.call_args_list[0]
    assert first_call[1]["limit"] == 10

    # Verify second call was for oldest issue (with sort_by_number=True, no labels)
    second_call = mock_get_issues.call_args_list[1]
    assert second_call[1]["limit"] == 1
    assert second_call[1]["sort_by_number"] is True
    # Should not have labels filter for oldest issue mode
    assert "labels" not in second_call[1] or second_call[1]["labels"] is None

    # Verify assignment was attempted
    mock_assign.assert_called_once()


def test_display_cached_top_issues_empty(mocker, capsys):
    """display_cached_top_issues outputs nothing when cache is empty"""
    import src.gh_pr_phase_monitor.ui.display as display_module

    mocker.patch.object(display_module, "_cached_top_issues", [])
    from src.gh_pr_phase_monitor.ui.display import display_cached_top_issues
    display_cached_top_issues()
    out = capsys.readouterr().out
    assert out == ""


def test_display_cached_top_issues_shows_cached_data(mocker, capsys):
    """display_cached_top_issues displays the cached issues without calling get_issues_from_repositories"""
    import src.gh_pr_phase_monitor.ui.display as display_module

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
    from src.gh_pr_phase_monitor.ui.display import display_cached_top_issues
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
    import src.gh_pr_phase_monitor.ui.display as display_module

    mocker.patch.object(display_module, "_cached_top_issues", [])
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]
    fetched_issues = [
        {"title": "Issue A", "url": "https://github.com/testuser/test-repo/issues/1", "number": 1},
    ]
    mock_get_issues.return_value = fetched_issues
    display_issues_from_repos_without_prs(None)
    assert list(display_module._cached_top_issues) == fetched_issues


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
