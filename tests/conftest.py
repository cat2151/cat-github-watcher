"""
Shared pytest fixtures for the test suite.
"""

import pytest


@pytest.fixture(autouse=True)
def reset_display_issues_cache():
    """Reset the cross-iteration issues cache before and after each test.

    display.py caches issue data across calls to reduce GraphQL API consumption.
    Tests that mock get_issues_from_repositories would otherwise see stale cached
    data from previous tests, causing spurious call_count == 0 failures.
    """
    from src.gh_pr_phase_monitor.display import reset_issues_cache

    reset_issues_cache()
    yield
    reset_issues_cache()
