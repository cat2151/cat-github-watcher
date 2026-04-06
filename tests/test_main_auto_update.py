"""Focused tests for main auto-update wiring."""

import importlib

import pytest

main_module = importlib.import_module("src.gh_pr_phase_monitor.main")


@pytest.mark.parametrize("enabled", [False, True])
def test_main_passes_enable_auto_update_to_startup_check(monkeypatch, enabled):
    called = {}

    monkeypatch.setattr(main_module, "load_config", lambda _path: {"interval": "1m", "enable_auto_update": enabled})
    monkeypatch.setattr(main_module, "get_config_mtime", lambda _path: 0.0)
    monkeypatch.setattr(main_module, "parse_interval", lambda _value: 60)
    monkeypatch.setattr(main_module.signal, "signal", lambda *_args, **_kwargs: None)

    def fake_startup(*, repo_root=None, apply_update=True):
        called["repo_root"] = repo_root
        called["apply_update"] = apply_update
        raise KeyboardInterrupt("stop after startup")

    monkeypatch.setattr(main_module, "run_startup_self_update_foreground", fake_startup)

    with pytest.raises(KeyboardInterrupt, match="stop after startup"):
        main_module.main()

    assert called["repo_root"] is None
    assert called["apply_update"] is enabled
