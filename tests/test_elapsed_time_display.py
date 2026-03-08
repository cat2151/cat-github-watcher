"""
Test to verify that elapsed time is displayed correctly for unchanged PR states

This test ensures the new behavior requested in the issue:
"If the display content is exactly the same as before, change the display content
to show something like '現在、検知してから3分20秒経過' (Currently, 3 minutes 20 seconds have elapsed since detection)"
"""

import time
from datetime import datetime, timedelta, timezone

from src.gh_pr_phase_monitor.ui.display import display_status_summary
from src.gh_pr_phase_monitor.phase.phase_detector import PHASE_1, PHASE_LLM_WORKING
from src.gh_pr_phase_monitor.monitor.state_tracker import _pr_state_times
from src.gh_pr_phase_monitor.core.time_utils import format_elapsed_time
from src.gh_pr_phase_monitor.ui.wait_handler import wait_with_countdown
from src.gh_pr_phase_monitor.phase.html.llm_status_extractor import (
    get_latest_activity_timestamp,
    _parse_timestamp_from_status_text,
)


class TestElapsedTimeDisplay:
    """Test the elapsed time display functionality"""

    def setup_method(self):
        """Reset PR state times before each test"""
        _pr_state_times.clear()

    def test_format_elapsed_time_seconds_only(self):
        """Test formatting elapsed time when less than a minute"""
        assert format_elapsed_time(0) == "0秒"
        assert format_elapsed_time(30) == "30秒"
        assert format_elapsed_time(59) == "59秒"

    def test_format_elapsed_time_minutes_and_seconds(self):
        """Test formatting elapsed time with minutes and seconds"""
        assert format_elapsed_time(60) == "1分0秒"
        assert format_elapsed_time(90) == "1分30秒"
        assert format_elapsed_time(200) == "3分20秒"
        assert format_elapsed_time(3661) == "61分1秒"

    def test_elapsed_time_not_shown_for_new_prs(self, mocker):
        """Test that elapsed time is not shown for PRs detected for less than 60 seconds"""
        # Create mock PR data
        all_prs = [
            {
                "title": "New PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        # Verify that elapsed time is NOT displayed (PR is new)
        assert "経過" not in output
        assert "New PR" in output

    def test_elapsed_time_shown_after_60_seconds(self, mocker):
        """Test that elapsed time is shown for PRs in same state for more than 60 seconds"""
        # Create mock PR data
        all_prs = [
            {
                "title": "Old PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        # First call to set the initial detection time
        mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Manually adjust the detection time to simulate 200 seconds elapsed
        state_key = ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING)
        _pr_state_times[state_key] = time.time() - 200

        # Second call should show elapsed time
        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        # Verify that elapsed time IS displayed
        assert "現在、検知してから" in output
        assert "経過" in output
        assert "3分" in output  # Should be around 3 minutes

    def test_elapsed_time_resets_when_phase_changes(self, mocker):
        """Test that elapsed time tracking resets when PR phase changes"""
        # Create mock PR data
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]

        # First call with PHASE_LLM_WORKING
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify that state was tracked
        state_key_1 = ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING)
        assert state_key_1 in _pr_state_times

        # Simulate phase change by calling with a different phase
        pr_phases = [PHASE_1]
        mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify that old state was cleaned up and new state was tracked
        state_key_2 = ("https://github.com/owner/repo1/pulls/1", PHASE_1)
        assert state_key_1 not in _pr_state_times
        assert state_key_2 in _pr_state_times

    def test_cleanup_removes_old_pr_states(self, mocker):
        """Test that cleanup removes states for PRs that no longer exist"""
        # Create mock PR data
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
            },
        ]
        pr_phases = [PHASE_LLM_WORKING, PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 2}]

        # First call to track both PRs
        mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify both PRs are tracked
        assert len(_pr_state_times) == 2

        # Second call with only one PR
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]

        mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Verify only one PR is now tracked (cleanup removed the other)
        assert len(_pr_state_times) == 1
        assert ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING) in _pr_state_times

    def test_elapsed_time_shown_at_exactly_60_seconds(self, mocker):
        """Test that elapsed time is shown when exactly 60 seconds have elapsed (boundary condition)"""
        # Create mock PR data
        all_prs = [
            {
                "title": "PR at boundary",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        # First call to set the initial detection time
        mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Manually adjust the detection time to simulate exactly 60 seconds elapsed
        state_key = ("https://github.com/owner/repo1/pulls/1", PHASE_LLM_WORKING)
        _pr_state_times[state_key] = time.time() - 60

        # Second call should show elapsed time since it's >= 60
        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        # Verify that elapsed time IS displayed at the boundary
        assert "現在、検知してから" in output
        assert "経過" in output
        assert "1分0秒" in output  # Should be exactly 1 minute


class TestLLMWorkingCreatedAtWarning:
    """Test the warning display for LLM working PRs older than 30 minutes since creation"""

    def setup_method(self):
        """Reset PR state times before each test"""
        _pr_state_times.clear()

    def _make_created_at(self, seconds_ago: float) -> str:
        """Return an ISO 8601 UTC timestamp for a time in the past"""
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_warning_shown_for_llm_working_pr_older_than_30_minutes(self, mocker):
        """Warning should be shown for LLM working PRs created more than 30 minutes ago"""
        all_prs = [
            {
                "title": "Old LLM PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(1801),  # 30 min 1 sec ago
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります" in output
        assert "PRを人力で開いてチェックしてください" in output

    def test_warning_not_shown_for_llm_working_pr_younger_than_30_minutes(self, mocker):
        """Warning should NOT be shown for LLM working PRs created less than 30 minutes ago"""
        all_prs = [
            {
                "title": "New LLM PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(1799),  # 29 min 59 sec ago
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_not_shown_for_non_llm_working_phase(self, mocker):
        """Warning should NOT be shown for PRs not in LLM working phase, even if old"""
        all_prs = [
            {
                "title": "Old Phase1 PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(3600),  # 1 hour ago
            }
        ]
        pr_phases = [PHASE_1]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_not_shown_when_created_at_missing(self, mocker):
        """Warning should NOT be shown when createdAt field is absent"""
        all_prs = [
            {
                "title": "No Date PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                # no createdAt field
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって" not in output

    def test_warning_shown_at_exactly_30_minutes(self, mocker):
        """Warning should be shown at exactly 30 minutes (boundary condition)"""
        all_prs = [
            {
                "title": "Boundary PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(1800),  # exactly 30 minutes ago
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります" in output


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


class TestLLMWorkingLatestActivityWarning:
    """Tests for warning logic based on latest LLM session activity timestamp."""

    def setup_method(self):
        _pr_state_times.clear()

    def _make_activity_status(self, label: str, seconds_ago: float) -> str:
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        month_name = dt.strftime("%B")
        return (
            f"Copilot {label} on behalf of cat2151 "
            f"{month_name} {dt.day}, {dt.year} {dt.strftime('%H:%M')}"
        )

    def _make_created_at(self, seconds_ago: float) -> str:
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_warning_not_shown_when_activity_is_recent(self, mocker):
        """Warning must NOT appear when latest activity is only 4 minutes ago,
        even if the PR was created more than 24 hours ago."""
        started_status = self._make_activity_status("started work", 240)  # 4 minutes ago
        all_prs = [
            {
                "title": "Long-running PR with recent activity",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(86401),  # > 24 hours ago
                "llm_statuses": [started_status],
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_not_shown_when_reviewing_is_recent(self, mocker):
        """'started reviewing' 4 minutes ago must also suppress the warning."""
        reviewing_status = self._make_activity_status("started reviewing", 240)  # 4 minutes ago
        all_prs = [
            {
                "title": "Long-running PR with recent review activity",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(86401),  # > 24 hours ago
                "llm_statuses": [reviewing_status],
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_shown_when_activity_is_over_1_hour_ago(self, mocker):
        """Warning must appear when latest activity was more than 1 hour ago
        (session hang scenario)."""
        started_status = self._make_activity_status("started work", 3601)  # just over 1 hour ago
        all_prs = [
            {
                "title": "Hung session PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(7200),  # 2 hours ago
                "llm_statuses": [started_status],
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります" in output
        assert "PRを人力で開いてチェックしてください" in output

    def test_warning_not_shown_when_activity_is_exactly_below_1_hour(self, mocker):
        """Warning must NOT appear when latest activity is well under 1 hour ago.

        Note: status text stores only hour:minute (no seconds), so a borderline value
        of exactly 3599s could appear as ≥3600s after minute-truncation.  We use 45
        minutes (2700s) to remain safely below the threshold.
        """
        started_status = self._make_activity_status("started work", 2700)  # 45 minutes ago
        all_prs = [
            {
                "title": "Active PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(7200),
                "llm_statuses": [started_status],
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output

    def test_latest_activity_takes_precedence_over_created_at(self, mocker):
        """When llm_statuses contain a parseable timestamp, it must be
        used instead of createdAt for the warning decision."""
        # PR is >30 minutes old (would trigger old logic), but latest activity is recent
        started_status = self._make_activity_status("started work", 60)  # 1 minute ago
        all_prs = [
            {
                "title": "Old PR, but recently active",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(3600),  # 1 hour ago
                "llm_statuses": [started_status],
            }
        ]
        pr_phases = [PHASE_LLM_WORKING]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, pr_phases, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output
    """Test the wait_with_countdown functionality"""

    def test_countdown_displays_remaining_time(self, mocker):
        """Test that countdown displays remaining time correctly (counting down from initial value to 0)"""
        mock_print = mocker.patch("builtins.print")
        mock_sleep = mocker.patch("time.sleep")
        mock_time = mocker.patch("time.time")
        # Mock time.time to simulate passage of time
        mock_time.side_effect = [0, 0, 1, 2, 3, 3]  # start, loop checks
        wait_with_countdown(3, "3s")

        # Verify print was called with header
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Waiting 3s until next check" in output

        # Verify countdown messages were printed (remaining time, counting down)
        assert "Waiting 3秒" in output
        assert "Waiting 2秒" in output
        assert "Waiting 1秒" in output
        assert "Waiting 0秒" in output

        # Verify sleep was called correct number of times
        assert mock_sleep.call_count == 3

    def test_countdown_uses_carriage_return_for_updates(self, mocker):
        """Test that countdown uses ANSI escape sequences (carriage return) for in-place updates"""
        mock_print = mocker.patch("builtins.print")
        mocker.patch("time.sleep")
        mock_time = mocker.patch("time.time")
        # Mock time.time to simulate passage of time
        mock_time.side_effect = [0, 0, 1, 2, 2]
        wait_with_countdown(2, "2s")

        # Check that carriage return is used in countdown lines
        countdown_calls = [
            call
            for call in mock_print.call_args_list
            if "Waiting" in str(call) and "until next check" not in str(call)
        ]

        # Verify carriage return usage
        for call in countdown_calls[:-1]:  # All except the last one
            call_str = str(call)
            assert "\\r" in call_str or call_str.startswith("call('\\r")

    def test_countdown_handles_different_intervals(self, mocker):
        """Test that countdown properly handles different time intervals"""
        mock_print = mocker.patch("builtins.print")
        mock_sleep = mocker.patch("time.sleep")
        mock_time = mocker.patch("time.time")
        # Mock time.time to simulate passage of time
        mock_time.side_effect = [0, 0, 1, 2, 3, 4, 5, 5]
        wait_with_countdown(5, "5s")

        # Verify sleep was called 5 times (once per second)
        assert mock_sleep.call_count == 5

        # Verify final countdown display (should show 0 remaining)
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "Waiting 0秒" in output

    def test_countdown_formats_time_correctly(self, mocker):
        """Test that countdown formats time with minutes and seconds"""
        mock_print = mocker.patch("builtins.print")
        mocker.patch("time.sleep")
        mock_time = mocker.patch("time.time")
        # Mock time.time to simulate 90 seconds of elapsed time
        # We need enough values for 90 iterations + extra for checks
        times = [0] + [i for i in range(91) for _ in range(2)]  # start + pairs for each iteration
        mock_time.side_effect = times
        wait_with_countdown(90, "90s")

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        # Verify that minutes are displayed correctly (countdown from 90 seconds)
        # At 89 seconds remaining: "Waiting 1分29秒"
        # At 60 seconds remaining: "Waiting 1分0秒"
        assert "Waiting 1分29秒" in output
        assert "Waiting 1分0秒" in output
