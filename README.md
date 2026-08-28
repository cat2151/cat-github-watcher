# cat-github-watcher

**Archiving this project**

I am currently not using this. I am now using Claude Code and Codex CLI. What this app once achieved (and what I painstakingly maintained through GitHub and Copilot's frequent specification changes) can now all be accomplished more easily and with higher quality using Claude Code and Codex CLI.

**PR monitoring tool for the GitHub Copilot automatic implementation phase**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

※Most of this document is AI-generated. I generated it by submitting an issue to the agent.

## Current Status
- Currently dogfooding.
- Major bugs have been resolved.
- Frequent breaking changes.
- Notes
  - Initially, I attempted implementation with GitHub Actions, but it proved unsuitable for the purpose of PR monitoring, so I transitioned to a Python version.
  - The Python version monitors repositories owned by the authenticated GitHub user and performs notifications or actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This is a Python tool that monitors the phases of Pull Requests where GitHub Copilot performs automatic implementation, executing appropriate notifications and actions at the right time.
It targets repositories owned by the authenticated GitHub user, efficiently monitoring PRs using the GraphQL API.

## Features

- **Automatic Monitoring of All Repositories**: Automatically monitors PRs in all repositories owned by the authenticated GitHub user.
- **Leveraging GraphQL API**: Achieves fast monitoring with efficient data retrieval.
- **Phase Detection**: Automatically determines PR states (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent at work).
- **Dry-run Mode**: By default, only monitoring is performed, and actual actions (comment posting, marking PR as Ready, sending notifications) are not executed. Can be safely operated by explicit activation.
- **Automated Comment Posting**: Automatically posts appropriate comments based on the phase (requires activation in the configuration file).
- **Multi-agent Support**: Automatically mentions `@codex[agent]` if the PR creator is `openai-code-agent` or other `*-codex-coding-agent` types, `@claude[agent]` if `anthropic-code-agent` or other `*-claude-coding-agent` types, and falls back to `@copilot` if neither applies (can be overridden by `[coding_agent].agent_name`, defaults to @copilot if not set).
- **Automated Draft PR Ready-Up**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2 (requires activation in the configuration file).
- **Mobile Notifications**: Uses ntfy.sh to send mobile notifications when phase3 (awaiting review) is detected (requires activation in the configuration file).
  - Notifies when individual PRs enter phase3.
  - Also notifies when all PRs enter phase3 (message configurable in TOML).
- **Issue List Display**: If all PRs are in "LLM working" state, displays the top N issues (default: 10, changeable via `issue_display_limit`) for repositories without open PRs.
- **Self-Update**: Always checks for updates on startup and displays them. Automatic pull and restart only occur when `enable_auto_update = true`. If `enable_auto_update = false` (default, including unset), it only detects and displays updates without applying them. If true, update checks continue every minute during the monitoring loop. Self-update specific debug logs are displayed only when `enable_auto_update_debug_log = true`.
- **Local Repository Pull Detection**: By default, displays the pullable status of your repositories in the parent directory (Dry-run). Setting `auto_git_pull = true` will automatically `git pull` (refer to [cat-repo-auditor](https://github.com/cat2151/cat-repo-auditor) for reference implementation).
- **Automated `cargo install` Update**: For repositories operated via `cargo install`, setting `cargo_install_repos = ["repo-name"]` will automatically execute `cargo install --force` after a pull is complete, keeping the binary up-to-date.
- **Low-Power Mode**: Feature to automatically extend the monitoring interval when there is no change in status (configurable via `no_change_timeout` and `reduced_frequency_interval`). Disabled by default (since API quota is not consumed with ETag, allowing checks every minute).
- **Verbose Mode**: Displays detailed configuration information on startup and during execution to help detect configuration errors (activate with `verbose`).

## Architecture

This tool is a Python application modularized according to the Single Responsibility Principle (SRP).

### Directory Structure

```
cat-github-watcher/
├── cat-github-watcher.py    # Entry Point
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py         # ANSI Color Codes and Coloring
│       ├── config.py         # Configuration Loading and Parsing
│       ├── github_client.py  # GitHub API Integration
│       ├── phase_detector.py # PR Phase Detection Logic
│       ├── comment_manager.py # Comment Posting and Verification
│       ├── pr_actions.py     # PR Actions (Ready-Up, Browser Launch)
│       └── main.py           # Main Execution Loop
└── tests/                    # Test Files
```

### Phase Detection Logic

The tool determines the following four phases:

1.  **phase1 (Draft)**: The PR is in Draft state and has a review request.
2.  **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3.  **phase3 (Awaiting review)**: `copilot-swe-agent` has completed corrections, and it's awaiting human review.
4.  **LLM working (Coding agent at work)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

-   Python 3.11 or higher installed
-   GitHub CLI (`gh`) installed and authenticated
    ```bash
    gh auth login
    ```

### Setup

1.  Clone this repository:
    ```bash
    git clone https://github.com/cat2151/cat-github-watcher.git
    cd cat-github-watcher
    ```

2.  Create a configuration file (Optional):
    ```bash
    cp config.toml.example config.toml
    ```

3.  Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (Optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # Maximum number of issues to display from repositories without PRs
    # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
    issue_display_limit = 10
    
    # Timeout duration for no state change
    # If the state of all PRs (phase of each PR) does not change for this duration,
    # the monitoring interval switches to low-power mode (reduced_frequency_interval below)
    # Set to an empty string "" to disable (default)
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "" (disabled - ETag allows 304 checks without query consumption every minute)
    no_change_timeout = ""
    
    # Override coding agent mention for comments (defaults to @copilot if omitted)
    [coding_agent]
    agent_name = "@codex[agent]"
    
    # Monitoring interval in low-power mode
    # If no state changes are detected during the no_change_timeout period,
    # the monitoring interval switches to this interval to reduce API usage.
    # It returns to the normal monitoring interval when changes are detected.
    # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
    # Default: "1h" (1 hour)
    reduced_frequency_interval = "1h"
    
    # Verbose mode - displays detailed configuration information
    # When enabled, all settings are displayed on startup, and per-repository settings are shown during execution.
    # Helps detect configuration errors.
    # Default: false
    verbose = false
    
    # Terminal output color scheme
    # Can be set to monokai (default) or classic
    color_scheme = "monokai"

    # Individual color codes can be overridden in the [colors] section (#RRGGBB format/ANSI supported)
    # If omitted, the palette of the above color_scheme is used
    [colors]
    # phase1 = "#E6DB74"
    # phase2 = "#66D9EF"
    # phase3 = "#A6E22E"
    # llm = "#F92672"
    # url = "#79C1FF"
    # url = "\u001b[94m"  # Example ANSI in TOML (ESC=[94m)
    
    # Toggle PR author display
    # Controls whether "Author: <login>" is displayed in CLI output
    # Default: false
    display_pr_author = false
    
    # Local repository auto-pull setting (global flag specifically for the local repository watcher)
    # Default (false): Detects and only displays pullable repositories (Dry-run)
    # If set to true: Automatically `git pull` pullable repositories
    # Scans repositories in the parent directory every 5 minutes (executes git fetch)
    # ※ As this behavior is independent of PR actions, this flag is specified at the top-level only.
    auto_git_pull = false
    
    # Local repository scan target directory (defaults to the parent of the current directory)
    # local_repo_watcher_base_dir = ".."
    
    # Execution control flags for PR actions - can only be specified within [[rulesets]] sections
    # Global flags are no longer supported (except for auto_git_pull)
    # To apply settings to all repositories, use 'repositories = ["all"]'
    
    # Example ruleset configuration:
    # [[rulesets]]
    # name = "Default for all repositories - dry-run mode"
    # repositories = ["all"]  # "all" matches all repositories
    # enable_execution_phase1_to_phase2 = false  # Set to true to make draft PRs ready
    # enable_execution_phase2_to_phase3 = false  # Set to true to post phase2 comments
    # enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
    # enable_execution_phase3_to_merge = false   # Set to true to merge phase3 PRs
    
    # [[rulesets]]
    # name = "Simple: Auto-assign 'good first issue' to Copilot"
    # repositories = ["my-repo"]
    # assign_good_first_old = true  # This is enough! No [assign_to_copilot] section is needed.
    #                               # Default behavior: Open issue in browser for manual assignment.
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR.
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "<Enter your ntfy.sh topic name here>"  # As anyone can read/write to it, please use an unguessable string.
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
    all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs are in phase3
    
    # Phase3 Auto-Merge Settings (optional)
    # Automatically merges the PR once it reaches phase3 (awaiting review).
    # Before merging, the comment defined below will be posted to the PR.
    # After a successful merge, the feature branch will be automatically deleted.
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by setting enable_execution_phase3_to_merge = true in rulesets per repository.
    # IMPORTANT: If auto-merge is enabled, the comment field must be explicitly set.
    [phase3_merge]
    comment = "The agent determines that review comments have been addressed. User review is omitted under the user's responsibility. Merging PR."  # Comment to post before merging (required when auto-merge is enabled)
    automated = false  # Set to true to click the merge button via browser automation
    wait_seconds = 10  # Wait time (seconds) after browser launch and before button click
    debug_dir = "debug_screenshots"  # Debug info save location on image recognition failure (default: "debug_screenshots")
    notification_enabled = true  # Display a small notification window at specified coordinates during automated button operations
    notification_message = "Opening browser and searching for Merge button..."  # Message for the notification window
    notification_width = 400
    notification_height = 150
    notification_position_x = 100
    notification_position_y = 100
    maximize_on_first_fail = true  # Maximize window and re-search if button is not found on the first attempt
    
    # Automated Issue Assignment to Copilot (completely optional! this entire section is optional)
    # 
    # Simple usage: Just set `assign_good_first_old = true` in rulesets (see example above).
    # Define this section only if you wish to customize the default behavior.
    # 
    # Assignment behavior is controlled by ruleset flags:
    # - assign_ci_failure_old: Assign the oldest "ci-failure" issue (by issue number, default: false)
    # - assign_deploy_pages_failure_old: Assign the oldest "deploy-pages-failure" issue (by issue number, default: false)
    # - assign_good_first_old: Assign the oldest "good first issue" (by issue number, default: false)
    # - assign_old: Assign the oldest issue (by issue number, label agnostic, default: false)
    # Priority: ci-failure > deploy-pages-failure > good first issue > old issue
    # 
    # Default behavior (if this section is not defined):
    # - Automatically clicks the button via browser automation
    # - Image recognition using PyAutoGUI
    # - OCR fallback (optional) if image recognition fails
    # - wait_seconds = 2
    # 
    # REQUIRED: PyAutoGUI must be installed (pip install pyautogui pillow)
    # OPTIONAL: pytesseract must be installed for OCR fallback
    # 
    # IMPORTANT: For safety, this feature is disabled by default.
    # You must explicitly enable it by setting assign_ci_failure_old / assign_deploy_pages_failure_old /
    # assign_good_first_old / assign_old in rulesets per repository.
    [assign_to_copilot]
    wait_seconds = 2  # Wait time (seconds) after browser launch and before button click
    debug_dir = "debug_screenshots"  # Debug info save location on image recognition failure (default: "debug_screenshots")
    confidence = 0.8  # Image matching confidence 0.0-1.0 (default: 0.8)
    enable_ocr_detection = true  # Enable OCR fallback (default: true)
    notification_enabled = true  # Display a small notification window at specified coordinates during automated button operations
    notification_message = "Opening browser and searching for Copilot assignment button..."  # Message for the notification window
    notification_width = 400
    notification_height = 150
    notification_position_x = 100
    notification_position_y = 100
    maximize_on_first_fail = true  # Maximize window and re-search if button is not found on the first attempt
    # enable_html_detection = false  # HTML detection fallback (experimental, default: false)
    ```

4.  **Preparing Button Screenshots (Only if using automation)**:

    If you are using automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
    PyAutoGUI requires screenshots of the buttons it will click.

    **Required Screenshots:**

    For automated issue assignment (`assign_to_copilot` feature):
    -   `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button
    -   `assign.png` - Screenshot of the "Assign" button

    For automated PR merge (if `automated = true` in `phase3_merge` feature):
    -   `merge_pull_request.png` - Screenshot of the "Merge pull request" button
    -   `confirm_merge.png` - Screenshot of the "Confirm merge" button
    -   `delete_branch.png` - Screenshot of the "Delete branch" button (Optional)

    **How to take screenshots:**

    a. Open a GitHub issue or PR in your browser.
    b. Locate the button you want to automate.
    c. Take a screenshot of **only the button** (not the whole screen).
    d. Save it as a PNG file in the `screenshots` directory.
    e. Use the exact file names listed above.

    **Tips:**
    -   Screenshots should include only the button with a small margin.
    -   Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
    -   Ensure the button is clearly visible and not obscured.
    -   If the button's appearance changes (e.g., due to theme changes), you'll need to update the screenshots.
    -   Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).

    **Automatic Debug Information Saving:**
    -   If image recognition fails, debug information is automatically saved.
    -   Save location: `debug_screenshots/` directory (default).
    -   Saved content:
        -   Screenshot (of the entire screen at failure): `{button_name}_fail_{timestamp}.png`
        -   Candidate region screenshot (if found): `{button_name}_candidate_{timestamp}_{number}.png`
        -   Failure info JSON: `{button_name}_fail_{timestamp}.json`
            -   Button name, timestamp, confidence threshold, screenshot path, template image path.
            -   Candidate region information (coordinates, size, confidence).
    -   During debugging, up to 3 candidate regions are detected with lower confidence (0.7, 0.6, 0.5).
    -   The debug directory can be changed in settings: `debug_dir` option (within `assign_to_copilot` or `phase3_merge` sections).

    **Fallback Methods (if image recognition fails):**
    -   **OCR Detection (enabled by default)**: Uses pytesseract to detect button text.
        -   Directly detects text like "Assign to Copilot" on the screen.
        -   Robust against sub-pixel rendering differences.
        -   REQUIRED: tesseract-ocr must be installed (system-level).
        -   Disable: `enable_ocr_detection = false`.

    **Key Requirements:**
    -   You must be **already logged in to GitHub** in your default browser.
    -   Automation uses your existing browser session (no new authentication is performed).
    -   Ensure the correct GitHub window/tab is focused and visible on the screen when the button is to be clicked.
    -   If multiple GitHub pages are open, the first button found will be clicked.

    **Create the screenshots directory:**
    ```bash
    mkdir screenshots
    ```

5.  Install PyAutoGUI (Only if using automation):

    For basic image recognition only:
    ```bash
    pip install pyautogui pillow pygetwindow
    ```

    Including OCR fallback (recommended):
    ```bash
    pip install -r requirements-automation.txt
    ```

    If using OCR, install tesseract-ocr on your system:
    -   **Windows**: `choco install tesseract`
    -   **macOS**: `brew install tesseract`
    -   **Linux**: `apt-get install tesseract-ocr`

### Execution

Launch the tool to start monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Operational Flow

1.  **Launch**: Upon launch, the tool starts monitoring repositories owned by the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    -   **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, changes Draft PR to Ready state).
    -   **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, posts a comment requesting Copilot to apply changes).
    -   **phase3**: Opens the PR page in the browser.
        -   If `enable_execution_phase3_send_ntfy = true` in rulesets, also sends an ntfy.sh notification.
        -   If `enable_execution_phase3_to_merge = true` in rulesets, automatically merges the PR (uses global `[phase3_merge]` settings).
    -   **LLM working**: Waits (if all PRs are in this state, displays issues from repositories without open PRs).
5.  **Automated Issue Assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
    -   If `assign_ci_failure_old = true` in rulesets, automatically assigns the oldest "ci-failure" issue (by issue number).
    -   If `assign_deploy_pages_failure_old = true` in rulesets, automatically assigns the oldest "deploy-pages-failure" issue (by issue number).
    -   If `assign_good_first_old = true` in rulesets, automatically assigns the oldest "good first issue" (by issue number).
    -   If `assign_old = true` in rulesets, automatically assigns the oldest issue (by issue number, label agnostic).
    -   Priority: ci-failure > deploy-pages-failure > good first issue > old issue.
    -   Default behavior: Automatically clicks the button via PyAutoGUI (no `[assign_to_copilot]` section is needed).
    -   REQUIRED: PyAutoGUI must be installed and button screenshots must be prepared.
6.  **Repeat**: Continues monitoring at the configured interval.
    -   Monitoring continues every minute by default due to no API quota consumption with ETag.
    -   If `no_change_timeout` is set, the tool automatically switches to low-power mode (`reduced_frequency_interval`) if no state changes are detected for that duration.
    -   It returns to the normal monitoring interval when changes are detected.

### Dry-run Mode

By default, the tool operates in **Dry-run Mode**, performing no actual actions. This allows for safe verification of its operation.

-   **Phase1 (Draft → Ready-Up)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing.
-   **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing.
-   **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing.
-   **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing.
-   **Local Repository**: Displays pullable repositories as `[PULLABLE]` and `[DRY-RUN] Would pull <repo>` but does nothing.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repository"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Mark Draft PR as Ready
enable_execution_phase2_to_phase3 = true  # Post Phase2 comment
enable_execution_phase3_send_ntfy = true  # Send ntfy notification
enable_execution_phase3_to_merge = true   # Merge Phase3 PR
assign_ci_failure_old = true              # Auto-assign ci-failure issue
assign_deploy_pages_failure_old = true    # Auto-assign deploy-pages-failure issue
assign_good_first_old = true              # Auto-assign good first issue
```

To enable automatic local repository pulls, set it at the top-level (outside rulesets):
```toml
auto_git_pull = true  # Automatically `git pull` pullable local repositories
```

To automatically update binaries for repositories managed with `cargo install` after a pull:
```toml
cargo_install_repos = ["voicevox-playground-tui"]  # Executes `cargo install --force` after pull
```

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Caveats

-   GitHub CLI (`gh`) must be installed and authenticated.
-   Assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
-   Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
-   Be mindful of API rate limits as GraphQL API is used.
-   If using ntfy.sh notifications, configure a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

※The English README.md is automatically generated by GitHub Actions using Gemini's translation based on README.ja.md.

*Big Brother is watching your repositories. Now it’s the cat.* 🐱