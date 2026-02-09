"""
Tests for configurable color schemes
"""

import os
import tempfile

import pytest

from src.gh_pr_phase_monitor.colors import DEFAULT_COLOR_SCHEME, colorize_phase, set_color_scheme
from src.gh_pr_phase_monitor.config import load_config


@pytest.fixture(autouse=True)
def reset_color_scheme():
    """Ensure global color palette is restored after each test."""
    yield
    set_color_scheme(DEFAULT_COLOR_SCHEME)


def test_load_config_uses_default_color_scheme_when_missing():
    """Config without color_scheme should default to monokai."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write('interval = "1m"\n')
        config_path = f.name

    try:
        config = load_config(config_path)
        assert config["color_scheme"] == DEFAULT_COLOR_SCHEME
        # Default monokai palette embeds the 230;219;116 code for phase1
        assert "38;2;230;219;116" in colorize_phase("phase1")
    finally:
        os.unlink(config_path)


def test_load_config_applies_valid_color_scheme():
    """Config with supported color_scheme should be applied."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write('color_scheme = "classic"\n')
        config_path = f.name

    try:
        config = load_config(config_path)
        assert config["color_scheme"] == "classic"
        assert "\033[93m" in colorize_phase("phase1")
    finally:
        os.unlink(config_path)


def test_load_config_falls_back_on_invalid_color_scheme():
    """Unsupported color_scheme values should fall back to the default."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write('color_scheme = "unknown"\n')
        config_path = f.name

    try:
        config = load_config(config_path)
        assert config["color_scheme"] == DEFAULT_COLOR_SCHEME
        assert "38;2;230;219;116" in colorize_phase("phase1")
    finally:
        os.unlink(config_path)
