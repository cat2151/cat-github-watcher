Last updated: 2026-03-06

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
- .github/workflows/run-tests-on-pr.yml
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
- src/gh_pr_phase_monitor/monitor/snapshot_markdown.py
- src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py
- src/gh_pr_phase_monitor/monitor/state_tracker.py
- src/gh_pr_phase_monitor/phase/__init__.py
- src/gh_pr_phase_monitor/phase/llm_status_extractor.py
- src/gh_pr_phase_monitor/phase/phase_detector.py
- src/gh_pr_phase_monitor/phase/phase_detector_graphql.py
- src/gh_pr_phase_monitor/phase/pr_data_recorder.py
- src/gh_pr_phase_monitor/phase/pr_html_analyzer.py
- src/gh_pr_phase_monitor/phase/pr_html_fetcher.py
- src/gh_pr_phase_monitor/phase/pr_html_saver.py
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
- tests/test_html_to_markdown.py
- tests/test_integration_issue_fetching.py
- tests/test_interval_contamination_bug.py
- tests/test_interval_parsing.py
- tests/test_issue_assignment_priority.py
- tests/test_issue_fetching.py
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
- tests/test_pr_data_recorder.py
- tests/test_pr_data_recorder_html.py
- tests/test_pr_data_recorder_json.py
- tests/test_pr_html_analyzer.py
- tests/test_pr_title_fix.py
- tests/test_rate_limit_reset_display.py
- tests/test_rate_limit_throttle.py
- tests/test_rate_limit_usage_display.py
- tests/test_repos_with_prs_structure.py
- tests/test_show_issues_when_pr_count_less_than_3.py
- tests/test_status_summary.py
- tests/test_validate_phase3_merge_config.py
- tests/test_verbose_config.py
- tests/test_wait_handler_callback.py

## 現在のオープンIssues
## [Issue #346](../issue-notes/346.md): Fix: Save all open PRs to logs/pr — HTML-based status detection refactoring with clean directory structure
`logs/pr` was only receiving HTML from PRs in `PHASE_LLM_WORKING`. All other open PRs were silently skipped because HTML fetch was gated on the deprecated `record_reaction_snapshot()` flow which filtered by phase.

## Root cause

`record_reaction_snapshot()` in `pr_data_recorder.py` returned early f...
ラベル: 
--- issue-notes/346.md の内容 ---

```markdown

```

## [Issue #345](../issue-notes/345.md): logs/pr に保存されるPRがごく限られたものだけになってしまっている

ラベル: 
--- issue-notes/345.md の内容 ---

```markdown

```

## [Issue #335](../issue-notes/335.md): status PHASE1～3 の扱いを変更する

ラベル: 
--- issue-notes/335.md の内容 ---

```markdown

```

## [Issue #319](../issue-notes/319.md): ムダにGraphQLクエリを消費しすぎ

ラベル: 
--- issue-notes/319.md の内容 ---

```markdown

```

## [Issue #317](../issue-notes/317.md): auto pullの発展型として、対象userのアクティブなリポジトリを全てlocalにcloneし、高速に全リポジトリへのアクセスを可能とする、ことを検討する

ラベル: 
--- issue-notes/317.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/17.md
```md
{% raw %}
# issue development-status が生成したmdに誤りがある。issue-note へのlinkがURL誤りで、404となってしまう #17
[issues #17](https://github.com/cat2151/github-actions/issues/17)

# 事例
- 生成したmdのURL：
    - https://github.com/cat2151/github-actions/blob/main/generated-docs/development-status.md
- そのmdをGitHub上でdecodeして閲覧したときのURL、404である：
    - https://github.com/cat2151/github-actions/blob/main/generated-docs/issue-notes/16.md
- そのmdに実際に含まれるURL：
    - issue-notes/16.md
- あるべきURL：
    - https://github.com/cat2151/github-actions/blob/main/issue-notes/16.md
- あるべきURLがmdにどう含まれているべきか：
    - ../issue-notes/16.md

# どうする？
- 案
    - promptを修正する
    - promptの場所は：
        - .github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
    - 備考、cjs内にpromptがハードコーディングされており、promptをメンテしづらいので別途対処する : [issues #18](https://github.com/cat2151/github-actions/issues/18)

# 結果
- agentにpromptを投げた
    - ※promptは、development-statusで生成したもの
- レビューした
    - agentがフルパスで実装した、ことがわかった
- userが分析し、 ../ のほうが適切と判断した
    - ※「事例」コーナーを、あわせて修正した
- そのように指示してagentに修正させた
- testする

# 結果
- test green
- closeする

{% endraw %}
```

### .github/actions-tmp/issue-notes/19.md
```md
{% raw %}
# issue project-summary の development-status 生成時、issue-notes/ 配下のmdファイルの内容を参照させる #19
[issues #19](https://github.com/cat2151/github-actions/issues/19)

# 何が困るの？
- issue解決に向けての次の一手の内容が実態に即していないことが多い。

# 対策案
- issue-notes/ 配下のmdファイルの内容を参照させる

# 備考
- さらにmd内に書かれているfileも、project内をcjsに検索させて添付させると、よりGeminiの生成品質が向上する可能性がある。
    - [issues #20](https://github.com/cat2151/github-actions/issues/20)
- さらにproject overviewでGeminiがまとめたmdも、Geminiに与えると、よりGeminiの生成品質が向上する可能性がある。
    - [issues #21](https://github.com/cat2151/github-actions/issues/21)
- さらに、Geminiに与えたpromptをfileにしてcommit pushしておくと、デバッグに役立つ可能性がある。
    - [issues #22](https://github.com/cat2151/github-actions/issues/22)

# close条件
- issues #22 がcloseされること。
- commitされたpromptを確認し、issue-notes/ 配下のmdファイルがpromptに添付されていること、が確認できること。

# 状況
- 課題、実装したがtestができていない
- 対策、issues #22 が実装されれば、testができる
- 対策、issues #22 のcloseを待つ

# 状況
- issues #22 がcloseされた
- testできるようになった
- commitされたpromptを確認した。issue-notes/ 配下のmdファイルがpromptに添付されていること、が確認できた

# closeする

{% endraw %}
```

### .github/actions-tmp/issue-notes/35.md
```md
{% raw %}
# issue issue-notes作成時に、既存のnotesを調査して不要note削除を行うようにする。clean up #35
[issues #35](https://github.com/cat2151/github-actions/issues/35)

# 定義：
- 紐付くissueがある
    - issueがopen中である → 必要note。PRを進めるために必要。
    - issueがcloseされた
        - noteの中身が、先頭2行だけで、あとは空である → 不要note。closeされたが、空っぽのnoteである。
        - noteの中身が、上記以外である → 必要note。closeされて、issueの履歴としてナレッジとなるnoteである。
- 紐付くissueがない
    - noteの中身が、先頭2行だけで、あとは空である → 不要note。issueが削除されたし、空っぽのnoteである。
    - noteの中身が、上記以外である → 必要note。issueが削除されたが、issueの履歴としてナレッジとなるnoteである。

# なぜこのワークフローymlで実施するの？
- 利用者の利用コストを下げるため。
- もし別ワークフローymlだと、全てのリポジトリに新たにワークフローymlが追加となり、導入初期コストが高い。
- 別ワークフローにするメリットが小さい
- 位置づけとしては、issue-noteのメンテは、このワークフローで行う、として許容範囲内である、と考える

{% endraw %}
```

### .github/actions-tmp/issue-notes/7.md
```md
{% raw %}
# issue issue note生成できるかのtest用 #7
[issues #7](https://github.com/cat2151/github-actions/issues/7)

- 生成できた
- closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/9.md
```md
{% raw %}
# issue 関数コールグラフhtmlビジュアライズが0件なので、原因を可視化する #9
[issues #9](https://github.com/cat2151/github-actions/issues/9)

# agentに修正させたり、人力で修正したりした
- agentがハルシネーションし、いろいろ根の深いバグにつながる、エラー隠蔽などを仕込んでいたため、検知が遅れた
- 詳しくはcommit logを参照のこと
- WSL + actの環境を少し変更、act起動時のコマンドライン引数を変更し、generated-docsをmountする（ほかはデフォルト挙動であるcpだけにする）ことで、デバッグ情報をコンテナ外に出力できるようにし、デバッグを効率化した

# test green

# closeとする

{% endraw %}
```

### src/gh_pr_phase_monitor/phase/pr_data_recorder.py
```py
{% raw %}
"""
Utilities for capturing PR snapshots to aid debugging of phase detection.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .llm_status_extractor import _extract_llm_statuses
from .phase_detector import (
    PHASE_LLM_WORKING,
    has_comments_with_reactions,
    llm_working_from_statuses,
    update_comment_reaction_resolution,
)
from .pr_html_fetcher import _fetch_pr_html, _html_to_simple_markdown
from .pr_html_analyzer import _determine_html_status
from .pr_html_saver import save_html_to_logs
from ..monitor.snapshot_markdown import _build_markdown, _prepare_markdown_raw, _summarize_reactions
from ..monitor.snapshot_path_utils import _build_snapshot_dir_name, _format_timestamp

# Snapshots are stored alongside screenshots (not inside) for easy discovery
DEFAULT_SNAPSHOT_BASE_DIR = Path("pr_phase_snapshots")

# Once flag to prevent duplicate snapshots within the same iteration
_recorded_in_current_iteration: Set[str] = set()

# Store previous iteration's content for comparison (PR key -> {json, html_md, llm_statuses})
_previous_pr_content: Dict[str, Dict[str, Any]] = {}


def _build_logs_analysis(pr_url: str, is_draft: bool, statuses: list) -> dict:
    """logs/pr/ 保存用の解析結果辞書を構築する。"""
    return {
        "pr_url": pr_url,
        "is_draft": is_draft,
        "llm_statuses": statuses,
        "status": _determine_html_status(statuses, is_draft),
    }


def _write_if_changed(path: Path, content: str) -> None:
    """Write content to a file only when it changed."""
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == content:
                return
        except OSError:
            # If reading fails (permissions/I/O), overwrite with new content below
            pass
    path.write_text(content, encoding="utf-8")


def _capture_llm_statuses(
    html: Optional[str],
    html_markdown: str,
    llm_status_path: Optional[Path] = None,
    result_dict: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Extract LLM statuses, persist to JSON if path provided, and return metadata."""
    statuses = _extract_llm_statuses(html, html_markdown)
    augmented_markdown = html_markdown

    if statuses:
        status_line = f"LLM status: {', '.join(statuses)}"
        augmented_markdown = f"{html_markdown}\n\n{status_line}" if html_markdown else status_line

        if llm_status_path:
            status_payload = json.dumps({"llm_statuses": statuses}, ensure_ascii=False, indent=2)
            _write_if_changed(llm_status_path, status_payload)
            if result_dict is not None:
                result_dict["llm_status_path"] = llm_status_path
                result_dict["llm_statuses"] = statuses
    else:
        if llm_status_path:
            status_payload = json.dumps({"llm_statuses": []}, ensure_ascii=False, indent=2)
            _write_if_changed(llm_status_path, status_payload)
            if result_dict is not None:
                result_dict["llm_status_path"] = llm_status_path
                result_dict["llm_statuses"] = []

    return {
        "statuses": statuses,
        "html_markdown_with_status": augmented_markdown,
    }


def save_pr_snapshot(
    pr: Dict[str, Any],
    reason: str,
    base_dir: Optional[Path] = None,
    current_time: Optional[datetime] = None,
    fetch_html: bool = True,
    html_content: Optional[str] = None,
) -> Dict[str, Any]:
    """Save raw PR data, HTML, and markdown summary to disk.

    Args:
        pr: PR data dictionary.
        reason: Reason for capturing the snapshot.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.
        fetch_html: Whether to fetch HTML page (default: True). Set to False to avoid blocking network calls.
        html_content: Optional pre-fetched HTML content. If provided, this HTML is used instead of fetching.

    Returns:
        Dictionary containing:
        - snapshot_dir, raw_path, markdown_path (Path objects)
        - html_path, html_md_path, llm_status_path (Path objects, if HTML was fetched)
        - saved_json, saved_html (str, the actual content that was saved)
        - llm_statuses (list[str], extracted LLM statuses when HTML is available)
    """
    effective_time = current_time if current_time is not None else datetime.now()

    base_path = Path(base_dir) if base_dir is not None else DEFAULT_SNAPSHOT_BASE_DIR
    base_path = base_path.expanduser().resolve()

    # Directory name without timestamp (e.g., owner_repo_PR123)
    snapshot_dir_name = _build_snapshot_dir_name(pr)
    snapshot_dir = base_path / snapshot_dir_name
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    # File prefix with timestamp (e.g., 20260102_030405)
    timestamp_str = _format_timestamp(effective_time)
    file_prefix = timestamp_str

    raw_path = snapshot_dir / f"{file_prefix}_raw.json"
    markdown_path = snapshot_dir / f"{file_prefix}_summary.md"
    html_path = snapshot_dir / f"{file_prefix}_page.html"
    html_md_path = snapshot_dir / f"{file_prefix}_page.md"
    llm_status_path = snapshot_dir / f"{file_prefix}_llm_statuses.json"

    reactions_summary = _summarize_reactions(pr.get("commentNodes", pr.get("comments", [])))
    markdown_raw_snapshot = _prepare_markdown_raw(pr)

    # Save raw JSON
    raw_json = json.dumps(pr, ensure_ascii=False, indent=2)
    _write_if_changed(raw_path, raw_json)

    # Save markdown summary
    markdown_content = _build_markdown(
        pr,
        reason,
        timestamp_str,
        reactions_summary,
        snapshot_dir_name,
        markdown_raw_snapshot,
    )
    _write_if_changed(markdown_path, markdown_content)

    # Fetch and save HTML page
    pr_url = pr.get("url", "")
    result_dict = {
        "snapshot_dir": snapshot_dir,
        "raw_path": raw_path,
        "markdown_path": markdown_path,
        "saved_json": raw_json,
        "saved_html": "",
    }

    # Use pre-fetched HTML if provided, otherwise fetch if requested
    if html_content:
        # Use provided HTML content
        _write_if_changed(html_path, html_content)
        result_dict["html_path"] = html_path
        result_dict["saved_html"] = html_content

        # Convert HTML to markdown for better readability
        html_as_markdown = _html_to_simple_markdown(html_content)
        captured = _capture_llm_statuses(html_content, html_as_markdown, llm_status_path, result_dict)
        if captured["html_markdown_with_status"]:
            _write_if_changed(html_md_path, captured["html_markdown_with_status"])
            result_dict["html_md_path"] = html_md_path
    elif fetch_html and pr_url:
        # Fetch HTML if not provided
        fetched_html = _fetch_pr_html(pr_url)
        if fetched_html:
            _write_if_changed(html_path, fetched_html)
            result_dict["html_path"] = html_path
            result_dict["saved_html"] = fetched_html

            # Convert HTML to markdown for better readability
            html_as_markdown = _html_to_simple_markdown(fetched_html)
            captured = _capture_llm_statuses(fetched_html, html_as_markdown, llm_status_path, result_dict)
            if captured["html_markdown_with_status"]:
                _write_if_changed(html_md_path, captured["html_markdown_with_status"])
                result_dict["html_md_path"] = html_md_path

    return result_dict


def record_reaction_snapshot(
    pr: Dict[str, Any],
    phase: str,
    base_dir: Optional[Path] = None,
    current_time: Optional[datetime] = None,
    html_content: Optional[str] = None,
    enable_snapshots: bool = True,
) -> Optional[Dict[str, Any]]:
    """Record a snapshot when comment reactions force LLM working detection.

    Uses content-based deduplication: only saves a new timestamped snapshot when
    the PR JSON or HTML content (converted to markdown) has changed since the previous iteration.
    HTML is converted to markdown before comparison to avoid false changes from HTML tag variations.

    Optimization: When snapshots are enabled, HTML is only fetched when JSON hasn't changed to
    avoid unnecessary network calls. When snapshots are disabled, HTML may still be fetched to
    capture LLM statuses and reaction resolution even if JSON changed.

    Args:
        pr: PR data dictionary.
        phase: Detected phase for the PR.
        base_dir: Optional base directory for storing snapshots.
        current_time: Optional timestamp for deterministic testing.
        html_content: Optional pre-fetched HTML content to avoid network calls.
        enable_snapshots: When False, only fetches data needed for LLM working detection
            without writing files to pr_phase_snapshots/.

    Returns:
        Paths for created snapshot files, or None when no snapshot is recorded.
    """
    if phase != PHASE_LLM_WORKING:
        return None

    comment_nodes = pr.get("commentNodes", pr.get("comments", []))
    pr_key = pr.get("url") or _build_snapshot_dir_name(pr)
    if not has_comments_with_reactions(comment_nodes):
        # Fetch HTML for Draft PRs without review requests to detect Copilot timeline
        # events (#266). Previously, when there were no reactions we skipped fetching HTML,
        # so llm_statuses were never populated even though both "started work" and
        # "finished work" events are present on the PR page. This special-case fetch ensures
        # we still capture those statuses for LLM working detection when reactions are absent.
        is_draft = pr.get("isDraft", False)
        review_requests = pr.get("reviewRequests", [])
        if is_draft and not review_requests:
            # Always fetch fresh HTML every iteration so we never miss a newly-posted
            # "finished work" event.  Cross-iteration caching here was the root cause of
            # #266 re-occurring: a "started work"-only cached value would suppress all
            # future re-fetches, preventing "finished work" from ever being detected.
            pr_url = pr.get("url", "")
            if html_content:
                fetched = html_content
            elif pr_url:
                fetched = _fetch_pr_html(pr_url)
            else:
                fetched = None
            if fetched:
                html_md = _html_to_simple_markdown(fetched)
                captured = _capture_llm_statuses(fetched, html_md)
                if captured.get("statuses"):
                    pr["llm_statuses"] = captured["statuses"]
                save_html_to_logs(
                    fetched, pr_url,
                    analysis=_build_logs_analysis(pr_url, is_draft, captured.get("statuses", [])),
                )
        return None

    # Check once flag: prevent duplicate recording within the same iteration
    if pr_key in _recorded_in_current_iteration:
        return None

    # Prepare content for comparison (must match the format saved in save_pr_snapshot)
    current_json = json.dumps(pr, ensure_ascii=False, indent=2)

    # Check content-based deduplication: compare with previous iteration
    previous_content = _previous_pr_content.get(pr_key, {})
    previous_json = previous_content.get("json", "")
    previous_html_md = previous_content.get("html_md", "")
    latest_llm_statuses: List[str] = previous_content.get("llm_statuses", []) or []

    # Short-circuit: if JSON changed, we know content changed (no need to fetch HTML for comparison)
    json_changed = current_json != previous_json

    # Only fetch HTML if JSON hasn't changed (to check if HTML changed)
    # This avoids unnecessary network calls when JSON already indicates a change
    current_html_md = ""
    fetched_html = html_content
    pr_url = pr.get("url", "")

    captured_status = {"html_markdown_with_status": "", "statuses": []}
    should_fetch_html = not json_changed or not enable_snapshots

    if html_content:
        current_html_md = _html_to_simple_markdown(html_content)
        captured_status = _capture_llm_statuses(html_content, current_html_md)
        current_html_md = captured_status["html_markdown_with_status"]
        if captured_status["statuses"]:
            latest_llm_statuses = captured_status["statuses"]
            pr["llm_statuses"] = latest_llm_statuses
        if pr_url:
            _is_draft = pr.get("isDraft", False)
            save_html_to_logs(
                html_content, pr_url,
                analysis=_build_logs_analysis(pr_url, _is_draft, captured_status.get("statuses", [])),
            )

    if fetched_html is None and pr_url and should_fetch_html:
        # Fetch HTML when needed for deduplication or status capture
        fetched_html = _fetch_pr_html(pr_url)
        if fetched_html:
            # Convert HTML to markdown for comparison to avoid HTML tag noise
            current_html_md = _html_to_simple_markdown(fetched_html)
            captured_status = _capture_llm_statuses(fetched_html, current_html_md)
            current_html_md = captured_status["html_markdown_with_status"]
            if captured_status["statuses"]:
                latest_llm_statuses = captured_status["statuses"]
                pr["llm_statuses"] = latest_llm_statuses
            _is_draft = pr.get("isDraft", False)
            save_html_to_logs(
                fetched_html, pr_url,
                analysis=_build_logs_analysis(pr_url, _is_draft, captured_status.get("statuses", [])),
            )

    # Check if content has changed (compare markdown instead of raw HTML)
    html_changed = current_html_md != previous_html_md
    content_changed = json_changed or html_changed

    if not content_changed and previous_json:
        # Content unchanged, mark as recorded and skip saving
        if latest_llm_statuses:
            pr["llm_statuses"] = latest_llm_statuses
            if pr_key in _previous_pr_content:
                _previous_pr_content[pr_key]["llm_statuses"] = latest_llm_statuses
        _recorded_in_current_iteration.add(pr_key)
        return None

    # When snapshot saving is disabled, still fetch and store metadata for LLM working detection
    if not enable_snapshots:
        if captured_status.get("statuses"):
            latest_llm_statuses = captured_status["statuses"]
            pr["llm_statuses"] = latest_llm_statuses

        if current_html_md:
            llm_working = llm_working_from_statuses(captured_status.get("statuses", []))
            reactions_finished = llm_working is False
            update_comment_reaction_resolution(pr, comment_nodes, reactions_finished)

        _previous_pr_content[pr_key] = {
            "json": current_json,
            "html_md": current_html_md,
            "llm_statuses": latest_llm_statuses,
        }
        _recorded_in_current_iteration.add(pr_key)
        return None

    # Content changed or first time: save snapshot with timestamp
    # Pass pre-fetched HTML to avoid double-fetch
    snapshot_paths = save_pr_snapshot(
        pr,
        reason="comment_reactions_detected",
        base_dir=base_dir,
        current_time=current_time,
        html_content=fetched_html,  # Pass pre-fetched HTML if available
    )

    snapshot_llm_statuses = snapshot_paths.get("llm_statuses")
    if snapshot_llm_statuses:
        latest_llm_statuses = snapshot_llm_statuses
        pr["llm_statuses"] = latest_llm_statuses

    # If HTML wasn't fetched during comparison (because JSON changed), fetch it now for caching
    # This ensures we have HTML for the next iteration's comparison
    if fetched_html is None and pr_url:
        # HTML was saved by save_pr_snapshot, retrieve it from the result
        saved_html = snapshot_paths.get("saved_html", "")
        if saved_html:
            current_html_md = _html_to_simple_markdown(saved_html)
            captured_status = _capture_llm_statuses(saved_html, current_html_md)
            current_html_md = captured_status["html_markdown_with_status"]
            if captured_status["statuses"]:
                latest_llm_statuses = captured_status["statuses"]
                pr["llm_statuses"] = latest_llm_statuses
            _is_draft = pr.get("isDraft", False)
            save_html_to_logs(
                saved_html, pr_url,
                analysis=_build_logs_analysis(pr_url, _is_draft, captured_status.get("statuses", [])),
            )

    # Update reaction resolution cache based on HTML snapshot content
    if current_html_md:
        llm_working = llm_working_from_statuses(captured_status.get("statuses", []))
        reactions_finished = llm_working is False
        update_comment_reaction_resolution(pr, comment_nodes, reactions_finished)

    # Update previous content cache for next iteration
    # Store markdown version of HTML to avoid false changes from HTML tag variations
    _previous_pr_content[pr_key] = {
        "json": snapshot_paths.get("saved_json", current_json),
        "html_md": current_html_md,
        "llm_statuses": latest_llm_statuses,
    }

    # Mark as recorded in current iteration
    _recorded_in_current_iteration.add(pr_key)

    return snapshot_paths


def reset_snapshot_cache(clear_content_cache: bool = False) -> None:
    """Clear the once flag for the current iteration.

    This should be called at the start of each monitoring iteration to allow
    recording snapshots again. The previous content cache is preserved for
    content-based deduplication across iterations unless explicitly cleared.

    Args:
        clear_content_cache: If True, also clear the previous content cache.
            This should be set to True for tests to ensure clean state.
    """
    _recorded_in_current_iteration.clear()
    if clear_content_cache:
        _previous_pr_content.clear()

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
3884b9d Merge pull request #344 from cat2151/copilot/remove-deprecated-documents
4329de4 Delete obsolete documents (STRUCTURE.md, PHASE3_MERGE_IMPLEMENTATION.md, MERGE_CONFIGURATION_EXAMPLES.md, generated-docs/)
64a435f Initial plan
b33821a Merge pull request #343 from cat2151/copilot/fix-file-saving-feature
5c50f96 Add save_html_to_logs call in html_content pre-provided path of record_reaction_snapshot
dbdd149 Fix PR 338: always save HTML/JSON to logs/pr/ when fetched, with print for both save/skip cases
67ad9ce Initial plan
343dd3c Merge pull request #340 from cat2151/copilot/add-auto-update-logging-mode
122ed5a fix: address review feedback on foreground auto-update (flush, message, config validation)
8c6e9e1 feat: add foreground startup auto-update mode with explicit prints

### 変更されたファイル:
.github/copilot-instructions.md
MERGE_CONFIGURATION_EXAMPLES.md
PHASE3_MERGE_IMPLEMENTATION.md
STRUCTURE.md
generated-docs/development-status-generated-prompt.md
generated-docs/development-status.md
generated-docs/project-overview-generated-prompt.md
generated-docs/project-overview.md
pyproject.toml
src/gh_pr_phase_monitor/__init__.py
src/gh_pr_phase_monitor/actions/__init__.py
src/gh_pr_phase_monitor/actions/pr_actions.py
src/gh_pr_phase_monitor/browser/__init__.py
src/gh_pr_phase_monitor/browser/browser_automation.py
src/gh_pr_phase_monitor/browser/browser_cooldown.py
src/gh_pr_phase_monitor/browser/button_clicker.py
src/gh_pr_phase_monitor/browser/click_config_validator.py
src/gh_pr_phase_monitor/browser/window_manager.py
src/gh_pr_phase_monitor/core/__init__.py
src/gh_pr_phase_monitor/core/colors.py
src/gh_pr_phase_monitor/core/config.py
src/gh_pr_phase_monitor/core/config_printer.py
src/gh_pr_phase_monitor/core/interval_parser.py
src/gh_pr_phase_monitor/core/process_utils.py
src/gh_pr_phase_monitor/core/time_utils.py
src/gh_pr_phase_monitor/github/__init__.py
src/gh_pr_phase_monitor/github/comment_fetcher.py
src/gh_pr_phase_monitor/github/comment_manager.py
src/gh_pr_phase_monitor/github/github_auth.py
src/gh_pr_phase_monitor/github/github_client.py
src/gh_pr_phase_monitor/github/graphql_client.py
src/gh_pr_phase_monitor/github/issue_fetcher.py
src/gh_pr_phase_monitor/github/pr_fetcher.py
src/gh_pr_phase_monitor/github/rate_limit_handler.py
src/gh_pr_phase_monitor/github/repository_fetcher.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/monitor/__init__.py
src/gh_pr_phase_monitor/monitor/auto_updater.py
src/gh_pr_phase_monitor/monitor/local_repo_watcher.py
src/gh_pr_phase_monitor/monitor/monitor.py
src/gh_pr_phase_monitor/monitor/pages_watcher.py
src/gh_pr_phase_monitor/monitor/snapshot_markdown.py
src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py
src/gh_pr_phase_monitor/monitor/state_tracker.py
src/gh_pr_phase_monitor/phase/__init__.py
src/gh_pr_phase_monitor/phase/llm_status_extractor.py
src/gh_pr_phase_monitor/phase/phase_detector.py
src/gh_pr_phase_monitor/phase/phase_detector_graphql.py
src/gh_pr_phase_monitor/phase/pr_data_recorder.py
src/gh_pr_phase_monitor/phase/pr_html_analyzer.py
src/gh_pr_phase_monitor/phase/pr_html_fetcher.py
src/gh_pr_phase_monitor/phase/pr_html_saver.py
src/gh_pr_phase_monitor/ui/__init__.py
src/gh_pr_phase_monitor/ui/display.py
src/gh_pr_phase_monitor/ui/notification_window.py
src/gh_pr_phase_monitor/ui/notifier.py
src/gh_pr_phase_monitor/ui/wait_handler.py
tests/test_assign_issue_to_copilot.py
tests/test_auto_update_config.py
tests/test_auto_updater.py
tests/test_batteries_included_defaults.py
tests/test_browser_automation.py
tests/test_browser_automation_click.py
tests/test_browser_automation_ocr.py
tests/test_browser_automation_window.py
tests/test_check_process_before_autoraise.py
tests/test_color_scheme_config.py
tests/test_config_rulesets.py
tests/test_config_rulesets_features.py
tests/test_elapsed_time_display.py
tests/test_fetch_pr_html.py
tests/test_graphql_client_rate_limit.py
tests/test_graphql_query_intent_display.py
tests/test_hot_reload.py
tests/test_html_to_markdown.py
tests/test_integration_issue_fetching.py
tests/test_interval_contamination_bug.py
tests/test_issue_assignment_priority.py
tests/test_issue_fetching.py
tests/test_local_repo_watcher.py
tests/test_local_repo_watcher_background.py
tests/test_max_llm_working_parallel.py
tests/test_no_change_timeout.py
tests/test_no_open_prs_issue_display.py
tests/test_notification.py
tests/test_open_browser_cooldown.py
tests/test_pages_watcher.py
tests/test_phase3_merge.py
tests/test_phase_detection.py
tests/test_phase_detection_llm_status.py
tests/test_phase_detection_real_prs.py
tests/test_post_comment.py
tests/test_post_phase3_comment.py
tests/test_pr_actions.py
tests/test_pr_actions_dry_run.py
tests/test_pr_actions_rulesets_features.py
tests/test_pr_actions_with_rulesets.py
tests/test_pr_data_recorder.py
tests/test_pr_data_recorder_html.py
tests/test_pr_data_recorder_json.py
tests/test_pr_html_analyzer.py
tests/test_pr_title_fix.py
tests/test_rate_limit_usage_display.py
tests/test_repos_with_prs_structure.py
tests/test_show_issues_when_pr_count_less_than_3.py
tests/test_status_summary.py
tests/test_validate_phase3_merge_config.py
tests/test_verbose_config.py
tests/test_wait_handler_callback.py


---
Generated at: 2026-03-06 07:03:53 JST
