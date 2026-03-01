"""
GitHub Pages deployment monitoring module

Detects when the latest main branch commit is deployed to GitHub Pages,
and optionally opens the browser to the Pages URL or GitHub Actions page.
"""

import json
import subprocess
import webbrowser
from typing import Any, Dict, List, Optional, Set

from .browser_automation import (
    _can_open_browser,
    _get_remaining_cooldown,
    _record_browser_open,
    _should_autoraise_window,
)
from .config import resolve_execution_config_for_repo

# Track which repo+SHA combinations have been handled (browser opened or dry-run shown)
# Key format: "{owner}/{repo}@{sha}" for deployed, "{owner}/{repo}@errored:{sha}" for errored
_pages_browser_opened: Set[str] = set()


def get_main_branch_sha(owner: str, repo: str) -> Optional[str]:
    """Get the latest commit SHA on the main branch via gh api

    Note: This function assumes the default branch is named 'main'.
    Repositories using a different default branch name (e.g., 'master') are not supported.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Commit SHA string, or None if unavailable (e.g., Pages not enabled, API error,
        or repository does not have a 'main' branch)
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/branches/main", "--jq", ".commit.sha"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        sha = result.stdout.strip()
        return sha if sha and sha != "null" else None
    except subprocess.CalledProcessError:
        return None


def get_pages_latest_build(owner: str, repo: str) -> Optional[Dict[str, Any]]:
    """Get the latest GitHub Pages build via gh api

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Latest build dict with keys like 'status', 'commit', or None if unavailable
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/pages/builds/latest"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        text = result.stdout.strip()
        if not text or text == "null":
            return None
        return json.loads(text)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def get_pages_url(owner: str, repo: str) -> Optional[str]:
    """Get GitHub Pages URL via gh api

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Pages HTML URL string, or None if unavailable
    """
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/pages", "--jq", ".html_url"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        url = result.stdout.strip()
        return url if url and url != "null" else None
    except subprocess.CalledProcessError:
        return None


def check_pages_deployment(owner: str, repo: str) -> Dict[str, Any]:
    """Check GitHub Pages deployment status for a repository

    Compares the latest main branch commit SHA with the latest Pages build commit.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Dict with keys:
        - status: "deployed", "errored", "pending", or "unknown"
        - sha: main branch SHA (or None)
        - build_sha: Pages build commit SHA (or None)
        - build_status: raw Pages build status string (or None)
    """
    main_sha = get_main_branch_sha(owner, repo)

    if main_sha is None:
        return {"status": "unknown", "sha": None, "build_sha": None, "build_status": None}

    build = get_pages_latest_build(owner, repo)

    if build is None:
        return {"status": "pending", "sha": main_sha, "build_sha": None, "build_status": None}

    build_status = build.get("status")
    build_sha = build.get("commit")

    if build_status == "errored":
        return {"status": "errored", "sha": main_sha, "build_sha": build_sha, "build_status": build_status}

    if build_status == "built" and build_sha == main_sha:
        return {"status": "deployed", "sha": main_sha, "build_sha": build_sha, "build_status": build_status}

    return {"status": "pending", "sha": main_sha, "build_sha": build_sha, "build_status": build_status}


def process_pages_deployment(owner: str, repo: str, config: Optional[Dict[str, Any]] = None) -> None:
    """Check GitHub Pages deployment and act on the result

    Detects if deployment is complete or errored:
    - "deployed": opens Pages URL in browser (or dry-run message). Tracked via
      _pages_browser_opened so the browser is only opened once per commit SHA.
    - "errored": opens GitHub Actions page in browser (or dry-run message). Tracked
      similarly, so the browser is only opened once per errored build SHA.
    - "pending": prints progress info on every iteration (not tracked).
    - "unknown": silently skips (Pages not enabled or API error).

    Args:
        owner: Repository owner
        repo: Repository name
        config: Configuration dictionary (used for exec flags and browser settings)
    """
    result = check_pages_deployment(owner, repo)
    status = result["status"]
    main_sha = result["sha"] or ""
    build_sha = result["build_sha"] or ""
    repo_key = f"{owner}/{repo}"

    exec_config = resolve_execution_config_for_repo(config or {}, owner, repo)
    execution_enabled = exec_config.get("enable_execution_pages_open", False)

    if status == "deployed":
        deploy_key = f"{repo_key}@{main_sha}"
        if deploy_key in _pages_browser_opened:
            return

        print(f"  [{repo}] ✅ GitHub Pages deployed (SHA: {main_sha[:7]})")
        if execution_enabled:
            pages_url = get_pages_url(owner, repo)
            if pages_url:
                if not _can_open_browser():
                    remaining = _get_remaining_cooldown()
                    print(
                        f"    ⏳ Browser cooldown in effect. "
                        f"Please wait {int(remaining)} more seconds before opening next page."
                    )
                    return
                autoraise = _should_autoraise_window(config)
                webbrowser.open(pages_url, autoraise=autoraise)
                _record_browser_open()
                print(f"    Browser opened: {pages_url}")
            else:
                print(f"    ⚠️ Could not retrieve Pages URL for {repo_key}")
        else:
            pages_url = get_pages_url(owner, repo)
            url_display = pages_url if pages_url else f"https://{owner}.github.io/{repo}/"
            print(f"    [DRY-RUN] Would open browser to {url_display} (enable_execution_pages_open=false)")
        _pages_browser_opened.add(deploy_key)

    elif status == "errored":
        error_key = f"{repo_key}@errored:{build_sha or main_sha}"
        if error_key in _pages_browser_opened:
            return

        sha_display = (build_sha or main_sha)[:7] if (build_sha or main_sha) else "unknown"
        print(f"  [{repo}] ❌ GitHub Pages build ERRORED (SHA: {sha_display})")
        actions_url = f"https://github.com/{owner}/{repo}/actions"
        if execution_enabled:
            if not _can_open_browser():
                remaining = _get_remaining_cooldown()
                print(
                    f"    ⏳ Browser cooldown in effect. "
                    f"Please wait {int(remaining)} more seconds before opening next page."
                )
                return
            autoraise = _should_autoraise_window(config)
            webbrowser.open(actions_url, autoraise=autoraise)
            _record_browser_open()
            print(f"    Browser opened (Actions): {actions_url}")
        else:
            print(f"    [DRY-RUN] Would open browser to {actions_url} (enable_execution_pages_open=false)")
        _pages_browser_opened.add(error_key)

    elif status == "pending":
        sha_short = main_sha[:7] if main_sha else "N/A"
        build_short = build_sha[:7] if build_sha else "N/A"
        print(f"  [{repo}] ⏳ GitHub Pages deployment pending (main: {sha_short}, build: {build_short})")

    # status == "unknown": silently skip (Pages not enabled or API error)


def get_pages_repos_from_config(config: Dict[str, Any], current_user: str) -> List[Dict[str, str]]:
    """Get list of repos configured for Pages checking from rulesets

    Extracts repos where enable_execution_pages_open is explicitly set (true or false)
    in any ruleset. Repos set to false are included so that dry-run detection messages
    are shown (the actual browser opening is skipped by process_pages_deployment).
    Repos with pattern "all" are skipped (too expensive to enumerate).

    Args:
        config: Configuration dictionary
        current_user: GitHub username (used as owner for matched repos)

    Returns:
        List of dicts with "name" and "owner" keys
    """
    repos = []
    seen: Set[str] = set()
    for ruleset in config.get("rulesets", []):
        if not isinstance(ruleset, dict):
            continue
        if "enable_execution_pages_open" not in ruleset:
            continue  # Skip rulesets that don't mention Pages at all
        for pattern in ruleset.get("repositories", []):
            if not isinstance(pattern, str):
                continue
            if pattern.lower() == "all":
                continue  # Cannot enumerate all repos without additional API calls
            if pattern not in seen:
                repos.append({"name": pattern, "owner": current_user})
                seen.add(pattern)
    return repos


def check_pages_deployments_for_repos(repos: List[Dict[str, Any]], config: Optional[Dict[str, Any]] = None) -> None:
    """Check GitHub Pages deployment status for a list of repositories

    Processes all repos in the list; use get_pages_repos_from_config to get
    the appropriate repos filtered by Pages configuration in rulesets.

    Args:
        repos: List of repo dicts with "owner" and "name" keys
        config: Configuration dictionary
    """
    if not config or not repos:
        return

    checked: Set[str] = set()
    for repo in repos:
        owner = repo.get("owner", "")
        name = repo.get("name", "")
        if not owner or not name:
            continue
        repo_key = f"{owner}/{name}"
        if repo_key in checked:
            continue
        checked.add(repo_key)
        try:
            process_pages_deployment(owner, name, config)
        except Exception as e:
            print(f"  [{name}] Error checking Pages deployment: {e}")
