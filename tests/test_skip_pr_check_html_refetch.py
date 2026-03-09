"""
Tests for the skip_pr_check HTML re-fetch behavior.

When updatedAt is unchanged (get_repos_changed_since_last_check returns empty set),
the main loop should:
- Still call get_repositories_with_open_prs to check the fresh open PR count
- If open PR count is unchanged: skip get_pr_details_batch (GraphQL Phase 2),
  but still re-fetch HTML for each cached open PR to detect phase transitions
  (because updatedAt does not change when phase transitions 1A->1B, 1B->2A occur)
- If open PR count changed: run full Phase 1/2 (get_pr_details_batch is called)

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


def _setup_mocks(mocker, *, changed_repos, snapshot, fresh_repos_with_prs=None):
    """Set up common mocks for main loop tests.

    Args:
        fresh_repos_with_prs: What get_repositories_with_open_prs returns for the fresh count check.
            Defaults to the same repos as in snapshot (same counts → no Phase 1/2 forced).
    """
    mocker.patch("src.gh_pr_phase_monitor.main.load_config", return_value={"interval": "1m"})
    mocker.patch(
        "src.gh_pr_phase_monitor.monitor.iteration_runner.get_repos_changed_since_last_check",
        return_value=changed_repos,
    )
    mocker.patch(
        "src.gh_pr_phase_monitor.monitor.iteration_runner.get_last_pr_snapshot",
        return_value=snapshot,
    )
    mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.set_last_pr_snapshot")

    # By default, fresh count matches cached repos (no count change → no forced Phase 1/2)
    if fresh_repos_with_prs is None:
        fresh_repos_with_prs = snapshot[1] if snapshot is not None else []
    mock_get_repos = mocker.patch(
        "src.gh_pr_phase_monitor.monitor.iteration_runner.get_repositories_with_open_prs",
        return_value=fresh_repos_with_prs,
    )
    mock_get_prs = mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.get_pr_details_batch", return_value=[])
    mock_fetch_html = mocker.patch("src.gh_pr_phase_monitor.monitor.pr_processor.fetch_and_analyze_pr_html", return_value=None)
    mocker.patch("src.gh_pr_phase_monitor.monitor.pr_processor.determine_phase", return_value="LLM working")
    mocker.patch("src.gh_pr_phase_monitor.monitor.pr_processor.process_pr")
    mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.get_current_user", return_value="testuser")
    mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.get_pages_repos_from_config", return_value=[])
    mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.start_local_repo_monitoring")
    mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.display_pending_local_repo_results")
    mocker.patch("src.gh_pr_phase_monitor.main.display_status_summary")
    mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.display_issues_from_repos_without_prs")
    mocker.patch("src.gh_pr_phase_monitor.main.wait_with_countdown", side_effect=KeyboardInterrupt("exit"))
    return mock_fetch_html, mock_get_repos, mock_get_prs


def test_html_refetched_for_cached_prs_when_updated_at_unchanged(mocker):
    """updatedAt不変 + キャッシュPRあり + 件数変化なし: 件数チェック (Phase 1) を呼び、HTMLは再取得される。Phase 2 は呼ばれない。"""
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
    # 件数チェック用の GraphQL は呼ばれる
    mock_get_repos.assert_called_once()
    # 件数が変わっていないので get_pr_details_batch は呼ばれない
    mock_get_prs.assert_not_called()


def test_pr_count_unchanged_skips_phase2(mocker):
    """updatedAt不変 + キャッシュPRあり + 件数変化なし: Phase 1 (件数チェック) は呼ばれるが、Phase 2 (PR詳細取得) は呼ばれない。"""
    pr = _make_mock_pr()
    snapshot = ([pr], [{"name": "repo1", "owner": "testuser", "openPRCount": 1}])

    _, mock_get_repos, mock_get_prs = _setup_mocks(mocker, changed_repos=set(), snapshot=snapshot)

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # 件数チェック用の GraphQL は呼ばれる
    mock_get_repos.assert_called_once()
    # 件数が変わっていないので get_pr_details_batch は呼ばれない
    mock_get_prs.assert_not_called()


def test_pr_count_changed_triggers_phase12(mocker):
    """updatedAt不変でも open PR 件数/構成が変わっていたら Phase 1/2 を強制実行し、バリデーションも行う。"""
    pr = _make_mock_pr()
    # キャッシュは 1 件
    snapshot = ([pr], [{"name": "repo1", "owner": "testuser", "openPRCount": 1}])
    # GraphQL で取得した新鮮なリストは 2 件
    fresh_repos = [{"name": "repo1", "owner": "testuser", "openPRCount": 2}]

    _, mock_get_repos, mock_get_prs = _setup_mocks(
        mocker, changed_repos=set(), snapshot=snapshot, fresh_repos_with_prs=fresh_repos
    )
    mock_validate = mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.validate_phase3_merge_config_required")

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # 件数チェック用の GraphQL は呼ばれる
    mock_get_repos.assert_called_once()
    # 件数が変わったので get_pr_details_batch も呼ばれる
    mock_get_prs.assert_called_once()
    # validate_phase3_merge_config_required が呼ばれることを確認
    mock_validate.assert_called_once_with(mocker.ANY, "testuser", "repo1")


def test_count_map_change_triggers_phase12_same_total(mocker):
    """1件クローズ+1件新規のように合計件数が同じでもリポジトリ構成が変わった場合は Phase 1/2 を強制実行する。"""
    pr = _make_mock_pr()
    # キャッシュ: repo1=1件, repo2=1件 (合計2件)
    snapshot = (
        [pr],
        [
            {"name": "repo1", "owner": "testuser", "openPRCount": 1},
            {"name": "repo2", "owner": "testuser", "openPRCount": 1},
        ],
    )
    # 新鮮: repo1=2件, repo2=0件 (合計は同じ2件だが構成が変化)
    fresh_repos = [{"name": "repo1", "owner": "testuser", "openPRCount": 2}]

    _, mock_get_repos, mock_get_prs = _setup_mocks(
        mocker, changed_repos=set(), snapshot=snapshot, fresh_repos_with_prs=fresh_repos
    )

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # 件数チェック用の GraphQL は呼ばれる
    mock_get_repos.assert_called_once()
    # 合計は同じでもリポジトリ構成が変わったので get_pr_details_batch が呼ばれる
    mock_get_prs.assert_called_once()


def test_baseline_reset_when_snapshot_is_none(mocker):
    """updatedAt不変 + スナップショットなし: updatedAtベースラインをリセットして次イテレーションでフルチェックを強制する。"""
    _, _, _ = _setup_mocks(mocker, changed_repos=set(), snapshot=None)
    mock_reset = mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.reset_repos_updated_at_baseline")

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
    mock_reset = mocker.patch("src.gh_pr_phase_monitor.monitor.iteration_runner.reset_repos_updated_at_baseline")

    from src.gh_pr_phase_monitor.main import main

    try:
        main()
    except KeyboardInterrupt:
        pass

    # PRが空のスナップショットの場合もベースラインをリセット
    mock_reset.assert_called_once()
