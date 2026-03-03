"""
Display and UI functions for status summary and issues
"""

import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import github_client
from .colors import colorize_phase, colorize_url
from .config import (
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_assign_to_copilot_config,
    resolve_execution_config_for_repo,
)
from .github_client import assign_issue_to_copilot, get_issues_from_repositories
from .phase_detector import PHASE_LLM_WORKING, get_llm_working_progress_label
from .state_tracker import cleanup_old_pr_states, get_pr_state_time, set_pr_state_time
from .time_utils import format_elapsed_time

# Cross-iteration issue cache.
# Key: "owner/name", Value: list of issues / last known repository updatedAt.
# Cache is invalidated per-repo when its updatedAt changes, ensuring we always
# reflect any repository activity (issue open/close, PR updates, etc.).
# Using updatedAt instead of openIssueCount avoids false cache hits when one
# issue is closed and another is opened in the same iteration (count unchanged).
_cached_repo_issues: Dict[str, List[Dict[str, Any]]] = {}
_cached_repo_updated_at: Dict[str, str] = {}

# Upper bound for the limit parameter when fetching all issues from a repo batch.
# get_issues_from_repositories caps per-repo results at ISSUES_PER_REPO (50), so the
# real maximum is num_repos * 50.  This constant just needs to be larger than that.
_MAX_ISSUES_FETCH_LIMIT = 100_000


def reset_issues_cache() -> None:
    """Reset the issues cache (used in tests and on explicit invalidation)."""
    _cached_repo_issues.clear()
    _cached_repo_updated_at.clear()


def display_status_summary(
    all_prs: List[Dict[str, Any]],
    pr_phases: List[str],
    repos_with_prs: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """Display a concise summary of current PR status

    This summary helps users understand the overall status at a glance,
    especially useful on terminals with limited display lines.
    Uses the same format as process_pr() for consistency.

    Args:
        all_prs: List of all PRs
        pr_phases: List of phase strings corresponding to all_prs
        repos_with_prs: List of repositories with open PRs
        config: Optional configuration dict (uses display_pr_author when true)
    """
    print(f"\n{'=' * 50}")
    print("Status Summary:")
    print(f"{'=' * 50}")

    if not all_prs:
        print("  No open PRs to monitor")
        cleanup_old_pr_states([])
        return

    current_time = time.time()
    current_states = []

    # Display each PR using the same format as process_pr()
    display_pr_author = bool((config or {}).get("display_pr_author", False))
    for pr, phase in zip(all_prs, pr_phases):
        repo_info = pr.get("repository", {})
        repo_name = repo_info.get("name", "Unknown")
        title = pr.get("title", "Unknown")
        url = pr.get("url", "")
        author_login = (pr.get("author") or {}).get("login", "") or "Unknown"

        # Track state for elapsed time
        state_key = (url, phase)
        current_states.append(state_key)
        if get_pr_state_time(url, phase) is None:
            set_pr_state_time(url, phase, current_time)

        # Calculate elapsed time
        elapsed = current_time - get_pr_state_time(url, phase)

        # Display phase with colors using the same format
        progress_label = get_llm_working_progress_label(pr) if phase == PHASE_LLM_WORKING else None
        phase_display = colorize_phase(phase, progress_label)
        author_suffix = f" (Author: {author_login})" if display_pr_author else ""
        status_suffix = ""
        if phase == PHASE_LLM_WORKING:
            llm_statuses = pr.get("llm_statuses") or []
            if llm_statuses:
                status_suffix = f" (Latest LLM status: {llm_statuses[-1]})"
        base_line = f"  [{repo_name}] {phase_display}{status_suffix} {title}{author_suffix}"

        # Show elapsed time if state has persisted for more than 60 seconds
        if elapsed >= 60:
            elapsed_str = format_elapsed_time(elapsed)
            print(f"{base_line} (現在、検知してから{elapsed_str}経過)")
        else:
            print(base_line)

        # Show warning for LLM working PRs older than 30 minutes since creation
        if phase == PHASE_LLM_WORKING:
            created_at = pr.get("createdAt", "")
            if created_at:
                try:
                    # GitHub API returns ISO 8601 UTC timestamps ending with "Z"
                    # e.g. "2024-01-15T10:30:00Z"; replace Z with +00:00 for fromisoformat()
                    created_ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
                    if current_time - created_ts >= 1800:
                        print(
                            "    ⚠️  バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります。"
                            "PRを人力で開いてチェックしてください"
                        )
                except (ValueError, AttributeError):
                    pass

    # Clean up old PR states that are no longer present
    cleanup_old_pr_states(current_states)


def _resolve_assign_to_copilot_config(issue: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve assign_to_copilot configuration for a specific issue's repository

    Args:
        issue: Issue dictionary with repository information
        config: Global configuration dictionary (can be None)

    Returns:
        Configuration dictionary with assign_to_copilot settings
    """
    # Handle None config
    if config is None:
        return {"assign_to_copilot": {}}

    # Get repository-specific configuration
    repo_info = issue.get("repository", {})
    repo_owner = repo_info.get("owner", "")
    repo_name = repo_info.get("name", "")

    if repo_owner and repo_name:
        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
        # Check if any assignment flag is enabled for this repo
        if (
            exec_config.get("assign_good_first_old", False)
            or exec_config.get("assign_old", False)
            or exec_config.get("assign_ci_failure_old", False)
            or exec_config.get("assign_deploy_pages_failure_old", False)
        ):
            # Assignment enabled for this repo, use global assign_to_copilot settings with defaults
            return {"assign_to_copilot": get_assign_to_copilot_config(config)}
        else:
            # No assignment flags enabled
            return {"assign_to_copilot": {}}
    else:
        return {"assign_to_copilot": {}}


def display_issues_from_repos_without_prs(config: Optional[Dict[str, Any]] = None, llm_working_count: int = 0):
    """Display issues from repositories with no open PRs

    Args:
        config: Configuration dictionary (optional)
        llm_working_count: Number of PRs currently in "LLM working" state (default: 0)
    """
    print("Checking for repositories with no open PRs but with open issues...")

    try:
        repos_with_issues = github_client.get_repositories_with_no_prs_and_open_issues()

        if not repos_with_issues:
            print("  No repositories found with open issues and no open PRs")
        else:
            print(f"  Found {len(repos_with_issues)} repositories with open issues (no open PRs):")
            for repo in repos_with_issues:
                print(f"    - {repo['name']}: {repo['openIssueCount']} open issue(s)")

            issue_limit = config.get("issue_display_limit", 10) if config else 10

            # Fetch issues only for repos whose updatedAt has changed since last check.
            # On the very first run (empty cache) every repo is fetched.
            # Using updatedAt (instead of openIssueCount) correctly detects changes when
            # one issue is closed and another is opened in the same iteration.
            repos_to_fetch = [
                repo
                for repo in repos_with_issues
                if _cached_repo_updated_at.get(f"{repo['owner']}/{repo['name']}") != repo.get("updatedAt", "")
            ]

            if repos_to_fetch:
                # Single GraphQL call covering all changed repos, no server-side labels filter.
                # sort_by_number=True (CREATED_AT ASC) ensures the per-repo cap keeps the oldest
                # issues, which are the correct candidates for assignment selection.
                newly_fetched = get_issues_from_repositories(
                    repos_to_fetch,
                    limit=_MAX_ISSUES_FETCH_LIMIT,
                    sort_by_number=True,
                )

                # Group by repo and update cache
                newly_by_repo: Dict[str, List[Dict[str, Any]]] = {}
                for issue in newly_fetched:
                    r = issue["repository"]
                    key = f"{r['owner']}/{r['name']}"
                    newly_by_repo.setdefault(key, []).append(issue)

                for repo in repos_to_fetch:
                    key = f"{repo['owner']}/{repo['name']}"
                    _cached_repo_issues[key] = newly_by_repo.get(key, [])
                    _cached_repo_updated_at[key] = repo.get("updatedAt", "")

            # Combine cached issues for all current repos
            all_fetched_issues: List[Dict[str, Any]] = []
            for repo in repos_with_issues:
                key = f"{repo['owner']}/{repo['name']}"
                all_fetched_issues.extend(_cached_repo_issues.get(key, []))

            # Top N issues for display (sorted by last update, descending)
            top_issues = sorted(all_fetched_issues, key=lambda x: x.get("updatedAt", ""), reverse=True)[:issue_limit]

            assigned_issue_count = sum(1 for issue in top_issues if issue.get("assignees"))
            effective_llm_working_count = llm_working_count + assigned_issue_count

            if assigned_issue_count:
                print(f"  Detected {assigned_issue_count} open issue(s) with assignees; treating as LLM working load.")

            # Check if auto-assign feature is enabled in config
            # With the new design:
            # - Rulesets can specify "assign_good_first_old" to assign one old "good first issue" (oldest by issue number)
            # - Rulesets can specify "assign_ci_failure_old" to assign one old "ci-failure" issue (oldest by issue number)
            # - Rulesets can specify "assign_deploy_pages_failure_old" to assign one old "deploy-pages-failure" issue (oldest by issue number)
            # - Rulesets can specify "assign_old" to assign one old issue (oldest by issue number, any issue)
            # - All default to false
            # - Priority: ci-failure > deploy-pages-failure > good first issue > old issue

            # Check if any repository has auto-assign enabled
            # We need to check all repos to determine which mode to use
            # Also filter repos to only those with assignment properly enabled
            any_ci_failure = False
            any_deploy_pages_failure = False
            any_good_first = False
            any_old = False
            repos_with_ci_failure_enabled = []
            repos_with_deploy_pages_failure_enabled = []
            repos_with_good_first_enabled = []
            repos_with_old_enabled = []

            # Only check for assign flags if config is not None
            if config:
                for repo in repos_with_issues:
                    repo_owner = repo.get("owner", "")
                    repo_name = repo.get("name", "")
                    if repo_owner and repo_name:
                        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
                        # Check if any assignment flag is enabled
                        if exec_config.get("assign_ci_failure_old", False):
                            any_ci_failure = True
                            repos_with_ci_failure_enabled.append(repo)
                        if exec_config.get("assign_deploy_pages_failure_old", False):
                            any_deploy_pages_failure = True
                            repos_with_deploy_pages_failure_enabled.append(repo)
                        if exec_config.get("assign_good_first_old", False):
                            any_good_first = True
                            repos_with_good_first_enabled.append(repo)
                        if exec_config.get("assign_old", False):
                            any_old = True
                            repos_with_old_enabled.append(repo)

            # Check if we should pause auto-assignment due to too many LLM working PRs
            # Get max_llm_working_parallel setting from config (default: 3)
            max_llm_working = DEFAULT_MAX_LLM_WORKING_PARALLEL
            if config:
                max_llm_working = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)

            # Check if we should pause auto-assignment
            should_pause_assignment = effective_llm_working_count >= max_llm_working

            if should_pause_assignment:
                print(f"\n{'=' * 50}")
                print(f"LLM workingのPR数が最大並列数（{max_llm_working}）に達しています。")
                print(
                    "現在のLLM workingカウント: "
                    f"{effective_llm_working_count} (PR: {llm_working_count}, assigned issues: {assigned_issue_count})"
                )
                print("レートリミット回避のため、新しいissueの自動assignを保留します。")
                print(f"{'=' * 50}")
                # Skip assignment but continue to display issues
            else:
                # Always try to check for issues to assign (batteries-included)
                # Individual repositories must explicitly enable via rulesets for actual assignment
                # Priority: ci-failure > deploy-pages-failure > good first issue > old issue (all sorted by issue number ascending)
                assignment_modes = [
                    ("ci-failure", repos_with_ci_failure_enabled, ["ci-failure"], any_ci_failure),
                    (
                        "deploy-pages-failure",
                        repos_with_deploy_pages_failure_enabled,
                        ["deploy-pages-failure"],
                        any_deploy_pages_failure,
                    ),
                    ("good first issue", repos_with_good_first_enabled, ["good first issue"], any_good_first),
                    ("issue", repos_with_old_enabled, None, any_old),
                ]

                for label_name, repos_list, label_filter, is_enabled in assignment_modes:
                    if not is_enabled:
                        continue

                    print(f"\n{'=' * 50}")
                    print(f"Checking for the oldest '{label_name}' to auto-assign to Copilot...")
                    print(f"{'=' * 50}")

                    # Filter candidates from the already-fetched issue cache (no extra GraphQL query).
                    repos_set = {(r["owner"], r["name"]) for r in repos_list}
                    candidate_issues = [
                        issue
                        for issue in all_fetched_issues
                        if (issue["repository"]["owner"], issue["repository"]["name"]) in repos_set
                        and (label_filter is None or any(lbl in issue.get("labels", []) for lbl in label_filter))
                    ]
                    # Fallback: if no issues match the label_filter, it may be because the target
                    # label sits beyond the labels(first: 10) limit fetched by the GraphQL query,
                    # which would otherwise silently skip potentially assignable issues.
                    # In that case, fall back to all issues in the target repos so at least the
                    # oldest unassigned issue gets considered (it may or may not carry the target
                    # label; the reviewer must verify manually if needed).
                    if not candidate_issues and label_filter is not None:
                        candidate_issues = [
                            issue
                            for issue in all_fetched_issues
                            if (issue["repository"]["owner"], issue["repository"]["name"]) in repos_set
                        ]
                    candidate_issues.sort(key=lambda x: x["number"])
                    candidate_issues = candidate_issues[:1]

                    if candidate_issues:
                        issue = candidate_issues[0]
                        print(f"\n  Found oldest '{label_name}' (sorted by issue number, ascending):")
                        print(f"  #{issue['number']}: {issue['title']}")
                        print(f"     URL: {colorize_url(issue['url'])}")
                        labels = issue.get("labels", [])
                        label_str = ", ".join(str(label) for label in labels)
                        print(f"     Labels: {label_str}")
                        print("\n  Attempting to assign to Copilot...")

                        temp_config = _resolve_assign_to_copilot_config(issue, config)
                        success = assign_issue_to_copilot(issue, temp_config)
                        if not success:
                            print("  Assignment failed - will retry on next iteration")
                        # Invalidate cache for the assigned repo so the next iteration re-fetches
                        # fresh issue data (including up-to-date assignees), ensuring that
                        # assigned_issue_count remains accurate and max_llm_working_parallel is enforced.
                        repo_info = issue.get("repository", {})
                        cache_key = f"{repo_info.get('owner', '')}/{repo_info.get('name', '')}"
                        _cached_repo_issues.pop(cache_key, None)
                        _cached_repo_updated_at.pop(cache_key, None)
                        break
                    else:
                        if label_name == "issue":
                            print("  No issues found in repositories without open PRs")
                        else:
                            print(f"  No '{label_name}' issues found in repositories without open PRs")

            # Then, show top N issues from these repositories
            print(f"\n{'=' * 50}")
            print(f"Fetching top {issue_limit} issues from these repositories...")
            print(f"{'=' * 50}")

            if not top_issues:
                print("  No issues found")
            else:
                print(f"\n  Top {len(top_issues)} issues (sorted by last update, descending):\n")
                for idx, issue in enumerate(top_issues, 1):
                    print(f"  {idx}. #{issue['number']}: {issue['title']}")
                    print(f"     URL: {colorize_url(issue['url'])}")
                    print()
    except Exception as e:
        print(f"  Error fetching issues: {e}")
        traceback.print_exc()
