"""Tests for wait_with_countdown self-update callback handling."""

import src.gh_pr_phase_monitor.wait_handler as wait_handler


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
