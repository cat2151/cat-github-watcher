Last updated: 2026-03-10

# 開発状況生成プロンプト（開発者向け）

## 生成するもの：
- 現在openされているissuesを3行で要約する
- 次の一手の候補を3つlistする
- 次の一手の候補3つそれぞれについて、極力小さく分解して、その最初の小さな一歩を書く

## 生成しないもの：
- 「今日のissue目標」などuserに提案するもの
  - ハルシネーションの温床なので生成しない
- ハルシネーションしそうなものは生成しない（例、無価値なtaskや新issueを勝手に妄想してそれをuserに提案する等）
- プロジェクト構造情報（来訪者向け情報のため、別ファイルで管理）

## 「Agent実行プロンプト」生成ガイドライン：
「Agent実行プロンプト」作成時は以下の要素を必ず含めてください：

### 必須要素
1. **対象ファイル**: 分析/編集する具体的なファイルパス
2. **実行内容**: 具体的な分析や変更内容（「分析してください」ではなく「XXXファイルのYYY機能を分析し、ZZZの観点でmarkdown形式で出力してください」）
3. **確認事項**: 変更前に確認すべき依存関係や制約
4. **期待する出力**: markdown形式での結果や、具体的なファイル変更

### Agent実行プロンプト例

**良い例（上記「必須要素」4項目を含む具体的なプロンプト形式）**:
```
対象ファイル: `.github/workflows/translate-readme.yml`と`.github/workflows/call-translate-readme.yml`

実行内容: 対象ファイルについて、外部プロジェクトから利用する際に必要な設定項目を洗い出し、以下の観点から分析してください：
1) 必須入力パラメータ（target-branch等）
2) 必須シークレット（GEMINI_API_KEY）
3) ファイル配置の前提条件（README.ja.mdの存在）
4) 外部プロジェクトでの利用時に必要な追加設定

確認事項: 作業前に既存のworkflowファイルとの依存関係、および他のREADME関連ファイルとの整合性を確認してください。

期待する出力: 外部プロジェクトがこの`call-translate-readme.yml`を導入する際の手順書をmarkdown形式で生成してください。具体的には：必須パラメータの設定方法、シークレットの登録手順、前提条件の確認項目を含めてください。
```

**避けるべき例**:
- callgraphについて調べてください
- ワークフローを分析してください
- issue-noteの処理フローを確認してください

## 出力フォーマット：
以下のMarkdown形式で出力してください：

```markdown
# Development Status

## 現在のIssues
[以下の形式で3行でオープン中のissuesを要約。issue番号を必ず書く]
- [1行目の説明]
- [2行目の説明]
- [3行目の説明]

## 次の一手候補
1. [候補1のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```

2. [候補2のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```

3. [候補3のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```
```


# 開発状況情報
- 以下の開発状況情報を参考にしてください。
- Issue番号を記載する際は、必ず [Issue #番号](../issue-notes/番号.md) の形式でMarkdownリンクとして記載してください。

## プロジェクトのファイル一覧
- .editorconfig
- .github/actions-tmp/.github/workflows/call-callgraph.yml
- .github/actions-tmp/.github/workflows/call-check-large-files.yml
- .github/actions-tmp/.github/workflows/call-daily-project-summary.yml
- .github/actions-tmp/.github/workflows/call-issue-note.yml
- .github/actions-tmp/.github/workflows/call-rust-windows-check.yml
- .github/actions-tmp/.github/workflows/call-translate-readme.yml
- .github/actions-tmp/.github/workflows/callgraph.yml
- .github/actions-tmp/.github/workflows/check-large-files.yml
- .github/actions-tmp/.github/workflows/check-recent-human-commit.yml
- .github/actions-tmp/.github/workflows/daily-project-summary.yml
- .github/actions-tmp/.github/workflows/issue-note.yml
- .github/actions-tmp/.github/workflows/rust-windows-check.yml
- .github/actions-tmp/.github/workflows/translate-readme.yml
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/callgraph.ql
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/codeql-pack.lock.yml
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/qlpack.yml
- .github/actions-tmp/.github_automation/callgraph/config/example.json
- .github/actions-tmp/.github_automation/callgraph/docs/callgraph.md
- .github/actions-tmp/.github_automation/callgraph/presets/callgraph.js
- .github/actions-tmp/.github_automation/callgraph/presets/style.css
- .github/actions-tmp/.github_automation/callgraph/scripts/analyze-codeql.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/callgraph-utils.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/check-codeql-exists.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/check-node-version.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/common-utils.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/copy-commit-results.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/extract-sarif-info.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/find-process-results.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/generate-html-graph.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/generateHTML.cjs
- .github/actions-tmp/.github_automation/check-large-files/README.md
- .github/actions-tmp/.github_automation/check-large-files/check-large-files.toml.default
- .github/actions-tmp/.github_automation/check-large-files/scripts/check_large_files.py
- .github/actions-tmp/.github_automation/check_recent_human_commit/scripts/check-recent-human-commit.cjs
- .github/actions-tmp/.github_automation/project_summary/docs/daily-summary-setup.md
- .github/actions-tmp/.github_automation/project_summary/prompts/development-status-prompt.md
- .github/actions-tmp/.github_automation/project_summary/prompts/project-overview-prompt.md
- .github/actions-tmp/.github_automation/project_summary/scripts/ProjectSummaryCoordinator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/GitUtils.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/IssueTracker.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/generate-project-summary.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/CodeAnalyzer.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectAnalysisOrchestrator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectDataCollector.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectDataFormatter.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectOverviewGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/BaseGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/FileSystemUtils.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/ProjectFileUtils.cjs
- .github/actions-tmp/.github_automation/translate/docs/TRANSLATION_SETUP.md
- .github/actions-tmp/.github_automation/translate/scripts/translate-readme.cjs
- .github/actions-tmp/.gitignore
- .github/actions-tmp/.vscode/settings.json
- .github/actions-tmp/LICENSE
- .github/actions-tmp/README.ja.md
- .github/actions-tmp/README.md
- .github/actions-tmp/_config.yml
- .github/actions-tmp/generated-docs/callgraph.html
- .github/actions-tmp/generated-docs/callgraph.js
- .github/actions-tmp/generated-docs/development-status-generated-prompt.md
- .github/actions-tmp/generated-docs/development-status.md
- .github/actions-tmp/generated-docs/project-overview-generated-prompt.md
- .github/actions-tmp/generated-docs/project-overview.md
- .github/actions-tmp/generated-docs/style.css
- .github/actions-tmp/googled947dc864c270e07.html
- .github/actions-tmp/issue-notes/10.md
- .github/actions-tmp/issue-notes/11.md
- .github/actions-tmp/issue-notes/12.md
- .github/actions-tmp/issue-notes/13.md
- .github/actions-tmp/issue-notes/14.md
- .github/actions-tmp/issue-notes/15.md
- .github/actions-tmp/issue-notes/16.md
- .github/actions-tmp/issue-notes/17.md
- .github/actions-tmp/issue-notes/18.md
- .github/actions-tmp/issue-notes/19.md
- .github/actions-tmp/issue-notes/2.md
- .github/actions-tmp/issue-notes/20.md
- .github/actions-tmp/issue-notes/21.md
- .github/actions-tmp/issue-notes/22.md
- .github/actions-tmp/issue-notes/23.md
- .github/actions-tmp/issue-notes/24.md
- .github/actions-tmp/issue-notes/25.md
- .github/actions-tmp/issue-notes/26.md
- .github/actions-tmp/issue-notes/27.md
- .github/actions-tmp/issue-notes/28.md
- .github/actions-tmp/issue-notes/29.md
- .github/actions-tmp/issue-notes/3.md
- .github/actions-tmp/issue-notes/30.md
- .github/actions-tmp/issue-notes/35.md
- .github/actions-tmp/issue-notes/38.md
- .github/actions-tmp/issue-notes/4.md
- .github/actions-tmp/issue-notes/40.md
- .github/actions-tmp/issue-notes/44.md
- .github/actions-tmp/issue-notes/52.md
- .github/actions-tmp/issue-notes/7.md
- .github/actions-tmp/issue-notes/8.md
- .github/actions-tmp/issue-notes/9.md
- .github/actions-tmp/package-lock.json
- .github/actions-tmp/package.json
- .github/actions-tmp/src/main.js
- .github/copilot-instructions.md
- .github/workflows/call-check-large-files.yml
- .github/workflows/call-daily-project-summary.yml
- .github/workflows/call-issue-note.yml
- .github/workflows/call-translate-readme.yml
- .github/workflows/run-tests-on-push.yml
- .gitignore
- .vscode/settings.json
- LICENSE
- README.ja.md
- README.md
- _config.yml
- cat-github-watcher.py
- config.toml.example
- demo_automation.py
- docs/RULESETS.md
- docs/button-detection-improvements.ja.md
- docs/window-activation-feature.md
- fetch_pr_html.py
- generated-docs/project-overview-generated-prompt.md
- pyproject.toml
- pytest.ini
- requirements-automation.txt
- ruff.toml
- screenshots/assign.png
- screenshots/assign_to_copilot.png
- src/__init__.py
- src/gh_pr_phase_monitor/__init__.py
- src/gh_pr_phase_monitor/actions/__init__.py
- src/gh_pr_phase_monitor/actions/pr_actions.py
- src/gh_pr_phase_monitor/browser/__init__.py
- src/gh_pr_phase_monitor/browser/browser_automation.py
- src/gh_pr_phase_monitor/browser/browser_cooldown.py
- src/gh_pr_phase_monitor/browser/button_clicker.py
- src/gh_pr_phase_monitor/browser/click_config_validator.py
- src/gh_pr_phase_monitor/browser/window_manager.py
- src/gh_pr_phase_monitor/core/__init__.py
- src/gh_pr_phase_monitor/core/colors.py
- src/gh_pr_phase_monitor/core/config.py
- src/gh_pr_phase_monitor/core/config_printer.py
- src/gh_pr_phase_monitor/core/interval_parser.py
- src/gh_pr_phase_monitor/core/process_utils.py
- src/gh_pr_phase_monitor/core/time_utils.py
- src/gh_pr_phase_monitor/github/__init__.py
- src/gh_pr_phase_monitor/github/comment_fetcher.py
- src/gh_pr_phase_monitor/github/comment_manager.py
- src/gh_pr_phase_monitor/github/github_auth.py
- src/gh_pr_phase_monitor/github/github_client.py
- src/gh_pr_phase_monitor/github/graphql_client.py
- src/gh_pr_phase_monitor/github/issue_fetcher.py
- src/gh_pr_phase_monitor/github/pr_fetcher.py
- src/gh_pr_phase_monitor/github/rate_limit_handler.py
- src/gh_pr_phase_monitor/github/repository_fetcher.py
- src/gh_pr_phase_monitor/main.py
- src/gh_pr_phase_monitor/monitor/__init__.py
- src/gh_pr_phase_monitor/monitor/auto_updater.py
- src/gh_pr_phase_monitor/monitor/error_logger.py
- src/gh_pr_phase_monitor/monitor/iteration_runner.py
- src/gh_pr_phase_monitor/monitor/local_repo_watcher.py
- src/gh_pr_phase_monitor/monitor/monitor.py
- src/gh_pr_phase_monitor/monitor/pages_watcher.py
- src/gh_pr_phase_monitor/monitor/pr_processor.py
- src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py
- src/gh_pr_phase_monitor/monitor/state_tracker.py
- src/gh_pr_phase_monitor/phase/__init__.py
- src/gh_pr_phase_monitor/phase/html/__init__.py
- src/gh_pr_phase_monitor/phase/html/html_status_processor.py
- src/gh_pr_phase_monitor/phase/html/llm_status_extractor.py
- src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py
- src/gh_pr_phase_monitor/phase/html/pr_html_fetcher.py
- src/gh_pr_phase_monitor/phase/html/pr_html_saver.py
- src/gh_pr_phase_monitor/phase/phase_detector.py
- src/gh_pr_phase_monitor/ui/__init__.py
- src/gh_pr_phase_monitor/ui/display.py
- src/gh_pr_phase_monitor/ui/notification_window.py
- src/gh_pr_phase_monitor/ui/notifier.py
- src/gh_pr_phase_monitor/ui/wait_handler.py
- tests/test_assign_issue_to_copilot.py
- tests/test_auto_update_config.py
- tests/test_auto_updater.py
- tests/test_batteries_included_defaults.py
- tests/test_browser_automation.py
- tests/test_browser_automation_click.py
- tests/test_browser_automation_ocr.py
- tests/test_browser_automation_window.py
- tests/test_check_process_before_autoraise.py
- tests/test_color_scheme_config.py
- tests/test_config_rulesets.py
- tests/test_config_rulesets_features.py
- tests/test_elapsed_time_display.py
- tests/test_error_logging.py
- tests/test_fetch_pr_html.py
- tests/test_graphql_client_rate_limit.py
- tests/test_graphql_query_intent_display.py
- tests/test_has_comments_with_reactions.py
- tests/test_has_unresolved_review_threads.py
- tests/test_hot_reload.py
- tests/test_html_status_processor.py
- tests/test_html_to_markdown.py
- tests/test_integration_issue_fetching.py
- tests/test_interval_contamination_bug.py
- tests/test_interval_parsing.py
- tests/test_is_llm_working.py
- tests/test_issue_assignment_priority.py
- tests/test_issue_fetching.py
- tests/test_llm_status_timestamp.py
- tests/test_llm_working_warning.py
- tests/test_local_repo_watcher.py
- tests/test_local_repo_watcher_background.py
- tests/test_max_llm_working_parallel.py
- tests/test_no_change_timeout.py
- tests/test_no_open_prs_issue_display.py
- tests/test_notification.py
- tests/test_open_browser_cooldown.py
- tests/test_pages_watcher.py
- tests/test_phase3_merge.py
- tests/test_phase_detection.py
- tests/test_phase_detection_llm_status.py
- tests/test_phase_detection_real_prs.py
- tests/test_post_comment.py
- tests/test_post_phase3_comment.py
- tests/test_pr_actions.py
- tests/test_pr_actions_dry_run.py
- tests/test_pr_actions_rulesets_features.py
- tests/test_pr_actions_with_rulesets.py
- tests/test_pr_html_analyzer.py
- tests/test_pr_html_analyzer_copilot_review.py
- tests/test_pr_title_fix.py
- tests/test_rate_limit_reset_display.py
- tests/test_rate_limit_throttle.py
- tests/test_rate_limit_usage_display.py
- tests/test_repos_with_prs_structure.py
- tests/test_show_issues_when_pr_count_less_than_3.py
- tests/test_skip_pr_check_html_refetch.py
- tests/test_status_summary.py
- tests/test_updated_at_optimization.py
- tests/test_validate_phase3_merge_config.py
- tests/test_verbose_config.py
- tests/test_wait_handler_callback.py

## 現在のオープンIssues
## [Issue #411](../issue-notes/411.md): phase3A後PRクローズ時にauto pullが実行されない問題を修正
- [x] Understand the issue: when a repo's PR was in phase3A and the user merges/closes it, the open PR count drops to 0, so `notify_phase3_detected` is never called and auto-pull never happens
- [x] Add `_repos_awaiting_post_phase3_check: Set[str]` tracking in `local_repo_watcher.py`
- [x] Modify `n...
ラベル: 
--- issue-notes/411.md の内容 ---

```markdown

```

## [Issue #410](../issue-notes/410.md): PRをcloseし、pullすべき状態のリポジトリになったのに、opened PRが0になったためか自動pullがされていなかった

ラベル: 
--- issue-notes/410.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/10.md
```md
{% raw %}
# issue callgraph を他projectから使いやすくする #10
[issues #10](https://github.com/cat2151/github-actions/issues/10)

# ブレインストーミング
- 洗い出し
    - 他projectから使う場合の問題を洗い出す、今見えている範囲で、手早く、このnoteに可視化する
    - 洗い出したものは、一部は別issueに切り分ける
- close条件
    - [x] まずは4つそれぞれを個別のdirに切り分けてtest greenとなること、とするつもり
        - 別issueに切り分けるつもり
- 切り分け
    - 別dirに切り分ける
        - [x] 課題、`codeql-queries/` が `.github/` 配下にある。対策、`.github_automation/callgraph/codeql-queries/` とする
        - [x] 課題、scriptも、`.github/`配下にある。対策、移動する
        - 方法、agentを試し、ハルシネーションで時間が取られるなら人力に切り替える
- test
    - local WSL + act でtestする
- 名前
    - [x] 課題、名前 enhanced が不要。対策、名前から enhanced を削除してymlなどもそれぞれ同期して修正すべし
- docs
    - [x] call導入手順を書く

# 状況
- 実際に他project tonejs-mml-to-json リポジトリにて使うことができている
    - その際に発生した運用ミスは、
        - call導入手順のメンテを行ったので、改善された、と判断する

# closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/11.md
```md
{% raw %}
# issue translate を他projectから使いやすくする #11
[issues #11](https://github.com/cat2151/github-actions/issues/11)

# ブレインストーミング
- 課題、個別dirへの移動が必要。
    - scripts
- 課題、promptをハードコーディングでなく、promptsに切り出す。
    - さらに、呼び出し元ymlから任意のpromptsを指定できるようにする。
- 済、課題、README以外のtranslateも可能にするか検討する
    - 対策、シンプル優先でREADME決め打ちにする
        - 理由、README以外の用途となると、複数ファイルをどうGemini APIにわたすか？等、仕様が爆発的にふくらんでいくリスクがある
        - README以外の用途が明確でないうちは、README決め打ちにするほうがよい
- docs
    - call導入手順を書く

# 状況
- 上記のうち、別dirへの切り分け等は実施済みのはず
- どうする？
    - それをここに可視化する。

{% endraw %}
```

### src/gh_pr_phase_monitor/monitor/local_repo_watcher.py
```py
{% raw %}
"""
Local repository monitoring module

Scans the parent directory of the current working directory for local git
repositories owned by the current GitHub user, checks if they have pullable
changes (upstream commits not yet merged), and optionally auto-pulls them.

Inspired by cat-repo-auditor/github_local_checker.py.
"""

from __future__ import annotations

import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

from .auto_updater import REPO_ROOT, restart_application
from ..core.colors import Colors

# Status constants (same classification as cat-repo-auditor)
STATUS_PULLABLE = "pullable"  # behind > 0, ahead == 0, not dirty → can pull now
STATUS_DIVERGED = "diverged"  # behind > 0 and ahead > 0 → needs manual merge
STATUS_UP_TO_DATE = "up_to_date"  # behind == 0 → already latest
STATUS_UNKNOWN = "unknown"  # fetch failed or dirty with behind > 0

# Throttle repeated git-fetch cycles to avoid excessive network calls
LOCAL_REPO_CHECK_INTERVAL_SECONDS = 300  # 5 minutes

_last_local_check_time: float = 0.0

# Per-repo state constants for background check tracking
REPO_STATE_STARTUP_CHECKING = "startup_checking"  # 起動時検査中
REPO_STATE_DONE = "done"  # 起動後検査完了
REPO_STATE_NEEDS_CHECK = "needs_check"  # 起動後検査が必要（phase3検知）
REPO_STATE_CHECKING = "checking"  # 起動後検査中

# Module-level state for background monitoring
_repo_states: Dict[str, str] = {}  # repo_name -> state
_pending_lines: List[str] = []  # 表示待ち行（次のintervalで一括表示）
_pending_needs_restart: bool = False  # 自己更新による再起動フラグ
_state_lock = threading.Lock()
_startup_started: bool = False  # 起動時検査を開始済みか


def _run_git(args: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"  # Prevent credential prompts from blocking
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        env=env,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _is_git_repo(path: str) -> bool:
    """Return True if the directory is a git repository."""
    rc, _, _ = _run_git(["rev-parse", "--git-dir"], path)
    return rc == 0


def _get_remote_url(path: str) -> Optional[str]:
    """Return the URL of the 'origin' remote, or None."""
    rc, out, _ = _run_git(["remote", "get-url", "origin"], path)
    return out if rc == 0 and out else None


def _is_target_repo(remote_url: str, github_username: str) -> bool:
    """Return True if the remote URL belongs to the given GitHub user.

    Supports both HTTPS (https://github.com/<user>/...)
    and SSH (git@github.com:<user>/...) URL formats.
    Uses strict host matching to avoid false positives from URLs like
    'github.com.evil.com' or 'notgithub.com'.
    """
    user_low = github_username.lower()
    stripped = remote_url.strip().lower()

    # SSH format: git@github.com:<user>/...
    if stripped.startswith("git@github.com:"):
        rest = stripped[len("git@github.com:") :]
        return rest.startswith(f"{user_low}/")

    # HTTPS format: https://github.com/<user>/...
    for prefix in ("https://github.com/", "http://github.com/"):
        if stripped.startswith(prefix):
            rest = stripped[len(prefix) :]
            return rest.startswith(f"{user_low}/")

    return False


def _is_dirty(path: str) -> bool:
    """Return True if the working tree has uncommitted changes."""
    rc, out, _ = _run_git(["status", "--porcelain"], path)
    return bool(out) if rc == 0 else True


def _get_current_branch(path: str) -> Optional[str]:
    """Return the current branch name, or None on failure."""
    rc, out, _ = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
    return out if rc == 0 else None


def _fetch_remote(path: str) -> tuple[bool, Optional[str]]:
    """Fetch from origin. Returns (success, error_message_or_None)."""
    rc, _, err = _run_git(["fetch", "origin", "--quiet"], path)
    if rc != 0:
        msg = f"git fetch 失敗: {err}" if err else "git fetch 失敗"
        return False, msg
    return True, None


def _get_behind_ahead(path: str, branch: str) -> tuple[int, int]:
    """Return (behind, ahead) relative to origin/<branch>, or (-1, -1) on failure."""
    tracking = f"origin/{branch}"
    rc, out, _ = _run_git(
        ["rev-list", "--left-right", "--count", f"{tracking}...HEAD"],
        path,
    )
    if rc != 0:
        return -1, -1
    parts = out.split()
    if len(parts) != 2:
        return -1, -1
    return int(parts[0]), int(parts[1])


def _pull_repo(path: str) -> tuple[bool, str]:
    """Execute git pull --ff-only. Returns (success, message).

    Should only be called for repos classified as pullable
    (dirty=False, ahead==0, behind>0).
    """
    rc, out, err = _run_git(["pull", "--ff-only"], path)
    if rc != 0:
        return False, err or "git pull 失敗"
    return True, out or "Already up to date."


def _check_repo(path: str, github_username: str) -> dict:
    """Fetch and classify a single repository.

    Returns a dict with keys:
        name, path, remote_url, branch, dirty, behind, ahead, status, error, is_target
    """
    p = Path(path)
    result: dict = {
        "name": p.name,
        "path": path,
        "remote_url": None,
        "branch": None,
        "dirty": False,
        "behind": None,
        "ahead": None,
        "status": STATUS_UNKNOWN,
        "error": None,
        "is_target": False,
    }

    if not _is_git_repo(path):
        return result

    remote_url = _get_remote_url(path)
    result["remote_url"] = remote_url
    if not remote_url:
        return result

    if not _is_target_repo(remote_url, github_username):
        return result

    result["is_target"] = True

    fetch_ok, fetch_err = _fetch_remote(path)
    if not fetch_ok:
        result["error"] = fetch_err
        return result

    branch = _get_current_branch(path)
    result["branch"] = branch
    if not branch:
        result["error"] = "ブランチ取得失敗"
        return result

    dirty = _is_dirty(path)
    result["dirty"] = dirty

    behind, ahead = _get_behind_ahead(path, branch)
    if behind == -1:
        result["error"] = f"origin/{branch} との比較失敗"
        return result

    result["behind"] = behind
    result["ahead"] = ahead

    # Classify status (same logic as cat-repo-auditor)
    if behind == 0:
        result["status"] = STATUS_UP_TO_DATE
    elif behind > 0 and ahead > 0:
        result["status"] = STATUS_DIVERGED
    elif behind > 0 and ahead == 0:
        if dirty:
            result["status"] = STATUS_UNKNOWN  # want to pull but dirty
        else:
            result["status"] = STATUS_PULLABLE
    else:
        # Fallback for any unexpected combination not covered above
        # (e.g. if _get_behind_ahead returns values outside [0, +inf)).
        # Treat conservatively as unknown rather than risking incorrect action.
        result["status"] = STATUS_UNKNOWN

    return result


def check_local_repos(config: dict, github_username: str) -> None:
    """Scan local repos in the base directory, display pullable ones, and optionally pull.

    By default (dry-run), pullable repos are displayed but not pulled.
    Set ``auto_git_pull = true`` in config.toml to enable auto-pull.

    Args:
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    global _last_local_check_time

    now = time.time()
    if _last_local_check_time and now - _last_local_check_time < LOCAL_REPO_CHECK_INTERVAL_SECONDS:
        return
    _last_local_check_time = now

    base_dir_str = config.get("local_repo_watcher_base_dir", None)
    if base_dir_str:
        base_dir = Path(base_dir_str)
    else:
        base_dir = Path.cwd().parent

    if not base_dir.exists() or not base_dir.is_dir():
        return

    enable_pull = config.get("auto_git_pull", False)

    # Collect candidate directories (siblings in the base dir)
    try:
        candidates = [str(d) for d in sorted(base_dir.iterdir()) if d.is_dir() and not d.name.startswith(".")]
    except PermissionError:
        return

    if not candidates:
        return

    # Check each candidate with live progress display (same style as wait countdown)
    total = len(candidates)
    results = []
    max_msg_len = 0
    for i, d in enumerate(candidates):
        repo_name = Path(d).name
        msg = f"[{i + 1}/{total}] リポジトリ確認中: {repo_name}..."
        if len(msg) > max_msg_len:
            max_msg_len = len(msg)
        padding = max_msg_len - len(msg)
        print(f"\r{msg}{' ' * padding}", end="", flush=True)
        results.append(_check_repo(d, github_username))
    if candidates:
        print(f"\r{' ' * max_msg_len}\r", end="", flush=True)
    target_results = [r for r in results if r["is_target"]]

    pullable = [r for r in target_results if r["status"] == STATUS_PULLABLE]
    diverged = [r for r in target_results if r["status"] == STATUS_DIVERGED]

    if not pullable and not diverged:
        return

    print(f"\n{'=' * 50}")
    print("ローカルリポジトリ状態:")
    print(f"{'=' * 50}")

    for r in pullable:
        detail = f"behind {r['behind']}"
        print(f"  {Colors.GREEN}[PULLABLE]{Colors.RESET} {r['name']}  ({detail})")
        if enable_pull:
            ok, msg = _pull_repo(r["path"])
            if ok:
                print(f"    ✓ pull 完了: {r['name']}")
                if Path(r["path"]).resolve() == REPO_ROOT:
                    print("    自分自身が更新されました。アプリケーションを再起動します...")
                    restart_application()
            else:
                print(f"    ✗ pull 失敗: {r['name']}: {msg}")
        else:
            print(f"    [DRY-RUN] Would pull {r['name']} (auto_git_pull=false)")

    for r in diverged:
        detail = f"behind {r['behind']}, ahead {r['ahead']}"
        print(f"  {Colors.YELLOW}[DIVERGED]{Colors.RESET} {r['name']}  ({detail}) ⚠ 手動マージが必要")


def _get_base_dir(config: dict) -> Optional[Path]:
    """Return the base directory for local repo scanning, or None if not valid."""
    base_dir_str = config.get("local_repo_watcher_base_dir", None)
    base_dir = Path(base_dir_str) if base_dir_str else Path.cwd().parent
    if not base_dir.exists() or not base_dir.is_dir():
        return None
    return base_dir


def _accumulate_result(result: dict, enable_pull: bool) -> None:
    """Process a single repo check result: pull if needed, accumulate display lines.

    Must be called with _state_lock NOT held (since _pull_repo may block).
    Acquires _state_lock to append to _pending_lines / set _pending_needs_restart.
    """
    global _pending_needs_restart

    if not result["is_target"]:
        return
    if result["status"] not in (STATUS_PULLABLE, STATUS_DIVERGED):
        return

    lines: List[str] = []
    needs_restart = False

    if result["status"] == STATUS_PULLABLE:
        detail = f"behind {result['behind']}"
        lines.append(f"  {Colors.GREEN}[PULLABLE]{Colors.RESET} {result['name']}  ({detail})")
        if enable_pull:
            ok, msg = _pull_repo(result["path"])
            if ok:
                lines.append(f"    ✓ pull 完了: {result['name']}")
                if Path(result["path"]).resolve() == REPO_ROOT:
                    lines.append("    自分自身が更新されました。アプリケーションを再起動します...")
                    needs_restart = True
            else:
                lines.append(f"    ✗ pull 失敗: {result['name']}: {msg}")
        else:
            lines.append(f"    [DRY-RUN] Would pull {result['name']} (auto_git_pull=false)")
    else:  # STATUS_DIVERGED
        detail = f"behind {result['behind']}, ahead {result['ahead']}"
        lines.append(f"  {Colors.YELLOW}[DIVERGED]{Colors.RESET} {result['name']}  ({detail}) ⚠ 手動マージが必要")

    with _state_lock:
        _pending_lines.extend(lines)
        if needs_restart:
            _pending_needs_restart = True


def _background_startup_check(config: dict, github_username: str) -> None:
    """Background thread: check all repos in base_dir and accumulate results.

    各リポジトリの状態を STARTUP_CHECKING → DONE に更新しながら順次検査する。
    """
    base_dir = _get_base_dir(config)
    if base_dir is None:
        return

    enable_pull = config.get("auto_git_pull", False)

    try:
        candidates = [str(d) for d in sorted(base_dir.iterdir()) if d.is_dir() and not d.name.startswith(".")]
    except PermissionError:
        return

    if not candidates:
        return

    # Mark all candidates as STARTUP_CHECKING before any check begins
    with _state_lock:
        for d in candidates:
            _repo_states[Path(d).name] = REPO_STATE_STARTUP_CHECKING

    for d in candidates:
        repo_name = Path(d).name
        try:
            result = _check_repo(d, github_username)
            _accumulate_result(result, enable_pull)
        except Exception:
            pass
        finally:
            with _state_lock:
                _repo_states[repo_name] = REPO_STATE_DONE


def _background_single_repo_check(repo_path: str, repo_name: str, github_username: str, enable_pull: bool) -> None:
    """Background thread: check a single repo and accumulate result.

    phase3検知時に呼び出される。検査後に状態を DONE に更新する。
    """
    try:
        result = _check_repo(repo_path, github_username)
        _accumulate_result(result, enable_pull)
    except Exception:
        pass
    finally:
        with _state_lock:
            _repo_states[repo_name] = REPO_STATE_DONE


def start_local_repo_monitoring(config: dict, github_username: str) -> None:
    """アプリ起動時に全リポジトリ検査をバックグラウンドで開始する。

    1回のみ実行される。メインループをブロックしない。
    検査結果は次のintervalで display_pending_local_repo_results() により表示される。

    Args:
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    global _startup_started
    with _state_lock:
        if _startup_started:
            return
        _startup_started = True

    t = threading.Thread(
        target=_background_startup_check,
        args=(config, github_username),
        daemon=True,
    )
    t.start()


def notify_phase3_detected(repo_name: str, config: dict, github_username: str) -> None:
    """phase3を検知したリポジトリのpullable検査をバックグラウンドで開始する。

    既に検査中・待機中のリポジトリは重複して開始しない。
    検査結果は次のintervalで display_pending_local_repo_results() により表示される。

    Args:
        repo_name: GitHub リポジトリ名（ローカルディレクトリ名と一致）。
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    with _state_lock:
        current_state = _repo_states.get(repo_name)
        if current_state in (REPO_STATE_STARTUP_CHECKING, REPO_STATE_NEEDS_CHECK, REPO_STATE_CHECKING, REPO_STATE_DONE):
            return  # 既に検査済み・検査中または待機中
        _repo_states[repo_name] = REPO_STATE_NEEDS_CHECK

    base_dir = _get_base_dir(config)
    if base_dir is None:
        with _state_lock:
            _repo_states[repo_name] = REPO_STATE_DONE
        return

    repo_path = str(base_dir / repo_name)
    if not Path(repo_path).is_dir():
        with _state_lock:
            _repo_states[repo_name] = REPO_STATE_DONE
        return

    enable_pull = config.get("auto_git_pull", False)

    with _state_lock:
        _repo_states[repo_name] = REPO_STATE_CHECKING

    t = threading.Thread(
        target=_background_single_repo_check,
        args=(repo_path, repo_name, github_username, enable_pull),
        daemon=True,
    )
    t.start()


def display_pending_local_repo_results() -> None:
    """バックグラウンド検査の蓄積結果を表示し、クリアする。

    メインループの各イテレーションで呼び出す。
    表示するものがなければ何も出力しない。
    自己更新（REPO_ROOT の pull 完了）が検出された場合はアプリを再起動する。
    """
    global _pending_needs_restart

    with _state_lock:
        lines = list(_pending_lines)
        _pending_lines.clear()
        needs_restart = _pending_needs_restart
        _pending_needs_restart = False

    if not lines:
        return

    print(f"\n{'=' * 50}")
    print("ローカルリポジトリ状態:")
    print(f"{'=' * 50}")
    for line in lines:
        print(line)

    if needs_restart:
        restart_application()

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
2cbe5bb Merge pull request #409 from cat2151/copilot/refactor-main-py-for-orchestration
3a933be Address review comments: fix comment, add missing mocks for get_current_user/pages/local-repo
d3e887a Refactor main.py into thin orchestration layer (iteration_runner, determine_current_interval)
3873011 Initial plan
2fe17ec Merge pull request #407 from cat2151/copilot/refactor-large-file-in-main-py
434cdd4 fix: pr_processor.pyのインポートをsiblingインポートに修正
f23fa0f リファクタリング: main.pyを532行→470行に削減 (error_logger.py, pr_processor.py分離)
f7e50e2 Initial plan
f3c1aaf Update project summaries (overview & development status) [auto]
ce7295e Merge pull request #405 from cat2151/copilot/evaluate-window-close-confusion

### 変更されたファイル:
generated-docs/development-status-generated-prompt.md
generated-docs/development-status.md
generated-docs/project-overview-generated-prompt.md
generated-docs/project-overview.md
src/gh_pr_phase_monitor/__init__.py
src/gh_pr_phase_monitor/actions/pr_actions.py
src/gh_pr_phase_monitor/browser/browser_automation.py
src/gh_pr_phase_monitor/github/github_client.py
src/gh_pr_phase_monitor/github/pr_fetcher.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/monitor/error_logger.py
src/gh_pr_phase_monitor/monitor/iteration_runner.py
src/gh_pr_phase_monitor/monitor/monitor.py
src/gh_pr_phase_monitor/monitor/pr_processor.py
src/gh_pr_phase_monitor/monitor/snapshot_markdown.py
src/gh_pr_phase_monitor/phase/html/html_status_processor.py
src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py
src/gh_pr_phase_monitor/ui/wait_handler.py
tests/test_check_process_before_autoraise.py
tests/test_error_logging.py
tests/test_html_status_processor.py
tests/test_pr_html_analyzer.py
tests/test_show_issues_when_pr_count_less_than_3.py
tests/test_skip_pr_check_html_refetch.py


---
Generated at: 2026-03-10 07:03:29 JST
