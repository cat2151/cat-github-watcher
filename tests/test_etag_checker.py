"""
Tests for the ETag-based repository change detection in etag_checker.

Verifies that:
- check_repos_etag_changed() returns None on the first call (baseline established)
- Returns False when all pages return 304 Not Modified (nothing changed)
- Returns True when any page returns 200 (something changed)
- ETags are stored and sent as If-None-Match on subsequent calls
- Pagination is handled correctly (_last_page_count tracks multi-page accounts)
- Errors / empty output are treated as "changed" (safe fallback)
- reset_etag_state() resets all module-level state
"""


def _reset():
    """Reset module-level state in etag_checker between tests."""
    import src.gh_pr_phase_monitor.github.etag_checker as ec

    ec._page_etags.clear()
    ec._last_page_count = 0
    ec._initialized = False


# ---------------------------------------------------------------------------
# _parse_response
# ---------------------------------------------------------------------------


class TestParseResponse:
    def test_empty_output(self):
        from src.gh_pr_phase_monitor.github.etag_checker import _parse_response

        is_304, etag, has_next = _parse_response("")
        assert is_304 is False
        assert etag is None
        assert has_next is False

    def test_detects_304(self):
        from src.gh_pr_phase_monitor.github.etag_checker import _parse_response

        output = "HTTP/2 304 \r\n\r\n"
        is_304, etag, has_next = _parse_response(output)
        assert is_304 is True
        assert etag is None
        assert has_next is False

    def test_parses_etag_from_200(self):
        from src.gh_pr_phase_monitor.github.etag_checker import _parse_response

        output = 'HTTP/2 200 \netag: W/"abc123"\ncontent-type: application/json\n\n[]\n'
        is_304, etag, has_next = _parse_response(output)
        assert is_304 is False
        assert etag == 'W/"abc123"'
        assert has_next is False

    def test_detects_link_next(self):
        from src.gh_pr_phase_monitor.github.etag_checker import _parse_response

        output = (
            "HTTP/2 200 \n"
            'etag: W/"xyz"\n'
            'link: <https://api.github.com/user/repos?page=2>; rel="next"\n'
            "\n"
            "[]\n"
        )
        is_304, etag, has_next = _parse_response(output)
        assert is_304 is False
        assert etag == 'W/"xyz"'
        assert has_next is True

    def test_no_link_next_when_only_rel_prev(self):
        from src.gh_pr_phase_monitor.github.etag_checker import _parse_response

        output = (
            "HTTP/2 200 \n"
            'etag: W/"zzz"\n'
            'link: <https://api.github.com/user/repos?page=1>; rel="prev"\n'
            "\n"
            "[]\n"
        )
        is_304, etag, has_next = _parse_response(output)
        assert has_next is False


# ---------------------------------------------------------------------------
# check_repos_etag_changed — first call
# ---------------------------------------------------------------------------


class TestCheckReposEtagChangedFirstCall:
    def setup_method(self):
        _reset()

    def test_returns_none_on_first_call(self, mocker):
        """First call with a 200 response should return None (baseline established)."""
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"abc"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        result = check_repos_etag_changed()

        assert result is None

    def test_stores_etag_on_first_call(self, mocker):
        """After the first call the ETag should be stored in _page_etags."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"first-etag"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        check_repos_etag_changed()

        assert ec._page_etags.get(1) == 'W/"first-etag"'
        assert ec._initialized is True

    def test_sets_last_page_count_single_page(self, mocker):
        """With no Link: next header, _last_page_count should be set to 1."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"e1"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        check_repos_etag_changed()

        assert ec._last_page_count == 1


# ---------------------------------------------------------------------------
# check_repos_etag_changed — 304 (nothing changed)
# ---------------------------------------------------------------------------


class TestCheckReposEtagChanged304:
    def setup_method(self):
        _reset()

    def _pre_populate(self, etag: str = 'W/"e1"', last_page: int = 1):
        """Simulate a previous successful call by populating module state."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec

        ec._page_etags[1] = etag
        ec._last_page_count = last_page
        ec._initialized = True

    def test_returns_false_on_304(self, mocker):
        """304 response should return False (nothing changed)."""
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        self._pre_populate()

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        result = check_repos_etag_changed()

        assert result is False

    def test_sends_if_none_match_header(self, mocker):
        """The stored ETag should be forwarded as the If-None-Match arg."""
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        self._pre_populate(etag='W/"stored-etag"')

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mock_run = mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        check_repos_etag_changed()

        mock_run.assert_called_once_with(1, 'W/"stored-etag"')

    def test_does_not_overwrite_etag_on_304(self, mocker):
        """A 304 response should leave _page_etags unchanged."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        self._pre_populate(etag='W/"keep-me"')

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        check_repos_etag_changed()

        assert ec._page_etags[1] == 'W/"keep-me"'


# ---------------------------------------------------------------------------
# check_repos_etag_changed — 200 (something changed)
# ---------------------------------------------------------------------------


class TestCheckReposEtagChanged200:
    def setup_method(self):
        _reset()

    def _pre_populate(self, etag: str = 'W/"old"', last_page: int = 1):
        import src.gh_pr_phase_monitor.github.etag_checker as ec

        ec._page_etags[1] = etag
        ec._last_page_count = last_page
        ec._initialized = True

    def test_returns_true_on_200(self, mocker):
        """A 200 response (ETag changed) should return True."""
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        self._pre_populate()

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"new-etag"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        result = check_repos_etag_changed()

        assert result is True

    def test_updates_stored_etag_on_200(self, mocker):
        """A 200 response should update _page_etags with the new ETag."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        self._pre_populate(etag='W/"old"')

        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"new"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        check_repos_etag_changed()

        assert ec._page_etags[1] == 'W/"new"'

    def test_returns_true_on_error_output(self, mocker):
        """An unrecognized / error response is treated as changed (safe fallback)."""
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        self._pre_populate()

        mock_result = mocker.MagicMock()
        mock_result.stdout = ""  # no usable output
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        result = check_repos_etag_changed()

        assert result is True


# ---------------------------------------------------------------------------
# Pagination support
# ---------------------------------------------------------------------------


class TestPagination:
    def setup_method(self):
        _reset()

    def test_first_call_two_pages(self, mocker):
        """First call with two pages should return None after storing both ETags."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        page1_output = (
            "HTTP/2 200 \n"
            'etag: W/"p1"\n'
            'link: <https://api.github.com/user/repos?page=2>; rel="next"\n'
            "\n[]\n"
        )
        page2_output = 'HTTP/2 200 \netag: W/"p2"\n\n[]\n'

        call_count = [0]

        def fake_run(page, etag=None):
            call_count[0] += 1
            m = mocker.MagicMock()
            m.stdout = page1_output if page == 1 else page2_output
            return m

        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            side_effect=fake_run,
        )

        result = check_repos_etag_changed()

        assert result is None
        assert ec._page_etags[1] == 'W/"p1"'
        assert ec._page_etags[2] == 'W/"p2"'
        assert ec._last_page_count == 2
        assert call_count[0] == 2

    def test_second_call_both_pages_304(self, mocker):
        """When all pages return 304, the result should be False."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        # Simulate a previous successful call with 2 pages
        ec._page_etags[1] = 'W/"p1"'
        ec._page_etags[2] = 'W/"p2"'
        ec._last_page_count = 2
        ec._initialized = True

        mock_result = mocker.MagicMock()
        mock_result.stdout = "HTTP/2 304 \n\n"
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        result = check_repos_etag_changed()

        assert result is False

    def test_second_call_page2_changed(self, mocker):
        """When page 1 is 304 but page 2 returns 200, the result should be True."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        ec._page_etags[1] = 'W/"p1"'
        ec._page_etags[2] = 'W/"p2"'
        ec._last_page_count = 2
        ec._initialized = True

        def fake_run(page, etag=None):
            m = mocker.MagicMock()
            if page == 1:
                m.stdout = "HTTP/2 304 \n\n"
            else:
                m.stdout = 'HTTP/2 200 \netag: W/"p2-new"\n\n[]\n'
            return m

        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            side_effect=fake_run,
        )

        result = check_repos_etag_changed()

        assert result is True
        assert ec._page_etags[2] == 'W/"p2-new"'

    def test_purges_stale_etags_when_page_count_shrinks(self, mocker):
        """When the account shrinks from 2 pages to 1, stale ETags beyond page 1 are removed."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import check_repos_etag_changed

        # Simulate state after a previous 2-page response
        ec._page_etags[1] = 'W/"p1-old"'
        ec._page_etags[2] = 'W/"p2-old"'
        ec._last_page_count = 2
        ec._initialized = True

        # Now only one page is returned (repos were deleted, no Link: next)
        mock_result = mocker.MagicMock()
        mock_result.stdout = 'HTTP/2 200 \netag: W/"p1-new"\n\n[]\n'
        mocker.patch(
            "src.gh_pr_phase_monitor.github.etag_checker._run_repos_api",
            return_value=mock_result,
        )

        result = check_repos_etag_changed()

        assert result is True
        assert ec._last_page_count == 1
        assert 1 in ec._page_etags
        assert 2 not in ec._page_etags  # stale entry purged


# ---------------------------------------------------------------------------
# reset_etag_state
# ---------------------------------------------------------------------------


class TestResetEtagState:
    def test_reset_clears_all_state(self, mocker):
        """reset_etag_state() should clear all module-level state."""
        import src.gh_pr_phase_monitor.github.etag_checker as ec
        from src.gh_pr_phase_monitor.github.etag_checker import reset_etag_state

        ec._page_etags[1] = 'W/"e1"'
        ec._last_page_count = 3
        ec._initialized = True

        reset_etag_state()

        assert ec._page_etags == {}
        assert ec._last_page_count == 0
        assert ec._initialized is False
