"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

from .actions.pr_actions import process_pr
from .core.config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_config_mtime,
    load_config,
    parse_interval,
    print_config,
    validate_phase3_merge_config_required,
)
from .core.time_utils import format_elapsed_time
from .github.github_auth import get_current_user
from .github.github_client import (
    get_pr_details_batch,
    get_repos_changed_since_last_check,
    get_repositories_with_open_prs,
    reset_repos_updated_at_baseline,
)
from .github.graphql_client import GitHubRateLimitError, get_rate_limit_info
from .github.rate_limit_handler import (
    _check_rate_limit_throttle,
    _display_rate_limit_usage,
    _format_rate_limit_reset,
)
from .monitor.auto_updater import (
    UPDATE_CHECK_INTERVAL_SECONDS,
    maybe_self_update,
    run_startup_self_update_foreground,
)
from .monitor.local_repo_watcher import (
    display_pending_local_repo_results,
    notify_phase3_detected,
    start_local_repo_monitoring,
)
from .monitor.monitor import check_no_state_change_timeout
from .monitor.pages_watcher import check_pages_deployments_for_repos, get_pages_repos_from_config
from .monitor.state_tracker import get_last_pr_snapshot, set_last_pr_snapshot
from .phase.html.html_status_processor import fetch_and_analyze_pr_html
from .phase.phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase, is_llm_working
from .ui.display import display_cached_top_issues, display_issues_from_repos_without_prs, display_status_summary
from .ui.wait_handler import wait_with_countdown

LOG_DIR = Path("logs")


def log_error_to_file(message: str, exc: Exception | None = None, base_dir: Path | str | None = None) -> None:
    """Append an error entry to logs/error.log without interrupting execution"""
    try:
        log_dir = Path(base_dir) if base_dir else LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception:
        # Avoid any logging-related failures impacting the main loop
        pass


def _process_open_prs(
    all_prs: list,
    phase3_repo_names: list,
    config: dict,
) -> None:
    """HTML取得・phase判定・PR処理を全openなPRに対して実行する。

    all_prs の各PRに対して fetch_and_analyze_pr_html → determine_phase → process_pr を実行し、
    結果を pr["phase"] に書き込み、phase3_repo_names に追記する。
    """
    for pr in all_prs:
        try:
            # HTMLを取得・解析・保存（メインフロー: phaseに関わらず全PRに対して実行）
            try:
                fetch_and_analyze_pr_html(pr)
            except Exception as html_error:
                print(f"    Failed to fetch/analyze HTML for PR: {html_error}")
                log_error_to_file(
                    f"Failed to fetch/analyze HTML for {pr.get('url', 'unknown')}",
                    html_error,
                )

            # pr["llm_statuses"] が更新された後にphaseを判定する
            phase = determine_phase(pr)

            pr["phase"] = phase
            process_pr(pr, config, phase)

            # phase3検知時: 該当リポジトリをpullable検査の対象に登録
            if phase == PHASE_3:
                repo_name = pr.get("repository", {}).get("name", "")
                if repo_name and repo_name not in phase3_repo_names:
                    phase3_repo_names.append(repo_name)
        except Exception as pr_error:
            log_error_to_file(
                f"Failed to process PR {pr.get('url', 'unknown') or pr.get('title', 'unknown')}",
                pr_error,
            )
            pr["phase"] = PHASE_LLM_WORKING


def main():
    """Main execution function"""
    # --fetch-pr-html <URL> オプション: PR HTMLを取得してlogs/pr/に保存して終了
    if len(sys.argv) >= 3 and sys.argv[1] == "--fetch-pr-html":
        from .phase.html.pr_html_saver import save_pr_html

        result = save_pr_html(sys.argv[2])
        sys.exit(0 if result else 1)

    config_path = "config.toml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    # Load config if it exists, otherwise use defaults
    config = {}
    config_mtime = 0.0
    try:
        config = load_config(config_path)
        config_mtime = get_config_mtime(config_path)
    except FileNotFoundError:
        print(f"Warning: Config file '{config_path}' not found, using defaults")
        print("You can create a config.toml file to customize settings")
        print("Expected format:")
        print('interval = "1m"  # Check interval (e.g., "30s", "1m", "5m")')
        print()

    # Get interval
    normal_interval_str = config.get("interval", "1m")
    try:
        normal_interval_seconds = parse_interval(normal_interval_str)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("GitHub PR Phase Monitor")
    print("=" * 50)
    print(f"Monitoring interval: {normal_interval_str} ({normal_interval_seconds} seconds)")
    print("Monitoring all repositories for the current GitHub user")
    print("Press CTRL+C to stop monitoring")
    print("=" * 50)

    # Print configuration if verbose mode is enabled
    if config.get("verbose", False):
        print_config(config)

    # Set up signal handler for graceful interruption
    def signal_handler(_signum, _frame):
        print("\n\nMonitoring interrupted by user (CTRL+C)")
        print("Exiting...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # 起動直後に自己リポジトリのアップデートチェックを実行（常に実行）
    run_startup_self_update_foreground()

    # Infinite monitoring loop
    iteration = 0
    consecutive_failures = 0
    while True:
        iteration += 1

        if config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE):
            try:
                maybe_self_update()
            except Exception as update_error:
                log_error_to_file("Auto-update check failed", update_error)

        print(f"\n{'=' * 50}")
        print(f"Check #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")

        # Capture rate limit before API calls for per-iteration consumption tracking
        try:
            before_rate_limit = get_rate_limit_info()
        except Exception as rate_limit_error:
            log_error_to_file("Failed to fetch pre-iteration rate limit info", rate_limit_error)
            before_rate_limit = None

        # Initialize variables to track status for summary
        all_prs = []
        repos_with_prs = []
        phase3_repo_names: list[str] = []
        skip_pr_check = False

        try:
            # updatedAt pre-check: determine which repos (if any) changed since last iteration.
            # On the first call this stores the baseline and returns None (run full check).
            # On subsequent calls this compares the baseline and returns the set of changed repos.
            # If the set is empty, nothing changed and we can skip Phase 1 + Phase 2 entirely.
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
                    # Display issues when no repositories with open PRs are found
                    # No PRs means llm_working_count = 0
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

                    # Track phases to detect if all PRs are in "LLM working"
                    _process_open_prs(all_prs, phase3_repo_names, config)

                # Save PR snapshot for display on subsequent skip-check iterations.
                # Done after Phase 1/2 (including the empty case) so the cache is always
                # up-to-date and never shows stale PRs when there are actually none.
                set_last_pr_snapshot(all_prs, repos_with_prs)

                if all_prs:
                    # Count how many PRs are in "LLM working" phase
                    # This count is used for rate limit protection - when too many PRs are being
                    # worked on simultaneously, we pause auto-assignment to prevent API rate limits
                    llm_working_count = sum(1 for pr in all_prs if is_llm_working(pr))
                    max_llm_working_parallel = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)
                    llm_working_below_cap = llm_working_count < max_llm_working_parallel

                    # Look for new issues to assign when:
                    # 1. All PRs are in "LLM working" phase (existing work is in progress), OR
                    # 2. PR count is less than 3 (few PRs, so we can look for more work)
                    # The llm_working_count throttles assignment when parallel work is too high
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
                        # Display issues and potentially auto-assign new work
                        # Throttling is applied inside the function based on llm_working_count
                        display_issues_from_repos_without_prs(config, llm_working_count=llm_working_count)

            elif skip_pr_check:
                # updatedAt 不変: GraphQL Phase 1/2 はスキップ
                # しかし、open PR のphase変化（1A→1B, 1B→2A等）を検知するため、HTMLを毎回再取得する
                # (updatedAt はPRのphase変化では更新されないため、HTMLフェッチが必須)
                snapshot = get_last_pr_snapshot()
                if snapshot is not None and snapshot[0]:
                    cached_prs, cached_repos = snapshot

                    # open PR 件数を毎回 GraphQL で再取得し、変化があれば Phase 1/2 を強制実行する
                    # (updatedAt は PR の新規作成を反映しないことがあるため、件数の乖離が生じうる)
                    print("\n  open PR 件数を再確認中 (GraphQL)...")
                    fresh_repos_with_prs = get_repositories_with_open_prs()
                    cached_total = sum(r.get("openPRCount", 0) for r in cached_repos)
                    fresh_total = sum(r.get("openPRCount", 0) for r in fresh_repos_with_prs)

                    if fresh_total != cached_total:
                        # PR 件数が変化 → Phase 1/2 を強制実行して最新の PR 一覧を取得する
                        print(f"  open PR 件数が変化 ({cached_total} → {fresh_total})。Phase 1/2 を強制実行します。")
                        repos_with_prs = fresh_repos_with_prs
                        all_prs = get_pr_details_batch(repos_with_prs)
                        if all_prs:
                            print(f"\n  Found {len(all_prs)} open PR(s) total")
                            _process_open_prs(all_prs, phase3_repo_names, config)
                        set_last_pr_snapshot(all_prs, repos_with_prs)
                    else:
                        # PR 件数は変化なし → HTML のみ再取得 (phase 変化を検知するため)
                        print("\n  open PR のHTML再取得 (updatedAt 不変でもphase変化を検知するため / Refetching HTML for open PRs to detect phase changes)...")
                        all_prs = cached_prs
                        repos_with_prs = cached_repos
                        _process_open_prs(all_prs, phase3_repo_names, config)
                        set_last_pr_snapshot(all_prs, repos_with_prs)

                    # skip_pr_check を False にリセット: 今イテレーションの表示セクション (display_status_summary)
                    # でスナップショットではなく最新のHTML取得結果を使うため
                    skip_pr_check = False
                else:
                    # スナップショット未作成またはPRなし: 次イテレーションでフルチェックを強制する
                    # (updatedAt ベースラインをリセットすることで、次回の get_repos_changed_since_last_check が
                    #  None を返し、通常の Phase 1/2 チェックが実行される)
                    log_error_to_file(
                        "skip_pr_check=True but no cached PR snapshot; resetting updatedAt baseline for full check next iteration",
                        None,
                    )
                    reset_repos_updated_at_baseline()

                # 変化なし: キャッシュからTop 10 issuesを表示 (GraphQLクエリ不要)
                display_cached_top_issues()

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
                display_pending_local_repo_results()
            except Exception as local_repo_error:
                log_error_to_file("Failed to check local repos", local_repo_error)

            # Reset consecutive-failure counter on a successful iteration
            consecutive_failures = 0

        except GitHubRateLimitError as e:
            print(f"\nError: {e}")
            rate_limit_info = getattr(e, "rate_limit_info", None)
            if isinstance(rate_limit_info, dict):
                used = rate_limit_info.get("used", "unknown")
                remaining = rate_limit_info.get("remaining", "unknown")
                limit = rate_limit_info.get("limit", "unknown")
                reset = rate_limit_info.get("reset")
                reset_display, reset_in_display = _format_rate_limit_reset(reset)
                print(
                    f"GraphQL API利用状況: used={used}, remaining={remaining}, limit={limit}, "
                    f"reset={reset_display}, reset_in={reset_in_display}"
                )
            print("GitHub APIのレート制限に達しています。リセット後に再実行してください。")
            print("確認コマンド: gh api rate_limit")
            log_error_to_file("GitHub API rate limit exceeded during monitoring loop", e)
            consecutive_failures += 1
        except RuntimeError as e:
            print(f"\nError: {e}")
            print("Please ensure you are authenticated with gh CLI")
            log_error_to_file("Runtime error during monitoring loop", e)
            consecutive_failures += 1
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            traceback.print_exc()
            log_error_to_file("Unexpected error during monitoring loop", e)

            # Track consecutive unexpected failures to avoid infinite error loops
            consecutive_failures += 1

            if consecutive_failures >= 3:
                print("\nEncountered 3 consecutive unexpected errors; continuing monitoring with error counter capped.")
                consecutive_failures = 3

        # Display status summary before waiting
        # This helps users understand the current state at a glance,
        # especially on terminals with limited display lines.
        # Note: If an error occurred during data collection, the summary will show
        # incomplete or empty data, which is acceptable as it reflects the actual
        # state that was successfully retrieved before the error.
        try:
            after_rate_limit = get_rate_limit_info()
            _display_rate_limit_usage(before_rate_limit, after_rate_limit)
        except Exception as rate_limit_display_error:
            log_error_to_file("Failed to display rate limit usage", rate_limit_display_error)
            after_rate_limit = None

        # Check if current consumption rate would exhaust the rate limit before reset
        try:
            should_throttle, throttled_interval = _check_rate_limit_throttle(
                before_rate_limit, after_rate_limit, normal_interval_seconds
            )
        except Exception as throttle_error:
            log_error_to_file("Failed to check rate limit throttle", throttle_error)
            should_throttle = False
            throttled_interval = normal_interval_seconds

        try:
            display_prs, display_repos = all_prs, repos_with_prs
            no_change = False
            if skip_pr_check:
                snapshot = get_last_pr_snapshot()
                if snapshot is not None:
                    display_prs, display_repos = snapshot
                    no_change = True
            display_status_summary(display_prs, display_repos, config, no_change=no_change)
        except Exception as summary_error:
            log_error_to_file("Failed to display status summary", summary_error)

        # Check if PR state has not changed for too long and switch to reduced frequency mode
        try:
            use_reduced_frequency = check_no_state_change_timeout(all_prs, config)
        except Exception as timeout_error:
            log_error_to_file("Failed to evaluate reduced frequency interval", timeout_error)
            use_reduced_frequency = False

        # Determine which interval to use
        if use_reduced_frequency:
            # Use reduced frequency interval (default: 1h)
            reduced_interval_str = (config or {}).get("reduced_frequency_interval", "1h")
            try:
                reduced_interval_seconds = parse_interval(reduced_interval_str)
                current_interval_seconds = reduced_interval_seconds
                current_interval_str = reduced_interval_str
            except ValueError as e:
                print(f"Error: Invalid reduced_frequency_interval format: {e}")
                sys.exit(1)
        elif should_throttle:
            # Rate limit throttling: slow down to avoid exhausting the quota before reset
            current_interval_seconds = throttled_interval
            current_interval_str = format_elapsed_time(throttled_interval)
            print(f"\n{'=' * 50}")
            print("現在の消費ペースでは、レートリミットがリセットされる前に使い切る可能性があります。")
            print(f"監視間隔を{current_interval_str}に延長します。")
            print(f"{'=' * 50}")
        else:
            # Use normal interval (preserved separately to avoid contamination)
            current_interval_seconds = normal_interval_seconds
            current_interval_str = normal_interval_str

        # Wait with countdown display and check for config changes
        try:
            new_config, new_interval_seconds, new_interval_str, new_config_mtime = wait_with_countdown(
                current_interval_seconds,
                current_interval_str,
                config_path,
                config_mtime,
                self_update_callback=maybe_self_update
                if config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE)
                else None,
                self_update_interval_seconds=UPDATE_CHECK_INTERVAL_SECONDS,
            )
        except Exception as wait_error:
            log_error_to_file("wait_with_countdown failed; falling back to sleep", wait_error)
            time.sleep(current_interval_seconds)
            continue

        # Update config and interval based on what was returned from wait
        # Config will be non-empty only if successfully reloaded during wait
        config_reloaded = new_config_mtime != config_mtime
        if config_reloaded and new_config:
            config = new_config
            # Update normal interval only on hot reload (config change).
            # This prevents the normal interval from being contaminated by reduced frequency
            # interval values that may be returned from wait_with_countdown().
            normal_interval_seconds = new_interval_seconds
            normal_interval_str = new_interval_str
        # Always update mtime
        config_mtime = new_config_mtime


if __name__ == "__main__":
    main()
