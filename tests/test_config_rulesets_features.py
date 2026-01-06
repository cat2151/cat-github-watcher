"""
Tests for ruleset-based phase3_merge and assign_to_copilot configuration resolution
"""

import pytest

from src.gh_pr_phase_monitor.config import resolve_execution_config_for_repo


class TestResolveExecutionConfigWithPhase3Merge:
    """Test phase3_merge configuration resolution in rulesets"""

    def test_global_phase3_merge_config(self):
        """Global phase3_merge config should be used when no rulesets"""
        config = {
            "phase3_merge": {
                "enabled": True,
                "comment": "Global merge comment",
                "automated": False,
            }
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["phase3_merge"]["enabled"] is True
        assert result["phase3_merge"]["comment"] == "Global merge comment"
        assert result["phase3_merge"]["automated"] is False

    def test_ruleset_overrides_phase3_merge(self):
        """Ruleset should override global phase3_merge settings"""
        config = {
            "phase3_merge": {
                "enabled": False,
                "comment": "Global merge comment",
                "automated": False,
            },
            "rulesets": [
                {
                    "name": "Enable merge for test-repo",
                    "repositories": ["owner/test-repo"],
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "Ruleset merge comment",
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["phase3_merge"]["enabled"] is True
        assert result["phase3_merge"]["comment"] == "Ruleset merge comment"
        assert result["phase3_merge"]["automated"] is True

    def test_ruleset_partial_phase3_merge_override(self):
        """Ruleset can partially override phase3_merge settings"""
        config = {
            "phase3_merge": {
                "enabled": False,
                "comment": "Global merge comment",
                "automated": False,
                "wait_seconds": 10,
            },
            "rulesets": [
                {
                    "repositories": ["all"],
                    "phase3_merge": {
                        "enabled": True,
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        # Overridden settings
        assert result["phase3_merge"]["enabled"] is True
        assert result["phase3_merge"]["automated"] is True
        # Preserved settings from global
        assert result["phase3_merge"]["comment"] == "Global merge comment"
        assert result["phase3_merge"]["wait_seconds"] == 10

    def test_multiple_rulesets_phase3_merge_override(self):
        """Later rulesets should override earlier ones for phase3_merge"""
        config = {
            "phase3_merge": {
                "enabled": False,
                "comment": "Global",
                "automated": False,
            },
            "rulesets": [
                {
                    "repositories": ["all"],
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "First ruleset",
                    }
                },
                {
                    "repositories": ["owner/test-repo"],
                    "phase3_merge": {
                        "comment": "Second ruleset",
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        # enabled comes from first ruleset
        assert result["phase3_merge"]["enabled"] is True
        # comment overridden by second ruleset
        assert result["phase3_merge"]["comment"] == "Second ruleset"
        # automated from second ruleset
        assert result["phase3_merge"]["automated"] is True

    def test_no_phase3_merge_in_ruleset_keeps_global(self):
        """Ruleset without phase3_merge should keep global settings"""
        config = {
            "phase3_merge": {
                "enabled": True,
                "comment": "Global merge comment",
            },
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["phase3_merge"]["enabled"] is True
        assert result["phase3_merge"]["comment"] == "Global merge comment"

    def test_empty_phase3_merge_dict_in_global(self):
        """Empty phase3_merge in global config should work"""
        config = {
            "phase3_merge": {},
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "phase3_merge": {
                        "enabled": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["phase3_merge"]["enabled"] is True


class TestResolveExecutionConfigWithAssignToCopilot:
    """Test assign_to_copilot configuration resolution in rulesets"""

    def test_global_assign_to_copilot_config(self):
        """Global assign_to_copilot config should be used when no rulesets"""
        config = {
            "assign_to_copilot": {
                "enabled": True,
                "assign_lowest_number_issue": False,
                "automated": True,
            }
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["assign_to_copilot"]["enabled"] is True
        assert result["assign_to_copilot"]["assign_lowest_number_issue"] is False
        assert result["assign_to_copilot"]["automated"] is True

    def test_ruleset_overrides_assign_to_copilot(self):
        """Ruleset should override global assign_to_copilot settings"""
        config = {
            "assign_to_copilot": {
                "enabled": False,
                "assign_lowest_number_issue": False,
                "automated": False,
            },
            "rulesets": [
                {
                    "name": "Enable assign for test-repo",
                    "repositories": ["owner/test-repo"],
                    "assign_to_copilot": {
                        "enabled": True,
                        "assign_lowest_number_issue": True,
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["assign_to_copilot"]["enabled"] is True
        assert result["assign_to_copilot"]["assign_lowest_number_issue"] is True
        assert result["assign_to_copilot"]["automated"] is True

    def test_ruleset_partial_assign_to_copilot_override(self):
        """Ruleset can partially override assign_to_copilot settings"""
        config = {
            "assign_to_copilot": {
                "enabled": False,
                "assign_lowest_number_issue": False,
                "automated": False,
                "wait_seconds": 10,
                "browser": "edge",
            },
            "rulesets": [
                {
                    "repositories": ["all"],
                    "assign_to_copilot": {
                        "enabled": True,
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        # Overridden settings
        assert result["assign_to_copilot"]["enabled"] is True
        assert result["assign_to_copilot"]["automated"] is True
        # Preserved settings from global
        assert result["assign_to_copilot"]["assign_lowest_number_issue"] is False
        assert result["assign_to_copilot"]["wait_seconds"] == 10
        assert result["assign_to_copilot"]["browser"] == "edge"

    def test_multiple_rulesets_assign_to_copilot_override(self):
        """Later rulesets should override earlier ones for assign_to_copilot"""
        config = {
            "assign_to_copilot": {
                "enabled": False,
                "assign_lowest_number_issue": False,
                "automated": False,
            },
            "rulesets": [
                {
                    "repositories": ["all"],
                    "assign_to_copilot": {
                        "enabled": True,
                    }
                },
                {
                    "repositories": ["owner/test-repo"],
                    "assign_to_copilot": {
                        "assign_lowest_number_issue": True,
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        # enabled comes from first ruleset
        assert result["assign_to_copilot"]["enabled"] is True
        # assign_lowest_number_issue from second ruleset
        assert result["assign_to_copilot"]["assign_lowest_number_issue"] is True
        # automated from second ruleset
        assert result["assign_to_copilot"]["automated"] is True

    def test_no_assign_to_copilot_in_ruleset_keeps_global(self):
        """Ruleset without assign_to_copilot should keep global settings"""
        config = {
            "assign_to_copilot": {
                "enabled": True,
                "automated": False,
            },
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["assign_to_copilot"]["enabled"] is True
        assert result["assign_to_copilot"]["automated"] is False


class TestResolveExecutionConfigCombined:
    """Test combined phase3_merge and assign_to_copilot configuration"""

    def test_both_features_in_same_ruleset(self):
        """Ruleset can configure both phase3_merge and assign_to_copilot"""
        config = {
            "phase3_merge": {
                "enabled": False,
            },
            "assign_to_copilot": {
                "enabled": False,
            },
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "phase3_merge": {
                        "enabled": True,
                        "comment": "Merged by automation",
                    },
                    "assign_to_copilot": {
                        "enabled": True,
                        "automated": True,
                    }
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["enable_execution_phase3_to_merge"] is True
        assert result["phase3_merge"]["enabled"] is True
        assert result["phase3_merge"]["comment"] == "Merged by automation"
        assert result["assign_to_copilot"]["enabled"] is True
        assert result["assign_to_copilot"]["automated"] is True

    def test_different_repos_different_configs(self):
        """Different repositories can have different feature configurations"""
        config = {
            "phase3_merge": {"enabled": False},
            "assign_to_copilot": {"enabled": False},
            "rulesets": [
                {
                    "repositories": ["owner/repo1"],
                    "phase3_merge": {
                        "enabled": True,
                        "automated": False,
                    }
                },
                {
                    "repositories": ["owner/repo2"],
                    "assign_to_copilot": {
                        "enabled": True,
                        "automated": True,
                    }
                }
            ],
        }
        
        # repo1 should have merge enabled
        result1 = resolve_execution_config_for_repo(config, "owner", "repo1")
        assert result1["phase3_merge"]["enabled"] is True
        assert result1["phase3_merge"]["automated"] is False
        assert result1["assign_to_copilot"]["enabled"] is False
        
        # repo2 should have assign enabled
        result2 = resolve_execution_config_for_repo(config, "owner", "repo2")
        assert result2["phase3_merge"]["enabled"] is False
        assert result2["assign_to_copilot"]["enabled"] is True
        assert result2["assign_to_copilot"]["automated"] is True

    def test_invalid_phase3_merge_type_ignored(self):
        """Invalid phase3_merge type in ruleset should be ignored"""
        config = {
            "phase3_merge": {"enabled": True, "comment": "Global"},
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "phase3_merge": "invalid_string",  # Invalid type
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        # Should keep global settings since invalid type is ignored
        assert result["phase3_merge"]["enabled"] is True
        assert result["phase3_merge"]["comment"] == "Global"

    def test_invalid_assign_to_copilot_type_ignored(self):
        """Invalid assign_to_copilot type in ruleset should be ignored"""
        config = {
            "assign_to_copilot": {"enabled": True, "automated": False},
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "assign_to_copilot": ["invalid", "list"],  # Invalid type
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        # Should keep global settings since invalid type is ignored
        assert result["assign_to_copilot"]["enabled"] is True
        assert result["assign_to_copilot"]["automated"] is False

    def test_no_global_phase3_merge_uses_empty_dict(self):
        """No global phase3_merge should result in empty dict"""
        config = {
            "rulesets": [
                {
                    "repositories": ["owner/test-repo"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["phase3_merge"] == {}
        assert result["assign_to_copilot"] == {}
