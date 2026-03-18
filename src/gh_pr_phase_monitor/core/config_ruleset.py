"""Ruleset-based execution configuration resolution"""

from typing import Any, Dict


def _validate_boolean_flag(value: Any, flag_name: str) -> bool:
    """Validate that a configuration flag is a boolean value

    Args:
        value: The value to validate
        flag_name: Name of the flag for error messages

    Returns:
        The boolean value

    Raises:
        ValueError: If the value is not a boolean
    """
    if not isinstance(value, bool):
        raise ValueError(
            f"Configuration flag '{flag_name}' must be a boolean (true/false), got {type(value).__name__}: {value}"
        )
    return value


def resolve_execution_config_for_repo(config: Dict[str, Any], repo_owner: str, repo_name: str) -> Dict[str, Any]:
    """Resolve execution configuration for a specific repository using rulesets

    This function applies rulesets in order, with later rulesets overriding earlier ones.
    Global execution flags are no longer supported - all settings must be in rulesets.

    Args:
        config: Configuration dictionary loaded from TOML
        repo_owner: Repository owner (kept for compatibility, but not used in matching)
        repo_name: Repository name

    Returns:
        Dictionary with execution flags and feature settings:
        - enable_execution_phase1_to_phase2
        - enable_execution_phase2_to_phase3
        - enable_execution_phase3_send_ntfy
        - enable_execution_phase3_to_merge
        - enable_execution_pr_title_fix_comment
        - assign_good_first_old: Assign one old "good first issue"
        - assign_ci_failure_old: Assign one old "ci-failure" issue
        - assign_deploy_pages_failure_old: Assign one old "deploy-pages-failure" issue
        - assign_old: Assign one old issue (any issue)
    """
    # Start with all flags disabled (no global defaults)
    result = {
        "enable_execution_phase1_to_phase2": False,
        "enable_execution_phase2_to_phase3": False,
        "enable_execution_phase3_send_ntfy": False,
        "enable_execution_phase3_to_merge": False,
        "enable_execution_pr_title_fix_comment": False,  # Post comment when problematic PR title detected
        "enable_execution_pages_open": False,  # Open browser when GitHub Pages deployment completes
        "assign_good_first_old": False,  # Assign one old "good first issue"
        "assign_ci_failure_old": False,  # Assign one old "ci-failure" issue
        "assign_deploy_pages_failure_old": False,  # Assign one old "deploy-pages-failure" issue
        "assign_old": False,  # Assign one old issue (any issue)
    }

    # Apply rulesets if they exist
    rulesets = config.get("rulesets", [])
    if not isinstance(rulesets, list):
        return result

    for ruleset in rulesets:
        if not isinstance(ruleset, dict):
            continue

        # Get target repositories for this ruleset
        repositories = ruleset.get("repositories", [])
        if not isinstance(repositories, list):
            continue

        # Check if this ruleset applies to the current repository
        applies = False
        for repo_pattern in repositories:
            if not isinstance(repo_pattern, str):
                continue
            # "all" matches all repositories
            if repo_pattern.lower() == "all":
                applies = True
                break
            # Match by repository name only
            if repo_pattern == repo_name:
                applies = True
                break

        # If this ruleset applies, override execution flags with validation
        if applies:
            if "enable_execution_phase1_to_phase2" in ruleset:
                result["enable_execution_phase1_to_phase2"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase1_to_phase2"], "enable_execution_phase1_to_phase2"
                )
            if "enable_execution_phase2_to_phase3" in ruleset:
                result["enable_execution_phase2_to_phase3"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase2_to_phase3"], "enable_execution_phase2_to_phase3"
                )
            if "enable_execution_phase3_send_ntfy" in ruleset:
                result["enable_execution_phase3_send_ntfy"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase3_send_ntfy"], "enable_execution_phase3_send_ntfy"
                )
            if "enable_execution_phase3_to_merge" in ruleset:
                result["enable_execution_phase3_to_merge"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase3_to_merge"], "enable_execution_phase3_to_merge"
                )
            if "enable_execution_pr_title_fix_comment" in ruleset:
                result["enable_execution_pr_title_fix_comment"] = _validate_boolean_flag(
                    ruleset["enable_execution_pr_title_fix_comment"], "enable_execution_pr_title_fix_comment"
                )
            if "enable_execution_pages_open" in ruleset:
                result["enable_execution_pages_open"] = _validate_boolean_flag(
                    ruleset["enable_execution_pages_open"], "enable_execution_pages_open"
                )

            # Apply auto-assign flags
            if "assign_good_first_old" in ruleset:
                result["assign_good_first_old"] = _validate_boolean_flag(
                    ruleset["assign_good_first_old"], "assign_good_first_old"
                )
            if "assign_ci_failure_old" in ruleset:
                result["assign_ci_failure_old"] = _validate_boolean_flag(
                    ruleset["assign_ci_failure_old"], "assign_ci_failure_old"
                )
            if "assign_deploy_pages_failure_old" in ruleset:
                result["assign_deploy_pages_failure_old"] = _validate_boolean_flag(
                    ruleset["assign_deploy_pages_failure_old"], "assign_deploy_pages_failure_old"
                )
            if "assign_old" in ruleset:
                result["assign_old"] = _validate_boolean_flag(ruleset["assign_old"], "assign_old")

    return result
