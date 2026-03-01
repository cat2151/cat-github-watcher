"""
GraphQL client module for executing queries via GitHub CLI
"""

import json
import subprocess
from typing import Any, Dict


class GitHubRateLimitError(RuntimeError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, message: str, rate_limit_info: Dict[str, Any] | None = None):
        super().__init__(message)
        self.rate_limit_info = rate_limit_info


def _is_rate_limit_exceeded_error(stderr: str) -> bool:
    """Return True when stderr indicates a GitHub API rate limit exhaustion."""
    lower_stderr = stderr.lower()
    return "rate limit" in lower_stderr and ("exceeded" in lower_stderr or "exhausted" in lower_stderr)


def _get_graphql_rate_limit_info() -> Dict[str, Any] | None:
    """Fetch GraphQL rate limit details via gh api rate_limit.

    Returns:
        Dictionary containing GraphQL rate-limit fields, or None if unavailable.
    """
    try:
        result = subprocess.run(
            ["gh", "api", "rate_limit"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        data = json.loads(result.stdout or "{}")
        graphql_info = data.get("resources", {}).get("graphql")
        if isinstance(graphql_info, dict):
            return graphql_info
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def execute_graphql_query(query: str, variables: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Execute a GraphQL query using gh CLI

    Args:
        query: GraphQL query string
        variables: Optional dictionary of GraphQL variables

    Returns:
        Parsed JSON response from GitHub API

    Raises:
        RuntimeError: If the query execution fails
        json.JSONDecodeError: If the response cannot be parsed
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]

    # Add variables to command if provided
    if variables:
        for key, value in variables.items():
            cmd.extend(["-F", f"{key}={value}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            error_message = f"Error parsing JSON response from gh CLI: {e}\nRaw output from gh:\n{result.stdout}"
            print(error_message)
            raise RuntimeError(error_message) from e

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing GraphQL query: {e}"
        print(error_message)
        stderr_text = (e.stderr or "").strip()
        if stderr_text:
            print(f"stderr: {stderr_text}")

        if _is_rate_limit_exceeded_error(stderr_text):
            graphql_limit_info = _get_graphql_rate_limit_info()
            if graphql_limit_info:
                limit = graphql_limit_info.get("limit", "unknown")
                used = graphql_limit_info.get("used", "unknown")
                remaining = graphql_limit_info.get("remaining", "unknown")
                reset = graphql_limit_info.get("reset", "unknown")
                rate_limit_message = (
                    "GitHub API rate limit exceeded. "
                    f"GraphQL limit: used={used}, remaining={remaining}, limit={limit}, reset={reset}. "
                    "Wait for reset and retry."
                )
            else:
                rate_limit_message = (
                    "GitHub API rate limit exceeded. "
                    "Wait for reset and retry. "
                    "You can check remaining quota with `gh api rate_limit`."
                )
            raise GitHubRateLimitError(rate_limit_message, rate_limit_info=graphql_limit_info) from e

        raise RuntimeError(error_message) from e
