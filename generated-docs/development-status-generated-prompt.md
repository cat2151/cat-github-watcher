Last updated: 2026-03-11

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
## [Issue #414](../issue-notes/414.md): 大きなファイルの検出: 2個のファイルが500行を超えています
以下のファイルが500行を超えています。リファクタリングを検討してください。

## 検出されたファイル

| ファイル | 行数 | 超過行数 |
|---------|------|----------|
| `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` | 543 | +43 |
| `tests/test_local_repo_watcher.py` | 524 | +24 |

## テスト実施のお願い

- リファクタリング前後にテストを実行し、それぞれのテスト失敗件数を報告してください
- リファクタリング前後のど...
ラベル: refactoring, code-quality, automated
--- issue-notes/414.md の内容 ---

```markdown

```

## [Issue #413](../issue-notes/413.md): Auto-run `cargo install --force` after git pull for configured Rust repos
- [x] Add `cargo_install_repos` config option (list of repo names)
- [x] Add `_run_cargo_install(path)` + `_summarize_cargo_error()` for multi-line cargo error normalization
- [x] Run `cargo install --force --path <path>` after successful pull for matching repos (both sync and background paths)
- [x...
ラベル: 
--- issue-notes/413.md の内容 ---

```markdown

```

## [Issue #412](../issue-notes/412.md): cargo installで運用するリポジトリは、pullしてもそのままでは最新にならないため、UXに改善の余地がありそう

ラベル: 
--- issue-notes/412.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/12.md
```md
{% raw %}
# issue project-summary を他projectから使いやすくする #12
[issues #12](https://github.com/cat2151/github-actions/issues/12)

# 保留、別projectでの検証待ちのもの
- promptsをcall側ymlで指定可能にする
  - 保留の理由
    - YAGNI原則
      - 現状の共通workflow側のpromptsで問題ないうちは、保留とする
        - そのままで使える可能性が高い見込み
      - 検証が必要
      - 別promptsを実際に書く必要が出たときに、追加実装をする
# 課題、 docs/ をメンテする
- 対象は、 daily-summary-setup.md
- call-daily-project-summary.yml の導入手順を書く
- どうする？
  - 次の日次バッチでagent用promptを生成させる
- 結果
  - 生成させた
  - 導入手順をメンテさせた
  - 人力でさらにメンテした
  - これでOKと判断する。
  - あとは必要に応じてissue起票すればよい、今すぐのissue起票は不要（YAGNI原則）、と判断する

# closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/13.md
```md
{% raw %}
# issue issue-note を他projectから使いやすくする #13
[issues #13](https://github.com/cat2151/github-actions/issues/13)

- docs
    - call導入手順を書く

{% endraw %}
```

### .github/actions-tmp/issue-notes/14.md
```md
{% raw %}
# issue Development Status のdocument生成において、最初の小さな一歩 を実現する用のプロンプト生成がされなくなっている #14
[issues #14](https://github.com/cat2151/github-actions/issues/14)

## 何が困るの？
- #11の場合
- 期待値
    - 最初の小さな一歩 : [Issue #11]のtranslateについて、現在の処理フローを確認し、外部プロジェクトから利用する際にどのような情報（翻訳対象のファイルパス、ターゲット言語設定など）が必要となるかを明確にする。これにより、再利用可能なワークフロー設計の基礎を築く。
    - 最初の小さな一歩をagentに実行させるためのプロンプト : 現在のGitHub Actions翻訳ワークフロー（translate-readme.yml、call-translate-readme.yml、translate-readme.cjs）を分析し、外部プロジェクトから利用する際に必要となる設定項目を洗い出してください。具体的には、以下の観点から調査し、markdown形式でまとめてください：1) 必須入力パラメータ（現在はtarget-branchのみ） 2) 必須シークレット（GEMINI_API_KEY） 3) ファイル配置の前提条件（README.ja.md の存在、配置場所） 4) 翻訳対象ファイル名の制約（現在はREADME固定） 5) ブランチ・トリガー設定の制約 6) 外部プロジェクトでの利用時に追加で必要となりそうな設定項目の提案
- 実際の結果
    - 最初の小さな一歩: [Issue #11]のtranslateについて、現在の処理フローを確認し、外部プロジェクトから利用する際にどのような情報（翻訳対象のファイルパス、ターゲット言語設定など）が必要となるかを明確にする。これにより、再利用可能なワークフロー設計の基礎を築く。

## close条件
- 期待値のように、Agent実行プロンプト、が生成されること

## agentに修正させた
- development-status.md を修正させた
- test green

## closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/2.md
```md
{% raw %}
# issue GitHub Actions「関数コールグラフhtmlビジュアライズ生成」を共通ワークフロー化する #2
[issues #2](https://github.com/cat2151/github-actions/issues/2)


# prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlファイルを、以下の2つのファイルに分割してください。
1. 共通ワークフロー       cat2151/github-actions/.github/workflows/callgraph_enhanced.yml
2. 呼び出し元ワークフロー cat2151/github-actions/.github/workflows/call-callgraph_enhanced.yml
まずplanしてください
```

# 結果
- indent
    - linter？がindentのエラーを出しているがyml内容は見た感じOK
    - テキストエディタとagentの相性問題と判断する
    - 別のテキストエディタでsaveしなおし、テキストエディタをreload
    - indentのエラーは解消した
- LLMレビュー
    - agent以外の複数のLLMにレビューさせる
    - prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
以下の2つのファイルをレビューしてください。最優先で、エラーが発生するかどうかだけレビューしてください。エラー以外の改善事項のチェックをするかわりに、エラー発生有無チェックに最大限注力してください。

--- 共通ワークフロー

# GitHub Actions Reusable Workflow for Call Graph Generation
name: Generate Call Graph

# TODO Windowsネイティブでのtestをしていた名残が残っているので、今後整理していく。今はWSL act でtestしており、Windowsネイティブ環境依存問題が解決した
#  ChatGPTにレビューさせるとそこそこ有用そうな提案が得られたので、今後それをやる予定
#  agentに自己チェックさせる手も、セカンドオピニオンとして選択肢に入れておく

on:
  workflow_call:

jobs:
  check-commits:
    runs-on: ubuntu-latest
    outputs:
      should-run: ${{ steps.check.outputs.should-run }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 50 # 過去のコミットを取得

      - name: Check for user commits in last 24 hours
        id: check
        run: |
          node .github/scripts/callgraph_enhanced/check-commits.cjs

  generate-callgraph:
    needs: check-commits
    if: needs.check-commits.outputs.should-run == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      security-events: write
      actions: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set Git identity
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

      - name: Remove old CodeQL packages cache
        run: rm -rf ~/.codeql/packages

      - name: Check Node.js version
        run: |
          node .github/scripts/callgraph_enhanced/check-node-version.cjs

      - name: Install CodeQL CLI
        run: |
          wget https://github.com/github/codeql-cli-binaries/releases/download/v2.22.1/codeql-linux64.zip
          unzip codeql-linux64.zip
          sudo mv codeql /opt/codeql
          echo "/opt/codeql" >> $GITHUB_PATH

      - name: Install CodeQL query packs
        run: |
          /opt/codeql/codeql pack install .github/codeql-queries

      - name: Check CodeQL exists
        run: |
          node .github/scripts/callgraph_enhanced/check-codeql-exists.cjs

      - name: Verify CodeQL Configuration
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs verify-config

      - name: Remove existing CodeQL DB (if any)
        run: |
          rm -rf codeql-db

      - name: Perform CodeQL Analysis
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs analyze

      - name: Check CodeQL Analysis Results
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs check-results

      - name: Debug CodeQL execution
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs debug

      - name: Wait for CodeQL results
        run: |
          node -e "setTimeout(()=>{}, 10000)"

      - name: Find and process CodeQL results
        run: |
          node .github/scripts/callgraph_enhanced/find-process-results.cjs

      - name: Generate HTML graph
        run: |
          node .github/scripts/callgraph_enhanced/generate-html-graph.cjs

      - name: Copy files to generated-docs and commit results
        run: |
          node .github/scripts/callgraph_enhanced/copy-commit-results.cjs

--- 呼び出し元
# 呼び出し元ワークフロー: call-callgraph_enhanced.yml
name: Call Call Graph Enhanced

on:
  schedule:
    # 毎日午前5時(JST) = UTC 20:00前日
    - cron: '0 20 * * *'
  workflow_dispatch:

jobs:
  call-callgraph-enhanced:
    # uses: cat2151/github-actions/.github/workflows/callgraph_enhanced.yml
    uses: ./.github/workflows/callgraph_enhanced.yml # ローカルでのテスト用
```

# レビュー結果OKと判断する
- レビュー結果を人力でレビューした形になった

# test
- #4 同様にローカル WSL + act でtestする
- エラー。userのtest設計ミス。
  - scriptの挙動 : src/ がある前提
  - 今回の共通ワークフローのリポジトリ : src/ がない
  - 今回testで実現したいこと
    - 仮のソースでよいので、関数コールグラフを生成させる
  - 対策
    - src/ にダミーを配置する
- test green
  - ただしcommit pushはしてないので、html内容が0件NG、といったケースの検知はできない
  - もしそうなったら別issueとしよう

# test green

# commit用に、yml 呼び出し元 uses をlocal用から本番用に書き換える

# closeとする
- もしhtml内容が0件NG、などになったら、別issueとするつもり

{% endraw %}
```

### .github/actions-tmp/issue-notes/3.md
```md
{% raw %}
# issue GitHub Actions「issue note生成」を共通ワークフロー化する #3
[issues #3](https://github.com/cat2151/github-actions/issues/3)

- 前提
  - userは、translateのworkflowを共通ワークフロー化し、動くようにしたので、共通ワークフロー化の知識がある
  - よって、今回は、promptでplanさせ、そのplanをuserがレビューし、planの改善を指示できるので、ハルシネーションのリスクを下げることができる

- prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlはまだ共通ワークフロー化されず、
呼び出し元からコピーされたままの状態です。
このymlファイル名のまま、
中身を共通ワークフロー化してください。
呼び出し元ymlは別途書きますので気にしないでください。
まずplanしてください
```

- plan 生成結果
```
共通ワークフロー化のためのplanは以下の通りです。

1. 目的
現在の issue-note.yml を「共通ワークフロー」として再設計し、他リポジトリや他ワークフローから workflow_call で呼び出せるようにする。
2. 主な変更点
on: トリガーを workflow_call に変更（直接イベントで起動しない）。
必要な入力（inputs）やシークレット（secrets）を workflow_call セクションで定義。
github.event.issue などのイベント依存部分を、inputs経由で受け取る形に修正。
既存の処理（issueノート生成、コミット、issue body更新）はそのまま活かすが、パラメータ化する。
3. 具体的な修正内容
on: issues: → on: workflow_call: に変更。
inputs で必要な値（例: issue_title, issue_number, issue_body, issue_url など）を受け取る。
スクリプト内の ${{ github.event.issue.xxx }} を ${{ inputs.xxx }} に置換。
github-script ステップも同様にinputsを参照。
必要に応じて secrets も workflow_call で受け取れるようにする。
4. ファイル名・配置
ファイル名はそのまま issue-note.yml。
配置場所は workflows でOK（共通ワークフローとしてもこの場所で良い）。
5. 呼び出し元への影響
呼び出し元ワークフローで uses: <repo>/.github/workflows/issue-note.yml@main のように参照し、inputsを渡す形になる。
このplanで進めます。次に、実際の共通ワークフロー化のためのyml修正案を作成しますか？
```

- userがplanレビューし、OKを出した
- agentに生成結果ymlをレビューさせた、OKとなった
  - userはこのレビューは認知負荷が高いのでskipとする（単純な細かい間違い探し作業になるので、それはagentに任せた）
-  エラー。呼び出し元ymlのエラーがあり修正。共通ワークフローのエラー指摘があり、共通ワークフロー側の修正が必要となった
```
原因の分析：

呼び出し元（tonejs-mml-to-jsonのissue-note.yml）は、reusable workflow（cat2151/github-actions/.github/workflows/issue-note.yml@main）をusesで呼び出し、inputsをwithで渡しています。
共通ワークフロー（reusable workflow）は inputs を workflow_call で受け取り、各ステップで ${{ inputs.xxx }} で参照しています。
しかし、エラーが発生したのは actions/github-script@v7 の script 内です。
エラーの本質的な原因：

actions/github-script の script: で ${{ inputs.issue_number }} のような式を直接 JavaScript テンプレートリテラル内で使っていますが、これはサポートされていません。
script: の中は JavaScript であり、YAMLの ${{ ... }} は展開されません（または意図通りに展開されません）。
そのため、inputs 変数は script 内の JavaScript で未定義となり、ReferenceError になります。
正しい書き方：

actions/github-script の script: でワークフローの inputs を使いたい場合は、with: で input を environment 変数や script の引数として渡し、JavaScript で process.env から取得するか、github-script の input 機能を使う必要があります。
例（修正版）：

このように、inputs の値を env で渡し、script 内では process.env で参照してください。

まとめ：

actions/github-script の script 内で ${{ inputs.xxx }} を直接使うと ReferenceError になる
env: で値を渡し、process.env で参照するのが正しい
修正が必要です。修正版のワークフローが必要な場合はお知らせください。
```

- test green
- closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/4.md
```md
{% raw %}
# issue GitHub Actions「project概要生成」を共通ワークフロー化する #4
[issues #4](https://github.com/cat2151/github-actions/issues/4)

# prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlファイルを、以下の2つのファイルに分割してください。
1. 共通ワークフロー       cat2151/github-actions/.github/workflows/daily-project-summary.yml
2. 呼び出し元ワークフロー cat2151/github-actions/.github/workflows/call-daily-project-summary.yml
まずplanしてください
```

# 結果、あちこちハルシネーションのあるymlが生成された
- agentの挙動があからさまにハルシネーション
    - インデントが修正できない、「失敗した」という
    - 構文誤りを認識できない
- 人力で修正した

# このagentによるセルフレビューが信頼できないため、別のLLMによるセカンドオピニオンを試す
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
以下の2つのファイルをレビューしてください。最優先で、エラーが発生するかどうかだけレビューてください。エラー以外の改善事項のチェックをするかわりに、エラー発生有無チェックに最大限注力してください。

--- 呼び出し元

name: Call Daily Project Summary

on:
  schedule:
    # 日本時間 07:00 (UTC 22:00 前日)
    - cron: '0 22 * * *'
  workflow_dispatch:

jobs:
  call-daily-project-summary:
    uses: cat2151/github-actions/.github/workflows/daily-project-summary.yml
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

--- 共通ワークフロー
name: Daily Project Summary
on:
  workflow_call:

jobs:
  generate-summary:
    runs-on: ubuntu-latest

    permissions:
      contents: write
      issues: read
      pull-requests: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0  # 履歴を取得するため

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          # 一時的なディレクトリで依存関係をインストール
          mkdir -p /tmp/summary-deps
          cd /tmp/summary-deps
          npm init -y
          npm install @google/generative-ai @octokit/rest
          # generated-docsディレクトリを作成
          mkdir -p $GITHUB_WORKSPACE/generated-docs

      - name: Generate project summary
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          NODE_PATH: /tmp/summary-deps/node_modules
        run: |
          node .github/scripts/generate-project-summary.cjs

      - name: Check for generated summaries
        id: check_summaries
        run: |
          if [ -f "generated-docs/project-overview.md" ] && [ -f "generated-docs/development-status.md" ]; then
            echo "summaries_generated=true" >> $GITHUB_OUTPUT
          else
            echo "summaries_generated=false" >> $GITHUB_OUTPUT
          fi

      - name: Commit and push summaries
        if: steps.check_summaries.outputs.summaries_generated == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          # package.jsonの変更のみリセット（generated-docsは保持）
          git restore package.json 2>/dev/null || true
          # サマリーファイルのみを追加
          git add generated-docs/project-overview.md
          git add generated-docs/development-status.md
          git commit -m "Update project summaries (overview & development status)"
          git push

      - name: Summary generation result
        run: |
          if [ "${{ steps.check_summaries.outputs.summaries_generated }}" == "true" ]; then
            echo "✅ Project summaries updated successfully"
            echo "📊 Generated: project-overview.md & development-status.md"
          else
            echo "ℹ️ No summaries generated (likely no user commits in the last 24 hours)"
          fi
```

# 上記promptで、2つのLLMにレビューさせ、合格した

# 細部を、先行する2つのymlを参照に手直しした

# ローカルtestをしてからcommitできるとよい。方法を検討する
- ローカルtestのメリット
    - 素早く修正のサイクルをまわせる
    - ムダにgit historyを汚さない
        - これまでの事例：「実装したつもり」「エラー。修正したつもり」「エラー。修正したつもり」...（以降エラー多数）
- 方法
    - ※検討、WSL + act を環境構築済みである。test可能であると判断する
    - 呼び出し元のURLをコメントアウトし、相対パス記述にする
    - ※備考、テスト成功すると結果がcommit pushされる。それでよしとする
- 結果
    - OK
    - secretsを簡略化できるか試した、できなかった、現状のsecrets記述が今わかっている範囲でベストと判断する
    - OK

# test green

# commit用に、yml 呼び出し元 uses をlocal用から本番用に書き換える

# closeとする

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
from typing import Dict, List, Optional, Set

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

# Repos that reached phase3A and are awaiting post-merge pullable re-check.
# When updatedAt changes for these repos (e.g. user merged the PR), we trigger
# a new pullable check even though there are no open PRs.
_repos_awaiting_post_phase3_check: Set[str] = set()


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
    pulled_successfully = False

    if result["status"] == STATUS_PULLABLE:
        detail = f"behind {result['behind']}"
        lines.append(f"  {Colors.GREEN}[PULLABLE]{Colors.RESET} {result['name']}  ({detail})")
        if enable_pull:
            ok, msg = _pull_repo(result["path"])
            if ok:
                lines.append(f"    ✓ pull 完了: {result['name']}")
                pulled_successfully = True
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
        if pulled_successfully:
            _repos_awaiting_post_phase3_check.discard(result["name"])


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
        # Track this repo for post-merge auto-pull re-check regardless of current state
        _repos_awaiting_post_phase3_check.add(repo_name)
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


def notify_repos_updated_after_phase3(changed_repo_names: Set[str], config: dict, github_username: str) -> None:
    """phase3A済みリポジトリのupdatedAtが変化したらpullable検査を再トリガーする。

    PRをmerge/closeした後にupdatedAtが変化したリポジトリについて、
    open PRが0件でも自動pullが行われるようにするための仕組み。

    phase3Aを検知済みのリポジトリが changed_repo_names に含まれる場合、
    そのリポジトリのpullable検査を再度バックグラウンドで開始する。

    Args:
        changed_repo_names: updatedAt が変化したリポジトリ名の集合。
        config: Configuration dictionary loaded from TOML.
        github_username: The current GitHub user's login name.
    """
    with _state_lock:
        repos_to_recheck: List[str] = []
        for repo_name in changed_repo_names:
            if repo_name not in _repos_awaiting_post_phase3_check:
                continue
            current_state = _repo_states.get(repo_name)
            # CHECKING系状態のときは状態を消さず、再チェックもスキップする
            if current_state in (REPO_STATE_STARTUP_CHECKING, REPO_STATE_CHECKING):
                continue
            # DONE のときだけ状態をリセットして再チェックを許可する
            if current_state == REPO_STATE_DONE:
                _repo_states.pop(repo_name, None)
            repos_to_recheck.append(repo_name)

    # Call notify_phase3_detected outside the lock to avoid deadlock
    for repo_name in repos_to_recheck:
        print(f"  phase3A済みリポジトリのupdatedAt変化を検知: {repo_name} → pullable再確認")
        notify_phase3_detected(repo_name, config, github_username)


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

### tests/test_local_repo_watcher.py
```py
{% raw %}
"""Tests for local_repo_watcher module."""

from __future__ import annotations

import importlib
import os
import pathlib
import sys
import tempfile
import types

import pytest

sys.modules.setdefault("mouseinfo", types.SimpleNamespace(MouseInfoWindow=lambda: None))
sys.modules.setdefault("pyautogui", types.ModuleType("pyautogui"))
sys.modules.setdefault("pygetwindow", types.ModuleType("pygetwindow"))
sys.modules.setdefault("pytesseract", types.ModuleType("pytesseract"))
sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
sys.modules.setdefault("tkinter.messagebox", types.ModuleType("tkinter.messagebox"))
os.environ.setdefault("DISPLAY", ":0")

local_repo_watcher = importlib.import_module("src.gh_pr_phase_monitor.monitor.local_repo_watcher")


@pytest.fixture(autouse=True)
def reset_last_check_time():
    """Reset throttle timer before each test so checks always run."""
    original = local_repo_watcher._last_local_check_time
    local_repo_watcher._last_local_check_time = 0.0
    yield
    local_repo_watcher._last_local_check_time = original


@pytest.fixture(autouse=True)
def reset_phase3_tracking():
    """Reset phase3 post-merge tracking state before each test."""
    # These structures are mutated by background threads in local_repo_watcher;
    # take the module's state lock to avoid races during tests.
    with local_repo_watcher._state_lock:
        local_repo_watcher._repos_awaiting_post_phase3_check.clear()
        local_repo_watcher._repo_states.clear()
        local_repo_watcher._pending_lines.clear()
        local_repo_watcher._pending_needs_restart = False
        local_repo_watcher._startup_started = False
    yield
    with local_repo_watcher._state_lock:
        local_repo_watcher._repos_awaiting_post_phase3_check.clear()
        local_repo_watcher._repo_states.clear()
        local_repo_watcher._pending_lines.clear()
        local_repo_watcher._pending_needs_restart = False
        local_repo_watcher._startup_started = False


class TestIsTargetRepo:
    """Tests for _is_target_repo helper."""

    def test_https_url_matches_correct_user(self):
        assert local_repo_watcher._is_target_repo("https://github.com/myuser/myrepo.git", "myuser")

    def test_ssh_url_matches_correct_user(self):
        assert local_repo_watcher._is_target_repo("git@github.com:myuser/myrepo.git", "myuser")

    def test_does_not_match_different_user(self):
        assert not local_repo_watcher._is_target_repo("https://github.com/otheruser/myrepo.git", "myuser")

    def test_non_github_url_not_matched(self):
        assert not local_repo_watcher._is_target_repo("https://gitlab.com/myuser/myrepo.git", "myuser")

    def test_case_insensitive_matching(self):
        assert local_repo_watcher._is_target_repo("https://github.com/MyUser/MyRepo.git", "myuser")

    def test_fake_github_domain_not_matched(self):
        """URLs like 'github.com.evil.com' must not be accepted."""
        assert not local_repo_watcher._is_target_repo("https://github.com.evil.com/myuser/repo.git", "myuser")

    def test_notgithub_domain_not_matched(self):
        """URLs like 'notgithub.com' must not be accepted."""
        assert not local_repo_watcher._is_target_repo("https://notgithub.com/myuser/repo.git", "myuser")


class TestStatusClassification:
    """Tests for the status classification in _check_repo."""

    def _make_result(self, behind: int, ahead: int, dirty: bool) -> str:
        """Helper: run classification logic directly and return the status."""
        # Reproduce the classification logic from _check_repo
        status = local_repo_watcher.STATUS_UNKNOWN
        if behind == 0:
            status = local_repo_watcher.STATUS_UP_TO_DATE
        elif behind > 0 and ahead > 0:
            status = local_repo_watcher.STATUS_DIVERGED
        elif behind > 0 and ahead == 0:
            status = local_repo_watcher.STATUS_UNKNOWN if dirty else local_repo_watcher.STATUS_PULLABLE
        return status

    def test_behind_only_clean_is_pullable(self):
        assert self._make_result(behind=3, ahead=0, dirty=False) == local_repo_watcher.STATUS_PULLABLE

    def test_behind_only_dirty_is_unknown(self):
        assert self._make_result(behind=3, ahead=0, dirty=True) == local_repo_watcher.STATUS_UNKNOWN

    def test_ahead_only_is_up_to_date(self):
        """ahead-only (no behind) means nothing to pull → up_to_date."""
        assert self._make_result(behind=0, ahead=2, dirty=False) == local_repo_watcher.STATUS_UP_TO_DATE

    def test_both_behind_and_ahead_is_diverged(self):
        assert self._make_result(behind=2, ahead=1, dirty=False) == local_repo_watcher.STATUS_DIVERGED

    def test_up_to_date_when_behind_zero(self):
        assert self._make_result(behind=0, ahead=0, dirty=False) == local_repo_watcher.STATUS_UP_TO_DATE


class TestCheckLocalRepos:
    """Tests for the main check_local_repos function."""

    def test_no_pullable_repos_produces_no_output(self, monkeypatch, capsys):
        """When no repos are pullable/diverged, nothing should be printed."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        # Simulate: base_dir has one repo, already up-to-date
        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 0,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_UP_TO_DATE,
                "error": None,
                "is_target": True,
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir}
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "PULLABLE" not in captured.out
        assert "DRY-RUN" not in captured.out

    def test_pullable_repo_displayed_in_dry_run(self, monkeypatch, capsys):
        """Pullable repos should display a DRY-RUN message when auto-pull is disabled."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 3,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "PULLABLE" in captured.out
        assert "myrepo" in captured.out
        assert "DRY-RUN" in captured.out
        assert "auto_git_pull=false" in captured.out

    def test_pullable_repo_auto_pulled_when_enabled(self, monkeypatch, capsys):
        """When auto_git_pull=true, pullable repos should be pulled."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 2,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )

        pull_called = []

        def fake_pull(path):
            pull_called.append(path)
            return True, "Already up to date."

        monkeypatch.setattr(local_repo_watcher, "_pull_repo", fake_pull)

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(pull_called) == 1
        captured = capsys.readouterr()
        assert "PULLABLE" in captured.out
        assert "DRY-RUN" not in captured.out
        assert "pull 完了" in captured.out

    def test_diverged_repo_displayed_without_pull(self, monkeypatch, capsys):
        """Diverged repos should be displayed but never auto-pulled."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 2,
                "ahead": 1,
                "status": local_repo_watcher.STATUS_DIVERGED,
                "error": None,
                "is_target": True,
            },
        )

        pull_called = []
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: pull_called.append(path) or (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        assert len(pull_called) == 0
        captured = capsys.readouterr()
        assert "DIVERGED" in captured.out
        assert "myrepo" in captured.out

    def test_throttle_skips_check_within_interval(self, monkeypatch, capsys):
        """The check should be throttled and not run if called within the interval."""
        import time

        local_repo_watcher._last_local_check_time = time.time()

        check_called = []
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda *a: check_called.append(a))

        config = {}
        local_repo_watcher.check_local_repos(config, "myuser")

        assert len(check_called) == 0

    def test_nonexistent_base_dir_is_silent(self, monkeypatch, capsys):
        """If the base directory does not exist, nothing should be printed."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)
        config = {"local_repo_watcher_base_dir": "/nonexistent/path/that/does/not/exist"}
        local_repo_watcher.check_local_repos(config, "myuser")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_pull_failure_displayed(self, monkeypatch, capsys):
        """When auto-pull fails, the failure message should be shown."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 1,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (False, "conflict detected"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        captured = capsys.readouterr()
        assert "pull 失敗" in captured.out
        assert "conflict detected" in captured.out


class TestSelfUpdateOnPull:
    """Tests for auto-restart when cat-github-watcher itself is pulled."""

    def test_restarts_when_self_repo_is_pulled(self, monkeypatch, capsys):
        """When the pulled repo is REPO_ROOT, restart_application should be called."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = pathlib.Path(tmpdir)
            self_repo_dir = base_dir / "cat-github-watcher"
            self_repo_dir.mkdir()

            # Treat the temporary self_repo_dir as the application REPO_ROOT.
            monkeypatch.setattr(local_repo_watcher, "REPO_ROOT", self_repo_dir)

            monkeypatch.setattr(
                local_repo_watcher,
                "_check_repo",
                lambda path, user: {
                    "name": "cat-github-watcher",
                    "path": str(self_repo_dir),
                    "remote_url": "https://github.com/cat2151/cat-github-watcher.git",
                    "branch": "main",
                    "dirty": False,
                    "behind": 1,
                    "ahead": 0,
                    "status": local_repo_watcher.STATUS_PULLABLE,
                    "error": None,
                    "is_target": True,
                },
            )
            monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))

            restarted = []
            monkeypatch.setattr(local_repo_watcher, "restart_application", lambda: restarted.append(True))

            config = {"local_repo_watcher_base_dir": str(base_dir), "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "cat2151")

            assert restarted, "restart_application should have been called"
            captured = capsys.readouterr()
            assert "再起動します" in captured.out

    def test_does_not_restart_for_other_repos(self, monkeypatch, capsys):
        """When the pulled repo is NOT REPO_ROOT, restart_application should NOT be called."""
        monkeypatch.setattr(local_repo_watcher, "_last_local_check_time", 0.0)

        monkeypatch.setattr(
            local_repo_watcher,
            "_check_repo",
            lambda path, user: {
                "name": "myrepo",
                "path": path,
                "remote_url": "https://github.com/myuser/myrepo.git",
                "branch": "main",
                "dirty": False,
                "behind": 1,
                "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE,
                "error": None,
                "is_target": True,
            },
        )
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "Updated."))

        restarted = []
        monkeypatch.setattr(local_repo_watcher, "restart_application", lambda: restarted.append(True))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}
            local_repo_watcher.check_local_repos(config, "myuser")

        assert not restarted, "restart_application should NOT have been called"


class TestNotifyPhase3Detected:
    """Tests for notify_phase3_detected phase3 tracking."""

    def test_notify_phase3_detected_registers_repo_for_post_phase3_check(self, monkeypatch):
        """notify_phase3_detected should add the repo to _repos_awaiting_post_phase3_check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}

            monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: {
                "name": "myrepo", "path": path, "remote_url": "https://github.com/u/myrepo.git",
                "branch": "main", "dirty": False, "behind": 0, "ahead": 0,
                "status": local_repo_watcher.STATUS_UP_TO_DATE, "error": None, "is_target": True,
            })

            local_repo_watcher.notify_phase3_detected("myrepo", config, "myuser")

        assert "myrepo" in local_repo_watcher._repos_awaiting_post_phase3_check

    def test_notify_phase3_detected_already_done_still_registers(self, monkeypatch):
        """Repos in REPO_STATE_DONE should still be registered for post-phase3 re-check."""
        local_repo_watcher._repo_states["myrepo"] = local_repo_watcher.REPO_STATE_DONE

        config = {}
        local_repo_watcher.notify_phase3_detected("myrepo", config, "myuser")

        assert "myrepo" in local_repo_watcher._repos_awaiting_post_phase3_check


def _wait_for(condition, timeout=2.0, interval=0.05):
    """Poll condition until it is True or timeout expires. Returns True if condition was met."""
    import time
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


class TestNotifyReposUpdatedAfterPhase3:
    """Tests for notify_repos_updated_after_phase3."""

    def test_triggers_recheck_for_phase3_repos_with_updated_at_change(self, monkeypatch):
        """Repos in _repos_awaiting_post_phase3_check whose updatedAt changed should be re-checked."""
        check_called = []

        def fake_check_repo(path, user):
            check_called.append(path)
            return {
                "name": "myrepo", "path": path,
                "remote_url": "https://github.com/u/myrepo.git",
                "branch": "main", "dirty": False, "behind": 2, "ahead": 0,
                "status": local_repo_watcher.STATUS_PULLABLE, "error": None, "is_target": True,
            }

        monkeypatch.setattr(local_repo_watcher, "_check_repo", fake_check_repo)
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}

            # Register myrepo as phase3 detected
            local_repo_watcher._repos_awaiting_post_phase3_check.add("myrepo")

            # Simulate updatedAt change for myrepo (PR was merged)
            local_repo_watcher.notify_repos_updated_after_phase3({"myrepo"}, config, "myuser")

            assert _wait_for(lambda: len(check_called) > 0), "Background check should have been triggered for myrepo"

    def test_does_not_trigger_recheck_for_repos_not_in_phase3_set(self, monkeypatch):
        """Repos NOT in _repos_awaiting_post_phase3_check should not be re-checked."""
        check_called = []
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: check_called.append(path))

        config = {}
        local_repo_watcher.notify_repos_updated_after_phase3({"other-repo"}, config, "myuser")

        import time
        time.sleep(0.1)
        assert len(check_called) == 0, "Should NOT check repos not in _repos_awaiting_post_phase3_check"

    def test_removes_from_awaiting_set_after_successful_pull(self, monkeypatch):
        """After a successful auto-pull, the repo should be removed from the tracking set."""
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: {
            "name": "myrepo", "path": path,
            "remote_url": "https://github.com/u/myrepo.git",
            "branch": "main", "dirty": False, "behind": 1, "ahead": 0,
            "status": local_repo_watcher.STATUS_PULLABLE, "error": None, "is_target": True,
        })
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: (True, "ok"))
        monkeypatch.setattr(local_repo_watcher, "REPO_ROOT", pathlib.Path("/some/other/repo"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": True}

            local_repo_watcher._repos_awaiting_post_phase3_check.add("myrepo")
            local_repo_watcher.notify_repos_updated_after_phase3({"myrepo"}, config, "myuser")

            assert _wait_for(lambda: "myrepo" not in local_repo_watcher._repos_awaiting_post_phase3_check), (
                "Repo should be removed from tracking set after successful pull"
            )

    def test_stays_in_awaiting_set_when_pull_disabled(self, monkeypatch):
        """When auto_git_pull=false, the repo should stay in the tracking set (not pulled)."""
        monkeypatch.setattr(local_repo_watcher, "_check_repo", lambda path, user: {
            "name": "myrepo", "path": path,
            "remote_url": "https://github.com/u/myrepo.git",
            "branch": "main", "dirty": False, "behind": 1, "ahead": 0,
            "status": local_repo_watcher.STATUS_PULLABLE, "error": None, "is_target": True,
        })
        pull_called = []
        monkeypatch.setattr(local_repo_watcher, "_pull_repo", lambda path: pull_called.append(path) or (True, "ok"))

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_repo = pathlib.Path(tmpdir) / "myrepo"
            fake_repo.mkdir()
            config = {"local_repo_watcher_base_dir": tmpdir, "auto_git_pull": False}

            local_repo_watcher._repos_awaiting_post_phase3_check.add("myrepo")
            local_repo_watcher.notify_repos_updated_after_phase3({"myrepo"}, config, "myuser")

            # Wait for background thread to finish checking (but not pulling)
            assert _wait_for(
                lambda: local_repo_watcher._repo_states.get("myrepo") == local_repo_watcher.REPO_STATE_DONE
            ), "Background check should complete"

        assert len(pull_called) == 0, "Should not pull when auto_git_pull=false"
        assert "myrepo" in local_repo_watcher._repos_awaiting_post_phase3_check, (
            "Repo should remain in tracking set when not pulled (dry-run mode)"
        )

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
b5259da Merge pull request #411 from cat2151/copilot/monitor-updatedat-check-auto-pull
6da263d Update project summaries (overview & development status) [auto]
13e250c Fix: レビュー指摘3件を修正（CHECKING中スキップ、ロック付きfixture、UnboundLocalError回避）
415c1dc Fix: phase3A後のPRクローズ時にauto pullが実行されない問題を修正
921747e Initial plan
2cbe5bb Merge pull request #409 from cat2151/copilot/refactor-main-py-for-orchestration
3a933be Address review comments: fix comment, add missing mocks for get_current_user/pages/local-repo
d3e887a Refactor main.py into thin orchestration layer (iteration_runner, determine_current_interval)
3873011 Initial plan
2fe17ec Merge pull request #407 from cat2151/copilot/refactor-large-file-in-main-py

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
src/gh_pr_phase_monitor/monitor/local_repo_watcher.py
src/gh_pr_phase_monitor/monitor/monitor.py
src/gh_pr_phase_monitor/monitor/pr_processor.py
src/gh_pr_phase_monitor/monitor/snapshot_markdown.py
src/gh_pr_phase_monitor/ui/wait_handler.py
tests/test_check_process_before_autoraise.py
tests/test_error_logging.py
tests/test_local_repo_watcher.py
tests/test_show_issues_when_pr_count_less_than_3.py
tests/test_skip_pr_check_html_refetch.py


---
Generated at: 2026-03-11 07:02:39 JST
