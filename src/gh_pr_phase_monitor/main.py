"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

from .monitor.auto_updater import (
    UPDATE_CHECK_INTERVAL_SECONDS,
    apply_startup_restart_if_needed,
    maybe_self_update,
    start_startup_self_update_check,
)
from .core.config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS,
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_config_mtime,
    load_config,
    parse_interval,
    print_config,
    validate_phase3_merge_config_required,
)
from .ui.display import display_issues_from_repos_without_prs, display_status_summary
from .github.github_auth import get_current_user
from .github.github_client import get_pr_details_batch, get_repositories_with_open_prs
from .github.graphql_client import GitHubRateLimitError, get_rate_limit_info
from .monitor.local_repo_watcher import (
    display_pending_local_repo_results,
    notify_phase3_detected,
    start_local_repo_monitoring,
)
from .monitor.monitor import check_no_state_change_timeout
from .monitor.pages_watcher import check_pages_deployments_for_repos, get_pages_repos_from_config
from .phase.phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase, set_use_graphql_phase_detection
from .actions.pr_actions import process_pr
from .phase.pr_data_recorder import record_reaction_snapshot, reset_snapshot_cache
from .phase.pr_html_saver import save_pr_html
from .github.rate_limit_handler import (
    _check_rate_limit_throttle,
    _display_rate_limit_usage,
    _format_rate_limit_reset,
)
from .core.time_utils import format_elapsed_time
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


def main():
    """Main execution function"""
    # --fetch-pr-html <URL> オプション: PR HTMLを取得してlogs/pr/に保存して終了
    if len(sys.argv) >= 3 and sys.argv[1] == "--fetch-pr-html":
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

    set_use_graphql_phase_detection(config.get("use_graphql_phase_detection", False))

    # Get interval setting (default to 1 minute if not specified)
    # Keep the normal interval separate from the current interval to prevent the normal
    # interval from being overwritten by reduced frequency interval values during mode switches
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

    # 起動直後に別スレッドで自己リポジトリのアップデートチェックを一度実行
    if config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE):
        start_startup_self_update_check()

    # Infinite monitoring loop
    iteration = 0
    consecutive_failures = 0
    while True:
        iteration += 1

        if config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE):
            try:
                apply_startup_restart_if_needed()
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

        # Reset snapshot cache to allow recording new snapshots in this iteration
        reset_snapshot_cache()

        # Initialize variables to track status for summary
        all_prs = []
        pr_phases = []
        repos_with_prs = []
        phase3_repo_names: list[str] = []

        try:
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

                    snapshots_enabled = config.get("enable_pr_phase_snapshots", DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS)
                    # Track phases to detect if all PRs are in "LLM working"
                    for pr in all_prs:
                        try:
                            phase = determine_phase(pr)

                            try:
                                record_reaction_snapshot(pr, phase, enable_snapshots=snapshots_enabled)
                                phase = determine_phase(pr)
                            except Exception as snapshot_error:
                                print(f"    Failed to capture PR reaction/LLM status data: {snapshot_error}")
                                log_error_to_file(
                                    f"Failed to capture PR reaction/LLM status data for {pr.get('url', 'unknown')}",
                                    snapshot_error,
                                )

                            # 検証用: HTML と JSON を常時保存
                            try:
                                pr_url = pr.get("url", "")
                                if pr_url:
                                    save_pr_html(pr_url)
                            except Exception as html_save_error:
                                log_error_to_file(
                                    f"Failed to save HTML/JSON for {pr.get('url', 'unknown')}",
                                    html_save_error,
                                )

                            pr_phases.append(phase)
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
                            pr_phases.append(PHASE_LLM_WORKING)

                    # Count how many PRs are in "LLM working" phase
                    # This count is used for rate limit protection - when too many PRs are being
                    # worked on simultaneously, we pause auto-assignment to prevent API rate limits
                    llm_working_count = sum(1 for phase in pr_phases if phase == PHASE_LLM_WORKING)
                    max_llm_working_parallel = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)
                    llm_working_below_cap = llm_working_count < max_llm_working_parallel

                    # Look for new issues to assign when:
                    # 1. All PRs are in "LLM working" phase (existing work is in progress), OR
                    # 2. PR count is less than 3 (few PRs, so we can look for more work)
                    # The llm_working_count throttles assignment when parallel work is too high
                    total_pr_count = len(all_prs)
                    all_llm_working = bool(pr_phases) and all(phase == PHASE_LLM_WORKING for phase in pr_phases)
                    all_phase3 = bool(pr_phases) and all(phase == PHASE_3 for phase in pr_phases)
                    active_parallel_prs = sum(1 for phase in pr_phases if phase != PHASE_3)

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
            display_status_summary(all_prs, pr_phases, repos_with_prs, config)
        except Exception as summary_error:
            log_error_to_file("Failed to display status summary", summary_error)

        # Check if PR state has not changed for too long and switch to reduced frequency mode
        try:
            use_reduced_frequency = check_no_state_change_timeout(all_prs, pr_phases, config)
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
            set_use_graphql_phase_detection(config.get("use_graphql_phase_detection", False))
            # Update normal interval only on hot reload (config change).
            # This prevents the normal interval from being contaminated by reduced frequency
            # interval values that may be returned from wait_with_countdown().
            normal_interval_seconds = new_interval_seconds
            normal_interval_str = new_interval_str
        # Always update mtime
        config_mtime = new_config_mtime


if __name__ == "__main__":
    main()
