"""
Tests for pr_html_saver module (and fetch_pr_html wrapper)
"""

from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.phase.pr_html_saver import fetch_pr_html, parse_pr_url, save_pr_html


class TestParsePrUrl:
    def test_valid_url(self):
        owner, repo, pr_number = parse_pr_url("https://github.com/cat2151/cat-github-watcher/pull/123")
        assert owner == "cat2151"
        assert repo == "cat-github-watcher"
        assert pr_number == "123"

    def test_invalid_url_returns_none_triple(self):
        owner, repo, pr_number = parse_pr_url("https://example.com/not-a-pr")
        assert owner is None
        assert repo is None
        assert pr_number is None

    def test_missing_pull_segment(self):
        owner, repo, pr_number = parse_pr_url("https://github.com/cat2151/cat-github-watcher")
        assert owner is None
        assert repo is None
        assert pr_number is None

    def test_pr_number_extracted(self):
        _, _, pr_number = parse_pr_url("https://github.com/org/repo/pull/999")
        assert pr_number == "999"


class TestFetchPrHtml:
    def _make_run(self, returncode=0, stdout=""):
        mock = MagicMock()
        mock.returncode = returncode
        mock.stdout = stdout
        return mock

    def test_returns_html_on_success(self):
        html_body = "<html><body>PR content</body></html>"
        curl_mock = self._make_run(returncode=0, stdout=f"{html_body}\n200")

        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", return_value=curl_mock):
            result = fetch_pr_html("https://github.com/owner/repo/pull/1")

        assert result == html_body

    def test_returns_none_on_curl_failure(self):
        curl_mock = self._make_run(returncode=1, stdout="")

        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", return_value=curl_mock):
            result = fetch_pr_html("https://github.com/owner/repo/pull/1")

        assert result is None

    def test_returns_none_on_non_2xx_status(self):
        html_body = "<html>Not Found</html>"
        curl_mock = self._make_run(returncode=0, stdout=f"{html_body}\n404")

        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", return_value=curl_mock):
            result = fetch_pr_html("https://github.com/owner/repo/pull/1")

        assert result is None

    def test_returns_none_on_subprocess_exception(self):
        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", side_effect=OSError("no curl")):
            result = fetch_pr_html("https://github.com/owner/repo/pull/1")

        assert result is None


class TestSavePrHtml:
    def test_saves_file_with_correct_name(self, tmp_path):
        html_content = "<html><body>PR</body></html>"
        curl_mock = MagicMock(returncode=0, stdout=f"{html_content}\n200")

        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", return_value=curl_mock):
            result = save_pr_html("https://github.com/cat2151/cat-github-watcher/pull/42", tmp_path)

        assert result is not None
        expected = tmp_path / "cat-github-watcher_42.html"
        assert result == expected
        assert expected.exists()
        assert expected.read_text(encoding="utf-8") == html_content

    def test_creates_output_directory(self, tmp_path):
        nested_dir = tmp_path / "a" / "b" / "logs" / "pr"
        html_content = "<html>test</html>"
        curl_mock = MagicMock(returncode=0, stdout=f"{html_content}\n200")

        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", return_value=curl_mock):
            result = save_pr_html("https://github.com/o/my-repo/pull/7", nested_dir)

        assert result is not None
        assert nested_dir.exists()

    def test_returns_none_for_invalid_url(self, tmp_path):
        result = save_pr_html("https://example.com/not-a-pr", tmp_path)
        assert result is None

    def test_returns_none_when_fetch_fails(self, tmp_path):
        curl_mock = MagicMock(returncode=1, stdout="")

        with patch("src.gh_pr_phase_monitor.phase.pr_html_fetcher.subprocess.run", return_value=curl_mock):
            result = save_pr_html("https://github.com/o/repo/pull/1", tmp_path)

        assert result is None


class TestMainFetchPrHtmlOption:
    """Tests for --fetch-pr-html option in main.py"""

    def test_exits_zero_on_success(self, tmp_path):
        """--fetch-pr-html with valid URL and successful fetch exits with code 0"""
        import sys

        import pytest

        saved_argv = sys.argv[:]
        sys.argv = ["cat-github-watcher.py", "--fetch-pr-html", "https://github.com/o/repo/pull/1"]
        try:
            with patch(
                "src.gh_pr_phase_monitor.phase.pr_html_saver.save_pr_html",
                return_value=tmp_path / "repo_1.html",
            ):
                from src.gh_pr_phase_monitor.main import main

                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
        finally:
            sys.argv = saved_argv

    def test_exits_one_on_failure(self):
        """--fetch-pr-html with fetch failure exits with code 1"""
        import sys

        import pytest

        saved_argv = sys.argv[:]
        sys.argv = ["cat-github-watcher.py", "--fetch-pr-html", "https://github.com/o/repo/pull/1"]
        try:
            with patch("src.gh_pr_phase_monitor.phase.pr_html_saver.save_pr_html", return_value=None):
                from src.gh_pr_phase_monitor.main import main

                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
        finally:
            sys.argv = saved_argv
