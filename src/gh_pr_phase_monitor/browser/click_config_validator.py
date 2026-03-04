"""Configuration validation and screenshot path utilities for button clicking.

Provides helper functions for validating button-clicking configuration values
and resolving screenshot file paths.
"""

from pathlib import Path
from typing import Any, Dict, Optional


def _validate_wait_seconds(config: Dict[str, Any], default: int = 10) -> int:
    """Validate and get wait_seconds from configuration

    Args:
        config: Configuration dict with wait_seconds setting
        default: Default wait time to fall back to when invalid

    Returns:
        Validated wait_seconds value (defaults to provided value if invalid)
    """
    try:
        wait_seconds = int(config.get("wait_seconds", default))
        if wait_seconds < 0:
            print(f"  ⚠ wait_seconds must be positive, using default: {default}")
            wait_seconds = default
    except (ValueError, TypeError):
        print(f"  ⚠ Invalid wait_seconds value in config, using default: {default}")
        wait_seconds = default
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
