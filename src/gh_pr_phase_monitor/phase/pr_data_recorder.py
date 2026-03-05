"""
Utilities for capturing PR snapshots to aid debugging of phase detection.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .llm_status_extractor import _extract_llm_statuses
from .phase_detector import (
    PHASE_LLM_WORKING,
    has_comments_with_reactions,
    llm_working_from_statuses,
    update_comment_reaction_resolution,
)
from .pr_html_fetcher import _fetch_pr_html, _html_to_simple_markdown
from .pr_html_analyzer import _determine_html_status
from .pr_html_saver import save_html_to_logs
from ..monitor.snapshot_markdown import _build_markdown, _prepare_markdown_raw, _summarize_reactions
from ..monitor.snapshot_path_utils import _build_snapshot_dir_name, _format_timestamp

# Snapshots are stored alongside screenshots (not inside) for easy discovery
DEFAULT_SNAPSHOT_BASE_DIR = Path("pr_phase_snapshots")

# Once flag to prevent duplicate snapshots within the same iteration
_recorded_in_current_iteration: Set[str] = set()

# Store previous iteration's content for comparison (PR key -> {json, html_md, llm_statuses})
_previous_pr_content: Dict[str, Dict[str, Any]] = {}


def _build_logs_analysis(pr_url: str, is_draft: bool, statuses: list) -> dict:
    """logs/pr/ 保存用の解析結果辞書を構築する。"""
    return {
        "pr_url": pr_url,
        "is_draft": is_draft,
        "llm_statuses": statuses,
        "status": _determine_html_status(statuses, is_draft),
    }


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
    enable_snapshots: bool = True,
) -> Optional[Dict[str, Any]]:
    """Record a snapshot when comment reactions force LLM working detection.

    Uses content-based deduplication: only saves a new timestamped snapshot when
    the PR JSON or HTML content (converted to markdown) has changed since the previous iteration.
    HTML is converted to markdown before comparison to avoid false changes from HTML tag variations.

    Optimization: When snapshots are enabled, HTML is only fetched when JSON hasn't changed to
    avoid unnecessary network calls. When snapshots are disabled, HTML may still be fetched to
    capture LLM statuses and reaction resolution even if JSON changed.

    Args:
        pr: PR data dictionary.
        phase: Detected phase for the PR.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.
        html_content: Optional pre-fetched HTML content to avoid network calls.
        enable_snapshots: When False, only fetches data needed for LLM working detection
            without writing files to pr_phase_snapshots/.

    Returns:
        Paths for created snapshot files, or None when no snapshot is recorded.
    """
    if phase != PHASE_LLM_WORKING:
        return None

    comment_nodes = pr.get("commentNodes", pr.get("comments", []))
    pr_key = pr.get("url") or _build_snapshot_dir_name(pr)
    if not has_comments_with_reactions(comment_nodes):
        # Fetch HTML for Draft PRs without review requests to detect Copilot timeline
        # events (#266). Previously, when there were no reactions we skipped fetching HTML,
        # so llm_statuses were never populated even though both "started work" and
        # "finished work" events are present on the PR page. This special-case fetch ensures
        # we still capture those statuses for LLM working detection when reactions are absent.
        is_draft = pr.get("isDraft", False)
        review_requests = pr.get("reviewRequests", [])
        if is_draft and not review_requests:
            # Always fetch fresh HTML every iteration so we never miss a newly-posted
            # "finished work" event.  Cross-iteration caching here was the root cause of
            # #266 re-occurring: a "started work"-only cached value would suppress all
            # future re-fetches, preventing "finished work" from ever being detected.
            pr_url = pr.get("url", "")
            if html_content:
                fetched = html_content
            elif pr_url:
                fetched = _fetch_pr_html(pr_url)
            else:
                fetched = None
            if fetched:
                html_md = _html_to_simple_markdown(fetched)
                captured = _capture_llm_statuses(fetched, html_md)
                if captured.get("statuses"):
                    pr["llm_statuses"] = captured["statuses"]
                save_html_to_logs(
                    fetched, pr_url,
                    analysis=_build_logs_analysis(pr_url, is_draft, captured.get("statuses", [])),
                )
        return None

    # Check once flag: prevent duplicate recording within the same iteration
    if pr_key in _recorded_in_current_iteration:
        return None

    # Prepare content for comparison (must match the format saved in save_pr_snapshot)
    current_json = json.dumps(pr, ensure_ascii=False, indent=2)

    # Check content-based deduplication: compare with previous iteration
    previous_content = _previous_pr_content.get(pr_key, {})
    previous_json = previous_content.get("json", "")
    previous_html_md = previous_content.get("html_md", "")
    latest_llm_statuses: List[str] = previous_content.get("llm_statuses", []) or []

    # Short-circuit: if JSON changed, we know content changed (no need to fetch HTML for comparison)
    json_changed = current_json != previous_json

    # Only fetch HTML if JSON hasn't changed (to check if HTML changed)
    # This avoids unnecessary network calls when JSON already indicates a change
    current_html_md = ""
    fetched_html = html_content
    pr_url = pr.get("url", "")

    captured_status = {"html_markdown_with_status": "", "statuses": []}
    should_fetch_html = not json_changed or not enable_snapshots

    if html_content:
        current_html_md = _html_to_simple_markdown(html_content)
        captured_status = _capture_llm_statuses(html_content, current_html_md)
        current_html_md = captured_status["html_markdown_with_status"]
        if captured_status["statuses"]:
            latest_llm_statuses = captured_status["statuses"]
            pr["llm_statuses"] = latest_llm_statuses

    if fetched_html is None and pr_url and should_fetch_html:
        # Fetch HTML when needed for deduplication or status capture
        fetched_html = _fetch_pr_html(pr_url)
        if fetched_html:
            # Convert HTML to markdown for comparison to avoid HTML tag noise
            current_html_md = _html_to_simple_markdown(fetched_html)
            captured_status = _capture_llm_statuses(fetched_html, current_html_md)
            current_html_md = captured_status["html_markdown_with_status"]
            if captured_status["statuses"]:
                latest_llm_statuses = captured_status["statuses"]
                pr["llm_statuses"] = latest_llm_statuses
            _is_draft = pr.get("isDraft", False)
            save_html_to_logs(
                fetched_html, pr_url,
                analysis=_build_logs_analysis(pr_url, _is_draft, captured_status.get("statuses", [])),
            )

    # Check if content has changed (compare markdown instead of raw HTML)
    html_changed = current_html_md != previous_html_md
    content_changed = json_changed or html_changed

    if not content_changed and previous_json:
        # Content unchanged, mark as recorded and skip saving
        if latest_llm_statuses:
            pr["llm_statuses"] = latest_llm_statuses
            if pr_key in _previous_pr_content:
                _previous_pr_content[pr_key]["llm_statuses"] = latest_llm_statuses
        _recorded_in_current_iteration.add(pr_key)
        return None

    # When snapshot saving is disabled, still fetch and store metadata for LLM working detection
    if not enable_snapshots:
        if captured_status.get("statuses"):
            latest_llm_statuses = captured_status["statuses"]
            pr["llm_statuses"] = latest_llm_statuses

        if current_html_md:
            llm_working = llm_working_from_statuses(captured_status.get("statuses", []))
            reactions_finished = llm_working is False
            update_comment_reaction_resolution(pr, comment_nodes, reactions_finished)

        _previous_pr_content[pr_key] = {
            "json": current_json,
            "html_md": current_html_md,
            "llm_statuses": latest_llm_statuses,
        }
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

    snapshot_llm_statuses = snapshot_paths.get("llm_statuses")
    if snapshot_llm_statuses:
        latest_llm_statuses = snapshot_llm_statuses
        pr["llm_statuses"] = latest_llm_statuses

    # If HTML wasn't fetched during comparison (because JSON changed), fetch it now for caching
    # This ensures we have HTML for the next iteration's comparison
    if fetched_html is None and pr_url:
        # HTML was saved by save_pr_snapshot, retrieve it from the result
        saved_html = snapshot_paths.get("saved_html", "")
        if saved_html:
            current_html_md = _html_to_simple_markdown(saved_html)
            captured_status = _capture_llm_statuses(saved_html, current_html_md)
            current_html_md = captured_status["html_markdown_with_status"]
            if captured_status["statuses"]:
                latest_llm_statuses = captured_status["statuses"]
                pr["llm_statuses"] = latest_llm_statuses
            _is_draft = pr.get("isDraft", False)
            save_html_to_logs(
                saved_html, pr_url,
                analysis=_build_logs_analysis(pr_url, _is_draft, captured_status.get("statuses", [])),
            )

    # Update reaction resolution cache based on HTML snapshot content
    if current_html_md:
        llm_working = llm_working_from_statuses(captured_status.get("statuses", []))
        reactions_finished = llm_working is False
        update_comment_reaction_resolution(pr, comment_nodes, reactions_finished)

    # Update previous content cache for next iteration
    # Store markdown version of HTML to avoid false changes from HTML tag variations
    _previous_pr_content[pr_key] = {
        "json": snapshot_paths.get("saved_json", current_json),
        "html_md": current_html_md,
        "llm_statuses": latest_llm_statuses,
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
