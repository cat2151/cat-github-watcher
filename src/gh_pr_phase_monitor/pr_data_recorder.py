"""
Utilities for capturing PR snapshots to aid debugging of phase detection.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .phase_detector import PHASE_LLM_WORKING, has_comments_with_reactions, update_comment_reaction_resolution

# Snapshots are stored alongside screenshots (not inside) for easy discovery
DEFAULT_SNAPSHOT_BASE_DIR = Path("pr_phase_snapshots")

# Once flag to prevent duplicate snapshots within the same iteration
_recorded_in_current_iteration: Set[str] = set()

# Store previous iteration's content for comparison (PR key -> {json, html_md})
_previous_pr_content: Dict[str, Dict[str, str]] = {}


def _sanitize_component(value: Any) -> str:
    """Sanitize a path component by replacing unsafe characters."""
    text = str(value) if value is not None else "unknown"
    text = text.strip() or "unknown"
    return re.sub(r"[^A-Za-z0-9_.-]", "_", text)


def _extract_pr_number(pr_url: str) -> str:
    """Extract PR number from URL if possible."""
    match = re.search(r"/pull/(\d+)", pr_url or "")
    if match:
        return match.group(1)
    return "unknown"


def _format_timestamp(current_time: Optional[datetime] = None) -> str:
    """Format timestamp for filenames."""
    return (current_time or datetime.now()).strftime("%Y%m%d_%H%M%S")


def _build_snapshot_dir_name(pr: Dict[str, Any]) -> str:
    """Build snapshot directory name like owner_repo_PR123 (no timestamp)."""
    repo_info = pr.get("repository") or {}
    owner = _sanitize_component(repo_info.get("owner", "unknown"))
    name = _sanitize_component(repo_info.get("name", "unknown"))
    pr_number = _extract_pr_number(pr.get("url", ""))
    return f"{owner}_{name}_PR{pr_number}"


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


def _eyes_reaction_finished(html_markdown: str) -> bool:
    """Detect whether eyes reactions were followed by a 'finished work' marker in the snapshot."""
    if not html_markdown:
        return False

    lowered = html_markdown.lower()
    eyes_index = lowered.rfind("reacted with eyes emoji")
    if eyes_index == -1:
        return False

    return lowered.find("finished work", eyes_index) != -1


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


def _prepare_markdown_raw(pr: Dict[str, Any]) -> str:
    """Prepare a markdown-friendly representation of the PR with filters applied."""
    pr_copy = json.loads(json.dumps(pr, ensure_ascii=False))
    pr_copy["commentNodes"] = _filter_reactions(pr_copy.get("commentNodes", []))
    pr_copy["comments"] = _filter_reactions(pr_copy.get("comments", []))

    return _json_to_markdown(pr_copy)


def _write_if_changed(path: Path, content: str) -> None:
    """Write content to a file only when it changed."""
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == content:
                return
        except OSError:
            # If reading fails (permissions/I/O), overwrite with new content below
            pass
    path.write_text(content, encoding="utf-8")


def _fetch_pr_html(pr_url: str) -> Optional[str]:
    """Fetch PR HTML page using curl.

    Args:
        pr_url: The PR URL to fetch

    Returns:
        HTML content as string, or None if fetch fails
    """
    try:
        result = subprocess.run(
            ["curl", "-L", "-s", pr_url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        # Silently fail on network/timeout errors - HTML fetch is optional
        pass
    return None


def _html_to_simple_markdown(html: Optional[str]) -> str:
    """Convert HTML to simple markdown for better readability.

    This is a basic conversion without external dependencies.
    It extracts text content and attempts to preserve structure.

    Improvements:
    - Removes header content before prc-PageLayout-Content div
    - Removes footer content and everything after
    - Consolidates consecutive blank lines (including space-only lines)
    - Preserves whitespace inside code blocks (pre/code tags)

    Args:
        html: HTML content as string, or None

    Returns:
        Simplified markdown representation
    """
    if not html:
        return ""

    text = html

    # Remove header content: keep only content from prc-PageLayout-Content onwards
    # Look for the div with class containing "prc-PageLayout-Content"
    content_match = re.search(r'<div[^>]*class="[^"]*prc-PageLayout-Content[^"]*"[^>]*>', text, flags=re.IGNORECASE)
    if content_match:
        # Keep everything from this div onwards
        text = text[content_match.start() :]

    # Remove footer content: remove everything from <footer> tag onwards
    footer_match = re.search(r"<footer[^>]*>", text, flags=re.IGNORECASE)
    if footer_match:
        # Keep everything before the footer
        text = text[: footer_match.start()]

    # Remove script and style tags with their content
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Convert common HTML elements to markdown
    # Headers
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", text, flags=re.DOTALL | re.IGNORECASE)

    # Links
    text = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r"[\2](\1)", text, flags=re.DOTALL | re.IGNORECASE)

    # Bold and italic
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.DOTALL | re.IGNORECASE)

    # Code blocks
    text = re.sub(r"<pre[^>]*>(.*?)</pre>", r"```\n\1\n```", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.DOTALL | re.IGNORECASE)

    # Lists
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", text, flags=re.DOTALL | re.IGNORECASE)

    # Paragraphs and line breaks
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Clean up excessive whitespace while preserving code block formatting
    # Process line by line to consolidate blank lines without affecting code blocks
    lines = text.split("\n")
    cleaned_lines = []
    prev_blank = False
    in_code_block = False

    for line in lines:
        # Track code block boundaries (markdown fenced code blocks)
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            cleaned_lines.append(line)
            prev_blank = False
            continue

        # Inside code blocks, preserve all whitespace exactly as-is
        if in_code_block:
            cleaned_lines.append(line)
            prev_blank = False
            continue

        # Outside code blocks, consolidate blank lines and normalize leading/trailing spaces
        is_blank = line.strip() == ""
        if is_blank:
            if not prev_blank:
                cleaned_lines.append("")
            prev_blank = True
        else:
            # For non-blank lines outside code blocks, only strip trailing whitespace
            # Keep leading whitespace for list indentation, but normalize multiple spaces
            cleaned_lines.append(line.rstrip())
            prev_blank = False

    text = "\n".join(cleaned_lines)

    return text.strip()


def _split_status_tokens(text: str, seen: Set[str]) -> List[str]:
    """Split potential status text into unique, lowercased tokens."""
    statuses: List[str] = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]*", text or ""):
        token_lower = token.lower()
        if token_lower in seen:
            continue
        if token_lower in {"llm", "status"}:
            continue
        seen.add(token_lower)
        statuses.append(token_lower)
    return statuses


def _extract_llm_statuses_from_markdown(html_markdown: str, seen: Set[str]) -> List[str]:
    """Extract LLM statuses from simplified markdown content."""
    statuses: List[str] = []
    if not html_markdown:
        return statuses

    lines = html_markdown.split("\n")
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if "llm status" not in lowered:
            continue

        # Inline statuses on the same line after a colon
        if ":" in line:
            _, inline = line.split(":", 1)
            statuses.extend(_split_status_tokens(inline, seen))

        # Collect bullet lines immediately following the heading/label
        collected = False
        for follow in lines[idx + 1 :]:
            stripped = follow.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                break
            if stripped.startswith(("-", "*")):
                statuses.extend(_split_status_tokens(stripped.lstrip("-* ").strip(), seen))
                collected = True
                continue
            # Stop at the first non-bullet content
            if collected:
                break
            break

    return statuses


def _extract_llm_statuses_from_html(html: str, seen: Set[str]) -> List[str]:
    """Extract LLM statuses from raw HTML attributes and nearby text."""
    statuses: List[str] = []
    if not html:
        return statuses

    attribute_patterns = [
        r'data-llm-status=["\']([^"\']+)["\']',
        r'aria-label=["\'][^"\']*LLM status[^"\']*[:：]\s*([^"\']+)["\']',
        r'title=["\'][^"\']*LLM status[^"\']*[:：]\s*([^"\']+)["\']',
    ]
    for pattern in attribute_patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            statuses.extend(_split_status_tokens(match.group(1), seen))

    for match in re.finditer(r"LLM status[^<]{0,80}", html, flags=re.IGNORECASE):
        statuses.extend(_split_status_tokens(match.group(0), seen))

    return statuses


def _extract_llm_statuses(html: Optional[str], html_markdown: str) -> List[str]:
    """Extract unique LLM statuses from HTML and its markdown representation."""
    seen: Set[str] = set()
    statuses: List[str] = []
    statuses.extend(_extract_llm_statuses_from_markdown(html_markdown, seen))
    if html:
        statuses.extend(_extract_llm_statuses_from_html(html, seen))
    return statuses


def _capture_llm_statuses(
    html: Optional[str],
    html_markdown: str,
    llm_status_path: Optional[Path] = None,
    result_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Extract LLM statuses, persist to JSON if path provided, and return metadata."""
    statuses = _extract_llm_statuses(html, html_markdown)
    augmented_markdown = html_markdown

    if statuses:
        status_line = f"LLM status: {', '.join(statuses)}"
        augmented_markdown = f"{html_markdown}\n\n{status_line}" if html_markdown else status_line

        if llm_status_path:
            status_payload = json.dumps({"llm_statuses": statuses}, ensure_ascii=False, indent=2)
            _write_if_changed(llm_status_path, status_payload)
            if result_dict is not None:
                result_dict["llm_status_path"] = llm_status_path
                result_dict["llm_statuses"] = statuses
    else:
        if llm_status_path:
            status_payload = json.dumps({"llm_statuses": []}, ensure_ascii=False, indent=2)
            _write_if_changed(llm_status_path, status_payload)
            if result_dict is not None:
                result_dict["llm_status_path"] = llm_status_path
                result_dict["llm_statuses"] = []

    return {
        "statuses": statuses,
        "html_markdown_with_status": augmented_markdown,
    }


def save_pr_snapshot(
    pr: Dict[str, Any],
    reason: str,
    base_dir: Optional[Path] = None,
    current_time: Optional[datetime] = None,
    fetch_html: bool = True,
    html_content: Optional[str] = None,
) -> Dict[str, Any]:
    """Save raw PR data, HTML, and markdown summary to disk.

    Args:
        pr: PR data dictionary.
        reason: Reason for capturing the snapshot.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.
        fetch_html: Whether to fetch HTML page (default: True). Set to False to avoid blocking network calls.
        html_content: Optional pre-fetched HTML content. If provided, this HTML is used instead of fetching.

    Returns:
        Dictionary containing:
        - snapshot_dir, raw_path, markdown_path (Path objects)
        - html_path, html_md_path, llm_status_path (Path objects, if HTML was fetched)
        - saved_json, saved_html (str, the actual content that was saved)
        - llm_statuses (list[str], extracted LLM statuses when HTML is available)
    """
    effective_time = current_time if current_time is not None else datetime.now()

    base_path = Path(base_dir) if base_dir is not None else DEFAULT_SNAPSHOT_BASE_DIR
    base_path = base_path.expanduser().resolve()

    # Directory name without timestamp (e.g., owner_repo_PR123)
    snapshot_dir_name = _build_snapshot_dir_name(pr)
    snapshot_dir = base_path / snapshot_dir_name
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    # File prefix with timestamp (e.g., 20260102_030405)
    timestamp_str = _format_timestamp(effective_time)
    file_prefix = timestamp_str

    raw_path = snapshot_dir / f"{file_prefix}_raw.json"
    markdown_path = snapshot_dir / f"{file_prefix}_summary.md"
    html_path = snapshot_dir / f"{file_prefix}_page.html"
    html_md_path = snapshot_dir / f"{file_prefix}_page.md"
    llm_status_path = snapshot_dir / f"{file_prefix}_llm_statuses.json"

    reactions_summary = _summarize_reactions(pr.get("commentNodes", pr.get("comments", [])))
    markdown_raw_snapshot = _prepare_markdown_raw(pr)

    # Save raw JSON
    raw_json = json.dumps(pr, ensure_ascii=False, indent=2)
    _write_if_changed(raw_path, raw_json)

    # Save markdown summary
    markdown_content = _build_markdown(
        pr,
        reason,
        timestamp_str,
        reactions_summary,
        snapshot_dir_name,
        markdown_raw_snapshot,
    )
    _write_if_changed(markdown_path, markdown_content)

    # Fetch and save HTML page
    pr_url = pr.get("url", "")
    result_dict = {
        "snapshot_dir": snapshot_dir,
        "raw_path": raw_path,
        "markdown_path": markdown_path,
        "saved_json": raw_json,
        "saved_html": "",
    }

    # Use pre-fetched HTML if provided, otherwise fetch if requested
    if html_content:
        # Use provided HTML content
        _write_if_changed(html_path, html_content)
        result_dict["html_path"] = html_path
        result_dict["saved_html"] = html_content

        # Convert HTML to markdown for better readability
        html_as_markdown = _html_to_simple_markdown(html_content)
        captured = _capture_llm_statuses(html_content, html_as_markdown, llm_status_path, result_dict)
        if captured["html_markdown_with_status"]:
            _write_if_changed(html_md_path, captured["html_markdown_with_status"])
            result_dict["html_md_path"] = html_md_path
    elif fetch_html and pr_url:
        # Fetch HTML if not provided
        fetched_html = _fetch_pr_html(pr_url)
        if fetched_html:
            _write_if_changed(html_path, fetched_html)
            result_dict["html_path"] = html_path
            result_dict["saved_html"] = fetched_html

            # Convert HTML to markdown for better readability
            html_as_markdown = _html_to_simple_markdown(fetched_html)
            captured = _capture_llm_statuses(fetched_html, html_as_markdown, llm_status_path, result_dict)
            if captured["html_markdown_with_status"]:
                _write_if_changed(html_md_path, captured["html_markdown_with_status"])
                result_dict["html_md_path"] = html_md_path

    return result_dict


def record_reaction_snapshot(
    pr: Dict[str, Any],
    phase: str,
    base_dir: Optional[Path] = None,
    current_time: Optional[datetime] = None,
    html_content: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Record a snapshot when comment reactions force LLM working detection.

    Uses content-based deduplication: only saves a new timestamped snapshot when
    the PR JSON or HTML content (converted to markdown) has changed since the previous iteration.
    HTML is converted to markdown before comparison to avoid false changes from HTML tag variations.

    Optimization: HTML is only fetched when JSON hasn't changed, avoiding unnecessary network
    calls when JSON changes already indicate content updates.

    Args:
        pr: PR data dictionary.
        phase: Detected phase for the PR.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.
        html_content: Optional pre-fetched HTML content to avoid network calls.

    Returns:
        Paths for created snapshot files, or None when no snapshot is recorded.
    """
    if phase != PHASE_LLM_WORKING:
        return None

    comment_nodes = pr.get("commentNodes", pr.get("comments", []))
    if not has_comments_with_reactions(comment_nodes):
        return None

    pr_key = pr.get("url") or _build_snapshot_dir_name(pr)

    # Check once flag: prevent duplicate recording within the same iteration
    if pr_key in _recorded_in_current_iteration:
        return None

    # Prepare content for comparison (must match the format saved in save_pr_snapshot)
    current_json = json.dumps(pr, ensure_ascii=False, indent=2)

    # Check content-based deduplication: compare with previous iteration
    previous_content = _previous_pr_content.get(pr_key, {})
    previous_json = previous_content.get("json", "")
    previous_html_md = previous_content.get("html_md", "")

    # Short-circuit: if JSON changed, we know content changed (no need to fetch HTML for comparison)
    json_changed = current_json != previous_json

    # Only fetch HTML if JSON hasn't changed (to check if HTML changed)
    # This avoids unnecessary network calls when JSON already indicates a change
    current_html_md = ""
    fetched_html = html_content
    pr_url = pr.get("url", "")

    captured_status = {"html_markdown_with_status": ""}
    if html_content:
        current_html_md = _html_to_simple_markdown(html_content)
        captured_status = _capture_llm_statuses(html_content, current_html_md)
        current_html_md = captured_status["html_markdown_with_status"]

    if fetched_html is None and not json_changed and pr_url:
        # JSON unchanged, check HTML for changes
        fetched_html = _fetch_pr_html(pr_url)
        if fetched_html:
            # Convert HTML to markdown for comparison to avoid HTML tag noise
            current_html_md = _html_to_simple_markdown(fetched_html)
            captured_status = _capture_llm_statuses(fetched_html, current_html_md)
            current_html_md = captured_status["html_markdown_with_status"]

    # Check if content has changed (compare markdown instead of raw HTML)
    html_changed = current_html_md != previous_html_md
    content_changed = json_changed or html_changed

    if not content_changed and previous_json:
        # Content unchanged, mark as recorded and skip saving
        _recorded_in_current_iteration.add(pr_key)
        return None

    # Content changed or first time: save snapshot with timestamp
    # Pass pre-fetched HTML to avoid double-fetch
    snapshot_paths = save_pr_snapshot(
        pr,
        reason="comment_reactions_detected",
        base_dir=base_dir,
        current_time=current_time,
        html_content=fetched_html,  # Pass pre-fetched HTML if available
    )

    # If HTML wasn't fetched during comparison (because JSON changed), fetch it now for caching
    # This ensures we have HTML for the next iteration's comparison
    if fetched_html is None and pr_url:
        # HTML was saved by save_pr_snapshot, retrieve it from the result
        saved_html = snapshot_paths.get("saved_html", "")
        if saved_html:
            current_html_md = _html_to_simple_markdown(saved_html)
            captured_status = _capture_llm_statuses(saved_html, current_html_md)
            current_html_md = captured_status["html_markdown_with_status"]

    # Update reaction resolution cache based on HTML snapshot content
    if current_html_md:
        reactions_finished = _eyes_reaction_finished(current_html_md)
        update_comment_reaction_resolution(pr, comment_nodes, reactions_finished)

    # Update previous content cache for next iteration
    # Store markdown version of HTML to avoid false changes from HTML tag variations
    _previous_pr_content[pr_key] = {
        "json": snapshot_paths.get("saved_json", current_json),
        "html_md": current_html_md,
    }

    # Mark as recorded in current iteration
    _recorded_in_current_iteration.add(pr_key)

    return snapshot_paths


def reset_snapshot_cache(clear_content_cache: bool = False) -> None:
    """Clear the once flag for the current iteration.

    This should be called at the start of each monitoring iteration to allow
    recording snapshots again. The previous content cache is preserved for
    content-based deduplication across iterations unless explicitly cleared.

    Args:
        clear_content_cache: If True, also clear the previous content cache.
            This should be set to True for tests to ensure clean state.
    """
    _recorded_in_current_iteration.clear()
    if clear_content_cache:
        _previous_pr_content.clear()
