"""
Test to verify that status summary is displayed correctly before waiting state

This test ensures the new behavior requested in the issue:
"To help users easily understand LLM working information even on terminals with few lines,
display a summary of LLM working status at the end before entering the waiting state"
"""

from unittest.mock import patch

from src.gh_pr_phase_monitor.main import display_status_summary
from src.gh_pr_phase_monitor.phase_detector import PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING


def test_display_status_summary_with_no_prs():
    """
    Test that display_status_summary correctly handles empty PR list
    """
    with patch("builtins.print") as mock_print:
        display_status_summary([], [], [])
        
        # Verify that a "No open PRs" message is displayed
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("No open PRs to monitor" in str(call) for call in calls)


def test_display_status_summary_with_mixed_phases():
    """
    Test that display_status_summary correctly counts and displays PRs by phase
    """
    # Create mock PR data
    all_prs = [
        {"title": "PR 1", "url": "https://github.com/owner/repo/pulls/1"},
        {"title": "PR 2", "url": "https://github.com/owner/repo/pulls/2"},
        {"title": "PR 3", "url": "https://github.com/owner/repo/pulls/3"},
        {"title": "PR 4", "url": "https://github.com/owner/repo/pulls/4"},
        {"title": "PR 5", "url": "https://github.com/owner/repo/pulls/5"},
    ]
    
    # Mixed phases: 1 phase1, 2 phase2, 1 phase3, 1 LLM working
    pr_phases = [PHASE_1, PHASE_2, PHASE_2, PHASE_3, PHASE_LLM_WORKING]
    
    repos_with_prs = [
        {"name": "repo1", "owner": "owner", "openPRCount": 3},
        {"name": "repo2", "owner": "owner", "openPRCount": 2},
    ]
    
    with patch("builtins.print") as mock_print:
        display_status_summary(all_prs, pr_phases, repos_with_prs)
        
        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        
        # Verify that total PR count is displayed
        assert "Total open PRs: 5" in output
        
        # Verify phase counts
        assert "Phase 1 (Draft): 1 PR(s)" in output
        assert "Phase 2 (Addressing review comments): 2 PR(s)" in output
        assert "Phase 3 (Waiting for review): 1 PR(s)" in output
        assert "LLM working: 1 PR(s)" in output
        
        # Verify repository count
        assert "Monitoring 2 repositories" in output


def test_display_status_summary_with_all_llm_working():
    """
    Test that display_status_summary correctly handles all PRs in LLM working state
    """
    # Create mock PR data
    all_prs = [
        {"title": "PR 1", "url": "https://github.com/owner/repo/pulls/1"},
        {"title": "PR 2", "url": "https://github.com/owner/repo/pulls/2"},
    ]
    
    # All PRs are in LLM working state
    pr_phases = [PHASE_LLM_WORKING, PHASE_LLM_WORKING]
    
    repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 2}]
    
    with patch("builtins.print") as mock_print:
        display_status_summary(all_prs, pr_phases, repos_with_prs)
        
        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        
        # Verify that total PR count is displayed
        assert "Total open PRs: 2" in output
        
        # Verify only LLM working is displayed
        assert "LLM working: 2 PR(s)" in output
        
        # Verify other phases are not mentioned
        assert "Phase 1" not in output
        assert "Phase 2" not in output
        assert "Phase 3" not in output


def test_display_status_summary_with_single_phase():
    """
    Test that display_status_summary correctly handles PRs in single phase
    """
    # Create mock PR data
    all_prs = [
        {"title": "PR 1", "url": "https://github.com/owner/repo/pulls/1"},
        {"title": "PR 2", "url": "https://github.com/owner/repo/pulls/2"},
        {"title": "PR 3", "url": "https://github.com/owner/repo/pulls/3"},
    ]
    
    # All PRs are in phase 3
    pr_phases = [PHASE_3, PHASE_3, PHASE_3]
    
    repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 3}]
    
    with patch("builtins.print") as mock_print:
        display_status_summary(all_prs, pr_phases, repos_with_prs)
        
        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        
        # Verify that total PR count is displayed
        assert "Total open PRs: 3" in output
        
        # Verify only phase 3 is displayed
        assert "Phase 3 (Waiting for review): 3 PR(s)" in output
        
        # Verify other phases are not mentioned
        assert "Phase 1" not in output
        assert "Phase 2" not in output
        assert "LLM working:" not in output


def test_display_status_summary_displays_summary_header():
    """
    Test that display_status_summary displays a clear summary header
    """
    all_prs = [{"title": "PR 1", "url": "https://github.com/owner/repo/pulls/1"}]
    pr_phases = [PHASE_1]
    repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]
    
    with patch("builtins.print") as mock_print:
        display_status_summary(all_prs, pr_phases, repos_with_prs)
        
        # Extract all printed messages
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        
        # Verify that "Status Summary" header is displayed
        assert "Status Summary:" in output


if __name__ == "__main__":
    test_display_status_summary_with_no_prs()
    print("✓ Test 1 passed: display_status_summary_with_no_prs")

    test_display_status_summary_with_mixed_phases()
    print("✓ Test 2 passed: display_status_summary_with_mixed_phases")

    test_display_status_summary_with_all_llm_working()
    print("✓ Test 3 passed: display_status_summary_with_all_llm_working")

    test_display_status_summary_with_single_phase()
    print("✓ Test 4 passed: display_status_summary_with_single_phase")

    test_display_status_summary_displays_summary_header()
    print("✓ Test 5 passed: display_status_summary_displays_summary_header")

    print("\n✅ All tests passed!")
