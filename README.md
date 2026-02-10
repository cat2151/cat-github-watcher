# cat-github-watcher

**PR Monitoring Tool for GitHub Copilot's Automatic Implementation Phase**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

*Note: This document is largely AI-generated. Issues were submitted to an agent for generation.*

## Current Status
- Dogfooding in progress.
- Major bugs have been addressed.
- Frequent breaking changes are occurring.
- For your reference:
  - Initially, an implementation via GitHub Actions was attempted, but it was found unsuitable for PR monitoring, leading to a migration to the Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on PR phases.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of GitHub Copilot's automatically implemented Pull Requests (PRs) and performs appropriate notifications and actions at the right time.
It targets user-owned repositories of authenticated GitHub users and leverages the GraphQL API for efficient PR monitoring.

## Features

- **Automatic monitoring of all repositories**: Automatically monitors PRs in all user-owned repositories for authenticated GitHub users.
- **GraphQL API utilization**: Achieves high-speed monitoring through efficient data retrieval.
- **Phase detection**: Automatically determines the PR's state (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent at work).
- **Dry-run mode**: By default, it only monitors and does not execute actual actions (posting comments, making PRs Ready, sending notifications). It can be safely operated by explicitly enabling execution.
- **Automatic comment posting**: Automatically posts appropriate comments based on the phase (requires explicit enablement in the configuration file).
- **Multi-agent support**: Automatically mentions `@codex[agent]` if the PR author is from the `*-codex-coding-agent` family (e.g., `openai-code-agent`), `@claude[agent]` if from the `*-claude-coding-agent` family (e.g., `anthropic-code-agent`), and falls back to `@copilot` otherwise (can be overridden by `[coding_agent].agent_name`; defaults to @copilot if not set).
- **Automatic Draft PR readiness**: Automatically changes Draft PRs to "Ready for review" status for addressing review comments in phase2 (requires explicit enablement in the configuration file).
- **Mobile notifications**: Uses ntfy.sh to send mobile notifications when phase3 (awaiting review) is detected (requires explicit enablement in the configuration file).
  - Notifies when individual PRs reach phase3.
  - Notifies when all PRs reach phase3 (message can be configured in TOML).
- **Issue list display**: If all PRs are "LLM working", displays the top N issues (default: 10, configurable via `issue_display_limit`) for repositories without open PRs.
- **Low-power mode**: If no state changes occur, the monitoring interval is automatically extended to reduce API usage (`no_change_timeout` and `reduced_frequency_interval` are configurable).
- **Verbose mode**: Displays detailed configuration information at startup and during execution to help detect configuration errors (enabled via `verbose`).

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
│       ├── pr_actions.py     # PR actions (make Ready, launch browser)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1.  **phase1 (Draft)**: The PR is in Draft state and has review requests.
2.  **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments, and changes are required.
3.  **phase3 (Awaiting review)**: `copilot-swe-agent` has completed changes and is awaiting human review.
4.  **LLM working (Coding agent at work)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.10 or higher is installed.
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

3.  Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # Maximum number of issues to display from repositories without PRs
    # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
    issue_display_limit = 10
    
    # Timeout duration for no state change
    # If the state of all PRs (phase of each PR) does not change for this duration,
    # the monitoring interval will switch to low-power mode (reduced_frequency_interval below)
    # Set to an empty string "" to disable
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "30m" (30 minutes - prioritizing stability)
    no_change_timeout = "30m"
    
    # Override the coding agent mention used in posted comments (defaults to @copilot if omitted)
    [coding_agent]
    agent_name = "@codex[agent]"
    
    # Monitoring interval in low-power mode
    # If no state changes are detected during the no_change_timeout period,
    # the monitoring interval will switch to this interval to reduce API usage.
    # It will revert to the normal monitoring interval when a change is detected.
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "1h" (1 hour)
    reduced_frequency_interval = "1h"
    
    # Verbose mode - displays detailed configuration information
    # If enabled, it shows all settings at startup and repository-specific settings during execution.
    # Helps detect configuration errors.
    # Default: false
    verbose = false
    
    # Terminal output color scheme
    # Can be set to "monokai" (default) or "classic"
    color_scheme = "monokai"

    # Individual color codes can be overridden in the [colors] section (#RRGGBB or ANSI format)
    # If omitted, the palette of the above color_scheme will be used.
    [colors]
    # phase1 = "#E6DB74"
    # phase2 = "#66D9EF"
    # phase3 = "#A6E22E"
    # llm = "#F92672"
    # url = "#79C1FF"
    # url = "\u001b[94m"  # Example ANSI in TOML (ESC=[94m)
    
    # Toggle PR author display
    # Controls whether "Author: <login>" is displayed in CLI output.
    # Default: false
    display_pr_author = false
    
    # Execution control flags - can only be specified within [[rulesets]] section.
    # Global flags are no longer supported.
    # To apply settings to all repositories, please use 'repositories = ["all"]'.
    
    # Ruleset configuration example:
    # [[rulesets]]
    # name = "Default for all repositories - dry-run mode"
    # repositories = ["all"]  # "all" matches all repositories
    # enable_execution_phase1_to_phase2 = false  # Set to true to convert draft PRs to ready
    # enable_execution_phase2_to_phase3 = false  # Set to true to post phase 2 comments
    # enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
    # enable_execution_phase3_to_merge = false   # Set to true to merge phase 3 PRs
    
    # [[rulesets]]
    # name = "Simple: Auto-assign 'good first issue' to Copilot"
    # repositories = ["my-repo"]
    # assign_good_first_old = true  # This is enough! [assign_to_copilot] section is not needed.
    #                               # Default behavior: Opens issue in browser for manual assignment
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR.
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "<Enter your ntfy.sh topic name here>"  # Anyone can read/write to it, so use an unguessable string.
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
    all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs reach phase3
    
    # Phase 3 auto-merge settings (optional)
    # Automatically merges PRs when they reach phase 3 (awaiting review).
    # Before merging, the comment defined below will be posted to the PR.
    # After successful merge, the feature branch will be automatically deleted.
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying enable_execution_phase3_to_merge = true in rulesets for each repository.
    # IMPORTANT: When auto-merge is enabled, the 'comment' field must be explicitly set.
    [phase3_merge]
    comment = "The agent has determined that review comments have been addressed. The user skips manual review at their own discretion. Merging the PR."  # Comment to post before merging (required when auto-merge is enabled)
    automated = false  # Set to true to click the merge button via browser automation
    wait_seconds = 10  # Wait time (seconds) after browser launch, before clicking the button
    debug_dir = "debug_screenshots"  # Destination for debugging information on image recognition failure (default: "debug_screenshots")
    notification_enabled = true  # Displays a small notification window at specified coordinates during automated button operation
    notification_message = "Opening browser and searching for Merge button..."  # Message for the notification window
    notification_width = 400
    notification_height = 150
    notification_position_x = 100
    notification_position_y = 100
    maximize_on_first_fail = true  # Maximizes the window and retries search if the button is not found on the first attempt.

    # Auto-assign issues to Copilot (completely optional! This entire section is optional)
    # 
    # Simple usage: Just set assign_good_first_old = true in rulesets (see example above).
    # Define this section ONLY if you want to customize the default behavior.
    # 
    # Assignment behavior is controlled by ruleset flags:
    # - assign_ci_failure_old: Assigns the oldest "ci-failure" issue (by issue number, default: false)
    # - assign_deploy_pages_failure_old: Assigns the oldest "deploy-pages-failure" issue (by issue number, default: false)
    # - assign_good_first_old: Assigns the oldest "good first issue" (by issue number, default: false)
    # - assign_old: Assigns the oldest issue (by issue number, label agnostic, default: false)
    # Priority: ci-failure > deploy-pages-failure > good first issue > old issue
    # 
    # Default behavior (if this section is not defined):
    # - Automatically clicks buttons via browser automation.
    # - Uses PyAutoGUI for image recognition.
    # - OCR fallback (optional) if image recognition fails.
    # - wait_seconds = 10
    # 
    # Required: PyAutoGUI installation is necessary (pip install pyautogui pillow)
    # Optional: pytesseract installation is necessary for OCR fallback.
    # 
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by specifying assign_ci_failure_old / assign_deploy_pages_failure_old /
    # assign_good_first_old / assign_old in rulesets for each repository.
    [assign_to_copilot]
    wait_seconds = 10  # Wait time (seconds) after browser launch, before clicking the button
    debug_dir = "debug_screenshots"  # Destination for debugging information on image recognition failure (default: "debug_screenshots")
    confidence = 0.8  # Image matching confidence 0.0-1.0 (default: 0.8)
    enable_ocr_detection = true  # Enable OCR fallback (default: true)
    notification_enabled = true  # Displays a small notification window at specified coordinates during automated button operation
    notification_message = "Opening browser and searching for Copilot assignment button..."  # Message for the notification window
    notification_width = 400
    notification_height = 150
    notification_position_x = 100
    notification_position_y = 100
    maximize_on_first_fail = true  # Maximizes the window and retries search if the button is not found on the first attempt.
    # enable_html_detection = false  # HTML detection fallback (experimental, default: false)
    ```

4.  **Preparing Button Screenshots (only if using automation)**:
   
    If you use automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
    PyAutoGUI requires screenshots of the buttons to click.
    
    **Required screenshots:**
    
    For automatic issue assignment (`assign_to_copilot` feature):
    - `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button
    - `assign.png` - Screenshot of the "Assign" button
    
    For automatic PR merging (`phase3_merge` feature with `automated = true`):
    - `merge_pull_request.png` - Screenshot of the "Merge pull request" button
    - `confirm_merge.png` - Screenshot of the "Confirm merge" button
    - `delete_branch.png` - Screenshot of the "Delete branch" button (optional)
    
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
    - If the button's appearance changes (e.g., theme change), you'll need to update the screenshots.
    - Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).
    
    **Automatic saving of debug information:**
    - If image recognition fails, debug information is automatically saved.
    - Save location: `debug_screenshots/` directory (default).
    - Saved content:
      - Screenshot (entire screen at time of failure): `{button_name}_fail_{timestamp}.png`
      - Candidate region screenshots (if found): `{button_name}_candidate_{timestamp}_{number}.png`
      - Failure info JSON: `{button_name}_fail_{timestamp}.json`
        - Button name, timestamp, confidence threshold, screenshot path, template image path.
        - Candidate region information (coordinates, size, confidence).
    - During debugging, up to 3 candidate regions are detected with low confidence (0.7, 0.6, 0.5).
    - The debug directory can be changed in the settings: `debug_dir` option (within `assign_to_copilot` or `phase3_merge` sections).
    
    **Fallback methods (if image recognition fails):**
    - **OCR detection (enabled by default)**: Uses pytesseract to detect button text.
      - Directly detects text like "Assign to Copilot" on screen.
      - Robust against subpixel rendering differences.
      - Required: tesseract-ocr installation (system level).
      - Disable: `enable_ocr_detection = false`.
    
    **Important requirements:**
    - You must already be **logged into GitHub in your default browser**.
    - Automation uses an existing browser session (it does not perform new authentication).
    - Ensure the correct GitHub window/tab is focused and visible on screen when clicking buttons.
    - If multiple GitHub pages are open, the first button found will be clicked.
    
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
    
    If using OCR, install tesseract-ocr on your system:
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
    -   **phase1**: Defaults to Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, it changes Draft PRs to Ready status).
    -   **phase2**: Defaults to Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, it posts a comment asking Copilot to apply changes).
    -   **phase3**: Opens the PR page in a browser.
        -   If `enable_execution_phase3_send_ntfy = true` in rulesets, it also sends ntfy.sh notifications.
        -   If `enable_execution_phase3_to_merge = true` in rulesets, it automatically merges the PR (using global `[phase3_merge]` settings).
    -   **LLM working**: Waits (if all PRs are in this state, displays issues from repositories without open PRs).
5.  **Automatic Issue Assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
    -   If `assign_ci_failure_old = true` in rulesets, automatically assigns the oldest "ci-failure" issue (by issue number).
    -   If `assign_deploy_pages_failure_old = true` in rulesets, automatically assigns the oldest "deploy-pages-failure" issue (by issue number).
    -   If `assign_good_first_old = true` in rulesets, automatically assigns the oldest "good first issue" (by issue number).
    -   If `assign_old = true` in rulesets, automatically assigns the oldest issue (by issue number, label agnostic).
    -   Priority: ci-failure > deploy-pages-failure > good first issue > old issue.
    -   Default behavior: Automatically clicks buttons via PyAutoGUI (the `[assign_to_copilot]` section is not needed for this basic behavior).
    -   Required: PyAutoGUI installation and preparation of button screenshots are necessary.
6.  **Repeat**: Continues monitoring at the configured interval.
    -   If the state remains unchanged for the duration set by `no_change_timeout`, it automatically switches to low-power mode (`reduced_frequency_interval`) to reduce API usage.
    -   It reverts to the normal monitoring interval when a change is detected.

### Dry-run Mode

By default, the tool operates in **Dry-run mode**, meaning it will not perform actual actions. This allows you to safely verify its operation.

-   **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing actually.
-   **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing actually.
-   **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing actually.
-   **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing actually.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of your `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repository"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Makes Draft PRs ready
enable_execution_phase2_to_phase3 = true  # Posts Phase2 comments
enable_execution_phase3_send_ntfy = true  # Sends ntfy notifications
enable_execution_phase3_to_merge = true   # Merges Phase3 PRs
assign_ci_failure_old = true              # Auto-assigns ci-failure issues
assign_deploy_pages_failure_old = true    # Auto-assigns deploy-pages-failure issues
assign_good_first_old = true              # Auto-assigns good first issues
```

### Stopping

You can stop monitoring with `Ctrl+C`.

## Notes

-   GitHub CLI (`gh`) must be installed and authenticated.
-   It assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
-   **Only user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
-   Be mindful of API rate limits when using the GraphQL API.
-   If using ntfy.sh notifications, please set up a topic on [ntfy.sh](https://ntfy.sh/) in advance.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

*The English `README.md` is automatically generated by GitHub Actions using Gemini's translation based on `README.ja.md`.*

*Big Brother is watching your repositories. Now it’s the cat.* 🐱