"""
GraphQL-based PR phase detection (Feature B).

This module contains the legacy GraphQL-based phase detection logic that uses
reviews, latestReviews, and reviewThreads from the GitHub GraphQL API.

This is kept for backward compatibility and can be enabled via
`use_graphql_phase_detection = true` in config.toml.
Future direction: deprecation.
"""

from typing import Any, Dict

from ..phase_detector import PHASE_2, PHASE_3, PHASE_LLM_WORKING, has_unresolved_review_threads


def _determine_phase_from_graphql_data(pr: Dict[str, Any]) -> str:
    """Determine PR phase using GraphQL reviews and review threads data.

    This is Feature B (legacy). Use only when use_graphql_phase_detection is enabled.
    """
    reviews = pr.get("reviews", [])
    latest_reviews = pr.get("latestReviews", [])
    review_threads = pr.get("reviewThreads", [])

    if not reviews or not latest_reviews:
        return PHASE_LLM_WORKING

    latest_review = reviews[-1]
    author_login = latest_review.get("author", {}).get("login", "")

    if author_login == "copilot-pull-request-reviewer":
        review_state = latest_review.get("state", "")

        if review_state == "CHANGES_REQUESTED":
            return PHASE_2

        if review_state == "COMMENTED":
            if has_unresolved_review_threads(review_threads):
                return PHASE_2
            return PHASE_3

        return PHASE_3

    if author_login == "copilot-swe-agent":
        latest_reviewer_index = None
        latest_reviewer_state = None
        first_swe_agent_index = None
        swe_agent_review_count = 0

        for i, review in enumerate(reviews):
            reviewer_login = review.get("author", {}).get("login", "")

            if reviewer_login == "copilot-swe-agent":
                swe_agent_review_count += 1
                if first_swe_agent_index is None:
                    first_swe_agent_index = i

            if reviewer_login == "copilot-pull-request-reviewer":
                latest_reviewer_index = i
                latest_reviewer_state = review.get("state", "")

        if latest_reviewer_state == "CHANGES_REQUESTED":
            return PHASE_2

        if has_unresolved_review_threads(review_threads):
            is_re_review = (
                latest_reviewer_index is not None
                and first_swe_agent_index is not None
                and latest_reviewer_index > first_swe_agent_index
            )

            if latest_reviewer_state == "COMMENTED":
                swe_agent_completed = swe_agent_review_count >= 1
            else:
                swe_agent_completed = swe_agent_review_count > 1 or is_re_review

            if swe_agent_completed:
                return PHASE_3
            else:
                return PHASE_2

        return PHASE_3

    return PHASE_LLM_WORKING
