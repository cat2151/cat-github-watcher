"""
Test to verify that the application exits when PR state does not change for too long
"""

import time

from src.gh_pr_phase_monitor.monitor import state_tracker
from src.gh_pr_phase_monitor.monitor.monitor import check_no_state_change_timeout
from src.gh_pr_phase_monitor.phase.phase_detector import PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING


class TestNoChangeTimeout:
    """Test the check_no_state_change_timeout function"""

    def setup_method(self):
        """Reset global state before each test"""
        state_tracker.set_last_state(None)
        state_tracker.set_reduced_frequency_mode(False)

    def test_default_timeout_when_config_not_set(self):
        """Test that no_change_timeout is disabled by default when not configured.

        ETag-based checks consume no API quota (304 Not Modified responses),
        so the reduced-frequency mode is disabled by default to avoid unexpected
        long waits that hurt UX.
        """
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
        ]
        config = {}

        # Feature is disabled by default (empty-string timeout), so state stays None
        result = check_no_state_change_timeout(all_prs, config)

        assert result is False
        assert state_tracker.get_last_state() is None

    def test_no_timeout_when_config_is_empty_string(self):
        """Test that no timeout occurs when no_change_timeout is empty string"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
        ]
        config = {"no_change_timeout": ""}

        # Should not exit
        check_no_state_change_timeout(all_prs, config)

        # State should remain None when disabled
        assert state_tracker.get_last_state() is None

    def test_timeout_when_state_unchanged(self):
        """Test that monitoring switches to reduced frequency mode when state does not change for timeout duration"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
        ]
        config = {"no_change_timeout": "1s"}  # Very short timeout for testing

        # First call: initialize the state
        result = check_no_state_change_timeout(all_prs, config)
        assert result is False  # Not in reduced frequency mode yet

        # Wait for timeout to elapse
        time.sleep(1.5)

        # Second call with same state: should switch to reduced frequency mode
        result = check_no_state_change_timeout(all_prs, config)
        assert result is True  # Now in reduced frequency mode

    def test_timer_reset_when_phase_changes(self):
        """Test that timer resets when any PR phase changes"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
        ]
        config = {"no_change_timeout": "2s"}

        # First call: start with phase3 and phase2
        check_no_state_change_timeout(all_prs, config)

        # Wait for some time but not full timeout
        time.sleep(1)

        # Second call: change phase of one PR, should reset timer
        all_prs[1]["phase"] = PHASE_3
        check_no_state_change_timeout(all_prs, config)

        # Wait less than timeout
        time.sleep(1)

        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, config)

    def test_timer_reset_when_pr_added(self):
        """Test that timer resets when a PR is added"""
        config = {"no_change_timeout": "2s"}

        # First call: two PRs
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
        ]
        check_no_state_change_timeout(all_prs, config)

        # Wait for some time but not full timeout
        time.sleep(1)

        # Second call: add a new PR, should reset timer
        all_prs.append(
            {
                "title": "PR 3",
                "url": "https://github.com/owner/repo1/pulls/3",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_1,
            }
        )
        check_no_state_change_timeout(all_prs, config)

        # Wait less than timeout
        time.sleep(1)

        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, config)

    def test_timer_reset_when_pr_removed(self):
        """Test that timer resets when a PR is removed"""
        config = {"no_change_timeout": "2s"}

        # First call: three PRs
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
            {
                "title": "PR 3",
                "url": "https://github.com/owner/repo1/pulls/3",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_1,
            },
        ]
        check_no_state_change_timeout(all_prs, config)

        # Wait for some time but not full timeout
        time.sleep(1)

        # Second call: remove a PR, should reset timer
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
        ]
        check_no_state_change_timeout(all_prs, config)

        # Wait less than timeout
        time.sleep(1)

        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, config)

    def test_invalid_timeout_format(self, mocker):
        """Test that invalid timeout format is handled gracefully"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
        ]
        config = {"no_change_timeout": "invalid"}

        # Should print warning and not exit
        mock_print = mocker.patch("builtins.print")
        check_no_state_change_timeout(all_prs, config)

        # Check that warning was printed
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Warning" in str(call) and "invalid" in str(call).lower() for call in calls)

    def test_empty_pr_list(self):
        """Test that empty PR list doesn't cause issues"""
        all_prs = []
        config = {"no_change_timeout": "30m"}

        # Should not exit
        check_no_state_change_timeout(all_prs, config)

    def test_timeout_message_in_japanese(self, mocker):
        """Test that mode switch message is displayed in Japanese"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
        ]
        config = {"no_change_timeout": "1s"}

        # First call: initialize the state
        check_no_state_change_timeout(all_prs, config)

        # Wait for timeout to elapse
        time.sleep(1.5)

        # Second call: should switch to reduced frequency mode with Japanese message
        mock_print = mocker.patch("builtins.print")
        result = check_no_state_change_timeout(all_prs, config)
        assert result is True

        # Check that Japanese message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "変化がない" in output
        assert "API利用の浪費を防止" in output
        assert "監視間隔を" in output  # Check for the interval change message without hardcoding the interval

    def test_prs_without_phase_key(self):
        """Test that PRs without a 'phase' key are handled gracefully (phase defaults to PHASE_LLM_WORKING)"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                # no "phase" key - will default to PHASE_LLM_WORKING
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                # no "phase" key - will default to PHASE_LLM_WORKING
            },
        ]
        config = {"no_change_timeout": "1s"}

        # Should not exit or crash, just handle gracefully
        check_no_state_change_timeout(all_prs, config)

    def test_same_phases_different_prs_triggers_reset(self):
        """Test that changing PR URLs (even with same phases) resets the timer"""
        config = {"no_change_timeout": "2s"}

        # First call: PR 1 and 2
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 2",
                "url": "https://github.com/owner/repo1/pulls/2",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
        ]
        check_no_state_change_timeout(all_prs, config)

        # Wait for some time but not full timeout
        time.sleep(1)

        # Second call: PR 1 and 3 (different PR, same phases), should reset timer
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
            {
                "title": "PR 3",
                "url": "https://github.com/owner/repo1/pulls/3",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_2,
            },
        ]
        check_no_state_change_timeout(all_prs, config)

        # Wait less than timeout
        time.sleep(1)

        # Should not exit because timer was reset
        check_no_state_change_timeout(all_prs, config)

    def test_no_timeout_with_frequent_phase_changes(self):
        """Test that timeout doesn't occur if state keeps changing"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_1,
            },
        ]
        config = {"no_change_timeout": "2s"}

        # Multiple calls with different phases
        phases_sequence = [PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING, PHASE_2]

        for phase in phases_sequence:
            all_prs[0]["phase"] = phase
            result = check_no_state_change_timeout(all_prs, config)
            assert result is False  # Should never enter reduced frequency mode
            time.sleep(0.5)  # Wait between changes but not enough to timeout

        # Should not have entered reduced frequency mode because state kept changing
        assert True  # If we get here, test passed

    def test_return_to_normal_mode_after_change(self, mocker):
        """Test that monitoring returns to normal mode when changes are detected after timeout"""
        all_prs = [
            {
                "title": "PR 1",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "phase": PHASE_3,
            },
        ]
        config = {"no_change_timeout": "1s"}

        # First call: start with phase3
        result = check_no_state_change_timeout(all_prs, config)
        assert result is False

        # Wait for timeout to elapse
        time.sleep(1.5)

        # Second call: should enter reduced frequency mode
        result = check_no_state_change_timeout(all_prs, config)
        assert result is True

        # Third call: change phase, should return to normal mode
        all_prs[0]["phase"] = PHASE_2
        mock_print = mocker.patch("builtins.print")
        result = check_no_state_change_timeout(all_prs, config)
        assert result is False

        # Check that return-to-normal message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)
        assert "変化を検知" in output
        assert "通常の監視間隔に戻ります" in output
