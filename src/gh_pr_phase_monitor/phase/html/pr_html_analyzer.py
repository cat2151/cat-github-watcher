"""
PR HTMLを解析して分析用JSONを生成するモジュール。

HTMLから llm_statuses（started/finished/reviewing）とPRのdraft状態を抽出し、
statusを算出するための元データをJSONに出力する。

このモジュールはHTMLの解析と元データの抽出・保存を担う。
ステータスの判定（PHASE1A〜PHASE3A への分類）は呼び出し側の責務。
"""

import json
import re
from pathlib import Path
from typing import Any, Optional

from .llm_status_extractor import _extract_llm_statuses
from ..phase_detector import (
    PHASE_3,
    _is_review_completed_event,
    _is_review_started_event,
    _phase_from_llm_statuses,
    llm_working_from_statuses,
)
from .pr_html_fetcher import _html_to_simple_markdown

# 7種のステータス定数
PHASE1A_DRAFT_LLM_WORKING = "PHASE1A_DRAFT_LLM_WORKING"
PHASE1B_DRAFT_LLM_FINISHED_WORK = "PHASE1B_DRAFT_LLM_FINISHED_WORK"
PHASE1B_LLM_FINISHED_WORK = "PHASE1B_LLM_FINISHED_WORK"  # 非draft: reviewing前でfinished work済み
PHASE1C_REVIEW_IN_PROGRESS = "PHASE1C_REVIEW_IN_PROGRESS"
PHASE2A_REVIEW_COMPLETED = "PHASE2A_REVIEW_COMPLETED"
PHASE2B_LLM_ADDRESSING_FEEDBACK = "PHASE2B_LLM_ADDRESSING_FEEDBACK"
PHASE3A_LLM_FEEDBACK_FINISHED_WORK = "PHASE3A_LLM_FEEDBACK_FINISHED_WORK"

_DRAFT_PATTERNS = [
    re.compile(r"<span[^>]*>\s*Draft\s*</span>", re.IGNORECASE),
    re.compile(r'aria-label="[^"]*Draft[^"]*"', re.IGNORECASE),
    re.compile(r'class="[^"]*State--draft[^"]*"', re.IGNORECASE),
    re.compile(r'data-state="draft"', re.IGNORECASE),
    re.compile(r'data-status="draft"', re.IGNORECASE),
    re.compile(r'"state"\s*:\s*"DRAFT"'),
    re.compile(r"octicon-git-pull-request-draft", re.IGNORECASE),
]


def _is_draft_from_html(html: str) -> bool:
    """HTMLからdraft状態を検出する。"""
    for pattern in _DRAFT_PATTERNS:
        if pattern.search(html):
            return True
    return False


def _is_review_still_in_progress(llm_statuses: list[str]) -> bool:
    """Return True when the last reviewing event is 'started reviewing' without a subsequent completed review.

    This distinguishes between a review that is currently underway ("started reviewing" only)
    and one that has completed ("finished reviewing", a plain "reviewing" event, or "reviewed").
    """
    last_started_review_idx: Optional[int] = None
    last_completed_review_idx: Optional[int] = None

    for idx, status in enumerate(llm_statuses):
        lowered = status.lower()
        if _is_review_started_event(lowered):
            last_started_review_idx = idx
            last_completed_review_idx = None  # A new review cycle begins; previous completion is no longer relevant.
        elif _is_review_completed_event(lowered):
            last_completed_review_idx = idx

    return last_started_review_idx is not None and last_completed_review_idx is None


def _determine_html_status(llm_statuses: list[str], is_draft: bool) -> str:
    """llm_statusesとdraft状態から7種のステータスを決定する。

    コアのphase2/3検出はphase_detectorの_phase_from_llm_statusesに委譲する。
    llm_statusesは時系列順（古い順）で渡すこと。
    """
    # Check for an in-progress review first: "started reviewing" without a subsequent
    # completion event means the review is underway (PHASE1C), not yet done (PHASE2+).
    if _is_review_still_in_progress(llm_statuses):
        return PHASE1C_REVIEW_IN_PROGRESS

    phase = _phase_from_llm_statuses(llm_statuses)

    if phase is None:
        llm_working = llm_working_from_statuses(llm_statuses)
        # 条件1: draftで、started work→finished work が検出された場合、1Bは確定
        if is_draft:
            if llm_working is False:
                return PHASE1B_DRAFT_LLM_FINISHED_WORK
            return PHASE1A_DRAFT_LLM_WORKING
        # 条件2: started reviewingがなく、started work→finished work が検出された場合、1Bは確定
        # （draftでない場合も対象。条件1に続けて明示することで想定ミスを防ぐ安全策とする）
        if llm_working is False:
            return PHASE1B_LLM_FINISHED_WORK
        return PHASE1C_REVIEW_IN_PROGRESS

    if phase == PHASE_3:
        return PHASE3A_LLM_FEEDBACK_FINISHED_WORK

    # phase == PHASE_2: review completed.
    # PHASE2A（未着手）とPHASE2B（対応中）を区別する
    # 最後のcompleted reviewイベント以降にstarted workがあるかで判断する
    last_review_idx: Optional[int] = None
    started_after_review = False
    for idx, status in enumerate(llm_statuses):
        lowered = status.lower()
        if _is_review_started_event(lowered):
            last_review_idx = None  # 新しいreviewサイクル開始: anchorをリセット
            started_after_review = False
        elif _is_review_completed_event(lowered):
            last_review_idx = idx  # review完了: anchorを更新
            started_after_review = False
        if "started work" in lowered and last_review_idx is not None and idx > last_review_idx:
            started_after_review = True

    return PHASE2B_LLM_ADDRESSING_FEEDBACK if started_after_review else PHASE2A_REVIEW_COMPLETED


def analyze_pr_html(html: str, pr_url: str = "") -> dict[str, Any]:
    """PR HTMLを解析してstatusを算出するための元データと判定結果を返す。

    Args:
        html: 解析対象のHTML文字列
        pr_url: PR URL（JSON出力用。省略可）

    Returns:
        {
            "pr_url": str,
            "is_draft": bool,
            "llm_statuses": list[str],  # 時系列順の "started work" / "finished work" / "reviewing" 等
            "status": str,              # PHASE1A〜PHASE3Aのいずれか
        }
    """
    html_markdown = _html_to_simple_markdown(html)
    llm_statuses = _extract_llm_statuses(html, html_markdown)
    is_draft = _is_draft_from_html(html)
    status = _determine_html_status(llm_statuses, is_draft)

    return {
        "pr_url": pr_url,
        "is_draft": is_draft,
        "llm_statuses": llm_statuses,
        "status": status,
    }


def save_analysis_json(analysis: dict[str, Any], html_path: Path) -> Path:
    """分析結果をJSONファイルに保存する。

    JSONファイル名はHTMLファイル名の拡張子を .json に変えたもの。

    Args:
        analysis: analyze_pr_html() の戻り値
        html_path: 対応するHTMLファイルのPath

    Returns:
        保存したJSONファイルのPath
    """
    json_path = html_path.with_suffix(".json")
    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"解析JSON保存完了: {json_path}")
    return json_path
