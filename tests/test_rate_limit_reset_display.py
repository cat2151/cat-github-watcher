from datetime import UTC, datetime

from src.gh_pr_phase_monitor.main import _format_rate_limit_reset


def test_format_rate_limit_reset_formats_utc_and_remaining_time():
    now = datetime(2026, 3, 1, 0, 0, 0, tzinfo=UTC)
    reset = now.timestamp() + 125  # 2分5秒

    reset_display, reset_in_display = _format_rate_limit_reset(reset, now=now)

    assert reset_display == "2026-03-01 00:02:05 UTC"
    assert reset_in_display == "2分5秒"


def test_format_rate_limit_reset_returns_zero_for_past_reset():
    now = datetime(2026, 3, 1, 0, 0, 10, tzinfo=UTC)
    reset = now.timestamp() - 5

    reset_display, reset_in_display = _format_rate_limit_reset(reset, now=now)

    assert reset_display == "2026-03-01 00:00:05 UTC"
    assert reset_in_display == "0秒"


def test_format_rate_limit_reset_returns_unknown_for_invalid_reset():
    reset_display, reset_in_display = _format_rate_limit_reset("not-a-number")

    assert reset_display == "unknown"
    assert reset_in_display == "unknown"
