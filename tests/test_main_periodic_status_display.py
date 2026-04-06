"""Tests for periodic cached PR status display wiring in main()."""

import importlib

main_module = importlib.import_module("src.gh_pr_phase_monitor.main")


def _setup_common_main_mocks(monkeypatch, wait_kwargs):
    monkeypatch.setattr(main_module, "load_config", lambda _path: {"interval": "1m", "enable_auto_update": False})
    monkeypatch.setattr(main_module, "get_config_mtime", lambda _path: 0.0)
    monkeypatch.setattr(main_module, "parse_interval", lambda _value: 60)
    monkeypatch.setattr(main_module.signal, "signal", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "set_auto_update_debug_log_enabled", lambda _enabled: None)
    monkeypatch.setattr(main_module, "run_startup_self_update_foreground", lambda *, apply_update=True: None)
    monkeypatch.setattr(main_module, "get_rate_limit_info", lambda: None)
    monkeypatch.setattr(main_module, "_display_rate_limit_usage", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(main_module, "_check_rate_limit_throttle", lambda *_args, **_kwargs: (False, 60))
    monkeypatch.setattr(main_module, "check_no_state_change_timeout", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(main_module, "determine_current_interval", lambda *_args, **_kwargs: (300, "5m"))
    monkeypatch.setattr(main_module, "display_status_summary", lambda *_args, **_kwargs: None)

    def fake_wait_with_countdown(*args, **kwargs):
        wait_kwargs.update(kwargs)
        raise KeyboardInterrupt("stop after first wait")

    monkeypatch.setattr(main_module, "wait_with_countdown", fake_wait_with_countdown)


def test_main_passes_periodic_status_callback_when_open_prs_exist(monkeypatch):
    wait_kwargs = {}
    _setup_common_main_mocks(monkeypatch, wait_kwargs)
    display_calls = []

    monkeypatch.setattr(
        main_module,
        "run_one_iteration",
        lambda _config, _iteration: (
            [
                {
                    "title": "Open PR",
                    "url": "https://github.com/owner/repo/pull/1",
                    "repository": {"name": "repo", "owner": "owner"},
                    "phase": "phase1",
                }
            ],
            [{"name": "repo", "owner": "owner", "openPRCount": 1}],
            False,
        ),
    )
    monkeypatch.setattr(main_module, "get_last_pr_snapshot", lambda: None)
    monkeypatch.setattr(
        main_module,
        "display_status_summary",
        lambda *args, **kwargs: display_calls.append((args, kwargs)),
    )

    try:
        main_module.main()
    except KeyboardInterrupt:
        pass

    assert callable(wait_kwargs["status_display_callback"])
    assert wait_kwargs["status_display_interval_seconds"] == 60
    wait_kwargs["status_display_callback"]()
    assert len(display_calls) == 2
    assert display_calls[1][0][0][0]["title"] == "Open PR"
    assert display_calls[1][0][1][0]["name"] == "repo"
    assert display_calls[1][1]["no_change"] is True


def test_main_skips_periodic_status_callback_when_no_open_prs(monkeypatch):
    wait_kwargs = {}
    _setup_common_main_mocks(monkeypatch, wait_kwargs)

    monkeypatch.setattr(main_module, "run_one_iteration", lambda _config, _iteration: ([], [], False))

    try:
        main_module.main()
    except KeyboardInterrupt:
        pass

    assert wait_kwargs["status_display_callback"] is None
    assert wait_kwargs["status_display_interval_seconds"] == 60
