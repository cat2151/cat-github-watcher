"""
Tests for has_unresolved_review_threads function
"""

from src.gh_pr_phase_monitor import has_unresolved_review_threads


class TestHasUnresolvedReviewThreads:
    """Test the has_unresolved_review_threads function"""

    def test_no_threads(self):
        """Empty threads list should return False"""
        assert has_unresolved_review_threads([]) is False

    def test_none_threads(self):
        """None threads should return False"""
        assert has_unresolved_review_threads(None) is False

    def test_all_resolved_threads(self):
        """All resolved threads should return False"""
        threads = [
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is False

    def test_unresolved_thread(self):
        """Unresolved thread should return True"""
        threads = [
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is True

    def test_mixed_resolved_unresolved(self):
        """Mix of resolved and unresolved should return True"""
        threads = [
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is True

    def test_outdated_unresolved_thread(self):
        """Outdated unresolved thread should return False (outdated doesn't need fixes)"""
        threads = [
            {"isResolved": False, "isOutdated": True, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is False

    def test_multiple_unresolved_threads(self):
        """Multiple unresolved threads should return True"""
        threads = [
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False, "comments": {"totalCount": 1}},
        ]
        assert has_unresolved_review_threads(threads) is True

    def test_thread_without_comments_field(self):
        """Thread without comments field should be handled gracefully"""
        threads = [
            {"isResolved": False, "isOutdated": False},  # No comments field
        ]
        # Should still return True based on isResolved status
        assert has_unresolved_review_threads(threads) is True

    def test_mixed_threads_with_and_without_comments_field(self):
        """Mix of threads with and without comments field should work correctly"""
        threads = [
            {"isResolved": True, "isOutdated": False, "comments": {"totalCount": 1}},
            {"isResolved": False, "isOutdated": False},  # No comments field
        ]
        # Should return True because there's an unresolved thread
        assert has_unresolved_review_threads(threads) is True
