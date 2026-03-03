"""
PRのHTMLを取得してlogs/pr/ディレクトリに保存するユーティリティ。
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

DEFAULT_OUTPUT_DIR = Path("logs/pr")


def parse_pr_url(url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """GitHub PR URLからowner、リポジトリ名、PR番号を抽出する。

    Args:
        url: GitHub PR URL (例: https://github.com/owner/repo/pull/123)

    Returns:
        (owner, repo_name, pr_number) のタプル。パース失敗時は (None, None, None)
    """
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not match:
        return None, None, None
    return match.group(1), match.group(2), match.group(3)


def fetch_pr_html(pr_url: str) -> Optional[str]:
    """PR HTMLページをcurlで取得する。gh auth tokenで認証を試みる。

    Args:
        pr_url: 取得対象のPR URL

    Returns:
        HTML文字列。取得失敗時はNone
    """
    try:
        token_result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        cmd = ["curl", "-L", "-s", "-w", "\n%{http_code}", pr_url]
        if token_result.returncode == 0 and token_result.stdout.strip():
            token = token_result.stdout.strip()
            cmd = [
                "curl",
                "-L",
                "-s",
                "-w",
                "\n%{http_code}",
                "-H",
                f"Authorization: token {token}",
                pr_url,
            ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            parts = result.stdout.rsplit("\n", 1)
            body = parts[0]
            http_code = parts[1].strip() if len(parts) > 1 else ""
            if body and http_code.startswith("2"):
                return body
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        pass
    return None


def save_pr_html(pr_url: str, output_dir: Path = DEFAULT_OUTPUT_DIR) -> Optional[Path]:
    """PR HTMLを取得してlogs/pr/{repo_name}_{pr_number}.htmlに保存する。

    Args:
        pr_url: 取得対象のPR URL
        output_dir: 保存先ディレクトリ（デフォルト: logs/pr）

    Returns:
        保存したファイルのPath。失敗時はNone
    """
    owner, repo_name, pr_number = parse_pr_url(pr_url)
    if not owner or not repo_name or not pr_number:
        print(f"エラー: 無効なPR URL: {pr_url}", file=sys.stderr)
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{repo_name}_{pr_number}.html"

    print(f"{owner}/{repo_name} PR#{pr_number} のHTMLを取得中...")
    html = fetch_pr_html(pr_url)

    if html is None:
        print(f"エラー: HTMLの取得に失敗しました: {pr_url}", file=sys.stderr)
        return None

    output_file.write_text(html, encoding="utf-8")
    print(f"保存完了: {output_file}")
    return output_file
