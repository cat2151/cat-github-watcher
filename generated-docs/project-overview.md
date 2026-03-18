Last updated: 2026-03-19

# Project Overview

## プロジェクト概要
- GitHub CopilotなどAIエージェントによる自動実装フェーズのプルリクエストを効率的に監視するPythonツールです。
- PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、AI作業中）を自動判定し、通知や自動アクションを実行します。
- ユーザー所有リポジトリのPR自動Ready化、コメント投稿、モバイル通知、Issue自動割り当て、ローカルリポジトリ同期などの機能を提供します。

## 技術スタック
- フロントエンド: PyAutoGUI, PyGetWindow, Pillow, pytesseract (ブラウザ自動操作およびOCRによるGUI要素検出に利用)。直接的なWeb UIは持ちませんが、既存のブラウザインターフェースを操作します。
- 音楽・オーディオ: 該当なし
- 開発ツール: GitHub CLI (`gh`), Git (ローカルリポジトリ監視、`gh auth login`による認証)。
- テスト: Pytest (豊富なテストスイートにより、機能の検証と品質維持に貢献)。
- ビルドツール: pip (Pythonパッケージ管理), cargo (Rustプロジェクトのバイナリ自動更新にオプションで利用)。
- 言語機能: Python 3.11+ (アプリケーションの主要開発言語)。GraphQL API (GitHubデータ取得のための効率的なクエリ言語)。
- 自動化・CI/CD: GitHub Actions (README翻訳などプロジェクトの補助的な自動化に利用。本体はPythonスクリプトによる自動化)、ntfy.sh (モバイル通知の自動化)、auto_updater (アプリケーションの自己更新機能)。
- 開発標準: Ruff (Pythonコードのリンティングとフォーマット), .editorconfig (エディタ設定の統一)。

## ファイル階層ツリー
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
**(注: 提供されたツリーは一部であり、完全な構造は以下の「ファイル詳細説明」で補足されます)**
```
cat-github-watcher/
├── .editorconfig
├── .gitignore
├── .vscode/
│   └── settings.json
├── LICENSE
├── README.ja.md
├── README.md
├── _config.yml
├── cat-github-watcher.py
├── config.toml.example
├── demo_automation.py
├── docs/
│   ├── RULESETS.md
│   ├── button-detection-improvements.ja.md
│   └── window-activation-feature.md
├── fetch_pr_html.py
├── generated-docs/
├── pyproject.toml
├── pytest.ini
├── requirements-automation.txt
├── ruff.toml
├── screenshots/
│   ├── assign.png
│   └── assign_to_copilot.png
├── src/
│   ├── __init__.py
│   └── gh_pr_phase_monitor/
│       ├── __init__.py
│       ├── actions/
│       │   ├── __init__.py
│       │   └── pr_actions.py
│       ├── browser/
│       │   ├── __init__.py
│       │   ├── browser_automation.py
│       │   ├── browser_cooldown.py
│       │   ├── button_clicker.py
│       │   ├── click_config_validator.py
│       │   ├── issue_assigner.py
│       │   └── window_manager.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── colors.py
│       │   ├── config.py
│       │   ├── config_printer.py
│       │   ├── config_ruleset.py
│       │   ├── interval_parser.py
│       │   ├── process_utils.py
│       │   └── time_utils.py
│       ├── github/
│       │   ├── __init__.py
│       │   ├── comment_fetcher.py
│       │   ├── comment_manager.py
│       │   ├── etag_checker.py
│       │   ├── github_auth.py
│       │   ├── github_client.py
│       │   ├── graphql_client.py
│       │   ├── issue_etag_checker.py
│       │   ├── issue_fetcher.py
│       │   ├── pr_fetcher.py
│       │   ├── rate_limit_handler.py
│       │   └── repository_fetcher.py
│       ├── main.py
│       ├── monitor/
│       │   ├── __init__.py
│       │   ├── auto_updater.py
│       │   ├── error_logger.py
│       │   ├── iteration_runner.py
│       │   ├── local_repo_cargo.py
│       │   ├── local_repo_checker.py
│       │   ├── local_repo_git.py
│       │   ├── local_repo_watcher.py
│       │   ├── monitor.py
│       │   ├── pages_watcher.py
│       │   ├── pr_processor.py
│       │   ├── snapshot_path_utils.py
│       │   └── state_tracker.py
│       ├── phase/
│       │   ├── __init__.py
│       │   ├── html/
│       │   │   ├── __init__.py
│       │   │   ├── html_status_processor.py
│       │   │   ├── llm_status_extractor.py
│       │   │   ├── pr_html_analyzer.py
│       │   │   ├── pr_html_fetcher.py
│       │   │   └── pr_html_saver.py
│       │   └── phase_detector.py
│       └── ui/
│           ├── __init__.py
│           ├── display.py
│           ├── notification_window.py
│           ├── notifier.py
│           └── wait_handler.py
└── tests/
    ├── test_assign_issue_to_copilot.py
    ├── test_auto_update_config.py
    ├── test_auto_updater.py
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_browser_automation_click.py
    ├── test_browser_automation_ocr.py
    ├── test_browser_automation_window.py
    ├── test_check_process_before_autoraise.py
    ├── test_color_scheme_config.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_error_logging.py
    ├── test_etag_checker.py
    ├── test_fetch_pr_html.py
    ├── test_graphql_client_rate_limit.py
    ├── test_graphql_query_intent_display.py
    ├── test_has_comments_with_reactions.py
    ├── test_has_unresolved_review_threads.py
    ├── test_hot_reload.py
    ├── test_html_status_processor.py
    ├── test_html_to_markdown.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_contamination_bug.py
    ├── test_interval_parsing.py
    ├── test_is_llm_working.py
    ├── test_issue_assignment_priority.py
    ├── test_issue_etag_checker.py
    ├── test_issue_fetching.py
    ├── test_llm_status_timestamp.py
    ├── test_llm_working_warning.py
    ├── test_local_repo_cargo.py
    ├── test_local_repo_checker.py
    ├── test_local_repo_git.py
    ├── test_local_repo_watcher.py
    ├── test_local_repo_watcher_background.py
    ├── test_max_llm_working_parallel.py
    ├── test_no_change_timeout.py
    ├── test_no_open_prs_issue_display.py
    ├── test_notification.py
    ├── test_open_browser_cooldown.py
    ├── test_pages_watcher.py
    ├── test_phase3_merge.py
    ├── test_phase_detection.py
    ├── test_phase_detection_llm_status.py
    ├── test_phase_detection_real_prs.py
    ├── test_post_comment.py
    ├── test_post_phase3_comment.py
    ├── test_pr_actions.py
    ├── test_pr_actions_dry_run.py
    ├── test_pr_actions_rulesets_features.py
    ├── test_pr_actions_with_rulesets.py
    ├── test_pr_html_analyzer.py
    ├── test_pr_html_analyzer_copilot_review.py
    ├── test_pr_title_fix.py
    ├── test_rate_limit_reset_display.py
    ├── test_rate_limit_throttle.py
    ├── test_rate_limit_usage_display.py
    ├── test_repos_with_prs_structure.py
    ├── test_show_issues_when_pr_count_less_than_3.py
    ├── test_skip_pr_check_html_refetch.py
    ├── test_status_summary.py
    ├── test_updated_at_optimization.py
    ├── test_validate_phase3_merge_config.py
    ├── test_verbose_config.py
    └── test_wait_handler_callback.py
```

## ファイル詳細説明

*   `cat-github-watcher.py`: アプリケーションのメインエントリーポイント。設定ファイルを読み込み、監視プロセスを開始します。
*   `config.toml.example`: アプリケーション設定のサンプルファイル。監視間隔、通知設定、自動化ルールなどが定義されています。
*   `pyproject.toml`: プロジェクトのPythonパッケージメタデータ、依存関係、ビルド設定などを記述するファイル。
*   `requirements-automation.txt`: 自動化機能（PyAutoGUIなど）に必要なPythonライブラリのリスト。
*   `ruff.toml`: Ruffリンター/フォーマッターの設定ファイル。コード品質とスタイルを維持します。
*   `screenshots/`: ブラウザ自動操作機能で使用するボタンのスクリーンショットを保存するディレクトリ。
    *   `assign.png`: GitHubの"Assign"ボタンのスクリーンショット。
    *   `assign_to_copilot.png`: GitHubの"Assign to Copilot"ボタンのスクリーンショット。
*   `src/gh_pr_phase_monitor/main.py`: プロジェクトの主要な監視ループを管理します。定期的にPRをチェックし、フェーズ判定とそれに続くアクションを調整します。
*   `src/gh_pr_phase_monitor/core/colors.py`: ターミナル出力の色付けに使用するANSIカラーコードとカラースキームを定義します。
*   `src/gh_pr_phase_monitor/core/config.py`: アプリケーションの設定ファイル（`config.toml`）の読み込み、解析、検証を行います。
*   `src/gh_pr_phase_monitor/core/config_ruleset.py`: 特定のリポジトリや条件に基づくルールセットの設定を扱います。
*   `src/gh_pr_phase_monitor/github/github_auth.py`: GitHub CLI (`gh`) を利用した認証処理を管理します。
*   `src/gh_pr_phase_monitor/github/github_client.py`: GitHub APIへの主要なインターフェースを提供し、GraphQLクエリの実行などを担当します。
*   `src/gh_pr_phase_monitor/github/pr_fetcher.py`: GitHubからプルリクエストの情報を取得するロジックを含みます。
*   `src/gh_pr_phase_monitor/github/issue_fetcher.py`: GitHubからIssueの情報を取得するロジックを含みます。
*   `src/gh_pr_phase_monitor/github/comment_manager.py`: プルリクエストへのコメント投稿や既存コメントの確認を管理します。
*   `src/gh_pr_phase_monitor/github/etag_checker.py`: ETagを利用してGitHub APIのレートリミットを効率的に管理し、変更がない場合はAPIコールをスキップします。
*   `src/gh_pr_phase_monitor/phase/phase_detector.py`: プルリクエストの現在の状態（フェーズ1, 2, 3, LLM作業中）を判定する主要なロジックを提供します。
*   `src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py`: PRのHTMLコンテンツを解析し、特定の情報（例：LLMのステータス）を抽出します。
*   `src/gh_pr_phase_monitor/actions/pr_actions.py`: PRのフェーズに応じて実行されるアクション（Draft解除、コメント投稿、ブラウザ起動など）を定義します。
*   `src/gh_pr_phase_monitor/browser/browser_automation.py`: PyAutoGUIなどを用いてブラウザを自動操作する低レベルな機能を提供します。
*   `src/gh_pr_phase_monitor/browser/issue_assigner.py`: 特定の条件に基づいてIssueを自動的に割り当てる機能を提供します。
*   `src/gh_pr_phase_monitor/monitor/auto_updater.py`: アプリケーション自身をGitHubから最新の状態に自動更新する機能を提供します。
*   `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`: ローカル環境のGitリポジトリを監視し、pull可能な状態を検知したり、自動でpullを実行したりします。
*   `src/gh_pr_phase_monitor/ui/display.py`: コンソールに情報を整形して表示する役割を担います。
*   `src/gh_pr_phase_monitor/ui/notifier.py`: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
*   `tests/`: プロジェクトの単体テストおよび統合テストを格納するディレクトリ。

## 関数詳細説明

*   `run_monitor()` (in `src/gh_pr_phase_monitor/main.py`):
    *   **役割**: アプリケーションのメイン監視ループを開始・管理します。
    *   **機能**: 設定された間隔で継続的にGitHubからPR情報を取得し、各PRのフェーズ判定、およびそれに応じたアクションの実行を調整します。自己更新チェックやローカルリポジトリ監視も統合します。
*   `fetch_open_pull_requests(client, repo_info)` (in `src/gh_pr_phase_monitor/github/pr_fetcher.py`):
    *   **役割**: 特定のリポジトリから現在オープンなプルリクエストのリストを取得します。
    *   **機能**: GitHub GraphQLクライアントを使用してAPIクエリを実行し、PRのタイトル、ステータス、コメント、レビュー状況などの詳細情報を取得します。
*   `detect_phase(pr_info, config)` (in `src/gh_pr_phase_monitor/phase/phase_detector.py`):
    *   **役割**: 指定されたプルリクエストが現在どの開発フェーズにあるかを判定します。
    *   **機能**: PRのDraft状態、レビューコメントの存在、特定のエージェントからのコメント内容、PRの更新状況などを分析し、「Draft状態」「レビュー指摘対応中」「レビュー待ち」「LLM作業中」のいずれかのフェーズを特定します。
*   `execute_pr_actions(pr, phase, config, github_client)` (in `src/gh_pr_phase_monitor/actions/pr_actions.py`):
    *   **役割**: プルリクエストの現在のフェーズに基づき、設定された自動アクションを実行します。
    *   **機能**: Dry-runモードの確認後、Draft PRをReadyにマークする、特定のコメントを投稿する、ntfy.shでモバイル通知を送信する、ブラウザでPRページを開く、あるいは自動マージを実行するなどの処理を行います。
*   `assign_issues_if_needed(rulesets_config, github_client)` (in `src/gh_pr_phase_monitor/browser/issue_assigner.py`):
    *   **役割**: オープンなPRがないリポジトリに対して、特定のラベルを持つIssueをAIエージェントに自動割り当てします。
    *   **機能**: 設定されたルール（`ci-failure`, `good first issue`など）に基づいて最も古いIssueを特定し、ブラウザ自動操作を用いてそのIssueを割り当てます。
*   `check_and_update(config)` (in `src/gh_pr_phase_monitor/monitor/auto_updater.py`):
    *   **役割**: アプリケーション自身がGitHubリポジトリの最新版に更新されているかを確認し、必要であれば自動でプルして再起動します。
    *   **機能**: ローカルリポジトリとリモートの差分をチェックし、変更があれば`git pull`を実行し、プロセスを再起動して常に最新のバージョンで動作するようにします。
*   `check_local_repositories(config)` (in `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`):
    *   **役割**: 指定されたローカルディレクトリ内のGitリポジトリを監視し、リモートに変更がある場合に通知または自動プルを実行します。
    *   **機能**: 各ローカルリポジトリで`git fetch`を実行し、リモートとローカルの差異を検知して表示します。`auto_git_pull`設定が有効な場合は自動で`git pull`を実行します。

## 関数呼び出し階層ツリー
```
cat-github-watcher.py (アプリケーション起動)
  └─ src.gh_pr_phase_monitor.main.run_monitor()
     ├─ src.gh_pr_phase_monitor.monitor.auto_updater.check_and_update() (自己更新チェック)
     ├─ src.gh_pr_phase_monitor.monitor.monitor.process_repositories() (リポジトリ処理メインループ)
     │  ├─ src.gh_pr_phase_monitor.github.repository_fetcher.fetch_user_repositories() (ユーザーリポジトリ取得)
     │  ├─ src.gh_pr_phase_monitor.github.pr_fetcher.fetch_open_pull_requests() (オープンPR取得)
     │  ├─ src.gh_pr_phase_monitor.phase.phase_detector.detect_phase() (PRフェーズ判定)
     │  ├─ src.gh_pr_phase_monitor.actions.pr_actions.execute_pr_actions() (PRアクション実行)
     │  │  ├─ src.gh_pr_phase_monitor.github.comment_manager.post_comment() (コメント投稿)
     │  │  ├─ src.gh_pr_phase_monitor.ui.notifier.send_notification() (ntfy通知)
     │  │  └─ src.gh_pr_phase_monitor.browser.browser_automation.open_and_click_button() (ブラウザ自動操作)
     │  └─ src.gh_pr_phase_monitor.browser.issue_assigner.assign_issues_if_needed() (Issue自動割り当て)
     │     └─ src.gh_pr_phase_monitor.github.issue_fetcher.fetch_issues() (Issue取得)
     │     └─ src.gh_pr_phase_monitor.browser.browser_automation.open_and_click_button() (ブラウザ自動操作)
     └─ src.gh_pr_phase_monitor.monitor.local_repo_watcher.check_local_repositories() (ローカルリポジトリ監視)
        ├─ src.gh_pr_phase_monitor.monitor.local_repo_git.check_pull_status() (Gitプル状態チェック)
        └─ src.gh_pr_phase_monitor.monitor.local_repo_cargo.handle_cargo_install() (Cargoバイナリ更新)

---
Generated at: 2026-03-19 07:05:29 JST
