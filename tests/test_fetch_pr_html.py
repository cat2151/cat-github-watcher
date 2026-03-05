"""
Tests for pr_html_saver module (and fetch_pr_html wrapper)
"""

from unittest.mock import MagicMock, patch

from src.gh_pr_phase_monitor.phase.pr_html_saver import fetch_pr_html, parse_pr_url, save_html_to_logs, save_pr_html


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


class TestSaveHtmlToLogs:
    def test_invalid_url_returns_none(self, tmp_path):
        result = save_html_to_logs("<html>content</html>", "https://example.com/not-a-pr", output_dir=tmp_path)
        assert result is None

    def test_invalid_url_prints_to_stderr(self, tmp_path, capsys):
        save_html_to_logs("<html></html>", "https://example.com/bad", output_dir=tmp_path)
        captured = capsys.readouterr()
        assert "エラー" in captured.err

    def test_saves_html_with_owner_in_filename(self, tmp_path):
        html = "<html><body>PR</body></html>"
        result = save_html_to_logs(html, "https://github.com/cat2151/my-repo/pull/5", output_dir=tmp_path)
        assert result is not None
        expected = tmp_path / "my-repo_5.html"
        assert result == expected
        assert expected.exists()
        assert expected.read_text(encoding="utf-8") == html

    def test_saves_json_alongside_html(self, tmp_path):
        html = "<html><body>PR</body></html>"
        result = save_html_to_logs(html, "https://github.com/cat2151/my-repo/pull/5", output_dir=tmp_path)
        assert result is not None
        json_path = result.with_suffix(".json")
        assert json_path.exists()

    def test_uses_pre_computed_analysis_without_reanalysis(self, tmp_path):
        html = "<html><body>PR</body></html>"
        precomputed = {"pr_url": "https://github.com/o/r/pull/1", "is_draft": True, "llm_statuses": [], "status": "PHASE1A_DRAFT_LLM_WORKING"}
        from unittest.mock import patch
        with patch("src.gh_pr_phase_monitor.phase.pr_html_saver.analyze_pr_html") as mock_analyze:
            save_html_to_logs(html, "https://github.com/o/r/pull/1", analysis=precomputed, output_dir=tmp_path)
            mock_analyze.assert_not_called()

    def test_skips_write_when_content_unchanged(self, tmp_path):
        html = "<html><body>PR</body></html>"
        url = "https://github.com/cat2151/my-repo/pull/7"
        analysis = {"pr_url": url, "is_draft": False, "llm_statuses": [], "status": "PHASE1C_REVIEW_IN_PROGRESS"}
        save_html_to_logs(html, url, analysis=analysis, output_dir=tmp_path)
        html_file = tmp_path / "my-repo_7.html"
        json_file = html_file.with_suffix(".json")
        mtime_html = html_file.stat().st_mtime_ns
        mtime_json = json_file.stat().st_mtime_ns
        # Second call with identical content – files should not be touched
        save_html_to_logs(html, url, analysis=analysis, output_dir=tmp_path)
        assert html_file.stat().st_mtime_ns == mtime_html
        assert json_file.stat().st_mtime_ns == mtime_json

    def test_creates_output_directory(self, tmp_path):
        nested = tmp_path / "a" / "b"
        html = "<html></html>"
        result = save_html_to_logs(html, "https://github.com/o/r/pull/3", output_dir=nested)
        assert result is not None
        assert nested.exists()

    def test_prints_saved_when_new_file(self, tmp_path, capsys):
        html = "<html><body>new PR</body></html>"
        url = "https://github.com/cat2151/my-repo/pull/9"
        save_html_to_logs(html, url, output_dir=tmp_path)
        captured = capsys.readouterr()
        assert captured.out.count("保存") == 2  # once for HTML, once for JSON
        assert "スキップ" not in captured.out

    def test_prints_skipped_when_content_unchanged(self, tmp_path, capsys):
        html = "<html><body>unchanged</body></html>"
        url = "https://github.com/cat2151/my-repo/pull/10"
        analysis = {"pr_url": url, "is_draft": False, "llm_statuses": [], "status": "PHASE1C_REVIEW_IN_PROGRESS"}
        save_html_to_logs(html, url, analysis=analysis, output_dir=tmp_path)
        capsys.readouterr()  # discard first-write output
        # Second call with identical content should print skip messages for both HTML and JSON
        save_html_to_logs(html, url, analysis=analysis, output_dir=tmp_path)
        captured = capsys.readouterr()
        assert captured.out.count("スキップ") == 2  # once for HTML, once for JSON


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
