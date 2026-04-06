"""Config defaults for auto-update."""

from src.gh_pr_phase_monitor.core.config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_ENABLE_AUTO_UPDATE_DEBUG_LOG,
    load_config,
)


def test_auto_update_defaults_disabled(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["enable_auto_update"] is DEFAULT_ENABLE_AUTO_UPDATE
    assert config["enable_auto_update"] is False
    assert config["enable_auto_update_debug_log"] is DEFAULT_ENABLE_AUTO_UPDATE_DEBUG_LOG
    assert config["enable_auto_update_debug_log"] is False


def test_auto_update_debug_log_can_be_enabled(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\nenable_auto_update_debug_log = true\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["enable_auto_update_debug_log"] is True
