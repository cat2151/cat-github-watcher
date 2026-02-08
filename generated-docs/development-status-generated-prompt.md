Last updated: 2026-02-09

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
- .github/actions-tmp/.github_automation/check-large-files/check-large-files.toml.example
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
- .github/actions-tmp/issue-notes/31.md
- .github/actions-tmp/issue-notes/4.md
- .github/actions-tmp/issue-notes/7.md
- .github/actions-tmp/issue-notes/8.md
- .github/actions-tmp/issue-notes/9.md
- .github/actions-tmp/package-lock.json
- .github/actions-tmp/package.json
- .github/actions-tmp/src/main.js
- .github/copilot-instructions.md
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
- src/gh_pr_phase_monitor/browser_automation.py
- src/gh_pr_phase_monitor/colors.py
- src/gh_pr_phase_monitor/comment_fetcher.py
- src/gh_pr_phase_monitor/comment_manager.py
- src/gh_pr_phase_monitor/config.py
- src/gh_pr_phase_monitor/display.py
- src/gh_pr_phase_monitor/github_auth.py
- src/gh_pr_phase_monitor/github_client.py
- src/gh_pr_phase_monitor/graphql_client.py
- src/gh_pr_phase_monitor/issue_fetcher.py
- src/gh_pr_phase_monitor/main.py
- src/gh_pr_phase_monitor/monitor.py
- src/gh_pr_phase_monitor/notifier.py
- src/gh_pr_phase_monitor/phase_detector.py
- src/gh_pr_phase_monitor/pr_actions.py
- src/gh_pr_phase_monitor/pr_data_recorder.py
- src/gh_pr_phase_monitor/pr_fetcher.py
- src/gh_pr_phase_monitor/repository_fetcher.py
- src/gh_pr_phase_monitor/state_tracker.py
- src/gh_pr_phase_monitor/time_utils.py
- src/gh_pr_phase_monitor/wait_handler.py
- tests/test_batteries_included_defaults.py
- tests/test_browser_automation.py
- tests/test_check_process_before_autoraise.py
- tests/test_config_rulesets.py
- tests/test_config_rulesets_features.py
- tests/test_elapsed_time_display.py
- tests/test_hot_reload.py
- tests/test_integration_issue_fetching.py
- tests/test_interval_contamination_bug.py
- tests/test_interval_parsing.py
- tests/test_issue_fetching.py
- tests/test_max_llm_working_parallel.py
- tests/test_no_change_timeout.py
- tests/test_no_open_prs_issue_display.py
- tests/test_notification.py
- tests/test_phase3_merge.py
- tests/test_phase_detection.py
- tests/test_post_comment.py
- tests/test_post_phase3_comment.py
- tests/test_pr_actions.py
- tests/test_pr_actions_rulesets_features.py
- tests/test_pr_actions_with_rulesets.py
- tests/test_pr_data_recorder.py
- tests/test_pr_title_fix.py
- tests/test_repos_with_prs_structure.py
- tests/test_show_issues_when_pr_count_less_than_3.py
- tests/test_status_summary.py
- tests/test_validate_phase3_merge_config.py
- tests/test_verbose_config.py

## 現在のオープンIssues
## [Issue #220](../issue-notes/220.md): LLM status timeline 表示はtomlでon/offできるようにし、デフォルトをoffとする

ラベル: 
--- issue-notes/220.md の内容 ---

```markdown

```

## [Issue #219](../issue-notes/219.md): 「README.ja.mdへの記載が漏れている機能」があるか調査する。codexとclaudeに対応したことは、記載が漏れてそう

ラベル: good first issue
--- issue-notes/219.md の内容 ---

```markdown

```

## [Issue #218](../issue-notes/218.md): 陳腐化したドキュメントを削除する。あわせて「もう一切使う可能性がなくなったscript」があるかlistしてPRに報告する

ラベル: good first issue
--- issue-notes/218.md の内容 ---

```markdown

```

## [Issue #217](../issue-notes/217.md): Make PR phase snapshots opt-in and keep LLM status capture
Adds an opt-in `enable_pr_phase_snapshots` flag (default `false`) so HTML/JSON/markdown snapshots under `pr_phase_snapshots/` are only written when enabled, while still fetching HTML for LLM status extraction and reaction resolution in LLM Working detection. Updates config loading/verbose output and...
ラベル: 
--- issue-notes/217.md の内容 ---

```markdown

```

## [Issue #216](../issue-notes/216.md): pr_phase_snapshots/ への取得は、tomlでon/off設定できるようにし、デフォルトをoffとする。もちろんLLM Working用の取得機能は独立して維持する

ラベル: 
--- issue-notes/216.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/README.ja.md
```md
{% raw %}
# GitHub Actions 共通ワークフロー集

このリポジトリは、**複数プロジェクトで使い回せるGitHub Actions共通ワークフロー集**です

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

# 3行で説明
- 🚀 プロジェクトごとのGitHub Actions管理をもっと楽に
- 🔗 共通化されたワークフローで、どのプロジェクトからも呼ぶだけでOK
- ✅ メンテは一括、プロジェクト開発に集中できます

## Quick Links
| 項目 | リンク |
|------|--------|
| 📖 プロジェクト概要 | [generated-docs/project-overview.md](generated-docs/project-overview.md) |
| 📖 コールグラフ | [generated-docs/callgraph.html](https://cat2151.github.io/github-actions/generated-docs/callgraph.html) |
| 📊 開発状況 | [generated-docs/development-status.md](generated-docs/development-status.md) |

# notes
- まだ共通化の作業中です
- まだワークフロー内容を改善中です

※README.md は README.ja.md を元にGeminiの翻訳でGitHub Actionsで自動生成しています

{% endraw %}
```

### README.ja.md
```md
{% raw %}
# cat-github-watcher

**GitHub Copilotによる自動実装フェーズのPR監視ツール**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

※このドキュメントは大部分がAI生成です。issueをagentに投げて生成させました。

## 状況
- ドッグフーディング中です。
- 大きなバグを一通り取りました。
- 破壊的変更が頻繁にあります。
- 備忘
  - 当初はGitHub Actionsで実装を試みましたが、PR監視という目的には適さないことが判明したため、Python版に移行しました。
  - Python版は、認証済みGitHubユーザーのユーザー所有リポジトリを監視し、PRのフェーズに応じた通知やアクションを実行します。

## Quick Links
| 項目 | リンク |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## 概要

GitHub Copilotが自動実装を行うPRのフェーズを監視し、適切なタイミングで通知やアクションを実行するPythonツールです。
認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIを利用して効率的にPRを監視します。

## 特徴

- **全リポジトリ自動監視**: 認証済みGitHubユーザーのユーザー所有リポジトリのPRを自動監視
- **GraphQL API活用**: 効率的なデータ取得で高速監視を実現
- **フェーズ検知**: PRの状態（phase1: Draft状態、phase2: レビュー指摘対応中、phase3: レビュー待ち、LLM working: コーディングエージェント作業中）を自動判定
- **Dry-runモード**: デフォルトでは監視のみ行い、実際のアクション（コメント投稿、PR Ready化、通知送信）は実行しない。明示的に有効化することで安全に運用可能
- **自動コメント投稿**: フェーズに応じて適切なコメントを自動投稿（要：設定ファイルで有効化）
- **Draft PR自動Ready化**: phase2でのレビュー指摘対応のため、Draft PRを自動的にReady状態に変更（要：設定ファイルで有効化）
- **モバイル通知**: ntfy.shを利用してphase3（レビュー待ち）を検知したらモバイル端末に通知（要：設定ファイルで有効化）
  - 個別のPRがphase3になったときに通知
  - すべてのPRがphase3になったときにも通知（メッセージはtomlで設定可能）
- **issue一覧表示**: 全PRが「LLM working」の場合、オープンPRのないリポジトリのissue上位N件を表示（デフォルト: 10件、`issue_display_limit`で変更可能）
- **省電力モード**: 状態変化がない場合、API使用量を削減するため監視間隔を自動的に延長（`no_change_timeout`と`reduced_frequency_interval`で設定可能）
- **Verboseモード**: 起動時と実行中に詳細な設定情報を表示し、設定ミスの検出を支援（`verbose`で有効化）

## アーキテクチャ

このツールは、単一責任の原則(SRP)に従ってモジュール化されたPythonアプリケーションです。

### ディレクトリ構成

```
cat-github-watcher/
├── cat-github-watcher.py    # エントリーポイント
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py         # ANSI カラーコードと色付け
│       ├── config.py         # 設定の読み込みと解析
│       ├── github_client.py  # GitHub API 連携
│       ├── phase_detector.py # PRフェーズ判定ロジック
│       ├── comment_manager.py # コメント投稿と確認
│       ├── pr_actions.py     # PRアクション（Ready化、ブラウザ起動）
│       └── main.py           # メイン実行ループ
└── tests/                    # テストファイル
```

### フェーズ判定ロジック

ツールは以下の4つのフェーズを判定します：

1. **phase1 (Draft状態)**: PRがDraft状態で、レビューリクエストがある場合
2. **phase2 (レビュー指摘対応中)**: copilot-pull-request-reviewerがレビューコメントを投稿し、修正が必要な場合
3. **phase3 (レビュー待ち)**: copilot-swe-agentが修正を完了し、人間のレビュー待ちの場合
4. **LLM working (コーディングエージェント作業中)**: 上記のいずれにも該当しない場合（Copilotが実装中など）

## 使い方

### 前提条件

- Python 3.10 以上がインストールされている
- GitHub CLI (`gh`) がインストールされ、認証済みである
  ```bash
  gh auth login
  ```

### セットアップ

1. このリポジトリをクローン：
   ```bash
   git clone https://github.com/cat2151/cat-github-watcher.git
   cd cat-github-watcher
   ```

2. 設定ファイルを作成（オプション）：
   ```bash
   cp config.toml.example config.toml
   ```

3. `config.toml` を編集して、監視間隔や実行モード、ntfy.sh通知、Copilot自動割り当て、自動マージを設定（オプション）：
   ```toml
   # チェック間隔（"30s", "1m", "5m", "1h", "1d"など）
   interval = "1m"
   
   # PRのないリポジトリから表示するissue数の上限
   # デフォルトは10ですが、任意の正の数（例: 5, 15, 20）に変更可能
   issue_display_limit = 10
   
   # 状態変更なしのタイムアウト時間
   # 全PRの状態（各PRのフェーズ）がこの時間変化しない場合、
   # 監視間隔が省電力モード（下記のreduced_frequency_interval）に切り替わります
   # 空文字列 "" を設定すると無効化されます
   # サポートされる形式: "30s", "1m", "5m", "30m", "1h", "1d"
   # デフォルト: "30m" (30分 - 安定性優先)
   no_change_timeout = "30m"
   
   # 投稿コメントで使うコーディングエージェントのメンションを上書き（省略時は@copilot）
   [coding_agent]
   agent_name = "@codex[agent]"
   
   # 省電力モード時の監視間隔
   # no_change_timeout期間で状態変化が検知されない場合、
   # 監視間隔がこの間隔に切り替わりAPI使用量を削減します
   # 変化が検知されると、通常の監視間隔に戻ります
   # サポートされる形式: "30s", "1m", "5m", "30m", "1h", "1d"
   # デフォルト: "1h" (1時間)
   reduced_frequency_interval = "1h"
   
   # Verboseモード - 詳細な設定情報を表示
   # 有効にすると、起動時に全設定を表示し、実行中にリポジトリ毎の設定も表示します
   # 設定ミスの検出に役立ちます
   # デフォルト: false
   verbose = false
   
   # PR作者の表示切り替え
   # CLI出力で "Author: <login>" を表示するかどうかを制御します
   # デフォルト: false
   display_pr_author = false
   
   # 実行制御フラグ - [[rulesets]]セクション内でのみ指定可能
   # グローバルフラグはサポートされなくなりました
   # 全リポジトリに設定を適用するには 'repositories = ["all"]' を使用してください
   
   # ルールセット設定例:
   # [[rulesets]]
   # name = "全リポジトリのデフォルト - dry-runモード"
   # repositories = ["all"]  # "all" は全リポジトリにマッチします
   # enable_execution_phase1_to_phase2 = false  # trueにするとdraft PRをready化
   # enable_execution_phase2_to_phase3 = false  # trueにするとphase2コメント投稿
   # enable_execution_phase3_send_ntfy = false  # trueにするとntfy通知送信
   # enable_execution_phase3_to_merge = false   # trueにするとphase3 PRをマージ
   
   # [[rulesets]]
   # name = "シンプル: good first issueをCopilotに自動割り当て"
   # repositories = ["my-repo"]
   # assign_good_first_old = true  # これだけでOK！ [assign_to_copilot]セクションは不要です
   #                               # デフォルト動作: ブラウザでissueを開いて手動割り当て
   
   # ntfy.sh通知設定（オプション）
   # 通知にはPRを開くためのクリック可能なアクションボタンが含まれます
   [ntfy]
   enabled = false  # trueにすると通知を有効化
   topic = "<ここにntfy.shのトピック名を書く>"  # 誰でも読み書きできるので、推測されない文字列にしてください
   message = "PR is ready for review: {url}"  # メッセージテンプレート
   priority = 4  # 通知の優先度（1=最低、3=デフォルト、4=高、5=最高）
   all_phase3_message = "All PRs are now in phase3 (ready for review)"  # すべてのPRがphase3になったときのメッセージ
   
   # Phase3自動マージ設定（オプション）
   # PRがphase3（レビュー待ち）に達したら自動的にマージします
   # マージ前に、以下で定義したコメントがPRに投稿されます
   # マージ成功後、自動的にfeature branchが削除されます
   # 重要: 安全のため、この機能はデフォルトで無効です
   # リポジトリごとにrulesetsで enable_execution_phase3_to_merge = true を指定して明示的に有効化する必要があります
   # 重要：自動マージが有効な場合、commentフィールドを明示的に設定する必要があります
   [phase3_merge]
   comment = "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"  # マージ前に投稿するコメント（自動マージ有効時は必須）
   automated = false  # trueにするとブラウザ自動操縦でマージボタンをクリック
   wait_seconds = 10  # ブラウザ起動後、ボタンクリック前の待機時間（秒）
   debug_dir = "debug_screenshots"  # 画像認識失敗時のデバッグ情報保存先（デフォルト: "debug_screenshots"）
   
   # issueをCopilotに自動割り当て（完全にオプション！このセクション全体がオプションです）
   # 
   # シンプルな使い方: rulesetsで assign_good_first_old = true とするだけ（上記の例を参照）
   # このセクションは、デフォルト動作をカスタマイズしたい場合のみ定義してください。
   # 
   # 割り当て動作はrulesetのフラグで制御します:
   # - assign_good_first_old: 最も古い"good first issue"を割り当て（issue番号順、デフォルト: false）
   # - assign_old: 最も古いissueを割り当て（issue番号順、ラベル不問、デフォルト: false）
   # 両方がtrueの場合、"good first issue"を優先
   # 
   # デフォルト動作（このセクションが定義されていない場合）:
   # - ブラウザ自動操縦で自動的にボタンをクリック
   # - PyAutoGUIを使用した画像認識
   # - 画像認識が失敗した場合、OCRフォールバック（オプション）
   # - wait_seconds = 10
   # 
   # 必須: PyAutoGUIのインストールが必要（pip install pyautogui pillow）
   # オプション: OCRフォールバックにはpytesseractのインストールが必要
   # 
   # 重要: 安全のため、この機能はデフォルトで無効です
   # リポジトリごとにrulesetsで assign_good_first_old または assign_old を指定して明示的に有効化する必要があります
   [assign_to_copilot]
   wait_seconds = 10  # ブラウザ起動後、ボタンクリック前の待機時間（秒）
   debug_dir = "debug_screenshots"  # 画像認識失敗時のデバッグ情報保存先（デフォルト: "debug_screenshots"）
   confidence = 0.8  # 画像マッチングの信頼度 0.0-1.0（デフォルト: 0.8）
   enable_ocr_detection = true  # OCRフォールバックを有効化（デフォルト: true）
   # enable_html_detection = false  # HTML検出フォールバック（実験的、デフォルト: false）
   ```

4. **ボタンスクリーンショットの準備（自動化を使用する場合のみ）**:
   
   自動化機能（`automated = true` または `assign_to_copilot` / `phase3_merge` の有効化）を使用する場合、
   PyAutoGUIがクリックするボタンのスクリーンショットが必要です。
   
   **必要なスクリーンショット:**
   
   issueの自動割り当て用（`assign_to_copilot` 機能）:
   - `assign_to_copilot.png` - "Assign to Copilot" ボタンのスクリーンショット
   - `assign.png` - "Assign" ボタンのスクリーンショット
   
   PRの自動マージ用（`phase3_merge` 機能で `automated = true` の場合）:
   - `merge_pull_request.png` - "Merge pull request" ボタンのスクリーンショット
   - `confirm_merge.png` - "Confirm merge" ボタンのスクリーンショット
   - `delete_branch.png` - "Delete branch" ボタンのスクリーンショット（オプション）
   
   **スクリーンショットの撮り方:**
   
   a. GitHubのissueまたはPRをブラウザで開く
   b. 自動化したいボタンを見つける
   c. **ボタンだけ**のスクリーンショットを撮る（画面全体ではなく）
   d. PNG形式で `screenshots` ディレクトリに保存する
   e. 上記の正確なファイル名を使用する
   
   **ヒント:**
   - スクリーンショットはボタンのみを含め、小さな余白を含める
   - OSのスクリーンショットツールを使用する（Windows: Snipping Tool、Mac: Cmd+Shift+4）
   - ボタンがはっきり見え、隠れていないことを確認
   - ボタンの見た目が変わる場合（テーマ変更など）、スクリーンショットを更新する必要があります
   - 画像認識の信頼度を調整する場合は `confidence` 設定を使用（DPI scalingやテーマによる）
   
   **デバッグ情報の自動保存:**
   - 画像認識が失敗した場合、自動的にデバッグ情報が保存されます
   - 保存先：`debug_screenshots/` ディレクトリ（デフォルト）
   - 保存内容：
     - スクリーンショット（失敗時の画面全体）: `{button_name}_fail_{timestamp}.png`
     - 候補領域のスクリーンショット（見つかった場合）: `{button_name}_candidate_{timestamp}_{number}.png`
     - 失敗情報JSON: `{button_name}_fail_{timestamp}.json`
       - ボタン名、タイムスタンプ、信頼度閾値、スクリーンショットパス、テンプレート画像パス
       - 候補領域の情報（座標、サイズ、信頼度）
   - デバッグ時は低い信頼度（0.7, 0.6, 0.5）で最大3つの候補領域を検出
   - デバッグディレクトリは設定で変更可能：`debug_dir` オプション（`assign_to_copilot` または `phase3_merge` セクション内）
   
   **フォールバック方式（画像認識が失敗した場合）:**
   - **OCR検出（デフォルト有効）**: pytesseractを使用してボタンのテキストを検出
     - 「Assign to Copilot」などのテキストを画面上から直接検出
     - サブピクセルレンダリングの違いに対して頑健
     - 必須: tesseract-ocrのインストール（システムレベル）
     - 無効化: `enable_ocr_detection = false`
   
   **重要な要件:**
   - デフォルトブラウザで**GitHubに既にログイン済み**である必要があります
   - 自動化は既存のブラウザセッションを使用します（新しい認証は行いません）
   - ボタンクリック時に正しいGitHubウィンドウ/タブがフォーカスされ、画面に表示されていることを確認してください
   - 複数のGitHubページが開いている場合、最初に見つかったボタンがクリックされます
   
   **スクリーンショットディレクトリの作成:**
   ```bash
   mkdir screenshots
   ```

5. PyAutoGUIをインストール（自動化を使用する場合のみ）：
   
   基本的な画像認識のみ:
   ```bash
   pip install pyautogui pillow pygetwindow
   ```
   
   OCRフォールバックも含む（推奨）:
   ```bash
   pip install -r requirements-automation.txt
   ```
   
   OCRを使用する場合は、システムにtesseract-ocrをインストール:
   - **Windows**: `choco install tesseract`
   - **macOS**: `brew install tesseract`
   - **Linux**: `apt-get install tesseract-ocr`

### 実行

ツールを起動して監視を開始：

```bash
python3 cat-github-watcher.py [config.toml]
```

または、Pythonモジュールとして直接実行：

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### 動作の流れ

1. **起動**: ツールを起動すると、認証済みGitHubユーザーのユーザー所有リポジトリの監視を開始
2. **PR検知**: オープンPRを持つリポジトリを自動検出
3. **フェーズ判定**: 各PRのフェーズを判定（phase1/2/3、LLM working）
4. **アクション実行**:
   - **phase1**: デフォルトはDry-run（rulesetsで`enable_execution_phase1_to_phase2 = true`とするとDraft PRをReady状態に変更）
   - **phase2**: デフォルトはDry-run（rulesetsで`enable_execution_phase2_to_phase3 = true`とするとCopilotに変更適用を依頼するコメントを投稿）
   - **phase3**: ブラウザでPRページを開く
     - rulesetsで`enable_execution_phase3_send_ntfy = true`とするとntfy.sh通知も送信
     - rulesetsで`enable_execution_phase3_to_merge = true`とするとPRを自動マージ（グローバル`[phase3_merge]`設定を使用）
   - **LLM working**: 待機（全PRがこの状態の場合、オープンPRのないリポジトリのissueを表示）
5. **Issue自動割り当て**: 全PRが「LLM working」かつオープンPRのないリポジトリがある場合：
   - rulesetsで`assign_good_first_old = true`とすると最も古い"good first issue"を自動割り当て（issue番号順）
   - rulesetsで`assign_old = true`とすると最も古いissueを自動割り当て（issue番号順、ラベル不問）
   - 両方がtrueの場合、"good first issue"を優先
   - デフォルト動作: PyAutoGUIで自動的にボタンをクリック（`[assign_to_copilot]`セクションは不要）
   - 必須: PyAutoGUIのインストールとボタンスクリーンショットの準備が必要
6. **繰り返し**: 設定された間隔で監視を継続
   - 状態変化がない状態が`no_change_timeout`で設定された時間だけ続いた場合、自動的に省電力モード（`reduced_frequency_interval`）に切り替わりAPI使用量を削減
   - 変化が検知されると通常の監視間隔に戻る

### Dry-runモード

デフォルトでは、ツールは**Dry-runモード**で動作し、実際のアクションは実行しません。これにより、安全に動作を確認できます。

- **Phase1（Draft → Ready化）**: `[DRY-RUN] Would mark PR as ready for review` と表示されるが、実際には何もしない
- **Phase2（コメント投稿）**: `[DRY-RUN] Would post comment for phase2` と表示されるが、実際には何もしない
- **Phase3（ntfy通知）**: `[DRY-RUN] Would send ntfy notification` と表示されるが、実際には何もしない
- **Phase3（マージ）**: `[DRY-RUN] Would merge PR` と表示されるが、実際には何もしない

実際のアクションを有効にするには、`config.toml`の`[[rulesets]]`セクションで以下のフラグを`true`に設定します：
```toml
[[rulesets]]
name = "特定のリポジトリで自動化を有効化"
repositories = ["test-repo"]  # または ["all"] で全リポジトリ
enable_execution_phase1_to_phase2 = true  # Draft PRをReady化
enable_execution_phase2_to_phase3 = true  # Phase2コメント投稿
enable_execution_phase3_send_ntfy = true  # ntfy通知送信
enable_execution_phase3_to_merge = true   # Phase3 PRをマージ
assign_good_first_old = true              # good first issueを自動割り当て
```

### 停止

`Ctrl+C` で監視を停止できます。

## 注意事項

- GitHub CLI (`gh`) がインストールされ、認証済みである必要があります
- GitHub Copilot (特に copilot-pull-request-reviewer と copilot-swe-agent) との連携を前提としています
- 認証済みユーザーの**ユーザー所有リポジトリのみ**が監視対象になります。ツールをシンプルかつ集中させるため、Organizationリポジトリは含まれません（YAGNI原則）
- GraphQL APIを使用するため、APIレート制限に注意してください
- ntfy.sh通知を使用する場合は、事前に[ntfy.sh](https://ntfy.sh/)でトピックを設定してください

## テスト

プロジェクトにはpytestを使用したテストスイートが含まれています：

```bash
pytest tests/
```

## ライセンス

MIT License - 詳細はLICENSEファイルを参照してください

※英語版README.mdは、README.ja.mdを元にGeminiの翻訳でGitHub Actionsにより自動生成しています

*Big Brother is watching your repositories. Now it’s the cat.* 🐱

{% endraw %}
```

### .github/actions-tmp/issue-notes/16.md
```md
{% raw %}
# issue issue-note / project-summary / translate / callgraph をtonejs-mml-to-jsonから呼び出す #16
[issues #16](https://github.com/cat2151/github-actions/issues/16)

# これまでの課題
- issue-note / project-summary / translate / callgraph は、github-actions リポジトリ上ではtest greenである。
- だが他のリポジトリにおいて動作するか？が可視化不足である。

# 対策
- issue-note / project-summary / translate / callgraph をtonejs-mml-to-jsonから呼び出す
- 詳しく
    - まず、現状、tonejs-mml-to-json でその4つのworkflowがどうなっているか、このmdに可視化する
    - 例えば、既に呼び出している、呼び出していない、tonejs-mml-to-jsonにある古いworkflowを呼び出している

# 調査結果
- まず、現状、tonejs-mml-to-json でその4つのworkflowがどうなっているか、このmdに可視化する
    - 結果：
        - issue-note
            - tonejs-mml-to-jsonにある古いworkflowを呼び出している
        - project-summary
            - tonejs-mml-to-jsonにある古いworkflowを呼び出している
        - translate
            - tonejs-mml-to-jsonにある古いworkflowを呼び出している
        - callgraph
            - tonejs-mml-to-jsonにある古いworkflowを呼び出している

# どうする？
- issue-note
    - github-actions リポジトリにある、call-issue-note.yml をcpして使うようにする、まず単純cpして動くかを確認する
- project-summary
    - github-actions リポジトリにある、call-daily-project-summary.yml をcpして使うようにする、まず単純cpして動くかを確認する
- translate
    - github-actions リポジトリにある、call-translate-readme.yml をcpして使うようにする、まず単純cpして動くかを確認する
- callgraph
    - github-actions リポジトリにある、call-callgraph.yml をcpして使うようにする、まず単純cpして動くかを確認する

# 状況
- issue-note
    - tonejs-mml-to-jsonリポジトリにて、test green
    - issue-noteについては当issueのタスクは完了した、と判断する
- project-summary
    - tonejs-mml-to-jsonリポジトリにて、test green
    - project-summaryについては当issueのタスクは完了した、と判断する

# 状況
- translate
    - github-actions リポジトリにある、call-translate-readme.yml をcpして使うようにする、まず単純cpして動くかを確認する
        - 状況
            - 単純cpした
            - ソース机上レビューした。OK
            - トリガーはREADME.ja.mdのcommit
            - testは省略とする
            - もし今後README.ja.mdのcommit時にうまく動作しないとしても、そのとき対処すればOK、と判断する
    - translateについては当issueのタスクは完了した、と判断する

# どうする？
- callgraph
    - github-actions リポジトリにある、call-callgraph.yml をcpして使うようにする、まず単純cpして動くかを確認する

# 結果
- callgraph
    - tonejs-mml-to-jsonリポジトリにて、test red
    - logをみても情報不足なため、まずloggerを修正する
    - 結果、わかった、運用ミス、対象srcの指定の考慮漏れ
    - どうする？
        - 対象srcを指定する。tonejs-mml-to-jsonリポジトリにて進める
    - 結果
        - test green
    - callgraphについては当issueのタスクは完了した、と判断する

# 状況
- github-actions以外のリポジトリとして、
    - tonejs-mml-to-jsonリポジトリにおいて、
        - issue-note / project-summary / translate / callgraph がtest greenとなった。
        - closeできる、と判断する。

# closeとする

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

### .github/actions-tmp/issue-notes/18.md
```md
{% raw %}
# issue DevelopmentStatusGenerator.cjs 内に、Geminiに与えるpromptがハードコーディングされてしまっている #18
[issues #18](https://github.com/cat2151/github-actions/issues/18)

# 何が困るの？
- project把握しづらい。どこにpromptが書いてあるのか、把握しづらい。
- prompts/ にほかのpromptがあるため、方針がブレていると、読みづらい。
- 備忘、いくらテンプレートリテラルとプレースホルダーで密結合しているからとはいえ、ハードコーディングはNG。
    - それらはreplaceを使う等で楽に切り出しできるので。

# 問題のcjsの場所は？
- ファイルパス : .github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
- 関数 : generateDevelopmentStatus

# 結果
- Geminiに生成させたpromptを、agentに投げて、リファクタリングさせてみた
- ハルシネーションした。使い物にならなかった
- 人力でやる

# 結果
- test green

# closeとする


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

### .github/actions-tmp/issue-notes/20.md
```md
{% raw %}
# issue project-summary の development-status 生成時、issue-notes/ 配下のmdにファイル名が書いてあれば、そのファイル内容もpromptに添付、を試す #20
[issues #20](https://github.com/cat2151/github-actions/issues/20)

# 何が困るの？
- Geminiに次の一手を生成させるとき、cjsの内容も添付したほうが、生成品質が改善できる可能性がある。

# 案
## outputのimage
- promptが言及するfilename、について、そのfileの内容もすべてpromptに含める。
    - 軸は、projectのfilename一覧である。
        - 一覧それぞれのfilenameについて、promptで言及されているものをfile内容埋め込み、とする。
- 方向性
    - シンプルで明確なルール、曖昧さのないルールで、メンテを楽にすることを優先する
    - 余分なファイルが出てしまうが割り切ってOKとし、欠落リスクを減らせることを優先する
- 備考
    - 曖昧でメンテが必要な「documentからのfilename抽出」をやめ、
        - かわりに、逆に、「今のprojectにあるfileすべてのうち、promptで言及されているもの」を軸とする
## 実現方法の案
- project全体について、filenameと、filepath配列（複数ありうる）、のmapを取得する。そういう関数Aをまず実装する。
    - filepathは、agentが扱えるよう、github上のworkの絶対pathではなく、projectRootからの相対パス表記とする。
- そして、そのfilenameにmatchするfilepath配列について、filepathとファイル内容を記したmarkdown文字列を返却、という関数Bを実装する。
- さらに、Geminiにわたすpromptについて、前述の関数Aのfilenameそれぞれについて、prompt内を検索し、filenameが存在する場合は、そのfilenameについて、関数Bを用いてmarkdown文字列を取得する。そうして得られたmarkdown文字列群を返却する、という関数Cを実装する。
- さらに、promptの末尾に書いてあるプレースホルダー「`${file_contents}`」を、関数Cの結果で置き換える、という関数Dを実装する。
- 実際には、Geminiにわたすpromptのプレースホルダー展開は、2回にわたる必要がある。1回目でissues-note内容をpromptに埋め込む。2回目でそのpromptに対して関数Dを適用する。
## 備忘
- 上記は、agentにplanさせてレビューし、context不足と感じたら上記をメンテ、というサイクルで書いた。

# どうする？
- 上記をagentに投げる。documentやtestについてのplanもしてくるかもしれないがそこは時間の都合で省略して実施させるつもり。
- 投げた、実装させた、レビューして人力リファクタリングした
- testする

# 結果
- バグ
    - この20.mdにあるプレースホルダーが置換されてしまっている
    - issue-notesで言及されていないfileまで添付されてしまっている
- 分析
    - この20.mdにあるプレースホルダーが置換されてしまっている
        - 原因
            - 20.mdにあるプレースホルダーまで置換対象としてしまっていたため。
            - prompt全体のプレースホルダーを置換対象としてしまっていたため。
            - issue-notesを埋め込んだあとでの、プレースホルダー処理だったので、
                - 20.md が置換対象となってしまったため。
        - 対策案
            - プレースホルダーはすべて、「行頭と行末で囲まれている」ときだけ置換対象とする。
                - つまり文中やcode中のプレースホルダーは置換対象外とする。
            - さらに、2つ以上プレースホルダーが出たら想定外なので早期エラー終了させ、検知させる。
    - issue-notesで言及されていないfileまで添付されてしまっている
        - 原因
            - promptに、既にprojectの全file listが書き込まれたあとなので、
                - issue-noteで言及されていなくても、
                - promptの全file listを対象に検索してしまっている
        - 対策案の候補
            - プレースホルダー置換の順番を変更し、全file listは最後に置換する
            - file添付の対象を変更し、promptでなく、issue-notesとする
                - これが範囲が絞られているので安全である、と考える
        - 備忘
            - 全fileの対象は、リモートリポジトリ側のfileなので、secretsの心配はないし、実際に検索して確認済み

# どうする？
- agent半分、人力が半分（agentがハルシネーションでソース破壊したので、関数切り分けしたり、リファクタリングしたり）。
- で実装した。
- testする

# 結果
- test green

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

## 最近の変更（過去7日間）
### コミット履歴:
dc1c999 Merge pull request #215 from cat2151/codex/analyze-phase1-llm-status
8cbed8c fix: recompute phase after reaction snapshot
98db17c fix: respect llm status timeline for phase3 detection
3ae625e Initial plan
cf66373 Merge pull request #213 from cat2151/codex/remove-saved-pr-snapshot-message
f463821 chore: suppress snapshot snapshot log
55a5f8c Initial plan
ffcdc99 Merge pull request #211 from cat2151/codex/investigate-phase-display-issue
d3e31c0 chore: simplify llm timeline guard
d95b9f8 feat: print llm status timeline for debugging

### 変更されたファイル:
src/gh_pr_phase_monitor/display.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/phase_detector.py
src/gh_pr_phase_monitor/pr_actions.py
src/gh_pr_phase_monitor/pr_data_recorder.py
tests/test_phase_detection.py
tests/test_pr_actions.py
tests/test_pr_data_recorder.py
tests/test_status_summary.py


---
Generated at: 2026-02-09 07:02:46 JST
