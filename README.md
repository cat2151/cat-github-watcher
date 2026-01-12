# cat-github-watcher

**PR monitoring tool for the automated implementation phase with GitHub Copilot**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

Note: A significant portion of this document was AI-generated. It was produced by submitting an issue to an agent.

## Status
- Currently dogfooding.
- Major bugs have been addressed.
- Breaking changes occur frequently.
- Notes
  - Initially, implementation was attempted with GitHub Actions, but it was found unsuitable for PR monitoring, so it was migrated to a Python version.
  - The Python version monitors authenticated GitHub users' owned repositories and performs notifications and actions based on PR phases.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of PRs where GitHub Copilot performs automated implementation, executing notifications and actions at appropriate times.
It efficiently monitors PRs in authenticated GitHub users' owned repositories using the GraphQL API.

## Features

- **Automatic Monitoring of All Repositories**: Automatically monitors PRs in repositories owned by authenticated GitHub users.
- **Leverages GraphQL API**: Enables high-speed monitoring through efficient data retrieval.
- **Phase Detection**: Automatically determines the PR's status (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent in progress).
- **Dry-run Mode**: By default, it only monitors and does not perform actual actions (comment posting, marking PR as Ready, sending notifications). Safe operation is possible by explicitly enabling it.
- **Automatic Comment Posting**: Automatically posts appropriate comments based on the phase (requires enabling in config file).
- **Automatic Draft PR Readying**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2 (requires enabling in config file).
- **Mobile Notifications**: Uses ntfy.sh to notify mobile devices when phase3 (awaiting review) is detected (requires enabling in config file).
  - Notifies when individual PRs enter phase3.
  - Also notifies when all PRs enter phase3 (message configurable in TOML).
- **Issue List Display**: If all PRs are "LLM working", displays the top N issues (default: 10, changeable via `issue_display_limit`) for repositories without open PRs.
- **Power Saving Mode**: If there's no state change, monitoring intervals are automatically extended to reduce API usage (configurable with `no_change_timeout` and `reduced_frequency_interval`).
- **Verbose Mode**: Displays detailed configuration information at startup and during execution to assist in detecting configuration errors (enabled with `verbose`).

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
│       ├── pr_actions.py     # PR actions (Readying, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1. **phase1 (Draft state)**: PR is in Draft state and has review requests.
2. **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3. **phase3 (Awaiting review)**: `copilot-swe-agent` has completed corrections and is awaiting human review.
4. **LLM working (Coding agent in progress)**: None of the above apply (e.g., Copilot is implementing).

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

3. Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and automatic merging (optional):
   ```toml
   # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
   interval = "1m"
   
   # Maximum number of issues to display from repositories with no open PRs
   # Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
   issue_display_limit = 10
   
   # Timeout duration for no state change
   # If the state of all PRs (phase of each PR) does not change for this duration,
   # the monitoring interval switches to power-saving mode (see reduced_frequency_interval below).
   # Setting an empty string "" disables it.
   # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
   # Default: "30m" (30 minutes - stability priority)
   no_change_timeout = "30m"
   
   # Monitoring interval in power-saving mode
   # If no state change is detected during the no_change_timeout period,
   # the monitoring interval switches to this interval to reduce API usage.
   # When a change is detected, it reverts to the normal monitoring interval.
   # Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
   # Default: "1h" (1 hour)
   reduced_frequency_interval = "1h"
   
   # Verbose mode - displays detailed configuration information
   # When enabled, it displays all configurations at startup and per-repository configurations during execution.
   # Helps detect configuration errors.
   # Default: false
   verbose = false
   
   # Execution control flags - can only be specified within the [[rulesets]] section
   # Global flags are no longer supported.
   # To apply settings to all repositories, use 'repositories = ["all"]'.
   
   # Ruleset configuration example:
   # [[rulesets]]
   # name = "Default for all repositories - dry-run mode"
   # repositories = ["all"]  # "all" matches all repositories
   # enable_execution_phase1_to_phase2 = false  # set to true to ready a draft PR
   # enable_execution_phase2_to_phase3 = false  # set to true to post phase2 comments
   # enable_execution_phase3_send_ntfy = false  # set to true to send ntfy notification
   # enable_execution_phase3_to_merge = false   # set to true to merge phase3 PR
   
   # [[rulesets]]
   # name = "Simple: Auto-assign good first issue to Copilot"
   # repositories = ["my-repo"]
   # assign_good_first_old = true  # This is enough! The [assign_to_copilot] section is not needed.
   #                               # Default behavior: Open issue in browser for manual assignment
   
   # ntfy.sh Notification Settings (Optional)
   # Notifications include a clickable action button to open the PR.
   [ntfy]
   enabled = false  # set to true to enable notifications
   topic = "<Enter your ntfy.sh topic name here>"  # Anyone can read/write, so use an unguessable string.
   message = "PR is ready for review: {url}"  # Message template
   priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
   all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs enter phase3
   
   # Phase3 Auto-Merge Settings (Optional)
   # Automatically merges PRs when they reach phase3 (awaiting review).
   # Before merging, the comment defined below will be posted to the PR.
   # After a successful merge, the feature branch is automatically deleted.
   # Important: For safety, this feature is disabled by default.
   # You must explicitly enable this by setting enable_execution_phase3_to_merge = true in rulesets for each repository.
   [phase3_merge]
   comment = "All checks passed. Merging PR."  # Comment to post before merging
   automated = false  # set to true to click the merge button via browser automation
   automation_backend = "selenium"  # Automation backend: "selenium" or "playwright"
   wait_seconds = 10  # Wait time (seconds) after browser launch and before button click
   browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
   headless = false  # Run in headless mode (do not display window)
   
   # Auto-assign issues to Copilot (Completely optional! This entire section is optional)
   # 
   # Simple usage: Just set assign_good_first_old = true in rulesets (see example above).
   # Define this section only if you want to customize the default behavior.
   # 
   # Assignment behavior is controlled by ruleset flags:
   # - assign_good_first_old: Assigns the oldest "good first issue" (by issue number, default: false)
   # - assign_old: Assigns the oldest issue (by issue number, label-agnostic, default: false)
   # If both are true, "good first issue" takes precedence.
   # 
   # Default behavior (if this section is not defined):
   # - Automatically clicks buttons via browser automation
   # - Uses Playwright + Chromium
   # - wait_seconds = 10
   # - headless = false
   # 
   # Required: Selenium or Playwright must be installed.
   # 
   # Important: For safety, this feature is disabled by default.
   # You must explicitly enable this by specifying assign_good_first_old or assign_old in rulesets for each repository.
   [assign_to_copilot]
   automation_backend = "playwright"  # Automation backend: "selenium" or "playwright"
   wait_seconds = 10  # Wait time (seconds) after browser launch and before button click
   browser = "chromium"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
   headless = false  # Run in headless mode (do not display window)
   ```

4. **Prepare button screenshots (only if using automation)**:
   
   If you are using automation features (i.e., `automated = true` or enabling `assign_to_copilot` / `phase3_merge`), you will need screenshots of the buttons that PyAutoGUI will click.
   
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
   b. Find the button you want to automate.
   c. Take a screenshot of **only the button** (not the entire screen).
   d. Save it as a PNG file in the `screenshots` directory.
   e. Use the exact filenames listed above.
   
   **Tips:**
   - Screenshots should contain only the button, with a small margin.
   - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
   - Ensure the button is clearly visible and not obscured.
   - If the button's appearance changes (e.g., due to theme changes), you'll need to update the screenshots.
   - Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).
   
   **Important Requirements:**
   - You must already be **logged in to GitHub** in your default browser.
   - Automation uses your existing browser session (it does not perform new authentication).
   - Ensure the correct GitHub window/tab is focused and visible on the screen when the button is clicked.
   - If multiple GitHub pages are open, the first found button will be clicked.
   
   **Create the screenshots directory:**
   ```bash
   mkdir screenshots
   ```

5. Install PyAutoGUI (only if using automation):
   
   ```bash
   pip install -r requirements-automation.txt
   ```
   Or
   ```bash
   pip install pyautogui pillow
   ```

### Execution

Start the tool to begin monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Operational Flow

1. **Startup**: The tool starts monitoring repositories owned by the authenticated GitHub user.
2. **PR Detection**: Automatically detects repositories with open PRs.
3. **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4. **Action Execution**:
   - **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PRs are changed to Ready state).
   - **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, a comment is posted requesting Copilot to apply changes).
   - **phase3**: Opens the PR page in the browser.
     - If `enable_execution_phase3_send_ntfy = true` in rulesets, an ntfy.sh notification is also sent.
     - If `enable_execution_phase3_to_merge = true` in rulesets, the PR is automatically merged (using global `[phase3_merge]` settings).
   - **LLM working**: Waits (if all PRs are in this state, issues in repositories without open PRs are displayed).
5. **Issue Auto-Assignment**: If all PRs are "LLM working" and there are repositories without open PRs:
   - If `assign_good_first_old = true` in rulesets, the oldest "good first issue" is automatically assigned (by issue number).
   - If `assign_old = true` in rulesets, the oldest issue is automatically assigned (by issue number, label-agnostic).
   - If both are true, "good first issue" takes precedence.
   - Default behavior: Automatically clicks buttons with PyAutoGUI (the `[assign_to_copilot]` section is not needed).
   - Required: PyAutoGUI installation and button screenshot preparation are necessary.
6. **Repetition**: Continues monitoring at the configured interval.
   - If no state change persists for the duration set by `no_change_timeout`, it automatically switches to power-saving mode (`reduced_frequency_interval`) to reduce API usage.
   - When a change is detected, it reverts to the normal monitoring interval.

### Dry-run Mode

By default, the tool operates in **Dry-run mode** and does not perform actual actions, allowing you to safely verify its operation.

- **Phase1 (Draft → Readying)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing.
- **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing.
- **Phase3 (ntfy notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing.
- **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for specific repositories"
repositories = ["test-repo"]  # or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Ready a Draft PR
enable_execution_phase2_to_phase3 = true  # Post Phase2 comments
enable_execution_phase3_send_ntfy = true  # Send ntfy notification
enable_execution_phase3_to_merge = true   # Merge Phase3 PR
assign_good_first_old = true              # Auto-assign good first issue
```

### Stopping

You can stop monitoring with `Ctrl+C`.

## Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- It is predicated on integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
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

Note: The English README.md is automatically generated by GitHub Actions based on README.ja.md, translated by Gemini.

*Big Brother is watching your repositories. Now it’s the cat.* 🐱