"""
PR phase detection logic based on reviews and PR state
"""

import json
import re
from typing import Any, Dict, List, Union

# Phase constants
PHASE_LLM_WORKING = "LLM working"
PHASE_1 = "phase1"
PHASE_2 = "phase2"
PHASE_3 = "phase3"

# Tracks comment reaction signatures that were confirmed as "finished" via HTML snapshot analysis.
_finished_reaction_signatures: Dict[str, str] = {}


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


def determine_phase(pr: Dict[str, Any]) -> str:
    """Determine which phase the PR is in

    Args:
        pr: PR data dictionary

    Returns:
        Phase string: PHASE_1, PHASE_2, PHASE_3, or PHASE_LLM_WORKING
    """
    is_draft = pr.get("isDraft", False)
    reviews = pr.get("reviews", [])
    latest_reviews = pr.get("latestReviews", [])
    review_requests = pr.get("reviewRequests", [])
    # Use commentNodes if available (new API), fall back to comments for legacy compatibility
    comment_nodes = pr.get("commentNodes", pr.get("comments", []))
    # Get review threads (inline comments)
    review_threads = pr.get("reviewThreads", [])

    # Check if any comments have reactions - this indicates LLM is working
    # When the coding agent is responding to PR comments, those comments
    # may have reactions indicating the bot is processing them
    if has_comments_with_reactions(comment_nodes):
        if not comment_reactions_marked_finished(pr, comment_nodes):
            return PHASE_LLM_WORKING

    # Phase 1: Draft状態 (ただし、reviewRequestsが空の場合はLLM working)
    if is_draft:
        # reviewRequestsが空なら、LLM workingと判定
        if not review_requests:
            return PHASE_LLM_WORKING
        return PHASE_1

    # Phase 2 と Phase 3 の判定には reviews が必要
    if not reviews or not latest_reviews:
        return PHASE_LLM_WORKING

    # 最新のレビューを取得
    latest_review = reviews[-1]
    author_login = latest_review.get("author", {}).get("login", "")

    # Phase 2/3: copilot-pull-request-reviewer のレビュー後
    if author_login == "copilot-pull-request-reviewer":
        # レビューの状態を確認
        review_state = latest_review.get("state", "")

        # CHANGES_REQUESTEDの場合は確実にphase2
        if review_state == "CHANGES_REQUESTED":
            return PHASE_2

        # COMMENTEDの場合、実際のreview threads(インラインコメント)を確認
        # 未解決のレビュースレッドがある場合はphase2（修正が必要）、ない場合はphase3（レビュー待ち）
        if review_state == "COMMENTED":
            # Check actual review threads instead of text patterns
            if has_unresolved_review_threads(review_threads):
                return PHASE_2
            # レビューコメントがない場合はphase3
            return PHASE_3

        # それ以外(APPROVED, DISMISSED, PENDING等)はphase3
        return PHASE_3

    # Phase 3: copilot-swe-agent の修正後
    # ただし、copilot-pull-request-reviewerの未解決レビューがある場合はphase2
    if author_login == "copilot-swe-agent":
        # Find the positions of copilot-pull-request-reviewer and copilot-swe-agent reviews
        # to determine if there's a re-review from the reviewer after swe-agent started working
        latest_reviewer_index = None
        latest_reviewer_state = None
        first_swe_agent_index = None
        swe_agent_review_count = 0

        for i, review in enumerate(reviews):
            reviewer_login = review.get("author", {}).get("login", "")

            # Track copilot-swe-agent reviews
            if reviewer_login == "copilot-swe-agent":
                swe_agent_review_count += 1
                if first_swe_agent_index is None:
                    first_swe_agent_index = i

            # Track the latest copilot-pull-request-reviewer review
            if reviewer_login == "copilot-pull-request-reviewer":
                latest_reviewer_index = i
                latest_reviewer_state = review.get("state", "")

        # CHANGES_REQUESTEDの場合は常にphase2
        if latest_reviewer_state == "CHANGES_REQUESTED":
            return PHASE_2

        # Check if there are unresolved review threads
        if has_unresolved_review_threads(review_threads):
            # When copilot-pull-request-reviewer uses COMMENTED (not CHANGES_REQUESTED),
            # it indicates suggestions rather than required changes.
            # If swe-agent has posted even one review in response, the work is complete → phase3
            # This is different from CHANGES_REQUESTED where we'd want stronger completion signals.

            is_re_review = (
                latest_reviewer_index is not None
                and first_swe_agent_index is not None
                and latest_reviewer_index > first_swe_agent_index
            )

            # Determine if swe-agent has completed work
            if latest_reviewer_state == "COMMENTED":
                # For COMMENTED reviews (suggestions only), any swe-agent review indicates completion
                swe_agent_completed = swe_agent_review_count >= 1
            else:
                # For other states, require stronger completion signals
                swe_agent_completed = (
                    swe_agent_review_count > 1  # Multiple reviews indicate completion
                    or is_re_review  # Re-review after swe-agent indicates completion
                )

            if swe_agent_completed:
                # Swe-agent completed work → phase3
                return PHASE_3
            else:
                # Swe-agent just started or no clear completion signal → phase2
                return PHASE_2

        # 未解決のレビューコメントがない場合、または最新のレビューアーが満足している場合はphase3
        return PHASE_3

    return PHASE_LLM_WORKING
