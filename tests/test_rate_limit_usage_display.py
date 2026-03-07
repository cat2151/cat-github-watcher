
from src.gh_pr_phase_monitor.main import _display_rate_limit_usage


def _make_rate_limit(remaining: int, limit: int = 5000, reset_epoch: float = 1777777777.0) -> dict:
    return {"remaining": remaining, "limit": limit, "used": limit - remaining, "reset": reset_epoch}


def test_display_rate_limit_usage_shows_consumed_and_remaining(mocker, capsys):
    before = _make_rate_limit(remaining=4800)
    after = _make_rate_limit(remaining=4758)

    mocker.patch("src.gh_pr_phase_monitor.github.rate_limit_handler._format_rate_limit_reset",
        return_value=("2026-03-01 01:00:00 UTC", "58分"),)
    _display_rate_limit_usage(before, after)

    captured = capsys.readouterr()
    assert "今回消費=42点" in captured.out
    assert "残=4758/5000" in captured.out
    assert "リセット=2026-03-01 01:00:00 UTC" in captured.out
    assert "あと58分" in captured.out


def test_display_rate_limit_usage_no_before_omits_consumed(mocker, capsys):
    after = _make_rate_limit(remaining=4800)

    mocker.patch("src.gh_pr_phase_monitor.github.rate_limit_handler._format_rate_limit_reset",
        return_value=("2026-03-01 01:00:00 UTC", "30分"),)
    _display_rate_limit_usage(None, after)

    captured = capsys.readouterr()
    assert "今回消費" not in captured.out
    assert "残=4800/5000" in captured.out
    assert "リセット=2026-03-01 01:00:00 UTC" in captured.out


def test_display_rate_limit_usage_no_after_outputs_nothing(capsys):
    before = _make_rate_limit(remaining=4800)
    _display_rate_limit_usage(before, None)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_display_rate_limit_usage_zero_consumed(mocker, capsys):
    before = _make_rate_limit(remaining=5000)
    after = _make_rate_limit(remaining=5000)

    mocker.patch("src.gh_pr_phase_monitor.github.rate_limit_handler._format_rate_limit_reset",
        return_value=("2026-03-01 01:00:00 UTC", "60分"),)
    _display_rate_limit_usage(before, after)

    captured = capsys.readouterr()
    assert "今回消費=0点" in captured.out


def test_display_rate_limit_usage_negative_consumed_shows_reset_note(mocker, capsys):
    # レートリミットウィンドウがリセットされ after.remaining > before.remaining になるケース
    before = _make_rate_limit(remaining=100)
    after = _make_rate_limit(remaining=4900)

    mocker.patch("src.gh_pr_phase_monitor.github.rate_limit_handler._format_rate_limit_reset",
        return_value=("2026-03-01 01:00:00 UTC", "60分"),)
    _display_rate_limit_usage(before, after)

    captured = capsys.readouterr()
    assert "今回消費=0点" in captured.out
    assert "リセット後" in captured.out
