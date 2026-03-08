"""Tests for wait_with_countdown self-update callback handling."""

import src.gh_pr_phase_monitor.ui.wait_handler as wait_handler
from src.gh_pr_phase_monitor.ui.wait_handler import wait_with_countdown

def _patch_time(monkeypatch, start=0.0):
    current = {"value": start}

    def fake_time():
        return current["value"]

    def fake_sleep(duration):
        current["value"] += duration

    monkeypatch.setattr(wait_handler.time, "time", fake_time)
    monkeypatch.setattr(wait_handler.time, "sleep", fake_sleep)
    return current


def test_self_update_callback_invoked_at_interval(monkeypatch):
    calls = []
    _patch_time(monkeypatch, start=0.0)

    wait_handler.wait_with_countdown(
        3,
        "3s",
        self_update_callback=lambda: calls.append("ping"),
        self_update_interval_seconds=1,
    )

    assert len(calls) == 3


def test_self_update_callback_not_invoked_when_none(monkeypatch):
    _patch_time(monkeypatch, start=0.0)
    wait_handler.wait_with_countdown(2, "2s", self_update_callback=None)

    # Nothing to assert besides no exceptions; ensure the helper returns default tuple
    # and no callback-related side effects occur.
    # We still validate the function completes and returns expected shape.
    config, seconds, interval_str, _mtime = wait_handler.wait_with_countdown(1, "1s", self_update_callback=None)
    assert config == {}
    assert seconds == 1
    assert interval_str == "1s"


def test_self_update_callback_exception_is_logged(monkeypatch):
    _patch_time(monkeypatch, start=0.0)
    errors = []

    def fake_logger(exc: Exception):
        errors.append(str(exc))

    monkeypatch.setattr(wait_handler, "_log_self_update_error", fake_logger)

    def failing_callback():
        raise RuntimeError("boom")

    wait_handler.wait_with_countdown(
        2,
        "2s",
        self_update_callback=failing_callback,
        self_update_interval_seconds=1,
    )

    assert errors and "boom" in errors[0]


class TestWaitWithCountdownDisplay:
    """Test the terminal countdown display of wait_with_countdown()"""

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
