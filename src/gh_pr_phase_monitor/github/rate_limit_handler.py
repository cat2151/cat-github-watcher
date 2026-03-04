"""
Rate limit handling utilities for GitHub PR Phase Monitor.

Provides functions for monitoring GraphQL API rate limits, displaying usage
statistics, and throttling requests when approaching rate limit exhaustion.
"""

import math
import time
from datetime import UTC, datetime
from typing import Any

from ..core.time_utils import format_elapsed_time

MAX_RATE_LIMIT_THROTTLE_SECONDS = 600


def _format_rate_limit_reset(reset: Any, now: datetime | None = None) -> tuple[str, str]:
    """Format rate-limit reset epoch into UTC datetime and remaining duration."""
    if not isinstance(reset, (int, float)):
        return "unknown", "unknown"

    current = now or datetime.now(UTC)
    reset_dt = datetime.fromtimestamp(float(reset), UTC)
    remaining_seconds = max(0, int(reset_dt.timestamp() - current.timestamp()))
    return reset_dt.strftime("%Y-%m-%d %H:%M:%S UTC"), format_elapsed_time(remaining_seconds)


def _display_rate_limit_usage(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> None:
    """Display GraphQL API usage breakdown for this iteration."""
    if not after:
        return

    remaining = after.get("remaining", "?")
    limit = after.get("limit", "?")
    reset = after.get("reset")
    reset_display, reset_in_display = _format_rate_limit_reset(reset)
    status = f"残={remaining}/{limit}, リセット={reset_display} (あと{reset_in_display})"

    if before is not None and isinstance(before.get("remaining"), int) and isinstance(after.get("remaining"), int):
        raw_consumed = before["remaining"] - after["remaining"]
        if raw_consumed < 0:
            # レートリミットウィンドウがリセットされ、単純差分が負になるケース
            consumed = 0
            reset_note = " (リセット後)"
        else:
            consumed = raw_consumed
            reset_note = ""
        print(f"\nGraphQL API使用状況: 今回消費={consumed}点{reset_note}, {status}")
    else:
        print(f"\nGraphQL API使用状況: {status}")


def _check_rate_limit_throttle(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    normal_interval_seconds: int,
) -> tuple[bool, int]:
    """Check if the current rate limit consumption rate requires interval throttling.

    Calculates whether continuing at the current consumption rate would exhaust
    the GraphQL rate limit before the next reset window.

    Args:
        before: Rate limit info captured before API calls
        after: Rate limit info captured after API calls
        normal_interval_seconds: The configured normal monitoring interval

    Returns:
        Tuple of (should_throttle, recommended_interval_seconds).
        If should_throttle is False, recommended_interval_seconds equals normal_interval_seconds.
    """
    if not (before and after):
        return False, normal_interval_seconds

    remaining = after.get("remaining")
    reset = after.get("reset")
    if not isinstance(remaining, int) or not isinstance(reset, (int, float)):
        return False, normal_interval_seconds

    if not isinstance(before.get("remaining"), int):
        return False, normal_interval_seconds

    consumed = before["remaining"] - after["remaining"]
    if consumed <= 0:
        return False, normal_interval_seconds

    now = time.time()
    reset_seconds = max(0, int(reset) - now)
    if reset_seconds <= 0 or normal_interval_seconds <= 0:
        return False, normal_interval_seconds

    # Estimate how many more iterations until reset
    iterations_until_reset = reset_seconds / normal_interval_seconds
    projected_consumption = consumed * iterations_until_reset

    if projected_consumption <= remaining:
        return False, normal_interval_seconds

    # When remaining is 0, cap immediately at maximum throttle
    if remaining <= 0:
        return True, MAX_RATE_LIMIT_THROTTLE_SECONDS

    # Calculate the minimum safe interval to avoid exhausting the rate limit
    # safe_interval = reset_seconds / (remaining / consumed) = reset_seconds * consumed / remaining
    # Use ceil to round up so we never under-estimate the required interval
    safe_interval_seconds = math.ceil(reset_seconds * consumed / remaining)
    # Use at least 2x the normal interval to avoid micro-adjustments
    throttled_interval = max(normal_interval_seconds * 2, safe_interval_seconds)
    # Cap at max throttle to prevent excessively long waits
    throttled_interval = min(throttled_interval, MAX_RATE_LIMIT_THROTTLE_SECONDS)

    return True, throttled_interval
