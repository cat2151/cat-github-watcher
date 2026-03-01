"""
Configuration printing utilities
"""

from typing import Any, Dict

from .config import (
    DEFAULT_ASSIGN_TO_COPILOT_CONFIG,
    DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE,
    DEFAULT_COLOR_SCHEME,
    DEFAULT_DISPLAY_LLM_STATUS_TIMELINE,
    DEFAULT_DISPLAY_PR_AUTHOR,
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS,
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
)


def print_config(config: Dict[str, Any]) -> None:
    """Print all configuration settings in a readable format

    Args:
        config: Configuration dictionary loaded from TOML
    """
    print("\n" + "=" * 50)
    print("Configuration Settings:")
    print("=" * 50)

    # Print main settings
    print("\n[Main Settings]")
    print(f"  interval: {config.get('interval', '1m')}")
    print(f"  issue_display_limit: {config.get('issue_display_limit', 10)}")
    print(f"  no_change_timeout: {config.get('no_change_timeout', '30m')}")
    print(f"  reduced_frequency_interval: {config.get('reduced_frequency_interval', '1h')}")
    print(f"  max_llm_working_parallel: {config.get('max_llm_working_parallel', DEFAULT_MAX_LLM_WORKING_PARALLEL)}")
    print(f"  verbose: {config.get('verbose', False)}")
    print(f"  color_scheme: {config.get('color_scheme', DEFAULT_COLOR_SCHEME)}")
    print(
        f"  check_process_before_autoraise: {config.get('check_process_before_autoraise', DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE)}"
    )
    print(f"  display_pr_author: {config.get('display_pr_author', DEFAULT_DISPLAY_PR_AUTHOR)}")
    print(
        f"  display_llm_status_timeline: {config.get('display_llm_status_timeline', DEFAULT_DISPLAY_LLM_STATUS_TIMELINE)}"
    )
    print(f"  enable_pr_phase_snapshots: {config.get('enable_pr_phase_snapshots', DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS)}")
    print(f"  enable_auto_update: {config.get('enable_auto_update', DEFAULT_ENABLE_AUTO_UPDATE)}")

    coding_agent = config.get("coding_agent")
    if coding_agent and isinstance(coding_agent, dict):
        print("\n[Coding Agent]")
        print(f"  agent_name: {coding_agent.get('agent_name', 'N/A')}")

    # Print rulesets
    rulesets = config.get("rulesets", [])
    if rulesets and isinstance(rulesets, list):
        print("\n[Rulesets]")
        for i, ruleset in enumerate(rulesets, 1):
            if isinstance(ruleset, dict):
                print(f"\n  Ruleset #{i}:")
                print(f"    name: {ruleset.get('name', 'N/A')}")
                print(f"    repositories: {ruleset.get('repositories', [])}")
                print(
                    f"    enable_execution_phase1_to_phase2: {ruleset.get('enable_execution_phase1_to_phase2', 'not set')}"
                )
                print(
                    f"    enable_execution_phase2_to_phase3: {ruleset.get('enable_execution_phase2_to_phase3', 'not set')}"
                )
                print(
                    f"    enable_execution_phase3_send_ntfy: {ruleset.get('enable_execution_phase3_send_ntfy', 'not set')}"
                )
                print(
                    f"    enable_execution_phase3_to_merge: {ruleset.get('enable_execution_phase3_to_merge', 'not set')}"
                )
                print(f"    enable_execution_pages_open: {ruleset.get('enable_execution_pages_open', 'not set')}")
    else:
        print("\n[Rulesets]")
        print("  No rulesets configured")

    # Print ntfy settings
    ntfy = config.get("ntfy")
    if ntfy and isinstance(ntfy, dict):
        print("\n[ntfy.sh Notification Settings]")
        print(f"  enabled: {ntfy.get('enabled', False)}")
        if ntfy.get("enabled", False):
            print(f"  topic: {ntfy.get('topic', 'N/A')}")
            print(f"  message: {ntfy.get('message', 'N/A')}")
            print(f"  priority: {ntfy.get('priority', 4)}")

    # Print phase3_merge settings
    phase3_merge = config.get("phase3_merge")
    if phase3_merge and isinstance(phase3_merge, dict):
        print("\n[Phase3 Merge Settings]")
        print(f"  comment: {phase3_merge.get('comment', 'N/A')}")
        print(f"  automated: {phase3_merge.get('automated', False)}")
        if phase3_merge.get("automated", False):
            print(f"  automation_backend: {phase3_merge.get('automation_backend', 'playwright')}")
            print(f"  wait_seconds: {phase3_merge.get('wait_seconds', 10)}")
            print(f"  browser: {phase3_merge.get('browser', 'chromium')}")
            print(f"  headless: {phase3_merge.get('headless', False)}")

    # Print assign_to_copilot settings
    assign_to_copilot = config.get("assign_to_copilot")
    if assign_to_copilot and isinstance(assign_to_copilot, dict):
        print("\n[Auto-assign to Copilot Settings]")
        print(f"  assign_lowest_number_issue: {assign_to_copilot.get('assign_lowest_number_issue', False)}")
        print(f"  automation_backend: {assign_to_copilot.get('automation_backend', 'playwright')}")
        print(
            f"  wait_seconds: {assign_to_copilot.get('wait_seconds', DEFAULT_ASSIGN_TO_COPILOT_CONFIG['wait_seconds'])}"
        )
        print(f"  browser: {assign_to_copilot.get('browser', 'chromium')}")
        print(f"  headless: {assign_to_copilot.get('headless', False)}")

    print("\n" + "=" * 50)


def print_repo_execution_config(repo_owner: str, repo_name: str, exec_config: Dict[str, Any]) -> None:
    """Print execution configuration for a specific repository

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        exec_config: Execution configuration dictionary
    """
    print(f"    [Execution Config for {repo_name}]")
    print(f"      enable_execution_phase1_to_phase2: {exec_config.get('enable_execution_phase1_to_phase2', False)}")
    print(f"      enable_execution_phase2_to_phase3: {exec_config.get('enable_execution_phase2_to_phase3', False)}")
    print(f"      enable_execution_phase3_send_ntfy: {exec_config.get('enable_execution_phase3_send_ntfy', False)}")
    print(f"      enable_execution_phase3_to_merge: {exec_config.get('enable_execution_phase3_to_merge', False)}")
    print(
        f"      enable_execution_pr_title_fix_comment: {exec_config.get('enable_execution_pr_title_fix_comment', False)}"
    )
    print(f"      enable_execution_pages_open: {exec_config.get('enable_execution_pages_open', False)}")
    print(f"      assign_good_first_old: {exec_config.get('assign_good_first_old', False)}")
    print(f"      assign_ci_failure_old: {exec_config.get('assign_ci_failure_old', False)}")
    print(f"      assign_deploy_pages_failure_old: {exec_config.get('assign_deploy_pages_failure_old', False)}")
    print(f"      assign_old: {exec_config.get('assign_old', False)}")
