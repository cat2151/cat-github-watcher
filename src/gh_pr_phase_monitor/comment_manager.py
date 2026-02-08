"""
Comment management for posting and checking PR comments
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .github_client import get_existing_comments

CLAUDE_AGENT_LOGINS = {
    "anthropic-code-agent",
}

CODEX_AGENT_LOGINS = {
    "openai-code-agent",
}


def _get_agent_mention(pr: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> str:
    """Resolve which agent to mention, preferring config override, then PR author, then default

    Precedence:
        1. If config["coding_agent"]["agent_name"] is a non-empty string, use that (after stripping).
        2. Otherwise, detect the agent based on the PR author's login (Claude/Codex heuristics).
        3. If no match is found, fall back to "@copilot".
    """
    raw_coding_agent_config = (config or {}).get("coding_agent", {})
    coding_agent_config = raw_coding_agent_config if isinstance(raw_coding_agent_config, dict) else {}
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


def post_phase2_comment(
    pr: Dict[str, Any], repo_dir: Path = None, config: Optional[Dict[str, Any]] = None
) -> Optional[bool]:
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


def has_problematic_pr_title(title: str) -> bool:
    """Check if PR title indicates addressing review comments

    Args:
        title: PR title to check

    Returns:
        True if title is problematic (e.g., "Addressing PR comments", contains "PR review"), False otherwise
    """
    if not title:
        return False

    title_lower = title.lower()

    # Check for exact match or common variations
    problematic_patterns = [
        "addressing pr comments",
        "address pr comments",
        "pr review",
    ]

    return any(pattern in title_lower for pattern in problematic_patterns)


def has_pr_title_fix_comment(comments: List[Dict[str, Any]]) -> bool:
    """Check if a PR title fix comment already exists

    Args:
        comments: List of comment dictionaries

    Returns:
        True if comment exists, False otherwise
    """
    # Look for the unique marker text in the comment
    # We only check the marker text (not agent mention) to prevent duplicates
    # even if the mention changes (e.g., via config override or detection logic changes)
    marker_text = "PR titleとPR冒頭を、以下の方針で修正してください："

    for comment in comments:
        body = comment.get("body", "")
        if marker_text in body:
            return True
    return False


def post_pr_title_fix_comment(
    pr: Dict[str, Any], repo_dir: Path = None, config: Optional[Dict[str, Any]] = None
) -> Optional[bool]:
    """Post a comment to PR when title indicates addressing review comments

    Args:
        pr: PR data dictionary containing url and title
        repo_dir: Repository directory (optional, not used when working with URLs)
        config: Configuration dictionary (optional, used for agent detection)

    Returns:
        True if comment was posted successfully
        None if comment already exists (skipped)
        False if posting failed (e.g., invalid PR URL, subprocess error)
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return False

    agent_mention = _get_agent_mention(pr, config)

    # Check if we already posted a comment (check marker text only to prevent
    # duplicates even if mention changes via config or detection logic)
    existing_comments = get_existing_comments(pr_url, repo_dir)
    if has_pr_title_fix_comment(existing_comments):
        print("    PR title fix comment already exists, skipping")
        return None

    # Construct the comment body
    comment_body = f"""{agent_mention}
- PR titleとPR冒頭を、以下の方針で修正してください：
    - これまでの課題：
        - PR titleとPR冒頭に、「PR review commentに対応： レビュー指摘されたxxxを修正」のように書いてあるのはNGです。
        - なぜなら、将来git logを見たとき、このPRが何を改善したのかが分かりません。
    - 修正方針：
        - PR titleとPR冒頭に、「PR review commentに対応： レビュー指摘されたxxxを修正」のように書くことを禁止します。
        - PR titleとPR冒頭に、「このPR全体が達成したことの中核」を書いてください。
    - user向け補足：
        - この問題は単に、agentの実装のバグの後始末の応急対策です。
        - agentは指示を受け取ってPR titleとPR冒頭を修正したあと「修正できません」という回答をしますが、それもバグです。
        - ですので気にしなくてOKです。今後、この応急対策が不要になることを希望しています。"""

    cmd = ["gh", "pr", "comment", pr_url, "--body", comment_body]

    try:
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    Error posting PR title fix comment: {e}")
        stderr = getattr(e, "stderr", "No stderr available")
        print(f"    stderr: {stderr}")
        return False
