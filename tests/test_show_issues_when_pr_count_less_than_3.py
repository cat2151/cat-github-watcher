"""
Test to verify that issues are always displayed when PR count is less than 3,
regardless of PR phase.

This test ensures the behavior requested in the issue:
"If list has only 2 items (less than 3), always show the list table"
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.phase_detector import PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING


def _create_mock_pr(repo_name: str, title: str, url: str, phase: str):
    """Helper function to create a mock PR with the required structure"""
    base_pr = {
        "repository": {"name": repo_name, "owner": "testuser"},
        "title": title,
        "url": url,
        "reviewThreads": [],
        "commentNodes": [],
    }

    if phase == PHASE_1:
        # Phase 1: Draft with review requests
        base_pr["isDraft"] = True
        base_pr["reviews"] = []
        base_pr["latestReviews"] = []
        base_pr["reviewRequests"] = [{"requestedReviewer": {"login": "someone"}}]
    elif phase == PHASE_2:
        # Phase 2: Copilot reviewer commented with unresolved threads
        base_pr["isDraft"] = False
        base_pr["reviews"] = [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}]
        base_pr["latestReviews"] = [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "COMMENTED"}]
        base_pr["reviewRequests"] = []
        base_pr["reviewThreads"] = [{"isResolved": False, "isOutdated": False}]  # Unresolved thread
    elif phase == PHASE_3:
        # Phase 3: Copilot reviewer approved or commented without unresolved threads
        base_pr["isDraft"] = False
        base_pr["reviews"] = [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}]
        base_pr["latestReviews"] = [{"author": {"login": "copilot-pull-request-reviewer"}, "state": "APPROVED"}]
        base_pr["reviewRequests"] = []
        base_pr["reviewThreads"] = []  # No unresolved threads
    else:  # PHASE_LLM_WORKING
        # LLM working: No reviews or no copilot-pull-request-reviewer reviews
        base_pr["isDraft"] = False
        base_pr["reviews"] = []
        base_pr["latestReviews"] = []
        base_pr["reviewRequests"] = []
        base_pr["reviewThreads"] = []

    return base_pr


@patch("src.gh_pr_phase_monitor.main.wait_with_countdown")
@patch("src.gh_pr_phase_monitor.main.display_status_summary")
@patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
@patch("src.gh_pr_phase_monitor.main.process_pr")
@patch("src.gh_pr_phase_monitor.main.get_pr_details_batch")
@patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs")
@patch("src.gh_pr_phase_monitor.main.load_config")
def test_display_issues_when_two_prs_in_phase3(
    mock_load_config,
    mock_get_repos,
    mock_get_prs,
    mock_process_pr,
    mock_display_issues,
    mock_display_summary,
    mock_wait,
):
    """
    Test that issues are displayed when there are only 2 PRs (less than 3),
    even when they are in phase 3 (not "LLM working")
    """
    # Mock configuration
    mock_load_config.return_value = {"interval": "1m"}

    # Mock repositories with open PRs
    mock_get_repos.return_value = [
        {"name": "repo1", "owner": "testuser", "openPRCount": 1},
        {"name": "repo2", "owner": "testuser", "openPRCount": 1},
    ]

    # Mock 2 PRs in phase 3 (approved, waiting for human review)
    mock_get_prs.return_value = [
        _create_mock_pr("repo1", "PR 1", "https://github.com/testuser/repo1/pull/1", PHASE_3),
        _create_mock_pr("repo2", "PR 2", "https://github.com/testuser/repo2/pull/1", PHASE_3),
    ]

    # Mock wait_with_countdown to exit after first iteration
    mock_wait.side_effect = KeyboardInterrupt("Exit test")

    # Import main and run
    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        # Expected - mock_wait raises KeyboardInterrupt to exit after first iteration
        pass

    # Verify display_issues_from_repos_without_prs was called
    # This is the key assertion - issues should be displayed even when PRs are in phase 3
    assert mock_display_issues.called, "Issues should be displayed when PR count is less than 3"

    # Verify it was called with the correct llm_working_count (0 in this case, as no PRs are in LLM working)
    call_args = mock_display_issues.call_args
    assert call_args is not None
    assert call_args[1]["llm_working_count"] == 0


@patch("src.gh_pr_phase_monitor.main.wait_with_countdown")
@patch("src.gh_pr_phase_monitor.main.display_status_summary")
@patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
@patch("src.gh_pr_phase_monitor.main.process_pr")
@patch("src.gh_pr_phase_monitor.main.get_pr_details_batch")
@patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs")
@patch("src.gh_pr_phase_monitor.main.load_config")
def test_display_issues_when_one_pr_in_any_phase(
    mock_load_config,
    mock_get_repos,
    mock_get_prs,
    mock_process_pr,
    mock_display_issues,
    mock_display_summary,
    mock_wait,
):
    """
    Test that issues are displayed when there is only 1 PR (less than 3),
    regardless of phase
    """
    # Mock configuration
    mock_load_config.return_value = {"interval": "1m"}

    # Mock repositories with open PRs
    mock_get_repos.return_value = [{"name": "repo1", "owner": "testuser", "openPRCount": 1}]

    # Mock 1 PR in phase 1
    mock_get_prs.return_value = [
        _create_mock_pr("repo1", "PR 1", "https://github.com/testuser/repo1/pull/1", PHASE_1),
    ]

    # Mock wait_with_countdown to exit after first iteration
    mock_wait.side_effect = KeyboardInterrupt("Exit test")

    # Import main and run
    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        # Expected - mock_wait raises KeyboardInterrupt to exit after first iteration
        pass

    # Verify display_issues_from_repos_without_prs was called
    assert mock_display_issues.called, "Issues should be displayed when PR count is less than 3"


@patch("src.gh_pr_phase_monitor.main.wait_with_countdown")
@patch("src.gh_pr_phase_monitor.main.display_status_summary")
@patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
@patch("src.gh_pr_phase_monitor.main.process_pr")
@patch("src.gh_pr_phase_monitor.main.get_pr_details_batch")
@patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs")
@patch("src.gh_pr_phase_monitor.main.load_config")
def test_no_display_issues_when_three_or_more_prs_not_llm_working(
    mock_load_config,
    mock_get_repos,
    mock_get_prs,
    mock_process_pr,
    mock_display_issues,
    mock_display_summary,
    mock_wait,
):
    """
    Test that issues are NOT displayed when there are 3 or more PRs
    and not all are in "LLM working" phase
    """
    # Mock configuration
    mock_load_config.return_value = {"interval": "1m"}

    # Mock repositories with open PRs
    mock_get_repos.return_value = [
        {"name": "repo1", "owner": "testuser", "openPRCount": 1},
        {"name": "repo2", "owner": "testuser", "openPRCount": 1},
        {"name": "repo3", "owner": "testuser", "openPRCount": 1},
    ]

    # Mock 3 PRs in different phases (not all "LLM working")
    mock_get_prs.return_value = [
        _create_mock_pr("repo1", "PR 1", "https://github.com/testuser/repo1/pull/1", PHASE_1),
        _create_mock_pr("repo2", "PR 2", "https://github.com/testuser/repo2/pull/1", PHASE_2),
        _create_mock_pr("repo3", "PR 3", "https://github.com/testuser/repo3/pull/1", PHASE_3),
    ]

    # Mock wait_with_countdown to exit after first iteration
    mock_wait.side_effect = KeyboardInterrupt("Exit test")

    # Import main and run
    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        # Expected - mock_wait raises KeyboardInterrupt to exit after first iteration
        pass

    # Active parallel count excludes phase3, so with 1 phase3 + 2 active, issues should be displayed
    assert mock_display_issues.called, "Issues should be displayed when active (non-phase3) PRs are under cap"
    call_args = mock_display_issues.call_args
    assert call_args is not None
    assert call_args[1]["llm_working_count"] == 0


@patch("src.gh_pr_phase_monitor.main.wait_with_countdown")
@patch("src.gh_pr_phase_monitor.main.display_status_summary")
@patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
@patch("src.gh_pr_phase_monitor.main.process_pr")
@patch("src.gh_pr_phase_monitor.main.get_pr_details_batch")
@patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs")
@patch("src.gh_pr_phase_monitor.main.load_config")
def test_display_issues_when_three_or_more_prs_all_llm_working(
    mock_load_config,
    mock_get_repos,
    mock_get_prs,
    mock_process_pr,
    mock_display_issues,
    mock_display_summary,
    mock_wait,
):
    """
    Test that issues ARE displayed when there are 3 or more PRs
    and ALL are in "LLM working" phase (existing behavior should still work)
    """
    # Mock configuration
    mock_load_config.return_value = {"interval": "1m"}

    # Mock repositories with open PRs
    mock_get_repos.return_value = [
        {"name": "repo1", "owner": "testuser", "openPRCount": 1},
        {"name": "repo2", "owner": "testuser", "openPRCount": 1},
        {"name": "repo3", "owner": "testuser", "openPRCount": 1},
    ]

    # Mock 3 PRs all in "LLM working" phase
    mock_get_prs.return_value = [
        _create_mock_pr("repo1", "PR 1", "https://github.com/testuser/repo1/pull/1", PHASE_LLM_WORKING),
        _create_mock_pr("repo2", "PR 2", "https://github.com/testuser/repo2/pull/1", PHASE_LLM_WORKING),
        _create_mock_pr("repo3", "PR 3", "https://github.com/testuser/repo3/pull/1", PHASE_LLM_WORKING),
    ]

    # Mock wait_with_countdown to exit after first iteration
    mock_wait.side_effect = KeyboardInterrupt("Exit test")

    # Import main and run
    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        # Expected - mock_wait raises KeyboardInterrupt to exit after first iteration
        pass

    # Verify display_issues_from_repos_without_prs was called
    # When all PRs are in "LLM working", issues should be displayed (existing behavior)
    assert mock_display_issues.called, "Issues should be displayed when all PRs are in LLM working"

    # Verify it was called with the correct llm_working_count (3 in this case)
    call_args = mock_display_issues.call_args
    assert call_args is not None
    assert call_args[1]["llm_working_count"] == 3


@patch("src.gh_pr_phase_monitor.main.wait_with_countdown")
@patch("src.gh_pr_phase_monitor.main.display_status_summary")
@patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
@patch("src.gh_pr_phase_monitor.main.process_pr")
@patch("src.gh_pr_phase_monitor.main.get_pr_details_batch")
@patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs")
@patch("src.gh_pr_phase_monitor.main.load_config")
def test_display_issues_when_three_or_more_prs_all_phase3(
    mock_load_config,
    mock_get_repos,
    mock_get_prs,
    mock_process_pr,
    mock_display_issues,
    mock_display_summary,
    mock_wait,
):
    """
    Test that issues ARE displayed when there are 3 or more PRs
    and ALL are in phase3 (phase3 should not count toward parallel limits)
    """
    # Mock configuration
    mock_load_config.return_value = {"interval": "1m"}

    # Mock repositories with open PRs
    mock_get_repos.return_value = [
        {"name": "repo1", "owner": "testuser", "openPRCount": 1},
        {"name": "repo2", "owner": "testuser", "openPRCount": 1},
        {"name": "repo3", "owner": "testuser", "openPRCount": 1},
    ]

    # Mock 3 PRs all in phase3
    mock_get_prs.return_value = [
        _create_mock_pr("repo1", "PR 1", "https://github.com/testuser/repo1/pull/1", PHASE_3),
        _create_mock_pr("repo2", "PR 2", "https://github.com/testuser/repo2/pull/1", PHASE_3),
        _create_mock_pr("repo3", "PR 3", "https://github.com/testuser/repo3/pull/1", PHASE_3),
    ]

    # Mock wait_with_countdown to exit after first iteration
    mock_wait.side_effect = KeyboardInterrupt("Exit test")

    # Import main and run
    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        # Expected - mock_wait raises KeyboardInterrupt to exit after first iteration
        pass

    # Verify display_issues_from_repos_without_prs was called
    assert mock_display_issues.called, "Issues should be displayed when all PRs are phase3"

    # Phase3 should not contribute to llm_working_count
    call_args = mock_display_issues.call_args
    assert call_args is not None
    assert call_args[1]["llm_working_count"] == 0


@patch("src.gh_pr_phase_monitor.main.wait_with_countdown")
@patch("src.gh_pr_phase_monitor.main.display_status_summary")
@patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
@patch("src.gh_pr_phase_monitor.main.process_pr")
@patch("src.gh_pr_phase_monitor.main.get_pr_details_batch")
@patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs")
@patch("src.gh_pr_phase_monitor.main.load_config")
def test_display_issues_when_phase3_and_llm_working_mix(
    mock_load_config,
    mock_get_repos,
    mock_get_prs,
    mock_process_pr,
    mock_display_issues,
    mock_display_summary,
    mock_wait,
):
    """Phase3 PRs should not count toward the parallel cap; mixed phases still allow display."""

    mock_load_config.return_value = {"interval": "1m"}

    mock_get_repos.return_value = [
        {"name": "repo1", "owner": "testuser", "openPRCount": 1},
        {"name": "repo2", "owner": "testuser", "openPRCount": 1},
        {"name": "repo3", "owner": "testuser", "openPRCount": 1},
    ]

    mock_get_prs.return_value = [
        _create_mock_pr("repo1", "PR 1", "https://github.com/testuser/repo1/pull/1", PHASE_3),
        _create_mock_pr("repo2", "PR 2", "https://github.com/testuser/repo2/pull/1", PHASE_3),
        _create_mock_pr("repo3", "PR 3", "https://github.com/testuser/repo3/pull/1", PHASE_LLM_WORKING),
    ]

    mock_wait.side_effect = KeyboardInterrupt("Exit test")

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    assert mock_display_issues.called, "Issues should be displayed when only non-phase3 count is below cap"
    call_args = mock_display_issues.call_args
    assert call_args is not None
    assert call_args[1]["llm_working_count"] == 1
