"""
Tests for issue assignment priority and filtering in display_issues_from_repos_without_prs
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.ui.display import display_issues_from_repos_without_prs


def test_assign_only_fetches_from_enabled_repos():
    """
    Test that assignment only fetches issues from repos where
    assign_good_first_old or assign_old is enabled.
    This prevents fetching issues from repos that don't have assignment enabled.
    """
    with patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: two repos without PRs but with issues
                mock_get_repos.return_value = [
                    {"name": "repo-with-assign", "owner": "testuser", "openIssueCount": 2},
                    {"name": "repo-without-assign", "owner": "testuser", "openIssueCount": 3},
                ]

                # Mock issue response
                mock_get_issues.side_effect = [
                    [],  # First call: top issues for display/detection
                    # Second call: good first issue (should only fetch from repo-with-assign)
                    [
                        {
                            "title": "Good first issue from enabled repo",
                            "url": "https://github.com/testuser/repo-with-assign/issues/1",
                            "number": 1,
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "author": {"login": "contributor1"},
                            "repository": {"owner": "testuser", "name": "repo-with-assign"},
                            "labels": ["good first issue"],
                        }
                    ],
                ]

                mock_assign.return_value = True

                # Create config where only repo-with-assign has the assignment flag enabled
                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["repo-with-assign"],
                            "assign_good_first_old": True,
                        },
                        {
                            "repositories": ["repo-without-assign"],
                            # No assignment flags enabled
                        },
                    ],
                }

                # Call the function
                display_issues_from_repos_without_prs(config)

                # Verify that get_issues_from_repositories was called
                assert mock_get_issues.call_count == 2

                # Verify assignment fetch only included repo-with-assign
                second_call = mock_get_issues.call_args_list[1]
                repos_arg = second_call[0][0]  # First positional argument
                assert len(repos_arg) == 1
                assert repos_arg[0]["name"] == "repo-with-assign"

                # Verify assignment was attempted
                mock_assign.assert_called_once()


def test_priority_prefers_ci_failure_then_deploy_then_good_first():
    """
    Verify assignment priority: ci-failure > deploy-pages-failure > good first issue
    """
    with patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot") as mock_assign:
                mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]

                mock_get_issues.side_effect = [
                    [],  # First call: top issues for display/detection
                    [
                        {
                            "title": "CI failure",
                            "url": "https://github.com/testuser/test-repo/issues/10",
                            "number": 10,
                            "updatedAt": "2024-01-10T00:00:00Z",
                            "author": {"login": "bot"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                            "labels": ["ci-failure"],
                        }
                    ],
                ]

                mock_assign.return_value = True

                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_ci_failure_old": True,
                            "assign_deploy_pages_failure_old": True,
                            "assign_good_first_old": True,
                        }
                    ],
                }

                display_issues_from_repos_without_prs(config)

                assert mock_get_issues.call_count == 2
                second_call = mock_get_issues.call_args_list[1]
                assert second_call[1]["labels"] == ["ci-failure"]
                assert second_call[1]["sort_by_number"] is True
                mock_assign.assert_called_once()


def test_fallback_to_deploy_pages_failure_when_no_ci_failure():
    """
    When ci-failure issues are unavailable, fall back to deploy-pages-failure before good first issues.
    """
    with patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot") as mock_assign:
                mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]

                mock_get_issues.side_effect = [
                    [],  # First call: top issues for display/detection
                    [],  # No ci-failure issues
                    [
                        {
                            "title": "Pages deploy failure",
                            "url": "https://github.com/testuser/test-repo/issues/20",
                            "number": 20,
                            "updatedAt": "2024-02-01T00:00:00Z",
                            "author": {"login": "bot"},
                            "repository": {"owner": "testuser", "name": "test-repo"},
                            "labels": ["deploy-pages-failure"],
                        }
                    ],
                ]

                mock_assign.return_value = True

                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["test-repo"],
                            "assign_ci_failure_old": True,
                            "assign_deploy_pages_failure_old": True,
                            "assign_good_first_old": True,
                        }
                    ],
                }

                display_issues_from_repos_without_prs(config)

                assert mock_get_issues.call_count == 3
                second_call = mock_get_issues.call_args_list[1]
                assert second_call[1]["labels"] == ["ci-failure"]
                third_call = mock_get_issues.call_args_list[2]
                assert third_call[1]["labels"] == ["deploy-pages-failure"]
                assert third_call[1]["sort_by_number"] is True
                mock_assign.assert_called_once()
