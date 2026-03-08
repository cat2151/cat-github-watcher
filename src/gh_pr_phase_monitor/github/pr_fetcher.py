"""
PR fetching module for GitHub pull requests
"""

import json
from typing import Any, Dict, List

from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_BATCH_SIZE = 10


def get_pr_details_batch(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get PR details for multiple repositories in a single GraphQL query (Phase 2)

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys

    Returns:
        List of PR data matching the format expected by determine_phase()
    """
    if not repos:
        return []

    # Build GraphQL query with aliases for multiple repositories
    # Limit to REPOSITORIES_BATCH_SIZE repos per query to avoid overly complex queries
    all_prs = []

    for i in range(0, len(repos), REPOSITORIES_BATCH_SIZE):
        batch = repos[i : i + REPOSITORIES_BATCH_SIZE]

        # Build query fragments for each repository
        repo_queries = []
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_name = repo["name"]
            owner = repo["owner"]

            # Escape values to prevent GraphQL injection
            owner_literal = json.dumps(owner)
            repo_name_literal = json.dumps(repo_name)

            # Note: We intentionally fetch a single page of open PRs and rely on GitHub's
            # maximum page size (first: 100). Repositories with >100 open PRs will be
            # truncated; add pagination here if full coverage is required.
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              pullRequests(first: 100, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
                nodes {{
                  title
                  url
                  isDraft
                  createdAt
                  author {{
                    login
                  }}
                  reviewRequests(first: 10) {{
                    nodes {{
                      requestedReviewer {{
                        ... on User {{
                          login
                        }}
                        ... on Team {{
                          name
                        }}
                      }}
                    }}
                  }}
                  comments(last: 10) {{
                    nodes {{
                      reactionGroups {{
                        content
                        users {{
                          totalCount
                        }}
                      }}
                    }}
                  }}
                  # Note: We fetch only the first 100 review threads; PRs with more than 100
                  # threads will be truncated unless pagination is added.
                  reviewThreads(first: 100) {{
                    nodes {{
                      isResolved
                      isOutdated
                    }}
                  }}
                }}
              }}
            }}
            """
            repo_queries.append(repo_query)

        # Combine all repository queries
        full_query = f"""
        query {{
          {" ".join(repo_queries)}
          rateLimit {{
            cost
            remaining
            resetAt
          }}
        }}
        """

        # Execute GraphQL query
        batch_num = i // REPOSITORIES_BATCH_SIZE + 1
        data = execute_graphql_query(full_query, intent=f"PR詳細取得 (バッチ{batch_num}: {len(batch)}リポジトリ)")

        # Extract PR data from response
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_data = data.get("data", {}).get(alias, {})

            if repo_data:
                prs = repo_data.get("pullRequests", {}).get("nodes", [])
                repo_name = repo_data.get("name", repo["name"])
                owner = repo_data.get("owner", {}).get("login", repo["owner"])

                # Transform GraphQL data to match expected format
                for pr in prs:
                    # Transform reviewRequests
                    review_requests = []
                    for req in pr.get("reviewRequests", {}).get("nodes", []):
                        reviewer = req.get("requestedReviewer", {})
                        login = reviewer.get("login") or reviewer.get("name", "")
                        if login:
                            review_requests.append({"login": login})

                    # Handle null PR author
                    author_data = pr.get("author")
                    if author_data is None:
                        # Deleted account - use placeholder
                        author = {"login": "[deleted]"}
                    else:
                        author = {"login": author_data.get("login", "")}

                    # Extract comment nodes with reactionGroups
                    comment_nodes = pr.get("comments", {}).get("nodes", [])

                    # Extract review threads
                    review_threads = pr.get("reviewThreads", {}).get("nodes", [])

                    # Add repository info to PR
                    pr_with_repo = {
                        "title": pr.get("title", ""),
                        "url": pr.get("url", ""),
                        "isDraft": pr.get("isDraft", False),
                        "createdAt": pr.get("createdAt", ""),
                        "author": author,
                        "reviewRequests": review_requests,
                        "commentNodes": comment_nodes,
                        "reviewThreads": review_threads,
                        "repository": {"name": repo_name, "owner": owner},
                    }
                    all_prs.append(pr_with_repo)

    return all_prs
