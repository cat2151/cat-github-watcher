"""
Tests for issue assignment priority and filtering in display_issues_from_repos_without_prs
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.display import display_issues_from_repos_without_prs


def test_assign_only_fetches_from_enabled_repos():
    """
    Test that assignment only considers issues from repos where
    assign_good_first_old or assign_old is enabled.
    Issues from repos without assignment enabled must not be assigned.
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                # Mock response: two repos without PRs but with issues
                mock_get_repos.return_value = [
                    {"name": "repo-with-assign", "owner": "testuser", "openIssueCount": 2},
                    {"name": "repo-without-assign", "owner": "testuser", "openIssueCount": 3},
                ]

                # Single call returns issues from both repos
                mock_get_issues.return_value = [
                    {
                        "title": "Issue from non-assign repo",
                        "url": "https://github.com/testuser/repo-without-assign/issues/1",
                        "number": 1,
                        "updatedAt": "2024-01-01T00:00:00Z",
                        "labels": ["good first issue"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "repo-without-assign"},
                    },
                    {
                        "title": "Good first issue from enabled repo",
                        "url": "https://github.com/testuser/repo-with-assign/issues/2",
                        "number": 2,
                        "updatedAt": "2024-01-02T00:00:00Z",
                        "labels": ["good first issue"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "repo-with-assign"},
                    },
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

                # Issues are fetched in a single call
                assert mock_get_issues.call_count == 1

                # Verify assignment was attempted only for the enabled repo's issue
                mock_assign.assert_called_once()
                assigned_issue = mock_assign.call_args[0][0]
                assert assigned_issue["repository"]["name"] == "repo-with-assign"


def test_priority_prefers_ci_failure_then_deploy_then_good_first():
    """
    Verify assignment priority: ci-failure > deploy-pages-failure > good first issue
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]

                # Single call returns all issues; ci-failure takes priority over others
                mock_get_issues.return_value = [
                    {
                        "title": "CI failure",
                        "url": "https://github.com/testuser/test-repo/issues/10",
                        "number": 10,
                        "updatedAt": "2024-01-10T00:00:00Z",
                        "labels": ["ci-failure"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    },
                    {
                        "title": "Good first issue",
                        "url": "https://github.com/testuser/test-repo/issues/5",
                        "number": 5,
                        "updatedAt": "2024-01-05T00:00:00Z",
                        "labels": ["good first issue"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    },
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

                # Issues fetched in a single call; priority handled client-side
                assert mock_get_issues.call_count == 1
                # The ci-failure issue should be assigned (priority)
                mock_assign.assert_called_once()
                assigned_issue = mock_assign.call_args[0][0]
                assert "ci-failure" in assigned_issue.get("labels", [])


def test_fallback_to_deploy_pages_failure_when_no_ci_failure():
    """
    When ci-failure issues are unavailable, fall back to deploy-pages-failure before good first issues.
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]

                # No ci-failure issues, but a deploy-pages-failure issue exists
                mock_get_issues.return_value = [
                    {
                        "title": "Pages deploy failure",
                        "url": "https://github.com/testuser/test-repo/issues/20",
                        "number": 20,
                        "updatedAt": "2024-02-01T00:00:00Z",
                        "labels": ["deploy-pages-failure"],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "test-repo"},
                    }
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

                # Issues fetched in a single call; ci-failure filter finds nothing,
                # deploy-pages-failure filter finds the issue → assigned
                assert mock_get_issues.call_count == 1
                mock_assign.assert_called_once()
                assigned_issue = mock_assign.call_args[0][0]
                assert "deploy-pages-failure" in assigned_issue.get("labels", [])


def test_no_assignment_without_matching_label():
    """
    Regression test for PR #311: ensures no issue is assigned when none match the required label filter.
    """
    with patch("src.gh_pr_phase_monitor.github_client.get_repositories_with_no_prs_and_open_issues") as mock_get_repos:
        with patch("src.gh_pr_phase_monitor.display.get_issues_from_repositories") as mock_get_issues:
            with patch("src.gh_pr_phase_monitor.display.assign_issue_to_copilot") as mock_assign:
                mock_get_repos.return_value = [{"name": "old-repo", "owner": "testuser", "openIssueCount": 1}]

                # Issue exists but has NO "good first issue" label
                mock_get_issues.return_value = [
                    {
                        "title": "Old issue without any special label",
                        "url": "https://github.com/testuser/old-repo/issues/1",
                        "number": 1,
                        "updatedAt": "2020-01-01T00:00:00Z",
                        "labels": [],
                        "assignees": [],
                        "repository": {"owner": "testuser", "name": "old-repo"},
                    }
                ]

                config = {
                    "assign_to_copilot": {},
                    "rulesets": [
                        {
                            "repositories": ["old-repo"],
                            "assign_good_first_old": True,
                        }
                    ],
                }

                display_issues_from_repos_without_prs(config)

                # No issue should be assigned because none have the "good first issue" label
                mock_assign.assert_not_called()
