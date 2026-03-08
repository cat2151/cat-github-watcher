Last updated: 2026-03-09

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
- src/gh_pr_phase_monitor/monitor/local_repo_watcher.py
- src/gh_pr_phase_monitor/monitor/monitor.py
- src/gh_pr_phase_monitor/monitor/pages_watcher.py
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
## [Issue #406](../issue-notes/406.md): 大きなファイルの検出: 1個のファイルが500行を超えています
以下のファイルが500行を超えています。リファクタリングを検討してください。

## 検出されたファイル

| ファイル | 行数 | 超過行数 |
|---------|------|----------|
| `src/gh_pr_phase_monitor/main.py` | 532 | +32 |

## テスト実施のお願い

- リファクタリング前後にテストを実行し、それぞれのテスト失敗件数を報告してください
- リファクタリング前後のどちらかでテストがredの場合、まず別issueでtest greenにしてからリファクタリングしてください

## 推奨事項

1. 単一責任の原...
ラベル: refactoring, code-quality, automated
--- issue-notes/406.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### src/gh_pr_phase_monitor/main.py
```py
{% raw %}
"""
Main execution module for GitHub PR Phase Monitor
"""

import signal
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

from .actions.pr_actions import process_pr
from .core.config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_config_mtime,
    load_config,
    parse_interval,
    print_config,
    validate_phase3_merge_config_required,
)
from .core.time_utils import format_elapsed_time
from .github.github_auth import get_current_user
from .github.github_client import (
    get_pr_details_batch,
    get_repos_changed_since_last_check,
    get_repositories_with_open_prs,
    reset_repos_updated_at_baseline,
)
from .github.graphql_client import GitHubRateLimitError, get_rate_limit_info
from .github.rate_limit_handler import (
    _check_rate_limit_throttle,
    _display_rate_limit_usage,
    _format_rate_limit_reset,
)
from .monitor.auto_updater import (
    UPDATE_CHECK_INTERVAL_SECONDS,
    maybe_self_update,
    run_startup_self_update_foreground,
)
from .monitor.local_repo_watcher import (
    display_pending_local_repo_results,
    notify_phase3_detected,
    start_local_repo_monitoring,
)
from .monitor.monitor import check_no_state_change_timeout
from .monitor.pages_watcher import check_pages_deployments_for_repos, get_pages_repos_from_config
from .monitor.state_tracker import get_last_pr_snapshot, set_last_pr_snapshot
from .phase.html.html_status_processor import fetch_and_analyze_pr_html
from .phase.phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase, is_llm_working
from .ui.display import display_cached_top_issues, display_issues_from_repos_without_prs, display_status_summary
from .ui.wait_handler import wait_with_countdown

LOG_DIR = Path("logs")


def log_error_to_file(message: str, exc: Exception | None = None, base_dir: Path | str | None = None) -> None:
    """Append an error entry to logs/error.log without interrupting execution"""
    try:
        log_dir = Path(base_dir) if base_dir else LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception:
        # Avoid any logging-related failures impacting the main loop
        pass


def _process_open_prs(
    all_prs: list,
    phase3_repo_names: list,
    config: dict,
) -> None:
    """HTML取得・phase判定・PR処理を全openなPRに対して実行する。

    all_prs の各PRに対して fetch_and_analyze_pr_html → determine_phase → process_pr を実行し、
    結果を pr["phase"] に書き込み、phase3_repo_names に追記する。
    """
    for pr in all_prs:
        try:
            # HTMLを取得・解析・保存（メインフロー: phaseに関わらず全PRに対して実行）
            try:
                fetch_and_analyze_pr_html(pr)
            except Exception as html_error:
                print(f"    Failed to fetch/analyze HTML for PR: {html_error}")
                log_error_to_file(
                    f"Failed to fetch/analyze HTML for {pr.get('url', 'unknown')}",
                    html_error,
                )

            # pr["llm_statuses"] が更新された後にphaseを判定する
            phase = determine_phase(pr)

            pr["phase"] = phase
            process_pr(pr, config, phase)

            # phase3検知時: 該当リポジトリをpullable検査の対象に登録
            if phase == PHASE_3:
                repo_name = pr.get("repository", {}).get("name", "")
                if repo_name and repo_name not in phase3_repo_names:
                    phase3_repo_names.append(repo_name)
        except Exception as pr_error:
            log_error_to_file(
                f"Failed to process PR {pr.get('url', 'unknown') or pr.get('title', 'unknown')}",
                pr_error,
            )
            pr["phase"] = PHASE_LLM_WORKING


def main():
    """Main execution function"""
    # --fetch-pr-html <URL> オプション: PR HTMLを取得してlogs/pr/に保存して終了
    if len(sys.argv) >= 3 and sys.argv[1] == "--fetch-pr-html":
        from .phase.html.pr_html_saver import save_pr_html

        result = save_pr_html(sys.argv[2])
        sys.exit(0 if result else 1)

    config_path = "config.toml"

    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    # Load config if it exists, otherwise use defaults
    config = {}
    config_mtime = 0.0
    try:
        config = load_config(config_path)
        config_mtime = get_config_mtime(config_path)
    except FileNotFoundError:
        print(f"Warning: Config file '{config_path}' not found, using defaults")
        print("You can create a config.toml file to customize settings")
        print("Expected format:")
        print('interval = "1m"  # Check interval (e.g., "30s", "1m", "5m")')
        print()

    # Get interval
    normal_interval_str = config.get("interval", "1m")
    try:
        normal_interval_seconds = parse_interval(normal_interval_str)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("GitHub PR Phase Monitor")
    print("=" * 50)
    print(f"Monitoring interval: {normal_interval_str} ({normal_interval_seconds} seconds)")
    print("Monitoring all repositories for the current GitHub user")
    print("Press CTRL+C to stop monitoring")
    print("=" * 50)

    # Print configuration if verbose mode is enabled
    if config.get("verbose", False):
        print_config(config)

    # Set up signal handler for graceful interruption
    def signal_handler(_signum, _frame):
        print("\n\nMonitoring interrupted by user (CTRL+C)")
        print("Exiting...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # 起動直後に自己リポジトリのアップデートチェックを実行（常に実行）
    run_startup_self_update_foreground()

    # Infinite monitoring loop
    iteration = 0
    consecutive_failures = 0
    while True:
        iteration += 1

        if config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE):
            try:
                maybe_self_update()
            except Exception as update_error:
                log_error_to_file("Auto-update check failed", update_error)

        print(f"\n{'=' * 50}")
        print(f"Check #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")

        # Capture rate limit before API calls for per-iteration consumption tracking
        try:
            before_rate_limit = get_rate_limit_info()
        except Exception as rate_limit_error:
            log_error_to_file("Failed to fetch pre-iteration rate limit info", rate_limit_error)
            before_rate_limit = None

        # Initialize variables to track status for summary
        all_prs = []
        repos_with_prs = []
        phase3_repo_names: list[str] = []
        skip_pr_check = False

        try:
            # updatedAt pre-check: determine which repos (if any) changed since last iteration.
            # On the first call this stores the baseline and returns None (run full check).
            # On subsequent calls this compares the baseline and returns the set of changed repos.
            # If the set is empty, nothing changed and we can skip Phase 1 + Phase 2 entirely.
            try:
                changed_repos = get_repos_changed_since_last_check()
                if changed_repos is None:
                    print("  updatedAt ベースライン記録済み (初回チェック)")
                elif not changed_repos:
                    print("  リポジトリに変化なし (updatedAt 不変)。Phase 1/2 をスキップします。")
                    skip_pr_check = True
                else:
                    print(f"  {len(changed_repos)} リポジトリで変化を検知 → Phase 1/2 実行")
            except Exception as updated_at_error:
                log_error_to_file("updatedAt check failed, running full check", updated_at_error)

            if not skip_pr_check:
                # Phase 1: Get all repositories with open PRs (lightweight query)
                print("\nPhase 1: Fetching repositories with open PRs...")
                repos_with_prs = get_repositories_with_open_prs()

                if not repos_with_prs:
                    print("  No repositories with open PRs found")
                    # Display issues when no repositories with open PRs are found
                    # No PRs means llm_working_count = 0
                    display_issues_from_repos_without_prs(config, llm_working_count=0)
                else:
                    print(f"  Found {len(repos_with_prs)} repositories with open PRs:")
                    for repo in repos_with_prs:
                        print(f"    - {repo['name']}: {repo['openPRCount']} open PR(s)")

                # Validate phase3_merge configuration for all repositories
                # This must be done before processing PRs to fail fast
                print("\nValidating phase3_merge configuration...")
                for repo in repos_with_prs:
                    repo_owner = repo.get("owner", "")
                    repo_name = repo.get("name", "")
                    if repo_owner and repo_name:
                        validate_phase3_merge_config_required(config, repo_owner, repo_name)

                # Phase 2: Get PR details for repositories with open PRs (detailed query)
                print(f"\nPhase 2: Fetching PR details for {len(repos_with_prs)} repositories...")
                all_prs = get_pr_details_batch(repos_with_prs)

                if not all_prs:
                    print("  No PRs found")
                else:
                    print(f"\n  Found {len(all_prs)} open PR(s) total")
                    print(f"\n{'=' * 50}")
                    print("Processing PRs:")
                    print(f"{'=' * 50}")

                    # Track phases to detect if all PRs are in "LLM working"
                    _process_open_prs(all_prs, phase3_repo_names, config)

                # Save PR snapshot for display on subsequent skip-check iterations.
                # Done after Phase 1/2 (including the empty case) so the cache is always
                # up-to-date and never shows stale PRs when there are actually none.
                set_last_pr_snapshot(all_prs, repos_with_prs)

                if all_prs:
                    # Count how many PRs are in "LLM working" phase
                    # This count is used for rate limit protection - when too many PRs are being
                    # worked on simultaneously, we pause auto-assignment to prevent API rate limits
                    llm_working_count = sum(1 for pr in all_prs if is_llm_working(pr))
                    max_llm_working_parallel = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)
                    llm_working_below_cap = llm_working_count < max_llm_working_parallel

                    # Look for new issues to assign when:
                    # 1. All PRs are in "LLM working" phase (existing work is in progress), OR
                    # 2. PR count is less than 3 (few PRs, so we can look for more work)
                    # The llm_working_count throttles assignment when parallel work is too high
                    total_pr_count = len(all_prs)
                    all_llm_working = bool(all_prs) and all(is_llm_working(pr) for pr in all_prs)
                    all_phase3 = bool(all_prs) and all(pr.get("phase") == PHASE_3 for pr in all_prs)
                    active_parallel_prs = sum(1 for pr in all_prs if pr.get("phase") != PHASE_3)

                    if llm_working_below_cap or all_llm_working or active_parallel_prs < 3:
                        if all_llm_working and total_pr_count >= 3:
                            print(f"\n{'=' * 50}")
                            print("All PRs are in 'LLM working' phase")
                            print(f"{'=' * 50}")
                        elif all_phase3 and total_pr_count >= 3:
                            print(f"\n{'=' * 50}")
                            print("All PRs are in 'phase3' (ready for human review); treating parallel count as 0")
                            print(f"{'=' * 50}")
                        elif llm_working_below_cap:
                            print(f"\n{'=' * 50}")
                            print(
                                f"LLM working PRs below limit: {llm_working_count}/{max_llm_working_parallel} "
                                "(showing available work)"
                            )
                            print(f"{'=' * 50}")
                        elif active_parallel_prs < 3:
                            print(f"\n{'=' * 50}")
                            print(f"Active PR count (excluding phase3) is {active_parallel_prs} (less than 3)")
                            print(f"{'=' * 50}")
                        # Display issues and potentially auto-assign new work
                        # Throttling is applied inside the function based on llm_working_count
                        display_issues_from_repos_without_prs(config, llm_working_count=llm_working_count)

            elif skip_pr_check:
                # updatedAt 不変: GraphQL Phase 1/2 はスキップ
                # しかし、open PR のphase変化（1A→1B, 1B→2A等）を検知するため、HTMLを毎回再取得する
                # (updatedAt はPRのphase変化では更新されないため、HTMLフェッチが必須)
                snapshot = get_last_pr_snapshot()
                if snapshot is not None and snapshot[0]:
                    cached_prs, cached_repos = snapshot

                    # open PR 件数を毎回 GraphQL で再取得し、変化があれば Phase 1/2 を強制実行する
                    # (updatedAt は PR の新規作成を反映しないことがあるため、件数の乖離が生じうる)
                    # リポジトリごとの件数を辞書で比較することで、「1件クローズ+1件新規」のように
                    # 合計が変わらない場合でも変化を検知できる。
                    print("\n  open PR 件数を再確認中 (GraphQL)...")
                    fresh_repos_with_prs = get_repositories_with_open_prs()
                    cached_count_map = {
                        (r.get("owner", ""), r.get("name", "")): r.get("openPRCount", 0) for r in cached_repos
                    }
                    fresh_count_map = {
                        (r.get("owner", ""), r.get("name", "")): r.get("openPRCount", 0)
                        for r in fresh_repos_with_prs
                    }

                    if fresh_count_map != cached_count_map:
                        # リポジトリごとの PR 件数が変化 → Phase 1/2 を強制実行して最新の PR 一覧を取得する
                        print("  open PR 件数/構成が変化。Phase 1/2 を強制実行します。")
                        repos_with_prs = fresh_repos_with_prs

                        # validate phase3_merge configuration (same as normal Phase 1 flow)
                        print("\nValidating phase3_merge configuration...")
                        for repo in repos_with_prs:
                            repo_owner = repo.get("owner", "")
                            repo_name = repo.get("name", "")
                            if repo_owner and repo_name:
                                validate_phase3_merge_config_required(config, repo_owner, repo_name)

                        all_prs = get_pr_details_batch(repos_with_prs)
                        if all_prs:
                            print(f"\n  Found {len(all_prs)} open PR(s) total")
                            _process_open_prs(all_prs, phase3_repo_names, config)
                        set_last_pr_snapshot(all_prs, repos_with_prs)
                    else:
                        # PR 件数は変化なし → HTML のみ再取得 (phase 変化を検知するため)
                        print("\n  open PR のHTML再取得 (updatedAt 不変でもphase変化を検知するため / Refetching HTML for open PRs to detect phase changes)...")
                        all_prs = cached_prs
                        repos_with_prs = cached_repos
                        _process_open_prs(all_prs, phase3_repo_names, config)
                        set_last_pr_snapshot(all_prs, repos_with_prs)

                    # skip_pr_check を False にリセット: 今イテレーションの表示セクション (display_status_summary)
                    # でスナップショットではなく最新のHTML取得結果を使うため
                    skip_pr_check = False
                else:
                    # スナップショット未作成またはPRなし: 次イテレーションでフルチェックを強制する
                    # (updatedAt ベースラインをリセットすることで、次回の get_repos_changed_since_last_check が
                    #  None を返し、通常の Phase 1/2 チェックが実行される)
                    log_error_to_file(
                        "skip_pr_check=True but no cached PR snapshot; resetting updatedAt baseline for full check next iteration",
                        None,
                    )
                    reset_repos_updated_at_baseline()

                # 変化なし: キャッシュからTop 10 issuesを表示 (GraphQLクエリ不要)
                display_cached_top_issues()

            # Check GitHub Pages deployment status for configured repos
            # This runs regardless of whether there are open PRs (covers post-merge case)
            try:
                current_user = get_current_user()
                pages_repos = get_pages_repos_from_config(config, current_user)
                if pages_repos:
                    print(f"\n{'=' * 50}")
                    print("GitHub Pages deployment check:")
                    print(f"{'=' * 50}")
                    check_pages_deployments_for_repos(pages_repos, config)
            except Exception as pages_error:
                log_error_to_file("Failed to check Pages deployment", pages_error)
                current_user = None

            # Local repository pullable check (background-based)
            # 初回イテレーション: 全リポジトリをバックグラウンドで検査開始
            # phase3検知リポジトリ: バックグラウンドでpullable検査をトリガー
            # 蓄積された検査結果を表示（1秒ごとの逐次表示は廃止、次のintervalで一括表示）
            try:
                if current_user is None:
                    current_user = get_current_user()
                if iteration == 1:
                    start_local_repo_monitoring(config, current_user)
                else:
                    for repo_name in phase3_repo_names:
                        notify_phase3_detected(repo_name, config, current_user)
                display_pending_local_repo_results()
            except Exception as local_repo_error:
                log_error_to_file("Failed to check local repos", local_repo_error)

            # Reset consecutive-failure counter on a successful iteration
            consecutive_failures = 0

        except GitHubRateLimitError as e:
            print(f"\nError: {e}")
            rate_limit_info = getattr(e, "rate_limit_info", None)
            if isinstance(rate_limit_info, dict):
                used = rate_limit_info.get("used", "unknown")
                remaining = rate_limit_info.get("remaining", "unknown")
                limit = rate_limit_info.get("limit", "unknown")
                reset = rate_limit_info.get("reset")
                reset_display, reset_in_display = _format_rate_limit_reset(reset)
                print(
                    f"GraphQL API利用状況: used={used}, remaining={remaining}, limit={limit}, "
                    f"reset={reset_display}, reset_in={reset_in_display}"
                )
            print("GitHub APIのレート制限に達しています。リセット後に再実行してください。")
            print("確認コマンド: gh api rate_limit")
            log_error_to_file("GitHub API rate limit exceeded during monitoring loop", e)
            consecutive_failures += 1
        except RuntimeError as e:
            print(f"\nError: {e}")
            print("Please ensure you are authenticated with gh CLI")
            log_error_to_file("Runtime error during monitoring loop", e)
            consecutive_failures += 1
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            traceback.print_exc()
            log_error_to_file("Unexpected error during monitoring loop", e)

            # Track consecutive unexpected failures to avoid infinite error loops
            consecutive_failures += 1

            if consecutive_failures >= 3:
                print("\nEncountered 3 consecutive unexpected errors; continuing monitoring with error counter capped.")
                consecutive_failures = 3

        # Display status summary before waiting
        # This helps users understand the current state at a glance,
        # especially on terminals with limited display lines.
        # Note: If an error occurred during data collection, the summary will show
        # incomplete or empty data, which is acceptable as it reflects the actual
        # state that was successfully retrieved before the error.
        try:
            after_rate_limit = get_rate_limit_info()
            _display_rate_limit_usage(before_rate_limit, after_rate_limit)
        except Exception as rate_limit_display_error:
            log_error_to_file("Failed to display rate limit usage", rate_limit_display_error)
            after_rate_limit = None

        # Check if current consumption rate would exhaust the rate limit before reset
        try:
            should_throttle, throttled_interval = _check_rate_limit_throttle(
                before_rate_limit, after_rate_limit, normal_interval_seconds
            )
        except Exception as throttle_error:
            log_error_to_file("Failed to check rate limit throttle", throttle_error)
            should_throttle = False
            throttled_interval = normal_interval_seconds

        try:
            display_prs, display_repos = all_prs, repos_with_prs
            no_change = False
            if skip_pr_check:
                snapshot = get_last_pr_snapshot()
                if snapshot is not None:
                    display_prs, display_repos = snapshot
                    no_change = True
            display_status_summary(display_prs, display_repos, config, no_change=no_change)
        except Exception as summary_error:
            log_error_to_file("Failed to display status summary", summary_error)

        # Check if PR state has not changed for too long and switch to reduced frequency mode
        try:
            use_reduced_frequency = check_no_state_change_timeout(all_prs, config)
        except Exception as timeout_error:
            log_error_to_file("Failed to evaluate reduced frequency interval", timeout_error)
            use_reduced_frequency = False

        # Determine which interval to use
        if use_reduced_frequency:
            # Use reduced frequency interval (default: 1h)
            reduced_interval_str = (config or {}).get("reduced_frequency_interval", "1h")
            try:
                reduced_interval_seconds = parse_interval(reduced_interval_str)
                current_interval_seconds = reduced_interval_seconds
                current_interval_str = reduced_interval_str
            except ValueError as e:
                print(f"Error: Invalid reduced_frequency_interval format: {e}")
                sys.exit(1)
        elif should_throttle:
            # Rate limit throttling: slow down to avoid exhausting the quota before reset
            current_interval_seconds = throttled_interval
            current_interval_str = format_elapsed_time(throttled_interval)
            print(f"\n{'=' * 50}")
            print("現在の消費ペースでは、レートリミットがリセットされる前に使い切る可能性があります。")
            print(f"監視間隔を{current_interval_str}に延長します。")
            print(f"{'=' * 50}")
        else:
            # Use normal interval (preserved separately to avoid contamination)
            current_interval_seconds = normal_interval_seconds
            current_interval_str = normal_interval_str

        # Wait with countdown display and check for config changes
        try:
            new_config, new_interval_seconds, new_interval_str, new_config_mtime = wait_with_countdown(
                current_interval_seconds,
                current_interval_str,
                config_path,
                config_mtime,
                self_update_callback=maybe_self_update
                if config.get("enable_auto_update", DEFAULT_ENABLE_AUTO_UPDATE)
                else None,
                self_update_interval_seconds=UPDATE_CHECK_INTERVAL_SECONDS,
            )
        except Exception as wait_error:
            log_error_to_file("wait_with_countdown failed; falling back to sleep", wait_error)
            time.sleep(current_interval_seconds)
            continue

        # Update config and interval based on what was returned from wait
        # Config will be non-empty only if successfully reloaded during wait
        config_reloaded = new_config_mtime != config_mtime
        if config_reloaded and new_config:
            config = new_config
            # Update normal interval only on hot reload (config change).
            # This prevents the normal interval from being contaminated by reduced frequency
            # interval values that may be returned from wait_with_countdown().
            normal_interval_seconds = new_interval_seconds
            normal_interval_str = new_interval_str
        # Always update mtime
        config_mtime = new_config_mtime


if __name__ == "__main__":
    main()

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
ce7295e Merge pull request #405 from cat2151/copilot/evaluate-window-close-confusion
b3443cc 対策D+A: autoraiseデフォルトFalse（バックグラウンド開封）＋誤クローズ時の案内メッセージ出力
65722a2 Initial plan
997a5be Merge pull request #404 from cat2151/copilot/evaluate-fetching-strategy
e26d835 Remove unused GraphQL fields and dead legacy code from PR fetching
87a3a10 Initial plan
4c2e03f Merge pull request #403 from cat2151/copilot/fix-open-pr-count-display
5720d97 fix: per-repo count map comparison and add validation in forced Phase 1/2 branch
592b56e fix: re-fetch open PR count via GraphQL every iteration to prevent stale display
1d3bf3b Initial plan

### 変更されたファイル:
src/gh_pr_phase_monitor/__init__.py
src/gh_pr_phase_monitor/actions/pr_actions.py
src/gh_pr_phase_monitor/browser/browser_automation.py
src/gh_pr_phase_monitor/github/comment_manager.py
src/gh_pr_phase_monitor/github/github_client.py
src/gh_pr_phase_monitor/github/pr_fetcher.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/monitor/monitor.py
src/gh_pr_phase_monitor/monitor/snapshot_markdown.py
src/gh_pr_phase_monitor/monitor/state_tracker.py
src/gh_pr_phase_monitor/phase/html/html_status_processor.py
src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py
src/gh_pr_phase_monitor/phase/phase_detector.py
src/gh_pr_phase_monitor/ui/display.py
tests/test_check_process_before_autoraise.py
tests/test_elapsed_time_display.py
tests/test_html_status_processor.py
tests/test_interval_contamination_bug.py
tests/test_is_llm_working.py
tests/test_llm_working_warning.py
tests/test_no_change_timeout.py
tests/test_post_comment.py
tests/test_pr_html_analyzer.py
tests/test_skip_pr_check_html_refetch.py
tests/test_status_summary.py


---
Generated at: 2026-03-09 07:01:14 JST
