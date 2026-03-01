"""
Tests for has_comments_with_reactions function
"""

from src.gh_pr_phase_monitor import has_comments_with_reactions


class TestHasCommentsWithReactions:
    """Test the has_comments_with_reactions function"""

    def test_no_comments(self):
        """Empty comments list should return False"""
        assert has_comments_with_reactions([]) is False

    def test_comments_without_reactions(self):
        """Comments without reactionGroups should return False"""
        comments = [
            {"body": "Test comment 1"},
            {"body": "Test comment 2"},
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_empty_reaction_groups(self):
        """Comments with empty reactionGroups should return False"""
        comments = [
            {"body": "Test comment", "reactionGroups": []},
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_zero_count_reactions(self):
        """Comments with reactionGroups but zero users should return False"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 0}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is False

    def test_comments_with_reactions(self):
        """Comments with non-empty reactionGroups should return True"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 1}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_multiple_comments_with_reactions(self):
        """Multiple comments, one with reactions should return True"""
        comments = [
            {"body": "Test comment 1"},
            {
                "body": "Test comment 2",
                "reactionGroups": [
                    {"content": "EYES", "users": {"totalCount": 2}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_multiple_reaction_groups(self):
        """Comment with multiple reaction groups should return True"""
        comments = [
            {
                "body": "Test comment",
                "reactionGroups": [
                    {"content": "THUMBS_UP", "users": {"totalCount": 0}},
                    {"content": "EYES", "users": {"totalCount": 1}},
                ],
            },
        ]
        assert has_comments_with_reactions(comments) is True

    def test_backward_compatibility_with_integer(self):
        """Integer comments (from legacy API) should return False"""
        assert has_comments_with_reactions(5) is False

    def test_backward_compatibility_with_none(self):
        """None comments should return False"""
        assert has_comments_with_reactions(None) is False
