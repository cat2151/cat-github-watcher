Last updated: 2026-03-10

# Project Overview

## プロジェクト概要
- GitHub CopilotなどAIエージェントによる自動実装中のプルリクエスト(PR)のフェーズを監視するPythonツールです。
- PRの状態（ドラフト、レビュー対応中、レビュー待ち、LLM作業中）を自動判定し、適切なタイミングで通知やアクションを実行します。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIやブラウザ自動操作を活用し、開発プロセスを効率化します。

## 技術スタック
- フロントエンド: PyAutoGUI (GUI自動操作、ボタンクリック、画像認識), Pillow (画像処理), PyGetWindow (ウィンドウ管理), Notification Window (カスタム通知表示)
- 音楽・オーディオ: なし
- 開発ツール: GitHub CLI (`gh`, GitHub認証と操作), pytest (テストフレームワーク), ruff (Pythonリンター/フォーマッター), .editorconfig (コードスタイル定義)
- テスト: pytest (Pythonコードの単体・統合テスト)
- ビルドツール: Pythonの標準的なパッケージング/依存関係管理（`pyproject.toml`で指定、`pip`によるインストール）
- 言語機能: Python 3.11 以上 (非同期処理、型ヒントなど最新のPython機能)
- 自動化・CI/CD: git (リポジトリ操作、自動更新・プル), ntfy.sh (モバイル通知サービス), GitHub Actions (README翻訳などで利用実績あり、PR監視には不採用)
- 開発標準: .editorconfig (エディタ設定), ruff (コードフォーマット・静的解析)
- その他: GitHub GraphQL API (効率的なデータ取得), pytesseract (OCRによるテキスト検出、PyAutoGUIのフォールバック)

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

上記の簡易ツリーは、プロジェクト概要セクションで示された主要なモジュールに基づいています。提供された「ファイル階層ツリー」は詳細な情報を提供していますが、来訪者向けにプロジェクトの全体像を把握しやすくするため、主要なファイルとディレクトリのみを抜粋しました。完全な階層は下記「ファイル詳細説明」セクションをご参照ください。

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

*   **`.editorconfig`**: 異なるエディタやIDE間でコードスタイル（インデント、改行コードなど）を統一するための設定ファイルです。
*   **`.gitignore`**: Gitがバージョン管理の対象から除外するファイルやディレクトリを指定します（例: 一時ファイル、ビルド成果物）。
*   **`.vscode/settings.json`**: Visual Studio Codeエディタのワークスペース固有の設定ファイルで、開発環境を最適化します。
*   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記載したファイルです。
*   **`README.ja.md`**: プロジェクトの目的、特徴、使い方などを日本語で説明する主要なドキュメントです。
*   **`README.md`**: プロジェクトの目的、特徴、使い方などを英語で説明する主要なドキュメントです。
*   **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレータで利用される設定ファイルです。
*   **`cat-github-watcher.py`**: プロジェクトのメインエントリーポイントとなるスクリプトで、ツールの起動を担当します。
*   **`config.toml.example`**: ユーザーが設定を行うための設定ファイルのサンプルです。監視間隔、通知設定、自動アクションなどが記述されています。
*   **`demo_automation.py`**: ブラウザ自動操作機能のデモンストレーションまたはテストに使用されるスクリプトです。
*   **`docs/`**: プロジェクトに関する追加ドキュメントが格納されているディレクトリです。
    *   **`RULESETS.md`**: 設定ファイルにおけるルールセットの利用方法に関するドキュメントです。
    *   **`button-detection-improvements.ja.md`**: ボタン検出機能の改善点に関する日本語ドキュメントです。
    *   **`window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメントです。
*   **`fetch_pr_html.py`**: 特定のPRのHTMLコンテンツを取得するためのユーティリティスクリプトです。
*   **`generated-docs/`**: 自動生成されたドキュメントが格納されるディレクトリです。
*   **`pyproject.toml`**: Pythonプロジェクトのメタデータ、依存関係、ビルドシステムなどを定義する標準的な設定ファイルです。
*   **`pytest.ini`**: Pythonのテストフレームワークであるpytestの設定ファイルです。
*   **`requirements-automation.txt`**: 自動化機能（PyAutoGUIなど）に必要なPythonライブラリのリストです。
*   **`ruff.toml`**: PythonのリンターおよびフォーマッターであるRuffの設定ファイルです。
*   **`screenshots/`**: ブラウザ自動操作における画像認識用のボタンのスクリーンショットが格納されるディレクトリです。
    *   **`assign.png`**: 「Assign」ボタンのスクリーンショット。
    *   **`assign_to_copilot.png`**: 「Assign to Copilot」ボタンのスクリーンショット。
*   **`src/`**: プロジェクトの主要なソースコードが格納されているディレクトリです。
    *   **`src/__init__.py`**: Pythonパッケージであることを示すファイルです。
    *   **`src/gh_pr_phase_monitor/`**: PRフェーズ監視ツールの中核となるモジュール群です。
        *   **`src/gh_pr_phase_monitor/__init__.py`**: Pythonパッケージであることを示すファイルです。
        *   **`src/gh_pr_phase_monitor/actions/`**: PRに対するアクション関連のモジュールです。
            *   **`pr_actions.py`**: PRを「Ready for review」にする、マージするなどの具体的なアクションを定義します。
        *   **`src/gh_pr_phase_monitor/browser/`**: ブラウザ自動操作関連のモジュールです。
            *   **`browser_automation.py`**: PyAutoGUIなどを用いてブラウザの操作を自動化するロジックを含みます。
            *   **`browser_cooldown.py`**: ブラウザ操作間のクールダウン（待機時間）を管理します。
            *   **`button_clicker.py`**: 画像認識やOCRを用いて画面上のボタンをクリックする機能を提供します。
            *   **`click_config_validator.py`**: クリック設定の検証を行います。
            *   **`window_manager.py`**: ブラウザウィンドウの管理（アクティブ化、サイズ変更など）を行います。
        *   **`src/gh_pr_phase_monitor/core/`**: プロジェクトのコアユーティリティや共通機能を提供します。
            *   **`colors.py`**: ターミナル出力の色付けに使用するANSIカラーコードやカラースキームを定義します。
            *   **`config.py`**: `config.toml`から設定を読み込み、解析し、アプリケーション全体で利用可能にする機能を提供します。
            *   **`config_printer.py`**: 現在の設定情報を表示する機能を提供します（Verboseモードなどで使用）。
            *   **`interval_parser.py`**: 設定ファイルで指定された時間間隔（例: "30s", "1m"）をパースするユーティリティです。
            *   **`process_utils.py`**: プロセス関連のユーティリティ関数を提供します。
            *   **`time_utils.py`**: 時間計算やフォーマットに関するユーティリティ関数を提供します。
        *   **`src/gh_pr_phase_monitor/github/`**: GitHub APIとの連携を担当するモジュール群です。
            *   **`comment_fetcher.py`**: GitHub PRのコメントを取得します。
            *   **`comment_manager.py`**: PRへのコメント投稿や既存コメントの確認を行います。
            *   **`github_auth.py`**: GitHub APIの認証処理を担当します。
            *   **`github_client.py`**: GitHub APIとの主要なインターフェースを提供します。
            *   **`graphql_client.py`**: GitHub GraphQL APIクライアントとして機能し、クエリの実行を担当します。
            *   **`issue_fetcher.py`**: GitHubのIssue情報を取得します。
            *   **`pr_fetcher.py`**: GitHubのプルリクエスト情報を取得します。
            *   **`rate_limit_handler.py`**: GitHub APIのレート制限を監視し、適切に処理します。
            *   **`repository_fetcher.py`**: GitHubのリポジトリ情報を取得します。
        *   **`src/gh_pr_phase_monitor/main.py`**: プログラムのメイン実行ループと、監視プロセスを制御するロジックを含みます。
        *   **`src/gh_pr_phase_monitor/monitor/`**: 監視機能の中核となるモジュール群です。
            *   **`auto_updater.py`**: プロジェクト自身の自動更新（git pull）機能を提供します。
            *   **`error_logger.py`**: 実行中に発生したエラーをログに記録します。
            *   **`iteration_runner.py`**: 監視ループの各イテレーションを実行します。
            *   **`local_repo_watcher.py`**: ローカルリポジトリの変更（pull可能状態）を監視します。
            *   **`monitor.py`**: 全体的な監視ロジックと状態管理を統括します。
            *   **`pages_watcher.py`**: GitHub Pagesのデプロイ状況などを監視する機能を提供する可能性があります。
            *   **`pr_processor.py`**: 取得した各PRを処理し、フェーズ判定や必要なアクションの実行を調整します。
            *   **`snapshot_path_utils.py`**: 状態のスナップショットパスを管理するユーティリティです。
            *   **`state_tracker.py`**: PRの現在の状態や過去の状態を追跡し、変化を検知します。
        *   **`src/gh_pr_phase_monitor/phase/`**: PRのフェーズ判定に関連するモジュール群です。
            *   **`src/gh_pr_phase_monitor/phase/html/`**: PRのHTMLコンテンツを解析し、LLMエージェントのステータスなどを抽出します。
                *   **`html_status_processor.py`**: HTMLからPRのステータス情報を処理します。
                *   **`llm_status_extractor.py`**: PRのHTMLからLLM（例: Copilot）の作業状況を示す情報を抽出します。
                *   **`pr_html_analyzer.py`**: PRのHTMLコンテンツを詳細に分析します。
                *   **`pr_html_fetcher.py`**: PRページのHTMLコンテンツを取得します。
                *   **`pr_html_saver.py`**: 取得したPRのHTMLコンテンツを保存します。
            *   **`phase_detector.py`**: PRのコメントやステータスに基づいて、フェーズ（phase1, phase2, phase3, LLM working）を判定する主要なロジックを含みます。
        *   **`src/gh_pr_phase_monitor/ui/`**: ユーザーインターフェース関連のモジュールです。
            *   **`display.py`**: ターミナルへの情報表示（PRの状態、ログなど）を整形して行います。
            *   **`notification_window.py`**: 画面上に小さな通知ウィンドウを表示する機能を提供します。
            *   **`notifier.py`**: ntfy.shなどのサービスを通じて通知を送信します。
            *   **`wait_handler.py`**: 特定の条件が満たされるまで待機する処理を管理します。
*   **`tests/`**: プロジェクトのテストコードが格納されているディレクトリです。各`test_*.py`ファイルが特定の機能やモジュールのテストを担当します。

## 関数詳細説明

提供されたプロジェクト情報には具体的な関数名やシグネチャが含まれていませんが、ファイル構造とREADMEの機能説明から、以下のような役割を持つ関数が存在すると推測されます。

*   **`main` (src/gh_pr_phase_monitor/main.py)**:
    *   **役割**: アプリケーションのメインエントリポイントとして、設定の読み込み、初期化、そして監視ループの開始と制御を行います。
    *   **機能**: `config.toml`から設定をロードし、GitHubクライアントやその他のモジュールを初期化し、定期的なPR監視サイクルを開始します。自動更新や省電力モードへの移行なども管理します。

*   **`load_config` (src/gh_pr_phase_monitor/core/config.py)**:
    *   **役割**: 設定ファイル（`config.toml`）を読み込み、パースし、アプリケーションが利用できる設定オブジェクトを生成します。
    *   **機能**: TOML形式の設定ファイルを解析し、デフォルト値の適用、型変換、設定の検証などを行います。

*   **`fetch_repositories` (src/gh_pr_phase_monitor/github/repository_fetcher.py)**:
    *   **役割**: 認証済みGitHubユーザーが所有する全てのリポジトリ情報を取得します。
    *   **機能**: GitHub GraphQL APIを通じて、ユーザーのリポジトリリストを効率的に取得し、その中からPR監視の対象となるリポジトリを選別します。

*   **`fetch_pull_requests` (src/gh_pr_phase_monitor/github/pr_fetcher.py)**:
    *   **役割**: 特定のリポジトリまたは全監視対象リポジトリのオープンなプルリクエスト情報を取得します。
    *   **機能**: GraphQLクエリを構築し、各PRのタイトル、ステータス、コメント、レビュー状況などの詳細情報を取得します。

*   **`detect_phase` (src/gh_pr_phase_monitor/phase/phase_detector.py)**:
    *   **役割**: 取得したプルリクエストの情報を分析し、現在のフェーズ（Draft状態、レビュー指摘対応中、レビュー待ち、LLM作業中）を判定します。
    *   **機能**: PRのステータス、ラベル、レビューコメント、特定のキーワード（例: "copilot-pull-request-reviewer"）などを総合的に評価してフェーズを特定します。

*   **`post_comment` (src/gh_pr_phase_monitor/github/comment_manager.py)**:
    *   **役割**: 特定のプルリクエストに対してコメントを投稿します。
    *   **機能**: フェーズ判定結果に基づき、コーディングエージェントへのメンションを含む適切なコメントをPRに書き込みます。

*   **`mark_pr_ready_for_review` (src/gh_pr_phase_monitor/actions/pr_actions.py)**:
    *   **役割**: Draft状態のプルリクエストを「Ready for review」状態に変更します。
    *   **機能**: GitHub APIを呼び出してPRのステータスを更新します。

*   **`send_ntfy_notification` (src/gh_pr_phase_monitor/ui/notifier.py)**:
    *   **役割**: `ntfy.sh`サービスを通じてモバイル通知を送信します。
    *   **機能**: 特定のPRがレビュー待ちフェーズに達した場合などに、設定されたトピックとメッセージで通知をプッシュします。

*   **`merge_pull_request` (src/gh_pr_phase_monitor/actions/pr_actions.py)**:
    *   **役割**: レビュー待ちフェーズのプルリクエストを自動的にマージします。
    *   **機能**: GitHub APIまたはブラウザ自動操作を用いてPRのマージを実行し、成功後にブランチを削除するオプションも提供します。

*   **`assign_issue_to_copilot` (src/gh_pr_phase_monitor/browser/browser_automation.py, test_assign_issue_to_copilot.py などから推測)**:
    *   **役割**: 特定の条件（例: `good first issue`）を満たすIssueをCopilotに自動的に割り当てます。
    *   **機能**: PyAutoGUIやOCRを用いてブラウザ上で「Assign to Copilot」ボタンを検出し、クリックすることで割り当てを行います。

*   **`check_for_updates_and_restart` (src/gh_pr_phase_monitor/monitor/auto_updater.py)**:
    *   **役割**: プロジェクトの最新バージョンをチェックし、利用可能な場合は自動的に更新して再起動します。
    *   **機能**: `git pull`コマンドを実行し、変更があればPythonプロセスを再起動します。

*   **`monitor_local_repositories` (src/gh_pr_phase_monitor/monitor/local_repo_watcher.py)**:
    *   **役割**: ローカル環境にあるリポジトリのpull可能状態を監視し、必要に応じて自動で`git pull`を実行します。
    *   **機能**: 指定されたディレクトリ内のローカルリポジトリに対して`git fetch`を実行し、リモートとの差分を検知します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした

---
Generated at: 2026-03-10 07:04:03 JST
