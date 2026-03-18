"""
Configuration loading and parsing utilities
"""

import os
from typing import Any, Dict

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from .colors import (
    DEFAULT_COLOR_SCHEME,
    SUPPORTED_COLOR_KEYS,
    Colors,
    apply_custom_colors,
    get_supported_color_schemes,
    normalize_color_code,
    set_color_scheme,
)
from .config_ruleset import _validate_boolean_flag, resolve_execution_config_for_repo  # noqa: F401
from .interval_parser import parse_interval  # noqa: F401 - Re-exported for backwards compatibility
from .process_utils import is_process_running  # noqa: F401 - Re-exported for backwards compatibility

# Default configuration for phase3_merge feature (batteries included)
DEFAULT_PHASE3_MERGE_CONFIG: Dict[str, Any] = {
    "comment": "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。",
    "automated": False,
    "automation_backend": "playwright",
    "wait_seconds": 10,
    "browser": "chromium",
    "headless": False,
    "notification_enabled": True,
    "notification_message": "ブラウザを開いてMergeボタンを探索中...",
    "notification_width": 400,
    "notification_height": 150,
    "notification_position_x": 100,
    "notification_position_y": 100,
    "maximize_on_first_fail": True,
}

# Default configuration for assign_to_copilot feature (batteries included)
# Automated mode is always enabled by default
DEFAULT_ASSIGN_TO_COPILOT_CONFIG: Dict[str, Any] = {
    "automation_backend": "playwright",
    "wait_seconds": 2,
    "browser": "chromium",
    "headless": False,
    "notification_enabled": True,
    "notification_message": "ブラウザを開いてCopilot割り当てボタンを探索中...",
    "notification_width": 400,
    "notification_height": 150,
    "notification_position_x": 100,
    "notification_position_y": 100,
    "maximize_on_first_fail": True,
}

# Default maximum number of parallel PRs in "LLM working" state
# When this limit is reached, auto-assignment of new issues is paused to avoid rate limits
DEFAULT_MAX_LLM_WORKING_PARALLEL = 3

# Default value for check_process_before_autoraise
# When true, check if cat-window-watcher process is running and don't raise browser window if it is
DEFAULT_CHECK_PROCESS_BEFORE_AUTORAISE = True

# Default setting for displaying PR authors in CLI output
DEFAULT_DISPLAY_PR_AUTHOR = False

# Default setting for displaying LLM status timelines in CLI output
DEFAULT_DISPLAY_LLM_STATUS_TIMELINE = False

# Default setting for auto-update (disabled by default for safety)
DEFAULT_ENABLE_AUTO_UPDATE = False

# Default setting for saving pr_phase_snapshots (disabled by default for safety/privacy)
DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS = False

# Default setting for local repo auto-pull (disabled by default; display only by default)
DEFAULT_AUTO_GIT_PULL = False


def _validate_color_scheme(value: Any) -> str:
    """Validate that the color scheme is supported."""
    supported_schemes = get_supported_color_schemes()
    if not isinstance(value, str):
        raise ValueError(
            f"Configuration value 'color_scheme' must be a string ({', '.join(supported_schemes)}), "
            f"got {type(value).__name__}: {value}"
        )

    normalized = value.strip().lower()
    if normalized not in supported_schemes:
        raise ValueError(f"Unsupported color_scheme '{value}'. Supported schemes: {', '.join(supported_schemes)}")
    return normalized


def _load_custom_colors(config: Dict[str, Any]) -> Dict[str, str]:
    """Validate and normalize custom color overrides from config."""
    custom_colors = config.get("colors")
    if custom_colors is None:
        return {}

    if not isinstance(custom_colors, dict):
        print("Warning: [colors] section must be a table. Ignoring custom colors.")
        return {}

    validated_colors: Dict[str, str] = {}
    for key in SUPPORTED_COLOR_KEYS:
        if key not in custom_colors:
            continue
        try:
            validated_colors[key] = normalize_color_code(custom_colors[key], key)
        except ValueError as e:
            print(f"Warning: {e} Skipping '{key}'.")
    return validated_colors


def get_phase3_merge_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get phase3_merge configuration with defaults applied

    Args:
        config: Global configuration dictionary

    Returns:
        phase3_merge configuration with defaults for missing keys
    """
    user_config = config.get("phase3_merge", {})
    if not isinstance(user_config, dict):
        user_config = {}

    # Merge user config with defaults, user config takes precedence
    result = DEFAULT_PHASE3_MERGE_CONFIG.copy()
    result.update(user_config)
    return result


def validate_phase3_merge_config_required(config: Dict[str, Any], repo_owner: str, repo_name: str) -> None:
    """Validate that phase3_merge comment is explicitly configured when auto-merge is enabled

    When enable_execution_phase3_to_merge is true for a repository, the user MUST explicitly
    configure the comment in the [phase3_merge] section of config.toml.
    This is a safety measure to ensure users consciously set the merge comment.

    Args:
        config: Global configuration dictionary
        repo_owner: Repository owner
        repo_name: Repository name

    Raises:
        SystemExit: If auto-merge is enabled but comment is not explicitly configured
    """
    # Check if auto-merge is enabled for this repository
    exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
    if not exec_config.get("enable_execution_phase3_to_merge", False):
        # Auto-merge is not enabled, validation not required
        return

    # Auto-merge is enabled - check if comment is explicitly configured
    phase3_merge_section = config.get("phase3_merge")

    # Fail fast if [phase3_merge] section is missing
    if phase3_merge_section is None:
        print("\n" + "=" * 80)
        print("ERROR: Auto-merge configuration is missing")
        print("=" * 80)
        print(f"\nRepository: {repo_owner}/{repo_name}")
        print("enable_execution_phase3_to_merge = true")
        print("\nWhen auto-merge is enabled, you MUST explicitly configure the merge comment")
        print("in the [phase3_merge] section of config.toml.")
        print("\nPlease add the following to your config.toml:")
        print("\n[phase3_merge]")
        print(f'comment = "{DEFAULT_PHASE3_MERGE_CONFIG["comment"]}"')
        print("\nOr customize the comment to match your workflow.")
        print("=" * 80)
        raise SystemExit(1)

    # Fail fast if comment field is missing in [phase3_merge] section
    if not isinstance(phase3_merge_section, dict) or "comment" not in phase3_merge_section:
        print("\n" + "=" * 80)
        print("ERROR: Merge comment is not configured")
        print("=" * 80)
        print(f"\nRepository: {repo_owner}/{repo_name}")
        print("enable_execution_phase3_to_merge = true")
        print("\nWhen auto-merge is enabled, you MUST explicitly set the 'comment' field")
        print("in the [phase3_merge] section of config.toml.")
        print("\nPlease add the comment field to your [phase3_merge] section:")
        print("\n[phase3_merge]")
        print(f'comment = "{DEFAULT_PHASE3_MERGE_CONFIG["comment"]}"')
        print("\nOr customize the comment to match your workflow.")
        print("=" * 80)
        raise SystemExit(1)


def get_assign_to_copilot_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get assign_to_copilot configuration with defaults applied

    Args:
        config: Global configuration dictionary

    Returns:
        assign_to_copilot configuration with defaults for missing keys
    """
    user_config = config.get("assign_to_copilot", {})
    if not isinstance(user_config, dict):
        user_config = {}

    # Merge user config with defaults, user config takes precedence
    result = DEFAULT_ASSIGN_TO_COPILOT_CONFIG.copy()
    result.update(user_config)
    return result


def get_config_mtime(config_path: str = "config.toml") -> float:
    """Get the modification time of the configuration file

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Modification time as a timestamp (seconds since epoch)

    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    return os.path.getmtime(config_path)


def load_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Load configuration from TOML file

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Dictionary containing configuration data with validated settings

    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    # Validate max_llm_working_parallel setting
    if "max_llm_working_parallel" in config:
        value = config["max_llm_working_parallel"]
        if not isinstance(value, int) or value < 1:
            print(
                f"Warning: max_llm_working_parallel must be a positive integer, "
                f"got {type(value).__name__}: {value!r}. "
                f"Using default value: {DEFAULT_MAX_LLM_WORKING_PARALLEL}"
            )
            config["max_llm_working_parallel"] = DEFAULT_MAX_LLM_WORKING_PARALLEL
    if "display_pr_author" in config:
        try:
            config["display_pr_author"] = _validate_boolean_flag(config["display_pr_author"], "display_pr_author")
        except ValueError as e:
            print(f"Warning: {e}. Using default value: {DEFAULT_DISPLAY_PR_AUTHOR}")
            config["display_pr_author"] = DEFAULT_DISPLAY_PR_AUTHOR
    else:
        config["display_pr_author"] = DEFAULT_DISPLAY_PR_AUTHOR
    if "display_llm_status_timeline" in config:
        try:
            config["display_llm_status_timeline"] = _validate_boolean_flag(
                config["display_llm_status_timeline"], "display_llm_status_timeline"
            )
        except ValueError as e:
            print(f"Warning: {e}. Using default value: {DEFAULT_DISPLAY_LLM_STATUS_TIMELINE}")
            config["display_llm_status_timeline"] = DEFAULT_DISPLAY_LLM_STATUS_TIMELINE
    else:
        config["display_llm_status_timeline"] = DEFAULT_DISPLAY_LLM_STATUS_TIMELINE
    if "enable_pr_phase_snapshots" in config:
        try:
            config["enable_pr_phase_snapshots"] = _validate_boolean_flag(
                config["enable_pr_phase_snapshots"], "enable_pr_phase_snapshots"
            )
        except ValueError as e:
            print(f"Warning: {e}. Using default value: {DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS}")
            config["enable_pr_phase_snapshots"] = DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS
    else:
        config["enable_pr_phase_snapshots"] = DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS
    if "enable_auto_update" in config:
        try:
            config["enable_auto_update"] = _validate_boolean_flag(config["enable_auto_update"], "enable_auto_update")
        except ValueError as e:
            print(f"Warning: {e}. Using default value: {DEFAULT_ENABLE_AUTO_UPDATE}")
            config["enable_auto_update"] = DEFAULT_ENABLE_AUTO_UPDATE
    else:
        config["enable_auto_update"] = DEFAULT_ENABLE_AUTO_UPDATE
    if "auto_git_pull" in config:
        try:
            config["auto_git_pull"] = _validate_boolean_flag(config["auto_git_pull"], "auto_git_pull")
        except ValueError as e:
            print(f"Warning: {e}. Using default value: {DEFAULT_AUTO_GIT_PULL}")
            config["auto_git_pull"] = DEFAULT_AUTO_GIT_PULL
    else:
        config["auto_git_pull"] = DEFAULT_AUTO_GIT_PULL
    if "color_scheme" in config:
        try:
            config["color_scheme"] = _validate_color_scheme(config["color_scheme"])
        except ValueError as e:
            print(f"Warning: {e}. Using default value: {DEFAULT_COLOR_SCHEME}")
            config["color_scheme"] = DEFAULT_COLOR_SCHEME
    else:
        config["color_scheme"] = DEFAULT_COLOR_SCHEME

    # Apply color scheme immediately so downstream output uses it
    config["color_scheme"] = set_color_scheme(config["color_scheme"])

    # Apply optional custom color overrides
    custom_colors = _load_custom_colors(config)
    if custom_colors:
        apply_custom_colors(custom_colors)
    config["colors"] = {
        "phase1": Colors.YELLOW,
        "phase2": Colors.CYAN,
        "phase3": Colors.GREEN,
        "llm": Colors.MAGENTA,
        "url": Colors.BLUE,
    }

    return config


def print_config(*args, **kwargs):
    """Backward-compatible wrapper – lazily imports config_printer to avoid circular imports."""
    from . import config_printer

    return config_printer.print_config(*args, **kwargs)


def print_repo_execution_config(*args, **kwargs):
    """Backward-compatible wrapper – lazily imports config_printer to avoid circular imports."""
    from . import config_printer

    return config_printer.print_repo_execution_config(*args, **kwargs)



