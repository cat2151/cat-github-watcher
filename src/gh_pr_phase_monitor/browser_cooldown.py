"""Browser open cooldown tracking

Tracks the last time a browser was opened to prevent multiple pages
from being opened simultaneously during automated operations.
"""

import time
from typing import Optional

# Global state to track the last time a browser was opened
# This prevents opening multiple pages simultaneously which can cause issues
# with automated merge and assign operations
_last_browser_open_time: Optional[float] = None

# Minimum time (in seconds) to wait between opening browser pages
BROWSER_OPEN_COOLDOWN_SECONDS = 60


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
