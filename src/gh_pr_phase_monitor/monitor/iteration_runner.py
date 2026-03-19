"""One monitoring loop iteration for GitHub PR Phase Monitor."""

from ..core.config import DEFAULT_MAX_LLM_WORKING_PARALLEL, validate_phase3_merge_config_required
from ..github.github_auth import get_current_user
from ..github.github_client import (
    get_pr_details_batch,
    get_repos_changed_since_last_check,
    get_repositories_with_open_prs,
    reset_repos_updated_at_baseline,
)
from ..monitor.error_logger import log_error_to_file
from ..monitor.local_repo_watcher import (
    display_pending_local_repo_results,
    notify_phase3_detected,
    notify_repos_updated_after_phase3,
    start_local_repo_monitoring,
)
from ..monitor.pages_watcher import check_pages_deployments_for_repos, get_pages_repos_from_config
from ..monitor.pr_processor import _process_open_prs
from ..monitor.state_tracker import get_last_pr_snapshot, set_last_pr_snapshot
from ..phase.phase_detector import PHASE_3, is_llm_working
from ..ui.display import display_cached_top_issues, display_issues_from_repos_without_prs


def run_one_iteration(config: dict, iteration: int) -> tuple[list, list, bool]:
    """Execute one monitoring loop iteration.

    Runs:
    1. updatedAt pre-check (Phase 1/2 skip optimisation)
    2. Phase 1: fetch repos with open PRs (if not skipped)
    3. Phase 2: fetch PR details (if not skipped)
    4. PR processing (HTML fetch + phase detection + actions)
    5. GitHub Pages deployment check
    6. Local repository monitoring

    Returns:
        (all_prs, repos_with_prs, skip_pr_check)

    Raises:
        Any exception raised by the underlying calls (to be caught by the caller).
    """
    all_prs: list = []
    repos_with_prs: list = []
    phase3_repo_names: list[str] = []
    skip_pr_check = False
    current_user = None
    changed_repos: set | None = None

    # updatedAt pre-check: determine which repos (if any) changed since last iteration.
    try:
        changed_repos = get_repos_changed_since_last_check()
        if changed_repos is None:
            print("  updatedAt ベースライン記録済み (初回チェック)")
        elif not changed_repos:
            print("  リポジトリに変化なし (updatedAt 不変)。Phase 1/2 をスキップします。")
            skip_pr_check = True
        else:
            print(f"  {len(changed_repos)} リポジトリで変化を検知 → Phase 1/2 実行")
    except Exception as updated_at_error:
        log_error_to_file("updatedAt check failed, running full check", updated_at_error)

    if not skip_pr_check:
        # Phase 1: Get all repositories with open PRs (lightweight query)
        print("\nPhase 1: Fetching repositories with open PRs...")
        repos_with_prs = get_repositories_with_open_prs()

        if not repos_with_prs:
            print("  No repositories with open PRs found")
            display_issues_from_repos_without_prs(config, llm_working_count=0)
        else:
            print(f"  Found {len(repos_with_prs)} repositories with open PRs:")
            for repo in repos_with_prs:
                print(f"    - {repo['name']}: {repo['openPRCount']} open PR(s)")

        # Validate phase3_merge configuration for all repositories
        # This must be done before processing PRs to fail fast
        print("\nValidating phase3_merge configuration...")
        for repo in repos_with_prs:
            repo_owner = repo.get("owner", "")
            repo_name = repo.get("name", "")
            if repo_owner and repo_name:
                validate_phase3_merge_config_required(config, repo_owner, repo_name)

        # Phase 2: Get PR details for repositories with open PRs (detailed query)
        print(f"\nPhase 2: Fetching PR details for {len(repos_with_prs)} repositories...")
        all_prs = get_pr_details_batch(repos_with_prs)

        if not all_prs:
            print("  No PRs found")
        else:
            print(f"\n  Found {len(all_prs)} open PR(s) total")
            print(f"\n{'=' * 50}")
            print("Processing PRs:")
            print(f"{'=' * 50}")
            _process_open_prs(all_prs, phase3_repo_names, config)

        # Save PR snapshot for display on subsequent skip-check iterations.
        # Done after Phase 1/2 (including the empty case) so the cache is always
        # up-to-date and never shows stale PRs when there are actually none.
        set_last_pr_snapshot(all_prs, repos_with_prs)

        if all_prs:
            _maybe_display_available_work(all_prs, config)

    else:
        # updatedAt 不変: GraphQL Phase 1/2 はスキップ
        # しかし、open PR のphase変化（1A→1B, 1B→2A等）を検知するため、HTMLを毎回再取得する
        # (updatedAt はPRのphase変化では更新されないため、HTMLフェッチが必須)
        snapshot = get_last_pr_snapshot()
        if snapshot is not None and snapshot[0]:
            cached_prs, cached_repos = snapshot
            all_prs, repos_with_prs, skip_pr_check = _run_skip_check_path(
                cached_prs, cached_repos, phase3_repo_names, config
            )
        else:
            # スナップショット未作成またはPRなし: 次イテレーションでフルチェックを強制する
            # (updatedAt ベースラインをリセットすることで、次回の get_repos_changed_since_last_check が
            #  None を返し、通常の Phase 1/2 チェックが実行される)
            log_error_to_file(
                "skip_pr_check=True but no cached PR snapshot; resetting updatedAt baseline for full check next iteration",
                None,
            )
            reset_repos_updated_at_baseline()

        # Top 10 issues の表示はキャッシュを利用するため、issue-fetch 用の GraphQL クエリは不要
        # PRのあるリポジトリのissueはキャッシュから除外し、次回の非スキップイテレーションで再取得する
        display_cached_top_issues(repos_with_prs)

    # Check GitHub Pages deployment status for configured repos
    # This runs regardless of whether there are open PRs (covers post-merge case)
    try:
        current_user = get_current_user()
        pages_repos = get_pages_repos_from_config(config, current_user)
        if pages_repos:
            print(f"\n{'=' * 50}")
            print("GitHub Pages deployment check:")
            print(f"{'=' * 50}")
            check_pages_deployments_for_repos(pages_repos, config)
    except Exception as pages_error:
        log_error_to_file("Failed to check Pages deployment", pages_error)
        current_user = None

    # Local repository pullable check (background-based)
    # 初回イテレーション: 全リポジトリをバックグラウンドで検査開始
    # phase3検知リポジトリ: バックグラウンドでpullable検査をトリガー
    # 蓄積された検査結果を表示（1秒ごとの逐次表示は廃止、次のintervalで一括表示）
    try:
        if current_user is None:
            current_user = get_current_user()
        if iteration == 1:
            start_local_repo_monitoring(config, current_user)
        else:
            for repo_name in phase3_repo_names:
                notify_phase3_detected(repo_name, config, current_user)
            # phase3A済みリポジトリのupdatedAt変化を検知 → PRが0件でもauto pull
            if changed_repos:
                notify_repos_updated_after_phase3(changed_repos, config, current_user)
        display_pending_local_repo_results()
    except Exception as local_repo_error:
        log_error_to_file("Failed to check local repos", local_repo_error)

    return all_prs, repos_with_prs, skip_pr_check


def _maybe_display_available_work(all_prs: list, config: dict) -> None:
    """Display available work (issues) when conditions allow more parallel PRs.

    This is called after Phase 2 when there are open PRs. It checks whether
    the current PR state allows assigning new work and displays available issues.
    """
    llm_working_count = sum(1 for pr in all_prs if is_llm_working(pr))
    max_llm_working_parallel = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)
    llm_working_below_cap = llm_working_count < max_llm_working_parallel

    total_pr_count = len(all_prs)
    all_llm_working = bool(all_prs) and all(is_llm_working(pr) for pr in all_prs)
    all_phase3 = bool(all_prs) and all(pr.get("phase") == PHASE_3 for pr in all_prs)
    active_parallel_prs = sum(1 for pr in all_prs if pr.get("phase") != PHASE_3)

    if llm_working_below_cap or all_llm_working or active_parallel_prs < 3:
        if all_llm_working and total_pr_count >= 3:
            print(f"\n{'=' * 50}")
            print("All PRs are in 'LLM working' phase")
            print(f"{'=' * 50}")
        elif all_phase3 and total_pr_count >= 3:
            print(f"\n{'=' * 50}")
            print("All PRs are in 'phase3' (ready for human review); treating parallel count as 0")
            print(f"{'=' * 50}")
        elif llm_working_below_cap:
            print(f"\n{'=' * 50}")
            print(
                f"LLM working PRs below limit: {llm_working_count}/{max_llm_working_parallel} "
                "(showing available work)"
            )
            print(f"{'=' * 50}")
        elif active_parallel_prs < 3:
            print(f"\n{'=' * 50}")
            print(f"Active PR count (excluding phase3) is {active_parallel_prs} (less than 3)")
            print(f"{'=' * 50}")
        display_issues_from_repos_without_prs(config, llm_working_count=llm_working_count)


def _run_skip_check_path(
    cached_prs: list,
    cached_repos: list,
    phase3_repo_names: list,
    config: dict,
) -> tuple[list, list, bool]:
    """Handle the skip_pr_check path: re-check PR counts and re-fetch HTML if needed.

    Returns:
        (all_prs, repos_with_prs, skip_pr_check)
        skip_pr_check is always False (reset so display uses live HTML-fetched data).
    """
    # open PR 件数を毎回 GraphQL で再取得し、変化があれば Phase 1/2 を強制実行する
    # (updatedAt は PR の新規作成を反映しないことがあるため、件数の乖離が生じうる)
    # リポジトリごとの件数を辞書で比較することで、「1件クローズ+1件新規」のように
    # 合計が変わらない場合でも変化を検知できる。
    print("\n  open PR 件数を再確認中 (GraphQL)...")
    fresh_repos_with_prs = get_repositories_with_open_prs()
    cached_count_map = {
        (r.get("owner", ""), r.get("name", "")): r.get("openPRCount", 0) for r in cached_repos
    }
    fresh_count_map = {
        (r.get("owner", ""), r.get("name", "")): r.get("openPRCount", 0)
        for r in fresh_repos_with_prs
    }

    if fresh_count_map != cached_count_map:
        # リポジトリごとの PR 件数が変化 → Phase 1/2 を強制実行して最新の PR 一覧を取得する
        print("  open PR 件数/構成が変化。Phase 1/2 を強制実行します。")
        repos_with_prs = fresh_repos_with_prs

        # validate phase3_merge configuration (same as normal Phase 1 flow)
        print("\nValidating phase3_merge configuration...")
        for repo in repos_with_prs:
            repo_owner = repo.get("owner", "")
            repo_name = repo.get("name", "")
            if repo_owner and repo_name:
                validate_phase3_merge_config_required(config, repo_owner, repo_name)

        all_prs = get_pr_details_batch(repos_with_prs)
        if all_prs:
            print(f"\n  Found {len(all_prs)} open PR(s) total")
            _process_open_prs(all_prs, phase3_repo_names, config)
        set_last_pr_snapshot(all_prs, repos_with_prs)
    else:
        # PR 件数は変化なし → HTML のみ再取得 (phase 変化を検知するため)
        print(
            "\n  open PR のHTML再取得 (updatedAt 不変でもphase変化を検知するため"
            " / Refetching HTML for open PRs to detect phase changes)..."
        )
        all_prs = cached_prs
        repos_with_prs = cached_repos
        _process_open_prs(all_prs, phase3_repo_names, config)
        set_last_pr_snapshot(all_prs, repos_with_prs)

    # skip_pr_check を False にリセット: 今イテレーションの表示セクション (display_status_summary)
    # でスナップショットではなく最新のHTML取得結果を使うため
    return all_prs, repos_with_prs, False
