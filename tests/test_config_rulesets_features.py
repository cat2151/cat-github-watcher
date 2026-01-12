"""
Tests for ruleset-based assign flags
"""

from src.gh_pr_phase_monitor.config import resolve_execution_config_for_repo


class TestResolveExecutionConfigCombined:
    """Test combined execution flags and assign flags"""

    def test_execution_and_assign_flags_in_same_ruleset(self):
        """Ruleset can set both execution flags and assign flags"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "assign_good_first_old": True,
                }
            ],
        }

        result = resolve_execution_config_for_repo(config, "owner", "test-repo")

        assert result["enable_execution_phase3_to_merge"] is True
        assert result["assign_good_first_old"] is True

    def test_different_repos_different_flags(self):
        """Different repositories can have different feature flags"""
        config = {
            "rulesets": [
                {
                    "repositories": ["repo1"],
                    "enable_execution_phase3_to_merge": True,
                },
                {
                    "repositories": ["repo2"],
                    "assign_old": True,
                },
            ],
        }

        # repo1 should have merge execution enabled, assign not enabled (False)
        result1 = resolve_execution_config_for_repo(config, "owner", "repo1")
        assert result1["enable_execution_phase3_to_merge"] is True
        assert result1["assign_old"] is False  # Not set, default False

        # repo2 should have assign enabled, merge execution disabled
        result2 = resolve_execution_config_for_repo(config, "owner", "repo2")
        assert result2["enable_execution_phase3_to_merge"] is False  # Default disabled
        assert result2["assign_old"] is True

    def test_all_repos_then_specific_override(self):
        """Can enable for all repos then disable for specific ones"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase3_to_merge": True,
                    "assign_good_first_old": True,
                },
                {
                    "repositories": ["special-repo"],
                    "enable_execution_phase3_to_merge": False,
                },
            ],
        }

        # Normal repo should have both enabled
        result1 = resolve_execution_config_for_repo(config, "owner", "normal-repo")
        assert result1["enable_execution_phase3_to_merge"] is True
        assert result1["assign_good_first_old"] is True

        # Special repo should have merge execution disabled but assign enabled
        result2 = resolve_execution_config_for_repo(config, "owner", "special-repo")
        assert result2["enable_execution_phase3_to_merge"] is False
        assert result2["assign_good_first_old"] is True

    def test_invalid_value_types_raise_error(self):
        """Invalid value types should raise ValueError"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "assign_good_first_old": "true",  # String instead of boolean - should raise ValueError
                }
            ],
        }

        # This should raise ValueError due to validation
        try:
            resolve_execution_config_for_repo(config, "owner", "test-repo")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected


class TestAssignGoodFirstOldFlag:
    """Test assign_good_first_old flag in rulesets"""

    def test_assign_good_first_old_default_false(self):
        """assign_good_first_old should default to False"""
        config = {}
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        assert result["assign_good_first_old"] is False

    def test_ruleset_enables_assign_good_first_old(self):
        """Ruleset should enable assign_good_first_old for specific repository"""
        config = {
            "rulesets": [
                {
                    "name": "Enable good first old for test-repo",
                    "repositories": ["test-repo"],
                    "assign_good_first_old": True,
                }
            ],
        }

        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["assign_good_first_old"] is True

        # Other repo should default to False
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["assign_good_first_old"] is False

    def test_assign_old_flag(self):
        """Test assign_old flag in rulesets"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "assign_old": True,
                }
            ],
        }

        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["assign_old"] is True

        # Other repo should use default (False)
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["assign_old"] is False

    def test_both_assign_flags_can_be_set(self):
        """Both assign_good_first_old and assign_old can be set to true"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "assign_good_first_old": True,
                    "assign_old": True,
                }
            ],
        }

        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["assign_good_first_old"] is True
        assert result["assign_old"] is True

    def test_priority_good_first_over_old(self):
        """When both flags are enabled, good first should be prioritized in the logic"""
        # This is tested implicitly in the main.py logic where we check any_good_first first
        # Here we just verify that both flags can coexist in config
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "assign_good_first_old": True,
                    "assign_old": True,
                }
            ]
        }

        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["assign_good_first_old"] is True
        assert result["assign_old"] is True
