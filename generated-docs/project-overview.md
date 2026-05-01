Last updated: 2026-05-02

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト（PR）を効率的に監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIを用いてPRのフェーズを自動判定します。
- PRの状態に応じて、通知送信、コメント投稿、PR Ready化、自動マージ、Issue割り当てなどのアクションを実行します。

## 技術スタック
- フロントエンド: ターミナル出力のANSIカラーコード制御 (`src/gh_pr_phase_monitor/core/colors.py`)
- 音楽・オーディオ: 該当なし
- 開発ツール:
    - GitHub CLI (`gh`): GitHub API認証と基本的な操作に利用。
    - `ruff`: コードフォーマッターおよびリンターとして、コード品質と一貫性を維持。
- テスト:
    - `pytest`: Pythonコードの単体テストおよび結合テストフレームワーク。
- ビルドツール:
    - `cargo install`: ローカルのRustリポジトリのバイナリを自動更新する際に利用。
- 言語機能:
    - Python 3.11+: プロジェクトの主要な実装言語。
    - `TOML`: 設定ファイル (`config.toml`) のフォーマットとして利用。
- 自動化・CI/CD:
    - `ntfy.sh`: モバイル端末へのプッシュ通知サービス。
    - GitHub Actions: READMEドキュメントの自動翻訳などに利用。
    - `PyAutoGUI`: ブラウザ上のUI操作を自動化するためのライブラリ（画像認識、マウス・キーボード操作）。
    - `Pillow`: `PyAutoGUI`で画像処理を行うための画像ライブラリ。
    - `pygetwindow`: ウィンドウを操作し、ブラウザをアクティブ化するためのライブラリ。
    - `tesseract-ocr`: ブラウザ自動化で画像認識が失敗した場合のOCRフォールバック（ボタンテキスト検出）に利用。
- 開発標準:
    - `.editorconfig`: 異なるエディタ間でのコーディングスタイルの一貫性を維持。
    - `ruff.toml`: `ruff`の設定ファイルで、コードの品質とスタイルを強制。

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
    ├── test_main_auto_update.py
    ├── test_main_periodic_status_display.py
    ├── test_max_llm_working_parallel.py
    ├── test_no_change_timeout.py
    ├── test_no_open_prs_issue_cache.py
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
- **`.editorconfig`**: さまざまなエディタやIDE間で一貫したコーディングスタイルを定義する設定ファイル。
- **`.gitignore`**: Gitが追跡しないファイルやディレクトリを指定するリスト。
- **`.vscode/settings.json`**: Visual Studio Code用のワークスペース固有の設定ファイル。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）。
- **`README.ja.md`**: プロジェクトの日本語版説明ドキュメント。
- **`README.md`**: プロジェクトの英語版説明ドキュメント。
- **`_config.yml`**: GitHub Pagesなどのサイト設定ファイル。
- **`cat-github-watcher.py`**: プロジェクトの主要なエントリスクリプト。プログラムの実行を開始します。
- **`config.toml.example`**: 設定ファイル`config.toml`のサンプル。ユーザーがコピーしてカスタマイズするためのテンプレートです。
- **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーション用スクリプト。
- **`docs/`**: プロジェクトに関する追加ドキュメントが格納されているディレクトリ。
    - **`RULESETS.md`**: ルールセットの設定方法に関する詳細ドキュメント。
    - **`button-detection-improvements.ja.md`**: ボタン検出改善に関する日本語ドキュメント。
    - **`window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメント。
- **`fetch_pr_html.py`**: プルリクエストのHTMLコンテンツを取得するための補助スクリプト。
- **`generated-docs/`**: 自動生成されたドキュメントを格納するディレクトリ。
- **`pyproject.toml`**: Pythonプロジェクトのメタデータやビルドシステムに関する設定ファイル。
- **`pytest.ini`**: `pytest`テストランナーの設定ファイル。
- **`requirements-automation.txt`**: ブラウザ自動化機能に必要なPythonライブラリのリスト。
- **`ruff.toml`**: `ruff`リンターおよびフォーマッターの設定ファイル。
- **`screenshots/`**: ブラウザ自動化（PyAutoGUI）で使用するボタン画像のスクリーンショットを保存するディレクトリ。
    - **`assign.png`**: 「Assign」ボタンのスクリーンショット画像。
    - **`assign_to_copilot.png`**: 「Assign to Copilot」ボタンのスクリーンショット画像。
- **`src/`**: プロジェクトの主要なソースコードが格納されているディレクトリ。
    - **`gh_pr_phase_monitor/main.py`**: メインの監視ループとロジックをオーケストレーションする中心ファイル。
    - **`gh_pr_phase_monitor/actions/pr_actions.py`**: プルリクエストに対する各種アクション（Ready化、コメント投稿、マージなど）を定義および実行。
    - **`gh_pr_phase_monitor/browser/browser_automation.py`**: PyAutoGUIを利用したブラウザ操作の基盤機能。
    - **`gh_pr_phase_monitor/browser/button_clicker.py`**: 特定のボタン（画像認識）をクリックするロジック。
    - **`gh_pr_phase_monitor/browser/issue_assigner.py`**: IssueをGitHub Copilotに自動割り当てるためのブラウザ操作ロジック。
    - **`gh_pr_phase_monitor/browser/window_manager.py`**: ウィンドウの管理、アクティブ化、最大化などを行う機能。
    - **`gh_pr_phase_monitor/core/colors.py`**: ターミナル出力用のANSIカラーコードを定義し、テキストに色付けする機能。
    - **`gh_pr_phase_monitor/core/config.py`**: `config.toml`ファイルから設定を読み込み、解析し、提供する機能。
    - **`gh_pr_phase_monitor/core/config_ruleset.py`**: 設定のルールセットを管理・適用する機能。
    - **`gh_pr_phase_monitor/github/github_client.py`**: GitHub GraphQL APIと通信するための高レベルなクライアント。
    - **`gh_pr_phase_monitor/github/graphql_client.py`**: GraphQLクエリの低レベルな実行、レート制限処理、ETagキャッシュ管理。
    - **`gh_pr_phase_monitor/github/pr_fetcher.py`**: プルリクエストの情報をGitHub APIから取得する機能。
    - **`gh_pr_phase_monitor/github/issue_fetcher.py`**: Issueの情報をGitHub APIから取得する機能。
    - **`gh_pr_phase_monitor/github/comment_manager.py`**: PRへのコメント投稿や既存コメントの確認を行う機能。
    - **`gh_pr_phase_monitor/monitor/auto_updater.py`**: プロジェクト自身（リポジトリ）の更新をチェックし、必要に応じて自動で`git pull`と再起動を実行する機能。
    - **`gh_pr_phase_monitor/monitor/local_repo_watcher.py`**: ローカルリポジトリのpull可能状態を監視し、自動で`git pull`を実行する機能。
    - **`gh_pr_phase_monitor/phase/phase_detector.py`**: プルリクエストが現在どのフェーズ（Draft、レビュー指摘対応中など）にあるかを判定するロジック。
    - **`gh_pr_phase_monitor/phase/html/pr_html_analyzer.py`**: PRのHTMLコンテンツを解析し、LLMエージェントの作業状況などを抽出する機能。
    - **`gh_pr_phase_monitor/ui/display.py`**: ターミナルに監視ステータスやPR情報を整形して表示する機能。
    - **`gh_pr_phase_monitor/ui/notifier.py`**: ntfy.shサービスを通じてモバイル通知を送信する機能。
- **`tests/`**: プロジェクトの各種機能に対するテストスクリプトが格納されているディレクトリ。

## 関数詳細説明
本プロジェクトはモジュール化されており、各モジュールが特定の役割を持つ関数群を提供します。主要な関数をその役割に基づいて説明します。

-   **`main`モジュール (例: `src/gh_pr_phase_monitor/main.py`)**
    -   `run_monitor(config_path: Optional[str] = None) -> None`: プログラムのエントリーポイントとして機能し、設定を読み込み、メインの監視ループを開始します。
-   **`config`モジュール (例: `src/gh_pr_phase_monitor/core/config.py`)**
    -   `load_and_validate_config(config_file_path: str) -> dict`: 指定されたパスから設定ファイルを読み込み、その内容を検証して設定辞書を返します。
-   **`github_client`モジュール (例: `src/gh_pr_phase_monitor/github/github_client.py`)**
    -   `fetch_all_repositories() -> List[dict]`: 認証済みユーザーが所有するすべてのリポジトリ情報をGitHub GraphQL APIから取得します。
    -   `fetch_prs_for_repository(repo_name: str, etag: Optional[str] = None) -> Tuple[List[dict], str, bool]`: 特定のリポジトリのオープンなプルリクエスト情報を取得します。ETagを利用してAPIクォータの消費を抑えます。
    -   `mark_pr_as_ready_for_review(pr_node_id: str) -> bool`: 指定されたPRをドラフト状態からレビュー可能な状態にマークします。
-   **`graphql_client`モジュール (例: `src/gh_pr_phase_monitor/github/graphql_client.py`)**
    -   `execute_query(query: str, variables: Optional[dict] = None, etag: Optional[str] = None) -> Tuple[dict, Optional[str], int]`: GitHub GraphQL APIにクエリを実行し、結果、新しいETag、およびHTTPステータスコードを返します。
-   **`phase_detector`モジュール (例: `src/gh_pr_phase_monitor/phase/phase_detector.py`)**
    -   `detect_pr_phase(pr_data: dict, repo_config: dict) -> str`: プルリクエストのデータとリポジトリ設定に基づき、そのPRの現在のフェーズ（例: phase1, phase2, phase3, LLM working）を判定します。
-   **`pr_actions`モジュール (例: `src/gh_pr_phase_monitor/actions/pr_actions.py`)**
    -   `perform_phase_action(pr_data: dict, phase: str, config: dict, ruleset: dict, dry_run: bool) -> None`: 特定のPRが特定のフェーズにある場合に、設定されたアクション（コメント投稿、通知、Ready化、マージなど）を実行します。
-   **`comment_manager`モジュール (例: `src/gh_pr_phase_monitor/github/comment_manager.py`)**
    -   `post_comment_to_pr(pr_node_id: str, comment_body: str) -> bool`: 指定されたPRにコメントを投稿します。
    -   `has_specific_comment(pr_data: dict, comment_text: str) -> bool`: PRに特定のテキストを含むコメントが投稿されているかを確認します。
-   **`browser_automation`モジュール (例: `src/gh_pr_phase_monitor/browser/browser_automation.py`)**
    -   `open_browser_and_click(url: str, button_screenshots: List[str], config: dict) -> bool`: 指定されたURLをブラウザで開き、設定されたスクリーンショットに基づいてボタンをクリックしようとします。
-   **`issue_assigner`モジュール (例: `src/gh_pr_phase_monitor/browser/issue_assigner.py`)**
    -   `assign_issue_to_copilot(issue_url: str, config: dict) -> bool`: 指定されたIssueのURLを開き、ブラウザ自動操作でIssueをCopilotに割り当てます。
-   **`notifier`モジュール (例: `src/gh_pr_phase_monitor/ui/notifier.py`)**
    -   `send_ntfy_notification(topic: str, message: str, url: str, priority: int) -> None`: `ntfy.sh`サービスを通じて、指定されたトピックに通知を送信します。
-   **`auto_updater`モジュール (例: `src/gh_pr_phase_monitor/monitor/auto_updater.py`)**
    -   `check_for_updates(current_dir: str, enable_auto_update: bool, debug_log: bool) -> None`: プロジェクトのGitリポジトリに更新があるかを確認し、設定に応じて自動で`git pull`を実行して再起動します。
-   **`local_repo_watcher`モジュール (例: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`)**
    -   `watch_local_repositories(base_dir: str, auto_pull: bool, cargo_repos: List[str]) -> None`: 指定されたベースディレクトリ以下のローカルリポジトリを監視し、`git pull`が必要な場合は表示または自動実行します。また、`cargo install`リポジトリのバイナリ更新も行います。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした

---
Generated at: 2026-05-02 07:14:02 JST
