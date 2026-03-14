"""ETag-based repository change detection using GitHub REST API conditional requests.

Uses HTTP If-None-Match headers so that unchanged pages return 304 Not Modified
without consuming GitHub API rate-limit points.
"""

import subprocess
from typing import Dict, Optional, Tuple

# Per-page ETag storage: page_number -> ETag string
_page_etags: Dict[int, str] = {}

# Number of pages in the last complete (non-304) response
_last_page_count: int = 0

# Whether any ETag has been established (first-call tracker)
_initialized: bool = False


def _run_repos_api(page: int, etag: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run gh api --include for a page of /user/repos with an optional If-None-Match header."""
    args = ["gh", "api", "--include", f"/user/repos?per_page=100&page={page}"]
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


def _parse_response(output: str) -> Tuple[bool, Optional[str], bool]:
    """Parse gh api --include output into (is_304, etag, has_next_page).

    Args:
        output: Raw stdout from ``gh api --include``.

    Returns:
        is_304:        True when the server returned 304 Not Modified.
        etag:          The ETag value from response headers, or None if absent.
        has_next_page: True when the Link header contains rel="next".
    """
    lines = output.split("\n")
    if not lines:
        return False, None, False

    # The first line is the HTTP status line, e.g. "HTTP/2 200" or "HTTP/2 304"
    first_line = lines[0].strip()
    if "304" in first_line:
        return True, None, False

    etag: Optional[str] = None
    has_next_page = False
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
                etag = stripped.split(":", 1)[1].strip()
            elif lower.startswith("link:") and 'rel="next"' in stripped:
                has_next_page = True

    return False, etag, has_next_page


def check_repos_etag_changed() -> Optional[bool]:
    """Check whether any repository has changed by using per-page ETags on GET /user/repos.

    Sends ``If-None-Match`` headers (HTTP conditional GET) so that pages whose
    content has not changed return **304 Not Modified**, which does **not** consume
    GitHub API rate-limit points.

    On the first call no ETags are stored yet, so every page returns 200 and the
    ETags are saved as a baseline.

    On subsequent calls:
    - Pages that have not changed return 304 (free, no rate-limit cost).
    - Pages that have changed return 200 with a new ETag.

    Returns:
        None  — first call; baseline ETags stored; treat as possibly changed.
        False — all pages returned 304; nothing changed; GraphQL check can be skipped.
        True  — at least one page returned 200 (or an error occurred); proceed
                with the full updatedAt GraphQL check.
    """
    global _page_etags, _last_page_count, _initialized

    is_first_call = not _initialized
    any_changed = False
    page = 1

    while True:
        etag = _page_etags.get(page)
        result = _run_repos_api(page, etag)
        output = result.stdout or ""

        is_304, new_etag, has_next = _parse_response(output)

        if is_304:
            # This page is unchanged; check the next page only if we know it existed.
            if page >= _last_page_count:
                break
            page += 1
            continue

        # 200 OK (or an unrecognized error response) — treat as changed.
        if new_etag:
            _page_etags[page] = new_etag

        any_changed = True
        _initialized = True

        if not has_next:
            _last_page_count = page
            # Purge stale ETags for pages that no longer exist (e.g. repos were deleted).
            for p in list(_page_etags):
                if p > page:
                    del _page_etags[p]
            break
        page += 1

    if is_first_call:
        return None

    return any_changed


def reset_etag_state() -> None:
    """Reset all ETag state (useful for tests or when monitoring state needs a full refresh)."""
    global _page_etags, _last_page_count, _initialized
    _page_etags.clear()
    _last_page_count = 0
    _initialized = False
