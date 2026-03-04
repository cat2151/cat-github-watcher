# cat-github-watcher

**PR monitoring tool for the automatic implementation phase by GitHub Copilot**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

*This document is largely AI-generated. Issues were submitted to an agent for generation.*

## Status
- Currently dogfooding.
- Major bugs have been addressed.
- Frequent breaking changes are expected.
- Memo
  - Initially, we attempted to implement this with GitHub Actions, but it proved unsuitable for PR monitoring. We then migrated to a Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

A Python tool that monitors the phases of PRs where GitHub Copilot performs automatic implementations, executing notifications and actions at appropriate times.
It efficiently monitors PRs using the GraphQL API, targeting user-owned repositories of authenticated GitHub users.

## Features

- **Automatic monitoring of all repositories**: Automatically monitors PRs in all user-owned repositories for authenticated GitHub users.
- **Leveraging GraphQL API**: Achieves fast monitoring by efficiently fetching data.
- **Phase detection**: Automatically determines the PR's state (phase1: Draft, phase2: Addressing review feedback, phase3: Waiting for review, LLM working: Coding agent in progress).
- **Dry-run mode**: By default, only monitors and does not execute actual actions (posting comments, making PR Ready, sending notifications). Can be safely operated by explicit activation.
- **Automatic comment posting**: Automatically posts appropriate comments based on the phase (requires activation in the configuration file).
- **Multi-agent support**: Automatically mentions `@codex[agent]` if the PR author is `openai-code-agent` or similar `*-codex-coding-agent` types, `@claude[agent]` if it's `anthropic-code-agent` or similar `*-claude-coding-agent` types, and falls back to `@copilot` otherwise (can be overridden with `[coding_agent].agent_name`, defaults to `@copilot` if not set).
- **Automatic readying of Draft PRs**: Automatically changes Draft PRs to a Ready state to address review feedback in phase2 (requires activation in the configuration file).
- **Mobile notifications**: Uses ntfy.sh to send notifications to mobile devices when phase3 (waiting for review) is detected (requires activation in the configuration file).
  - Notifies when an individual PR enters phase3.
  - Also notifies when all PRs enter phase3 (message configurable in TOML).
- **Issue list display**: If all PRs are "LLM working", displays the top N issues (default: 10, changeable via `issue_display_limit`) for repositories without open PRs.
- **Self-update**: If `enable_auto_update = true` is set, detects updates in the GitHub repository every minute and automatically pulls and restarts if the working tree is clean and fast-forwardable (disabled by default).
- **Local repository pull detection**: By default, displays the pullable state of your repositories in the parent directory (Dry-run). Setting `auto_git_pull = true` will automatically `git pull` them (inspired by [cat-repo-auditor](https://github.com/cat2151/cat-repo-auditor)).
- **Power-saving mode**: If no state changes occur, monitoring intervals are automatically extended to reduce API usage (`no_change_timeout` and `reduced_frequency_interval` configurable).
- **Verbose mode**: Displays detailed configuration information on startup and during execution to help detect misconfigurations (enable with `verbose`).

## Architecture

This tool is a modularized Python application adhering to the Single Responsibility Principle (SRP).

### Directory Structure

```
cat-github-watcher/
├── cat-github-watcher.py    # Entry point
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py         # ANSI color codes and styling
│       ├── config.py         # Configuration loading and parsing
│       ├── github_client.py  # GitHub API integration
│       ├── phase_detector.py # PR phase detection logic
│       ├── comment_manager.py # Comment posting and verification
│       ├── pr_actions.py     # PR actions (Readying, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1.  **phase1 (Draft state)**: The PR is in Draft state and has review requests.
2.  **phase2 (Addressing review feedback)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3.  **phase3 (Waiting for review)**: `copilot-swe-agent` has completed corrections, and it's waiting for human review.
4.  **LLM working (Coding agent in progress)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.11 or higher is installed.
- GitHub CLI (`gh`) is installed and authenticated.
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

3.  Edit `config.toml` to configure monitoring intervals, execution mode, ntfy.sh notifications, Copilot auto-assignment, and automatic merging (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # Maximum number of issues to display from repositories without PRs
    # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
    issue_display_limit = 10
    
    # Timeout duration for no state change
    # If the state of all PRs (the phase of each PR) does not change for this duration,
    # the monitoring interval will switch to power-saving mode (reduced_frequency_interval below).
    # Set to an empty string "" to disable.
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "30m" (30 minutes - stability priority)
    no_change_timeout = "30m"
    
    # Overrides the mention for the coding agent used in comments (defaults to @copilot if omitted)
    [coding_agent]
    agent_name = "@codex[agent]"
    
    # Monitoring interval in power-saving mode
    # If no state change is detected during the no_change_timeout period,
    # the monitoring interval switches to this interval to reduce API usage.
    # It reverts to the normal monitoring interval when a change is detected.
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "1h" (1 hour)
    reduced_frequency_interval = "1h"
    
    # Verbose mode - Displays detailed configuration information
    # When enabled, all settings are displayed at startup, and per-repository settings are shown during execution.
    # Helps detect configuration errors.
    # Default: false
    verbose = false
    
    # Color scheme for terminal output
    # Can be set to monokai (default) or classic
    color_scheme = "monokai"

    # Individual color codes can be overridden in the [colors] section (#RRGGBB format / ANSI acceptable)
    # If omitted, the palette of the above color_scheme will be used
    [colors]
    # phase1 = "#E6DB74"
    # phase2 = "#66D9EF"
    # phase3 = "#A6E22E"
    # llm = "#F92672"
    # url = "#79C1FF"
    # url = "\u001b[94m"  # Example ANSI in TOML (ESC=[94m)
    
    # Toggle display of PR author
    # Controls whether "Author: <login>" is displayed in CLI output.
    # Default: false
    display_pr_author = false
    
    # Automatic pull setting for local repositories (global flag exclusive to local repository watcher)
    # Default (false): Detects and only displays pullable repositories (Dry-run)
    # If set to true: Automatically git pulls pullable repositories
    # Scans repositories in the parent directory every 5 minutes (executes git fetch)
    # * This behavior is independent of PR actions, so this flag is specified at the top level only.
    auto_git_pull = false
    
    # Base directory for local repository scanning (defaults to parent of current directory if omitted)
    # local_repo_watcher_base_dir = ".."
    
    # Execution control flags for PR actions - can only be specified within [[rulesets]] sections
    # Global flags are no longer supported (except auto_git_pull)
    # Use 'repositories = ["all"]' to apply settings to all repositories
    
    # Example ruleset configuration:
    # [[rulesets]]
    # name = "Default for all repositories - dry-run mode"
    # repositories = ["all"]  # "all" matches all repositories
    # enable_execution_phase1_to_phase2 = false  # Set to true to ready draft PRs
    # enable_execution_phase2_to_phase3 = false  # Set to true to post phase2 comments
    # enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
    # enable_execution_phase3_to_merge = false   # Set to true to merge phase3 PRs
    
    # [[rulesets]]
    # name = "Simple: Auto-assign good first issues to Copilot"
    # repositories = ["my-repo"]
    # assign_good_first_old = true  # This is enough! The [assign_to_copilot] section is not needed.
    #                               # Default behavior: Opens issue in browser for manual assignment.
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR.
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "<Enter your ntfy.sh topic name here>"  # Make it an unguessable string as anyone can read/write to it
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=min, 3=default, 4=high, 5=max)
    all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs enter phase3
    
    # Phase3 automatic merge settings (optional)
    # Automatically merges the PR when it reaches phase3 (waiting for review).
    # Before merging, the comment defined below will be posted to the PR.
    # After successful merge, the feature branch will be automatically deleted.
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying enable_execution_phase3_to_merge = true in rulesets for each repository.
    # IMPORTANT: If automatic merging is enabled, the comment field must be explicitly set.
    [phase3_merge]
    comment = "The agent determines that review feedback has been addressed. User review is skipped at the user's responsibility. Merging the PR."  # Comment to post before merging (required when auto-merge is enabled)
    automated = false  # Set to true for automated browser operation to click the merge button
    wait_seconds = 10  # Wait time in seconds after browser launch, before clicking the button
    debug_dir = "debug_screenshots"  # Directory to save debug info on image recognition failure (default: "debug_screenshots")
    notification_enabled = true  # Displays a small notification window at specified coordinates during automatic button operation
    notification_message = "Opening browser, searching for Merge button..."  # Message in the notification window
    notification_width = 400
    notification_height = 150
    notification_position_x = 100
    notification_position_y = 100
    maximize_on_first_fail = true  # Maximize window and retry search if button not found on first attempt

    # Auto-assign issues to Copilot (completely optional! This entire section is optional.)
    # 
    # Simple usage: Just set assign_good_first_old = true in rulesets (see example above).
    # Only define this section if you want to customize the default behavior.
    # 
    # Assignment behavior is controlled by ruleset flags:
    # - assign_ci_failure_old: Assigns the oldest "ci-failure" issue (by issue number, default: false)
    # - assign_deploy_pages_failure_old: Assigns the oldest "deploy-pages-failure" issue (by issue number, default: false)
    # - assign_good_first_old: Assigns the oldest "good first issue" (by issue number, default: false)
    # - assign_old: Assigns the oldest issue (by issue number, regardless of label, default: false)
    # Priority: ci-failure > deploy-pages-failure > good first issue > old issue
    # 
    # Default behavior (if this section is not defined):
    # - Automatically clicks buttons via browser automation.
    # - Uses image recognition with PyAutoGUI.
    # - OCR fallback if image recognition fails (optional).
    # - wait_seconds = 2
    # 
    # Required: PyAutoGUI installation (pip install pyautogui pillow)
    # Optional: pytesseract installation for OCR fallback
    # 
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying assign_ci_failure_old / assign_deploy_pages_failure_old /
    # assign_good_first_old / assign_old in rulesets for each repository.
    [assign_to_copilot]
    wait_seconds = 2  # Wait time in seconds after browser launch, before clicking the button
    debug_dir = "debug_screenshots"  # Directory to save debug info on image recognition failure (default: "debug_screenshots")
    confidence = 0.8  # Image matching confidence 0.0-1.0 (default: 0.8)
    enable_ocr_detection = true  # Enable OCR fallback (default: true)
    notification_enabled = true  # Displays a small notification window at specified coordinates during automatic button operation
    notification_message = "Opening browser, searching for Copilot assignment button..."  # Message in the notification window
    notification_width = 400
    notification_height = 150
    notification_position_x = 100
    notification_position_y = 100
    maximize_on_first_fail = true  # Maximize window and retry search if button not found on first attempt
    # enable_html_detection = false  # HTML detection fallback (experimental, default: false)
    ```

4.  **Prepare button screenshots (only if using automation)**:
    
    If you use automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
    PyAutoGUI requires screenshots of the buttons to click.
    
    **Required Screenshots:**
    
    For automatic issue assignment (`assign_to_copilot` feature):
    - `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button.
    - `assign.png` - Screenshot of the "Assign" button.
    
    For automatic PR merging (if `automated = true` in `phase3_merge` feature):
    - `merge_pull_request.png` - Screenshot of the "Merge pull request" button.
    - `confirm_merge.png` - Screenshot of the "Confirm merge" button.
    - `delete_branch.png` - Screenshot of the "Delete branch" button (optional).
    
    **How to take screenshots:**
    
    a. Open a GitHub issue or PR in your browser.
    b. Find the button you want to automate.
    c. Take a screenshot of **only the button** (not the entire screen).
    d. Save it as a PNG file in the `screenshots` directory.
    e. Use the exact filenames listed above.
    
    **Tips:**
    - Screenshots should include only the button, with a small margin.
    - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
    - Ensure the button is clearly visible and not obscured.
    - If the button's appearance changes (e.g., due to theme changes), you'll need to update the screenshots.
    - Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).
    
    **Automatic Debug Information Saving:**
    - If image recognition fails, debug information is automatically saved.
    - Save location: `debug_screenshots/` directory (default).
    - Saved content:
      - Screenshot (entire screen at time of failure): `{button_name}_fail_{timestamp}.png`
      - Candidate region screenshots (if found): `{button_name}_candidate_{timestamp}_{number}.png`
      - Failure info JSON: `{button_name}_fail_{timestamp}.json`
        - Button name, timestamp, confidence threshold, screenshot path, template image path.
        - Candidate region information (coordinates, size, confidence).
    - During debugging, up to 3 candidate regions are detected with lower confidence (0.7, 0.6, 0.5).
    - The debug directory can be changed in settings: `debug_dir` option (within `assign_to_copilot` or `phase3_merge` sections).
    
    **Fallback Methods (if image recognition fails):**
    - **OCR Detection (enabled by default)**: Uses pytesseract to detect button text.
      - Directly detects text like "Assign to Copilot" on the screen.
      - Robust against sub-pixel rendering differences.
      - Required: tesseract-ocr installation (system level).
      - Disable: `enable_ocr_detection = false`
    
    **Important Requirements:**
    - You must already be **logged into GitHub** in your default browser.
    - Automation uses your existing browser session (does not perform new authentication).
    - Ensure the correct GitHub window/tab is focused and visible on screen when clicking buttons.
    - If multiple GitHub pages are open, the first found button will be clicked.
    
    **Create the screenshots directory:**
    ```bash
    mkdir screenshots
    ```

5.  Install PyAutoGUI (only if using automation):
    
    For basic image recognition only:
    ```bash
    pip install pyautogui pillow pygetwindow
    ```
    
    Including OCR fallback (recommended):
    ```bash
    pip install -r requirements-automation.txt
    ```
    
    If using OCR, install tesseract-ocr system-wide:
    - **Windows**: `choco install tesseract`
    - **macOS**: `brew install tesseract`
    - **Linux**: `apt-get install tesseract-ocr`

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

1.  **Startup**: When the tool starts, it begins monitoring user-owned repositories for the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    - **phase1**: Defaults to Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PRs are changed to Ready).
    - **phase2**: Defaults to Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, a comment is posted requesting Copilot to apply changes).
    - **phase3**: Opens the PR page in the browser.
      - If `enable_execution_phase3_send_ntfy = true` in rulesets, an ntfy.sh notification is also sent.
      - If `enable_execution_phase3_to_merge = true` in rulesets, the PR is automatically merged (using global `[phase3_merge]` settings).
    - **LLM working**: Waits (if all PRs are in this state, displays issues from repositories without open PRs).
5.  **Issue Auto-Assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
    - If `assign_ci_failure_old = true` in rulesets, the oldest "ci-failure" issue is auto-assigned (by issue number).
    - If `assign_deploy_pages_failure_old = true` in rulesets, the oldest "deploy-pages-failure" issue is auto-assigned (by issue number).
    - If `assign_good_first_old = true` in rulesets, the oldest "good first issue" is auto-assigned (by issue number).
    - If `assign_old = true` in rulesets, the oldest issue is auto-assigned (by issue number, regardless of label).
    - Priority: ci-failure > deploy-pages-failure > good first issue > old issue
    - Default behavior: PyAutoGUI automatically clicks buttons (the `[assign_to_copilot]` section is not needed).
    - Required: PyAutoGUI installation and button screenshots are necessary.
6.  **Loop**: Continues monitoring at the configured interval.
    - If no state change is detected for the duration set by `no_change_timeout`, it automatically switches to power-saving mode (`reduced_frequency_interval`) to reduce API usage.
    - Returns to the normal monitoring interval when a change is detected.

### Dry-run Mode

By default, the tool operates in **Dry-run mode**, and no actual actions are executed. This allows for safe verification of its operation.

-   **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing.
-   **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing.
-   **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing.
-   **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing.
-   **Local Repository**: Displays `[PULLABLE]` for pullable repositories and `[DRY-RUN] Would pull <repo>` but does nothing.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repository"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Ready Draft PRs
enable_execution_phase2_to_phase3 = true  # Post Phase2 comments
enable_execution_phase3_send_ntfy = true  # Send ntfy notifications
enable_execution_phase3_to_merge = true   # Merge Phase3 PRs
assign_ci_failure_old = true              # Auto-assign ci-failure issues
assign_deploy_pages_failure_old = true    # Auto-assign deploy-pages-failure issues
assign_good_first_old = true              # Auto-assign good first issues
```

To enable automatic pulling for local repositories, configure it at the top level (outside of rulesets):
```toml
auto_git_pull = true  # Automatically git pull pullable local repositories
```

### Stopping

You can stop monitoring with `Ctrl+C`.

## Notes

-   GitHub CLI (`gh`) must be installed and authenticated.
-   Assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
-   Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
-   Be mindful of API rate limits when using the GraphQL API.
-   If using ntfy.sh notifications, configure your topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See LICENSE file for details

*The English README.md is automatically generated from README.ja.md using Gemini's translation via GitHub Actions.*

*Big Brother is watching your repositories. Now it’s the cat.* 🐱