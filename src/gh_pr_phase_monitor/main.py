"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback

from .core.config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_ENABLE_AUTO_UPDATE_DEBUG_LOG,
    get_config_mtime,
    load_config,
    parse_interval,
    print_config,
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
    set_auto_update_debug_log_enabled,
)
from .monitor.error_logger import log_error_to_file
from .monitor.iteration_runner import run_one_iteration
from .monitor.monitor import check_no_state_change_timeout, determine_current_interval
from .monitor.state_tracker import get_last_pr_snapshot
from .ui.display import display_cached_top_issues, display_status_summary
from .ui.wait_handler import wait_with_countdown


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

    set_auto_update_debug_log_enabled(
        config.get("enable_auto_update_debug_log", DEFAULT_ENABLE_AUTO_UPDATE_DEBUG_LOG)
    )

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

    # 起動直後に自己リポジトリのアップデート有無を確認する
    run_startup_self_update_foreground(
        apply_update=config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE)
    )

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

        all_prs: list = []
        repos_with_prs: list = []
        skip_pr_check = False

        try:
            all_prs, repos_with_prs, skip_pr_check = run_one_iteration(config, iteration)
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

        repos_for_cached_issue_display = list(display_repos)

        def redisplay_cached_issues() -> None:
            display_cached_top_issues(repos_for_cached_issue_display)

        # Check if PR state has not changed for too long and switch to reduced frequency mode
        try:
            use_reduced_frequency = check_no_state_change_timeout(all_prs, config)
        except Exception as timeout_error:
            log_error_to_file("Failed to evaluate reduced frequency interval", timeout_error)
            use_reduced_frequency = False

        # Determine which interval to use
        current_interval_seconds, current_interval_str = determine_current_interval(
            use_reduced_frequency,
            should_throttle,
            throttled_interval,
            normal_interval_seconds,
            normal_interval_str,
            config,
        )

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
                status_display_callback=redisplay_cached_issues,
                status_display_interval_seconds=60,
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
            set_auto_update_debug_log_enabled(
                config.get("enable_auto_update_debug_log", DEFAULT_ENABLE_AUTO_UPDATE_DEBUG_LOG)
            )
            # Update normal interval only on hot reload (config change).
            # This prevents the normal interval from being contaminated by reduced frequency
            # interval values that may be returned from wait_with_countdown().
            normal_interval_seconds = new_interval_seconds
            normal_interval_str = new_interval_str
        # Always update mtime
        config_mtime = new_config_mtime


if __name__ == "__main__":
    main()
