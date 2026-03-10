Last updated: 2026-03-11

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのPRを監視し、その状態に応じて適切な通知やアクションを実行するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIを用いて効率的にPRの進捗を管理します。
- レビュー待ちの通知、Draft PRの自動Ready化、レビュー指摘対応コメント投稿、issueの自動割り当てなど、開発ワークフローを効率化する機能を備えています。

## 技術スタック
- フロントエンド:
    - **PyAutoGUI**: ブラウザのUIを自動操作するためのPythonライブラリ。特定のボタンのクリックやウィンドウ操作に使用されます。
    - **Pillow**: 画像処理ライブラリで、PyAutoGUIがスクリーンショットの解析や画像認識を行う際に利用されます。
    - **PyGetWindow**: 実行中のウィンドウを管理し、特定ウィンドウのフォーカスや最大化などに使用されます。
- 音楽・オーディオ:
    - 該当する技術はありません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHubのコマンドラインインターフェース。本ツールのGitHub認証の前提条件となっています。
    - **VS Code**: 開発環境として推奨されており、`.vscode/settings.json`で設定が管理されています。
- テスト:
    - **pytest**: Pythonのテストフレームワーク。プロジェクトの各機能が意図通りに動作するかを検証するために使用されます。
- ビルドツール:
    - **pyproject.toml**: Pythonプロジェクトのビルド設定や依存関係を定義するための標準ファイル。
    - **TOML**: 設定ファイル(`config.toml`)の記述に使用される人間が読みやすい形式のマークアップ言語。
- 言語機能:
    - **Python 3.11+**: プロジェクトの主要な開発言語であり、その最新の言語機能が活用されています。
    - **GraphQL API**: GitHubのデータを効率的に取得するためのAPIクエリ言語。本ツールはGitHubのGraphQL APIを利用してPR情報を取得します。
- 自動化・CI/CD:
    - **git**: リポジトリのバージョン管理、自動更新機能（`git pull`）に利用されます。
    - **ntfy.sh**: モバイル端末への通知をプッシュするためのシンプルな通知サービス。PRがレビュー待ちになった際などに通知を送信します。
    - **tesseract-ocr**: 画像内のテキストを認識するOCRエンジン。PyAutoGUIの画像認識が失敗した場合のフォールバックとして利用されます。
- 開発標準:
    - **ruff**: 高速なPythonリンターおよびフォーマッター。コード品質の維持と統一されたコーディングスタイルを強制するために使用されます。
    - **.editorconfig**: 異なるエディタやIDE間で一貫したコーディングスタイルを定義するための設定ファイル。

## ファイル階層ツリー
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
│       │   ├── error_logger.py
│       │   ├── iteration_runner.py
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
  ├── test_issue_fetching.py
  ├── test_llm_status_timestamp.py
  ├── test_llm_working_warning.py
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
-   **`.editorconfig`**: 異なるエディタやIDE間で一貫したコーディングスタイル（インデント、改行コードなど）を定義する設定ファイル。
-   **`.gitignore`**: Gitがバージョン管理の対象外とするファイルやディレクトリを指定するファイル。
-   **`.vscode/settings.json`**: VS Codeエディタのワークスペース固有の設定を定義するファイル。リンターやフォーマッター、Pythonインタープリタなどの設定が含まれることがあります。
-   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記載したファイル。
-   **`README.ja.md`**: プロジェクトの日本語版説明書。概要、使い方、特徴などが記載されています。
-   **`README.md`**: プロジェクトの英語版説明書。日本語版を元に自動生成されています。
-   **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレータで使用される設定ファイル。
-   **`cat-github-watcher.py`**: プロジェクトのルートエントリーポイント。ツールを直接起動する際に使用されます。
-   **`config.toml.example`**: 設定ファイル`config.toml`のサンプル。ユーザーがコピーしてカスタマイズするためのテンプレートです。
-   **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーションやテストに使用されるスクリプト。
-   **`docs/RULESETS.md`**: 設定ファイルにおけるルールセット（`[[rulesets]]`）の具体的な設定方法や利用例を説明するドキュメント。
-   **`docs/button-detection-improvements.ja.md`**: ボタン検出機能の改善点に関する日本語ドキュメント。
-   **`docs/window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメント。
-   **`fetch_pr_html.py`**: PRのHTMLコンテンツを取得するための補助スクリプト。
-   **`generated-docs/`**: 自動生成されたドキュメントが格納されるディレクトリ。
-   **`pyproject.toml`**: Pythonプロジェクトのビルドシステム、依存関係、ツール設定を定義するファイル。
-   **`pytest.ini`**: pytestテストフレームワークの設定ファイル。テストの実行オプションなどが記述されます。
-   **`requirements-automation.txt`**: ブラウザ自動化に必要な追加のPythonライブラリをリストアップしたファイル。
-   **`ruff.toml`**: Ruffリンター/フォーマッターの設定ファイル。コードスタイルや静的解析ルールを定義します。
-   **`screenshots/`**: PyAutoGUIによるブラウザ自動化で使用するボタン画像のスクリーンショットが保存されるディレクトリ。
-   **`src/__init__.py`**: Pythonパッケージを示すための空のファイル。
-   **`src/gh_pr_phase_monitor/`**: プロジェクトの主要なPythonソースコードが格納されているパッケージ。
    -   **`src/gh_pr_phase_monitor/__init__.py`**: Pythonパッケージを示すための空のファイル。
    -   **`src/gh_pr_phase_monitor/actions/pr_actions.py`**: GitHub PRに対する実際のアクション（Draft PRのReady化、PRマージなど）を実行するロジックを格納。
    -   **`src/gh_pr_phase_monitor/browser/browser_automation.py`**: PyAutoGUIを利用したブラウザの自動操作（指定座標へのクリック、OCRによるテキスト検出など）を管理する。
    -   **`src/gh_pr_phase_monitor/browser/browser_cooldown.py`**: ブラウザ操作のクールダウン期間を管理し、連続した操作を防ぐ。
    -   **`src/gh_pr_phase_monitor/browser/button_clicker.py`**: 特定のボタン画像やテキストを認識し、クリックするロジックを実装。
    -   **`src/gh_pr_phase_monitor/browser/click_config_validator.py`**: ブラウザクリック自動化の設定の妥当性を検証。
    -   **`src/gh_pr_phase_monitor/browser/window_manager.py`**: ブラウザウィンドウの管理（アクティブ化、最大化など）を行う。
    -   **`src/gh_pr_phase_monitor/core/colors.py`**: ターミナル出力の色付けに使用するANSIカラーコードとカラースキームを定義。
    -   **`src/gh_pr_phase_monitor/core/config.py`**: `config.toml`ファイルの読み込み、パース、および設定値へのアクセスを管理。
    -   **`src/gh_pr_phase_monitor/core/config_printer.py`**: 現在の設定値をコンソールに整形して表示する機能を提供。
    -   **`src/gh_pr_phase_monitor/core/interval_parser.py`**: 設定ファイルで指定された時間間隔（例: "1m", "30s"）を秒数に変換する。
    -   **`src/gh_pr_phase_monitor/core/process_utils.py`**: プロセス関連のユーティリティ関数。
    -   **`src/gh_pr_phase_monitor/core/time_utils.py`**: 時間関連のユーティリティ関数。
    -   **`src/gh_pr_phase_monitor/github/comment_fetcher.py`**: GitHub PRのコメントを取得する機能。
    -   **`src/gh_pr_phase_monitor/github/comment_manager.py`**: GitHub PRにコメントを投稿したり、既存コメントを管理する機能。
    -   **`src/gh_pr_phase_monitor/github/github_auth.py`**: GitHub APIへの認証（GitHub CLI `gh`を利用）を管理。
    -   **`src/gh_pr_phase_monitor/github/github_client.py`**: GitHub APIとの主要なインタラクションを担当するクライアント。GraphQLクライアントをラップ。
    -   **`src/gh_pr_phase_monitor/github/graphql_client.py`**: GitHub GraphQL APIへのリクエストを送信し、レスポンスを処理する低レベルクライアント。
    -   **`src/gh_pr_phase_monitor/github/issue_fetcher.py`**: GitHub Issueの情報を取得する機能。
    -   **`src/gh_pr_phase_monitor/github/pr_fetcher.py`**: GitHub Pull Requestの情報を取得する機能。
    -   **`src/gh_pr_phase_monitor/github/rate_limit_handler.py`**: GitHub APIのレート制限を監視し、制限超過を避けるための処理（待機など）を実装。
    -   **`src/gh_pr_phase_monitor/github/repository_fetcher.py`**: 認証済みユーザーが所有するリポジトリの一覧を取得する機能。
    -   **`src/gh_pr_phase_monitor/main.py`**: 監視ツールのメイン実行ループを定義。設定の初期化、監視プロセスの開始と管理を行います。
    -   **`src/gh_pr_phase_monitor/monitor/auto_updater.py`**: ツール自身の自動更新（`git pull`）と再起動を管理する。
    -   **`src/gh_pr_phase_monitor/monitor/error_logger.py`**: 実行中に発生したエラーをログに記録する機能。
    -   **`src/gh_pr_phase_monitor/monitor/iteration_runner.py`**: 監視ループの各イテレーションを実行し、状態変化や省電力モードへの移行を管理。
    -   **`src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`**: ローカルにクローンされたリポジトリの変更を監視し、自動で`git pull`を行う機能。
    -   **`src/gh_pr_phase_monitor/monitor/monitor.py`**: 監視ロジックのコア。リポジトリとPRの情報を定期的にフェッチし、状態を管理する。
    -   **`src/gh_pr_phase_monitor/monitor/pages_watcher.py`**: GitHub Pagesのデプロイ状態を監視する機能。
    -   **`src/gh_pr_phase_monitor/monitor/pr_processor.py`**: 取得したPR情報を処理し、フェーズ判定やそれに基づくアクションの実行を調整する。
    -   **`src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py`**: 監視状態のスナップショットを保存するためのパスユーティリティ。
    -   **`src/gh_pr_phase_monitor/monitor/state_tracker.py`**: 監視対象のPRやリポジトリの現在の状態を追跡し、変更を検出する。
    -   **`src/gh_pr_phase_monitor/phase/html/html_status_processor.py`**: PRのHTMLからLLMのステータスやコメントを処理する。
    -   **`src/gh_pr_phase_monitor/phase/html/llm_status_extractor.py`**: PRのHTMLからLLM（例: Copilot）の作業ステータスを抽出する。
    -   **`src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py`**: PRのHTMLコンテンツを解析し、特定の情報（レビューコメントなど）を抽出する。
    -   **`src/gh_pr_phase_monitor/phase/html/pr_html_fetcher.py`**: GitHubからPRのHTMLコンテンツをフェッチする。
    -   **`src/gh_pr_phase_monitor/phase/html/pr_html_saver.py`**: 取得したPRのHTMLコンテンツをファイルに保存する。
    -   **`src/gh_pr_phase_monitor/phase/phase_detector.py`**: GitHub PRの現在の状態に基づき、ツールが定義する「フェーズ」（Draft、レビュー対応中、レビュー待ち、LLM作業中）を判定するロジック。
    -   **`src/gh_pr_phase_monitor/ui/display.py`**: 監視結果やステータス情報をコンソールに表示する整形された出力機能。
    -   **`src/gh_pr_phase_monitor/ui/notification_window.py`**: ブラウザ自動操作中に表示される小さな通知ウィンドウを管理。
    -   **`src/gh_pr_phase_monitor/ui/notifier.py`**: ntfy.shなどのサービスを利用してモバイル通知を送信する機能。
    -   **`src/gh_pr_phase_monitor/ui/wait_handler.py`**: 特定のイベントが発生するまで待機する機能（例: APIレート制限のリセット）。
-   **`tests/`**: プロジェクトのユニットテストおよび統合テストが格納されるディレクトリ。各`test_*.py`ファイルは、特定の機能やモジュールのテストを担当します。

## 関数詳細説明
提供されたプロジェクト情報から具体的な関数シグネチャは抽出できないため、主要な機能とそれを担うであろう関数について、その役割と入出力を推測して説明します。

-   **`main.py` 内の `run_monitor()`**:
    -   **役割**: 監視ツールのメイン実行ループを起動し、設定された間隔でPR監視とアクション実行を繰り返します。
    -   **引数**: `config_path` (str, オプション): 設定ファイルへのパス。
    -   **戻り値**: なし。ツールが停止するまでループし続けます。
    -   **機能**: 設定の読み込み、リポジトリの検出、PR情報のフェッチ、フェーズ判定、アクションの実行、省電力モードへの移行、自己更新のトリガーなどを調整します。

-   **`config.py` 内の `load_config()`**:
    -   **役割**: `config.toml`ファイルから設定を読み込み、パースして、プログラム内で利用可能なオブジェクトとして提供します。
    -   **引数**: `config_path` (str): 設定ファイルへのパス。
    -   **戻り値**: `dict`または`Config`オブジェクト: 読み込まれた設定データ。
    -   **機能**: TOML形式の解析、デフォルト値の適用、設定のバリデーション、ルールセットの解決などを行います。

-   **`github_client.py` 内の `fetch_pull_requests()`**:
    -   **役割**: GitHub GraphQL APIを使用して、認証済みユーザーが所有するリポジトリからオープンなPull Requestの情報を取得します。
    -   **引数**: `github_session` (GraphQLClientインスタンス): 認証済みのGitHub GraphQLクライアントセッション。
    -   **戻り値**: `list` of `PullRequest`オブジェクト: 取得されたPRのリスト。
    -   **機能**: GraphQLクエリの構築、APIリクエストの送信、レート制限の処理、PRデータのパース、関連するコメントやレビュー情報の取得を含みます。

-   **`phase_detector.py` 内の `detect_phase()`**:
    -   **役割**: 特定のPull Requestの現在の状態を分析し、それがどのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）にあるかを判定します。
    -   **引数**: `pull_request` (PullRequestオブジェクト): 判定対象のPRデータ。`comments` (list), `reviews` (list), `draft` (bool) などの情報を含む。
    -   **戻り値**: `str`: 判定されたフェーズ名（例: "phase1", "phase2", "phase3", "LLM working"）。
    -   **機能**: PRのDraft状態の確認、特定のBotからのコメントの有無、レビューコメントの未解決スレッドの有無などを基にロジックを適用します。

-   **`pr_actions.py` 内の `execute_pr_action()`**:
    -   **役割**: フェーズ判定結果に基づき、PRに対してコメント投稿、Draft PRのReady化、通知送信、自動マージなどの具体的なアクションを実行します。
    -   **引数**: `pull_request` (PullRequestオブジェクト): アクション対象のPR。`current_phase` (str): 現在のフェーズ。`config` (Configオブジェクト): アクション実行に必要な設定。`is_dry_run` (bool): ドライランモードかどうか。
    -   **戻り値**: `bool`: アクションが実行されたかどうか。
    -   **機能**: 設定されたルールセットに従って、対象のPRに対して適切なGitHub APIコールや外部サービス連携（ntfy.sh、ブラウザ自動化）をトリガーします。

-   **`browser_automation.py` 内の `click_button_with_screenshot()`**:
    -   **役割**: 指定されたスクリーンショット画像に一致するUI要素を画面上で探し、その位置をクリックします。必要に応じてOCRによるテキスト認識も利用します。
    -   **引数**: `button_image_path` (str): クリック対象のボタン画像のパス。`button_text` (str, オプション): OCRで認識するボタンテキスト。`confidence` (float): 画像認識の信頼度。`debug_dir` (str): デバッグ情報の保存先。
    -   **戻り値**: `bool`: ボタンのクリックが成功したかどうか。
    -   **機能**: PyAutoGUIを利用した画像認識、画面座標の取得、クリック操作、OCRフォールバック、デバッグ情報の保存を行います。

## 関数呼び出し階層ツリー
```
run_monitor (main.py)
├── load_config (config.py)
├── auto_update_and_restart (auto_updater.py)
├── setup_signal_handlers (process_utils.py)
├── monitor.run_loop (monitor.py)
│   ├── repository_fetcher.fetch_user_repositories (repository_fetcher.py)
│   │   └── graphql_client.query (graphql_client.py)
│   ├── pr_fetcher.fetch_open_pull_requests (pr_fetcher.py)
│   │   └── graphql_client.query (graphql_client.py)
│   ├── pr_processor.process_pull_requests (pr_processor.py)
│   │   ├── phase_detector.detect_phase (phase_detector.py)
│   │   │   ├── comment_fetcher.fetch_pr_comments (comment_fetcher.py)
│   │   │   └── pr_html_analyzer.analyze_pr_html (pr_html_analyzer.py)
│   │   │       └── pr_html_fetcher.fetch_pr_html (pr_html_fetcher.py)
│   │   ├── pr_actions.execute_pr_action (pr_actions.py)
│   │   │   ├── comment_manager.post_comment (comment_manager.py)
│   │   │   ├── notifier.send_notification (notifier.py)
│   │   │   ├── browser_automation.open_browser_and_click (browser_automation.py)
│   │   │   │   └── button_clicker.click_button_with_screenshot (button_clicker.py)
│   │   │   │       └── window_manager.activate_window (window_manager.py)
│   │   │   └── pr_actions.set_pr_ready_for_review (pr_actions.py)
│   │   ├── issue_fetcher.fetch_issues (issue_fetcher.py)
│   │   │   └── graphql_client.query (graphql_client.py)
│   │   └── display.display_status (display.py)
│   └── local_repo_watcher.watch_local_repos (local_repo_watcher.py)
│       └── process_utils.run_git_command (process_utils.py)
└── error_logger.log_exception (error_logger.py)

---
Generated at: 2026-03-11 07:03:14 JST
