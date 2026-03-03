Last updated: 2026-03-04

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
- fetch_pr_html.py
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
- src/gh_pr_phase_monitor/click_config_validator.py
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
- src/gh_pr_phase_monitor/pr_html_analyzer.py
- src/gh_pr_phase_monitor/pr_html_fetcher.py
- src/gh_pr_phase_monitor/pr_html_saver.py
- src/gh_pr_phase_monitor/process_utils.py
- src/gh_pr_phase_monitor/rate_limit_handler.py
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
## [Issue #323](../issue-notes/323.md): fix: phase2/phase3誤検出の根本修正とllm_statuses優先への統一
GraphQLの`reviewThreads`が明示resolveされない限り`isResolved: False`のまま残るため、Copilotがフィードバック対応済みでも常にphase2と誤判定されていた。

## 変更概要

### phase検出の優先順位統一（`phase_detector.py`）

`_phase_from_llm_statuses`をHTMLベースの一次シグナルに昇格：

- **拡張**: `PHASE_3`のみ返していたところを`PHASE_2`も返すよう拡張（reviewingイベントあり＋未完了 → PHASE_2、reviewingなし → None）...
ラベル: 
--- issue-notes/323.md の内容 ---

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

## [Issue #314](../issue-notes/314.md): 現在観測できるPRが、すべて現実はphase3なのに、判定結果が誤ってphase2という判定をされてしまっている

ラベル: 
--- issue-notes/314.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
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

### .github/actions-tmp/issue-notes/23.md
```md
{% raw %}
# issue issue 17が再発してしまっている #23
[issues #23](https://github.com/cat2151/github-actions/issues/23)

# 症状は？
- issue 17と同じ

# どうする？
- development-status-generated-prompt.md を確認する
- 結果
    - >Issue番号を記載する際は、必ず [Issue #番号](issue-notes/番号.md) の形式でMarkdownリンクとして記載してください。
    - 仮説、これが残っており、ほかの ../ 指定と競合し、どちらかがランダムで選ばれていた
    - 対策、ここを ../ 指定にする

# 結果
- test green

# closeとする

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

### src/gh_pr_phase_monitor/phase_detector.py
```py
{% raw %}
"""
PR phase detection logic based on reviews and PR state
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

# Phase constants
PHASE_LLM_WORKING = "LLM working"
PHASE_1 = "phase1"
PHASE_2 = "phase2"
PHASE_3 = "phase3"

# Tracks comment reaction signatures that were confirmed as "finished" via HTML snapshot analysis.
_finished_reaction_signatures: Dict[str, str] = {}


def _build_pr_key(pr: Dict[str, Any]) -> str:
    """Build a stable key for tracking reaction resolution state."""
    url = pr.get("url")
    if url:
        return url

    repo_info = pr.get("repository") or {}
    owner = repo_info.get("owner") or "unknown"
    name = repo_info.get("name") or "unknown"
    number = pr.get("number") or "unknown"
    return f"{owner}/{name}#{number}"


def _comment_reaction_signature(comment_nodes: Any) -> str:
    """Build a deterministic signature of comment reactions for change detection."""
    if not isinstance(comment_nodes, list):
        return ""

    signatures: List[Dict[str, Any]] = []
    for comment in comment_nodes:
        groups = []
        for group in comment.get("reactionGroups") or []:
            count = (group.get("users") or {}).get("totalCount", 0)
            if count:
                groups.append({"content": group.get("content"), "count": count})
        if groups:
            # Sort reactions within a comment so signature is order-insensitive
            groups.sort(key=lambda g: (g.get("content") or "", g.get("count", 0)))
            signatures.append({"reactions": groups})

    if not signatures:
        return ""

    # Sort comments by their reaction signature to avoid dependence on comment order
    signatures.sort(key=lambda item: json.dumps(item["reactions"], sort_keys=True))

    # Sort keys for deterministic output
    return json.dumps(signatures, sort_keys=True)


def update_comment_reaction_resolution(pr: Dict[str, Any], comment_nodes: Any, finished: bool) -> None:
    """Update resolution cache based on HTML analysis results."""
    pr_key = _build_pr_key(pr)
    signature = _comment_reaction_signature(comment_nodes)

    if not signature:
        _finished_reaction_signatures.pop(pr_key, None)
        return

    if finished:
        _finished_reaction_signatures[pr_key] = signature
    else:
        _finished_reaction_signatures.pop(pr_key, None)


def comment_reactions_marked_finished(pr: Dict[str, Any], comment_nodes: Any) -> bool:
    """Return True when reactions match a signature previously marked finished."""
    signature = _comment_reaction_signature(comment_nodes)
    if not signature:
        return False

    pr_key = _build_pr_key(pr)
    return _finished_reaction_signatures.get(pr_key) == signature


def reset_comment_reaction_resolution_cache() -> None:
    """Clear cached reaction resolution state (useful for tests)."""
    _finished_reaction_signatures.clear()


def has_comments_with_reactions(comments: Union[List[Dict[str, Any]], int, None]) -> bool:
    """Check if any comments have non-empty reactionGroups

    When the LLM (coding agent) is working on addressing PR comments
    (general pull request comments fetched via the `comments` field),
    those comments may have reactions (GitHub reactions like 👍, 👎, 😄, 🎉,
    😕, ❤️, 🚀, 👀, etc.) indicating the bot is processing them.
    This indicates the LLM is actively working.

    Args:
        comments: List of comment dictionaries with reactionGroups, or None/integer for backward compatibility

    Returns:
        True if any comment has non-empty reactionGroups, False otherwise
    """
    # Handle backward compatibility: comments might be an integer or None from legacy API
    if not comments or not isinstance(comments, list):
        return False

    for comment in comments:
        reaction_groups = comment.get("reactionGroups", [])
        if reaction_groups:
            # Check if any reaction group has users
            for group in reaction_groups:
                users = group.get("users", {})
                total_count = users.get("totalCount", 0)
                if total_count > 0:
                    return True

    return False


def has_unresolved_review_threads(review_threads: Union[List[Dict[str, Any]], None]) -> bool:
    """Check if there are any unresolved review threads (inline comments)

    Review threads contain inline code comments from reviews.
    If there are unresolved threads, the PR needs fixes (phase2).

    Args:
        review_threads: List of review thread dictionaries with isResolved, isOutdated, or None

    Returns:
        True if there are unresolved review threads, False otherwise
    """
    if not review_threads or not isinstance(review_threads, list):
        return False

    # Check if any thread is unresolved and not outdated
    for thread in review_threads:
        is_resolved = thread.get("isResolved", False)
        is_outdated = thread.get("isOutdated", False)

        # If a thread is not resolved and not outdated, it needs attention
        if not is_resolved and not is_outdated:
            return True

    return False


def has_inline_review_comments(review_body: str) -> bool:
    """DEPRECATED: Check if review body indicates inline code comments were generated

    This function is kept for backward compatibility but should not be used
    for new code. Use has_unresolved_review_threads() instead which checks
    actual review thread data rather than trying to infer from text patterns.

    Copilot's review body MAY contain text like:
    "Copilot reviewed X out of Y changed files in this pull request and generated N comment(s)."
    when inline comments are present. However, this pattern is not always present.

    Args:
        review_body: The body text of the review

    Returns:
        True if the review body indicates inline comments exist, False otherwise
    """
    if not review_body:
        return False

    # Check for the pattern indicating inline comments were generated
    # Pattern matches: "generated 1 comment" or "generated 2 comments" etc.
    # NOTE: This is unreliable - the pattern may not always be present!
    pattern = r"generated\s+\d+\s+comments?"
    return bool(re.search(pattern, review_body, re.IGNORECASE))


def llm_working_from_statuses(llm_statuses: List[str]) -> Optional[bool]:
    """Determine LLM working state from ordered LLM statuses.

    Returns True when the most recent state after any 'started work' entry has
    no subsequent 'finished work' entry, False when a later 'finished work'
    exists, and None when the statuses do not provide a signal.
    """
    if not llm_statuses:
        return None

    last_started_idx = None
    last_finished_idx = None
    reviewing_chain_finished_idx = None
    review_idx = None
    started_after_review_idx = None

    for idx, status in enumerate(llm_statuses):
        lowered = status.lower()
        if "reviewing" in lowered:
            review_idx = idx
            started_after_review_idx = None
        if "started work" in lowered:
            last_started_idx = idx
            if review_idx is not None and idx > review_idx:
                started_after_review_idx = idx
        if "finished work" in lowered:
            last_finished_idx = idx
            if started_after_review_idx is not None and idx > started_after_review_idx:
                reviewing_chain_finished_idx = idx

    if last_finished_idx is not None and last_started_idx is not None and last_finished_idx > last_started_idx:
        return False

    if reviewing_chain_finished_idx is not None and (
        last_started_idx is None or reviewing_chain_finished_idx >= last_started_idx
    ):
        return False

    if last_started_idx is not None and (last_finished_idx is None or last_started_idx > last_finished_idx):
        return True

    return None


def _phase_from_llm_statuses(llm_statuses: List[str]) -> Optional[str]:
    """Infer phase from LLM statuses when review data is unavailable.

    When the LLM statuses contain a reviewing event and all subsequent work
    has finished (no started work without matching finished work),
    this indicates phase 3.
    """
    if not llm_statuses:
        return None

    review_idx: Optional[int] = None
    last_started_idx: Optional[int] = None
    last_finished_idx: Optional[int] = None

    for idx, status in enumerate(llm_statuses):
        lowered = status.lower()
        if "reviewing" in lowered:
            review_idx = idx
        if "started work" in lowered:
            last_started_idx = idx
        if "finished work" in lowered:
            last_finished_idx = idx

    # Require a reviewing event and a finished-work event that happens *after* reviewing.
    if review_idx is None or last_finished_idx is None:
        return None
    if last_finished_idx <= review_idx:
        return None

    # Ensure there is no started-work event after the last finished-work event.
    if last_started_idx is not None and last_started_idx > last_finished_idx:
        return None

    return PHASE_3

    return None


def _determine_phase_without_comment_reactions(pr: Dict[str, Any]) -> str:
    """Determine the phase without considering comment reactions."""
    is_draft = pr.get("isDraft", False)
    reviews = pr.get("reviews", [])
    latest_reviews = pr.get("latestReviews", [])
    review_requests = pr.get("reviewRequests", [])
    review_threads = pr.get("reviewThreads", [])
    llm_statuses = pr.get("llm_statuses") or []

    # Phase 1: Draft状態
    # - reviewRequests が1件以上ある場合: 常に phase1
    # - reviewRequests が空の場合:
    #     - LLM が未完了 (llm_working_from_statuses(...) が True または None): LLM working
    #     - LLM が完了済み (llm_working_from_statuses(...) が False): phase1
    if is_draft:
        if not review_requests:
            llm_working = llm_working_from_statuses(llm_statuses)
            if llm_working is False:
                return PHASE_1
            return PHASE_LLM_WORKING
        return PHASE_1

    # Phase 2 と Phase 3 の判定には reviews が必要
    if not reviews or not latest_reviews:
        # LLMステータスからreviewingと作業完了を検出できればphase3
        status_phase = _phase_from_llm_statuses(llm_statuses)
        if status_phase is not None:
            return status_phase
        return PHASE_LLM_WORKING

    # 最新のレビューを取得
    latest_review = reviews[-1]
    author_login = latest_review.get("author", {}).get("login", "")

    # Phase 2/3: copilot-pull-request-reviewer のレビュー後
    if author_login == "copilot-pull-request-reviewer":
        # レビューの状態を確認
        review_state = latest_review.get("state", "")

        # CHANGES_REQUESTEDの場合は確実にphase2
        if review_state == "CHANGES_REQUESTED":
            return PHASE_2

        # COMMENTEDの場合、実際のreview threads(インラインコメント)を確認
        # 未解決のレビュースレッドがある場合はphase2（修正が必要）、ない場合はphase3（レビュー待ち）
        if review_state == "COMMENTED":
            # Check actual review threads instead of text patterns
            if has_unresolved_review_threads(review_threads):
                return PHASE_2
            # レビューコメントがない場合はphase3
            return PHASE_3

        # それ以外(APPROVED, DISMISSED, PENDING等)はphase3
        return PHASE_3

    # Phase 3: copilot-swe-agent の修正後
    # ただし、copilot-pull-request-reviewerの未解決レビューがある場合はphase2
    if author_login == "copilot-swe-agent":
        # Find the positions of copilot-pull-request-reviewer and copilot-swe-agent reviews
        # to determine if there's a re-review from the reviewer after swe-agent started working
        latest_reviewer_index = None
        latest_reviewer_state = None
        first_swe_agent_index = None
        swe_agent_review_count = 0

        for i, review in enumerate(reviews):
            reviewer_login = review.get("author", {}).get("login", "")

            # Track copilot-swe-agent reviews
            if reviewer_login == "copilot-swe-agent":
                swe_agent_review_count += 1
                if first_swe_agent_index is None:
                    first_swe_agent_index = i

            # Track the latest copilot-pull-request-reviewer review
            if reviewer_login == "copilot-pull-request-reviewer":
                latest_reviewer_index = i
                latest_reviewer_state = review.get("state", "")

        # CHANGES_REQUESTEDの場合は常にphase2
        if latest_reviewer_state == "CHANGES_REQUESTED":
            return PHASE_2

        # Check if there are unresolved review threads
        if has_unresolved_review_threads(review_threads):
            # When copilot-pull-request-reviewer uses COMMENTED (not CHANGES_REQUESTED),
            # it indicates suggestions rather than required changes.
            # If swe-agent has posted even one review in response, the work is complete → phase3
            # This is different from CHANGES_REQUESTED where we'd want stronger completion signals.

            is_re_review = (
                latest_reviewer_index is not None
                and first_swe_agent_index is not None
                and latest_reviewer_index > first_swe_agent_index
            )

            # Determine if swe-agent has completed work
            if latest_reviewer_state == "COMMENTED":
                # For COMMENTED reviews (suggestions only), any swe-agent review indicates completion
                swe_agent_completed = swe_agent_review_count >= 1
            else:
                # For other states, require stronger completion signals
                swe_agent_completed = (
                    swe_agent_review_count > 1  # Multiple reviews indicate completion
                    or is_re_review  # Re-review after swe-agent indicates completion
                )

            if swe_agent_completed:
                # Swe-agent completed work → phase3
                return PHASE_3
            else:
                # Swe-agent just started or no clear completion signal → phase2
                return PHASE_2

        # 未解決のレビューコメントがない場合、または最新のレビューアーが満足している場合はphase3
        return PHASE_3

    # LLMステータスからreviewingと作業完了を検出できればphase3
    status_phase = _phase_from_llm_statuses(pr.get("llm_statuses") or [])
    if status_phase is not None:
        return status_phase

    return PHASE_LLM_WORKING


def determine_phase(pr: Dict[str, Any]) -> str:
    """Determine which phase the PR is in

    Args:
        pr: PR data dictionary

    Returns:
        Phase string: PHASE_1, PHASE_2, PHASE_3, or PHASE_LLM_WORKING
    """
    # Use commentNodes if available (new API), fall back to comments for legacy compatibility
    comment_nodes = pr.get("commentNodes", pr.get("comments", []))

    # Check if any comments have reactions - this indicates LLM is working
    # When the coding agent is responding to PR comments, those comments
    # may have reactions indicating the bot is processing them
    if has_comments_with_reactions(comment_nodes):
        if not comment_reactions_marked_finished(pr, comment_nodes):
            llm_statuses = pr.get("llm_statuses") or []
            llm_working = llm_working_from_statuses(llm_statuses)
            if llm_working is False:
                return _determine_phase_without_comment_reactions(pr)
            return PHASE_LLM_WORKING

    return _determine_phase_without_comment_reactions(pr)


def get_llm_working_progress_label(pr: Dict[str, Any]) -> str:
    """Describe how far the PR has progressed when in LLM working phase."""
    base_phase = _determine_phase_without_comment_reactions(pr)

    if pr.get("isDraft", False):
        return "Phase 1 in progress"

    if base_phase == PHASE_3:
        return "Phase 2 completed"

    if base_phase == PHASE_2:
        return "Phase 2 in progress"

    return "Phase 1 completed"

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
f2003ec Merge pull request #322 from cat2151/copilot/get-pr-html-and-save
5fda161 fetch_pr_htmlを認証なしに変更（pr_html_fetcher._fetch_pr_htmlを再利用）
49c13f9 JSONにpr_urlとstatusを再追加（承認済みフォーマットに合わせる）
cd01622 JSONをstatus元データ（is_draft + llm_statuses）のみに絞り込み
73f87d2 pr_html_analyzer.py追加: HTML解析→6種status→JSON生成、pr_html_saver.pyから呼び出す
1913f82 --fetch-pr-html オプションを既存アプリに追加、実装を新規モジュール pr_html_saver.py に移動
c84dc0a PRのHTMLを取得してlogs/pr/に保存するスクリプト fetch_pr_html.py を追加
27e5661 Initial plan
d88a3a3 Revert "Merge pull request #311 from cat2151/copilot/reduce-graphql-consumption"
a66141d Merge pull request #311 from cat2151/copilot/reduce-graphql-consumption

### 変更されたファイル:
fetch_pr_html.py
generated-docs/development-status-generated-prompt.md
generated-docs/development-status.md
generated-docs/project-overview-generated-prompt.md
generated-docs/project-overview.md
src/gh_pr_phase_monitor/auto_updater.py
src/gh_pr_phase_monitor/graphql_client.py
src/gh_pr_phase_monitor/issue_fetcher.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/pr_fetcher.py
src/gh_pr_phase_monitor/pr_html_analyzer.py
src/gh_pr_phase_monitor/pr_html_saver.py
src/gh_pr_phase_monitor/rate_limit_handler.py
src/gh_pr_phase_monitor/repository_fetcher.py
tests/test_auto_updater.py
tests/test_fetch_pr_html.py
tests/test_graphql_query_intent_display.py
tests/test_pr_html_analyzer.py
tests/test_rate_limit_throttle.py
tests/test_rate_limit_usage_display.py


---
Generated at: 2026-03-04 07:03:33 JST
