"""
Tests for the hung-session warning logic in display_status_summary().

Covers both warning strategies:
  - createdAt-based fallback (30-minute threshold, no LLM status timestamps available)
  - Latest LLM activity timestamp (1-hour threshold, any status event with a parseable date)
"""

from datetime import datetime, timedelta, timezone

from src.gh_pr_phase_monitor.ui.display import display_status_summary
from src.gh_pr_phase_monitor.phase.phase_detector import PHASE_1, PHASE_LLM_WORKING
from src.gh_pr_phase_monitor.monitor.state_tracker import _pr_state_times


class TestLLMWorkingCreatedAtWarning:
    """Test the warning display for LLM working PRs older than 30 minutes since creation"""

    def setup_method(self):
        """Reset PR state times before each test"""
        _pr_state_times.clear()

    def _make_created_at(self, seconds_ago: float) -> str:
        """Return an ISO 8601 UTC timestamp for a time in the past"""
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_warning_shown_for_llm_working_pr_older_than_30_minutes(self, mocker):
        """Warning should be shown for LLM working PRs created more than 30 minutes ago"""
        all_prs = [
            {
                "title": "Old LLM PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(1801),  # 30 min 1 sec ago
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります" in output
        assert "PRを人力で開いてチェックしてください" in output

    def test_warning_not_shown_for_llm_working_pr_younger_than_30_minutes(self, mocker):
        """Warning should NOT be shown for LLM working PRs created less than 30 minutes ago"""
        all_prs = [
            {
                "title": "New LLM PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(1799),  # 29 min 59 sec ago
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_not_shown_for_non_llm_working_phase(self, mocker):
        """Warning should NOT be shown for PRs not in LLM working phase, even if old"""
        all_prs = [
            {
                "title": "Old Phase1 PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(3600),  # 1 hour ago
                "phase": PHASE_1,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_not_shown_when_created_at_missing(self, mocker):
        """Warning should NOT be shown when createdAt field is absent"""
        all_prs = [
            {
                "title": "No Date PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                # no createdAt field
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって" not in output

    def test_warning_shown_at_exactly_30_minutes(self, mocker):
        """Warning should be shown at exactly 30 minutes (boundary condition)"""
        all_prs = [
            {
                "title": "Boundary PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(1800),  # exactly 30 minutes ago
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(calls)

        assert "バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります" in output


class TestLLMWorkingLatestActivityWarning:
    """Tests for warning logic based on latest LLM session activity timestamp."""

    def setup_method(self):
        _pr_state_times.clear()

    def _make_activity_status(self, label: str, seconds_ago: float) -> str:
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        month_name = dt.strftime("%B")
        return (
            f"Copilot {label} on behalf of cat2151 "
            f"{month_name} {dt.day}, {dt.year} {dt.strftime('%H:%M')}"
        )

    def _make_created_at(self, seconds_ago: float) -> str:
        dt = datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_warning_not_shown_when_activity_is_recent(self, mocker):
        """Warning must NOT appear when latest activity is only 4 minutes ago,
        even if the PR was created more than 24 hours ago."""
        started_status = self._make_activity_status("started work", 240)  # 4 minutes ago
        all_prs = [
            {
                "title": "Long-running PR with recent activity",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(86401),  # > 24 hours ago
                "llm_statuses": [started_status],
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_not_shown_when_reviewing_is_recent(self, mocker):
        """'started reviewing' 4 minutes ago must also suppress the warning."""
        reviewing_status = self._make_activity_status("started reviewing", 240)  # 4 minutes ago
        all_prs = [
            {
                "title": "Long-running PR with recent review activity",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(86401),  # > 24 hours ago
                "llm_statuses": [reviewing_status],
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output
        assert "PRを人力で開いてチェックしてください" not in output

    def test_warning_shown_when_activity_is_over_1_hour_ago(self, mocker):
        """Warning must appear when latest activity was more than 1 hour ago
        (session hang scenario)."""
        started_status = self._make_activity_status("started work", 3601)  # just over 1 hour ago
        all_prs = [
            {
                "title": "Hung session PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(7200),  # 2 hours ago
                "llm_statuses": [started_status],
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります" in output
        assert "PRを人力で開いてチェックしてください" in output

    def test_warning_not_shown_when_activity_is_exactly_below_1_hour(self, mocker):
        """Warning must NOT appear when latest activity is well under 1 hour ago.

        Note: status text stores only hour:minute (no seconds), so a borderline value
        of exactly 3599s could appear as ≥3600s after minute-truncation.  We use 45
        minutes (2700s) to remain safely below the threshold.
        """
        started_status = self._make_activity_status("started work", 2700)  # 45 minutes ago
        all_prs = [
            {
                "title": "Active PR",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(7200),
                "llm_statuses": [started_status],
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output

    def test_latest_activity_takes_precedence_over_created_at(self, mocker):
        """When llm_statuses contain a parseable timestamp, it must be
        used instead of createdAt for the warning decision."""
        # PR is >30 minutes old (would trigger old logic), but latest activity is recent
        started_status = self._make_activity_status("started work", 60)  # 1 minute ago
        all_prs = [
            {
                "title": "Old PR, but recently active",
                "url": "https://github.com/owner/repo1/pulls/1",
                "repository": {"name": "repo1", "owner": "owner"},
                "createdAt": self._make_created_at(3600),  # 1 hour ago
                "llm_statuses": [started_status],
                "phase": PHASE_LLM_WORKING,
            }
        ]
        repos_with_prs = [{"name": "repo1", "owner": "owner", "openPRCount": 1}]

        mock_print = mocker.patch("builtins.print")
        display_status_summary(all_prs, repos_with_prs)

        output = " ".join(str(c) for c in mock_print.call_args_list)
        assert "バグって" not in output
