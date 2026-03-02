"""Tests for rate limit throttle detection in _check_rate_limit_throttle."""

import time

from src.gh_pr_phase_monitor.main import _check_rate_limit_throttle


def _make_rate_limit(remaining: int, reset_offset: int = 3600, limit: int = 5000) -> dict:
    """Create a rate limit dict with reset set `reset_offset` seconds from now."""
    return {
        "remaining": remaining,
        "limit": limit,
        "used": limit - remaining,
        "reset": int(time.time()) + reset_offset,
    }


def test_no_throttle_when_consumption_fits_in_remaining():
    # Consumed 10 per iteration, reset in 3600s, interval 60s → 60 iterations
    # Projected consumption = 10 * 60 = 600 < remaining 5000
    before = _make_rate_limit(remaining=5000, reset_offset=3600)
    after = _make_rate_limit(remaining=4990, reset_offset=3600)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert not should_throttle
    assert interval == 60


def test_throttle_when_consumption_would_exhaust_before_reset():
    # Consumed 100 per iteration, reset in 3600s, interval 60s → 60 iterations
    # Projected consumption = 100 * 60 = 6000 > remaining 1000
    before = _make_rate_limit(remaining=1100, reset_offset=3600)
    after = _make_rate_limit(remaining=1000, reset_offset=3600)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert should_throttle
    # Throttled interval >= 2 * normal_interval_seconds
    assert interval >= 120


def test_throttle_recommends_at_least_double_normal_interval():
    # Barely over limit - recommended interval should be at least 2x normal
    before = _make_rate_limit(remaining=200, reset_offset=3600)
    after = _make_rate_limit(remaining=100, reset_offset=3600)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert should_throttle
    assert interval >= 120


def test_throttle_capped_at_600_seconds():
    # Extreme case: very high consumption rate
    before = _make_rate_limit(remaining=1000, reset_offset=3600)
    after = _make_rate_limit(remaining=500, reset_offset=3600)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert should_throttle
    assert interval <= 600


def test_no_throttle_when_no_consumption():
    before = _make_rate_limit(remaining=5000)
    after = _make_rate_limit(remaining=5000)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert not should_throttle
    assert interval == 60


def test_no_throttle_when_before_is_none():
    after = _make_rate_limit(remaining=100)
    should_throttle, interval = _check_rate_limit_throttle(None, after, normal_interval_seconds=60)
    assert not should_throttle
    assert interval == 60


def test_no_throttle_when_after_is_none():
    before = _make_rate_limit(remaining=5000)
    should_throttle, interval = _check_rate_limit_throttle(before, None, normal_interval_seconds=60)
    assert not should_throttle
    assert interval == 60


def test_no_throttle_when_reset_already_passed():
    # reset in the past
    before = {"remaining": 200, "reset": int(time.time()) - 100}
    after = {"remaining": 100, "reset": int(time.time()) - 100}
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert not should_throttle
    assert interval == 60


def test_no_throttle_when_negative_consumed_after_reset():
    # After value is higher than before (rate limit window reset between calls)
    before = _make_rate_limit(remaining=100)
    after = _make_rate_limit(remaining=4900)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert not should_throttle
    assert interval == 60


def test_throttle_caps_at_600_when_remaining_is_zero():
    # remaining=0: should immediately return max throttle (600s)
    before = _make_rate_limit(remaining=50, reset_offset=3600)
    after = _make_rate_limit(remaining=0, reset_offset=3600)
    should_throttle, interval = _check_rate_limit_throttle(before, after, normal_interval_seconds=60)
    assert should_throttle
    assert interval == 600
