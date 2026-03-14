"""ETag-based issue change detection using GitHub REST API conditional requests.

Uses HTTP If-None-Match headers so that repositories whose open issue list has not
changed return 304 Not Modified without consuming GitHub API rate-limit points.
"""

import subprocess
from typing import Any, Dict, List, Optional, Tuple

# Per-repo ETag storage: "{owner}/{repo}" -> ETag string
_repo_issue_etags: Dict[str, str] = {}


def _run_issues_api(owner: str, repo: str, etag: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run gh api --include for the open issues endpoint of a repository.

    Uses ``sort=updated&direction=desc&per_page=1`` so the response always starts with
    the most-recently-updated open issue.  Any update to any open issue changes this
    response, which causes the ETag to change and the pre-check to return True.
    """
    args = ["gh", "api", "--include",
            f"/repos/{owner}/{repo}/issues?state=open&sort=updated&direction=desc&per_page=1"]
    if etag:
        args.extend(["-H", f"If-None-Match: {etag}"])
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _parse_issue_response(output: str) -> Tuple[bool, Optional[str]]:
    """Parse gh api --include output into (is_304, etag).

    Args:
        output: Raw stdout from ``gh api --include``.

    Returns:
        is_304: True when the server returned 304 Not Modified.
        etag:   The ETag value from response headers, or None if absent.
    """
    lines = output.split("\n")
    if not lines:
        return False, None

    # The first line is the HTTP status line, e.g. "HTTP/2 200" or "HTTP/2 304"
    first_line = lines[0].strip()
    if "304" in first_line:
        return True, None

    found_etag: Optional[str] = None
    in_headers = True

    for line in lines[1:]:
        if in_headers:
            stripped = line.strip()
            if not stripped:
                # Empty line separates HTTP headers from the response body
                in_headers = False
                continue
            lower = stripped.lower()
            if lower.startswith("etag:"):
                found_etag = stripped.split(":", 1)[1].strip()

    return False, found_etag


def check_issues_etag_changed(repos: List[Dict[str, Any]]) -> Optional[bool]:
    """Check whether any repository's issues have changed using per-repo ETags.

    Sends ``If-None-Match`` headers (HTTP conditional GET) so that repositories whose
    open issue list has not changed return **304 Not Modified**, which does **not**
    consume GitHub API rate-limit points.

    On the first call for a repository no ETag is stored yet, so the response returns
    200 and the ETag is saved as a baseline.

    On subsequent calls:
    - Repositories that have not changed return 304 (free, no rate-limit cost).
    - Repositories that have changed return 200 with a new ETag.

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys.

    Returns:
        None  — at least one repo has no stored ETag (first call); baseline established.
        False — all repos returned 304; nothing changed; GraphQL query can be skipped.
        True  — at least one repo returned 200 (or an error occurred); proceed with GraphQL.
    """
    if not repos:
        return False

    any_first_call = False
    any_changed = False
    any_checked = False

    for repo in repos:
        owner = repo.get("owner", "")
        name = repo.get("name", "")
        if not owner or not name:
            continue

        any_checked = True
        key = f"{owner}/{name}"
        stored_etag = _repo_issue_etags.get(key)

        if stored_etag is None:
            any_first_call = True

        result = _run_issues_api(owner, name, stored_etag)
        output = result.stdout or ""

        is_304, new_etag = _parse_issue_response(output)

        if is_304:
            # This repo's issues are unchanged
            continue

        # 200 OK (or an unrecognized error response) — treat as changed.
        if new_etag:
            _repo_issue_etags[key] = new_etag
        any_changed = True

    if not any_checked:
        # No valid repo entries were found; treat as changed to avoid silently skipping GraphQL.
        return True

    if any_first_call:
        return None

    return any_changed


def reset_issue_etag_state() -> None:
    """Reset all issue ETag state (useful for tests or when monitoring state needs a full refresh)."""
    _repo_issue_etags.clear()
