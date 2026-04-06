# cat-github-watcher

**PR monitoring tool for the automated implementation phase by GitHub Copilot**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

*Note: This document is largely AI-generated. Issues were submitted to an agent for generation.*

## Status
- Currently dogfooding.
- Major bugs have been addressed.
- Frequent breaking changes.
- Memo
  - Initially, implementation was attempted with GitHub Actions, but it proved unsuitable for PR monitoring, so it was migrated to a Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on the PR phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of Pull Requests where GitHub Copilot performs automated implementation and executes appropriate notifications and actions at the right time.
It targets user-owned repositories of authenticated GitHub users and efficiently monitors PRs using the GraphQL API.

## Features

- **Automated Monitoring of All Repositories**: Automatically monitors PRs in user-owned repositories of authenticated GitHub users.
- **GraphQL API Utilization**: Achieves high-speed monitoring through efficient data retrieval.
- **Phase Detection**: Automatically determines PR status (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent working).
- **Dry-run Mode**: By default, only monitoring is performed, and actual actions (comment posting, marking PR as Ready, sending notifications) are not executed. Can be safely operated by explicit activation.
- **Automated Comment Posting**: Automatically posts appropriate comments based on the phase (requires activation in the configuration file).
- **Multi-agent Support**: Automatically mentions `@codex[agent]` for PR authors like `openai-code-agent` (any `*-codex-coding-agent` type), `@claude[agent]` for `anthropic-code-agent` (any `*-claude-coding-agent` type), and falls back to `@copilot` if none of these match (can be overridden by `[coding_agent].agent_name`, defaults to @copilot if not set).
- **Automatic Draft PR Ready-fication**: Automatically changes Draft PRs to Ready state to address review comments in phase2 (requires activation in the configuration file).
- **Mobile Notifications**: Uses ntfy.sh to send mobile notifications when phase3 (awaiting review) is detected (requires activation in the configuration file).
  - Notifies when individual PRs enter phase3.
  - Also notifies when all PRs enter phase3 (message customizable in toml).
- **Issue List Display**: If all PRs are "LLM working," displays the top N issues (default: 10, changeable via `issue_display_limit`) for repositories without open PRs.
- **Self-update**: Always checks for updates on startup and displays them. Automatic `git pull` and restart occur only when `enable_auto_update = true`. When `enable_auto_update = false` (default, including unset), updates are detected and displayed but not applied. If true, update checks continue every minute during the monitoring loop. Self-update specific debug logs are displayed only when `enable_auto_update_debug_log = true`.
- **Local Repository Pull Detection**: By default, displays the pullable status of your repositories in the parent directory (Dry-run). Setting `auto_git_pull = true` will automatically `git pull` (reference implementation from [cat-repo-auditor](https://github.com/cat2151/cat-repo-auditor)).
- **`cargo install` Auto-update**: For repositories operated with `cargo install`, setting `cargo_install_repos = ["repo-name"]` will automatically execute `cargo install --force` after a pull to keep the binary up-to-date.
- **Power Saving Mode**: Automatically extends monitoring intervals when there are no status changes (configurable with `no_change_timeout` and `reduced_frequency_interval`). Disabled by default (as ETag allows checks every minute without consuming API quota).
- **Verbose Mode**: Displays detailed configuration information on startup and during execution to help detect configuration errors (enabled with `verbose`).

## Architecture

This tool is a modularized Python application following the Single Responsibility Principle (SRP).

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
│       ├── pr_actions.py     # PR actions (Ready-fication, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1. **phase1 (Draft)**: PR is in Draft state and has review requests.
2. **phase2 (Addressing Review Comments)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3. **phase3 (Awaiting Review)**: `copilot-swe-agent` has completed corrections, and it's awaiting human review.
4. **LLM working (Coding Agent Working)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.11 or higher installed
- GitHub CLI (`gh`) installed and authenticated
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

3. Edit `config.toml` to set monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (optional):
   ```toml
   # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
   interval = "1m"
   
   # Maximum number of issues to display from repositories without PRs
   # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
   issue_display_limit = 10
   
   # Timeout for no state change
   # If the state of all PRs (phase of each PR) does not change for this duration,
   # the monitoring interval will switch to power saving mode (reduced_frequency_interval below)
   # Set to an empty string "" to disable (default)
   # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
   # Default: "" (disabled - ETag allows 304 checks every minute without query consumption)
   no_change_timeout = ""
   
   # Overwrite coding agent mention for comments (defaults to @copilot if omitted)
   [coding_agent]
   agent_name = "@codex[agent]"
   
   # Monitoring interval in power saving mode
   # If no state change is detected during the no_change_timeout period,
   # the monitoring interval will switch to this interval to reduce API usage.
   # When a change is detected, it returns to the normal monitoring interval.
   # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
   # Default: "1h" (1 hour)
   reduced_frequency_interval = "1h"
   
   # Verbose mode - displays detailed configuration information
   # When enabled, it displays all settings on startup and repository-specific settings during execution.
   # Helps in detecting configuration errors.
   # Default: false
   verbose = false
   
   # Color scheme for terminal output
   # Can be monokai (default) or classic
   color_scheme = "monokai"

   # Individual color codes can be overridden in the [colors] section (#RRGGBB format/ANSI allowed)
   # If omitted, the palette of the above color_scheme will be used
   [colors]
   # phase1 = "#E6DB74"
   # phase2 = "#66D9EF"
   # phase3 = "#A6E22E"
   # llm = "#F92672"
   # url = "#79C1FF"
   # url = "\u001b[94m"  # Example ANSI in TOML (ESC=[94m)
   
   # Toggle display of PR author
   # Controls whether "Author: <login>" is displayed in CLI output
   # Default: false
   display_pr_author = false
   
   # Local repository auto-pull setting (global flag dedicated to local repository watcher)
   # Default (false): Detects and displays pullable repositories only (Dry-run)
   # Set to true: Automatically performs `git pull` on pullable repositories
   # Scans repositories in the parent directory every 5 minutes (executes git fetch)
   # * This behavior is independent of PR actions, so this flag is specified at the top-level only.
   auto_git_pull = false
   
   # Target directory for local repository scanning (defaults to parent of current directory if omitted)
   # local_repo_watcher_base_dir = ".."
   
   # Execution control flags for PR actions - can only be specified within [[rulesets]] sections
   # Global flags are no longer supported (except for auto_git_pull)
   # To apply settings to all repositories, use 'repositories = ["all"]'
   
   # Example ruleset configuration:
   # [[rulesets]]
   # name = "Default for all repositories - dry-run mode"
   # repositories = ["all"]  # "all" matches all repositories
   # enable_execution_phase1_to_phase2 = false  # Set to true to make draft PR ready
   # enable_execution_phase2_to_phase3 = false  # Set to true to post phase2 comments
   # enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
   # enable_execution_phase3_to_merge = false   # Set to true to merge phase3 PRs
   
   # [[rulesets]]
   # name = "Simple: Auto-assign good first issue to Copilot"
   # repositories = ["my-repo"]
   # assign_good_first_old = true  # This is enough! The [assign_to_copilot] section is not needed.
   #                               # Default behavior: Opens issue in browser for manual assignment.
   
   # ntfy.sh notification settings (optional)
   # Notifications include clickable action buttons to open PRs.
   [ntfy]
   enabled = false  # Set to true to enable notifications
   topic = "<Enter your ntfy.sh topic name here>"  # Anyone can read/write, so use an unguessable string.
   message = "PR is ready for review: {url}"  # Message template
   priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
   all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs are in phase3
   
   # Phase3 Auto-merge settings (optional)
   # Automatically merges PRs when they reach phase3 (awaiting review).
   # Before merging, the comment defined below will be posted to the PR.
   # After successful merge, the feature branch is automatically deleted.
   # IMPORTANT: For safety, this feature is disabled by default.
   # You must explicitly enable it by setting enable_execution_phase3_to_merge = true in rulesets per repository.
   # IMPORTANT: If auto-merge is enabled, the comment field must be explicitly set.
   [phase3_merge]
   comment = "The agent has determined that review comments have been addressed. User review is skipped at the user's discretion. Merging PR."  # Comment to post before merging (required when auto-merge is enabled)
   automated = false  # Set to true to click merge button via browser automation
   wait_seconds = 10  # Waiting time (seconds) after browser launch before clicking button
   debug_dir = "debug_screenshots"  # Location to save debug info on image recognition failure (default: "debug_screenshots")
   notification_enabled = true  # Display a small notification window at specified coordinates during automated button operation
   notification_message = "Opening browser and searching for Merge button..."  # Message for the notification window
   notification_width = 400
   notification_height = 150
   notification_position_x = 100
   notification_position_y = 100
   maximize_on_first_fail = true  # Maximize window and retry search if button not found on first attempt

   # Auto-assign issue to Copilot (completely optional! This entire section is optional)
   # 
   # Simple usage: Just set assign_good_first_old = true in rulesets (see example above).
   # Define this section ONLY if you want to customize the default behavior.
   # 
   # Assignment behavior is controlled by ruleset flags:
   # - assign_ci_failure_old: Assigns the oldest "ci-failure" issue (by issue number, default: false)
   # - assign_deploy_pages_failure_old: Assigns the oldest "deploy-pages-failure" issue (by issue number, default: false)
   # - assign_good_first_old: Assigns the oldest "good first issue" (by issue number, default: false)
   # - assign_old: Assigns the oldest issue (by issue number, regardless of label, default: false)
   # Priority: ci-failure > deploy-pages-failure > good first issue > old issue
   # 
   # Default behavior (if this section is not defined):
   # - Automatically clicks buttons via browser automation
   # - Uses PyAutoGUI for image recognition
   # - Optional OCR fallback if image recognition fails
   # - wait_seconds = 2
   # 
   # Required: PyAutoGUI must be installed (pip install pyautogui pillow)
   # Optional: pytesseract must be installed for OCR fallback
   # 
   # IMPORTANT: For safety, this feature is disabled by default.
   # You must explicitly enable it by setting assign_ci_failure_old / assign_deploy_pages_failure_old /
   # assign_good_first_old / assign_old in rulesets per repository.
   [assign_to_copilot]
   wait_seconds = 2  # Waiting time (seconds) after browser launch before clicking button
   debug_dir = "debug_screenshots"  # Location to save debug info on image recognition failure (default: "debug_screenshots")
   confidence = 0.8  # Confidence level for image matching 0.0-1.0 (default: 0.8)
   enable_ocr_detection = true  # Enable OCR fallback (default: true)
   notification_enabled = true  # Display a small notification window at specified coordinates during automated button operation
   notification_message = "Opening browser and searching for Copilot assignment button..."  # Message for the notification window
   notification_width = 400
   notification_height = 150
   notification_position_x = 100
   notification_position_y = 100
   maximize_on_first_fail = true  # Maximize window and retry search if button not found on first attempt
   # enable_html_detection = false  # HTML detection fallback (experimental, default: false)
   ```

4. **Prepare Button Screenshots (only if using automation)**:
   
   If you use automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
   PyAutoGUI requires screenshots of the buttons to click.
   
   **Required screenshots:**
   
   For automated issue assignment (`assign_to_copilot` feature):
   - `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button
   - `assign.png` - Screenshot of the "Assign" button
   
   For automated PR merging (if `phase3_merge` feature with `automated = true`):
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
   - Screenshots should only include the button, with a small margin.
   - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
   - Ensure the button is clearly visible and not obscured.
   - If the button's appearance changes (e.g., theme change), you'll need to update the screenshots.
   - Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).
   
   **Automatic Debug Information Saving:**
   - If image recognition fails, debug information is automatically saved.
   - Save location: `debug_screenshots/` directory (default).
   - Saved content:
     - Screenshot (entire screen at time of failure): `{button_name}_fail_{timestamp}.png`
     - Screenshots of candidate regions (if found): `{button_name}_candidate_{timestamp}_{number}.png`
     - Failure information JSON: `{button_name}_fail_{timestamp}.json`
       - Button name, timestamp, confidence threshold, screenshot path, template image path.
       - Candidate region information (coordinates, size, confidence).
   - During debugging, up to 3 candidate regions are detected with lower confidence (0.7, 0.6, 0.5).
   - The debug directory can be changed in settings: `debug_dir` option (within `assign_to_copilot` or `phase3_merge` sections).
   
   **Fallback Methods (if image recognition fails):**
   - **OCR Detection (enabled by default)**: Uses pytesseract to detect button text.
     - Detects text like "Assign to Copilot" directly on screen.
     - Robust against subpixel rendering differences.
     - Required: tesseract-ocr installation (system-level).
     - Disable: `enable_ocr_detection = false`.
   
   **Important Requirements:**
   - You must be **already logged in to GitHub** in your default browser.
   - Automation uses your existing browser session (does not perform new authentication).
   - Ensure the correct GitHub window/tab is focused and visible on screen when a button click occurs.
   - If multiple GitHub pages are open, the first visible button found will be clicked.
   
   **Create `screenshots` directory:**
   ```bash
   mkdir screenshots
   ```

5. Install PyAutoGUI (only if using automation):
   
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

1. **Startup**: When the tool starts, it begins monitoring user-owned repositories for the authenticated GitHub user.
2. **PR Detection**: Automatically detects repositories with open PRs.
3. **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4. **Action Execution**:
   - **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PR is changed to Ready state).
   - **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, posts a comment requesting Copilot to apply changes).
   - **phase3**: Opens the PR page in the browser.
     - If `enable_execution_phase3_send_ntfy = true` in rulesets, also sends an ntfy.sh notification.
     - If `enable_execution_phase3_to_merge = true` in rulesets, automatically merges the PR (uses global `[phase3_merge]` settings).
   - **LLM working**: Waits (if all PRs are in this state, displays issues from repositories without open PRs).
5. **Issue Auto-assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
   - If `assign_ci_failure_old = true` in rulesets, automatically assigns the oldest "ci-failure" issue (by issue number).
   - If `assign_deploy_pages_failure_old = true` in rulesets, automatically assigns the oldest "deploy-pages-failure" issue (by issue number).
   - If `assign_good_first_old = true` in rulesets, automatically assigns the oldest "good first issue" issue (by issue number).
   - If `assign_old = true` in rulesets, automatically assigns the oldest issue (by issue number, regardless of label).
   - Priority: ci-failure > deploy-pages-failure > good first issue > old issue.
   - Default behavior: Automatically clicks buttons via PyAutoGUI (no `[assign_to_copilot]` section required).
   - Required: PyAutoGUI installation and button screenshots.
6. **Repetition**: Continues monitoring at the configured interval.
   - Due to ETag, monitoring continues every minute by default without consuming API quota.
   - If `no_change_timeout` is set, and no state change occurs for that duration, it automatically switches to power-saving mode (`reduced_frequency_interval`).
   - Returns to the normal monitoring interval when a change is detected.

### Dry-run Mode

By default, the tool operates in **Dry-run mode** and does not execute actual actions. This allows you to verify its operation safely.

- **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing.
- **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing.
- **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing.
- **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing.
- **Local Repositories**: Displays `[PULLABLE]` for pullable repositories and `[DRY-RUN] Would pull <repo>` but does nothing.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repositories"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Marks Draft PRs as Ready
enable_execution_phase2_to_phase3 = true  # Posts Phase2 comments
enable_execution_phase3_send_ntfy = true  # Sends ntfy notifications
enable_execution_phase3_to_merge = true   # Merges Phase3 PRs
assign_ci_failure_old = true              # Auto-assigns ci-failure issues
assign_deploy_pages_failure_old = true    # Auto-assigns deploy-pages-failure issues
assign_good_first_old = true              # Auto-assigns good first issues
```

To enable automatic pull for local repositories, set it at the top-level (outside rulesets):
```toml
auto_git_pull = true  # Automatically performs git pull on pullable local repositories
```

To automatically update binaries for `cargo install` operated repositories after a pull:
```toml
cargo_install_repos = ["voicevox-playground-tui"]  # Executes cargo install --force after pull
```

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- Assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
- Only **user-owned repositories** of authenticated users are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
- Be mindful of API rate limits when using the GraphQL API.
- If using ntfy.sh notifications, configure your topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Tests

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See LICENSE file for details

*Note: The English README.md is automatically generated from README.ja.md by GitHub Actions using Gemini's translation.*

*Big Brother is watching your repositories. Now it’s the cat.* 🐱