# cat-github-watcher

**PR monitoring tool for the automated implementation phase by GitHub Copilot**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

※A significant portion of this document is AI-generated. Issues were submitted to an agent for generation.

## Status
- Currently dogfooding.
- Major bugs have been addressed.
- Frequent breaking changes occur.
- Memo
  - Initially, implementation was attempted with GitHub Actions, but it proved unsuitable for PR monitoring, so it was migrated to a Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

A Python tool that monitors the phases of pull requests where GitHub Copilot performs automatic implementation and executes appropriate notifications and actions at the right time.
It targets user-owned repositories of authenticated GitHub users and efficiently monitors PRs using the GraphQL API.

## Features

- **Automated monitoring of all repositories**: Automatically monitors PRs in user-owned repositories for authenticated GitHub users.
- **GraphQL API utilization**: Achieves high-speed monitoring with efficient data retrieval.
- **Phase detection**: Automatically determines the PR state (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent working).
- **Dry-run mode**: By default, only monitors and does not perform actual actions (posting comments, making PRs Ready, sending notifications). Can be safely operated by explicit enablement.
- **Automated comment posting**: Automatically posts appropriate comments based on the phase (requires enablement in the configuration file).
- **Multi-agent support**: Automatically mentions `@codex[agent]` for PR creators like `openai-code-agent` (any `*-codex-coding-agent` type) and `@claude[agent]` for PR creators like `anthropic-code-agent` (any `*-claude-coding-agent` type). Falls back to `@copilot` if neither applies (can be overridden by `[coding_agent].agent_name`; defaults to `@copilot` if unset).
- **Automated Draft PR Ready-up**: Automatically changes Draft PRs to Ready state for addressing review comments in phase2 (requires enablement in the configuration file).
- **Mobile notifications**: Uses ntfy.sh to notify mobile devices when phase3 (awaiting review) is detected (requires enablement in the configuration file).
  - Notifies when individual PRs enter phase3.
  - Also notifies when all PRs enter phase3 (message configurable in TOML).
- **Issue list display**: If all PRs are "LLM working", displays the top N issues (default: 10, changeable via `issue_display_limit`) for repositories without open PRs.
- **Self-update**: On startup, it always checks whether an update is available and shows the result. It only performs pull/restart when `enable_auto_update = true`. With `enable_auto_update = false` (default, including when omitted), it detects and displays available updates without applying them. When enabled, update checks also continue every minute during the monitoring loop.
- **Local repository pull detection**: By default, displays the pullable status of your repositories in the parent directory (Dry-run). Setting `auto_git_pull = true` automatically pulls them ([cat-repo-auditor](https://github.com/cat2151/cat-repo-auditor) reference implementation).
- **`cargo install` auto-update**: For repositories operated with `cargo install`, setting `cargo_install_repos = ["repo-name"]` automatically executes `cargo install --force` after a pull is complete to keep the binary up-to-date.
- **Power-saving mode**: Feature to automatically extend the monitoring interval when there are no state changes (configurable with `no_change_timeout` and `reduced_frequency_interval`). Disabled by default (since ETag allows 1-minute checks without consuming API quota).
- **Verbose mode**: Displays detailed configuration information on startup and during execution to assist in detecting configuration errors (enabled with `verbose`).

## Architecture

This tool is a modular Python application adhering to the Single Responsibility Principle (SRP).

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
│       ├── pr_actions.py     # PR actions (Ready-up, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1. **phase1 (Draft State)**: PR is in Draft state and has review requests.
2. **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3. **phase3 (Awaiting review)**: `copilot-swe-agent` has completed corrections, and is awaiting human review.
4. **LLM working (Coding agent working)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.11 or later installed.
- GitHub CLI (`gh`) installed and authenticated.
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

3. Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (optional):
   ```toml
   # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
   interval = "1m"
   
   # Maximum number of issues to display from repositories without PRs
   # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
   issue_display_limit = 10
   
   # Timeout for no state change
   # If the state of all PRs (the phase of each PR) does not change for this duration,
   # the monitoring interval will switch to power-saving mode (reduced_frequency_interval below)
   # Set to an empty string "" to disable (default)
   # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
   # Default: "" (disabled - ETag allows 304 checks without query consumption every minute)
   no_change_timeout = ""
   
   # Override the coding agent mention used in posted comments (defaults to @copilot if omitted)
   [coding_agent]
   agent_name = "@codex[agent]"
   
   # Monitoring interval in power-saving mode
   # If no state change is detected during the no_change_timeout period,
   # the monitoring interval will switch to this interval to reduce API usage.
   # Once a change is detected, it will revert to the normal monitoring interval.
   # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
   # Default: "1h" (1 hour)
   reduced_frequency_interval = "1h"
   
   # Verbose mode - Displays detailed configuration information
   # If enabled, all settings will be displayed on startup, and per-repository settings during execution.
   # Helps in detecting configuration errors.
   # Default: false
   verbose = false
   
   # Color scheme for terminal output
   # Can be "monokai" (default) or "classic"
   color_scheme = "monokai"

   # Individual color codes can be overridden in the [colors] section (#RRGGBB format/ANSI supported)
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
   
   # Local repository auto-pull setting (global flag for local repository watcher only)
   # Default (false): Detects and displays pullable repositories only (Dry-run)
   # Set to true: Automatically performs git pull on pullable repositories
   # Scans repositories in the parent directory every 5 minutes (executes git fetch)
   # ※ This behavior is independent of PR actions, so this flag is specified at the top level only.
   auto_git_pull = false
   
   # Local repository scan target directory (defaults to parent of current directory if omitted)
   # local_repo_watcher_base_dir = ".."
   
   # Execution control flags for PR actions - can only be specified within [[rulesets]] sections
   # Global flags are no longer supported (except for auto_git_pull)
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
   # name = "Simple: Auto-assign good first issues to Copilot"
   # repositories = ["my-repo"]
   # assign_good_first_old = true  # This is enough! No [assign_to_copilot] section needed
   #                               # Default behavior: Open issue in browser for manual assignment
   
   # ntfy.sh notification settings (optional)
   # Notifications include clickable action buttons to open the PR.
   [ntfy]
   enabled = false  # Set to true to enable notifications
   topic = "<Enter your ntfy.sh topic name here>"  # Make it an unguessable string as anyone can read/write to it
   message = "PR is ready for review: {url}"  # Message template
   priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
   all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs enter phase3
   
   # Phase3 auto-merge settings (optional)
   # Automatically merges PRs once they reach phase3 (awaiting review).
   # Before merging, the comment defined below will be posted to the PR.
   # After successful merge, the feature branch will be automatically deleted.
   # IMPORTANT: For safety, this feature is disabled by default.
   # You must explicitly enable it by specifying enable_execution_phase3_to_merge = true in rulesets for each repository.
   # IMPORTANT: If auto-merge is enabled, the comment field must be explicitly set.
   [phase3_merge]
   comment = "The agent has determined that review comments have been addressed. User review is omitted under user's responsibility. Merging the PR."  # Comment to post before merging (required when auto-merge is enabled)
   automated = false  # Set to true to click the merge button via browser automation
   wait_seconds = 10  # Wait time in seconds after browser launch before clicking the button
   debug_dir = "debug_screenshots"  # Directory for saving debug info on image recognition failure (default: "debug_screenshots")
   notification_enabled = true  # Display a small notification window at specified coordinates during button automation
   notification_message = "Opening browser and searching for Merge button..."  # Message in the notification window
   notification_width = 400
   notification_height = 150
   notification_position_x = 100
   notification_position_y = 100
   maximize_on_first_fail = true  # Maximize window and re-search if button not found the first time

   # Auto-assign issues to Copilot (completely optional! This entire section is optional)
   # 
   # Simple usage: Just set assign_good_first_old = true in rulesets (see example above)
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
   # - Uses image recognition with PyAutoGUI
   # - OCR fallback on image recognition failure (optional)
   # - wait_seconds = 2
   # 
   # Required: PyAutoGUI installation needed (pip install pyautogui pillow)
   # Optional: pytesseract installation needed for OCR fallback
   # 
   # IMPORTANT: For safety, this feature is disabled by default.
   # You must explicitly enable it by specifying assign_ci_failure_old / assign_deploy_pages_failure_old /
   # assign_good_first_old / assign_old in rulesets for each repository.
   [assign_to_copilot]
   wait_seconds = 2  # Wait time in seconds after browser launch before clicking the button
   debug_dir = "debug_screenshots"  # Directory for saving debug info on image recognition failure (default: "debug_screenshots")
   confidence = 0.8  # Image matching confidence 0.0-1.0 (default: 0.8)
   enable_ocr_detection = true  # Enable OCR fallback (default: true)
   notification_enabled = true  # Display a small notification window at specified coordinates during button automation
   notification_message = "Opening browser and searching for Copilot assignment button..."  # Message in the notification window
   notification_width = 400
   notification_height = 150
   notification_position_x = 100
   notification_position_y = 100
   maximize_on_first_fail = true  # Maximize window and re-search if button not found the first time
   # enable_html_detection = false  # HTML detection fallback (experimental, default: false)
   ```

4. **Prepare button screenshots (only if using automation)**:
   
   If using automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
   you need screenshots of the buttons PyAutoGUI will click.
   
   **Required screenshots:**
   
   For automated issue assignment (`assign_to_copilot` feature):
   - `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button
   - `assign.png` - Screenshot of the "Assign" button
   
   For automated PR merge (`phase3_merge` feature with `automated = true`):
   - `merge_pull_request.png` - Screenshot of the "Merge pull request" button
   - `confirm_merge.png` - Screenshot of the "Confirm merge" button
   - `delete_branch.png` - Screenshot of the "Delete branch" button (optional)
   
   **How to take screenshots:**
   
   a. Open a GitHub issue or PR in your browser.
   b. Locate the button you want to automate.
   c. Take a screenshot of **only the button** (not the entire screen).
   d. Save it as a PNG file in the `screenshots` directory.
   e. Use the exact file names mentioned above.
   
   **Tips:**
   - Screenshots should only contain the button, with a small margin.
   - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
   - Ensure the button is clearly visible and not obscured.
   - If the button's appearance changes (e.g., due to theme changes), you'll need to update the screenshots.
   - Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).
   
   **Automatic saving of debug information:**
   - If image recognition fails, debug information is automatically saved.
   - Save location: `debug_screenshots/` directory (default).
   - Saved content:
     - Screenshot (entire screen at time of failure): `{button_name}_fail_{timestamp}.png`
     - Candidate region screenshots (if found): `{button_name}_candidate_{timestamp}_{number}.png`
     - Failure information JSON: `{button_name}_fail_{timestamp}.json`
       - Button name, timestamp, confidence threshold, screenshot path, template image path.
       - Candidate region information (coordinates, size, confidence).
   - For debugging, up to 3 candidate regions are detected with lower confidence (0.7, 0.6, 0.5).
   - The debug directory can be changed in settings: `debug_dir` option (within `assign_to_copilot` or `phase3_merge` sections).
   
   **Fallback methods (if image recognition fails):**
   - **OCR detection (enabled by default)**: Uses pytesseract to detect button text.
     - Directly detects text like "Assign to Copilot" on screen.
     - Robust against sub-pixel rendering differences.
     - Required: tesseract-ocr installation (system level).
     - Disable: `enable_ocr_detection = false`.
   
   **Important requirements:**
   - You must be **already logged in to GitHub** in your default browser.
   - Automation uses existing browser sessions (does not perform new authentication).
   - Ensure the correct GitHub window/tab is focused and visible on screen when clicking buttons.
   - If multiple GitHub pages are open, the first button found will be clicked.
   
   **Create the screenshots directory:**
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

### Flow of Operation

1. **Startup**: When the tool starts, it begins monitoring user-owned repositories for the authenticated GitHub user.
2. **PR detection**: Automatically detects repositories with open PRs.
3. **Phase determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4. **Action execution**:
   - **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PRs are changed to Ready state).
   - **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, a comment requesting Copilot to apply changes is posted).
   - **phase3**: Opens the PR page in the browser.
     - If `enable_execution_phase3_send_ntfy = true` in rulesets, also sends an ntfy.sh notification.
     - If `enable_execution_phase3_to_merge = true` in rulesets, automatically merges the PR (using global `[phase3_merge]` settings).
   - **LLM working**: Waits (if all PRs are in this state, displays issues from repositories without open PRs).
5. **Automated issue assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
   - If `assign_ci_failure_old = true` in rulesets, automatically assigns the oldest "ci-failure" issue (by issue number).
   - If `assign_deploy_pages_failure_old = true` in rulesets, automatically assigns the oldest "deploy-pages-failure" issue (by issue number).
   - If `assign_good_first_old = true` in rulesets, automatically assigns the oldest "good first issue" (by issue number).
   - If `assign_old = true` in rulesets, automatically assigns the oldest issue (by issue number, regardless of label).
   - Priority: ci-failure > deploy-pages-failure > good first issue > old issue.
   - Default behavior: Automatically clicks buttons with PyAutoGUI (no `[assign_to_copilot]` section required).
   - Required: PyAutoGUI installation and button screenshots.
6. **Repeat**: Continues monitoring at the configured interval.
   - Due to ETag, monitoring continues every minute without consuming API quota by default.
   - If `no_change_timeout` is set, and no state change occurs for that duration, it automatically switches to power-saving mode (`reduced_frequency_interval`).
   - Returns to normal monitoring interval when a change is detected.

### Dry-run Mode

By default, the tool operates in **Dry-run mode** and does not perform actual actions. This allows for safe operation verification.

- **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing actually.
- **Phase2 (Comment posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing actually.
- **Phase3 (ntfy notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing actually.
- **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing actually.
- **Local repository**: Displays pullable repositories as `[PULLABLE]` and `[DRY-RUN] Would pull <repo>` but does nothing actually.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repositories"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Make Draft PRs Ready
enable_execution_phase2_to_phase3 = true  # Post Phase2 comments
enable_execution_phase3_send_ntfy = true  # Send ntfy notifications
enable_execution_phase3_to_merge = true   # Merge Phase3 PRs
assign_ci_failure_old = true              # Auto-assign ci-failure issues
assign_deploy_pages_failure_old = true    # Auto-assign deploy-pages-failure issues
assign_good_first_old = true              # Auto-assign good first issues
```

To enable automatic pulling of local repositories, set it at the top level (outside rulesets):
```toml
auto_git_pull = true  # Automatically git pull pullable local repositories
```

To automatically update binaries for repositories managed with `cargo install` after a pull:
```toml
cargo_install_repos = ["voicevox-playground-tui"]  # Execute cargo install --force after pull
```

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- Assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
- Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
- Be mindful of GitHub API rate limits as it uses the GraphQL API.
- If using ntfy.sh notifications, configure a topic on [ntfy.sh](https://ntfy.sh/) in advance.

## Tests

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

※The English README.md is automatically generated from README.ja.md via GitHub Actions using Gemini's translation.

*Big Brother is watching your repositories. Now it’s the cat.* 🐱
