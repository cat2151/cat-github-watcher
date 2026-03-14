"""
Repository fetching module for GitHub repositories
"""

from typing import Any, Dict, List, Optional, Set

from .etag_checker import check_repos_etag_changed
from .github_auth import get_current_user
from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_PER_PAGE = 100

# Module-level cache: stores the last known updatedAt for each repository.
# Used to detect which repos have changed since the previous check, allowing
# expensive Phase 1/2 queries to be skipped when nothing has changed.
_last_repo_updated_at: Dict[str, str] = {}


def get_all_repos_updated_at() -> Dict[str, str]:
    """Lightweight query: get updatedAt timestamps for all user-owned repositories.

    This is used to cheaply detect which repositories have changed since the last
    monitoring iteration, before deciding whether to run the expensive Phase 1/2 queries.

    Returns:
        Dict mapping repository name to its updatedAt ISO timestamp string.
        Example: {"repo1": "2024-01-01T00:00:00Z", "repo2": "2024-01-02T00:00:00Z"}
    """
    current_user = get_current_user()

    query = """
    query($login: String!) {{
      user(login: $login) {{
        repositories(first: {repositories_per_page}, ownerAffiliations: [OWNER]) {{
          nodes {{
            name
            updatedAt
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
      }}
      rateLimit {{
        cost
        remaining
      }}
    }}
    """.format(repositories_per_page=REPOSITORIES_PER_PAGE)

    result: Dict[str, str] = {}
    has_next_page = True
    end_cursor = None

    while has_next_page:
        if end_cursor:
            query_with_pagination = query.replace(
                f"repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER])",
                f'repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER], after: "{end_cursor}")',
            )
        else:
            query_with_pagination = query

        data = execute_graphql_query(
            query_with_pagination, {"login": current_user}, intent="リポジトリ更新日時一括チェック"
        )

        repositories = data.get("data", {}).get("user", {}).get("repositories", {})
        nodes = repositories.get("nodes", [])
        page_info = repositories.get("pageInfo", {})

        for repo in nodes:
            name = repo.get("name", "")
            updated_at = repo.get("updatedAt", "")
            if name and updated_at:
                result[name] = updated_at

        has_next_page = page_info.get("hasNextPage", False)
        end_cursor = page_info.get("endCursor")

    return result


def get_repos_changed_since_last_check() -> Optional[Set[str]]:
    """Perform a lightweight check to find repositories that changed since the last call.

    Uses a two-stage strategy:

    1. **ETag pre-check** (REST API, ``If-None-Match``):  Pages that have not
       changed return HTTP 304 Not Modified, which does **not** consume GitHub
       API rate-limit points.  If every page returns 304, no repository has
       changed and the function returns an empty set immediately — the more
       expensive GraphQL ``updatedAt`` query is skipped entirely.

    2. **GraphQL updatedAt check** (fallback): When the ETag pre-check detects
       a change (or cannot be used), the function falls back to comparing
       ``updatedAt`` timestamps fetched via GraphQL to identify exactly which
       repositories changed.

    On the very first call (no stored baselines) both the ETag baseline and the
    ``updatedAt`` baseline are established, and the function returns ``None``.

    Returns:
        None if no previous data exists (first call — baselines now stored).
        Empty set if no repositories changed since the last check.
        Non-empty set of repository names whose updatedAt changed.
    """
    # Stage 1: ETag pre-check — free 304 responses skip the GraphQL query.
    try:
        etag_result = check_repos_etag_changed()
        if etag_result is False:
            # All pages returned 304: nothing has changed, skip GraphQL.
            print("  ETag: 全ページ 304 Not Modified → リポジトリ変化なし (GraphQL スキップ)")
            return set()
    except Exception:
        # ETag check failure is non-fatal; fall through to the updatedAt check.
        pass

    # Stage 2: GraphQL updatedAt check.
    current_map = get_all_repos_updated_at()

    if not _last_repo_updated_at:
        _last_repo_updated_at.update(current_map)
        return None

    changed: Set[str] = {name for name, ts in current_map.items() if _last_repo_updated_at.get(name) != ts}
    # Also treat repos that disappeared from the snapshot (deleted/renamed/lost access) as changed
    changed |= _last_repo_updated_at.keys() - current_map.keys()

    _last_repo_updated_at.clear()
    _last_repo_updated_at.update(current_map)
    return changed


def reset_repos_updated_at_baseline() -> None:
    """Clear the stored updatedAt baseline so the next call to get_repos_changed_since_last_check()
    treats it as a first call (returns None and stores a fresh baseline, triggering a full check).

    Use this when the monitoring state is inconsistent (e.g., no PR snapshot but updatedAt says
    nothing changed) to ensure the next iteration performs a complete Phase 1/2 check.
    """
    _last_repo_updated_at.clear()


def get_repositories_with_open_prs() -> List[Dict[str, Any]]:
    """Get all repositories with open PR counts using GraphQL (Phase 1)

    Returns:
        List of repositories with name and open PR count
        Example: [{"name": "repo1", "owner": "user", "openPRCount": 2}, ...]
    """
    current_user = get_current_user()

    # GraphQL query to get all repositories with open PR counts
    # Only includes user-owned repos (not organization repos)
    query = """
    query($login: String!) {{
      user(login: $login) {{
        repositories(first: {repositories_per_page}, ownerAffiliations: [OWNER]) {{
          nodes {{
            name
            owner {{
              login
            }}
            pullRequests(states: OPEN) {{
              totalCount
            }}
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
      }}
      rateLimit {{
        cost
        remaining
      }}
    }}
    """.format(repositories_per_page=REPOSITORIES_PER_PAGE)

    repos_with_prs = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        # Build query with pagination
        if end_cursor:
            query_with_pagination = query.replace(
                f"repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER])",
                f'repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER], after: "{end_cursor}")',
            )
        else:
            query_with_pagination = query

        # Execute GraphQL query
        data = execute_graphql_query(
            query_with_pagination, {"login": current_user}, intent="リポジトリ一覧取得 (open PRあり)"
        )

        repositories = data.get("data", {}).get("user", {}).get("repositories", {})
        nodes = repositories.get("nodes", [])
        page_info = repositories.get("pageInfo", {})

        # Filter repositories with open PRs
        for repo in nodes:
            pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
            if pr_count > 0:
                repos_with_prs.append(
                    {"name": repo.get("name"), "owner": repo.get("owner", {}).get("login"), "openPRCount": pr_count}
                )

        has_next_page = page_info.get("hasNextPage", False)
        end_cursor = page_info.get("endCursor")

    return repos_with_prs


def get_all_repositories() -> List[Dict[str, Any]]:
    """Get all repositories for the authenticated user using GraphQL

    Returns:
        List of repositories with name, owner, open PR count, and open issue count
        Example: [{"name": "repo1", "owner": "user", "openPRCount": 2, "openIssueCount": 5}, ...]
    """
    current_user = get_current_user()

    # GraphQL query to get all repositories with open PR and issue counts
    # Only includes user-owned repos (not organization repos)
    query = """
    query($login: String!) {{
      user(login: $login) {{
        repositories(first: {repositories_per_page}, ownerAffiliations: [OWNER]) {{
          nodes {{
            name
            owner {{
              login
            }}
            pullRequests(states: OPEN) {{
              totalCount
            }}
            issues(states: OPEN) {{
              totalCount
            }}
          }}
          pageInfo {{
            hasNextPage
            endCursor
          }}
        }}
      }}
      rateLimit {{
        cost
        remaining
      }}
    }}
    """.format(repositories_per_page=REPOSITORIES_PER_PAGE)

    all_repos = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        # Build query with pagination
        if end_cursor:
            query_with_pagination = query.replace(
                f"repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER])",
                f'repositories(first: {REPOSITORIES_PER_PAGE}, ownerAffiliations: [OWNER], after: "{end_cursor}")',
            )
        else:
            query_with_pagination = query

        # Execute GraphQL query
        data = execute_graphql_query(query_with_pagination, {"login": current_user}, intent="リポジトリ一覧取得 (全件)")

        repositories = data.get("data", {}).get("user", {}).get("repositories", {})
        nodes = repositories.get("nodes", [])
        page_info = repositories.get("pageInfo", {})

        # Collect all repositories with their counts
        for repo in nodes:
            pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
            issue_count = repo.get("issues", {}).get("totalCount", 0)
            all_repos.append(
                {
                    "name": repo.get("name"),
                    "owner": repo.get("owner", {}).get("login"),
                    "openPRCount": pr_count,
                    "openIssueCount": issue_count,
                }
            )

        has_next_page = page_info.get("hasNextPage", False)
        end_cursor = page_info.get("endCursor")

    return all_repos


def get_repositories_with_no_prs_and_open_issues() -> List[Dict[str, Any]]:
    """Get repositories that have no open PRs but have open issues

    Returns:
        List of repositories with name, owner, and open issue count
        Example: [{"name": "repo1", "owner": "user", "openIssueCount": 5}, ...]
    """
    all_repos = get_all_repositories()

    # Filter repositories: no open PRs AND has open issues
    filtered_repos = [repo for repo in all_repos if repo["openPRCount"] == 0 and repo["openIssueCount"] > 0]

    return filtered_repos
