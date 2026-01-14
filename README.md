# cat-github-watcher

**PR Monitoring Tool for GitHub Copilot's Automated Implementation Phase**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

※A significant portion of this document is AI-generated. It was produced by submitting issues to an agent.

## Status
- Currently in dogfooding.
- Major bugs have been addressed.
- Frequent breaking changes.
- Notes
  - Initially, we attempted implementation with GitHub Actions, but it proved unsuitable for PR monitoring, leading to a migration to the Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of Pull Requests where GitHub Copilot performs automated implementation and executes appropriate notifications and actions at the right time.
It efficiently monitors PRs using the GraphQL API, targeting user-owned repositories of authenticated GitHub users.

## Features

- **Automatic monitoring of all repositories**: Automatically monitors PRs in user-owned repositories for authenticated GitHub users.
- **GraphQL API utilization**: Achieves high-speed monitoring through efficient data retrieval.
- **Phase detection**: Automatically determines the PR's state (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent in progress).
- **Dry-run mode**: By default, only monitors and does not perform actual actions (commenting, making PR ready, sending notifications). Can be safely operated by explicit enablement.
- **Automatic comment posting**: Automatically posts appropriate comments based on the phase (requires enablement in configuration file).
- **Automatic Draft PR readiness**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2 (requires enablement in configuration file).
- **Mobile notifications**: Uses ntfy.sh to send notifications to mobile devices when phase3 (awaiting review) is detected (requires enablement in configuration file).
  - Notifies when individual PRs enter phase3.
  - Also notifies when all PRs enter phase3 (message configurable in TOML).
- **Issue list display**: If all PRs are "LLM working", displays the top N issues (default: 10, changeable with `issue_display_limit`) for repositories without open PRs.
- **Power-saving mode**: Automatically extends the monitoring interval to reduce API usage when no state changes occur (configurable with `no_change_timeout` and `reduced_frequency_interval`).
- **Verbose mode**: Displays detailed configuration information at startup and during execution to help detect misconfigurations (enable with `verbose`).

## Architecture

This tool is a modularized Python application adhering to the Single Responsibility Principle (SRP).

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
│       ├── pr_actions.py     # PR actions (Ready state, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1.  **phase1 (Draft state)**: PR is in Draft state and has review requests.
2.  **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3.  **phase3 (Awaiting review)**: `copilot-swe-agent` has completed corrections, and it's awaiting human review.
4.  **LLM working (Coding agent in progress)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.x is installed
- GitHub CLI (`gh`) is installed and authenticated
  ```bash
  gh auth login
  ```

### Setup

1.  Clone this repository:
    ```bash
    git clone https://github.com/cat2151/cat-github-watcher.git
    cd cat-github-watcher
    ```

2.  Create a configuration file (optional):
    ```bash
    cp config.toml.example config.toml
    ```

3.  Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot automatic assignment, and automatic merge (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # Maximum number of issues to display from repositories without PRs
    # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
    issue_display_limit = 10
    
    # Timeout for no state change
    # If the state of all PRs (the phase of each PR) does not change for this duration,
    # the monitoring interval will switch to power-saving mode (reduced_frequency_interval below).
    # Set to an empty string "" to disable.
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "30m" (30 minutes - stability priority)
    no_change_timeout = "30m"
    
    # Monitoring interval in power-saving mode
    # If no state changes are detected during the no_change_timeout period,
    # the monitoring interval switches to this interval to reduce API usage.
    # It returns to the normal monitoring interval when a change is detected.
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "1h" (1 hour)
    reduced_frequency_interval = "1h"
    
    # Verbose mode - displays detailed configuration information
    # When enabled, it shows all settings at startup and repository-specific settings during execution.
    # Helps detect configuration errors.
    # Default: false
    verbose = false
    
    # Execution control flags - can only be specified within the [[rulesets]] section
    # Global flags are no longer supported
    # Use 'repositories = ["all"]' to apply settings to all repositories
    
    # Example ruleset configuration:
    # [[rulesets]]
    # name = "Default for all repositories - dry-run mode"
    # repositories = ["all"]  # "all" matches all repositories
    # enable_execution_phase1_to_phase2 = false  # set to true to make draft PRs ready
    # enable_execution_phase2_to_phase3 = false  # set to true to post phase2 comments
    # enable_execution_phase3_send_ntfy = false  # set to true to send ntfy notifications
    # enable_execution_phase3_to_merge = false   # set to true to merge phase3 PRs
    
    # [[rulesets]]
    # name = "Simple: Auto-assign good first issues to Copilot"
    # repositories = ["my-repo"]
    # assign_good_first_old = true  # This is enough! The [assign_to_copilot] section is not needed.
    #                               # Default behavior: Opens issue in browser for manual assignment.
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR.
    [ntfy]
    enabled = false  # set to true to enable notifications
    topic = "<write your ntfy.sh topic name here>"  # Use an unguessable string as anyone can read/write
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
    all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs are in phase3
    
    # Phase3 auto-merge settings (optional)
    # Automatically merges the PR once it reaches phase3 (awaiting review).
    # Before merging, the comment defined below will be posted to the PR.
    # After a successful merge, the feature branch will be automatically deleted.
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying enable_execution_phase3_to_merge = true in rulesets per repository.
    [phase3_merge]
    comment = "All checks passed. Merging PR."  # Comment to post before merging
    automated = false  # set to true to automatically click merge button via browser automation
    automation_backend = "selenium"  # Automation backend: "selenium" or "playwright"
    wait_seconds = 10  # Wait time (seconds) after browser launch before clicking the button
    browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
    headless = false  # Run in headless mode (do not display browser window)
    debug_dir = "debug_screenshots"  # Directory to save debug info on image recognition failure (default: "debug_screenshots")
    
    # Auto-assign issue to Copilot (completely optional! This entire section is optional)
    #
    # Simple usage: Just set assign_good_first_old = true in rulesets (see example above)
    # Define this section ONLY if you want to customize the default behavior.
    #
    # Assignment behavior is controlled by ruleset flags:
    # - assign_good_first_old: Assigns the oldest "good first issue" (by issue number, default: false)
    # - assign_old: Assigns the oldest issue (by issue number, regardless of label, default: false)
    # If both are true, "good first issue" takes precedence.
    #
    # Default behavior (if this section is not defined):
    # - Automatically clicks the button via browser automation
    # - Uses Playwright + Chromium
    # - wait_seconds = 10
    # - headless = false
    #
    # REQUIRED: Selenium or Playwright must be installed
    #
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying assign_good_first_old or assign_old in rulesets per repository.
    [assign_to_copilot]
    automation_backend = "playwright"  # Automation backend: "selenium" or "playwright"
    wait_seconds = 10  # Wait time (seconds) after browser launch before clicking the button
    browser = "chromium"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
    headless = false  # Run in headless mode (do not display browser window)
    debug_dir = "debug_screenshots"  # Directory to save debug info on image recognition failure (default: "debug_screenshots")
    ```

4.  **Prepare Button Screenshots (only if using automation)**:

    If you use automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
    PyAutoGUI requires screenshots of the buttons to click.

    **Required Screenshots:**

    For automatic issue assignment (`assign_to_copilot` feature):
    - `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button
    - `assign.png` - Screenshot of the "Assign" button

    For automatic PR merging (if `automated = true` in `phase3_merge` feature):
    - `merge_pull_request.png` - Screenshot of the "Merge pull request" button
    - `confirm_merge.png` - Screenshot of the "Confirm merge" button
    - `delete_branch.png` - Screenshot of the "Delete branch" button (optional)

    **How to take screenshots:**

    a. Open a GitHub issue or PR in your browser.
    b. Locate the button you want to automate.
    c. Take a screenshot of **only the button** (not the entire screen).
    d. Save it as a PNG file in the `screenshots` directory.
    e. Use the exact filenames listed above.

    **Tips:**
    - Screenshots should include only the button, with a small margin.
    - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
    - Ensure the button is clearly visible and not obscured.
    - If the button's appearance changes (e.g., due to theme changes), you'll need to update the screenshots.
    - If you need to adjust image recognition reliability, use the `confidence` setting (due to DPI scaling or theme).

    **Automatic debug information saving:**
    - If image recognition fails, debug information is automatically saved.
    - Save location: `debug_screenshots/` directory (default).
    - Saved content:
      - Screenshot (entire screen at time of failure): `{button_name}_fail_{timestamp}.png`
      - Failure info JSON: `{button_name}_fail_{timestamp}.json`
        - Button name, timestamp, confidence threshold, screenshot path, template image path.
    - The debug directory can be changed in settings: `debug_dir` option (within `assign_to_copilot` or `phase3_merge` sections).

    **Important Requirements:**
    - You must already be **logged in to GitHub** in your default browser.
    - Automation uses your existing browser session (it does not perform new authentication).
    - Ensure the correct GitHub window/tab is focused and visible on screen when a button click is attempted.
    - If multiple GitHub pages are open, the first found button will be clicked.

    **Create the screenshots directory:**
    ```bash
    mkdir screenshots
    ```

5.  Install PyAutoGUI (only if using automation):
    ```bash
    pip install -r requirements-automation.txt
    ```
    or
    ```bash
    pip install pyautogui pillow
    ```

### Execution

Launch the tool to start monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Workflow

1.  **Startup**: When the tool starts, it begins monitoring user-owned repositories for the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    -   **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PR is changed to Ready state).
    -   **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, posts a comment asking Copilot to apply changes).
    -   **phase3**: Opens the PR page in the browser.
        -   If `enable_execution_phase3_send_ntfy = true` in rulesets, an ntfy.sh notification is also sent.
        -   If `enable_execution_phase3_to_merge = true` in rulesets, the PR is automatically merged (using global `[phase3_merge]` settings).
    -   **LLM working**: Waits (if all PRs are in this state, displays issues from repositories without open PRs).
5.  **Automatic Issue Assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
    -   If `assign_good_first_old = true` in rulesets, automatically assigns the oldest "good first issue" (by issue number).
    -   If `assign_old = true` in rulesets, automatically assigns the oldest issue (by issue number, regardless of label).
    -   If both are true, "good first issue" takes precedence.
    -   Default behavior: Automatically clicks buttons with PyAutoGUI (no `[assign_to_copilot]` section required).
    -   Required: PyAutoGUI installation and button screenshots.
6.  **Repeat**: Continues monitoring at the configured interval.
    -   If no state changes are detected for the duration set by `no_change_timeout`, it automatically switches to power-saving mode (`reduced_frequency_interval`) to reduce API usage.
    -   Returns to the normal monitoring interval when a change is detected.

### Dry-run Mode

By default, the tool operates in **Dry-run mode**, meaning it does not perform actual actions. This allows you to safely verify its behavior.

-   **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing actually.
-   **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing actually.
-   **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing actually.
-   **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing actually.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repository"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Make Draft PR ready
enable_execution_phase2_to_phase3 = true  # Post Phase2 comments
enable_execution_phase3_send_ntfy = true  # Send ntfy notifications
enable_execution_phase3_to_merge = true   # Merge Phase3 PRs
assign_good_first_old = true              # Auto-assign good first issues
```

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Notes

-   GitHub CLI (`gh`) must be installed and authenticated.
-   Assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
-   Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
-   Be mindful of API rate limits as it uses the GraphQL API.
-   If using ntfy.sh notifications, please configure a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details

※The English README.md is automatically generated by GitHub Actions based on README.ja.md using Gemini's translation.

*Big Brother is watching your repositories. Now it’s the cat.* 🐱