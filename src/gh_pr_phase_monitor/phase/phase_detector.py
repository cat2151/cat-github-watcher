"""
PR phase detection logic based on reviews and PR state
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

# Phase constants
PHASE_LLM_WORKING = "LLM working"
PHASE_1 = "phase1"
PHASE_2 = "phase2"
PHASE_3 = "phase3"

# Tracks comment reaction signatures that were confirmed as "finished" via HTML snapshot analysis.
_finished_reaction_signatures: Dict[str, str] = {}

# Feature B (GraphQL-based phase detection) flag.
# When False (default), only HTML/llm_statuses-based detection (Feature A) is used.
# Set to True via use_graphql_phase_detection = true in config.toml.
_use_graphql_phase_detection: bool = False


def set_use_graphql_phase_detection(enabled: bool) -> None:
    """Enable or disable GraphQL-based phase detection (Feature B).

    When disabled (default), phase is determined solely from llm_statuses extracted from HTML.
    When enabled, falls back to GraphQL reviews/reviewThreads data when llm_statuses lack a
    reviewing event.
    """
    global _use_graphql_phase_detection
    _use_graphql_phase_detection = enabled


def _build_pr_key(pr: Dict[str, Any]) -> str:
    """Build a stable key for tracking reaction resolution state."""
    url = pr.get("url")
    if url:
        return url

    repo_info = pr.get("repository") or {}
    owner = repo_info.get("owner") or "unknown"
    name = repo_info.get("name") or "unknown"
    number = pr.get("number") or "unknown"
    return f"{owner}/{name}#{number}"


def _comment_reaction_signature(comment_nodes: Any) -> str:
    """Build a deterministic signature of comment reactions for change detection."""
    if not isinstance(comment_nodes, list):
        return ""

    signatures: List[Dict[str, Any]] = []
    for comment in comment_nodes:
        groups = []
        for group in comment.get("reactionGroups") or []:
            count = (group.get("users") or {}).get("totalCount", 0)
            if count:
                groups.append({"content": group.get("content"), "count": count})
        if groups:
            # Sort reactions within a comment so signature is order-insensitive
            groups.sort(key=lambda g: (g.get("content") or "", g.get("count", 0)))
            signatures.append({"reactions": groups})

    if not signatures:
        return ""

    # Sort comments by their reaction signature to avoid dependence on comment order
    signatures.sort(key=lambda item: json.dumps(item["reactions"], sort_keys=True))

    # Sort keys for deterministic output
    return json.dumps(signatures, sort_keys=True)


def update_comment_reaction_resolution(pr: Dict[str, Any], comment_nodes: Any, finished: bool) -> None:
    """Update resolution cache based on HTML analysis results."""
    pr_key = _build_pr_key(pr)
    signature = _comment_reaction_signature(comment_nodes)

    if not signature:
        _finished_reaction_signatures.pop(pr_key, None)
        return

    if finished:
        _finished_reaction_signatures[pr_key] = signature
    else:
        _finished_reaction_signatures.pop(pr_key, None)


def comment_reactions_marked_finished(pr: Dict[str, Any], comment_nodes: Any) -> bool:
    """Return True when reactions match a signature previously marked finished."""
    signature = _comment_reaction_signature(comment_nodes)
    if not signature:
        return False

    pr_key = _build_pr_key(pr)
    return _finished_reaction_signatures.get(pr_key) == signature


def reset_comment_reaction_resolution_cache() -> None:
    """Clear cached reaction resolution state (useful for tests)."""
    _finished_reaction_signatures.clear()


def has_comments_with_reactions(comments: Union[List[Dict[str, Any]], int, None]) -> bool:
    """Check if any comments have non-empty reactionGroups

    When the LLM (coding agent) is working on addressing PR comments
    (general pull request comments fetched via the `comments` field),
    those comments may have reactions (GitHub reactions like 👍, 👎, 😄, 🎉,
    😕, ❤️, 🚀, 👀, etc.) indicating the bot is processing them.
    This indicates the LLM is actively working.

    Args:
        comments: List of comment dictionaries with reactionGroups, or None/integer for backward compatibility

    Returns:
        True if any comment has non-empty reactionGroups, False otherwise
    """
    # Handle backward compatibility: comments might be an integer or None from legacy API
    if not comments or not isinstance(comments, list):
        return False

    for comment in comments:
        reaction_groups = comment.get("reactionGroups", [])
        if reaction_groups:
            # Check if any reaction group has users
            for group in reaction_groups:
                users = group.get("users", {})
                total_count = users.get("totalCount", 0)
                if total_count > 0:
                    return True

    return False


def has_unresolved_review_threads(review_threads: Union[List[Dict[str, Any]], None]) -> bool:
    """Check if there are any unresolved review threads (inline comments)

    Review threads contain inline code comments from reviews.
    If there are unresolved threads, the PR needs fixes (phase2).

    Args:
        review_threads: List of review thread dictionaries with isResolved, isOutdated, or None

    Returns:
        True if there are unresolved review threads, False otherwise
    """
    if not review_threads or not isinstance(review_threads, list):
        return False

    # Check if any thread is unresolved and not outdated
    for thread in review_threads:
        is_resolved = thread.get("isResolved", False)
        is_outdated = thread.get("isOutdated", False)

        # If a thread is not resolved and not outdated, it needs attention
        if not is_resolved and not is_outdated:
            return True

    return False


def has_inline_review_comments(review_body: str) -> bool:
    """DEPRECATED: Check if review body indicates inline code comments were generated

    This function is kept for backward compatibility but should not be used
    for new code. Use has_unresolved_review_threads() instead which checks
    actual review thread data rather than trying to infer from text patterns.

    Copilot's review body MAY contain text like:
    "Copilot reviewed X out of Y changed files in this pull request and generated N comment(s)."
    when inline comments are present. However, this pattern is not always present.

    Args:
        review_body: The body text of the review

    Returns:
        True if the review body indicates inline comments exist, False otherwise
    """
    if not review_body:
        return False

    # Check for the pattern indicating inline comments were generated
    # Pattern matches: "generated 1 comment" or "generated 2 comments" etc.
    # NOTE: This is unreliable - the pattern may not always be present!
    pattern = r"generated\s+\d+\s+comments?"
    return bool(re.search(pattern, review_body, re.IGNORECASE))


def llm_working_from_statuses(llm_statuses: List[str]) -> Optional[bool]:
    """Determine LLM working state from ordered LLM statuses.

    Returns True when the most recent state after any 'started work' entry has
    no subsequent 'finished work' entry, False when a later 'finished work'
    exists, and None when the statuses do not provide a signal.
    """
    if not llm_statuses:
        return None

    last_started_idx = None
    last_finished_idx = None
    reviewing_chain_finished_idx = None
    review_idx = None
    started_after_review_idx = None

    for idx, status in enumerate(llm_statuses):
        lowered = status.lower()
        if "reviewing" in lowered:
            review_idx = idx
            started_after_review_idx = None
        if "started work" in lowered:
            last_started_idx = idx
            if review_idx is not None and idx > review_idx:
                started_after_review_idx = idx
        if "finished work" in lowered:
            last_finished_idx = idx
            if started_after_review_idx is not None and idx > started_after_review_idx:
                reviewing_chain_finished_idx = idx

    if last_finished_idx is not None and last_started_idx is not None and last_finished_idx > last_started_idx:
        return False

    if reviewing_chain_finished_idx is not None and (
        last_started_idx is None or reviewing_chain_finished_idx >= last_started_idx
    ):
        return False

    if last_started_idx is not None and (last_finished_idx is None or last_started_idx > last_finished_idx):
        return True

    return None


def _phase_from_llm_statuses(llm_statuses: List[str]) -> Optional[str]:
    """Infer phase from LLM statuses.

    Returns PHASE_3 when reviewing → started work → finished work are detected in that order.
    Returns PHASE_2 when reviewing occurred but post-review work (started→finished) is not yet complete.
    Returns None when no reviewing event found (cannot determine phase2/3).

    Tracking is reset on each new reviewing event so only the most recent review cycle counts.
    """
    if not llm_statuses:
        return None

    last_review_idx: Optional[int] = None
    last_started_after_review_idx: Optional[int] = None
    last_finished_after_started_after_review_idx: Optional[int] = None

    for idx, status in enumerate(llm_statuses):
        lowered = status.lower()
        if "reviewing" in lowered:
            last_review_idx = idx
            last_started_after_review_idx = None  # reset on new reviewing event
            last_finished_after_started_after_review_idx = None
        elif "started work" in lowered and last_review_idx is not None:
            last_started_after_review_idx = idx
            last_finished_after_started_after_review_idx = None  # reset finished when a new started begins
        elif "finished work" in lowered and last_started_after_review_idx is not None:
            last_finished_after_started_after_review_idx = idx

    if last_review_idx is None:
        return None  # no reviewing event: cannot determine phase2/3

    # reviewing → started work → finished work all in order → phase3
    if last_finished_after_started_after_review_idx is not None:
        return PHASE_3

    # reviewing occurred but post-review work not yet complete → phase2
    return PHASE_2


def _determine_phase_without_comment_reactions(pr: Dict[str, Any]) -> str:
    """Determine the phase without considering comment reactions."""
    is_draft = pr.get("isDraft", False)
    review_requests = pr.get("reviewRequests", [])
    llm_statuses = pr.get("llm_statuses") or []

    # Phase 1: Draft状態
    # - reviewRequests が1件以上ある場合: 常に phase1
    # - reviewRequests が空の場合:
    #     - LLM が未完了 (llm_working_from_statuses(...) が True または None): LLM working
    #     - LLM が完了済み (llm_working_from_statuses(...) が False): phase1
    if is_draft:
        if not review_requests:
            llm_working = llm_working_from_statuses(llm_statuses)
            if llm_working is False:
                return PHASE_1
            return PHASE_LLM_WORKING
        return PHASE_1

    # 非draftPR: llm_statusesを優先シグナルとして使用。
    # reviewingイベントがある場合、HTMLから抽出したllm_statusesはGraphQLデータより
    # 正確にフィードバック対応状況を反映する（GraphQLのスレッドは明示的にresolveされない
    # 限りisResolved: Falseのまま残るため）。
    # reviewingイベントがない場合（Noneを返す）はFeature B（GraphQL）にフォールバック（要設定）。
    status_phase = _phase_from_llm_statuses(llm_statuses)
    if status_phase is not None:
        return status_phase

    # llm_statusesにreviewingイベントがない場合: Feature B（GraphQL）を使用するか確認
    if _use_graphql_phase_detection:
        from .legacy.phase_detector_graphql import _determine_phase_from_graphql_data

        return _determine_phase_from_graphql_data(pr)

    # Feature B無効時（デフォルト）: reviewingイベントなし = LLM working
    return PHASE_LLM_WORKING


def determine_phase(pr: Dict[str, Any]) -> str:
    """Determine which phase the PR is in

    Args:
        pr: PR data dictionary

    Returns:
        Phase string: PHASE_1, PHASE_2, PHASE_3, or PHASE_LLM_WORKING
    """
    # Use commentNodes if available (new API), fall back to comments for legacy compatibility
    comment_nodes = pr.get("commentNodes", pr.get("comments", []))

    # Check if any comments have reactions - this indicates LLM is working
    # When the coding agent is responding to PR comments, those comments
    # may have reactions indicating the bot is processing them
    if has_comments_with_reactions(comment_nodes):
        if not comment_reactions_marked_finished(pr, comment_nodes):
            llm_statuses = pr.get("llm_statuses") or []
            llm_working = llm_working_from_statuses(llm_statuses)
            if llm_working is False:
                return _determine_phase_without_comment_reactions(pr)
            return PHASE_LLM_WORKING

    return _determine_phase_without_comment_reactions(pr)


def get_llm_working_progress_label(pr: Dict[str, Any]) -> str:
    """Describe how far the PR has progressed when in LLM working phase."""
    base_phase = _determine_phase_without_comment_reactions(pr)

    if pr.get("isDraft", False):
        return "Phase 1 in progress"

    if base_phase == PHASE_3:
        return "Phase 2 completed"

    if base_phase == PHASE_2:
        return "Phase 2 in progress"

    return "Phase 1 completed"
