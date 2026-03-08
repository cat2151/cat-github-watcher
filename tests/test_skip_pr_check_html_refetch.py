"""
Tests for the skip_pr_check HTML re-fetch behavior.

When updatedAt is unchanged (get_repos_changed_since_last_check returns empty set),
the main loop should:
- Skip GraphQL Phase 1/2 (get_repositories_with_open_prs, get_pr_details_batch)
- Still re-fetch HTML for each cached open PR to detect phase transitions
  (because updatedAt does not change when phase transitions 1A->1B, 1B->2A occur)

When updatedAt is unchanged but snapshot is None or empty (error during prior iteration):
- Should reset the updatedAt baseline so the next iteration performs a full check
"""


def _make_mock_pr(pr_url="https://github.com/testuser/repo1/pull/1"):
    return {
        "url": pr_url,
        "title": "Test PR",
        "repository": {"name": "repo1", "owner": "testuser"},
        "isDraft": True,
        "reviews": [],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [],
        "reviewThreads": [],
    }


def _setup_mocks(mocker, *, changed_repos, snapshot):
    """Set up common mocks for main loop tests."""
    mocker.patch("src.gh_pr_phase_monitor.main.load_config", return_value={"interval": "1m"})
    mocker.patch(
        "src.gh_pr_phase_monitor.main.get_repos_changed_since_last_check",
        return_value=changed_repos,
    )
    mocker.patch(
        "src.gh_pr_phase_monitor.main.get_last_pr_snapshot",
        return_value=snapshot,
    )
    mocker.patch("src.gh_pr_phase_monitor.main.set_last_pr_snapshot")
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.main.get_repositories_with_open_prs", return_value=[])
    mock_get_prs = mocker.patch("src.gh_pr_phase_monitor.main.get_pr_details_batch", return_value=[])
    mock_fetch_html = mocker.patch("src.gh_pr_phase_monitor.main.fetch_and_analyze_pr_html", return_value=None)
    mocker.patch("src.gh_pr_phase_monitor.main.determine_phase", return_value="LLM working")
    mocker.patch("src.gh_pr_phase_monitor.main.process_pr")
    mocker.patch("src.gh_pr_phase_monitor.main.display_status_summary")
    mocker.patch("src.gh_pr_phase_monitor.main.display_issues_from_repos_without_prs")
    mocker.patch("src.gh_pr_phase_monitor.main.wait_with_countdown", side_effect=KeyboardInterrupt("exit"))
    return mock_fetch_html, mock_get_repos, mock_get_prs


def test_html_refetched_for_cached_prs_when_updated_at_unchanged(mocker):
    """updatedAt不変 + キャッシュPRあり: GraphQLスキップ、HTMLは再取得される。"""
    pr = _make_mock_pr()
    snapshot = ([pr], [{"name": "repo1", "owner": "testuser", "openPRCount": 1}])

    mock_fetch_html, mock_get_repos, mock_get_prs = _setup_mocks(mocker, changed_repos=set(), snapshot=snapshot)

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # HTMLは再取得される（phase変化を検知するため）
    mock_fetch_html.assert_called_once_with(pr)
    # GraphQL Phase 1/2 は呼ばれない
    mock_get_repos.assert_not_called()
    mock_get_prs.assert_not_called()


def test_graphql_not_called_when_updated_at_unchanged(mocker):
    """updatedAt不変のとき、get_repositories_with_open_prs と get_pr_details_batch は呼ばれない。"""
    pr = _make_mock_pr()
    snapshot = ([pr], [{"name": "repo1", "owner": "testuser", "openPRCount": 1}])

    _, mock_get_repos, mock_get_prs = _setup_mocks(mocker, changed_repos=set(), snapshot=snapshot)

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    mock_get_repos.assert_not_called()
    mock_get_prs.assert_not_called()


def test_baseline_reset_when_snapshot_is_none(mocker):
    """updatedAt不変 + スナップショットなし: updatedAtベースラインをリセットして次イテレーションでフルチェックを強制する。"""
    _, _, _ = _setup_mocks(mocker, changed_repos=set(), snapshot=None)
    mock_reset = mocker.patch("src.gh_pr_phase_monitor.main.reset_repos_updated_at_baseline")

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # スナップショットなしの場合、ベースラインをリセットして次イテレーションでフルチェックを促す
    mock_reset.assert_called_once()


def test_baseline_reset_when_snapshot_prs_empty(mocker):
    """updatedAt不変 + キャッシュPRが空のスナップショット: ベースラインをリセットして次イテレーションでフルチェックを強制する。"""
    snapshot = ([], [])  # empty PRs

    _, _, _ = _setup_mocks(mocker, changed_repos=set(), snapshot=snapshot)
    mock_reset = mocker.patch("src.gh_pr_phase_monitor.main.reset_repos_updated_at_baseline")

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # PRが空のスナップショットの場合もベースラインをリセット
    mock_reset.assert_called_once()
