"""
Unit tests for LLM status timestamp parsing and latest-activity lookup.

Covers:
  - _parse_timestamp_from_status_text()
  - get_latest_activity_timestamp()
"""

import time
from datetime import datetime, timedelta, timezone

from src.gh_pr_phase_monitor.phase.html.llm_status_extractor import (
    _parse_timestamp_from_status_text,
    get_latest_activity_timestamp,
)


class TestParseTimestampFromStatusText:
    """Unit tests for _parse_timestamp_from_status_text()"""

    def test_parses_full_date_format(self):
        """Should parse 'Month DD, YYYY HH:MM' embedded in a status string"""
        text = "Copilot started work on behalf of cat2151 March 7, 2026 10:01"
        ts = _parse_timestamp_from_status_text(text)
        assert ts is not None
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        assert dt.year == 2026
        assert dt.month == 3
        assert dt.day == 7
        assert dt.hour == 10
        assert dt.minute == 1

    def test_parses_without_comma_after_day(self):
        """Should parse 'Month DD YYYY HH:MM' (no comma after day)"""
        text = "Copilot started work on behalf of user January 15 2025 09:30"
        ts = _parse_timestamp_from_status_text(text)
        assert ts is not None
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        assert dt.year == 2025
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 9
        assert dt.minute == 30

    def test_returns_none_for_text_without_date(self):
        """Should return None when no date is present"""
        assert _parse_timestamp_from_status_text("started work") is None
        assert _parse_timestamp_from_status_text("Copilot started work on behalf of user") is None
        assert _parse_timestamp_from_status_text("") is None

    def test_all_months_parseable(self):
        """All twelve month names should be recognised"""
        months = [
            ("January", 1), ("February", 2), ("March", 3), ("April", 4),
            ("May", 5), ("June", 6), ("July", 7), ("August", 8),
            ("September", 9), ("October", 10), ("November", 11), ("December", 12),
        ]
        for month_name, month_num in months:
            text = f"started work {month_name} 1, 2026 00:00"
            ts = _parse_timestamp_from_status_text(text)
            assert ts is not None, f"Failed to parse month: {month_name}"
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            assert dt.month == month_num


class TestGetLatestActivityTimestamp:
    """Unit tests for get_latest_activity_timestamp()"""

    def _make_status(self, label: str, seconds_ago: float) -> str:
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        month_name = dt.strftime("%B")
        return f"Copilot {label} on behalf of cat2151 {month_name} {dt.day}, {dt.year} {dt.strftime('%H:%M')}"

    def test_returns_none_for_empty_list(self):
        assert get_latest_activity_timestamp([]) is None

    def test_returns_none_when_no_entry_has_timestamp(self):
        """Entries without an embedded date return None."""
        statuses = ["Copilot finished work on behalf of user"]
        assert get_latest_activity_timestamp(statuses) is None

    def test_returns_timestamp_for_started_work(self):
        """'started work' with an embedded date is a valid activity timestamp."""
        status = self._make_status("started work", 120)  # 2 minutes ago
        ts = get_latest_activity_timestamp([status])
        assert ts is not None
        assert abs(time.time() - ts - 120) < 65  # within 1 minute of expected (rounding)

    def test_returns_timestamp_for_started_reviewing(self):
        """'started reviewing' with an embedded date is also a valid activity timestamp."""
        status = self._make_status("started reviewing", 120)  # 2 minutes ago
        ts = get_latest_activity_timestamp([status])
        assert ts is not None
        assert abs(time.time() - ts - 120) < 65

    def test_returns_none_when_no_status_has_timestamp(self):
        """If no status entry contains a parseable date, return None."""
        assert get_latest_activity_timestamp(["started work"]) is None

    def test_returns_latest_when_multiple_entries(self):
        """Should return the timestamp of the most recent entry."""
        older = self._make_status("started work", 7200)  # 2 hours ago
        newer = self._make_status("started work on feedback", 300)  # 5 minutes ago
        ts = get_latest_activity_timestamp([older, newer])
        assert ts is not None
        # Should be closer to 5 minutes ago than 2 hours ago
        assert abs(time.time() - ts - 300) < 65

    def test_returns_latest_across_mixed_event_types(self):
        """The newest timestamp wins regardless of event type."""
        older_started = self._make_status("started work", 7200)  # 2 hours ago
        newer_reviewing = self._make_status("started reviewing", 300)  # 5 minutes ago
        ts = get_latest_activity_timestamp([older_started, newer_reviewing])
        assert ts is not None
        assert abs(time.time() - ts - 300) < 65
