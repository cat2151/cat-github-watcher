"""Config defaults for auto-update."""

from src.gh_pr_phase_monitor.core.config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_STARTUP_AUTO_UPDATE_FOREGROUND,
    load_config,
)


def test_auto_update_defaults_disabled(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["enable_auto_update"] is DEFAULT_ENABLE_AUTO_UPDATE
    assert config["enable_auto_update"] is False


def test_startup_auto_update_foreground_defaults_true(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["startup_auto_update_foreground"] is DEFAULT_STARTUP_AUTO_UPDATE_FOREGROUND
    assert config["startup_auto_update_foreground"] is True


def test_startup_auto_update_foreground_can_be_set_false(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\nstartup_auto_update_foreground = false\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["startup_auto_update_foreground"] is False


def test_startup_auto_update_foreground_invalid_type_uses_default(tmp_path, capsys):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\nstartup_auto_update_foreground = "yes"\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["startup_auto_update_foreground"] is DEFAULT_STARTUP_AUTO_UPDATE_FOREGROUND
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "startup_auto_update_foreground" in captured.out
