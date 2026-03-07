"""
Utilities for extracting LLM working status information from PR HTML pages.
"""

import html as html_lib
import re
from typing import List, Optional, Set

from .pr_html_fetcher import _html_to_simple_markdown


def _normalize_status_text(text: str) -> str:
    """Normalize status text by removing markup and collapsing whitespace."""
    cleaned = html_lib.unescape(text or "")
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"https?://\S+", "", cleaned)
    cleaned = cleaned.replace("**", "").replace("__", "")
    cleaned = re.sub(r"^\s*#+\s*", "", cleaned)
    cleaned = re.sub(r"\bView session\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("Uh oh! There was an error while loading.", "")
    cleaned = cleaned.replace("Please reload this page", "")
    cleaned = re.sub(r"\s*[-*]\s+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _add_status(statuses: List[str], seen: Set[str], text: str) -> None:
    """Append normalized status text if it's new."""
    normalized = _normalize_status_text(text)
    if not normalized:
        return
    normalized = re.sub(r"^llm status[:\s-]+", "", normalized, flags=re.IGNORECASE).strip()
    if not normalized or normalized.lower() == "llm status":
        return
    lower = normalized.lower()
    if lower in {
        "draft",
        "reviewers",
        "assignees",
        "labels",
        "projects",
        "milestone",
        "development",
        "2 participants",
        "sign up for free to join this conversation on github. already have an account? sign in to comment",
        "this file contains hidden or bidirectional unicode text that may be interpreted or compiled differently than what appears below. to review, open the file in an editor that reveals hidden unicode characters. learn more about bidirectional unicode characters",
        "show hidden characters",
        "none yet",
        "no milestone",
        "successfully merging this pull request may close these issues.",
    }:
        return
    if "error while loading" in lower or "reload this page" in lower:
        return
    if "sorry, something went wrong" in lower:
        return
    if lower.startswith("add this suggestion"):
        return
    if normalized.startswith(("](", "[")):
        return
    actionable_markers = (
        "started",
        "finished",
        "comment",
        "reviewed",
        "review request",
        "requested a review",
        "ready for review",
    )
    if not any(marker in lower for marker in actionable_markers):
        return
    if "commented" in lower:
        return
    if normalized.endswith("on behalf of"):
        return
    key = lower
    if key in seen:
        return
    seen.add(key)
    statuses.append(normalized)


def _extract_llm_statuses_from_markdown(html_markdown: str, seen: Set[str]) -> List[str]:
    """Extract LLM statuses from simplified markdown content."""
    statuses: List[str] = []
    if not html_markdown:
        return statuses

    segments = [segment.strip() for segment in re.split(r"\n{2,}", html_markdown) if segment.strip()]
    idx = 0
    while idx < len(segments):
        segment = segments[idx]
        lowered = segment.lower()
        combined = segment

        should_collect_trailing = "llm status" in lowered
        if should_collect_trailing:
            next_idx = idx + 1
            while next_idx < len(segments):
                next_segment = segments[next_idx]
                next_lower = next_segment.lower()
                if "llm status" in next_lower or "session_id=" in next_segment:
                    break
                if "llm status" in lowered:
                    _add_status(statuses, seen, next_segment)
                else:
                    combined = f"{combined} {next_segment}"
                next_idx += 1
            idx = next_idx - 1

        if "llm status" in lowered:
            payload = re.sub(r"^llm status[:\s-]+", "", segment, flags=re.IGNORECASE).strip()
            if payload:
                _add_status(statuses, seen, payload)
        elif "session_id=" in segment:
            # Extract individual session_id= link texts instead of the full combined segment.
            # A markdown segment may contain both non-session content (e.g. "reviewed" text
            # from an adjacent review-event timeline item) and one or more session_id= links.
            # Adding the whole combined segment would create a spurious status string that
            # confuses review-cycle detection in _phase_from_llm_statuses (the combined
            # "reviewed…started work" text would be treated as a single review-reset event).
            # Extracting individual link texts preserves each session event separately while
            # leaving the "reviewed" detection to the HTML extractor (which runs first and
            # processes timeline items in chronological order).
            session_link_re = re.compile(r"\[([^\]]+)\]\([^)]*session_id=[^)]+\)")
            session_texts = [m.group(1) for m in session_link_re.finditer(segment)]
            if session_texts:
                for text in session_texts:
                    _add_status(statuses, seen, text)
            else:
                # Fallback: no session_id= links found in markdown-link format,
                # so fall back to adding the combined text (e.g. plain-text mode).
                _add_status(statuses, seen, combined)

        idx += 1

    return statuses


def _extract_llm_statuses_from_html(html: str, seen: Set[str]) -> List[str]:
    """Extract LLM statuses from timeline session blocks and HTML attributes."""
    statuses: List[str] = []
    if not html:
        return statuses

    timeline_pattern = re.compile(
        r'<div[^>]*class="[^"]*TimelineItem-body[^"]*"[^>]*>(.*?)</div>', re.DOTALL | re.IGNORECASE
    )
    copilot_hovercard_re = re.compile(r'data-hovercard-type=["\']copilot["\']', re.IGNORECASE)
    author_from_copilot_re = re.compile(
        r'data-hovercard-type=["\']copilot["\'][^>]*>([^<]+)</a>', re.IGNORECASE
    )
    for body in re.findall(timeline_pattern, html):
        if "session_id=" in body:
            timeline_text = _html_to_simple_markdown(body)
            _add_status(statuses, seen, timeline_text)
        elif copilot_hovercard_re.search(body):
            author_match = author_from_copilot_re.search(body)
            if not author_match:
                continue
            author = author_match.group(1).strip()
            parts = re.split(r"</strong\b[^>]*>", body, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) < 2:
                continue
            action_text = _html_to_simple_markdown(parts[1]).strip()
            if action_text:
                _add_status(statuses, seen, f"{author} {action_text}")

    attribute_patterns = [
        r'data-llm-status=["\']([^"\']+)["\']',
        r'aria-label=["\'][^"\']*LLM status[^"\']*[:：]\s*([^"\']+)["\']',
        r'title=["\'][^"\']*LLM status[^"\']*[:：]\s*([^"\']+)["\']',
    ]
    for pattern in attribute_patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            _add_status(statuses, seen, match.group(1))

    return statuses


def _extract_llm_statuses(html: Optional[str], html_markdown: str) -> List[str]:
    """Extract unique LLM statuses from HTML and its markdown representation.

    HTML extraction runs first so that timeline items are processed in their
    chronological order (review event before work events).  Markdown extraction
    runs second as a fallback, contributing only events not already captured by
    the HTML extractor (e.g. plain-text "LLM status:" labels).
    """
    seen: Set[str] = set()
    statuses: List[str] = []
    if html:
        statuses.extend(_extract_llm_statuses_from_html(html, seen))
    statuses.extend(_extract_llm_statuses_from_markdown(html_markdown, seen))
    return statuses
