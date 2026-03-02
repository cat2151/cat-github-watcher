Last updated: 2026-03-03

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
- .github/actions-tmp/issue-notes/49.md
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
## [Issue #308](../issue-notes/308.md): 大きなファイルの検出: 1個のファイルが500行を超えています
以下のファイルが500行を超えています。リファクタリングを検討してください。

## 検出されたファイル

| ファイル | 行数 | 超過行数 |
|---------|------|----------|
| `src/gh_pr_phase_monitor/main.py` | 510 | +10 |

## テスト実施のお願い

- リファクタリング前後にテストを実行し、それぞれのテスト失敗件数を報告してください
- リファクタリング前後のどちらかでテストがredの場合、まず別issueでtest greenにしてからリファクタリングしてください

## 推奨事項

1. 単一責任の原...
ラベル: refactoring, code-quality, automated
--- issue-notes/308.md の内容 ---

```markdown

```

## [Issue #307](../issue-notes/307.md): 起動直後に別スレッドで自己アップデートチェックを実行する
停止中にアップデートが行われた場合、次のメインループ実行まで検知が遅延していた。起動時に即座にアップデートチェックを走らせることで、再起動後すぐに最新コードへ更新できるようにする。

## 変更点

- **`auto_updater.py`**: `start_startup_self_update_check()` を追加
  - daemonスレッドで `maybe_self_update()` を一度呼び出す
  - 対象は自己リポジトリのみ
  - 例外はprint出力して飲み込む（クラッシュ防止）

- **`main.py`**: シグナルハンドラー設定後・メインループ開始前に呼...
ラベル: 
--- issue-notes/307.md の内容 ---

```markdown

```

## [Issue #304](../issue-notes/304.md): 今ある「自分自身をpullしたら自動アップデートする」、について、起動直後のタイミングにおいても、別スレッドで一度実行する

ラベル: 
--- issue-notes/304.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
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

### src/gh_pr_phase_monitor/auto_updater.py
```py
{% raw %}
"""Self-update utility using gh CLI and git."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

UPDATE_CHECK_INTERVAL_SECONDS = 60
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_last_check_time: float = 0.0
_REMOTE_PATTERN = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")


def _run_command(args: list[str], cwd: Path | str | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command and return the completed process without raising on error."""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        check=False,
    )


def _parse_remote_url(remote_url: str) -> Optional[Tuple[str, str]]:
    """Parse a GitHub remote URL into (owner, repo)."""
    match = _REMOTE_PATTERN.search(remote_url.strip())
    if not match:
        return None
    return match.group("owner"), match.group("repo")


def _get_tracking_branch(repo_root: Path) -> Optional[Tuple[str, str]]:
    """Return (remote, branch) for the current upstream if configured."""
    result = _run_command(["git", "-C", str(repo_root), "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if result.returncode != 0:
        return None

    ref = result.stdout.strip()
    if "/" not in ref:
        return None
    remote, branch = ref.split("/", 1)
    if not remote or not branch:
        return None
    return remote, branch


def _get_remote_repo(repo_root: Path, remote_name: str) -> Optional[Tuple[str, str]]:
    """Return (owner, repo) for the given remote using its URL."""
    result = _run_command(["git", "-C", str(repo_root), "remote", "get-url", remote_name])
    if result.returncode != 0:
        return None
    parsed = _parse_remote_url(result.stdout)
    return parsed


def _get_local_head_sha(repo_root: Path) -> Optional[str]:
    """Return the current HEAD SHA."""
    result = _run_command(["git", "-C", str(repo_root), "rev-parse", "HEAD"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _get_remote_latest_sha(owner: str, repo: str, branch: str, cwd: Path) -> Optional[str]:
    """Fetch the latest SHA for the remote branch via gh api."""
    result = _run_command(
        [
            "gh",
            "api",
            f"repos/{owner}/{repo}/commits",
            "-F",
            f"sha={branch}",
            "-F",
            "per_page=1",
            "--jq",
            ".[0].sha",
        ],
        cwd=cwd,
    )
    if result.returncode != 0:
        return None
    sha = result.stdout.strip()
    return sha or None


def _is_worktree_clean(repo_root: Path) -> bool:
    """Check if the worktree has no local modifications."""
    result = _run_command(["git", "-C", str(repo_root), "status", "--porcelain"])
    return result.returncode == 0 and not result.stdout.strip()


def _pull_fast_forward(repo_root: Path, remote_name: str, branch: str) -> bool:
    """Attempt a fast-forward pull; return True on success."""
    result = _run_command(["git", "-C", str(repo_root), "pull", "--ff-only", remote_name, branch])
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        print(f"Auto-update skipped: git pull failed ({message}).")
        return False
    return True


def restart_application() -> None:
    """Restart the current Python process with the same arguments."""
    os.chdir(REPO_ROOT)
    os.execv(sys.executable, [sys.executable] + sys.argv)


def maybe_self_update(repo_root: Path | None = None) -> bool:
    """Check for repository updates and restart the app if new commits are available."""
    global _last_check_time
    now = time.time()
    if _last_check_time and now - _last_check_time < UPDATE_CHECK_INTERVAL_SECONDS:
        return False
    _last_check_time = now

    repo_root = repo_root or REPO_ROOT
    tracking = _get_tracking_branch(repo_root)
    if not tracking:
        return False
    remote_name, branch = tracking

    remote_repo = _get_remote_repo(repo_root, remote_name)
    if not remote_repo:
        return False
    owner, repo = remote_repo

    local_sha = _get_local_head_sha(repo_root)
    if not local_sha:
        return False

    remote_sha = _get_remote_latest_sha(owner, repo, branch, repo_root)
    if not remote_sha or remote_sha == local_sha:
        return False

    if not _is_worktree_clean(repo_root):
        print("Auto-update skipped: local changes detected.")
        return False

    if not _pull_fast_forward(repo_root, remote_name, branch):
        return False

    print("Auto-update applied: restarting application to use the latest code...")
    restart_application()
    return True

{% endraw %}
```

### src/gh_pr_phase_monitor/main.py
```py
{% raw %}
"""
Main execution module for GitHub PR Phase Monitor
"""

import math
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
from .graphql_client import GitHubRateLimitError, get_rate_limit_info
from .local_repo_watcher import (
    display_pending_local_repo_results,
    notify_phase3_detected,
    start_local_repo_monitoring,
)
from .monitor import check_no_state_change_timeout
from .pages_watcher import check_pages_deployments_for_repos, get_pages_repos_from_config
from .phase_detector import PHASE_3, PHASE_LLM_WORKING, determine_phase
from .pr_actions import process_pr
from .pr_data_recorder import record_reaction_snapshot, reset_snapshot_cache
from .time_utils import format_elapsed_time
from .wait_handler import wait_with_countdown

LOG_DIR = Path("logs")
MAX_RATE_LIMIT_THROTTLE_SECONDS = 600


def _format_rate_limit_reset(reset: Any, now: datetime | None = None) -> tuple[str, str]:
    """Format rate-limit reset epoch into UTC datetime and remaining duration."""
    if not isinstance(reset, (int, float)):
        return "unknown", "unknown"

    current = now or datetime.now(UTC)
    reset_dt = datetime.fromtimestamp(float(reset), UTC)
    remaining_seconds = max(0, int(reset_dt.timestamp() - current.timestamp()))
    return reset_dt.strftime("%Y-%m-%d %H:%M:%S UTC"), format_elapsed_time(remaining_seconds)


def _display_rate_limit_usage(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> None:
    """Display GraphQL API usage breakdown for this iteration."""
    if not after:
        return

    remaining = after.get("remaining", "?")
    limit = after.get("limit", "?")
    reset = after.get("reset")
    reset_display, reset_in_display = _format_rate_limit_reset(reset)
    status = f"残={remaining}/{limit}, リセット={reset_display} (あと{reset_in_display})"

    if before is not None and isinstance(before.get("remaining"), int) and isinstance(after.get("remaining"), int):
        raw_consumed = before["remaining"] - after["remaining"]
        if raw_consumed < 0:
            # レートリミットウィンドウがリセットされ、単純差分が負になるケース
            consumed = 0
            reset_note = " (リセット後)"
        else:
            consumed = raw_consumed
            reset_note = ""
        print(f"\nGraphQL API使用状況: 今回消費={consumed}点{reset_note}, {status}")
    else:
        print(f"\nGraphQL API使用状況: {status}")


def _check_rate_limit_throttle(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    normal_interval_seconds: int,
) -> tuple[bool, int]:
    """Check if the current rate limit consumption rate requires interval throttling.

    Calculates whether continuing at the current consumption rate would exhaust
    the GraphQL rate limit before the next reset window.

    Args:
        before: Rate limit info captured before API calls
        after: Rate limit info captured after API calls
        normal_interval_seconds: The configured normal monitoring interval

    Returns:
        Tuple of (should_throttle, recommended_interval_seconds).
        If should_throttle is False, recommended_interval_seconds equals normal_interval_seconds.
    """
    if not (before and after):
        return False, normal_interval_seconds

    remaining = after.get("remaining")
    reset = after.get("reset")
    if not isinstance(remaining, int) or not isinstance(reset, (int, float)):
        return False, normal_interval_seconds

    if not isinstance(before.get("remaining"), int):
        return False, normal_interval_seconds

    consumed = before["remaining"] - after["remaining"]
    if consumed <= 0:
        return False, normal_interval_seconds

    now = time.time()
    reset_seconds = max(0, int(reset) - now)
    if reset_seconds <= 0 or normal_interval_seconds <= 0:
        return False, normal_interval_seconds

    # Estimate how many more iterations until reset
    iterations_until_reset = reset_seconds / normal_interval_seconds
    projected_consumption = consumed * iterations_until_reset

    if projected_consumption <= remaining:
        return False, normal_interval_seconds

    # When remaining is 0, cap immediately at maximum throttle
    if remaining <= 0:
        return True, MAX_RATE_LIMIT_THROTTLE_SECONDS

    # Calculate the minimum safe interval to avoid exhausting the rate limit
    # safe_interval = reset_seconds / (remaining / consumed) = reset_seconds * consumed / remaining
    # Use ceil to round up so we never under-estimate the required interval
    safe_interval_seconds = math.ceil(reset_seconds * consumed / remaining)
    # Use at least 2x the normal interval to avoid micro-adjustments
    throttled_interval = max(normal_interval_seconds * 2, safe_interval_seconds)
    # Cap at max throttle to prevent excessively long waits
    throttled_interval = min(throttled_interval, MAX_RATE_LIMIT_THROTTLE_SECONDS)

    return True, throttled_interval


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

        # Capture rate limit before API calls for per-iteration consumption tracking
        try:
            before_rate_limit = get_rate_limit_info()
        except Exception as rate_limit_error:
            log_error_to_file("Failed to fetch pre-iteration rate limit info", rate_limit_error)
            before_rate_limit = None

        # Reset snapshot cache to allow recording new snapshots in this iteration
        reset_snapshot_cache()

        # Initialize variables to track status for summary
        all_prs = []
        pr_phases = []
        repos_with_prs = []
        phase3_repo_names: list[str] = []

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
47d323f Merge pull request #306 from cat2151/copilot/add-query-cost-indicator
99ca8c5 レビュー指摘対応: 定数化・ceil丸め・docstring修正
15c83e6 GraphQLクエリごとに意図・消費コストを表示し、レートリミット超過時に動的インターバル延長
105aed7 Initial plan
e0401a1 Merge pull request #303 from cat2151/copilot/refactor-large-file-detection
8b0aa9e Split test_local_repo_watcher.py: move TestBackgroundMonitoring to separate file
1dd503d Initial plan
e38af6e Merge pull request #301 from cat2151/copilot/optimize-pullable-search
719015b fix: PRレビューコメントへの対応
85bd8dd feat: バックグラウンドスレッドでpullable検索を最適化

### 変更されたファイル:
generated-docs/development-status-generated-prompt.md
generated-docs/development-status.md
generated-docs/project-overview-generated-prompt.md
generated-docs/project-overview.md
src/gh_pr_phase_monitor/button_clicker.py
src/gh_pr_phase_monitor/click_config_validator.py
src/gh_pr_phase_monitor/graphql_client.py
src/gh_pr_phase_monitor/issue_fetcher.py
src/gh_pr_phase_monitor/local_repo_watcher.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/phase_detector.py
src/gh_pr_phase_monitor/pr_fetcher.py
src/gh_pr_phase_monitor/repository_fetcher.py
tests/test_graphql_query_intent_display.py
tests/test_local_repo_watcher_background.py
tests/test_rate_limit_throttle.py
tests/test_rate_limit_usage_display.py
tests/test_status_summary.py


---
Generated at: 2026-03-03 07:04:23 JST
