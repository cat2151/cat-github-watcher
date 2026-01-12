# cat-github-watcher

**PR Monitoring Tool for GitHub Copilot's Automated Implementation Phases**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

*Note: This document is largely AI-generated. It was produced by submitting issues to an agent.*

## Status
- Dogfooding in progress.
- Major bugs have been addressed.
- Frequent breaking changes are occurring.
- Notes
  - Initially, implementation was attempted with GitHub Actions, but it was found unsuitable for the purpose of PR monitoring, so it was migrated to a Python version.
  - The Python version monitors repositories owned by authenticated GitHub users and performs notifications and actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of Pull Requests (PRs) where GitHub Copilot performs automated implementation, and executes appropriate notifications and actions at the right time.
It targets repositories owned by authenticated GitHub users and efficiently monitors PRs using the GraphQL API.

## Features

- **Automatic Monitoring of All Repositories**: Automatically monitors PRs in repositories owned by authenticated GitHub users.
- **GraphQL API Utilization**: Achieves fast monitoring through efficient data retrieval.
- **Phase Detection**: Automatically determines the PR's status (phase1: Draft state, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent in progress).
- **Dry-run Mode**: By default, only monitoring is performed, and actual actions (comment posting, making PR Ready, sending notifications) are not executed. Safe operation is possible by explicitly enabling it.
- **Automatic Comment Posting**: Automatically posts appropriate comments based on the phase (requires: enabling in the configuration file).
- **Automatic Draft PR Ready-ing**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2 (requires: enabling in the configuration file).
- **Mobile Notifications**: Uses ntfy.sh to send notifications to mobile devices when phase3 (awaiting review) is detected (requires: enabling in the configuration file).
  - Notifies when an individual PR enters phase3.
  - Also notifies when all PRs enter phase3 (message configurable in TOML).
- **Issue List Display**: If all PRs are "LLM working", displays the top 10 issues from repositories without open PRs.

## Architecture

This tool is a Python application modularized according to the Single Responsibility Principle (SRP).

### Directory Structure

```
cat-github-watcher/
├── cat-github-watcher.py    # Entry point
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py         # ANSI color codes and coloring
│       ├── config.py         # Configuration loading and parsing
│       ├── github_client.py  # GitHub API integration
│       ├── phase_detector.py # PR phase detection logic
│       ├── comment_manager.py # Comment posting and verification
│       ├── pr_actions.py     # PR actions (Ready-ing, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool identifies the following four phases:

1. **phase1 (Draft State)**: When the PR is in Draft state and there is a review request.
2. **phase2 (Addressing Review Comments)**: When `copilot-pull-request-reviewer` has posted review comments and corrections are needed.
3. **phase3 (Awaiting Review)**: When `copilot-swe-agent` has completed corrections and is awaiting human review.
4. **LLM working (Coding Agent in Progress)**: When none of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.x is installed.
- GitHub CLI (`gh`) is installed and authenticated.
  ```bash
  gh auth login
  ```

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/cat2151/cat-github-watcher.git
   cd cat-github-watcher
   ```

2. Create a configuration file (optional):
   ```bash
   cp config.toml.example config.toml
   ```

3. Edit `config.toml` to configure the monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (optional):
   ```toml
   # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
   interval = "1m"
   
   # Execution control flags - only configurable within [[rulesets]] sections
   # Global flags are no longer supported
   # Use 'repositories = ["all"]' to apply settings to all repositories
   
   # Ruleset configuration example:
   # [[rulesets]]
   # name = "Default for all repositories - dry-run mode"
   # repositories = ["all"]  # "all" matches all repositories
   # enable_execution_phase1_to_phase2 = false  # set to true to make draft PRs ready
   # enable_execution_phase2_to_phase3 = false  # set to true to post phase2 comments
   # enable_execution_phase3_send_ntfy = false  # set to true to send ntfy notifications
   # enable_execution_phase3_to_merge = false   # set to true to merge phase3 PRs
   # enable_assign_to_copilot = false           # set to true to enable auto-assign feature (uses global [assign_to_copilot] setting)
   
   # ntfy.sh notification settings (optional)
   # Notifications include clickable action buttons to open the PR
   [ntfy]
   enabled = false  # set to true to enable notifications
   topic = "<Your ntfy.sh topic name here>"  # Anyone can read/write, so use an unguessable string
   message = "PR is ready for review: {url}"  # Message template
   priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
   all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs are in phase3
   
   # Phase3 automatic merge settings (optional)
   # Automatically merges the PR when it reaches phase3 (awaiting review)
   # The comment defined below will be posted to the PR before merging
   # After successful merge, the feature branch will be automatically deleted
   # IMPORTANT: For safety, this feature is disabled by default
   # You must explicitly enable it by setting enable_execution_phase3_to_merge = true in the rulesets for each repository
   [phase3_merge]
   comment = "All checks passed. Merging PR."  # Comment to post before merging
   automated = false  # set to true to click the merge button via browser automation
   automation_backend = "selenium"  # Automation backend: "selenium" or "playwright"
   wait_seconds = 10  # Waiting time in seconds after browser launch and before button click
   browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
   headless = false  # Run in headless mode (no window display)
   
   # Auto-assign "good first issue" issues to Copilot (optional)
   # If enabled, it will open the issue in the browser and prompt you to click the "Assign to Copilot" button
   # If automated = true, it will automatically click the button via browser automation
   # IMPORTANT: For safety, this feature is disabled by default
   # You must explicitly enable it by setting enable_assign_to_copilot = true in the rulesets for each repository
   [assign_to_copilot]
   assign_lowest_number_issue = false  # set to true to assign the issue with the lowest number (regardless of "good first issue" label)
   automated = false  # set to true to enable browser automation (requires: pip install selenium webdriver-manager or playwright)
   automation_backend = "selenium"  # Automation backend: "selenium" or "playwright"
   wait_seconds = 10  # Waiting time in seconds after browser launch and before button click
   browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
   headless = false  # Run in headless mode (no window display)
   ```

4. (Optional) If you plan to use browser automation, install Selenium or Playwright:
   
   **If using Selenium:**
   ```bash
   pip install -r requirements-automation.txt
   ```
   or
   ```bash
   pip install selenium webdriver-manager
   ```
   
   Drivers for the browsers to be used:
   - **Edge**: Standard on Windows 10/11 (no additional installation required)
   - **Chrome**: ChromeDriver will be downloaded automatically
   - **Firefox**: GeckoDriver will be downloaded automatically
   
   **If using Playwright:**
   ```bash
   pip install playwright
   playwright install
   ```
   
   Playwright supports chromium, firefox, and webkit browsers.

### Execution

Start the tool to begin monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Workflow

1. **Startup**: When the tool starts, it begins monitoring repositories owned by the authenticated GitHub user.
2. **PR Detection**: Automatically detects repositories with open PRs.
3. **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4. **Action Execution**:
   - **phase1**: Dry-run by default (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PRs are changed to Ready state).
   - **phase2**: Dry-run by default (if `enable_execution_phase2_to_phase3 = true` in rulesets, a comment is posted requesting Copilot to apply changes).
   - **phase3**: Opens the PR page in the browser.
     - If `enable_execution_phase3_send_ntfy = true` in rulesets, ntfy.sh notifications are also sent.
     - If `enable_execution_phase3_to_merge = true` in rulesets, the PR is automatically merged (uses global `[phase3_merge]` settings).
   - **LLM working**: Waits (if all PRs are in this state, issues from repositories without open PRs are displayed).
5. **Issue Auto-Assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
   - If `enable_assign_to_copilot = true` in rulesets, the auto-assignment feature is enabled (uses global `[assign_to_copilot]` settings).
   - By default, assigns issues with the "good first issue" label.
   - If `assign_lowest_number_issue = true`, assigns the issue with the lowest number (regardless of label).
6. **Repetition**: Continues monitoring at the configured interval.

### Dry-run Mode

By default, the tool operates in **Dry-run mode** and does not execute actual actions, allowing safe verification of its operation.

- **Phase1 (Draft → Ready-ing)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing in practice.
- **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing in practice.
- **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing in practice.
- **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing in practice.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repositories"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Make Draft PRs Ready
enable_execution_phase2_to_phase3 = true  # Post Phase2 comment
enable_execution_phase3_send_ntfy = true  # Send ntfy notification
enable_execution_phase3_to_merge = true   # Merge Phase3 PR
enable_assign_to_copilot = true           # Enable auto-assignment feature (uses global [assign_to_copilot] setting)
```

### Stopping

You can stop monitoring with `Ctrl+C`.

## Important Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- Integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`) is assumed.
- Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
- Be mindful of API rate limits as it uses the GraphQL API.
- If using ntfy.sh notifications, configure a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

*Note: The English README.md is automatically generated by GitHub Actions using Gemini's translation based on README.ja.md.*

*Big Brother is watching your repositories. Now it’s the cat.* 🐱