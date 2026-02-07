"""
Comment management for posting and checking PR comments
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .github_client import get_existing_comments

CLAUDE_AGENT_LOGINS = {
    "claude",
    "claude-ai",
    "claude-dev",
    "claude-coding-agent",
}

CODEX_AGENT_LOGINS = {
    "codex",
    "codex-ai",
    "codex-coding-agent",
}


def _get_agent_mention(pr: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> str:
    """Resolve which agent to mention based on PR author"""
    coding_agent_config = (config or {}).get("coding_agent", {})
    custom_agent_name = coding_agent_config.get("agent_name")
    if isinstance(custom_agent_name, str) and custom_agent_name.strip():
        return custom_agent_name.strip()

    author_login = (pr.get("author") or {}).get("login", "")
    normalized = author_login.lower()

    if normalized in CLAUDE_AGENT_LOGINS or normalized.endswith("-claude-coding-agent"):
        return "@claude[agent]"

    if normalized in CODEX_AGENT_LOGINS or normalized.endswith("-codex-coding-agent"):
        return "@codex[agent]"

    return "@copilot"


def has_copilot_apply_comment(comments: List[Dict[str, Any]], agent_mention: str = "@copilot") -> bool:
    """Check if an apply comment for the agent already exists

    Args:
        comments: List of comment dictionaries
        agent_mention: Agent mention to search for (defaults to Copilot)

    Returns:
        True if comment exists, False otherwise
    """
    target = f"{agent_mention} apply changes"

    for comment in comments:
        body = comment.get("body", "")
        if target in body:
            return True
    return False


def post_phase2_comment(pr: Dict[str, Any], repo_dir: Path = None, config: Optional[Dict[str, Any]] = None) -> Optional[bool]:
    """Post a comment to PR when phase2 is detected

    Args:
        pr: PR data dictionary containing url and reviews
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        True if comment was posted successfully
        None if comment already exists (skipped)
        False if posting failed (e.g., invalid PR URL, subprocess error)
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return False

    agent_mention = _get_agent_mention(pr, config)

    # Check if we already posted a comment for this agent
    existing_comments = get_existing_comments(pr_url, repo_dir)
    if has_copilot_apply_comment(existing_comments, agent_mention):
        print("    Comment already exists, skipping")
        return None

    # Construct comment body linking to the PR
    # Reviews don't have direct URLs in the JSON, but we can link to the PR
    comment_body = f"{agent_mention} apply changes based on the comments in [this pull request]({pr_url})"

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_body]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False


def post_phase3_comment(pr: Dict[str, Any], comment_text: str, repo_dir: Path = None) -> bool:
    """Post a comment to PR when phase3 merge is about to happen

    Args:
        pr: PR data dictionary containing url
        comment_text: The comment text to post (from configuration)
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        True if comment was posted successfully, False otherwise
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return False

    # No need to check for existing comment - we want to post this comment before merging

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_text]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False
