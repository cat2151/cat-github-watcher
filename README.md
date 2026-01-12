# cat-github-watcher

**PR Monitoring Tool for GitHub Copilot's Automated Implementation Phase**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

*This document is largely AI-generated. It was created by submitting an issue to an agent.*

## Status
- Currently dogfooding.
- Most major bugs have been addressed.
- Breaking changes occur frequently.
- Notes
  - Initially, implementation was attempted with GitHub Actions, but it was found unsuitable for PR monitoring, so we transitioned to a Python version.
  - The Python version monitors user-owned repositories of an authenticated GitHub user and performs notifications and actions based on the PR phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of PRs where GitHub Copilot performs automated implementation, and executes notifications and actions at appropriate times.
It targets user-owned repositories of an authenticated GitHub user, leveraging the GraphQL API for efficient PR monitoring.

## Features

- **Automatic Monitoring of All Repositories**: Automatically monitors PRs in user-owned repositories of an authenticated GitHub user.
- **Leveraging GraphQL API**: Achieves fast monitoring through efficient data retrieval.
- **Phase Detection**: Automatically determines PR status (phase1: Draft state, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent at work).
- **Dry-run Mode**: By default, only monitoring is performed, and actual actions (comment posting, making PR Ready, sending notifications) are not executed. Can be operated safely by explicitly enabling.
- **Automatic Comment Posting**: Automatically posts appropriate comments based on the phase (requires enablement in configuration file).
- **Automatic Readying of Draft PRs**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2 (requires enablement in configuration file).
- **Mobile Notifications**: Uses ntfy.sh to send notifications to mobile devices when phase3 (awaiting review) is detected (requires enablement in configuration file).
  - Notifies when individual PRs enter phase3.
  - Also notifies when all PRs enter phase3 (message configurable in toml).
- **Issue List Display**: Displays the top 10 issues for repositories without open PRs, if all PRs are in "LLM working" state.

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
│       ├── pr_actions.py     # PR actions (making Ready, launching browser)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1.  **phase1 (Draft state)**: PR is in Draft state and has review requests.
2.  **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments and fixes are needed.
3.  **phase3 (Awaiting review)**: `copilot-swe-agent` has completed fixes and is awaiting human review.
4.  **LLM working (Coding agent at work)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

-   Python 3.x is installed.
-   GitHub CLI (`gh`) is installed and authenticated.
    ```bash
    gh auth login
    ```

### Setup

1.  Clone this repository:
    ```bash
    git clone https://github.com/cat2151/cat-github-watcher.git
    cd cat-github-watcher
    ```

2.  Create configuration file (optional):
    ```bash
    cp config.toml.example config.toml
    ```

3.  Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # Execution control flags - can only be specified within [[rulesets]] sections
    # Global flags are no longer supported
    # Use 'repositories = ["all"]' to apply settings to all repositories
    
    # Ruleset configuration example:
    # [[rulesets]]
    # name = "Default for all repositories - dry-run mode"
    # repositories = ["all"]  # "all" matches all repositories
    # enable_execution_phase1_to_phase2 = false  # Set to true to make draft PRs ready
    # enable_execution_phase2_to_phase3 = false  # Set to true to post phase2 comments
    # enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
    # enable_execution_phase3_to_merge = false   # Set to true to merge phase3 PRs
    
    # [[rulesets]]
    # name = "Simple: Automatically assign good first issues to Copilot"
    # repositories = ["my-repo"]
    # assign_good_first_old = true  # This is all you need! [assign_to_copilot] section is not required
    #                               # Default behavior: Opens issue in browser for manual assignment
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "<Enter your ntfy.sh topic name here>"  # Should be an unguessable string, as anyone can read/write to it
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=urgent)
    all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs are in phase3
    
    # Phase3 Automatic Merge Settings (Optional)
    # Automatically merges a PR once it reaches phase3 (awaiting review)
    # Before merging, a comment defined below will be posted to the PR
    # After a successful merge, the feature branch will be automatically deleted
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying enable_execution_phase3_to_merge = true in rulesets for each repository.
    [phase3_merge]
    comment = "All checks passed. Merging PR."  # Comment to post before merging
    automated = false  # Set to true to click the merge button via browser automation
    automation_backend = "selenium"  # Automation backend: "selenium" or "playwright"
    wait_seconds = 10  # Wait time in seconds after browser launch before clicking button
    browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
    headless = false  # Run in headless mode (without displaying a window)
    
    # Automatically assign issues to Copilot (Completely optional! This entire section is optional.)
    # 
    # Simple usage: Just set assign_good_first_old = true in rulesets (see example above).
    # Only define this section if you wish to customize the default behavior.
    # 
    # Assignment behavior is controlled by ruleset flags:
    # - assign_good_first_old: Assign the oldest "good first issue" (by issue number, default: false)
    # - assign_old: Assign the oldest issue (by issue number, any label, default: false)
    # If both are true, "good first issue" takes precedence.
    # 
    # Default behavior (if this section is not defined):
    # - Automatically clicks the button via browser automation
    # - Uses Playwright + Chromium
    # - wait_seconds = 10
    # - headless = false
    # 
    # Required: Selenium or Playwright must be installed.
    # 
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying assign_good_first_old or assign_old in rulesets for each repository.
    [assign_to_copilot]
    automation_backend = "playwright"  # Automation backend: "selenium" or "playwright"
    wait_seconds = 10  # Wait time in seconds after browser launch before clicking button
    browser = "chromium"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
    headless = false  # Run in headless mode (without displaying a window)
    ```

4.  Install Selenium or Playwright for browser automation:
   
    **If using Selenium:**
    ```bash
    pip install -r requirements-automation.txt
    ```
    or
    ```bash
    pip install selenium webdriver-manager
    ```
   
    Browser drivers for use:
    -   **Edge**: Built-in on Windows 10/11 (no additional installation required).
    -   **Chrome**: ChromeDriver will be automatically downloaded.
    -   **Firefox**: GeckoDriver will be automatically downloaded.
   
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

1.  **Startup**: When the tool starts, it begins monitoring user-owned repositories of the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    -   **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PRs are changed to Ready state).
    -   **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, a comment is posted asking Copilot to apply changes).
    -   **phase3**: Opens the PR page in the browser.
        -   If `enable_execution_phase3_send_ntfy = true` in rulesets, also sends ntfy.sh notifications.
        -   If `enable_execution_phase3_to_merge = true` in rulesets, automatically merges the PR (using global `[phase3_merge]` settings).
    -   **LLM working**: Waits (if all PRs are in this state, displays issues for repositories without open PRs).
5.  **Issue Auto-Assignment**: If all PRs are in "LLM working" state and there are repositories without open PRs:
    -   If `assign_good_first_old = true` in rulesets, automatically assigns the oldest "good first issue" (by issue number).
    -   If `assign_old = true` in rulesets, automatically assigns the oldest issue (by issue number, any label).
    -   If both are true, "good first issue" takes precedence.
    -   Default behavior: Automatically clicks the button via browser automation (the `[assign_to_copilot]` section is not required).
    -   Required: Selenium or Playwright must be installed.
6.  **Repetition**: Continues monitoring at the configured interval.

### Dry-run Mode

By default, the tool operates in **Dry-run mode** and does not perform actual actions. This allows you to safely verify its operation.

-   **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing actually.
-   **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing actually.
-   **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing actually.
-   **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing actually.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repository"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Make Draft PRs Ready
enable_execution_phase2_to_phase3 = true  # Post Phase2 comments
enable_execution_phase3_send_ntfy = true  # Send ntfy notifications
enable_execution_phase3_to_merge = true   # Merge Phase3 PRs
assign_good_first_old = true              # Auto-assign good first issues
```

### Stopping the Tool

You can stop monitoring with `Ctrl+C`.

## Important Notes

-   GitHub CLI (`gh`) must be installed and authenticated.
-   This tool assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
-   Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
-   Be mindful of GraphQL API rate limits.
-   If using ntfy.sh notifications, configure a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Tests

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

*The English README.md is automatically generated by GitHub Actions using Gemini's translation based on README.ja.md.*

*Big Brother is watching your repositories. Now it’s the cat. 🐱*