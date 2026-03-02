"""Button clicker module for browser automation

Provides utilities for finding and clicking buttons on screen using
image recognition (PyAutoGUI) with OCR fallback (pytesseract).
"""

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .click_config_validator import (
    _get_screenshot_path,
    _validate_button_delay,  # noqa: F401 (re-exported for backward compatibility)
    _validate_confidence,
    _validate_wait_seconds,  # noqa: F401 (re-exported for backward compatibility)
)
from .window_manager import _maybe_maximize_window

# PyAutoGUI imports are optional - will be imported only if automation is enabled
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None  # Set to None when not available

# pytesseract imports are optional - for OCR-based button detection fallback
try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    pytesseract = None
    # Note: PIL.Image is imported locally in _click_button_with_ocr when needed

# Track whether the notification window was explicitly closed by the user
_user_cancelled_notification = False


def set_user_cancelled_notification() -> None:
    """Set the user-cancelled flag (call this when the notification window is closed by the user)."""
    global _user_cancelled_notification
    _user_cancelled_notification = True


def reset_user_cancelled_notification() -> None:
    """Reset the user-cancelled flag (call this before starting a new automation sequence)."""
    global _user_cancelled_notification
    _user_cancelled_notification = False


# Debug candidate detection settings
# These thresholds are only used when image recognition fails with the original confidence threshold
# The search stops after finding DEBUG_MAX_CANDIDATES candidates
DEBUG_CANDIDATE_CONFIDENCE_THRESHOLDS = [0.7, 0.6, 0.5]  # Try these confidence levels for debug candidates
DEBUG_MAX_CANDIDATES = 3  # Maximum number of candidate regions to save for debugging

# OCR detection settings
OCR_BUTTON_PADDING = 20  # Pixels to add around detected text to account for button borders


def _log_error(message: str, exc: Exception | BaseException | None = None) -> None:
    """Append an error entry to logs/error.log without raising further exceptions."""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        from datetime import UTC

        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception as log_exc:
        print(
            f"[button_clicker._log_error] Failed to write to error.log: {log_exc!r} (original message: {message})",
            file=sys.stderr,
        )


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
        _log_error(f"Failed to capture debug screenshot for '{button_name}'", e)
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


def _click_button_with_image(
    button_name: str,
    config: Dict[str, Any],
    *,
    max_attempts: int = 1,
    poll_interval: float = 0.0,
    pre_click_delay: float = 0.5,
) -> bool:
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

    if _user_cancelled_notification:
        print("  ⚠ Notification window was closed by user; skipping button search")
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
        attempts = max(1, max_attempts)
        has_maximized = False
        for attempt in range(attempts):
            print(f"  → Looking for button using screenshot: {screenshot_path}")
            print(
                "  ⚠ Make sure the correct GitHub browser window/tab is focused "
                "because the first matching button on the entire screen will be clicked."
            )
            location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

            if location is None and not has_maximized:
                if _maybe_maximize_window(config):
                    has_maximized = True
                    time.sleep(0.5)  # Allow layout to settle after maximizing
                    location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

            if location is None and attempt < attempts - 1:
                if _user_cancelled_notification:
                    print("  ⚠ Notification window was closed by user; skipping button search")
                    return False
                if poll_interval > 0:
                    time.sleep(poll_interval)
                continue

            if location is None:
                if _user_cancelled_notification:
                    print("  ⚠ Notification window was closed by user; skipping button search")
                    return False
                print(f"  ✗ Could not find button '{button_name}' on screen with image recognition")
                print("     Trying fallback methods...")
                # Save debug information for troubleshooting
                try:
                    _save_debug_info(button_name, confidence, config)
                except Exception as debug_exc:  # noqa: BLE001
                    _log_error(f"Failed to save debug info for '{button_name}' after image search miss", debug_exc)

                # Try OCR-based detection as fallback
                print("  → Attempting OCR fallback...")
                if _click_button_with_ocr(button_name, config):
                    return True

                print(f"  ✗ All detection methods failed for button '{button_name}'")
                return False

            # Re-verify just before clicking to avoid stale coordinates, then click immediately
            verification_location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)
            if verification_location is None:
                print(f"  ✗ Button '{button_name}' not found during final verification; skipping click")
                return False
            center = pyautogui.center(verification_location)
            if _user_cancelled_notification:
                print("  ⚠ Notification window was closed by user; skipping button search")
                return False
            if pre_click_delay > 0:
                time.sleep(pre_click_delay)
            pyautogui.click(center)
            print(f"  ✓ Clicked button '{button_name}' at position {center}")
            return True

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_name}': {e}")
        print("     This may occur if running in a headless environment, SSH session without display,")
        print("     or if the screen is locked. PyAutoGUI requires an active display.")
        _log_error(f"Button click failed for '{button_name}'", e)
        # Save debug information even on exception
        try:
            _save_debug_info(button_name, confidence, config)
        except Exception as debug_exc:
            _log_error(f"Failed to save debug info for '{button_name}' after exception", debug_exc)
        return False
