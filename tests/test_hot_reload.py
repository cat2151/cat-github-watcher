"""
Tests for hot reload functionality
"""

import os
import tempfile
import time
from pathlib import Path

import pytest

from src.gh_pr_phase_monitor.config import get_config_mtime, load_config


class TestConfigMtime:
    """Test the get_config_mtime function"""

    def test_get_config_mtime(self):
        """Test getting modification time of a config file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('interval = "1m"\n')
            config_path = f.name

        try:
            # Get the modification time
            mtime = get_config_mtime(config_path)
            
            # Verify it's a float (timestamp)
            assert isinstance(mtime, float)
            assert mtime > 0
            
            # Verify we can get the same time again
            mtime2 = get_config_mtime(config_path)
            assert mtime == mtime2
        finally:
            os.unlink(config_path)

    def test_get_config_mtime_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_config_mtime("/tmp/nonexistent_config_file.toml")

    def test_config_mtime_changes_on_modification(self):
        """Test that modification time changes when file is modified"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('interval = "1m"\n')
            config_path = f.name

        try:
            # Get initial modification time
            mtime1 = get_config_mtime(config_path)
            
            # Wait a bit to ensure time difference
            time.sleep(0.1)
            
            # Modify the file
            with open(config_path, "w") as f:
                f.write('interval = "2m"\n')
            
            # Get new modification time
            mtime2 = get_config_mtime(config_path)
            
            # Verify the modification time has changed
            assert mtime2 > mtime1
        finally:
            os.unlink(config_path)

    def test_hot_reload_detection(self):
        """Test that we can detect when config needs to be reloaded"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('interval = "1m"\n')
            config_path = f.name

        try:
            # Load initial config
            config1 = load_config(config_path)
            mtime1 = get_config_mtime(config_path)
            
            assert config1["interval"] == "1m"
            
            # Wait and modify the config
            time.sleep(0.1)
            with open(config_path, "w") as f:
                f.write('interval = "5m"\n')
            
            # Check if mtime has changed
            mtime2 = get_config_mtime(config_path)
            assert mtime2 != mtime1
            
            # Reload config
            config2 = load_config(config_path)
            assert config2["interval"] == "5m"
        finally:
            os.unlink(config_path)


class TestHotReloadScenarios:
    """Test various hot reload scenarios"""

    def test_config_reload_with_new_interval(self):
        """Test that config can be reloaded with a new interval"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('interval = "30s"\n')
            config_path = f.name

        try:
            # Initial state
            config = load_config(config_path)
            mtime = get_config_mtime(config_path)
            assert config["interval"] == "30s"
            
            # Simulate modification
            time.sleep(0.1)
            with open(config_path, "w") as f:
                f.write('interval = "2m"\n')
            
            # Check for changes
            new_mtime = get_config_mtime(config_path)
            if new_mtime != mtime:
                # Reload
                new_config = load_config(config_path)
                assert new_config["interval"] == "2m"
                assert new_config["interval"] != config["interval"]
        finally:
            os.unlink(config_path)

    def test_config_reload_with_multiple_settings(self):
        """Test that all settings are reloaded, not just interval"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('interval = "1m"\nverbose = false\n')
            config_path = f.name

        try:
            # Initial state
            config = load_config(config_path)
            mtime = get_config_mtime(config_path)
            assert config["interval"] == "1m"
            assert config["verbose"] is False
            
            # Modify multiple settings
            time.sleep(0.1)
            with open(config_path, "w") as f:
                f.write('interval = "3m"\nverbose = true\nissue_display_limit = 20\n')
            
            # Check and reload
            new_mtime = get_config_mtime(config_path)
            if new_mtime != mtime:
                new_config = load_config(config_path)
                assert new_config["interval"] == "3m"
                assert new_config["verbose"] is True
                assert new_config["issue_display_limit"] == 20
        finally:
            os.unlink(config_path)

    def test_no_reload_when_config_unchanged(self):
        """Test that config is not reloaded when file hasn't changed"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('interval = "1m"\n')
            config_path = f.name

        try:
            # Initial load
            config = load_config(config_path)
            mtime1 = get_config_mtime(config_path)
            
            # Wait but don't modify
            time.sleep(0.1)
            
            # Check mtime again
            mtime2 = get_config_mtime(config_path)
            
            # Should be the same
            assert mtime1 == mtime2
        finally:
            os.unlink(config_path)
