"""Browser automation module for automated button clicking

This module provides functionality to automate clicking buttons in a browser
using PyAutoGUI with image recognition. It's designed to work on Windows PCs
and can be optionally enabled through configuration.

Important: Users must provide screenshots of the buttons they want to click.
See README.ja.md for instructions on how to capture button screenshots.
"""

import sys
import time
import traceback
import webbrowser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .browser_cooldown import (
    BROWSER_OPEN_COOLDOWN_SECONDS,  # noqa: F401 (re-exported for backward compatibility)
    _can_open_browser,
    _get_remaining_cooldown,
    _record_browser_open,
)
from .button_clicker import (
    PYAUTOGUI_AVAILABLE,
    _click_button_with_image,  # noqa: F401 (re-exported for backward compatibility)
    _click_button_with_ocr,  # noqa: F401 (re-exported for backward compatibility)
    _get_screenshot_path,  # noqa: F401 (re-exported for backward compatibility)
    _save_debug_info,  # noqa: F401 (re-exported for backward compatibility)
    _validate_button_delay,
    _validate_wait_seconds,
    reset_user_cancelled_notification,
    set_user_cancelled_notification,
)
from .config import (
    DEFAULT_ASSIGN_TO_COPILOT_CONFIG,
    DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE,
    get_assign_to_copilot_config,
    get_phase3_merge_config,
    is_process_running,
)
from .notification_window import (
    NotificationWindow,
    _close_notification_window,
    _start_button_notification,
    _update_notification_status,
    _wait_with_cancellation,
    _was_closed_by_user,
)
from .window_manager import (
    _activate_window_by_title,  # noqa: F401 (re-exported for backward compatibility)
    _get_active_window_title,
)

# Track which issue URLs have had assignment attempted with timestamp: dict of URL -> timestamp
# This prevents repeatedly trying to assign the same issue when automation fails
# URLs expire after 24 hours, allowing retries for temporary failures
_issue_assign_attempted: Dict[str, float] = {}

# Time (in seconds) before an issue URL can be retried (24 hours)
ISSUE_ASSIGN_RETRY_AFTER_SECONDS = 24 * 60 * 60

DEFAULT_ASSIGN_NOTIFICATION_MESSAGE = "ブラウザを開いてCopilot割り当てボタンを探索中..."
DEFAULT_MERGE_NOTIFICATION_MESSAGE = "ブラウザを開いてMergeボタンを探索中..."
ASSIGN_CANCEL_MESSAGE = "auto assignを中断します"


def _log_error(message: str, exc: Exception | BaseException | None = None) -> None:
    """Append an error entry to logs/error.log without raising further exceptions."""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception as log_exc:
        # Logging must never raise; emit minimal message to stderr as last resort.
        print(
            f"[browser_automation._log_error] Failed to write to error.log: {log_exc!r} (original message: {message})",
            file=sys.stderr,
        )


def _set_user_cancelled() -> None:
    """Set the global user-cancelled flag (called back from NotificationWindow)."""
    set_user_cancelled_notification()


def is_pyautogui_available() -> bool:
    """Check if PyAutoGUI is available for use

    Returns:
        True if PyAutoGUI is installed and available, False otherwise
    """
    return PYAUTOGUI_AVAILABLE


def _should_autoraise_window(config: Optional[Dict[str, Any]] = None) -> bool:
    """Determine if browser window should be raised to foreground

    Args:
        config: Configuration dictionary

    Returns:
        True if window should be raised, False otherwise
    """
    if config is None:
        config = {}

    # Get the check_process_before_autoraise setting (default: True)
    check_process = config.get("check_process_before_autoraise", DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE)

    # If the setting is disabled, always autoraise
    if not check_process:
        return True

    # If enabled, check if cat-window-watcher is running
    if is_process_running("cat-window-watcher"):
        print("  ℹ cat-window-watcher is running, browser window will not be raised to foreground")
        return False

    return True


def assign_issue_to_copilot_automated(issue_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically assign an issue to Copilot by clicking buttons in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the issue in a browser (requires an already-authenticated browser session)
    2. Wait for the configured time (default 2 seconds)
    3. Click the "Assign to Copilot" button (using screenshot)
    4. Click the "Assign" button (using screenshot)

    Important: This function uses webbrowser.open() which opens the URL in your system's
    default browser. You must be already logged into GitHub in that browser for the
    automation to work. The function does not handle authentication.

    Note: To prevent issues with opening multiple pages simultaneously, this function
    will only open a browser if at least 60 seconds have passed since the last browser
    was opened. If the cooldown has not elapsed, the function returns False and the
    operation will be retried in the next monitoring iteration.

    Note: Once an assignment attempt has been made for a specific issue URL (whether
    successful or not), subsequent attempts for the same URL will be skipped for 24 hours
    to prevent repeatedly opening the same page when automation fails. After 24 hours,
    the issue URL can be retried automatically, allowing recovery from temporary failures
    (e.g., missing screenshots, UI changes). This prevents opening duplicate browser tabs
    while still allowing eventual retries.

    Required screenshots (must be provided by user):
    - assign_to_copilot.png: Screenshot of "Assign to Copilot" button
    - assign.png: Screenshot of "Assign" button

    Args:
        issue_url: The URL of the GitHub issue
        config: Optional configuration dict with automation settings
                Supported keys in assign_to_copilot section:
                - wait_seconds (int): Seconds to wait for page load (default: 2)
                - button_delay (float): Seconds to wait between button clicks (default: 2.0)
                - confidence (float): Image matching confidence 0.0-1.0 (default: 0.8)
                - screenshot_dir (str): Directory containing screenshots (default: "screenshots")

    Returns:
        True if automation was successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not installed. Install with: pip install pyautogui pillow")
        return False

    reset_user_cancelled_notification()

    # Check if assignment has already been attempted for this issue recently
    if issue_url in _issue_assign_attempted:
        last_attempt_time = _issue_assign_attempted[issue_url]
        elapsed = time.time() - last_attempt_time
        if elapsed < ISSUE_ASSIGN_RETRY_AFTER_SECONDS:
            remaining_hours = (ISSUE_ASSIGN_RETRY_AFTER_SECONDS - elapsed) / 3600
            print("  ℹ Assignment already attempted for this issue recently")
            print(f"     Will retry after {remaining_hours:.1f} hours (to prevent duplicate tabs)")
            return False
        else:
            # Enough time has passed, allow retry
            print(f"  ℹ Retrying assignment (last attempt was {elapsed / 3600:.1f} hours ago)")

    # Check if enough time has passed since the last browser open
    if not _can_open_browser():
        remaining = _get_remaining_cooldown()
        print(f"  ⏳ Browser cooldown in effect. Please wait {int(remaining)} more seconds before opening next page.")
        print("     This prevents issues with opening multiple pages simultaneously.")
        print("     Will retry in the next monitoring iteration.")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    assign_config = get_assign_to_copilot_config(config)
    active_window_title = _get_active_window_title()

    # Validate and get configuration values
    wait_seconds = _validate_wait_seconds(assign_config, default=DEFAULT_ASSIGN_TO_COPILOT_CONFIG["wait_seconds"])
    button_delay = _validate_button_delay(assign_config)
    notification: Optional[NotificationWindow] = None

    try:
        print("  → [PyAutoGUI] Opening issue in browser...")
        print("  ℹ Ensure you are already logged into GitHub in your default browser")

        # Determine if window should be raised to foreground
        autoraise = _should_autoraise_window(config)
        notification = _start_button_notification(
            assign_config,
            DEFAULT_ASSIGN_NOTIFICATION_MESSAGE,
            cancel_message=ASSIGN_CANCEL_MESSAGE,
            on_user_cancel=_set_user_cancelled,
        )

        try:
            try:
                opened = webbrowser.open(issue_url, autoraise=autoraise)
                if not opened:
                    print(f"  ✗ Browser did not open for issue URL '{issue_url}'")
                    print("     Please check your default browser settings")
                    return False
            except Exception as e:
                print(f"  ✗ Failed to open browser for issue URL '{issue_url}': {e}")
                return False

            # Record the browser open time to enforce cooldown
            _record_browser_open()

            # Mark this issue as having an assignment attempt with current timestamp
            # This is done immediately after browser opens to prevent repeated browser opens
            # even if the automation fails later (e.g., button not found). The goal is to
            # prevent opening 30+ tabs of the same URL, not to retry until successful.
            # The timestamp allows retries after 24 hours for temporary failures.
            _issue_assign_attempted[issue_url] = time.time()

            # Wait for the configured time
            print(f"  → Waiting {wait_seconds} seconds for page to load...")
            if _wait_with_cancellation(wait_seconds, notification):
                print("  ⚠ Notification window was closed by user; skipping automated assignment")
                return False

            # Activate window if window_title is configured (1 second before clicking buttons)
            window_title = assign_config.get("window_title")
            if window_title:
                print("  → Waiting 1 second before activating window...")
                time.sleep(1)  # Wait 1 second before activating window
                _activate_window_by_title(window_title, assign_config)
            active_window_title = _get_active_window_title() or active_window_title

            # Click "Assign to Copilot" button
            print("  → Looking for 'Assign to Copilot' button...")
            _update_notification_status(notification, "Assign to Copilotボタンを探索中です…", active_window_title)
            if _was_closed_by_user(notification):
                print("  ⚠ Notification window was closed by user; skipping automated assignment")
                return False
            if not _click_button_with_image(
                "assign_to_copilot",
                assign_config,
                max_attempts=30,
                poll_interval=1.0,
                pre_click_delay=1.0,
            ):
                print("  ✗ Could not find or click 'Assign to Copilot' button")
                active_window_title = _get_active_window_title() or active_window_title
                _update_notification_status(
                    notification, "Assign to Copilotボタンを探索中です…まだ見つかりません…", active_window_title
                )
                return False

            active_window_title = _get_active_window_title() or active_window_title
            _update_notification_status(
                notification, "Assign to Copilotボタンを発見しました。クリックします", active_window_title
            )
            print("  ✓ Clicked 'Assign to Copilot' button")

            # Wait for the assignment UI to appear
            print(f"  → Waiting {button_delay} seconds for UI to respond...")
            if _wait_with_cancellation(button_delay, notification):
                print("  ⚠ Notification window was closed by user; skipping automated assignment")
                return False

            if _was_closed_by_user(notification):
                print("  ⚠ Notification window was closed by user; skipping automated assignment")
                return False

            # Click "Assign" button
            print("  → Looking for 'Assign' button...")
            active_window_title = _get_active_window_title() or active_window_title
            _update_notification_status(notification, "緑のAssignボタンを探索中です…", active_window_title)
            if not _click_button_with_image(
                "assign",
                assign_config,
                max_attempts=30,
                poll_interval=1.0,
                pre_click_delay=1.0,
            ):
                print("  ✗ Could not find or click 'Assign' button")
                active_window_title = _get_active_window_title() or active_window_title
                _update_notification_status(
                    notification, "緑のAssignボタンを探索中です…まだ見つかりません…", active_window_title
                )
                return False

            active_window_title = _get_active_window_title() or active_window_title
            _update_notification_status(
                notification,
                "緑のAssignボタンを発見しました。クリックしました。自動assignを正常終了します",
                active_window_title,
            )
            print("  ✓ Clicked 'Assign' button")
            print("  ✓ [PyAutoGUI] Successfully automated issue assignment to Copilot")

            # Wait before finishing
            time.sleep(button_delay)

            return True
        finally:
            _close_notification_window(notification)
    except Exception as exc:  # Catch unexpected automation errors without terminating the monitor loop
        _log_error(f"Auto-assign failed for {issue_url}", exc)
        print("  ✗ Unexpected error during automated assignment; skipping and continuing")
        return False


def merge_pr_automated(pr_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically merge a PR by clicking the merge button in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the PR in a browser (requires an already-authenticated browser session)
    2. Wait for the configured time (default 10 seconds)
    3. Click the "Merge pull request" button (using screenshot)
    4. Click the "Confirm merge" button (using screenshot)
    5. Click the "Delete branch" button (using screenshot)

    Important: This function uses webbrowser.open() which opens the URL in your system's
    default browser. You must be already logged into GitHub in that browser for the
    automation to work. The function does not handle authentication.

    Note: To prevent issues with opening multiple pages simultaneously, this function
    will only open a browser if at least 60 seconds have passed since the last browser
    was opened. If the cooldown has not elapsed, the function returns False and the
    operation will be retried in the next monitoring iteration.

    Required screenshots (must be provided by user):
    - merge_pull_request.png: Screenshot of "Merge pull request" button
    - confirm_merge.png: Screenshot of "Confirm merge" button
    - delete_branch.png: Screenshot of "Delete branch" button (optional)

    Args:
        pr_url: The URL of the GitHub PR
        config: Optional configuration dict with automation settings
                Supported keys in phase3_merge section:
                - wait_seconds (int): Seconds to wait for page load (default: 10)
                - button_delay (float): Seconds to wait between button clicks (default: 2.0)
                - confidence (float): Image matching confidence 0.0-1.0 (default: 0.8)
                - screenshot_dir (str): Directory containing screenshots (default: "screenshots")

    Returns:
        True if automation was successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        print("  ✗ PyAutoGUI is not installed. Install with: pip install pyautogui pillow")
        return False

    reset_user_cancelled_notification()

    # Check if enough time has passed since the last browser open
    if not _can_open_browser():
        remaining = _get_remaining_cooldown()
        print(f"  ⏳ Browser cooldown in effect. Please wait {int(remaining)} more seconds before opening next page.")
        print("     This prevents issues with opening multiple pages simultaneously.")
        print("     Will retry in the next monitoring iteration.")
        return False

    # Get configuration settings
    if config is None:
        config = {}

    merge_config = get_phase3_merge_config(config)

    # Validate and get configuration values
    wait_seconds = _validate_wait_seconds(merge_config)
    button_delay = _validate_button_delay(merge_config)
    notification: Optional[NotificationWindow] = None

    print("  → [PyAutoGUI] Opening PR in browser...")
    print("  ℹ Ensure you are already logged into GitHub in your default browser")

    # Determine if window should be raised to foreground
    autoraise = _should_autoraise_window(config)
    notification = _start_button_notification(
        merge_config, DEFAULT_MERGE_NOTIFICATION_MESSAGE, on_user_cancel=_set_user_cancelled
    )

    try:
        try:
            opened = webbrowser.open(pr_url, autoraise=autoraise)
            if not opened:
                print(f"  ✗ Browser did not open for PR URL '{pr_url}'")
                print("     Please check your default browser settings")
                return False
        except Exception as e:
            print(f"  ✗ Failed to open browser for PR URL '{pr_url}': {e}")
            return False

        # Record the browser open time to enforce cooldown
        _record_browser_open()

        # Wait for the configured time
        print(f"  → Waiting {wait_seconds} seconds for page to load...")
        if _wait_with_cancellation(wait_seconds, notification):
            print("  ⚠ Notification window was closed by user; skipping automated merge")
            return False

        # Activate window if window_title is configured (1 second before clicking buttons)
        window_title = merge_config.get("window_title")
        if window_title:
            print("  → Waiting 1 second before activating window...")
            if _wait_with_cancellation(1, notification):
                print("  ⚠ Notification window was closed by user; skipping automated merge")
                return False
            _activate_window_by_title(window_title, merge_config)

        # Click "Merge pull request" button
        print("  → Looking for 'Merge pull request' button...")
        if _was_closed_by_user(notification):
            print("  ⚠ Notification window was closed by user; skipping automated merge")
            return False
        if not _click_button_with_image("merge_pull_request", merge_config):
            print("  ✗ Could not find or click 'Merge pull request' button")
            return False

        print("  ✓ Clicked 'Merge pull request' button")

        # Wait for the confirmation UI to appear
        print(f"  → Waiting {button_delay} seconds for UI to respond...")
        if _wait_with_cancellation(button_delay, notification):
            print("  ⚠ Notification window was closed by user; skipping automated merge")
            return False

        # Click "Confirm merge" button
        print("  → Looking for 'Confirm merge' button...")
        if _was_closed_by_user(notification):
            print("  ⚠ Notification window was closed by user; skipping automated merge")
            return False
        if not _click_button_with_image("confirm_merge", merge_config):
            print("  ✗ Could not find or click 'Confirm merge' button")
            return False

        print("  ✓ Clicked 'Confirm merge' button")

        # Wait for merge to complete and delete branch button to appear
        print(f"  → Waiting {button_delay + 1.0} seconds for merge to complete...")
        if _wait_with_cancellation(button_delay + 1.0, notification):
            print("  ⚠ Notification window was closed by user; skipping automated merge")
            return False

        # Click "Delete branch" button (optional - don't fail if not found)
        print("  → Looking for 'Delete branch' button...")
        if _was_closed_by_user(notification):
            print("  ⚠ Notification window was closed by user; skipping automated merge")
            return False
        if not _click_button_with_image("delete_branch", merge_config):
            print("  ⚠ Could not find or click 'Delete branch' button (may have already been deleted)")
        else:
            print("  ✓ Clicked 'Delete branch' button")

        print("  ✓ [PyAutoGUI] Successfully automated PR merge")

        # Wait before finishing
        _wait_with_cancellation(button_delay, notification)

        return True
    finally:
        _close_notification_window(notification)
