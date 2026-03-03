#!/usr/bin/env python3
"""
PRのHTMLを取得してローカルに保存するスクリプト（スタンドアロン用ラッパー）。

Usage:
    python fetch_pr_html.py <PR_URL>
    python cat-github-watcher.py --fetch-pr-html <PR_URL>

Example:
    python fetch_pr_html.py https://github.com/cat2151/cat-github-watcher/pull/123

Saves the HTML to: logs/pr/{repo_name}_{pr_number}.html
"""

import sys

from src.gh_pr_phase_monitor.pr_html_saver import fetch_pr_html, parse_pr_url, save_pr_html

__all__ = ["parse_pr_url", "fetch_pr_html", "save_pr_html"]


def main() -> None:
    if len(sys.argv) < 2:
        print(f"使い方: {sys.argv[0]} <PR_URL>", file=sys.stderr)
        print("例: python fetch_pr_html.py https://github.com/owner/repo/pull/123", file=sys.stderr)
        sys.exit(1)

    pr_url = sys.argv[1]
    result = save_pr_html(pr_url)
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
