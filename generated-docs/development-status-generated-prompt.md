Last updated: 2026-03-19

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
- src/gh_pr_phase_monitor/browser/issue_assigner.py
- src/gh_pr_phase_monitor/browser/window_manager.py
- src/gh_pr_phase_monitor/core/__init__.py
- src/gh_pr_phase_monitor/core/colors.py
- src/gh_pr_phase_monitor/core/config.py
- src/gh_pr_phase_monitor/core/config_printer.py
- src/gh_pr_phase_monitor/core/config_ruleset.py
- src/gh_pr_phase_monitor/core/interval_parser.py
- src/gh_pr_phase_monitor/core/process_utils.py
- src/gh_pr_phase_monitor/core/time_utils.py
- src/gh_pr_phase_monitor/github/__init__.py
- src/gh_pr_phase_monitor/github/comment_fetcher.py
- src/gh_pr_phase_monitor/github/comment_manager.py
- src/gh_pr_phase_monitor/github/etag_checker.py
- src/gh_pr_phase_monitor/github/github_auth.py
- src/gh_pr_phase_monitor/github/github_client.py
- src/gh_pr_phase_monitor/github/graphql_client.py
- src/gh_pr_phase_monitor/github/issue_etag_checker.py
- src/gh_pr_phase_monitor/github/issue_fetcher.py
- src/gh_pr_phase_monitor/github/pr_fetcher.py
- src/gh_pr_phase_monitor/github/rate_limit_handler.py
- src/gh_pr_phase_monitor/github/repository_fetcher.py
- src/gh_pr_phase_monitor/main.py
- src/gh_pr_phase_monitor/monitor/__init__.py
- src/gh_pr_phase_monitor/monitor/auto_updater.py
- src/gh_pr_phase_monitor/monitor/error_logger.py
- src/gh_pr_phase_monitor/monitor/iteration_runner.py
- src/gh_pr_phase_monitor/monitor/local_repo_cargo.py
- src/gh_pr_phase_monitor/monitor/local_repo_checker.py
- src/gh_pr_phase_monitor/monitor/local_repo_git.py
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
- tests/test_etag_checker.py
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
- tests/test_issue_etag_checker.py
- tests/test_issue_fetching.py
- tests/test_llm_status_timestamp.py
- tests/test_llm_working_warning.py
- tests/test_local_repo_cargo.py
- tests/test_local_repo_checker.py
- tests/test_local_repo_git.py
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
## [Issue #426](../issue-notes/426.md): 大きなファイルの検出: 1個のファイルが500行を超えています
以下のファイルが500行を超えています。リファクタリングを検討してください。

## 検出されたファイル

| ファイル | 行数 | 超過行数 |
|---------|------|----------|
| `tests/test_no_open_prs_issue_display.py` | 519 | +19 |

## テスト実施のお願い

- リファクタリング前後にテストを実行し、それぞれのテスト失敗件数を報告してください
- リファクタリング前後のどちらかでテストがredの場合、まず別issueでtest greenにしてからリファクタリングしてください

## 推奨事項

1...
ラベル: refactoring, code-quality, automated
--- issue-notes/426.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/26.md
```md
{% raw %}
# issue userによるcommitがなくなって24時間超経過しているのに、毎日ムダにproject summaryとcallgraphの自動生成が行われてしまっている #26
[issues #26](https://github.com/cat2151/github-actions/issues/26)

# どうする？
- logを確認する。24時間チェックがバグっている想定。
- もしlogから判別できない場合は、logを改善する。

# log確認結果
- botによるcommitなのに、user commitとして誤判別されている
```
Checking for user commits in the last 24 hours...
User commits found: true
Recent user commits:
7654bf7 Update callgraph.html [auto]
abd2f2d Update project summaries (overview & development status)
```

# ざっくり調査結果
- #27 が判明した

# どうする？
- [x] #27 を修正する。これで自動的に #26 も修正される想定。
    - 当該処理を修正する。
    - もしデータ不足なら、より詳細なlog生成を実装する。
- 別件として、このチェックはむしろworkflow ymlの先頭で行うのが適切と考える。なぜなら、以降のムダな処理をカットできるのでエコ。
    - [x] #28 を起票したので、そちらで実施する。

# close条件は？
- 前提
    - [x] 先行タスクである #27 と #28 が完了済みであること
- 誤爆がなくなること。
    - つまり、userによるcommitがなくなって24時間超経過後の日次バッチにて、
        - ムダなdevelopment status生成、等がないこと
        - jobのlogに「commitがないので処理しません」的なmessageが出ること
- どうする？
    - 日次バッチを本番を流して本番testする

# 結果
- github-actions logより：
    - 直近24hのcommitはbotによる1件のみであった
    - よって後続jobはskipとなった
    - ことを確認した
- close条件を満たした、と判断する
```
Run node .github_automation/check_recent_human_commit/scripts/check-recent-human-commit.cjs
BOT: Commit 5897f0c6df6bc2489f9ce3579b4f351754ee0551 | Author: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com> | Message: Update project summaries (overview & development status) [auto]
has_recent_human_commit=false
```

# closeとする

{% endraw %}
```

### src/gh_pr_phase_monitor/ui/display.py
```py
{% raw %}
"""
Display and UI functions for status summary and issues
"""

import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.colors import colorize_phase, colorize_url
from ..core.config import (
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_assign_to_copilot_config,
    resolve_execution_config_for_repo,
)
from ..core.time_utils import format_elapsed_time
from ..github import github_client
from ..github.github_client import assign_issue_to_copilot, get_issues_from_repositories
from ..github.issue_etag_checker import check_issues_etag_changed
from ..monitor.state_tracker import cleanup_old_pr_states, get_pr_state_time, set_pr_state_time
from ..phase.html.llm_status_extractor import get_latest_activity_timestamp
from ..phase.phase_detector import PHASE_LLM_WORKING, get_llm_working_progress_label, is_llm_working

# Module-level cache for the most recently fetched top issues
_cached_top_issues: List[Dict[str, Any]] = []


def display_cached_top_issues() -> None:
    """Display top issues from the in-memory cache without making any API calls.

    This is used when no repository changes are detected (skip_pr_check=True) to show
    the last-known issue list without consuming API tokens.
    """
    if not _cached_top_issues:
        return
    print(f"\n{'=' * 50}")
    print(f"  Top {len(_cached_top_issues)} issues (sorted by last update, descending, from cache):\n")
    for idx, issue in enumerate(_cached_top_issues, 1):
        print(f"  {idx}. #{issue['number']}: {issue['title']}")
        print(f"     URL: {colorize_url(issue['url'])}")
        print()


def display_status_summary(
    all_prs: List[Dict[str, Any]],
    repos_with_prs: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
    no_change: bool = False,
) -> None:
    """Display a concise summary of current PR status

    This summary helps users understand the overall status at a glance,
    especially useful on terminals with limited display lines.
    Uses the same format as process_pr() for consistency.

    Args:
        all_prs: List of all PRs. Each PR dict must have pr["phase"] set to its computed phase.
        repos_with_prs: List of repositories with open PRs
        config: Optional configuration dict (uses display_pr_author when true)
        no_change: When True, indicates PR check was skipped because no changes were
                   detected; a note is appended to indicate no change since last check
    """
    print(f"\n{'=' * 50}")
    print("Status Summary:")
    print(f"{'=' * 50}")

    if not all_prs:
        print("  No open PRs to monitor")
        cleanup_old_pr_states([])
        return

    current_time = time.time()
    current_states = []

    # Display each PR using the same format as process_pr()
    display_pr_author = bool((config or {}).get("display_pr_author", False))
    for pr in all_prs:
        phase = pr.get("phase", PHASE_LLM_WORKING)
        repo_info = pr.get("repository", {})
        repo_name = repo_info.get("name", "Unknown")
        title = pr.get("title", "Unknown")
        url = pr.get("url", "")
        author_login = (pr.get("author") or {}).get("login", "") or "Unknown"

        # Track state for elapsed time
        state_key = (url, phase)
        current_states.append(state_key)
        if get_pr_state_time(url, phase) is None:
            set_pr_state_time(url, phase, current_time)

        # Calculate elapsed time
        elapsed = current_time - get_pr_state_time(url, phase)

        # Display phase/status with colors using the same format as process_pr()
        html_status = pr.get("html_status")
        llm_statuses = pr.get("llm_statuses") or []
        if html_status:
            # 1A~3Aのstatusを直接表示する（HTMLによるstatus判定機能モード）
            phase_display = colorize_phase(html_status)
            status_suffix = f" (Latest LLM status: {llm_statuses[-1]})" if llm_statuses else ""
        else:
            # フォールバック: 従来のphaseベースの表示
            progress_label = get_llm_working_progress_label(pr) if phase == PHASE_LLM_WORKING else None
            phase_display = colorize_phase(phase, progress_label)
            status_suffix = f" (Latest LLM status: {llm_statuses[-1]})" if phase == PHASE_LLM_WORKING and llm_statuses else ""
        author_suffix = f" (Author: {author_login})" if display_pr_author else ""
        base_line = f"  [{repo_name}] {phase_display}{status_suffix} {title}{author_suffix}"

        # Show elapsed time if state has persisted for more than 60 seconds
        if elapsed >= 60:
            elapsed_str = format_elapsed_time(elapsed)
            print(f"{base_line} (現在、検知してから{elapsed_str}経過)")
        else:
            print(base_line)
        print(f"    URL: {colorize_url(url)}")

        # Show warning for LLM working PRs where the session appears stuck.
        # Primary check: if any LLM status entry carries an embedded timestamp,
        # use the most recent one as the "session last active" time and warn when
        # it is >= 1 hour old.  This prevents false alerts when Copilot recently
        # restarted — even if the PR was created long ago — and covers all event
        # types (started work, started reviewing, finished work, etc.).
        # Fallback: when no parseable timestamp exists in any status entry, use
        # the PR's createdAt field with the original 30-minute threshold.
        if is_llm_working(pr):
            latest_activity_ts = get_latest_activity_timestamp(llm_statuses)
            if latest_activity_ts is not None:
                if current_time - latest_activity_ts >= 3600:
                    print(
                        "    ⚠️  バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります。"
                        "PRを人力で開いてチェックしてください"
                    )
            else:
                created_at = pr.get("createdAt", "")
                if created_at:
                    try:
                        # GitHub API returns ISO 8601 UTC timestamps ending with "Z"
                        # e.g. "2024-01-15T10:30:00Z"; replace Z with +00:00 for fromisoformat()
                        created_ts = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
                        if current_time - created_ts >= 1800:
                            print(
                                "    ⚠️  バグって、実はLLMがwork finishedなのに、workingと判定されている可能性があります。"
                                "PRを人力で開いてチェックしてください"
                            )
                    except (ValueError, AttributeError):
                        pass

    # Clean up old PR states that are no longer present
    cleanup_old_pr_states(current_states)

    if no_change:
        print("  （前回から変化なし）")


def _resolve_assign_to_copilot_config(issue: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve assign_to_copilot configuration for a specific issue's repository

    Args:
        issue: Issue dictionary with repository information
        config: Global configuration dictionary (can be None)

    Returns:
        Configuration dictionary with assign_to_copilot settings
    """
    # Handle None config
    if config is None:
        return {"assign_to_copilot": {}}

    # Get repository-specific configuration
    repo_info = issue.get("repository", {})
    repo_owner = repo_info.get("owner", "")
    repo_name = repo_info.get("name", "")

    if repo_owner and repo_name:
        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
        # Check if any assignment flag is enabled for this repo
        if (
            exec_config.get("assign_good_first_old", False)
            or exec_config.get("assign_old", False)
            or exec_config.get("assign_ci_failure_old", False)
            or exec_config.get("assign_deploy_pages_failure_old", False)
        ):
            # Assignment enabled for this repo, use global assign_to_copilot settings with defaults
            return {"assign_to_copilot": get_assign_to_copilot_config(config)}
        else:
            # No assignment flags enabled
            return {"assign_to_copilot": {}}
    else:
        return {"assign_to_copilot": {}}


def display_issues_from_repos_without_prs(config: Optional[Dict[str, Any]] = None, llm_working_count: int = 0):
    """Display issues from repositories with no open PRs

    Args:
        config: Configuration dictionary (optional)
        llm_working_count: Number of PRs currently in "LLM working" state (default: 0)
    """
    print("Checking for repositories with no open PRs but with open issues...")

    try:
        repos_with_issues = github_client.get_repositories_with_no_prs_and_open_issues()

        if not repos_with_issues:
            print("  No repositories found with open issues and no open PRs")
        else:
            print(f"  Found {len(repos_with_issues)} repositories with open issues (no open PRs):")
            for repo in repos_with_issues:
                print(f"    - {repo['name']}: {repo['openIssueCount']} open issue(s)")

            # Fetch top issues early to detect assigned work and reuse for display
            issue_limit = config.get("issue_display_limit", 10) if config else 10

            # ETag pre-check: skip GraphQL if no issues changed (HTTP 304 Not Modified)
            etag_result = check_issues_etag_changed(repos_with_issues)
            if etag_result is False:
                print("  ETag: 全リポジトリ 304 Not Modified → issue変化なし (GraphQL スキップ)")
                # Filter cache to exclude repos that have gained open PRs since the last fetch.
                # repos_with_issues only contains repos with openPRCount == 0, so any cached
                # issue whose repo is no longer in this list means that repo now has a PR.
                valid_repo_keys = {(r.get("owner", ""), r.get("name", "")) for r in repos_with_issues}
                filtered = [
                    i for i in _cached_top_issues
                    if (i.get("repository", {}).get("owner", ""), i.get("repository", {}).get("name", ""))
                    in valid_repo_keys
                ]
                if len(filtered) != len(_cached_top_issues):
                    _cached_top_issues.clear()
                    _cached_top_issues.extend(filtered)
                display_cached_top_issues()
                return

            top_issues = get_issues_from_repositories(repos_with_issues, limit=issue_limit)

            # Cache the fetched issues so they can be displayed without re-fetching on no-change iterations
            _cached_top_issues.clear()
            _cached_top_issues.extend(top_issues)

            assigned_issue_count = sum(1 for issue in top_issues if issue.get("assignees"))
            effective_llm_working_count = llm_working_count + assigned_issue_count

            if assigned_issue_count:
                print(f"  Detected {assigned_issue_count} open issue(s) with assignees; treating as LLM working load.")

            # Check if auto-assign feature is enabled in config
            # With the new design:
            # - Rulesets can specify "assign_good_first_old" to assign one old "good first issue" (oldest by issue number)
            # - Rulesets can specify "assign_ci_failure_old" to assign one old "ci-failure" issue (oldest by issue number)
            # - Rulesets can specify "assign_deploy_pages_failure_old" to assign one old "deploy-pages-failure" issue (oldest by issue number)
            # - Rulesets can specify "assign_old" to assign one old issue (oldest by issue number, any issue)
            # - All default to false
            # - Priority: ci-failure > deploy-pages-failure > good first issue > old issue

            # Check if any repository has auto-assign enabled
            # We need to check all repos to determine which mode to use
            # Also filter repos to only those with assignment properly enabled
            any_ci_failure = False
            any_deploy_pages_failure = False
            any_good_first = False
            any_old = False
            repos_with_ci_failure_enabled = []
            repos_with_deploy_pages_failure_enabled = []
            repos_with_good_first_enabled = []
            repos_with_old_enabled = []

            # Only check for assign flags if config is not None
            if config:
                for repo in repos_with_issues:
                    repo_owner = repo.get("owner", "")
                    repo_name = repo.get("name", "")
                    if repo_owner and repo_name:
                        exec_config = resolve_execution_config_for_repo(config, repo_owner, repo_name)
                        # Check if any assignment flag is enabled
                        if exec_config.get("assign_ci_failure_old", False):
                            any_ci_failure = True
                            repos_with_ci_failure_enabled.append(repo)
                        if exec_config.get("assign_deploy_pages_failure_old", False):
                            any_deploy_pages_failure = True
                            repos_with_deploy_pages_failure_enabled.append(repo)
                        if exec_config.get("assign_good_first_old", False):
                            any_good_first = True
                            repos_with_good_first_enabled.append(repo)
                        if exec_config.get("assign_old", False):
                            any_old = True
                            repos_with_old_enabled.append(repo)

            # Check if we should pause auto-assignment due to too many LLM working PRs
            # Get max_llm_working_parallel setting from config (default: 3)
            max_llm_working = DEFAULT_MAX_LLM_WORKING_PARALLEL
            if config:
                max_llm_working = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)

            # Check if we should pause auto-assignment
            should_pause_assignment = effective_llm_working_count >= max_llm_working

            if should_pause_assignment:
                print(f"\n{'=' * 50}")
                print(f"LLM workingのPR数が最大並列数（{max_llm_working}）に達しています。")
                print(
                    "現在のLLM workingカウント: "
                    f"{effective_llm_working_count} (PR: {llm_working_count}, assigned issues: {assigned_issue_count})"
                )
                print("レートリミット回避のため、新しいissueの自動assignを保留します。")
                print(f"{'=' * 50}")
                # Skip assignment but continue to display issues
            else:
                # Always try to check for issues to assign (batteries-included)
                # Individual repositories must explicitly enable via rulesets for actual assignment
                # Priority: ci-failure > deploy-pages-failure > good first issue > old issue (all sorted by issue number ascending)
                assignment_modes = [
                    ("ci-failure", repos_with_ci_failure_enabled, ["ci-failure"], any_ci_failure),
                    (
                        "deploy-pages-failure",
                        repos_with_deploy_pages_failure_enabled,
                        ["deploy-pages-failure"],
                        any_deploy_pages_failure,
                    ),
                    ("good first issue", repos_with_good_first_enabled, ["good first issue"], any_good_first),
                    ("issue", repos_with_old_enabled, None, any_old),
                ]

                for label_name, repos_list, label_filter, is_enabled in assignment_modes:
                    if not is_enabled:
                        continue

                    print(f"\n{'=' * 50}")
                    print(f"Checking for the oldest '{label_name}' to auto-assign to Copilot...")
                    print(f"{'=' * 50}")

                    query_kwargs = {"limit": 1, "sort_by_number": True}
                    if label_filter:
                        query_kwargs["labels"] = label_filter

                    candidate_issues = get_issues_from_repositories(repos_list, **query_kwargs)

                    if candidate_issues:
                        issue = candidate_issues[0]
                        print(f"\n  Found oldest '{label_name}' (sorted by issue number, ascending):")
                        print(f"  #{issue['number']}: {issue['title']}")
                        print(f"     URL: {colorize_url(issue['url'])}")
                        labels = issue.get("labels", [])
                        label_str = ", ".join(str(label) for label in labels)
                        print(f"     Labels: {label_str}")
                        print("\n  Attempting to assign to Copilot...")

                        temp_config = _resolve_assign_to_copilot_config(issue, config)
                        success = assign_issue_to_copilot(issue, temp_config)
                        if not success:
                            print("  Assignment failed - will retry on next iteration")
                        break
                    else:
                        if label_name == "issue":
                            print("  No issues found in repositories without open PRs")
                        else:
                            print(f"  No '{label_name}' issues found in repositories without open PRs")

            # Then, show top N issues from these repositories
            print(f"\n{'=' * 50}")
            print(f"Fetching top {issue_limit} issues from these repositories...")
            print(f"{'=' * 50}")

            if not top_issues:
                print("  No issues found")
            else:
                print(f"\n  Top {len(top_issues)} issues (sorted by last update, descending):\n")
                for idx, issue in enumerate(top_issues, 1):
                    print(f"  {idx}. #{issue['number']}: {issue['title']}")
                    print(f"     URL: {colorize_url(issue['url'])}")
                    print()
    except Exception as e:
        print(f"  Error fetching issues: {e}")
        traceback.print_exc()

{% endraw %}
```

### tests/test_no_open_prs_issue_display.py
```py
{% raw %}
"""
Test to verify that issues are displayed when no repositories with open PRs are found

This test ensures the new behavior requested in the issue:
"Add the condition 'No repositories with open PRs found' to the conditions for displaying the latest issue."
"""


from src.gh_pr_phase_monitor.core.colors import colorize_url
from src.gh_pr_phase_monitor.ui.display import display_issues_from_repos_without_prs


def test_issue_url_is_colorized(mocker, capsys):
    """Issue URLs should be colorized for easier clicking"""
    url = "https://github.com/testuser/test-repo/issues/1"
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 1,
        }
    ]
    mock_get_issues.return_value = [
        {
            "title": "Issue 1",
            "url": url,
            "number": 1,
        }
    ]

    display_issues_from_repos_without_prs(None)

    colored_url = colorize_url(url)
    output = capsys.readouterr().out
    assert colored_url in output


def test_display_issues_when_no_repos_with_prs(mocker):
    """
    Test that display_issues_from_repos_without_prs correctly displays issues
    when there are no repositories with open PRs
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_assign = mocker.patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 2,
        }
    ]

    # Mock good first issue response
    mock_get_issues.side_effect = [
        # First call: top 10 issues (used for detection/display)
        [
            {
                "title": "Issue 1",
                "url": "https://github.com/testuser/test-repo/issues/1",
                "number": 1,
                "updatedAt": "2024-01-01T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
            {
                "title": "Issue 2",
                "url": "https://github.com/testuser/test-repo/issues/2",
                "number": 2,
                "updatedAt": "2024-01-02T00:00:00Z",
                "author": {"login": "contributor2"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
        ],
        # Second call: good first issue for assignment
        [
            {
                "title": "Good first issue",
                "url": "https://github.com/testuser/test-repo/issues/1",
                "number": 1,
                "updatedAt": "2024-01-01T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
                "labels": ["good first issue"],
            }
        ],
    ]

    mock_assign.return_value = True

    # Create config with assign_to_copilot enabled via rulesets
    config = {
        "assign_to_copilot": {},  # Empty section provides defaults
        "rulesets": [
            {
                "repositories": ["test-repo"],
                "assign_good_first_old": True,  # Enable good first issue assignment
            }
        ],
    }

    # Call the function with config
    display_issues_from_repos_without_prs(config)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched twice (good first issue + top 10)
    assert mock_get_issues.call_count == 2

    # Verify first call was for top issues (used for detection/display)
    first_call = mock_get_issues.call_args_list[0]
    assert first_call[1]["limit"] == 10

    # Verify second call was for good first issue assignment (with sort_by_number=True)
    second_call = mock_get_issues.call_args_list[1]
    assert second_call[1]["limit"] == 1
    assert second_call[1]["labels"] == ["good first issue"]
    assert second_call[1]["sort_by_number"] is True

    # Verify assignment was attempted
    mock_assign.assert_called_once()


def test_display_issues_when_no_repos_with_issues(mocker):
    """
    Test that display_issues_from_repos_without_prs handles the case
    when there are no repositories with issues
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    # Mock response: no repos with issues
    mock_get_repos.return_value = []

    # Call the function with empty config - should not raise an error
    display_issues_from_repos_without_prs({})

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()


def test_display_issues_handles_exceptions(mocker):
    """
    Test that display_issues_from_repos_without_prs handles exceptions gracefully
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    # Mock an exception
    mock_get_repos.side_effect = Exception("API Error")

    # Call the function with empty config - should not raise an error
    display_issues_from_repos_without_prs({})

    # Verify that the function attempted to fetch repos
    mock_get_repos.assert_called_once()


def test_display_issues_with_assign_disabled(mocker):
    """
    Test that display_issues_from_repos_without_prs does NOT attempt assignment
    when the feature is disabled
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_assign = mocker.patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 2,
        }
    ]

    # Mock issue responses - only one call now for displaying issues
    mock_get_issues.side_effect = [
        # Only call for top 10 issues
        [
            {
                "title": "Issue 1",
                "url": "https://github.com/testuser/test-repo/issues/1",
                "number": 1,
                "updatedAt": "2024-01-01T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
        ],
    ]

    # Create config without rulesets enabling assign flags
    config = {"assign_to_copilot": {}}  # Defaults available, but no ruleset enables it

    # Call the function with config
    display_issues_from_repos_without_prs(config)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched only once (top 10), no assign attempt
    assert mock_get_issues.call_count == 1

    # Verify assignment was NOT attempted (no ruleset enabling it)
    mock_assign.assert_not_called()


def test_display_issues_with_custom_limit(mocker):
    """
    Test that display_issues_from_repos_without_prs respects the issue_display_limit config
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 10,
        }
    ]

    # Mock issue response - only display issues call
    mock_get_issues.side_effect = [
        # Only call: top N issues with custom limit
        [
            {
                "title": f"Issue {i}",
                "url": f"https://github.com/testuser/test-repo/issues/{i}",
                "number": i,
                "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            }
            for i in range(1, 6)
        ],
    ]

    # Create config with custom issue_display_limit, no assign flags
    config = {"assign_to_copilot": {}, "issue_display_limit": 5}

    # Call the function with config
    display_issues_from_repos_without_prs(config)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched once (top N only, no auto-assign)
    assert mock_get_issues.call_count == 1
    # Check the call used the custom limit
    call = mock_get_issues.call_args_list[0]
    assert call[1]["limit"] == 5


def test_display_issues_with_none_config(mocker):
    """
    Test that display_issues_from_repos_without_prs handles None config gracefully
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 10,
        }
    ]

    # Mock issue response - only display issues
    mock_get_issues.side_effect = [
        # Only call: top 10 issues
        [
            {
                "title": f"Issue {i}",
                "url": f"https://github.com/testuser/test-repo/issues/{i}",
                "number": i,
                "updatedAt": f"2024-01-{i:02d}T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            }
            for i in range(1, 11)
        ],
    ]

    # Call the function with None config - should use default limit of 10
    display_issues_from_repos_without_prs(None)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched once (top 10 only, no assign)
    assert mock_get_issues.call_count == 1
    # Check the call used the default limit of 10
    call = mock_get_issues.call_args_list[0]
    assert call[1]["limit"] == 10


def test_display_issues_with_assign_lowest_number(mocker):
    """
    Test that display_issues_from_repos_without_prs correctly assigns the oldest issue
    when assign_old is enabled (replaces assign_lowest_number_issue)
    """
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_assign = mocker.patch("src.gh_pr_phase_monitor.ui.display.assign_issue_to_copilot")
    # Mock response: repos with no PRs but with issues
    mock_get_repos.return_value = [
        {
            "name": "test-repo",
            "owner": "testuser",
            "openIssueCount": 3,
        }
    ]

    # Mock lowest number issue response
    mock_get_issues.side_effect = [
        # First call: top 10 issues for display/detection
        [
            {
                "title": "Issue 1",
                "url": "https://github.com/testuser/test-repo/issues/5",
                "number": 5,
                "updatedAt": "2024-01-05T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
            {
                "title": "Issue 2",
                "url": "https://github.com/testuser/test-repo/issues/10",
                "number": 10,
                "updatedAt": "2024-01-10T00:00:00Z",
                "author": {"login": "contributor2"},
                "repository": {"owner": "testuser", "name": "test-repo"},
            },
        ],
        # Second call: oldest issue
        [
            {
                "title": "Issue with lowest number",
                "url": "https://github.com/testuser/test-repo/issues/5",
                "number": 5,
                "updatedAt": "2024-01-05T00:00:00Z",
                "author": {"login": "contributor1"},
                "repository": {"owner": "testuser", "name": "test-repo"},
                "labels": ["bug"],
            }
        ],
    ]

    mock_assign.return_value = True

    # Create config with assign_old enabled in rulesets
    config = {
        "assign_to_copilot": {},
        "rulesets": [
            {
                "repositories": ["test-repo"],
                "assign_old": True,  # Enable old issue assignment
            }
        ],
    }

    # Call the function with config
    display_issues_from_repos_without_prs(config)

    # Verify that the function fetched repos without PRs
    mock_get_repos.assert_called_once()

    # Verify that issues were fetched twice (oldest issue + top 10)
    assert mock_get_issues.call_count == 2

    # Verify first call was for top issues (display/detection)
    first_call = mock_get_issues.call_args_list[0]
    assert first_call[1]["limit"] == 10

    # Verify second call was for oldest issue (with sort_by_number=True, no labels)
    second_call = mock_get_issues.call_args_list[1]
    assert second_call[1]["limit"] == 1
    assert second_call[1]["sort_by_number"] is True
    # Should not have labels filter for oldest issue mode
    assert "labels" not in second_call[1] or second_call[1]["labels"] is None

    # Verify assignment was attempted
    mock_assign.assert_called_once()


def test_display_cached_top_issues_empty(mocker, capsys):
    """display_cached_top_issues outputs nothing when cache is empty"""
    import src.gh_pr_phase_monitor.ui.display as display_module

    mocker.patch.object(display_module, "_cached_top_issues", [])
    from src.gh_pr_phase_monitor.ui.display import display_cached_top_issues
    display_cached_top_issues()
    out = capsys.readouterr().out
    assert out == ""


def test_display_cached_top_issues_shows_cached_data(mocker, capsys):
    """display_cached_top_issues displays the cached issues without calling get_issues_from_repositories"""
    import src.gh_pr_phase_monitor.ui.display as display_module

    mocker.patch.object(display_module, "_cached_top_issues", [
        {
            "title": "Cached Issue 1",
            "url": "https://github.com/testuser/test-repo/issues/10",
            "number": 10,
        },
        {
            "title": "Cached Issue 2",
            "url": "https://github.com/testuser/test-repo/issues/20",
            "number": 20,
        },
    ])
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    from src.gh_pr_phase_monitor.ui.display import display_cached_top_issues
    display_cached_top_issues()
    out = capsys.readouterr().out
    assert "Cached Issue 1" in out
    assert "Cached Issue 2" in out
    assert "#10" in out
    assert "#20" in out
    # Confirm no API calls were made
    mock_get_issues.assert_not_called()


def test_display_issues_populates_cache(mocker):
    """display_issues_from_repos_without_prs populates _cached_top_issues after fetching"""
    import src.gh_pr_phase_monitor.ui.display as display_module

    mocker.patch.object(display_module, "_cached_top_issues", [])
    mock_get_repos = mocker.patch("src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues")
    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")
    mock_get_repos.return_value = [{"name": "test-repo", "owner": "testuser", "openIssueCount": 1}]
    fetched_issues = [
        {"title": "Issue A", "url": "https://github.com/testuser/test-repo/issues/1", "number": 1},
    ]
    mock_get_issues.return_value = fetched_issues
    display_issues_from_repos_without_prs(None)
    assert list(display_module._cached_top_issues) == fetched_issues


def test_etag_304_filters_cache_when_repo_gains_pr(mocker, capsys):
    """Regression: ETag 304 path must not display cached issues from repos that now have open PRs.

    Scenario:
    - Cache contains issues from repo-a (no PR) and repo-b (no PR).
    - A PR is opened for repo-a, so get_repositories_with_no_prs_and_open_issues returns only [repo-b].
    - ETag check returns False (304, no change in repo-b's issues).
    - Expected: only repo-b's issues are shown; repo-a's issues are excluded from the display.
    """
    import src.gh_pr_phase_monitor.ui.display as display_module

    # Pre-populate the cache with issues from two repos (one of which will gain a PR)
    stale_cache = [
        {
            "title": "Issue from repo-a",
            "url": "https://github.com/testuser/repo-a/issues/1",
            "number": 1,
            "repository": {"owner": "testuser", "name": "repo-a"},
        },
        {
            "title": "Issue from repo-b",
            "url": "https://github.com/testuser/repo-b/issues/2",
            "number": 2,
            "repository": {"owner": "testuser", "name": "repo-b"},
        },
    ]
    mocker.patch.object(display_module, "_cached_top_issues", list(stale_cache))

    # repo-a now has a PR → only repo-b is in repos_with_issues
    mock_get_repos = mocker.patch(
        "src.gh_pr_phase_monitor.github.github_client.get_repositories_with_no_prs_and_open_issues"
    )
    mock_get_repos.return_value = [{"name": "repo-b", "owner": "testuser", "openIssueCount": 1}]

    # ETag check returns False (304 — no change in repo-b)
    mock_etag = mocker.patch("src.gh_pr_phase_monitor.ui.display.check_issues_etag_changed")
    mock_etag.return_value = False

    mock_get_issues = mocker.patch("src.gh_pr_phase_monitor.ui.display.get_issues_from_repositories")

    display_issues_from_repos_without_prs(None)

    # 304 path must not make any GraphQL fetch
    mock_get_issues.assert_not_called()

    out = capsys.readouterr().out
    # repo-b's issue should appear
    assert "Issue from repo-b" in out
    # repo-a now has a PR — its cached issue must NOT appear
    assert "Issue from repo-a" not in out
    # Cache should have been updated to remove repo-a's issues and keep repo-b's
    assert all(i.get("repository", {}).get("name") != "repo-a" for i in display_module._cached_top_issues)
    assert any(i.get("repository", {}).get("name") == "repo-b" for i in display_module._cached_top_issues)


if __name__ == "__main__":
    test_display_issues_when_no_repos_with_prs()
    print("✓ Test 1 passed: display_issues_when_no_repos_with_prs")

    test_display_issues_when_no_repos_with_issues()
    print("✓ Test 2 passed: display_issues_when_no_repos_with_issues")

    test_display_issues_handles_exceptions()
    print("✓ Test 3 passed: display_issues_handles_exceptions")

    test_display_issues_with_assign_disabled()
    print("✓ Test 4 passed: display_issues_with_assign_disabled")

    test_display_issues_with_custom_limit()
    print("✓ Test 5 passed: display_issues_with_custom_limit")

    test_display_issues_with_none_config()
    print("✓ Test 6 passed: display_issues_with_none_config")

    test_display_issues_with_assign_lowest_number()
    print("✓ Test 7 passed: display_issues_with_assign_lowest_number")

    print("\n✅ All tests passed!")

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
8d77fec Merge pull request #425 from cat2151/copilot/split-large-source-file
d3554d0 Fix test performance: use _wait_with_cancellation mock; fix docstring
5f84131 Address code review: clarify test mock naming and add comments
ceeb4d2 Split large files per SRP: config_ruleset.py + issue_assigner.py
8b4bb7a Initial plan
37741c9 Merge pull request #423 from cat2151/copilot/fix-regression-in-top-10-issues
24e236c test: assert get_issues_from_repositories not called on ETag 304 path
07651df fix: filter cached issues by current repos-without-PRs in ETag 304 path
5b7759f Initial plan
9cea74f Update project summaries (overview & development status) [auto]

### 変更されたファイル:
README.ja.md
README.md
generated-docs/development-status-generated-prompt.md
generated-docs/development-status.md
generated-docs/project-overview-generated-prompt.md
generated-docs/project-overview.md
src/gh_pr_phase_monitor/actions/pr_actions.py
src/gh_pr_phase_monitor/browser/browser_automation.py
src/gh_pr_phase_monitor/browser/issue_assigner.py
src/gh_pr_phase_monitor/core/config.py
src/gh_pr_phase_monitor/core/config_printer.py
src/gh_pr_phase_monitor/core/config_ruleset.py
src/gh_pr_phase_monitor/github/github_client.py
src/gh_pr_phase_monitor/github/issue_etag_checker.py
src/gh_pr_phase_monitor/monitor/monitor.py
src/gh_pr_phase_monitor/phase/html/html_status_processor.py
src/gh_pr_phase_monitor/ui/display.py
tests/test_browser_automation.py
tests/test_browser_automation_window.py
tests/test_check_process_before_autoraise.py
tests/test_issue_etag_checker.py
tests/test_no_change_timeout.py
tests/test_no_open_prs_issue_display.py


---
Generated at: 2026-03-19 07:04:54 JST
