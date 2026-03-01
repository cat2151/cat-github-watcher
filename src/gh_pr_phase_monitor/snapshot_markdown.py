"""
Markdown formatting utilities for PR phase snapshots.
"""

import json
from typing import Any, Dict, List

from .phase_detector import PHASE_LLM_WORKING
from .snapshot_path_utils import _extract_pr_number


def _escape_newlines(value: str) -> str:
    """Escape newline and carriage return characters in strings for markdown readability.

    Args:
        value: String value to escape

    Returns:
        String with escaped newlines and carriage returns
    """
    return value.replace("\n", "\\n").replace("\r", "\\r")


def _json_to_markdown(data: Any, indent_level: int = 0) -> str:
    """Convert JSON data to a nested markdown bullet list representation.

    Args:
        data: JSON data to convert (dict, list, or primitive)
        indent_level: Current indentation level for nested structures

    Returns:
        Markdown-formatted string representation
    """
    indent = "  " * indent_level
    lines = []

    if isinstance(data, dict):
        for key, value in data.items():
            if value is None:
                lines.append(f"{indent}- **{key}**: null")
            elif isinstance(value, (str, int, float, bool)):
                # Escape newlines in string values for readability
                if isinstance(value, str):
                    value_str = _escape_newlines(value)
                else:
                    value_str = str(value)
                lines.append(f"{indent}- **{key}**: {value_str}")
            elif isinstance(value, dict):
                if not value:
                    lines.append(f"{indent}- **{key}**: {{}}")
                else:
                    lines.append(f"{indent}- **{key}**:")
                    lines.append(_json_to_markdown(value, indent_level + 1))
            elif isinstance(value, list):
                if not value:
                    lines.append(f"{indent}- **{key}**: []")
                else:
                    lines.append(f"{indent}- **{key}**: ({len(value)} items)")
                    lines.append(_json_to_markdown(value, indent_level + 1))
            else:
                lines.append(f"{indent}- **{key}**: {value}")
    elif isinstance(data, list):
        for idx, item in enumerate(data, start=1):
            if isinstance(item, (str, int, float, bool)):
                if isinstance(item, str):
                    item_str = _escape_newlines(item)
                else:
                    item_str = str(item)
                lines.append(f"{indent}- [{idx}]: {item_str}")
            elif isinstance(item, dict):
                if not item:
                    lines.append(f"{indent}- [{idx}]: {{}}")
                else:
                    lines.append(f"{indent}- [{idx}]:")
                    lines.append(_json_to_markdown(item, indent_level + 1))
            elif isinstance(item, list):
                if not item:
                    lines.append(f"{indent}- [{idx}]: []")
                else:
                    lines.append(f"{indent}- [{idx}]: ({len(item)} items)")
                    lines.append(_json_to_markdown(item, indent_level + 1))
            else:
                lines.append(f"{indent}- [{idx}]: {item}")
    else:
        # Primitive value at root level
        if isinstance(data, str):
            lines.append(_escape_newlines(data))
        else:
            lines.append(str(data))

    return "\n".join(lines)


def _filter_reactions(comment_nodes: Any) -> List[Dict[str, Any]]:
    """Filter out comments without any reactions and drop zero-count reaction groups."""
    if not isinstance(comment_nodes, list):
        return []

    filtered_comments: List[Dict[str, Any]] = []
    for comment in comment_nodes:
        reaction_groups = []
        for group in comment.get("reactionGroups") or []:
            count = (group.get("users") or {}).get("totalCount", 0)
            if count:
                reaction_groups.append(group)

        if reaction_groups:
            comment_copy = dict(comment)
            comment_copy["reactionGroups"] = reaction_groups
            filtered_comments.append(comment_copy)

    return filtered_comments


def _prepare_markdown_raw(pr: Dict[str, Any]) -> str:
    """Prepare a markdown-friendly representation of the PR with filters applied."""
    pr_copy = json.loads(json.dumps(pr, ensure_ascii=False))
    pr_copy["commentNodes"] = _filter_reactions(pr_copy.get("commentNodes", []))
    comments_value = pr_copy.get("comments")
    if isinstance(comments_value, list):
        pr_copy["comments"] = _filter_reactions(comments_value)

    return _json_to_markdown(pr_copy)


def _summarize_reactions(comment_nodes: Any) -> List[str]:
    """Return human-readable summaries of reaction groups."""
    summaries: List[str] = []
    if not isinstance(comment_nodes, list):
        return summaries

    for idx, comment in enumerate(comment_nodes, start=1):
        for group in comment.get("reactionGroups") or []:
            count = (group.get("users") or {}).get("totalCount", 0)
            if count:
                content = group.get("content", "UNKNOWN")
                summaries.append(f"Comment {idx}: {content} x{count}")

    return summaries


def _summarize_review_threads(review_threads: Any) -> str:
    """Summarize unresolved review threads."""
    if not isinstance(review_threads, list):
        return "n/a"

    unresolved = sum(
        1 for thread in review_threads if not thread.get("isResolved", False) and not thread.get("isOutdated", False)
    )
    return f"{unresolved} unresolved"


def _build_markdown(
    pr: Dict[str, Any],
    reason: str,
    timestamp_str: str,
    reactions_summary: List[str],
    snapshot_dir_name: str,
    markdown_raw_snapshot: str,
) -> str:
    """Build human-readable markdown representation of the snapshot."""
    repo_info = pr.get("repository") or {}
    owner = repo_info.get("owner", "unknown")
    name = repo_info.get("name", "unknown")
    url = pr.get("url", "unknown")
    pr_number = _extract_pr_number(url)
    title = pr.get("title", "")
    author = (pr.get("author") or {}).get("login", "unknown")
    reviews = pr.get("reviews") or []
    latest_review = reviews[-1] if reviews else {}
    review_threads = pr.get("reviewThreads")
    body_text = (pr.get("body") or "").replace("\r\n", "\n")

    lines = [
        f"# PR snapshot {owner}/{name} #{pr_number}",
        "",
        f"- Timestamp: {timestamp_str}",
        f"- Snapshot directory: {snapshot_dir_name}",
        f"- URL: {url}",
        f"- Title: {title}",
        f"- Author: {author}",
        f"- Phase decision: {PHASE_LLM_WORKING}",
        f"- Reason: {reason}",
        "",
        "## Reviews",
        f"- Review count: {len(reviews)}",
        f"- Latest review state: {latest_review.get('state', 'unknown') or 'unknown'}",
        "",
        "## Review threads",
        f"- {_summarize_review_threads(review_threads)}",
        "",
        "## Comment reactions",
    ]

    if reactions_summary:
        lines.extend(f"- {item}" for item in reactions_summary)
    else:
        lines.append("- None")

    lines.append("")
    if body_text:
        lines.append("## Body (rendered)")
        lines.append("```text")
        lines.append(body_text)
        lines.append("```")
        lines.append("")

    lines.append("## Raw snapshot")
    lines.append(f"- Saved at: {timestamp_str}")
    lines.append("")
    lines.append(markdown_raw_snapshot)

    return "\n".join(lines)
