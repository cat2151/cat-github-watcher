"""
Tests for GitHub Pages deployment monitoring (pages_watcher module)
"""


from src.gh_pr_phase_monitor.monitor import pages_watcher
from src.gh_pr_phase_monitor.monitor.pages_watcher import (
    check_pages_deployment,
    check_pages_deployments_for_repos,
    get_main_branch_sha,
    get_pages_latest_build,
    get_pages_repos_from_config,
    get_pages_url,
    process_pages_deployment,
)


class TestGetMainBranchSha:
    """Tests for get_main_branch_sha"""

    def test_returns_sha_on_success(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = "abc1234567890abcdef\n"
        mock_run = mocker.patch("subprocess.run", return_value=mock_result)
        result = get_main_branch_sha("owner", "repo")
        assert result == "abc1234567890abcdef"
        mock_run.assert_called_once_with(
            ["gh", "api", "repos/owner/repo/branches/main", "--jq", ".commit.sha"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )

    def test_returns_none_on_api_error(self, mocker):
        import subprocess

        mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "gh"))
        result = get_main_branch_sha("owner", "repo")
        assert result is None

    def test_returns_none_on_empty_response(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = "\n"
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_main_branch_sha("owner", "repo")
        assert result is None

    def test_returns_none_on_null_response(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = "null\n"
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_main_branch_sha("owner", "repo")
        assert result is None


class TestGetPagesLatestBuild:
    """Tests for get_pages_latest_build"""

    def test_returns_build_on_success(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = '{"status": "built", "commit": "abc123"}\n'
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_pages_latest_build("owner", "repo")
        assert result == {"status": "built", "commit": "abc123"}

    def test_returns_none_on_api_error(self, mocker):
        import subprocess

        mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "gh"))
        result = get_pages_latest_build("owner", "repo")
        assert result is None

    def test_returns_none_on_empty_response(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = ""
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_pages_latest_build("owner", "repo")
        assert result is None

    def test_returns_none_on_null_response(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = "null\n"
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_pages_latest_build("owner", "repo")
        assert result is None

    def test_returns_none_on_invalid_json(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = "not-json"
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_pages_latest_build("owner", "repo")
        assert result is None


class TestGetPagesUrl:
    """Tests for get_pages_url"""

    def test_returns_url_on_success(self, mocker):
        mock_result = mocker.MagicMock()
        mock_result.stdout = "https://owner.github.io/repo/\n"
        mocker.patch("subprocess.run", return_value=mock_result)
        result = get_pages_url("owner", "repo")
        assert result == "https://owner.github.io/repo/"

    def test_returns_none_on_api_error(self, mocker):
        import subprocess

        mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "gh"))
        result = get_pages_url("owner", "repo")
        assert result is None


class TestCheckPagesDeployment:
    """Tests for check_pages_deployment logic"""

    def test_deployed_when_built_and_sha_matches(self, mocker):
        sha = "abc1234567890abcdef"
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_main_branch_sha", return_value=sha)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_latest_build",
                return_value={"status": "built", "commit": sha},)
        result = check_pages_deployment("owner", "repo")
        assert result["status"] == "deployed"
        assert result["sha"] == sha
        assert result["build_sha"] == sha
        assert result["build_status"] == "built"

    def test_pending_when_build_sha_differs(self, mocker):
        main_sha = "abc1234567890abcdef"
        build_sha = "def456"
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_main_branch_sha", return_value=main_sha)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_latest_build",
                return_value={"status": "built", "commit": build_sha},)
        result = check_pages_deployment("owner", "repo")
        assert result["status"] == "pending"
        assert result["sha"] == main_sha
        assert result["build_sha"] == build_sha

    def test_errored_when_build_status_errored(self, mocker):
        sha = "abc1234567890abcdef"
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_main_branch_sha", return_value=sha)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_latest_build",
                return_value={"status": "errored", "commit": sha},)
        result = check_pages_deployment("owner", "repo")
        assert result["status"] == "errored"
        assert result["sha"] == sha

    def test_unknown_when_main_sha_unavailable(self, mocker):
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_main_branch_sha", return_value=None)
        result = check_pages_deployment("owner", "repo")
        assert result["status"] == "unknown"
        assert result["sha"] is None

    def test_pending_when_no_build_found(self, mocker):
        sha = "abc1234567890abcdef"
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_main_branch_sha", return_value=sha)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_latest_build", return_value=None)
        result = check_pages_deployment("owner", "repo")
        assert result["status"] == "pending"
        assert result["sha"] == sha
        assert result["build_sha"] is None


class TestProcessPagesDeployment:
    """Tests for process_pages_deployment"""

    def setup_method(self):
        """Clear tracking state before each test"""
        pages_watcher._pages_browser_opened.clear()

    def _make_config(self, pages_open_enabled: bool, repo_name: str = "test-repo"):
        return {
            "rulesets": [
                {
                    "repositories": [repo_name],
                    "enable_execution_pages_open": pages_open_enabled,
                }
            ]
        }

    def test_opens_browser_when_deployed_and_enabled(self, mocker):
        sha = "abc1234567890abcdef"
        pages_url = "https://owner.github.io/test-repo/"
        config = self._make_config(True)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
                return_value={"status": "deployed", "sha": sha, "build_sha": sha, "build_status": "built"},)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_url", return_value=pages_url)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._can_open_browser", return_value=True)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._should_autoraise_window", return_value=True)
        mock_record = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._record_browser_open")
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        process_pages_deployment("owner", "test-repo", config)
        mock_open.assert_called_once_with(pages_url, autoraise=True)
        mock_record.assert_called_once()

    def test_dry_run_when_deployed_and_disabled(self, mocker, capsys):
        sha = "abc1234567890abcdef"
        pages_url = "https://owner.github.io/test-repo/"
        config = self._make_config(False)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
                return_value={"status": "deployed", "sha": sha, "build_sha": sha, "build_status": "built"},)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_url", return_value=pages_url)
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        process_pages_deployment("owner", "test-repo", config)
        mock_open.assert_not_called()
        captured = capsys.readouterr()
        assert "[DRY-RUN]" in captured.out
        assert "enable_execution_pages_open=false" in captured.out

    def test_browser_not_opened_twice_for_same_sha(self, mocker):
        sha = "abc1234567890abcdef"
        pages_url = "https://owner.github.io/test-repo/"
        config = self._make_config(True)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
                return_value={"status": "deployed", "sha": sha, "build_sha": sha, "build_status": "built"},)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_url", return_value=pages_url)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._can_open_browser", return_value=True)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._should_autoraise_window", return_value=True)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._record_browser_open")
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        # First call - should open browser
        process_pages_deployment("owner", "test-repo", config)
        assert mock_open.call_count == 1

        # Second call with same SHA - should not open browser again
        process_pages_deployment("owner", "test-repo", config)
        assert mock_open.call_count == 1

    def test_opens_actions_when_errored_and_enabled(self, mocker):
        sha = "abc1234567890abcdef"
        config = self._make_config(True)
        actions_url = "https://github.com/owner/test-repo/actions"

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
                return_value={"status": "errored", "sha": sha, "build_sha": sha, "build_status": "errored"},)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._can_open_browser", return_value=True)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._should_autoraise_window", return_value=True)
        mock_record = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._record_browser_open")
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        process_pages_deployment("owner", "test-repo", config)
        mock_open.assert_called_once_with(actions_url, autoraise=True)
        mock_record.assert_called_once()

    def test_dry_run_when_errored_and_disabled(self, mocker, capsys):
        sha = "abc1234567890abcdef"
        config = self._make_config(False)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
            return_value={"status": "errored", "sha": sha, "build_sha": sha, "build_status": "errored"},)
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        process_pages_deployment("owner", "test-repo", config)
        mock_open.assert_not_called()
        captured = capsys.readouterr()
        assert "[DRY-RUN]" in captured.out
        assert "actions" in captured.out

    def test_shows_pending_message_each_iteration(self, mocker, capsys):
        sha = "abc1234"
        build_sha = "def456"
        config = self._make_config(True)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
                return_value={"status": "pending", "sha": sha, "build_sha": build_sha, "build_status": "building"},)
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        process_pages_deployment("owner", "test-repo", config)
        process_pages_deployment("owner", "test-repo", config)
        mock_open.assert_not_called()
        captured = capsys.readouterr()
        # Pending message should appear twice (no tracking)
        assert captured.out.count("pending") == 2

    def test_unknown_status_produces_no_output(self, mocker, capsys):
        config = self._make_config(True)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
            return_value={"status": "unknown", "sha": None, "build_sha": None, "build_status": None},)
        process_pages_deployment("owner", "test-repo", config)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_cooldown_prevents_browser_open(self, mocker, capsys):
        sha = "abc1234567890abcdef"
        pages_url = "https://owner.github.io/test-repo/"
        config = self._make_config(True)

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.check_pages_deployment",
                return_value={"status": "deployed", "sha": sha, "build_sha": sha, "build_status": "built"},)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.get_pages_url", return_value=pages_url)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._can_open_browser", return_value=False)
        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher._get_remaining_cooldown", return_value=45.0)
        mock_open = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.webbrowser.open")
        process_pages_deployment("owner", "test-repo", config)
        mock_open.assert_not_called()
        captured = capsys.readouterr()
        assert "cooldown" in captured.out


class TestGetPagesReposFromConfig:
    """Tests for get_pages_repos_from_config"""

    def test_returns_repos_with_flag_explicitly_set(self):
        config = {
            "rulesets": [
                {
                    "repositories": ["repo-a"],
                    "enable_execution_pages_open": True,
                },
                {
                    "repositories": ["repo-b"],
                    "enable_execution_pages_open": False,
                },
            ]
        }
        result = get_pages_repos_from_config(config, "myuser")
        names = [r["name"] for r in result]
        assert "repo-a" in names
        assert "repo-b" in names

    def test_skips_repos_without_flag(self):
        config = {
            "rulesets": [
                {
                    "repositories": ["repo-a"],
                    # No enable_execution_pages_open key
                    "enable_execution_phase1_to_phase2": True,
                },
            ]
        }
        result = get_pages_repos_from_config(config, "myuser")
        assert result == []

    def test_skips_all_pattern(self):
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_pages_open": True,
                },
            ]
        }
        result = get_pages_repos_from_config(config, "myuser")
        assert result == []

    def test_deduplicates_repos_across_rulesets(self):
        config = {
            "rulesets": [
                {
                    "repositories": ["repo-a"],
                    "enable_execution_pages_open": True,
                },
                {
                    "repositories": ["repo-a"],
                    "enable_execution_pages_open": False,
                },
            ]
        }
        result = get_pages_repos_from_config(config, "myuser")
        assert len(result) == 1
        assert result[0]["name"] == "repo-a"

    def test_uses_current_user_as_owner(self):
        config = {
            "rulesets": [
                {
                    "repositories": ["my-repo"],
                    "enable_execution_pages_open": True,
                },
            ]
        }
        result = get_pages_repos_from_config(config, "testuser")
        assert result[0]["owner"] == "testuser"

    def test_empty_config(self):
        result = get_pages_repos_from_config({}, "myuser")
        assert result == []


class TestCheckPagesDeploymentsForRepos:
    """Tests for check_pages_deployments_for_repos"""

    def setup_method(self):
        pages_watcher._pages_browser_opened.clear()

    def test_processes_all_repos_in_list(self, mocker):
        repos = [
            {"name": "repo-a", "owner": "user"},
            {"name": "repo-b", "owner": "user"},
        ]
        config = {
            "rulesets": [
                {"repositories": ["repo-a", "repo-b"], "enable_execution_pages_open": False},
            ]
        }

        mock_process = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.process_pages_deployment")
        check_pages_deployments_for_repos(repos, config)
        assert mock_process.call_count == 2
        mock_process.assert_any_call("user", "repo-a", config)
        mock_process.assert_any_call("user", "repo-b", config)

    def test_skips_duplicates(self, mocker):
        repos = [
            {"name": "repo-a", "owner": "user"},
            {"name": "repo-a", "owner": "user"},
        ]
        config = {
            "rulesets": [
                {"repositories": ["repo-a"], "enable_execution_pages_open": True},
            ]
        }

        mock_process = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.process_pages_deployment")
        check_pages_deployments_for_repos(repos, config)
        assert mock_process.call_count == 1

    def test_returns_early_with_no_config(self, mocker):
        repos = [{"name": "repo-a", "owner": "user"}]
        mock_process = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.process_pages_deployment")
        check_pages_deployments_for_repos(repos, None)
        mock_process.assert_not_called()

    def test_returns_early_with_empty_repos(self, mocker):
        config = {"rulesets": [{"repositories": ["repo-a"], "enable_execution_pages_open": True}]}
        mock_process = mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.process_pages_deployment")
        check_pages_deployments_for_repos([], config)
        mock_process.assert_not_called()

    def test_handles_exception_from_process(self, mocker, capsys):
        repos = [{"name": "repo-a", "owner": "user"}]
        config = {
            "rulesets": [
                {"repositories": ["repo-a"], "enable_execution_pages_open": True},
            ]
        }

        mocker.patch("src.gh_pr_phase_monitor.monitor.pages_watcher.process_pages_deployment",
            side_effect=Exception("API error"),)
        # Should not raise; exception is caught and printed
        check_pages_deployments_for_repos(repos, config)
        captured = capsys.readouterr()
        assert "Error checking Pages deployment" in captured.out
