"""
Tests for html_status_processor - HTMLによるstatus判定機能モードのメイン処理。

fetch_and_analyze_pr_html() が全openなPRに対してphaseに関わらず
HTMLを取得し、1A～3Aのstatusに分類して保存することを確認する。
"""

import pytest

from src.gh_pr_phase_monitor.phase.html.html_status_processor import fetch_and_analyze_pr_html
from src.gh_pr_phase_monitor.phase.html.pr_html_analyzer import (
    PHASE1A_DRAFT_LLM_WORKING,
    PHASE1B_DRAFT_LLM_FINISHED_WORK,
    PHASE1C_REVIEW_IN_PROGRESS,
    PHASE2A_REVIEW_COMPLETED,
    PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
)


def _make_pr(url="https://github.com/owner/repo/pull/1"):
    return {"url": url, "title": "Test PR"}


def test_fetch_and_analyze_pr_html_returns_none_when_no_url():
    pr = {"title": "No URL PR"}
    result = fetch_and_analyze_pr_html(pr)
    assert result is None


def test_fetch_and_analyze_pr_html_returns_none_when_fetch_fails(mocker):
    pr = _make_pr()
    mock_fetch = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor._fetch_pr_html")
    mock_fetch.return_value = None
    result = fetch_and_analyze_pr_html(pr)
    assert result is None
    mock_fetch.assert_called_once_with(pr["url"])


def test_fetch_and_analyze_pr_html_saves_html_and_updates_pr(mocker):
    """HTML取得成功時: HTML+JSONを保存し、pr["llm_statuses"]とpr["html_status"]を更新する。"""
    pr = _make_pr()
    mock_html = "<html><body>PR content</body></html>"
    mock_analysis = {
        "pr_url": pr["url"],
        "is_draft": False,
        "llm_statuses": ["Copilot started reviewing"],
        "status": PHASE2A_REVIEW_COMPLETED,
    }

    mock_fetch = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor._fetch_pr_html")
    mock_analyze = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.analyze_pr_html")
    mock_save = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.save_html_to_logs")
    mock_fetch.return_value = mock_html
    mock_analyze.return_value = mock_analysis

    result = fetch_and_analyze_pr_html(pr)

    # HTML+JSON保存が呼ばれること
    mock_save.assert_called_once_with(mock_html, pr["url"], analysis=mock_analysis)

    # pr辞書が更新されること
    assert pr["llm_statuses"] == ["Copilot started reviewing"]
    assert pr["html_status"] == PHASE2A_REVIEW_COMPLETED

    # 解析結果が返されること
    assert result == mock_analysis


def test_fetch_and_analyze_pr_html_called_for_all_phases(mocker):
    """phaseに関わらず（phase1, phase2, phase3, LLM working）HTMLが取得・保存されること。"""
    for pr_url in [
        "https://github.com/owner/repo/pull/1",
        "https://github.com/owner/repo/pull/2",
        "https://github.com/owner/repo/pull/3",
    ]:
        pr = _make_pr(url=pr_url)
        mock_html = "<html><body>content</body></html>"
        mock_analysis = {
            "pr_url": pr_url,
            "is_draft": False,
            "llm_statuses": [],
            "status": PHASE1C_REVIEW_IN_PROGRESS,
        }

        mock_fetch = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor._fetch_pr_html")
        mock_analyze = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.analyze_pr_html")
        mock_save = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.save_html_to_logs")
        mock_fetch.return_value = mock_html
        mock_analyze.return_value = mock_analysis

        result = fetch_and_analyze_pr_html(pr)

        assert result is not None
        mock_fetch.assert_called_once_with(pr_url)
        mock_save.assert_called_once()
        assert pr.get("html_status") == PHASE1C_REVIEW_IN_PROGRESS


def test_fetch_and_analyze_pr_html_updates_llm_statuses_for_phase_detection(mocker):
    """HTML解析後にpr["llm_statuses"]が更新されるため、determine_phase()が正しく動作すること。"""
    from src.gh_pr_phase_monitor.phase.phase_detector import determine_phase

    pr = {
        "url": "https://github.com/owner/repo/pull/42",
        "title": "Phase3 PR",
        "isDraft": False,
        "reviews": [],
        "latestReviews": [],
        "reviewRequests": [],
        "commentNodes": [],
        "reviewThreads": [],
    }

    # HTML解析後のllm_statusesでphase3が検出されること
    statuses_for_phase3 = ["Copilot started reviewing", "Copilot started work", "Copilot finished work"]
    mock_analysis = {
        "pr_url": pr["url"],
        "is_draft": False,
        "llm_statuses": statuses_for_phase3,
        "status": PHASE3A_LLM_FEEDBACK_FINISHED_WORK,
    }

    mock_fetch = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor._fetch_pr_html")
    mock_analyze = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.analyze_pr_html")
    mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.save_html_to_logs")
    mock_fetch.return_value = "<html><body>PR content</body></html>"
    mock_analyze.return_value = mock_analysis

    fetch_and_analyze_pr_html(pr)

    # llm_statusesが更新されたのでphase3が検出されること
    from src.gh_pr_phase_monitor.phase.phase_detector import PHASE_3
    assert pr["llm_statuses"] == statuses_for_phase3
    assert determine_phase(pr) == PHASE_3


def test_fetch_and_analyze_pr_html_updates_pr_title_from_html(mocker):
    """HTML取得成功時: analysisにtitleが含まれる場合、pr["title"]を更新する。"""
    pr = {"url": "https://github.com/owner/repo/pull/1", "title": "WIP: old title"}
    mock_html = "<html><body>PR content</body></html>"
    mock_analysis = {
        "pr_url": pr["url"],
        "is_draft": False,
        "llm_statuses": [],
        "status": "PHASE1C_REVIEW_IN_PROGRESS",
        "title": "New title without WIP",
    }

    mock_fetch = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor._fetch_pr_html")
    mock_analyze = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.analyze_pr_html")
    mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.save_html_to_logs")
    mock_fetch.return_value = mock_html
    mock_analyze.return_value = mock_analysis

    fetch_and_analyze_pr_html(pr)

    # pr["title"]がHTMLから取得した最新タイトルで更新されること
    assert pr["title"] == "New title without WIP"


def test_fetch_and_analyze_pr_html_does_not_update_title_when_not_in_analysis(mocker):
    """HTML取得成功時: analysisにtitleが含まれない場合、pr["title"]は変更しない。"""
    pr = {"url": "https://github.com/owner/repo/pull/1", "title": "Original title"}
    mock_html = "<html><body>PR content</body></html>"
    mock_analysis = {
        "pr_url": pr["url"],
        "is_draft": False,
        "llm_statuses": [],
        "status": "PHASE1C_REVIEW_IN_PROGRESS",
        # "title" key absent - title extraction failed
    }

    mock_fetch = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor._fetch_pr_html")
    mock_analyze = mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.analyze_pr_html")
    mocker.patch("src.gh_pr_phase_monitor.phase.html.html_status_processor.save_html_to_logs")
    mock_fetch.return_value = mock_html
    mock_analyze.return_value = mock_analysis

    fetch_and_analyze_pr_html(pr)

    # titleがanalysisにない場合、pr["title"]は変更されないこと
    assert pr["title"] == "Original title"
