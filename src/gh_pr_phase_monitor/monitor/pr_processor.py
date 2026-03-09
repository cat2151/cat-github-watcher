"""
PR processing utilities for GitHub PR Phase Monitor
"""

from ..actions.pr_actions import process_pr
from ..phase.html.html_status_processor import fetch_and_analyze_pr_html
from ..phase.phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase
from .error_logger import log_error_to_file


def _process_open_prs(
    all_prs: list,
    phase3_repo_names: list,
    config: dict,
) -> None:
    """HTML取得・phase判定・PR処理を全openなPRに対して実行する。

    all_prs の各PRに対して fetch_and_analyze_pr_html → determine_phase → process_pr を実行し、
    結果を pr["phase"] に書き込み、phase3_repo_names に追記する。
    """
    for pr in all_prs:
        try:
            # HTMLを取得・解析・保存（メインフロー: phaseに関わらず全PRに対して実行）
            try:
                fetch_and_analyze_pr_html(pr)
            except Exception as html_error:
                print(f"    Failed to fetch/analyze HTML for PR: {html_error}")
                log_error_to_file(
                    f"Failed to fetch/analyze HTML for {pr.get('url', 'unknown')}",
                    html_error,
                )

            # pr["llm_statuses"] が更新された後にphaseを判定する
            phase = determine_phase(pr)

            pr["phase"] = phase
            process_pr(pr, config, phase)

            # phase3検知時: 該当リポジトリをpullable検査の対象に登録
            if phase == PHASE_3:
                repo_name = pr.get("repository", {}).get("name", "")
                if repo_name and repo_name not in phase3_repo_names:
                    phase3_repo_names.append(repo_name)
        except Exception as pr_error:
            log_error_to_file(
                f"Failed to process PR {pr.get('url', 'unknown') or pr.get('title', 'unknown')}",
                pr_error,
            )
            pr["phase"] = PHASE_LLM_WORKING
