"""
Tests for the ETag-based issue change detection in issue_etag_checker.

Verifies that:
- check_issues_etag_changed() returns None on the first call (baseline established)
- Returns False when all repos return 304 Not Modified (nothing changed)
- Returns True when any repo returns 200 (something changed)
- ETags are stored and sent as If-None-Match on subsequent calls
- Errors / empty output are treated as "changed" (safe fallback)
- reset_issue_etag_state() resets all module-level state
- Empty repos list returns False immediately (nothing to check)
"""


def _reset():
    """Reset module-level state in issue_etag_checker between tests."""
    import src.gh_pr_phase_monitor.github.issue_etag_checker as iec

    iec._repo_issue_etags.clear()


def _populate_etag_cache(owner: str = "user", repo: str = "repo1", etag: str = 'W/"e1"') -> None:
    """Populate the ETag cache to simulate a previous successful call."""
    import src.gh_pr_phase_monitor.github.issue_etag_checker as iec

    iec._repo_issue_etags[f"{owner}/{repo}"] = etag


# ---------------------------------------------------------------------------
# _parse_issue_response
# ---------------------------------------------------------------------------


class TestParseIssueResponse:
    def test_empty_output(self):
        from src.gh_pr_phase_monitor.github.issue_etag_checker import _parse_issue_response

        is_304, etag = _parse_issue_response("")
        assert is_304 is False
        assert etag is None

    def test_detects_304(self):
        from src.gh_pr_phase_monitor.github.issue_etag_checker import _parse_issue_response

        output = "HTTP/2 304 \r\n\r\n"
        is_304, etag = _parse_issue_response(output)
        assert is_304 is True
        assert etag is None

    def test_parses_etag_from_200(self):
        from src.gh_pr_phase_monitor.github.issue_etag_checker import _parse_issue_response

        output = 'HTTP/2 200 \netag: W/"abc123"\ncontent-type: application/json\n\n[]\n'
        is_304, etag = _parse_issue_response(output)
        assert is_304 is False
        assert etag == 'W/"abc123"'

    def test_no_etag_in_200(self):
        from src.gh_pr_phase_monitor.github.issue_etag_checker import _parse_issue_response

        output = "HTTP/2 200 \ncontent-type: application/json\n\n[]\n"
        is_304, etag = _parse_issue_response(output)
        assert is_304 is False
        assert etag is None


# ---------------------------------------------------------------------------
# check_issues_etag_changed — empty repos
# ---------------------------------------------------------------------------


class TestCheckIssuesEtagChangedEmptyRepos:
    def setup_method(self):
        _reset()

    def test_empty_repos_returns_false(self):
        """Empty repos list returns False immediately without any API calls."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        result = check_issues_etag_changed([])
        assert result is False

    def test_all_invalid_entries_returns_true(self, mocker):
        """When all entries are missing owner/name, treat as changed to avoid skipping GraphQL incorrectly."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        mock_run = mocker.patch("src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api")

        repos = [{"owner": "", "name": "repo1"}, {"owner": "user", "name": ""}]
        result = check_issues_etag_changed(repos)

        assert result is True
        mock_run.assert_not_called()

    def test_url_uses_sort_updated_direction_desc(self, mocker):
        """_run_issues_api should request sort=updated&direction=desc so any update changes the ETag."""
        import subprocess

        from src.gh_pr_phase_monitor.github.issue_etag_checker import _run_issues_api

        mock_run = mocker.patch("subprocess.run", return_value=mocker.MagicMock())

        _run_issues_api("user", "repo1")

        called_args = mock_run.call_args[0][0]
        url_arg = next(a for a in called_args if "issues" in a)
        assert "sort=updated" in url_arg
        assert "direction=desc" in url_arg


# ---------------------------------------------------------------------------
# check_issues_etag_changed — first call
# ---------------------------------------------------------------------------


class TestCheckIssuesEtagChangedFirstCall:
    def setup_method(self):
        _reset()

    def test_returns_none_on_first_call(self, mocker):
        """First call with a 200 response should return None (baseline established)."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"abc"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        result = check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert result is None

    def test_stores_etag_on_first_call(self, mocker):
        """After the first call the ETag should be stored in _repo_issue_etags."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"first-etag"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert iec._repo_issue_etags.get("user/repo1") == 'W/"first-etag"'

    def test_multiple_repos_first_call(self, mocker):
        """First call with multiple repos should return None and store all ETags."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        def fake_run(owner, repo, etag=None):
            m = mocker.MagicMock()
            m.stdout = f'HTTP/2 200 \netag: W/"etag-{repo}"\n\n[]\n'
            return m

        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            side_effect=fake_run,
        )

        repos = [{"owner": "user", "name": "repo1"}, {"owner": "user", "name": "repo2"}]
        result = check_issues_etag_changed(repos)

        assert result is None
        assert iec._repo_issue_etags.get("user/repo1") == 'W/"etag-repo1"'
        assert iec._repo_issue_etags.get("user/repo2") == 'W/"etag-repo2"'


# ---------------------------------------------------------------------------
# check_issues_etag_changed — 304 (nothing changed)
# ---------------------------------------------------------------------------


class TestCheckIssuesEtagChanged304:
    def setup_method(self):
        _reset()

    def test_returns_false_on_304(self, mocker):
        """304 response should return False (nothing changed)."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        _populate_etag_cache()

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        result = check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert result is False

    def test_sends_if_none_match_header(self, mocker):
        """The stored ETag should be forwarded as the If-None-Match arg."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        _populate_etag_cache(etag='W/"stored-etag"')

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mock_run = mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        mock_run.assert_called_once_with("user", "repo1", 'W/"stored-etag"')

    def test_does_not_overwrite_etag_on_304(self, mocker):
        """A 304 response should leave _repo_issue_etags unchanged."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        _populate_etag_cache(etag='W/"keep-me"')

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert iec._repo_issue_etags["user/repo1"] == 'W/"keep-me"'

    def test_all_repos_304_returns_false(self, mocker):
        """When all repos return 304, the result should be False."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        iec._repo_issue_etags["user/repo1"] = 'W/"e1"'
        iec._repo_issue_etags["user/repo2"] = 'W/"e2"'

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        repos = [{"owner": "user", "name": "repo1"}, {"owner": "user", "name": "repo2"}]
        result = check_issues_etag_changed(repos)

        assert result is False


# ---------------------------------------------------------------------------
# check_issues_etag_changed — 200 (something changed)
# ---------------------------------------------------------------------------


class TestCheckIssuesEtagChanged200:
    def setup_method(self):
        _reset()

    def test_returns_true_on_200(self, mocker):
        """A 200 response (ETag changed) should return True."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        _populate_etag_cache()

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"new-etag"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        result = check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert result is True

    def test_updates_stored_etag_on_200(self, mocker):
        """A 200 response should update _repo_issue_etags with the new ETag."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        _populate_etag_cache(etag='W/"old"')

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"new"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert iec._repo_issue_etags["user/repo1"] == 'W/"new"'

    def test_returns_true_on_error_output(self, mocker):
        """An unrecognized / error response is treated as changed (safe fallback)."""
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        _populate_etag_cache()

        mock_result = mocker.MagicMock()
        mock_result.stdout = ""  # no usable output
        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            return_value=mock_result,
        )

        result = check_issues_etag_changed([{"owner": "user", "name": "repo1"}])

        assert result is True

    def test_one_changed_repo_returns_true(self, mocker):
        """When one repo is 304 but another is 200, the result should be True."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        iec._repo_issue_etags["user/repo1"] = 'W/"e1"'
        iec._repo_issue_etags["user/repo2"] = 'W/"e2"'

        def fake_run(owner, repo, etag=None):
            m = mocker.MagicMock()
            if repo == "repo1":
                m.stdout = "HTTP/2 304 \n\n"
            else:
                m.stdout = 'HTTP/2 200 \netag: W/"e2-new"\n\n[]\n'
            return m

        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            side_effect=fake_run,
        )

        repos = [{"owner": "user", "name": "repo1"}, {"owner": "user", "name": "repo2"}]
        result = check_issues_etag_changed(repos)

        assert result is True
        assert iec._repo_issue_etags["user/repo2"] == 'W/"e2-new"'


# ---------------------------------------------------------------------------
# Mixed first-call and cached repos
# ---------------------------------------------------------------------------


class TestCheckIssuesEtagMixed:
    def setup_method(self):
        _reset()

    def test_new_repo_alongside_cached_returns_none(self, mocker):
        """When one repo is new (no stored ETag) and another is 304, result is None."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import check_issues_etag_changed

        # repo1 is cached, repo2 is new
        iec._repo_issue_etags["user/repo1"] = 'W/"e1"'

        def fake_run(owner, repo, etag=None):
            m = mocker.MagicMock()
            if repo == "repo1":
                m.stdout = "HTTP/2 304 \n\n"
            else:
                m.stdout = 'HTTP/2 200 \netag: W/"e2-new"\n\n[]\n'
            return m

        mocker.patch(
            "src.gh_pr_phase_monitor.github.issue_etag_checker._run_issues_api",
            side_effect=fake_run,
        )

        repos = [{"owner": "user", "name": "repo1"}, {"owner": "user", "name": "repo2"}]
        result = check_issues_etag_changed(repos)

        assert result is None
        assert iec._repo_issue_etags["user/repo2"] == 'W/"e2-new"'


# ---------------------------------------------------------------------------
# reset_issue_etag_state
# ---------------------------------------------------------------------------


class TestResetIssueEtagState:
    def test_reset_clears_all_state(self):
        """reset_issue_etag_state() should clear all module-level state."""
        import src.gh_pr_phase_monitor.github.issue_etag_checker as iec
        from src.gh_pr_phase_monitor.github.issue_etag_checker import reset_issue_etag_state

        iec._repo_issue_etags["user/repo1"] = 'W/"e1"'
        iec._repo_issue_etags["user/repo2"] = 'W/"e2"'

        reset_issue_etag_state()

        assert iec._repo_issue_etags == {}
