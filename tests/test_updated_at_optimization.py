"""
Tests for the updatedAt-based GraphQL query optimization in repository_fetcher.

Verifies that:
- get_repos_changed_since_last_check() returns None on first call (baseline stored)
- Returns an empty set when nothing changed
- Returns the changed repo names when updatedAt differs
- Module-level state is updated correctly after each call
"""



def _reset_module_state():
    """Reset the module-level _last_repo_updated_at dict between tests."""
    import src.gh_pr_phase_monitor.github.repository_fetcher as rf

    rf._last_repo_updated_at.clear()


class TestGetReposChangedSinceLastCheck:
    """Tests for get_repos_changed_since_last_check()."""

    def setup_method(self):
        _reset_module_state()

    def test_returns_none_on_first_call(self, mocker):
        """First call should store baseline and return None (no prior data)."""
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        current_map = {"repo-a": "2024-01-01T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=current_map,
        )
        result = get_repos_changed_since_last_check()

        assert result is None

    def test_stores_baseline_on_first_call(self, mocker):
        """After the first call, _last_repo_updated_at should contain the fetched values."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        current_map = {"repo-a": "2024-01-01T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=current_map,
        )
        get_repos_changed_since_last_check()

        assert rf._last_repo_updated_at == current_map

    def test_returns_empty_set_when_nothing_changed(self, mocker):
        """Second call with same updatedAt values should return an empty set."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        current_map = {"repo-a": "2024-01-01T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}
        # Pre-populate the stored baseline
        rf._last_repo_updated_at.update(current_map)

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=dict(current_map),
        )
        result = get_repos_changed_since_last_check()

        assert result == set()

    def test_returns_changed_repo_names(self, mocker):
        """When a repo's updatedAt changes, it should appear in the returned set."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        old_map = {"repo-a": "2024-01-01T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}
        new_map = {"repo-a": "2024-01-03T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}
        rf._last_repo_updated_at.update(old_map)

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=new_map,
        )
        result = get_repos_changed_since_last_check()

        assert result == {"repo-a"}

    def test_returns_multiple_changed_repo_names(self, mocker):
        """Multiple changed repos should all appear in the returned set."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        old_map = {
            "repo-a": "2024-01-01T00:00:00Z",
            "repo-b": "2024-01-02T00:00:00Z",
            "repo-c": "2024-01-03T00:00:00Z",
        }
        new_map = {
            "repo-a": "2024-01-05T00:00:00Z",  # changed
            "repo-b": "2024-01-02T00:00:00Z",  # unchanged
            "repo-c": "2024-01-06T00:00:00Z",  # changed
        }
        rf._last_repo_updated_at.update(old_map)

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=new_map,
        )
        result = get_repos_changed_since_last_check()

        assert result == {"repo-a", "repo-c"}

    def test_includes_new_repos_not_in_baseline(self, mocker):
        """A repo that was not in the previous snapshot is treated as changed."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        old_map = {"repo-a": "2024-01-01T00:00:00Z"}
        new_map = {"repo-a": "2024-01-01T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}
        rf._last_repo_updated_at.update(old_map)

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=new_map,
        )
        result = get_repos_changed_since_last_check()

        assert "repo-b" in result

    def test_updates_baseline_after_second_call(self, mocker):
        """After each call, _last_repo_updated_at should be updated to the latest values."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        old_map = {"repo-a": "2024-01-01T00:00:00Z"}
        new_map = {"repo-a": "2024-01-03T00:00:00Z"}
        rf._last_repo_updated_at.update(old_map)

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=new_map,
        )
        get_repos_changed_since_last_check()

        assert rf._last_repo_updated_at == new_map

    def test_includes_removed_repos_as_changed(self, mocker):
        """A repo that was in the baseline but no longer appears is treated as changed."""
        import src.gh_pr_phase_monitor.github.repository_fetcher as rf
        from src.gh_pr_phase_monitor.github.repository_fetcher import get_repos_changed_since_last_check

        old_map = {"repo-a": "2024-01-01T00:00:00Z", "repo-b": "2024-01-02T00:00:00Z"}
        # repo-b has disappeared (deleted, renamed, or access revoked)
        new_map = {"repo-a": "2024-01-01T00:00:00Z"}
        rf._last_repo_updated_at.update(old_map)

        mocker.patch(
            "src.gh_pr_phase_monitor.github.repository_fetcher.get_all_repos_updated_at",
            return_value=new_map,
        )
        result = get_repos_changed_since_last_check()

        assert "repo-b" in result
