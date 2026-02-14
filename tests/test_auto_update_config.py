"""Config defaults for auto-update."""

from src.gh_pr_phase_monitor.config import DEFAULT_ENABLE_AUTO_UPDATE, load_config


def test_auto_update_defaults_disabled(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text('interval = "1m"\n', encoding="utf-8")

    config = load_config(str(config_path))

    assert config["enable_auto_update"] is DEFAULT_ENABLE_AUTO_UPDATE
    assert config["enable_auto_update"] is False
