"""
HTMLによるstatus判定機能モード・メイン処理。

全openなPRに対してHTMLを取得し、1A～3Aのstatusに分類し、
HTML+JSONをlogs/prに保存する。
"""

from typing import Any, Dict, Optional

from .pr_html_fetcher import _fetch_pr_html
from .pr_html_analyzer import analyze_pr_html
from .pr_html_saver import save_html_to_logs


def fetch_and_analyze_pr_html(pr: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """PR HTMLを取得・解析し、logs/prに保存する（メインフロー）。

    全てのopenなPRに対して呼ばれる。phaseに関わらず必ずHTMLを取得し、
    1A～3Aのstatusに分類してlogs/prに保存する。

    pr["llm_statuses"] と pr["html_status"] を更新するため、
    呼び出し後に determine_phase(pr) を実行すると最新のstatusが反映される。

    Args:
        pr: PR データ辞書。llm_statuses と html_status を更新する。

    Returns:
        analyze_pr_html() の結果dict（pr_url, is_draft, llm_statuses, status）。
        HTML取得失敗時は None。
    """
    pr_url = pr.get("url", "")
    if not pr_url:
        return None

    html = _fetch_pr_html(pr_url)
    if not html:
        return None

    analysis = analyze_pr_html(html, pr_url)

    # HTML+JSONをlogs/pr/に保存（phaseに関わらず常に保存）
    save_html_to_logs(html, pr_url, analysis=analysis)

    # phase判定・表示用にpr辞書を更新
    pr["llm_statuses"] = analysis.get("llm_statuses", [])
    pr["html_status"] = analysis.get("status", "")
    pr["has_implement_suggestions_button"] = analysis.get("has_implement_suggestions_button", False)

    return analysis
