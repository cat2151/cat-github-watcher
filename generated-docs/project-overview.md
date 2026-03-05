Last updated: 2026-03-06

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動実装を行うPull Requestのフェーズを監視するツールです。
- 認証済みGitHubユーザーが所有するリポジトリのPRを自動検出し、その進捗を追跡します。
- PRの状態（Draft、レビュー対応中、レビュー待ちなど）に応じて、自動コメント投稿、PRのReady化、モバイル通知などのアクションを実行します。

## 技術スタック
- フロントエンド: PyAutoGUI (GUI自動操作によるブラウザ連携), Pillow (画像処理), PyGetWindow (ウィンドウ管理), pytesseract (OCRによるテキスト検出)
- 音楽・オーディオ: 該当なし
- 開発ツール: GitHub CLI (gh) (GitHub認証と操作), Git (バージョン管理), pytest (テストフレームワーク), Ruff (Pythonコードのリンター・フォーマッター), TOML (設定ファイル形式), .editorconfig (コードスタイルの一貫性維持), VS Code (統合開発環境の設定)
- テスト: pytest (Pythonコードの単体・結合テスト)
- ビルドツール: pip (Pythonパッケージのインストールと依存関係管理)
- 言語機能: Python 3.11+ (主要プログラミング言語), GitHub GraphQL API (効率的なデータ取得のためのGitHub API)
- 自動化・CI/CD: ntfy.sh (モバイルプッシュ通知サービス), PyAutoGUI (ブラウザ自動操作), 自己更新機能 (ツールの自動アップデート), 自動Git Pull機能 (ローカルリポジトリの自動更新)
- 開発標準: .editorconfig (コーディングスタイル統一), Ruff (コード品質・スタイルチェック)

## ファイル階層ツリー
```
cat-github-watcher/
├── cat-github-watcher.py
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py
│       ├── config.py
│       ├── github_client.py
│       ├── phase_detector.py
│       ├── comment_manager.py
│       ├── pr_actions.py
│       └── main.py
└── tests/
```

※ 提供された簡略化されたツリーに加え、プロジェクト情報から詳細なツリーを以下に再掲します。

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
│       │   └── window_manager.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── colors.py
│       │   ├── config.py
│       │   ├── config_printer.py
│       │   ├── interval_parser.py
│       │   ├── process_utils.py
│       │   └── time_utils.py
│       ├── github/
│       │   ├── __init__.py
│       │   ├── comment_fetcher.py
│       │   ├── comment_manager.py
│       │   ├── github_auth.py
│       │   ├── github_client.py
│       │   ├── graphql_client.py
│       │   ├── issue_fetcher.py
│       │   ├── pr_fetcher.py
│       │   ├── rate_limit_handler.py
│       │   └── repository_fetcher.py
│       ├── main.py
│       ├── monitor/
│       │   ├── __init__.py
│       │   ├── auto_updater.py
│       │   ├── local_repo_watcher.py
│       │   ├── monitor.py
│       │   ├── pages_watcher.py
│       │   ├── snapshot_markdown.py
│       │   ├── snapshot_path_utils.py
│       │   └── state_tracker.py
│       ├── phase/
│       │   ├── __init__.py
│       │   ├── llm_status_extractor.py
│       │   ├── phase_detector.py
│       │   ├── phase_detector_graphql.py
│       │   ├── pr_data_recorder.py
│       │   ├── pr_html_analyzer.py
│       │   ├── pr_html_fetcher.py
│       │   └── pr_html_saver.py
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
    ├── test_fetch_pr_html.py
    ├── test_graphql_client_rate_limit.py
    ├── test_graphql_query_intent_display.py
    ├── test_has_comments_with_reactions.py
    ├── test_has_unresolved_review_threads.py
    ├── test_hot_reload.py
    ├── test_html_to_markdown.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_contamination_bug.py
    ├── test_interval_parsing.py
    ├── test_issue_assignment_priority.py
    ├── test_issue_fetching.py
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
    ├── test_pr_data_recorder.py
    ├── test_pr_data_recorder_html.py
    ├── test_pr_data_recorder_json.py
    ├── test_pr_html_analyzer.py
    ├── test_pr_title_fix.py
    ├── test_rate_limit_reset_display.py
    ├── test_rate_limit_throttle.py
    ├── test_rate_limit_usage_display.py
    ├── test_repos_with_prs_structure.py
    ├── test_show_issues_when_pr_count_less_than_3.py
    ├── test_status_summary.py
    ├── test_validate_phase3_merge_config.py
    ├── test_verbose_config.py
    └── test_wait_handler_callback.py
```

## ファイル詳細説明
-   `.editorconfig`: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
-   `.gitignore`: Gitがバージョン管理の対象としないファイルやディレクトリを指定する設定ファイルです。
-   `.vscode/settings.json`: VS Codeエディタのワークスペース固有の設定を定義します。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）を記載しています。
-   `README.ja.md`: プロジェクトの日本語版説明ドキュメントです。
-   `README.md`: プロジェクトの英語版説明ドキュメントです。
-   `_config.yml`: GitHub Pagesなどの静的サイトジェネレーターの設定ファイル（ドキュメントサイト用）です。
-   `cat-github-watcher.py`: プロジェクトのエントリーポイントとなるメインスクリプトです。
-   `config.toml.example`: ツールが使用する設定ファイル`config.toml`のサンプルです。
-   `demo_automation.py`: 自動化機能のデモンストレーション用スクリプトです。
-   `docs/RULESETS.md`: プロジェクトの設定におけるルールセットに関する詳細なドキュメントです。
-   `docs/button-detection-improvements.ja.md`: ボタン検出機能の改善に関する日本語ドキュメントです。
-   `docs/window-activation-feature.md`: ウィンドウアクティベーション機能に関するドキュメントです。
-   `fetch_pr_html.py`: Pull RequestのHTMLコンテンツを取得するための補助スクリプトです。
-   `generated-docs/`: 自動生成されたドキュメントを格納するディレクトリです。
-   `pyproject.toml`: Pythonプロジェクトのメタデータやビルド設定を定義するファイルです。
-   `pytest.ini`: pytestテストフレームワークの設定ファイルです。
-   `requirements-automation.txt`: 自動化機能に必要なPythonパッケージのリストです。
-   `ruff.toml`: Ruffリンターの設定ファイルです。
-   `screenshots/`: ブラウザ自動操作で使用するボタンのスクリーンショットを格納するディレクトリです。
    -   `assign.png`: "Assign"ボタンのスクリーンショット。
    -   `assign_to_copilot.png`: "Assign to Copilot"ボタンのスクリーンショット。
-   `src/gh_pr_phase_monitor/actions/pr_actions.py`: PRをReady状態に変更したり、ブラウザでPRページを開いたりするなどのアクションを実行するロジックを含みます。
-   `src/gh_pr_phase_monitor/browser/browser_automation.py`: ブラウザ自動操作の主要なロジックを実装しています。
-   `src/gh_pr_phase_monitor/browser/browser_cooldown.py`: ブラウザ操作間のクールダウン（待機時間）を管理し、APIレート制限などを考慮します。
-   `src/gh_pr_phase_monitor/browser/button_clicker.py`: 画像認識やOCR（光学文字認識）を用いて特定のボタンを検出し、クリックする処理を担います。
-   `src/gh_pr_phase_monitor/browser/click_config_validator.py`: ボタンクリック操作に関する設定の有効性を検証します。
-   `src/gh_pr_phase_monitor/browser/window_manager.py`: ブラウザウィンドウの管理や操作（最大化、前面表示など）に関するロジックを提供します。
-   `src/gh_pr_phase_monitor/core/colors.py`: ターミナル出力用のANSIカラーコードを定義し、色付けを容易にするユーティリティです。
-   `src/gh_pr_phase_monitor/core/config.py`: `config.toml`ファイルから設定を読み込み、パースし、管理する役割を担います。
-   `src/gh_pr_phase_monitor/core/config_printer.py`: 現在のアクティブな設定情報を整形してコンソールに表示するユーティリティです。
-   `src/gh_pr_phase_monitor/core/interval_parser.py`: "30s"や"1m"のような時間間隔を表す文字列を解析し、秒数などに変換するユーティリティです。
-   `src/gh_pr_phase_monitor/core/process_utils.py`: プロセス関連のユーティリティ関数を提供します。
-   `src/gh_pr_phase_monitor/core/time_utils.py`: 時間に関する様々なユーティリティ関数を提供します。
-   `src/gh_pr_phase_monitor/github/comment_fetcher.py`: GitHub Pull Requestのコメントを取得するロジックを実装しています。
-   `src/gh_pr_phase_monitor/github/comment_manager.py`: GitHub Pull Requestへのコメント投稿や、既存コメントの管理を行います。
-   `src/gh_pr_phase_monitor/github/github_auth.py`: GitHub CLI (`gh`) を利用した認証処理を担当します。
-   `src/gh_pr_phase_monitor/github/github_client.py`: GitHub APIとの基本的な連携を行うクライアントを提供します。
-   `src/gh_pr_phase_monitor/github/graphql_client.py`: GitHub GraphQL APIを操作するためのクライアントです。
-   `src/gh_pr_phase_monitor/github/issue_fetcher.py`: GitHub Issuesの情報を取得するロジックを実装しています。
-   `src/gh_pr_phase_monitor/github/pr_fetcher.py`: GitHub Pull Requestの情報を取得するロジックを実装しています。
-   `src/gh_pr_phase_monitor/github/rate_limit_handler.py`: GitHub APIのレート制限を監視し、制限を超えないようにリクエストを管理します。
-   `src/gh_pr_phase_monitor/github/repository_fetcher.py`: GitHubリポジトリの情報を取得するロジックを実装しています。
-   `src/gh_pr_phase_monitor/main.py`: プロジェクトのメイン実行ループと、各モジュールの連携を orchestrate する役割を担います。
-   `src/gh_pr_phase_monitor/monitor/auto_updater.py`: ツール自身をGitHubリポジトリの最新版に自動的に更新する機能を提供します。
-   `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`: ローカルにクローンされたリポジトリの状態を監視し、更新が必要かなどをチェックします。
-   `src/gh_pr_phase_monitor/monitor/monitor.py`: Pull Request監視の主要なロジックと、監視状態の管理を行います。
-   `src/gh_pr_phase_monitor/monitor/pages_watcher.py`: GitHub Pagesのデプロイ状況などを監視する機能を提供します。
-   `src/gh_pr_phase_monitor/monitor/snapshot_markdown.py`: PRの状態のスナップショットをMarkdown形式で生成するユーティリティです。
-   `src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py`: スナップショットファイルのパス管理ユーティリティです。
-   `src/gh_pr_phase_monitor/monitor/state_tracker.py`: 監視対象のPRやリポジトリの状態変化を追跡し、記録します。
-   `src/gh_pr_phase_monitor/phase/llm_status_extractor.py`: LLM（大規模言語モデル）の作業ステータスをPRコメントから抽出するロジックを実装しています。
-   `src/gh_pr_phase_monitor/phase/phase_detector.py`: Pull Requestの現在のフェーズ（例: Draft、レビュー待ち）を高レベルで判定する主要なロジックです。
-   `src/gh_pr_phase_monitor/phase/phase_detector_graphql.py`: GraphQL APIを利用してPull Requestのフェーズをより詳細かつ効率的に判定するロジックです。
-   `src/gh_pr_phase_monitor/phase/pr_data_recorder.py`: Pull Requestに関するデータを記録・保存する機能を提供します。
-   `src/gh_pr_phase_monitor/phase/pr_html_analyzer.py`: Pull RequestのHTMLコンテンツを解析し、特定の情報（LLMのステータスなど）を抽出します。
-   `src/gh_pr_phase_monitor/phase/pr_html_fetcher.py`: Pull RequestのHTMLコンテンツをウェブから取得するロジックです。
-   `src/gh_pr_phase_monitor/phase/pr_html_saver.py`: 取得したPull RequestのHTMLコンテンツをローカルに保存するロジックです。
-   `src/gh_pr_phase_monitor/ui/display.py`: ターミナルへの情報表示を整形し、ユーザーフレンドリーな形式で出力します。
-   `src/gh_pr_phase_monitor/ui/notification_window.py`: GUI通知ウィンドウを表示する機能を提供します。
-   `src/gh_pr_phase_monitor/ui/notifier.py`: ntfy.shサービスを利用してモバイル端末に通知を送信するロジックを実装しています。
-   `src/gh_pr_phase_monitor/ui/wait_handler.py`: 非同期処理や特定の条件が満たされるまでの待機処理を管理するユーティリティです。
-   `tests/`: プロジェクトのテストコードを格納するディレクトリです。各`test_*.py`ファイルは特定のモジュールや機能に対するテストスクリプト。

## 関数詳細説明
提供されたプロジェクト情報には、各関数の具体的な役割、引数、戻り値、機能に関する詳細な説明が含まれていませんでした。そのため、ハルシネーションを避けるため、具体的な関数の詳細を生成することはできません。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした

---
Generated at: 2026-03-06 07:04:29 JST
