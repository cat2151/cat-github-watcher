"""
PRのHTMLを取得してlogs/pr/ディレクトリに保存するユーティリティ。
"""

import re
import sys
from pathlib import Path
from typing import Optional

from .pr_html_analyzer import analyze_pr_html, save_analysis_json
from .pr_html_fetcher import _fetch_pr_html

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
    """PR HTMLページをcurlで取得する（認証なし）。

    実際の取得処理は pr_html_fetcher._fetch_pr_html() に委譲する。

    Args:
        pr_url: 取得対象のPR URL

    Returns:
        HTML文字列。取得失敗時はNone
    """
    return _fetch_pr_html(pr_url)


def save_html_to_logs(html: str, pr_url: str, output_dir: Path = DEFAULT_OUTPUT_DIR) -> Optional[Path]:
    """取得済みHTMLをlogs/pr/{repo_name}_{pr_number}.htmlに保存する（検証用）。

    HTMLの再取得は行わない。引数の html をそのまま保存する。
    保存と同時にHTMLを解析して {repo_name}_{pr_number}.json も出力する。

    Args:
        html: 保存するHTML文字列
        pr_url: PR URL（ファイル名生成・JSON解析に使用）
        output_dir: 保存先ディレクトリ（デフォルト: logs/pr）

    Returns:
        保存したファイルのPath。失敗時はNone
    """
    owner, repo_name, pr_number = parse_pr_url(pr_url)
    if not owner or not repo_name or not pr_number:
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{repo_name}_{pr_number}.html"

    output_file.write_text(html, encoding="utf-8")

    # HTML解析してstatusを算出するための元データJSONを生成・保存
    analysis = analyze_pr_html(html, pr_url)
    save_analysis_json(analysis, output_file)

    return output_file


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

    # HTML解析してstatusを算出するための元データJSONを生成・保存
    analysis = analyze_pr_html(html, pr_url)
    save_analysis_json(analysis, output_file)

    return output_file
