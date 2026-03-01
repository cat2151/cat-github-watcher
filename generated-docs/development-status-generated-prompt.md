Last updated: 2026-03-02

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
- .github/actions-tmp/issue-notes/46.md
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
- .gitignore
- .vscode/settings.json
- LICENSE
- MERGE_CONFIGURATION_EXAMPLES.md
- PHASE3_MERGE_IMPLEMENTATION.md
- README.ja.md
- README.md
- STRUCTURE.md
- _config.yml
- cat-github-watcher.py
- config.toml.example
- demo_automation.py
- docs/RULESETS.md
- docs/button-detection-improvements.ja.md
- docs/window-activation-feature.md
- generated-docs/project-overview-generated-prompt.md
- pytest.ini
- requirements-automation.txt
- ruff.toml
- screenshots/assign.png
- screenshots/assign_to_copilot.png
- src/__init__.py
- src/gh_pr_phase_monitor/__init__.py
- src/gh_pr_phase_monitor/auto_updater.py
- src/gh_pr_phase_monitor/browser_automation.py
- src/gh_pr_phase_monitor/browser_cooldown.py
- src/gh_pr_phase_monitor/button_clicker.py
- src/gh_pr_phase_monitor/colors.py
- src/gh_pr_phase_monitor/comment_fetcher.py
- src/gh_pr_phase_monitor/comment_manager.py
- src/gh_pr_phase_monitor/config.py
- src/gh_pr_phase_monitor/config_printer.py
- src/gh_pr_phase_monitor/display.py
- src/gh_pr_phase_monitor/github_auth.py
- src/gh_pr_phase_monitor/github_client.py
- src/gh_pr_phase_monitor/graphql_client.py
- src/gh_pr_phase_monitor/interval_parser.py
- src/gh_pr_phase_monitor/issue_fetcher.py
- src/gh_pr_phase_monitor/llm_status_extractor.py
- src/gh_pr_phase_monitor/local_repo_watcher.py
- src/gh_pr_phase_monitor/main.py
- src/gh_pr_phase_monitor/monitor.py
- src/gh_pr_phase_monitor/notification_window.py
- src/gh_pr_phase_monitor/notifier.py
- src/gh_pr_phase_monitor/pages_watcher.py
- src/gh_pr_phase_monitor/phase_detector.py
- src/gh_pr_phase_monitor/pr_actions.py
- src/gh_pr_phase_monitor/pr_data_recorder.py
- src/gh_pr_phase_monitor/pr_fetcher.py
- src/gh_pr_phase_monitor/pr_html_fetcher.py
- src/gh_pr_phase_monitor/process_utils.py
- src/gh_pr_phase_monitor/repository_fetcher.py
- src/gh_pr_phase_monitor/snapshot_markdown.py
- src/gh_pr_phase_monitor/snapshot_path_utils.py
- src/gh_pr_phase_monitor/state_tracker.py
- src/gh_pr_phase_monitor/time_utils.py
- src/gh_pr_phase_monitor/wait_handler.py
- src/gh_pr_phase_monitor/window_manager.py
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
- tests/test_graphql_client_rate_limit.py
- tests/test_has_comments_with_reactions.py
- tests/test_has_unresolved_review_threads.py
- tests/test_hot_reload.py
- tests/test_html_to_markdown.py
- tests/test_integration_issue_fetching.py
- tests/test_interval_contamination_bug.py
- tests/test_interval_parsing.py
- tests/test_issue_assignment_priority.py
- tests/test_issue_fetching.py
- tests/test_local_repo_watcher.py
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
- tests/test_pr_data_recorder.py
- tests/test_pr_data_recorder_html.py
- tests/test_pr_data_recorder_json.py
- tests/test_pr_title_fix.py
- tests/test_rate_limit_reset_display.py
- tests/test_repos_with_prs_structure.py
- tests/test_show_issues_when_pr_count_less_than_3.py
- tests/test_status_summary.py
- tests/test_validate_phase3_merge_config.py
- tests/test_verbose_config.py
- tests/test_wait_handler_callback.py

## 現在のオープンIssues
## [Issue #298](../issue-notes/298.md): 大きなファイルの検出: 1個のファイルが500行を超えています
以下のファイルが500行を超えています。リファクタリングを検討してください。

## 検出されたファイル

| ファイル | 行数 | 超過行数 |
|---------|------|----------|
| `src/gh_pr_phase_monitor/button_clicker.py` | 518 | +18 |

## テスト実施のお願い

- リファクタリング前後にテストを実行し、それぞれのテスト失敗件数を報告してください
- リファクタリング前後のどちらかでテストがredの場合、まず別issueでtest greenにしてからリファクタリングしてください

## 推奨事項
...
ラベル: refactoring, code-quality, automated
--- issue-notes/298.md の内容 ---

```markdown

```

## [Issue #297](../issue-notes/297.md): GraphQL API消費回数の内訳を毎イテレーション表示する
- [x] `graphql_client.py`: `get_rate_limit_info()` で `OSError` も捕捉する（`gh` がPATHにない場合のクラッシュ防止）
- [x] `main.py`: `before_rate_limit` 取得を try/except で囲み、失敗時は `None` にフォールバック
- [x] `main.py`: `consumed` が負になる場合（レートリミットウィンドウがリセットされた場合）を 0 表示＋「リセット後」ノートで対応
- [x] テスト: 負の消費量ケースのテストを追加（10テスト全通過）
- [x] ruff l...
ラベル: 
--- issue-notes/297.md の内容 ---

```markdown

```

## [Issue #296](../issue-notes/296.md): 1分ごとに、GraphQL API の消費回数の内訳を表示する。現在、すぐ1000くらい減っているようなので原因調査用。あわせて回復までの時間も表示する

ラベル: good first issue
--- issue-notes/296.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/7.md
```md
{% raw %}
# issue issue note生成できるかのtest用 #7
[issues #7](https://github.com/cat2151/github-actions/issues/7)

- 生成できた
- closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/8.md
```md
{% raw %}
# issue 関数コールグラフhtmlビジュアライズ生成の対象ソースファイルを、呼び出し元ymlで指定できるようにする #8
[issues #8](https://github.com/cat2151/github-actions/issues/8)

# これまでの課題
- 以下が決め打ちになっていた
```
  const allowedFiles = [
    'src/main.js',
    'src/mml2json.js',
    'src/play.js'
  ];
```

# 対策
- 呼び出し元ymlで指定できるようにする

# agent
- agentにやらせることができれば楽なので、初手agentを試した
- 失敗
    - ハルシネーションしてscriptを大量破壊した
- 分析
    - 修正対象scriptはagentが生成したもの
    - 低品質な生成結果でありソースが巨大
    - ハルシネーションで破壊されやすいソース
    - AIの生成したソースは、必ずしもAIフレンドリーではない

# 人力リファクタリング
- 低品質コードを、最低限agentが扱えて、ハルシネーションによる大量破壊を防止できる内容、にする
- 手短にやる
    - そもそもビジュアライズは、agentに雑に指示してやらせたもので、
    - 今後別のビジュアライザを選ぶ可能性も高い
    - 今ここで手間をかけすぎてコンコルド効果（サンクコストバイアス）を増やすのは、project群をトータルで俯瞰して見たとき、損
- 対象
    - allowedFiles のあるソース
        - callgraph-utils.cjs
            - たかだか300行未満のソースである
            - この程度でハルシネーションされるのは予想外
            - やむなし、リファクタリングでソース分割を進める

# agentに修正させる
## prompt
```
allowedFilesを引数で受け取るようにしたいです。
ないならエラー。
最終的に呼び出し元すべてに波及して修正したいです。

呼び出し元をたどってエントリポイントも見つけて、
エントリポイントにおいては、
引数で受け取ったjsonファイル名 allowedFiles.js から
jsonファイル allowedFiles.jsonの内容をreadして
変数 allowedFilesに格納、
後続処理に引き渡す、としたいです。

まずplanしてください。
planにおいては、修正対象のソースファイル名と関数名を、呼び出し元を遡ってすべて特定し、listしてください。
```

# 修正が順調にできた
- コマンドライン引数から受け取る作りになっていなかったので、そこだけ指示して修正させた
- yml側は人力で修正した

# 他のリポジトリから呼び出した場合にバグらないよう修正する
- 気付いた
    - 共通ワークフローとして他のリポジトリから使った場合はバグるはず。
        - ymlから、共通ワークフロー側リポジトリのcheckoutが漏れているので。
- 他のyml同様に修正する
- あわせて全体にymlをリファクタリングし、修正しやすくし、今後のyml読み書きの学びにしやすくする

# local WSL + act : test green

# closeとする
- もし生成されたhtmlがNGの場合は、別issueとするつもり

{% endraw %}
```

### src/gh_pr_phase_monitor/button_clicker.py
```py
{% raw %}
"""Button clicker module for browser automation

Provides utilities for finding and clicking buttons on screen using
image recognition (PyAutoGUI) with OCR fallback (pytesseract).
"""

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .window_manager import _maybe_maximize_window

# PyAutoGUI imports are optional - will be imported only if automation is enabled
try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None  # Set to None when not available

# pytesseract imports are optional - for OCR-based button detection fallback
try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    pytesseract = None
    # Note: PIL.Image is imported locally in _click_button_with_ocr when needed

# Track whether the notification window was explicitly closed by the user
_user_cancelled_notification = False


def set_user_cancelled_notification() -> None:
    """Set the user-cancelled flag (call this when the notification window is closed by the user)."""
    global _user_cancelled_notification
    _user_cancelled_notification = True


def reset_user_cancelled_notification() -> None:
    """Reset the user-cancelled flag (call this before starting a new automation sequence)."""
    global _user_cancelled_notification
    _user_cancelled_notification = False


# Debug candidate detection settings
# These thresholds are only used when image recognition fails with the original confidence threshold
# The search stops after finding DEBUG_MAX_CANDIDATES candidates
DEBUG_CANDIDATE_CONFIDENCE_THRESHOLDS = [0.7, 0.6, 0.5]  # Try these confidence levels for debug candidates
DEBUG_MAX_CANDIDATES = 3  # Maximum number of candidate regions to save for debugging

# OCR detection settings
OCR_BUTTON_PADDING = 20  # Pixels to add around detected text to account for button borders


def _log_error(message: str, exc: Exception | BaseException | None = None) -> None:
    """Append an error entry to logs/error.log without raising further exceptions."""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        from datetime import UTC

        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception as log_exc:
        print(
            f"[button_clicker._log_error] Failed to write to error.log: {log_exc!r} (original message: {message})",
            file=sys.stderr,
        )


def _validate_wait_seconds(config: Dict[str, Any], default: int = 10) -> int:
    """Validate and get wait_seconds from configuration

    Args:
        config: Configuration dict with wait_seconds setting
        default: Default wait time to fall back to when invalid

    Returns:
        Validated wait_seconds value (defaults to provided value if invalid)
    """
    try:
        wait_seconds = int(config.get("wait_seconds", default))
        if wait_seconds < 0:
            print(f"  ⚠ wait_seconds must be positive, using default: {default}")
            wait_seconds = default
    except (ValueError, TypeError):
        print(f"  ⚠ Invalid wait_seconds value in config, using default: {default}")
        wait_seconds = default
    return wait_seconds


def _validate_confidence(config: Dict[str, Any]) -> float:
    """Validate and get confidence from configuration

    Args:
        config: Configuration dict with confidence setting

    Returns:
        Validated confidence value (defaults to 0.8 if invalid)
    """
    try:
        confidence = float(config.get("confidence", 0.8))
        if not 0.0 <= confidence <= 1.0:
            print("  ⚠ confidence must be between 0.0 and 1.0, using default: 0.8")
            confidence = 0.8
    except (ValueError, TypeError):
        print("  ⚠ Invalid confidence value in config, using default: 0.8")
        confidence = 0.8
    return confidence


def _validate_button_delay(config: Dict[str, Any]) -> float:
    """Validate and get button_delay from configuration

    Args:
        config: Configuration dict with button_delay setting

    Returns:
        Validated button_delay value in seconds (defaults to 2.0 if invalid)
    """
    try:
        button_delay = float(config.get("button_delay", 2.0))
        if button_delay < 0:
            print("  ⚠ button_delay must be positive, using default: 2.0")
            button_delay = 2.0
    except (ValueError, TypeError):
        print("  ⚠ Invalid button_delay value in config, using default: 2.0")
        button_delay = 2.0
    return button_delay


def _get_screenshot_path(button_name: str, config: Dict[str, Any]) -> Optional[Path]:
    """Get the path to the button screenshot image

    Args:
        button_name: Name of the button (e.g., "assign_to_copilot", "assign", "merge_pull_request")
        config: Configuration dict (assign_to_copilot or phase3_merge section) with screenshot_dir setting

    Returns:
        Path to the screenshot image, or None if not found
    """
    # Get screenshot directory from config, default to ./screenshots
    screenshot_dir_str = config.get("screenshot_dir", "screenshots")
    screenshot_dir = Path(screenshot_dir_str).expanduser().resolve()

    # Look for the screenshot with common image extensions
    for ext in [".png", ".jpg", ".jpeg"]:
        screenshot_path = screenshot_dir / f"{button_name}{ext}"
        if screenshot_path.exists():
            return screenshot_path

    return None


def _save_debug_info(button_name: str, confidence: float, config: Dict[str, Any]) -> None:
    """Save debug information when image recognition fails

    This function saves:
    1. Full screenshot of current screen
    2. Top 3 candidate locations (if any found with lower confidence)
    3. JSON metadata with all information

    Args:
        button_name: Name of the button that failed to be found
        confidence: Confidence threshold that was used
        config: Configuration dict with debug_dir setting
    """
    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        return

    # Get debug directory from config, default to ./debug_screenshots
    debug_dir_str = config.get("debug_dir", "debug_screenshots")
    debug_dir = Path(debug_dir_str).expanduser().resolve()

    # Create debug directory if it doesn't exist
    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"  ⚠ Could not create debug directory '{debug_dir}': {e}")
        return

    # Generate timestamp once for consistency between filename and JSON
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")  # Include microseconds for uniqueness

    # Take screenshot of current screen
    screenshot_filename = f"{button_name}_fail_{timestamp}.png"
    screenshot_path = debug_dir / screenshot_filename

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(str(screenshot_path))
        print(f"  ℹ Debug screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"  ⚠ Could not save debug screenshot: {e}")
        _log_error(f"Failed to capture debug screenshot for '{button_name}'", e)
        return

    # Get template screenshot path and handle None case
    template_path = _get_screenshot_path(button_name, config)
    template_screenshot = str(template_path) if template_path else None

    # Try to find candidate matches with lower confidence threshold
    candidates = []
    if template_path:
        try:
            # Try multiple confidence levels to find potential matches
            for test_confidence in DEBUG_CANDIDATE_CONFIDENCE_THRESHOLDS:
                # Only try confidence levels lower than the original threshold
                if test_confidence >= confidence:
                    continue

                print(f"  → Searching for candidates with confidence {test_confidence}...")
                all_locations = list(pyautogui.locateAllOnScreen(str(template_path), confidence=test_confidence))

                if all_locations:
                    print(f"  ℹ Found {len(all_locations)} candidate(s) with confidence {test_confidence}")
                    # Save up to DEBUG_MAX_CANDIDATES candidates at this confidence level
                    for idx, loc in enumerate(all_locations[:DEBUG_MAX_CANDIDATES]):
                        candidate_info = {
                            "confidence_used": test_confidence,
                            "left": loc.left,
                            "top": loc.top,
                            "width": loc.width,
                            "height": loc.height,
                        }
                        candidates.append(candidate_info)

                        # Save cropped image of the candidate region
                        try:
                            candidate_img = screenshot.crop(
                                (loc.left, loc.top, loc.left + loc.width, loc.top + loc.height)
                            )
                            candidate_filename = f"{button_name}_candidate_{timestamp}_{len(candidates)}.png"
                            candidate_path = debug_dir / candidate_filename
                            candidate_img.save(str(candidate_path))
                            candidate_info["image_path"] = str(candidate_path)
                            print(f"  ℹ Saved candidate #{len(candidates)}: {candidate_path}")
                        except Exception as e:
                            print(f"  ⚠ Could not save candidate image: {e}")

                    # Stop after finding candidates
                    if len(candidates) >= DEBUG_MAX_CANDIDATES:
                        break

        except Exception as e:
            print(f"  ⚠ Error searching for candidates: {e}")

    # Save failure information to JSON
    json_filename = f"{button_name}_fail_{timestamp}.json"
    json_path = debug_dir / json_filename

    failure_info = {
        "button_name": button_name,
        "timestamp": now.isoformat(),  # Use the same datetime object for consistency
        "confidence": confidence,
        "screenshot_path": str(screenshot_path),
        "template_screenshot": template_screenshot,
        "candidates_found": len(candidates),
        "candidates": candidates,
    }

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(failure_info, f, indent=2, ensure_ascii=False)
        print(f"  ℹ Debug info saved: {json_path}")
        if candidates:
            print(f"  ℹ Found {len(candidates)} potential candidate(s) - check debug directory for details")
    except Exception as e:
        print(f"  ⚠ Could not save debug info JSON: {e}")


def _click_button_with_ocr(button_name: str, config: Dict[str, Any]) -> bool:
    """Find and click a button using OCR text detection

    This is a fallback method when image recognition fails. It uses OCR
    to find text on screen and click buttons by their text content.

    Args:
        button_name: Name of the button (e.g., "assign_to_copilot", "assign")
        config: Configuration dict with automation settings

    Returns:
        True if button was found and clicked, False otherwise
    """
    if not PYTESSERACT_AVAILABLE or pytesseract is None:
        print("  ℹ pytesseract is not available for OCR-based button detection")
        return False

    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        print("  ℹ PyAutoGUI is required for OCR-based button detection")
        return False

    # OCR detection is enabled by default (True) to serve as a fallback when image recognition fails
    if not config.get("enable_ocr_detection", True):
        print("  ℹ OCR-based detection is disabled")
        return False

    # Map button names to the text we're looking for
    button_text_map = {
        "assign_to_copilot": "Assign to Copilot",
        "assign": "Assign",
        "merge_pull_request": "Merge pull request",
        "confirm_merge": "Confirm merge",
        "delete_branch": "Delete branch",
    }

    target_text = button_text_map.get(button_name)
    if not target_text:
        print(f"  ⚠ Unknown button name '{button_name}' for OCR detection")
        return False

    try:
        print(f"  → Attempting OCR-based detection for '{target_text}' button...")

        # Take a screenshot
        screenshot = pyautogui.screenshot()

        # Use pytesseract to get bounding boxes of all text
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        # Search for the target text in the OCR results
        n_boxes = len(data["text"])
        found_regions = []

        # Look for consecutive words that match our target text
        target_words = target_text.lower().split()

        for i in range(n_boxes):
            text = data["text"][i].lower().strip()
            if not text:
                continue

            # Check if we found the start of our target phrase
            if text == target_words[0]:
                # Try to match all consecutive words
                matches = [i]
                for j, target_word in enumerate(target_words[1:], start=1):
                    if i + j < n_boxes:
                        next_text = data["text"][i + j].lower().strip()
                        if next_text == target_word:
                            matches.append(i + j)
                        else:
                            break
                    else:
                        break

                # If we matched all words, we found the button text
                if len(matches) == len(target_words):
                    # Calculate bounding box for all matched words
                    xs = [data["left"][idx] for idx in matches]
                    ys = [data["top"][idx] for idx in matches]
                    ws = [data["width"][idx] for idx in matches]
                    hs = [data["height"][idx] for idx in matches]

                    left = min(xs)
                    top = min(ys)
                    right = max(x + w for x, w in zip(xs, ws))
                    bottom = max(y + h for y, h in zip(ys, hs))

                    # Expand the region to account for button padding
                    region = {
                        "left": max(0, left - OCR_BUTTON_PADDING),
                        "top": max(0, top - OCR_BUTTON_PADDING),
                        "right": min(screenshot.width, right + OCR_BUTTON_PADDING),
                        "bottom": min(screenshot.height, bottom + OCR_BUTTON_PADDING),
                    }
                    found_regions.append(region)

        if not found_regions:
            print(f"  ✗ Text '{target_text}' not found using OCR")
            return False

        # Use the first found region (or could use heuristics to pick the best one)
        region = found_regions[0]
        center_x = int((region["left"] + region["right"]) / 2)
        center_y = int((region["top"] + region["bottom"]) / 2)

        print(f"  → Found '{target_text}' at position ({center_x}, {center_y})")

        # Click the button
        time.sleep(0.5)  # Brief pause before clicking
        pyautogui.click(center_x, center_y)
        print(f"  ✓ Clicked '{target_text}' button using OCR detection")

        return True

    except Exception as e:
        print(f"  ⚠ OCR-based detection failed: {e}")
        return False


def _click_button_with_image(
    button_name: str,
    config: Dict[str, Any],
    *,
    max_attempts: int = 1,
    poll_interval: float = 0.0,
    pre_click_delay: float = 0.5,
) -> bool:
    """Find and click a button using image recognition

    Args:
        button_name: Name of the button screenshot file (without extension)
        config: Configuration dict with screenshot settings (including optional confidence)

    Returns:
        True if button was found and clicked, False otherwise

    Note:
        Uses image recognition to find and click buttons on screen. The first matching
        button found on the entire screen will be clicked. Ensure the correct GitHub
        browser window/tab is focused and visible before running this function.

        When image recognition fails, debug information (screenshot and failure details)
        will be saved to the debug_dir directory (default: ./debug_screenshots).
    """
    if not PYAUTOGUI_AVAILABLE or pyautogui is None:
        print("  ✗ PyAutoGUI is not available")
        return False

    if _user_cancelled_notification:
        print("  ⚠ Notification window was closed by user; skipping button search")
        return False

    screenshot_path = _get_screenshot_path(button_name, config)
    if screenshot_path is None:
        print(f"  ✗ Screenshot not found for button '{button_name}'")
        print(f"     Please save a screenshot as '{button_name}.png' in the screenshots directory")
        print("     See README.ja.md for instructions")
        return False

    # Get confidence from config
    confidence = _validate_confidence(config)

    try:
        attempts = max(1, max_attempts)
        has_maximized = False
        for attempt in range(attempts):
            print(f"  → Looking for button using screenshot: {screenshot_path}")
            print(
                "  ⚠ Make sure the correct GitHub browser window/tab is focused "
                "because the first matching button on the entire screen will be clicked."
            )
            location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

            if location is None and not has_maximized:
                if _maybe_maximize_window(config):
                    has_maximized = True
                    time.sleep(0.5)  # Allow layout to settle after maximizing
                    location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)

            if location is None and attempt < attempts - 1:
                if _user_cancelled_notification:
                    print("  ⚠ Notification window was closed by user; skipping button search")
                    return False
                if poll_interval > 0:
                    time.sleep(poll_interval)
                continue

            if location is None:
                if _user_cancelled_notification:
                    print("  ⚠ Notification window was closed by user; skipping button search")
                    return False
                print(f"  ✗ Could not find button '{button_name}' on screen with image recognition")
                print("     Trying fallback methods...")
                # Save debug information for troubleshooting
                try:
                    _save_debug_info(button_name, confidence, config)
                except Exception as debug_exc:  # noqa: BLE001
                    _log_error(f"Failed to save debug info for '{button_name}' after image search miss", debug_exc)

                # Try OCR-based detection as fallback
                print("  → Attempting OCR fallback...")
                if _click_button_with_ocr(button_name, config):
                    return True

                print(f"  ✗ All detection methods failed for button '{button_name}'")
                return False

            # Re-verify just before clicking to avoid stale coordinates, then click immediately
            verification_location = pyautogui.locateOnScreen(str(screenshot_path), confidence=confidence)
            if verification_location is None:
                print(f"  ✗ Button '{button_name}' not found during final verification; skipping click")
                return False
            center = pyautogui.center(verification_location)
            if _user_cancelled_notification:
                print("  ⚠ Notification window was closed by user; skipping button search")
                return False
            if pre_click_delay > 0:
                time.sleep(pre_click_delay)
            pyautogui.click(center)
            print(f"  ✓ Clicked button '{button_name}' at position {center}")
            return True

    except Exception as e:
        print(f"  ✗ Error clicking button '{button_name}': {e}")
        print("     This may occur if running in a headless environment, SSH session without display,")
        print("     or if the screen is locked. PyAutoGUI requires an active display.")
        _log_error(f"Button click failed for '{button_name}'", e)
        # Save debug information even on exception
        try:
            _save_debug_info(button_name, confidence, config)
        except Exception as debug_exc:
            _log_error(f"Failed to save debug info for '{button_name}' after exception", debug_exc)
        return False

{% endraw %}
```

### src/gh_pr_phase_monitor/graphql_client.py
```py
{% raw %}
"""
GraphQL client module for executing queries via GitHub CLI
"""

import json
import subprocess
from typing import Any, Dict


class GitHubRateLimitError(RuntimeError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, message: str, rate_limit_info: Dict[str, Any] | None = None):
        super().__init__(message)
        self.rate_limit_info = rate_limit_info


def _is_rate_limit_exceeded_error(stderr: str) -> bool:
    """Return True when stderr indicates a GitHub API rate limit exhaustion."""
    lower_stderr = stderr.lower()
    return "rate limit" in lower_stderr and ("exceeded" in lower_stderr or "exhausted" in lower_stderr)


def _get_graphql_rate_limit_info() -> Dict[str, Any] | None:
    """Fetch GraphQL rate limit details via gh api rate_limit.

    Returns:
        Dictionary containing GraphQL rate-limit fields, or None if unavailable.
    """
    try:
        result = subprocess.run(
            ["gh", "api", "rate_limit"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        data = json.loads(result.stdout or "{}")
        graphql_info = data.get("resources", {}).get("graphql")
        if isinstance(graphql_info, dict):
            return graphql_info
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def execute_graphql_query(query: str, variables: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Execute a GraphQL query using gh CLI

    Args:
        query: GraphQL query string
        variables: Optional dictionary of GraphQL variables

    Returns:
        Parsed JSON response from GitHub API

    Raises:
        RuntimeError: If the query execution fails
        json.JSONDecodeError: If the response cannot be parsed
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]

    # Add variables to command if provided
    if variables:
        for key, value in variables.items():
            cmd.extend(["-F", f"{key}={value}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            error_message = f"Error parsing JSON response from gh CLI: {e}\nRaw output from gh:\n{result.stdout}"
            print(error_message)
            raise RuntimeError(error_message) from e

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing GraphQL query: {e}"
        print(error_message)
        stderr_text = (e.stderr or "").strip()
        if stderr_text:
            print(f"stderr: {stderr_text}")

        if _is_rate_limit_exceeded_error(stderr_text):
            graphql_limit_info = _get_graphql_rate_limit_info()
            if graphql_limit_info:
                limit = graphql_limit_info.get("limit", "unknown")
                used = graphql_limit_info.get("used", "unknown")
                remaining = graphql_limit_info.get("remaining", "unknown")
                reset = graphql_limit_info.get("reset", "unknown")
                rate_limit_message = (
                    "GitHub API rate limit exceeded. "
                    f"GraphQL limit: used={used}, remaining={remaining}, limit={limit}, reset={reset}. "
                    "Wait for reset and retry."
                )
            else:
                rate_limit_message = (
                    "GitHub API rate limit exceeded. "
                    "Wait for reset and retry. "
                    "You can check remaining quota with `gh api rate_limit`."
                )
            raise GitHubRateLimitError(rate_limit_message, rate_limit_info=graphql_limit_info) from e

        raise RuntimeError(error_message) from e

{% endraw %}
```

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
from typing import Any

from .auto_updater import UPDATE_CHECK_INTERVAL_SECONDS, maybe_self_update
from .config import (
    DEFAULT_ENABLE_AUTO_UPDATE,
    DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS,
    DEFAULT_MAX_LLM_WORKING_PARALLEL,
    get_config_mtime,
    load_config,
    parse_interval,
    print_config,
    validate_phase3_merge_config_required,
)
from .display import display_issues_from_repos_without_prs, display_status_summary
from .github_auth import get_current_user
from .github_client import get_pr_details_batch, get_repositories_with_open_prs
from .graphql_client import GitHubRateLimitError
from .local_repo_watcher import check_local_repos
from .monitor import check_no_state_change_timeout
from .pages_watcher import check_pages_deployments_for_repos, get_pages_repos_from_config
from .phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase
from .pr_actions import process_pr
from .pr_data_recorder import record_reaction_snapshot, reset_snapshot_cache
from .time_utils import format_elapsed_time
from .wait_handler import wait_with_countdown

LOG_DIR = Path("logs")


def _format_rate_limit_reset(reset: Any, now: datetime | None = None) -> tuple[str, str]:
    """Format rate-limit reset epoch into UTC datetime and remaining duration."""
    if not isinstance(reset, (int, float)):
        return "unknown", "unknown"

    current = now or datetime.now(UTC)
    reset_dt = datetime.fromtimestamp(float(reset), UTC)
    remaining_seconds = max(0, int(reset_dt.timestamp() - current.timestamp()))
    return reset_dt.strftime("%Y-%m-%d %H:%M:%S UTC"), format_elapsed_time(remaining_seconds)


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


def main():
    """Main execution function"""
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

    # Get interval setting (default to 1 minute if not specified)
    # Keep the normal interval separate from the current interval to prevent the normal
    # interval from being overwritten by reduced frequency interval values during mode switches
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

        # Reset snapshot cache to allow recording new snapshots in this iteration
        reset_snapshot_cache()

        # Initialize variables to track status for summary
        all_prs = []
        pr_phases = []
        repos_with_prs = []

        try:
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

                    snapshots_enabled = config.get("enable_pr_phase_snapshots", DEFAULT_ENABLE_PR_PHASE_SNAPSHOTS)
                    # Track phases to detect if all PRs are in "LLM working"
                    for pr in all_prs:
                        try:
                            phase = determine_phase(pr)

                            try:
                                record_reaction_snapshot(pr, phase, enable_snapshots=snapshots_enabled)
                                phase = determine_phase(pr)
                            except Exception as snapshot_error:
                                print(f"    Failed to capture PR reaction/LLM status data: {snapshot_error}")
                                log_error_to_file(
                                    f"Failed to capture PR reaction/LLM status data for {pr.get('url', 'unknown')}",
                                    snapshot_error,
                                )

                            pr_phases.append(phase)
                            process_pr(pr, config, phase)
                        except Exception as pr_error:
                            log_error_to_file(
                                f"Failed to process PR {pr.get('url', 'unknown') or pr.get('title', 'unknown')}",
                                pr_error,
                            )
                            pr_phases.append(PHASE_LLM_WORKING)

                    # Count how many PRs are in "LLM working" phase
                    # This count is used for rate limit protection - when too many PRs are being
                    # worked on simultaneously, we pause auto-assignment to prevent API rate limits
                    llm_working_count = sum(1 for phase in pr_phases if phase == PHASE_LLM_WORKING)
                    max_llm_working_parallel = config.get("max_llm_working_parallel", DEFAULT_MAX_LLM_WORKING_PARALLEL)
                    llm_working_below_cap = llm_working_count < max_llm_working_parallel

                    # Look for new issues to assign when:
                    # 1. All PRs are in "LLM working" phase (existing work is in progress), OR
                    # 2. PR count is less than 3 (few PRs, so we can look for more work)
                    # The llm_working_count throttles assignment when parallel work is too high
                    total_pr_count = len(all_prs)
                    all_llm_working = bool(pr_phases) and all(phase == PHASE_LLM_WORKING for phase in pr_phases)
                    all_phase3 = bool(pr_phases) and all(phase == PHASE_3 for phase in pr_phases)
                    active_parallel_prs = sum(1 for phase in pr_phases if phase != PHASE_3)

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

            # Check local repository pullable status
            # By default (dry-run), displays repos that can be pulled.
            # Set auto_git_pull = true in config.toml to auto-pull.
            try:
                if current_user is None:
                    current_user = get_current_user()
                check_local_repos(config, current_user)
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
            display_status_summary(all_prs, pr_phases, repos_with_prs, config)
        except Exception as summary_error:
            log_error_to_file("Failed to display status summary", summary_error)

        # Check if PR state has not changed for too long and switch to reduced frequency mode
        try:
            use_reduced_frequency = check_no_state_change_timeout(all_prs, pr_phases, config)
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
b692705 Merge pull request #295 from cat2151/copilot/fix-phase2-llm-issue
4c5c514 Fix: phase2 LLM working の進捗ラベルを「Phase 1 completed」から「Phase 2 in progress」に修正
dde6e54 Initial plan
aa53c9e Merge pull request #294 from cat2151/copilot/improve-search-response-time
a6c92d5 進捗表示の残像修正: max_msg_lenで最長メッセージ長を追跡
190eb46 pullableの検索処理中に1行進捗表示を追加（ハング防止）
edf28ff Initial plan
e4e58e0 Merge pull request #293 from cat2151/copilot/add-warning-for-long-working-prs
3ea8229 LLM workingのPRが起票から30分以上経過している場合に警告を表示
bf9a489 Initial plan

### 変更されたファイル:
src/gh_pr_phase_monitor/browser_automation.py
src/gh_pr_phase_monitor/browser_cooldown.py
src/gh_pr_phase_monitor/button_clicker.py
src/gh_pr_phase_monitor/config.py
src/gh_pr_phase_monitor/config_printer.py
src/gh_pr_phase_monitor/display.py
src/gh_pr_phase_monitor/interval_parser.py
src/gh_pr_phase_monitor/local_repo_watcher.py
src/gh_pr_phase_monitor/notification_window.py
src/gh_pr_phase_monitor/phase_detector.py
src/gh_pr_phase_monitor/pr_fetcher.py
src/gh_pr_phase_monitor/process_utils.py
src/gh_pr_phase_monitor/window_manager.py
tests/test_assign_issue_to_copilot.py
tests/test_browser_automation.py
tests/test_browser_automation_click.py
tests/test_browser_automation_ocr.py
tests/test_browser_automation_window.py
tests/test_check_process_before_autoraise.py
tests/test_elapsed_time_display.py
tests/test_has_comments_with_reactions.py
tests/test_has_unresolved_review_threads.py
tests/test_html_to_markdown.py
tests/test_issue_assignment_priority.py
tests/test_issue_fetching.py
tests/test_local_repo_watcher.py
tests/test_no_open_prs_issue_display.py
tests/test_open_browser_cooldown.py
tests/test_phase_detection.py
tests/test_phase_detection_llm_status.py
tests/test_phase_detection_real_prs.py
tests/test_pr_actions.py
tests/test_pr_actions_dry_run.py
tests/test_pr_data_recorder.py
tests/test_pr_data_recorder_html.py
tests/test_pr_data_recorder_json.py
tests/test_status_summary.py


---
Generated at: 2026-03-02 07:01:24 JST
