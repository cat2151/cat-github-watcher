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
    # Skip if a longer already-captured entry already contains this text as a substring.
    # This prevents short link-text forms (e.g. "started work") from being added when
    # the full form (e.g. "Copilot started work on behalf of ... March 7, 2026 14:20")
    # was already captured by the HTML-element extractor.
    # Only check entries that are strictly longer (same-length exact matches are caught above).
    if any(key in existing for existing in seen if len(existing) > len(key)):
        return
    seen.add(key)
    statuses.append(normalized)


def _extract_llm_statuses_via_text_patterns(html_markdown: str, seen: Set[str]) -> List[str]:
    """Extract LLM statuses by scanning plain-text patterns in HTML-converted-to-markdown.

    Handles the case that the HTML-element extractor misses:
    - Plain-text ``LLM status:`` labels written in PR comment bodies.

    Note: ``session_id=`` links are intentionally NOT handled here.  All Copilot
    session events appear inside ``TimelineItem-body`` elements and are captured
    authoritatively by ``_extract_llm_statuses_via_html_elements``.  Any
    ``session_id=`` links outside those elements are duplicate references —
    always with degraded short-form anchor texts — and processing them causes
    spurious short-form entries that break review-cycle detection.
    """
    statuses: List[str] = []
    if not html_markdown:
        return statuses

    segments = [segment.strip() for segment in re.split(r"\n{2,}", html_markdown) if segment.strip()]
    idx = 0
    while idx < len(segments):
        segment = segments[idx]
        lowered = segment.lower()

        if "llm status" in lowered:
            next_idx = idx + 1
            while next_idx < len(segments):
                next_segment = segments[next_idx]
                next_lower = next_segment.lower()
                if "llm status" in next_lower:
                    break
                _add_status(statuses, seen, next_segment)
                next_idx += 1
            idx = next_idx - 1

            payload = re.sub(r"^llm status[:\s-]+", "", segment, flags=re.IGNORECASE).strip()
            if payload:
                _add_status(statuses, seen, payload)

        idx += 1

    return statuses


def _extract_llm_statuses_via_html_elements(html: str, seen: Set[str]) -> List[str]:
    """Extract LLM statuses by parsing HTML structural elements (timeline items and attributes).

    Scans ``TimelineItem-body`` divs for ``session_id=`` links and Copilot hovercard
    events, and also checks ``data-llm-status`` / ``aria-label`` / ``title`` attributes.
    Because this walks the HTML structure in document order it preserves chronological
    ordering of events (e.g. review before subsequent work events).
    """
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
    """Extract unique LLM statuses from HTML and its plain-text representation.

    HTML-element extraction runs first so that timeline items are processed in their
    chronological order (review event before work events).  Text-pattern extraction
    runs second as a fallback, contributing only events not already captured by
    the HTML-element extractor (e.g. plain-text "LLM status:" labels, or
    ``session_id=`` links outside ``TimelineItem-body`` elements).
    """
    seen: Set[str] = set()
    statuses: List[str] = []
    if html:
        statuses.extend(_extract_llm_statuses_via_html_elements(html, seen))
    statuses.extend(_extract_llm_statuses_via_text_patterns(html_markdown, seen))
    return statuses
