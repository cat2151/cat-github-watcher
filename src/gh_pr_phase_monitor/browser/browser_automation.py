"""Browser automation module for automated button clicking

This module provides functionality to automate clicking buttons in a browser
using PyAutoGUI with image recognition. It's designed to work on Windows PCs
and can be optionally enabled through configuration.

Important: Users must provide screenshots of the buttons they want to click.
See README.ja.md for instructions on how to capture button screenshots.
"""

import sys
import traceback
import webbrowser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import (
    DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE,
    get_phase3_merge_config,
    is_process_running,
)
from ..ui.notification_window import (
    NotificationWindow,
    _close_notification_window,
    _start_button_notification,
    _wait_with_cancellation,
    _was_closed_by_user,
)
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
from .issue_assigner import (  # noqa: F401 (re-exported for backward compatibility)
    ASSIGN_CANCEL_MESSAGE,
    DEFAULT_ASSIGN_NOTIFICATION_MESSAGE,
    ISSUE_ASSIGN_RETRY_AFTER_SECONDS,
    _issue_assign_attempted,
    assign_issue_to_copilot_automated,
)
from .window_manager import (
    _activate_window_by_title,  # noqa: F401 (re-exported for backward compatibility)
    )

DEFAULT_MERGE_NOTIFICATION_MESSAGE = "ブラウザを開いてMergeボタンを探索中..."


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

    # Open browser in background by default to avoid CTRL+W accidentally closing
    # the newly opened tab when user was intending to close another window
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
