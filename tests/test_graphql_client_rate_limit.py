import subprocess
from unittest.mock import patch

import pytest

from src.gh_pr_phase_monitor.github.graphql_client import GitHubRateLimitError, execute_graphql_query


def test_execute_graphql_query_raises_rate_limit_error_on_api_limit_exceeded():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            subprocess.CalledProcessError(
                returncode=1,
                cmd=["gh", "api", "graphql"],
                stderr="gh: API rate limit already exceeded for user ID 5794738.",
            ),
            subprocess.CompletedProcess(
                args=["gh", "api", "rate_limit"],
                returncode=0,
                stdout='{"resources": {"graphql": {"limit": 5000, "used": 5003, "remaining": 0, "reset": 1777777777}}}',
                stderr="",
            ),
        ]

        with pytest.raises(
            GitHubRateLimitError,
            match="used=5003, remaining=0, limit=5000, reset=1777777777",
        ) as exc_info:
            execute_graphql_query("query { viewer { login } }")

        assert exc_info.value.rate_limit_info == {"limit": 5000, "used": 5003, "remaining": 0, "reset": 1777777777}


def test_execute_graphql_query_keeps_non_rate_limit_errors_as_runtime_error():
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["gh", "api", "graphql"],
            stderr="gh: authentication required",
        )

        with pytest.raises(RuntimeError) as exc_info:
            execute_graphql_query("query { viewer { login } }")

        assert not isinstance(exc_info.value, GitHubRateLimitError)
