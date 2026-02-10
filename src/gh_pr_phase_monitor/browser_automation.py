"""Browser automation module for automated button clicking

This module provides functionality to automate clicking buttons in a browser
using PyAutoGUI with image recognition. It's designed to work on Windows PCs
and can be optionally enabled through configuration.

Important: Users must provide screenshots of the buttons they want to click.
See README.ja.md for instructions on how to capture button screenshots.
"""

import json
import re
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .colors import Colors
from .config import (
    DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE,
    get_assign_to_copilot_config,
    get_phase3_merge_config,
    is_process_running,
)

# PyAutoGUI imports are optional - will be imported only if automation is enabled
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None  # Set to None when not available

# PyGetWindow imports are optional - will be imported only if automation is enabled
try:
    import pygetwindow as gw

    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    gw = None  # Set to None when not available

# tkinter imports are optional - used for on-screen notification window
try:
    import tkinter as tk

    TKINTER_AVAILABLE = True
except Exception:
    TKINTER_AVAILABLE = False
    tk = None

# pytesseract imports are optional - for OCR-based button detection fallback
try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    pytesseract = None
    # Note: PIL.Image is imported locally in _click_button_with_ocr when needed

# Global state to track the last time a browser was opened
# This prevents opening multiple pages simultaneously which can cause issues
# with automated merge and assign operations
_last_browser_open_time: Optional[float] = None

# Minimum time (in seconds) to wait between opening browser pages
BROWSER_OPEN_COOLDOWN_SECONDS = 60

# Track which issue URLs have had assignment attempted with timestamp: dict of URL -> timestamp
# This prevents repeatedly trying to assign the same issue when automation fails
# URLs expire after 24 hours, allowing retries for temporary failures
_issue_assign_attempted: Dict[str, float] = {}

# Time (in seconds) before an issue URL can be retried (24 hours)
ISSUE_ASSIGN_RETRY_AFTER_SECONDS = 24 * 60 * 60

# Debug candidate detection settings
# These thresholds are only used when image recognition fails with the original confidence threshold
# The search stops after finding DEBUG_MAX_CANDIDATES candidates
DEBUG_CANDIDATE_CONFIDENCE_THRESHOLDS = [0.7, 0.6, 0.5]  # Try these confidence levels for debug candidates
DEBUG_MAX_CANDIDATES = 3  # Maximum number of candidate regions to save for debugging

# OCR detection settings
OCR_BUTTON_PADDING = 20  # Pixels to add around detected text to account for button borders

# Default notification window settings for button-based automation
DEFAULT_NOTIFICATION_WIDTH = 400
DEFAULT_NOTIFICATION_HEIGHT = 150
DEFAULT_NOTIFICATION_POSITION_X = 100
DEFAULT_NOTIFICATION_POSITION_Y = 100
DEFAULT_ASSIGN_NOTIFICATION_MESSAGE = "ブラウザを開いてCopilot割り当てボタンを探索中..."
DEFAULT_MERGE_NOTIFICATION_MESSAGE = "ブラウザを開いてMergeボタンを探索中..."


_SIMPLE_ANSI_HEX = {
    "90": "#555555",
    "91": "#ff5555",
    "92": "#55ff55",
    "93": "#ffff55",
    "94": "#5555ff",
    "95": "#ff55ff",
    "96": "#55ffff",
    "97": "#ffffff",
}


def _ansi_to_hex(color_code: str) -> Optional[str]:
    true_color = re.search(r"\x1b\[38;2;(\d+);(\d+);(\d+)m", color_code or "")
    if true_color:
        red, green, blue = (int(true_color.group(i)) for i in range(1, 4))
        return f"#{red:02x}{green:02x}{blue:02x}"

    indexed = re.search(r"\x1b\[(\d{2})m", color_code or "")
    if indexed:
        return _SIMPLE_ANSI_HEX.get(indexed.group(1))
    return None


def _is_dark_mode_enabled() -> bool:
    try:
        if sys.platform == "darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            return result.stdout.strip().lower() == "dark"

        if sys.platform.startswith("win"):
            try:
                import winreg

                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                ) as key:
                    apps_use_light, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return apps_use_light == 0
            except Exception:
                return False

        # Linux / other POSIX (best-effort GNOME detection)
        gsettings_cmds = [
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
        ]
        for cmd in gsettings_cmds:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
                )
                output = result.stdout.strip().lower()
                if result.returncode == 0 and output:
                    if "dark" in output:
                        return True
                    if "light" in output:
                        return False
            except Exception:
                continue
    except Exception:
        return False

    return False


def _get_notification_theme() -> Dict[str, str]:
    dark_mode = _is_dark_mode_enabled()
    background = "#111111" if dark_mode else "#ffffff"
    fallback_text = "#f5f5f5" if dark_mode else "#111111"

    accent = _ansi_to_hex(Colors.BLUE) or _ansi_to_hex(Colors.CYAN) or _ansi_to_hex(Colors.GREEN)
    text_color = accent or fallback_text

    return {"background": background, "text": text_color, "accent": accent or text_color}


def _parse_int_setting(value: Any, default: int) -> int:
    """Parse an integer setting with a safe fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class NotificationWindow:
    """Lightweight topmost notification window shown during automation."""

    def __init__(self, message: str, width: int, height: int, x: int, y: int):
        self.message = message
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.root = None
        self._should_close = False

    def show(self) -> None:
        """Show the notification window on a separate thread."""
        if not TKINTER_AVAILABLE or tk is None:
            return

        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        """Render the window and block in its own Tk event loop."""
        try:
            self.root = tk.Tk()
            self.root.title("処理中")
            theme = _get_notification_theme()
            self.root.configure(
                bg=theme["background"],
                highlightbackground=theme["accent"],
                highlightcolor=theme["accent"],
                highlightthickness=2,
            )
            geometry = f"{self.width}x{self.height}+{self.x}+{self.y}"
            self.root.geometry(geometry)
            self.root.attributes("-topmost", True)

            wraplength = max(0, self.width - 50)
            label = tk.Label(
                self.root,
                text=self.message,
                font=("Arial", 16),
                wraplength=wraplength,
                bg=theme["background"],
                fg=theme["text"],
            )
            label.pack(expand=True, padx=20, pady=20)

            def _check_close() -> None:
                """Poll for close requests from other threads and shut down Tk safely."""
                if self._should_close and self.root is not None:
                    try:
                        self.root.quit()
                        self.root.destroy()
                    except Exception as e:
                        print(f"  ⚠ Failed to close notification window cleanly: {e}")
                    return
                if self.root is not None:
                    self.root.after(100, _check_close)

            self.root.after(100, _check_close)
            self.root.mainloop()
        except Exception:
            self.root = None

    def close(self) -> None:
        """Request the notification window to close."""
        self._should_close = True


def _start_button_notification(config: Dict[str, Any], default_message: str) -> Optional[NotificationWindow]:
    """Create and show a notification window when configured."""
    if not config.get("notification_enabled", True):
        return None

    if not TKINTER_AVAILABLE or tk is None:
        print("  ℹ Tkinter is not available; skipping notification window")
        return None

    width = _parse_int_setting(config.get("notification_width", DEFAULT_NOTIFICATION_WIDTH), DEFAULT_NOTIFICATION_WIDTH)
    height = _parse_int_setting(
        config.get("notification_height", DEFAULT_NOTIFICATION_HEIGHT), DEFAULT_NOTIFICATION_HEIGHT
    )
    pos_x = _parse_int_setting(
        config.get("notification_position_x", DEFAULT_NOTIFICATION_POSITION_X), DEFAULT_NOTIFICATION_POSITION_X
    )
    pos_y = _parse_int_setting(
        config.get("notification_position_y", DEFAULT_NOTIFICATION_POSITION_Y), DEFAULT_NOTIFICATION_POSITION_Y
    )
    message = str(config.get("notification_message", default_message))

    window = NotificationWindow(message, width, height, pos_x, pos_y)
    try:
        window.show()
        return window
    except Exception as e:
        print(f"  ⚠ Failed to show notification window: {e}")
        return None


def _close_notification_window(window: Optional[NotificationWindow]) -> None:
    """Close notification window safely."""
    if window:
        try:
            window.close()
        except Exception as e:
            print(f"  ⚠ Failed to close notification window: {e}")


def _should_maximize_on_first_fail(config: Dict[str, Any]) -> bool:
    """Check whether maximize-on-fail retry is enabled (default: True)."""
    value = config.get("maximize_on_first_fail", True)
    if isinstance(value, bool):
        return value
    return True


def _maximize_window(config: Dict[str, Any]) -> bool:
    """Attempt to maximize the target or active window for better visibility."""
    if not PYGETWINDOW_AVAILABLE or gw is None:
        print("  ℹ pygetwindow is not available; skipping window maximization")
        return False

    window_title = config.get("window_title")
    try:
        target_window = None
        if window_title:
            print(f"  → Searching for window to maximize (title contains '{window_title}')")
            all_windows = gw.getAllWindows()
            matches = [w for w in all_windows if window_title.lower() in w.title.lower()]
            if matches:
                target_window = matches[0]

        if target_window is None:
            try:
                target_window = gw.getActiveWindow()
            except Exception:
                target_window = None

        if target_window is None:
            print("  ⚠ Could not find a window to maximize")
            return False

        if getattr(target_window, "isMinimized", False):
            target_window.restore()

        try:
            target_window.activate()
        except Exception:
            # Some platforms/window managers may not support activate; continue without failing
            pass

        try:
            target_window.maximize()
        except Exception:
            # Some platforms may not support maximize; rely on activate/restore
            pass

        print("  → Maximized target window to improve button detection")
        return True
    except Exception as e:
        print(f"  ⚠ Failed to maximize window: {e}")
        return False


def _maybe_maximize_window(config: Dict[str, Any]) -> bool:
    """Maximize window only when configured to do so."""
    if not _should_maximize_on_first_fail(config):
        return False
    return _maximize_window(config)


def is_pyautogui_available() -> bool:
    """Check if PyAutoGUI is available for use

    Returns:
        True if PyAutoGUI is installed and available, False otherwise
    """
    return PYAUTOGUI_AVAILABLE


def _can_open_browser() -> bool:
    """Check if enough time has passed since the last browser open

    Returns:
        True if a browser can be opened (cooldown period has passed), False otherwise
    """
    global _last_browser_open_time
    if _last_browser_open_time is None:
        return True
    elapsed = time.time() - _last_browser_open_time
    return elapsed >= BROWSER_OPEN_COOLDOWN_SECONDS


def _record_browser_open() -> None:
    """Record the current time as the last browser open time"""
    global _last_browser_open_time
    _last_browser_open_time = time.time()


def _get_remaining_cooldown() -> float:
    """Get the remaining cooldown time in seconds

    Returns:
        Remaining seconds until next browser can be opened, or 0 if ready
    """
    global _last_browser_open_time
    if _last_browser_open_time is None:
        return 0.0
    elapsed = time.time() - _last_browser_open_time
    remaining = BROWSER_OPEN_COOLDOWN_SECONDS - elapsed
    return max(0.0, remaining)


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


def _activate_window_by_title(window_title: Optional[str], config: Dict[str, Any]) -> bool:
    """Activate a window by its title to bring it to the foreground

    Args:
        window_title: The title (or partial title) of the window to activate
        config: Configuration dict (currently unused, reserved for future options)

    Returns:
        True if window was found and activated, False otherwise

    Raises:
        SystemExit: If pygetwindow is not available when window_title is configured (fail-fast)
    """
    if not window_title:
        print("  ⚠ No window_title configured, skipping window activation")
        return False

    if not PYGETWINDOW_AVAILABLE or gw is None:
        error_msg = (
            "\n" + "=" * 80 + "\n"
            "ERROR: PyGetWindow library is not available\n" + "=" * 80 + "\n"
            "\nWindow activation is configured (window_title is set) but the required\n"
            "pygetwindow library is not installed.\n"
            "\nPlease install the required dependencies:\n"
            "  pip install -r requirements-automation.txt\n"
            "\nOr install pygetwindow directly:\n"
            "  pip install pygetwindow\n"
            "\nAlternatively, remove the 'window_title' setting from your config.toml\n"
            "if you don't need window activation.\n" + "=" * 80
        )
        print(error_msg)
        raise SystemExit(1)

    try:
        print(f"  → Looking for window with title containing: '{window_title}'")

        # Get all windows
        all_windows = gw.getAllWindows()

        # Find windows matching the title (case-insensitive partial match)
        matching_windows = [w for w in all_windows if window_title.lower() in w.title.lower()]

        if not matching_windows:
            print(f"  ⚠ No window found with title containing: '{window_title}'")
            print(f"     Available windows: {[w.title for w in all_windows[:10]]}")
            return False

        # Activate the first matching window
        target_window = matching_windows[0]
        print(f"  → Activating window: '{target_window.title}'")

        # Try to activate/restore the window
        if target_window.isMinimized:
            target_window.restore()

        target_window.activate()
        print("  ✓ Window activated successfully")
        return True

    except Exception as e:
        print(f"  ⚠ Failed to activate window: {e}")
        return False


def _validate_wait_seconds(config: Dict[str, Any]) -> int:
    """Validate and get wait_seconds from configuration

    Args:
        config: Configuration dict with wait_seconds setting

    Returns:
        Validated wait_seconds value (defaults to 10 if invalid)
    """
    try:
        wait_seconds = int(config.get("wait_seconds", 10))
        if wait_seconds < 0:
            print("  ⚠ wait_seconds must be positive, using default: 10")
            wait_seconds = 10
    except (ValueError, TypeError):
        print("  ⚠ Invalid wait_seconds value in config, using default: 10")
        wait_seconds = 10
    return wait_seconds


def _validate_confidence(config: Dict[str, Any]) -> float:
    """Validate and get confidence from configuration

    Args:
        config: Configuration dict with confidence setting

    Returns:
        Validated confidence value (defaults to 0.8 if invalid)
    """
    try:
        confidence = float(config.get("confidence", 0.8))
        if not 0.0 <= confidence <= 1.0:
            print("  ⚠ confidence must be between 0.0 and 1.0, using default: 0.8")
            confidence = 0.8
    except (ValueError, TypeError):
        print("  ⚠ Invalid confidence value in config, using default: 0.8")
        confidence = 0.8
    return confidence


def _validate_button_delay(config: Dict[str, Any]) -> float:
    """Validate and get button_delay from configuration

    Args:
        config: Configuration dict with button_delay setting

    Returns:
        Validated button_delay value in seconds (defaults to 2.0 if invalid)
    """
    try:
        button_delay = float(config.get("button_delay", 2.0))
        if button_delay < 0:
            print("  ⚠ button_delay must be positive, using default: 2.0")
            button_delay = 2.0
    except (ValueError, TypeError):
        print("  ⚠ Invalid button_delay value in config, using default: 2.0")
        button_delay = 2.0
    return button_delay


def _get_screenshot_path(button_name: str, config: Dict[str, Any]) -> Optional[Path]:
    """Get the path to the button screenshot image

    Args:
        button_name: Name of the button (e.g., "assign_to_copilot", "assign", "merge_pull_request")
        config: Configuration dict (assign_to_copilot or phase3_merge section) with screenshot_dir setting

    Returns:
        Path to the screenshot image, or None if not found
    """
    # Get screenshot directory from config, default to ./screenshots
    screenshot_dir_str = config.get("screenshot_dir", "screenshots")
    screenshot_dir = Path(screenshot_dir_str).expanduser().resolve()

    # Look for the screenshot with common image extensions
    for ext in [".png", ".jpg", ".jpeg"]:
        screenshot_path = screenshot_dir / f"{button_name}{ext}"
        if screenshot_path.exists():
            return screenshot_path

    return None


def _save_debug_info(button_name: str, confidence: float, config: Dict[str, Any]) -> None:
    """Save debug information when image recognition fails

    This function saves:
    1. Full screenshot of current screen
    2. Top 3 candidate locations (if any found with lower confidence)
    3. JSON metadata with all information

    Args:
        button_name: Name of the button that failed to be found
        confidence: Confidence threshold that was used
        config: Configuration dict with debug_dir setting
    """
    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        return

    # Get debug directory from config, default to ./debug_screenshots
    debug_dir_str = config.get("debug_dir", "debug_screenshots")
    debug_dir = Path(debug_dir_str).expanduser().resolve()

    # Create debug directory if it doesn't exist
    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"  ⚠ Could not create debug directory '{debug_dir}': {e}")
        return

    # Generate timestamp once for consistency between filename and JSON
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds for uniqueness

    # Take screenshot of current screen
    screenshot_filename = f"{button_name}_fail_{timestamp}.png"
    screenshot_path = debug_dir / screenshot_filename

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(str(screenshot_path))
        print(f"  ℹ Debug screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"  ⚠ Could not save debug screenshot: {e}")
        return

    # Get template screenshot path and handle None case
    template_path = _get_screenshot_path(button_name, config)
    template_screenshot = str(template_path) if template_path else None

    # Try to find candidate matches with lower confidence threshold
    candidates = []
    if template_path:
        try:
            # Try multiple confidence levels to find potential matches
            for test_confidence in DEBUG_CANDIDATE_CONFIDENCE_THRESHOLDS:
                # Only try confidence levels lower than the original threshold
                if test_confidence >= confidence:
                    continue

                print(f"  → Searching for candidates with confidence {test_confidence}...")
                all_locations = list(pyautogui.locateAllOnScreen(str(template_path), confidence=test_confidence))

                if all_locations:
                    print(f"  ℹ Found {len(all_locations)} candidate(s) with confidence {test_confidence}")
                    # Save up to DEBUG_MAX_CANDIDATES candidates at this confidence level
                    for idx, loc in enumerate(all_locations[:DEBUG_MAX_CANDIDATES]):
                        candidate_info = {
                            "confidence_used": test_confidence,
                            "left": loc.left,
                            "top": loc.top,
                            "width": loc.width,
                            "height": loc.height,
                        }
                        candidates.append(candidate_info)

                        # Save cropped image of the candidate region
                        try:
                            candidate_img = screenshot.crop(
                                (loc.left, loc.top, loc.left + loc.width, loc.top + loc.height)
                            )
                            candidate_filename = f"{button_name}_candidate_{timestamp}_{len(candidates)}.png"
                            candidate_path = debug_dir / candidate_filename
                            candidate_img.save(str(candidate_path))
                            candidate_info["image_path"] = str(candidate_path)
                            print(f"  ℹ Saved candidate #{len(candidates)}: {candidate_path}")
                        except Exception as e:
                            print(f"  ⚠ Could not save candidate image: {e}")

                    # Stop after finding candidates
                    if len(candidates) >= DEBUG_MAX_CANDIDATES:
                        break

        except Exception as e:
            print(f"  ⚠ Error searching for candidates: {e}")

    # Save failure information to JSON
    json_filename = f"{button_name}_fail_{timestamp}.json"
    json_path = debug_dir / json_filename

    failure_info = {
        "button_name": button_name,
        "timestamp": now.isoformat(),  # Use the same datetime object for consistency
        "confidence": confidence,
        "screenshot_path": str(screenshot_path),
        "template_screenshot": template_screenshot,
        "candidates_found": len(candidates),
        "candidates": candidates,
    }

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(failure_info, f, indent=2, ensure_ascii=False)
        print(f"  ℹ Debug info saved: {json_path}")
        if candidates:
            print(f"  ℹ Found {len(candidates)} potential candidate(s) - check debug directory for details")
    except Exception as e:
        print(f"  ⚠ Could not save debug info JSON: {e}")


def _click_button_with_ocr(button_name: str, config: Dict[str, Any]) -> bool:
    """Find and click a button using OCR text detection

    This is a fallback method when image recognition fails. It uses OCR
    to find text on screen and click buttons by their text content.

    Args:
        button_name: Name of the button (e.g., "assign_to_copilot", "assign")
        config: Configuration dict with automation settings

    Returns:
        True if button was found and clicked, False otherwise
    """
    if not PYTESSERACT_AVAILABLE or pytesseract is None:
        print("  ℹ pytesseract is not available for OCR-based button detection")
        return False

    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        print("  ℹ PyAutoGUI is required for OCR-based button detection")
        return False

    # OCR detection is enabled by default (True) to serve as a fallback when image recognition fails
    if not config.get("enable_ocr_detection", True):
        print("  ℹ OCR-based detection is disabled")
        return False

    # Map button names to the text we're looking for
    button_text_map = {
        "assign_to_copilot": "Assign to Copilot",
        "assign": "Assign",
        "merge_pull_request": "Merge pull request",
        "confirm_merge": "Confirm merge",
        "delete_branch": "Delete branch",
    }

    target_text = button_text_map.get(button_name)
    if not target_text:
        print(f"  ⚠ Unknown button name '{button_name}' for OCR detection")
        return False

    try:
        print(f"  → Attempting OCR-based detection for '{target_text}' button...")

        # Take a screenshot
        screenshot = pyautogui.screenshot()

        # Use pytesseract to get bounding boxes of all text
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        # Search for the target text in the OCR results
        n_boxes = len(data["text"])
        found_regions = []

        # Look for consecutive words that match our target text
        target_words = target_text.lower().split()

        for i in range(n_boxes):
            text = data["text"][i].lower().strip()
            if not text:
                continue

            # Check if we found the start of our target phrase
            if text == target_words[0]:
                # Try to match all consecutive words
                matches = [i]
                for j, target_word in enumerate(target_words[1:], start=1):
                    if i + j < n_boxes:
                        next_text = data["text"][i + j].lower().strip()
                        if next_text == target_word:
                            matches.append(i + j)
                        else:
                            break
                    else:
                        break

                # If we matched all words, we found the button text
                if len(matches) == len(target_words):
                    # Calculate bounding box for all matched words
                    xs = [data["left"][idx] for idx in matches]
                    ys = [data["top"][idx] for idx in matches]
                    ws = [data["width"][idx] for idx in matches]
                    hs = [data["height"][idx] for idx in matches]

                    left = min(xs)
                    top = min(ys)
                    right = max(x + w for x, w in zip(xs, ws))
                    bottom = max(y + h for y, h in zip(ys, hs))

                    # Expand the region to account for button padding
                    region = {
                        "left": max(0, left - OCR_BUTTON_PADDING),
                        "top": max(0, top - OCR_BUTTON_PADDING),
                        "right": min(screenshot.width, right + OCR_BUTTON_PADDING),
                        "bottom": min(screenshot.height, bottom + OCR_BUTTON_PADDING),
                    }
                    found_regions.append(region)

        if not found_regions:
            print(f"  ✗ Text '{target_text}' not found using OCR")
            return False

        # Use the first found region (or could use heuristics to pick the best one)
        region = found_regions[0]
        center_x = int((region["left"] + region["right"]) / 2)
        center_y = int((region["top"] + region["bottom"]) / 2)

        print(f"  → Found '{target_text}' at position ({center_x}, {center_y})")

        # Click the button
        time.sleep(0.5)  # Brief pause before clicking
        pyautogui.click(center_x, center_y)
        print(f"  ✓ Clicked '{target_text}' button using OCR detection")

        return True

    except Exception as e:
        print(f"  ⚠ OCR-based detection failed: {e}")
        return False


def _click_button_with_image(button_name: str, config: Dict[str, Any]) -> bool:
    """Find and click a button using image recognition

    Args:
        button_name: Name of the button screenshot file (without extension)
        config: Configuration dict with screenshot settings (including optional confidence)

    Returns:
        True if button was found and clicked, False otherwise

    Note:
        Uses image recognition to find and click buttons on screen. The first matching
        button found on the entire screen will be clicked. Ensure the correct GitHub
        browser window/tab is focused and visible before running this function.

        When image recognition fails, debug information (screenshot and failure details)
        will be saved to the debug_dir directory (default: ./debug_screenshots).
    """
    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        print("  ✗ PyAutoGUI is not available")
        return False

    screenshot_path = _get_screenshot_path(button_name, config)
    if screenshot_path is None:
        print(f"  ✗ Screenshot not found for button '{button_name}'")
        print(f"     Please save a screenshot as '{button_name}.png' in the screenshots directory")
        print("     See README.ja.md for instructions")
        return False

    # Get confidence from config
    confidence = _validate_confidence(config)

    try:
        print(f"  → Looking for button using screenshot: {screenshot_path}")
        print(
            "  ⚠ Make sure the correct GitHub browser window/tab is focused "
            "because the first matching button on the entire screen will be clicked."
        )
        location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

        if location is None:
            if _maybe_maximize_window(config):
                time.sleep(0.5)  # Allow layout to settle after maximizing
                location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

        if location is None:
            print(f"  ✗ Could not find button '{button_name}' on screen with image recognition")
            print("     Trying fallback methods...")
            # Save debug information for troubleshooting
            _save_debug_info(button_name, confidence, config)

            # Try OCR-based detection as fallback
            print("  → Attempting OCR fallback...")
            if _click_button_with_ocr(button_name, config):
                return True

            print(f"  ✗ All detection methods failed for button '{button_name}'")
            return False

        # Click in the center of the found button
        center = pyautogui.center(location)
        time.sleep(0.5)  # Brief pause before clicking
        pyautogui.click(center)
        print(f"  ✓ Clicked button '{button_name}' at position {center}")
        return True

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_name}': {e}")
        print("     This may occur if running in a headless environment, SSH session without display,")
        print("     or if the screen is locked. PyAutoGUI requires an active display.")
        # Save debug information even on exception
        try:
            _save_debug_info(button_name, confidence, config)
        except Exception:
            pass  # Silently ignore errors in debug info saving
        return False


def assign_issue_to_copilot_automated(issue_url: str, config: Optional[Dict[str, Any]] = None) -> bool:
    """Automatically assign an issue to Copilot by clicking buttons in browser

    This function uses PyAutoGUI with image recognition to:
    1. Open the issue in a browser (requires an already-authenticated browser session)
    2. Wait for the configured time (default 10 seconds)
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

    # Validate and get configuration values
    wait_seconds = _validate_wait_seconds(assign_config)
    button_delay = _validate_button_delay(assign_config)
    notification: Optional[NotificationWindow] = None

    print("  → [PyAutoGUI] Opening issue in browser...")
    print("  ℹ Ensure you are already logged into GitHub in your default browser")

    # Determine if window should be raised to foreground
    autoraise = _should_autoraise_window(config)
    notification = _start_button_notification(assign_config, DEFAULT_ASSIGN_NOTIFICATION_MESSAGE)

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
        time.sleep(wait_seconds)

        # Activate window if window_title is configured (1 second before clicking buttons)
        window_title = assign_config.get("window_title")
        if window_title:
            print("  → Waiting 1 second before activating window...")
            time.sleep(1)  # Wait 1 second before activating window
            _activate_window_by_title(window_title, assign_config)

        # Click "Assign to Copilot" button
        print("  → Looking for 'Assign to Copilot' button...")
        if not _click_button_with_image("assign_to_copilot", assign_config):
            print("  ✗ Could not find or click 'Assign to Copilot' button")
            return False

        print("  ✓ Clicked 'Assign to Copilot' button")

        # Wait for the assignment UI to appear
        print(f"  → Waiting {button_delay} seconds for UI to respond...")
        time.sleep(button_delay)

        # Click "Assign" button
        print("  → Looking for 'Assign' button...")
        if not _click_button_with_image("assign", assign_config):
            print("  ✗ Could not find or click 'Assign' button")
            return False

        print("  ✓ Clicked 'Assign' button")
        print("  ✓ [PyAutoGUI] Successfully automated issue assignment to Copilot")

        # Wait before finishing
        time.sleep(button_delay)

        return True
    finally:
        _close_notification_window(notification)


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
    notification = _start_button_notification(merge_config, DEFAULT_MERGE_NOTIFICATION_MESSAGE)

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
        time.sleep(wait_seconds)

        # Activate window if window_title is configured (1 second before clicking buttons)
        window_title = merge_config.get("window_title")
        if window_title:
            print("  → Waiting 1 second before activating window...")
            time.sleep(1)  # Wait 1 second before activating window
            _activate_window_by_title(window_title, merge_config)

        # Click "Merge pull request" button
        print("  → Looking for 'Merge pull request' button...")
        if not _click_button_with_image("merge_pull_request", merge_config):
            print("  ✗ Could not find or click 'Merge pull request' button")
            return False

        print("  ✓ Clicked 'Merge pull request' button")

        # Wait for the confirmation UI to appear
        print(f"  → Waiting {button_delay} seconds for UI to respond...")
        time.sleep(button_delay)

        # Click "Confirm merge" button
        print("  → Looking for 'Confirm merge' button...")
        if not _click_button_with_image("confirm_merge", merge_config):
            print("  ✗ Could not find or click 'Confirm merge' button")
            return False

        print("  ✓ Clicked 'Confirm merge' button")

        # Wait for merge to complete and delete branch button to appear
        print(f"  → Waiting {button_delay + 1.0} seconds for merge to complete...")
        time.sleep(button_delay + 1.0)

        # Click "Delete branch" button (optional - don't fail if not found)
        print("  → Looking for 'Delete branch' button...")
        if not _click_button_with_image("delete_branch", merge_config):
            print("  ⚠ Could not find or click 'Delete branch' button (may have already been deleted)")
        else:
            print("  ✓ Clicked 'Delete branch' button")

        print("  ✓ [PyAutoGUI] Successfully automated PR merge")

        # Wait before finishing
        time.sleep(button_delay)

        return True
    finally:
        _close_notification_window(notification)
