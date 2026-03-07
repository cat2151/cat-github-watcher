Last updated: 2026-03-08

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動生成したPull Requestのフェーズを効率的に監視するPythonツールです。
- 各フェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）に応じて、自動コメント投稿、PRのReady化、自動マージ、モバイル通知などのアクションを実行します。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIと必要に応じてブラウザ自動操作を用いて開発ワークフローを支援します。

## 技術スタック
- フロントエンド:
    - **PyAutoGUI**: スクリーンショットによる画像認識、カーソル移動、クリック、キー入力など、GUIをプログラムで自動化するためのPythonライブラリ。ブラウザでのボタン操作などに利用されます。
    - **Pillow**: Python Imaging Library (PIL) のフォークであり、画像処理機能を提供します。PyAutoGUIの依存ライブラリとして画像認識処理に利用されます。
    - **PyGetWindow**: ウィンドウを操作（移動、サイズ変更、アクティブ化など）するためのライブラリで、ブラウザ自動操作時のウィンドウ管理に利用されます。
    - **Pytesseract**: GoogleのOCRエンジンTesseractのPythonラッパー。画像認識が失敗した場合のフォールバックとして、画面上のテキスト検出に利用されます。
    - **Tesseract-OCR**: Pytesseractが利用するオープンソースのOCRエンジン。システムレベルでのインストールが必要です。
- 音楽・オーディオ: 該当なし
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHubの認証とAPIアクセスをコマンドラインから行うためのツール。本プロジェクトの前提条件としてユーザー認証に利用されます。
- テスト:
    - **pytest**: Python用の強力なテストフレームワーク。テストスイートの実行に利用されます。
- ビルドツール: 該当なし（Pythonの標準的な実行環境とpipによる依存管理）
- 言語機能:
    - **Python 3.11以上**: プロジェクトの主要な開発言語および実行環境。
    - **GraphQL API**: GitHub APIとの効率的なデータ交換プロトコル。PR情報の取得などに利用されます。
    - **TOML**: 設定ファイル（`config.toml`）の記述形式として使用されます。
- 自動化・CI/CD:
    - **ntfy.sh**: モバイル端末へのプッシュ通知サービス。PRのフェーズ変更などをリアルタイムで通知するために利用されます。
    - **GitHub Actions**: プロジェクトのREADME.md自動生成に使用されています。（プロジェクト本体のCI/CDではなく、ドキュメント生成に利用）
- 開発標準:
    - **Ruff**: 高速なPythonリンターおよびフォーマッター。コード品質の維持とスタイルの統一に利用されます。
    - **.editorconfig**: 異なるエディタやIDE間でコードスタイルを統一するための設定ファイル。

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

※ 提供されたツリーは一部のみだったため、より詳細な情報から補完した構造を以下に示します。
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
    ├── test_pr_html_analyzer.py
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

*   **`.editorconfig`**: 異なるエディタやIDE間で一貫したコーディングスタイル（インデント、改行コードなど）を維持するための設定ファイル。
*   **`.gitignore`**: Gitが追跡しないファイルやディレクトリ（ビルド生成物、ログ、環境固有の設定など）を指定するファイル。
*   **`.vscode/settings.json`**: Visual Studio Codeエディタのワークスペース固有の設定ファイル。リンターやフォーマッターの動作などを定義します。
*   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記載したファイル。
*   **`README.ja.md`**: プロジェクトの概要、機能、使い方などを日本語で説明するメインドキュメント。
*   **`README.md`**: プロジェクトの概要、機能、使い方などを英語で説明するドキュメント。GitHub Actionsにより`README.ja.md`から自動生成されます。
*   **`_config.yml`**: おそらくGitHub Pagesなどの静的サイトジェネレータで使用される設定ファイル。
*   **`cat-github-watcher.py`**: プロジェクトのエントリーポイントとなるスクリプト。`src/gh_pr_phase_monitor/main.py`のラッパーとして機能する可能性があります。
*   **`config.toml.example`**: 設定ファイル`config.toml`のテンプレート。ユーザーがコピーして環境に合わせて設定をカスタマイズするための例を提供します。
*   **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーションやテストに使用されるスクリプト。
*   **`docs/RULESETS.md`**: `config.toml`で定義される`rulesets`機能に関する詳細な説明ドキュメント。
*   **`docs/button-detection-improvements.ja.md`**: ボタン検出機能の改善点や仕組みについて日本語で説明するドキュメント。
*   **`docs/window-activation-feature.md`**: ウィンドウアクティベーション機能に関する説明ドキュメント。
*   **`fetch_pr_html.py`**: PRのHTMLコンテンツをフェッチ（取得）するための補助スクリプト。デバッグや特定の状況でのHTML解析に利用されます。
*   **`generated-docs/`**: 自動生成されたドキュメントが格納されるディレクトリ。
*   **`pyproject.toml`**: Pythonプロジェクトの設定ファイル。ビルドシステム、依存関係、ツール設定（Ruffなど）を定義します。
*   **`pytest.ini`**: pytestのテスト設定ファイル。テストの実行オプションなどを指定します。
*   **`requirements-automation.txt`**: 自動化機能（PyAutoGUIなど）に必要なPythonライブラリのリスト。
*   **`ruff.toml`**: Ruffリンター/フォーマッターの設定ファイル。コーディング規約やチェックルールを定義します。
*   **`screenshots/`**: ブラウザ自動操作で使用するボタンの画像認識用スクリーンショットが保存されるディレクトリ。
    *   `assign.png`: "Assign" ボタンのスクリーンショット。
    *   `assign_to_copilot.png`: "Assign to Copilot" ボタンのスクリーンショット。
*   **`src/gh_pr_phase_monitor/actions/pr_actions.py`**: PRに関連する具体的なアクション（Draft PRのReady化、コメント投稿、マージなど）を実行するロジックを実装します。
*   **`src/gh_pr_phase_monitor/browser/browser_automation.py`**: ブラウザ自動操作の主要なロジックをカプセル化します。
*   **`src/gh_pr_phase_monitor/browser/browser_cooldown.py`**: ブラウザ操作間のクールダウン（待機時間）を管理し、過度な操作を防ぎます。
*   **`src/gh_pr_phase_monitor/browser/button_clicker.py`**: PyAutoGUIを使用して、指定されたボタンのスクリーンショットに基づいてブラウザ上のボタンをクリックするロジックを実装します。
*   **`src/gh_pr_phase_monitor/browser/click_config_validator.py`**: ブラウザクリック自動化のための設定（`config.toml`内）を検証する機能を提供します。
*   **`src/gh_pr_phase_monitor/browser/window_manager.py`**: ウィンドウの管理（アクティブ化、最大化など）を行うためのヘルパー関数を提供します。
*   **`src/gh_pr_phase_monitor/core/colors.py`**: ターミナル出力の色付けに使用するANSIカラーコードとカラースキームを定義します。
*   **`src/gh_pr_phase_monitor/core/config.py`**: `config.toml`ファイルを読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供する役割を担います。
*   **`src/gh_pr_phase_monitor/core/config_printer.py`**: `verbose`モードが有効な場合に、現在の設定情報をターミナルに整形して表示する機能を提供します。
*   **`src/gh_pr_phase_monitor/core/interval_parser.py`**: 設定ファイルで指定される時間間隔（例: "30s", "1m"）を内部処理用の秒数に変換するロジックを実装します。
*   **`src/gh_pr_phase_monitor/core/process_utils.py`**: プロセス関連のユーティリティ関数（例: プロセスが実行中かどうかの確認）を提供します。
*   **`src/gh_pr_phase_monitor/core/time_utils.py`**: 時間関連のユーティリティ関数（例: 経過時間の計算、タイムスタンプのフォーマット）を提供します。
*   **`src/gh_pr_phase_monitor/github/comment_fetcher.py`**: GitHub APIを使用してPRコメントを取得する機能を提供します。
*   **`src/gh_pr_phase_monitor/github/comment_manager.py`**: PRへのコメント投稿、既存コメントの確認などのコメント管理機能を提供します。
*   **`src/gh_pr_phase_monitor/github/github_auth.py`**: GitHub CLI (`gh`) を利用した認証処理を管理します。
*   **`src/gh_pr_phase_monitor/github/github_client.py`**: GitHub REST APIとの高レベルなインタラクションを提供し、他のモジュールがGitHubデータにアクセスするための統一されたインターフェースを提供します。
*   **`src/gh_pr_phase_monitor/github/graphql_client.py`**: GitHub GraphQL APIを介してデータをクエリするための低レベルクライアントを実装します。
*   **`src/gh_pr_phase_monitor/github/issue_fetcher.py`**: GitHubからIssue情報を取得する機能を提供します。
*   **`src/gh_pr_phase_monitor/github/pr_fetcher.py`**: GitHubからPull Request情報を取得する機能に特化しています。
*   **`src/gh_pr_phase_monitor/github/rate_limit_handler.py`**: GitHub APIのレート制限を監視し、制限に達した際に適切な処理（待機など）を行うロジックを実装します。
*   **`src/gh_pr_phase_monitor/github/repository_fetcher.py`**: ユーザーが所有するGitHubリポジトリのリストを取得する機能を提供します。
*   **`src/gh_pr_phase_monitor/main.py`**: プロジェクトのメイン実行ループを定義し、設定の初期化、監視プロセスの開始、各モジュール間の協調を管理します。
*   **`src/gh_pr_phase_monitor/monitor/auto_updater.py`**: プロジェクト自身の自動更新機能（git pullして再起動）を実装します。
*   **`src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`**: ローカルのファイルシステム上のリポジトリを監視し、リモートからの`git pull`が必要かどうかを検知する機能を提供します。
*   **`src/gh_pr_phase_monitor/monitor/monitor.py`**: PR監視の中核ロジックをカプセル化し、一定間隔でのPR情報のフェッチ、フェーズ判定、アクション実行を調整します。
*   **`src/gh_pr_phase_monitor/monitor/pages_watcher.py`**: GitHub Pagesに関連する変更やデプロイ状況を監視する機能を提供します。
*   **`src/gh_pr_phase_monitor/monitor/snapshot_markdown.py`**: スナップショットデータをMarkdown形式で生成する機能を提供します。
*   **`src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py`**: スナップショットファイルのパスを管理するユーティリティ関数を提供します。
*   **`src/gh_pr_phase_monitor/monitor/state_tracker.py`**: PRの過去の状態を追跡し、変化を検出するためのロジックを実装します。省電力モードのトリガーにも関与します。
*   **`src/gh_pr_phase_monitor/phase/html/html_status_processor.py`**: PRのHTMLコンテンツを処理し、ステータス情報を抽出する機能を提供します。
*   **`src/gh_pr_phase_monitor/phase/html/llm_status_extractor.py`**: PRのHTMLからLLM（Copilotなど）の作業状況に関する特定の情報を抽出する機能に特化しています。
*   **`src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py`**: PRのHTMLを解析し、フェーズ判定に必要な情報を特定するロジックを実装します。
*   **`src/gh_pr_phase_monitor/phase/html/pr_html_fetcher.py`**: PRのHTMLコンテンツをWebから取得する機能を提供します。
*   **`src/gh_pr_phase_monitor/phase/html/pr_html_saver.py`**: 取得したPRのHTMLコンテンツをローカルに保存する機能を提供します。デバッグや履歴管理に利用されます。
*   **`src/gh_pr_phase_monitor/phase/phase_detector.py`**: PRのコメント、ステータス、タイトルなどに基づいて、現在のフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を判定する中核ロジックを実装します。
*   **`src/gh_pr_phase_monitor/ui/display.py`**: ターミナルにPR情報やステータスを整形して表示するための関数群を提供します。
*   **`src/gh_pr_phase_monitor/ui/notification_window.py`**: 自動化操作中にユーザーへの小さな通知ウィンドウを表示する機能を提供します。
*   **`src/gh_pr_phase_monitor/ui/notifier.py`**: ntfy.shサービスを介してモバイル通知を送信する機能を提供します。
*   **`src/gh_pr_phase_monitor/ui/wait_handler.py`**: APIリクエスト間の待機や、UI操作時のクールダウンなど、各種待機処理を管理します。
*   **`tests/`**: pytestフレームワークを使用した単体テストおよび統合テストのスクリプト群が格納されるディレクトリ。各テストファイルは特定の機能の検証を行います。

## 関数詳細説明

*   **`run_monitor(config_path: str = None)` (src/gh_pr_phase_monitor/main.py 内)**
    *   **役割**: アプリケーションのメイン監視ループを開始します。設定の読み込み、自動更新のチェック、GitHubリポジトリのPR監視、フェーズ判定、およびそれに応じたアクションの実行を調整します。
    *   **引数**:
        *   `config_path`: (オプション) 使用する設定ファイルのパス。指定しない場合はデフォルトの`config.toml`が使用されます。
    *   **戻り値**: なし。アプリケーションは無限ループで実行されます。
    *   **機能**: 初期設定のロード、自動更新の実行、設定された間隔でのPR監視サイクル（PR情報のフェッチ、フェーズ判定、アクション実行）の継続的な実行。省電力モードへの移行管理も行います。

*   **`load_config(config_path: str)` (src/gh_pr_phase_monitor/core/config.py 内)**
    *   **役割**: 指定されたパスのTOML形式設定ファイルを読み込み、解析して設定オブジェクトを返します。デフォルト値の適用や設定のバリデーションも行います。
    *   **引数**:
        *   `config_path`: 読み込む設定ファイル（`config.toml`など）のパス。
    *   **戻り値**: 設定オブジェクト（辞書型またはカスタムクラスのインスタンス）。
    *   **機能**: TOMLファイルのパース、不足している設定に対するデフォルト値の適用、`rulesets`の解釈、`interval`などの時間設定の正規化。

*   **`fetch_all_user_repos_with_prs(github_client: GitHubClient)` (src/gh_pr_phase_monitor/github/repository_fetcher.py や pr_fetcher.py と連携)**
    *   **役割**: 認証済みのGitHubユーザーが所有するすべてのリポジトリから、オープンなPull Request（PR）情報を効率的に取得します。GraphQL APIを利用して必要なデータを一度にフェッチします。
    *   **引数**:
        *   `github_client`: GitHub APIと通信するためのクライアントインスタンス。
    *   **戻り値**: オープンPRを持つリポジトリとそのPR情報のリスト。
    *   **機能**: GraphQLクエリの構築と実行、APIレート制限のハンドリング、取得したPRデータの構造化。

*   **`detect_pr_phase(pr_info: dict, comments: list, html_analyzer: PRHtmlAnalyzer)` (src/gh_pr_phase_monitor/phase/phase_detector.py 内)**
    *   **役割**: 指定されたPull Requestの現在のフェーズ（phase1: Draft、phase2: レビュー指摘対応中、phase3: レビュー待ち、LLM working: コーディングエージェント作業中）を判定します。PRの情報、コメント履歴、HTMLコンテンツの分析結果を考慮します。
    *   **引数**:
        *   `pr_info`: GitHubから取得したPRの詳細情報。
        *   `comments`: PRに投稿されたコメントのリスト。
        *   `html_analyzer`: PRのHTMLコンテンツを解析するインスタンス。
    *   **戻り値**: PRのフェーズを示す文字列（例: "phase1", "phase2", "phase3", "LLM working"）。
    *   **機能**: Draftステータスチェック、特定のレビューコメント（copilot-pull-request-reviewer, copilot-swe-agent）の有無、未解決のレビュー指摘スレッドの有無、HTMLからのLLMステータス抽出などに基づいてフェーズを決定します。

*   **`execute_pr_actions(pr_info: dict, current_phase: str, config: dict, ruleset: dict)` (src/gh_pr_phase_monitor/actions/pr_actions.py 内)**
    *   **役割**: PRの現在のフェーズと設定されたルールセットに基づいて、適切な自動アクション（コメント投稿、PRのReady化、通知送信、自動マージなど）を実行します。Dry-runモードもサポートします。
    *   **引数**:
        *   `pr_info`: 対象のPR情報。
        *   `current_phase`: `detect_pr_phase`によって判定されたPRの現在のフェーズ。
        *   `config`: アプリケーション全体の読み込まれた設定。
        *   `ruleset`: 現在のPRに適用される特定のルールセット設定。
    *   **戻り値**: なし。
    *   **機能**: フェーズごとに設定されたフラグ（`enable_execution_phase1_to_phase2`など）をチェックし、`comment_manager.post_comment`、`notifier.send_notification`、`browser_automation.click_button_by_image`などの低レベルアクションを呼び出します。

*   **`send_notification(topic: str, message: str, url: str)` (src/gh_pr_phase_monitor/ui/notifier.py 内)**
    *   **役割**: ntfy.shサービスを利用して、指定されたトピックにメッセージとURLを含むプッシュ通知を送信します。
    *   **引数**:
        *   `topic`: ntfy.shの通知トピック名。
        *   `message`: 通知本文として送信するメッセージ。
        *   `url`: 通知に埋め込むクリック可能なURL（PRのリンクなど）。
    *   **戻り値**: なし。
    *   **機能**: HTTPリクエストをntfy.shのエンドポイントに送信し、指定された情報で通知を作成します。

*   **`click_button_by_image(image_path: str, confidence: float, ocr_text: str = None)` (src/gh_pr_phase_monitor/browser/button_clicker.py 内)**
    *   **役割**: PyAutoGUIを使用して、指定された画像（ボタンのスクリーンショット）が画面上に表示されたらそれをクリックします。画像が見つからない場合は、オプションでOCRによるテキスト検出にフォールバックします。
    *   **引数**:
        *   `image_path`: クリックするボタンのスクリーンショット画像ファイルへのパス。
        *   `confidence`: 画像マッチングの信頼度（0.0〜1.0）。
        *   `ocr_text`: (オプション) 画像認識が失敗した場合にOCRで検出するテキスト。
    *   **戻り値**: `True`をクリックに成功した場合、`False`を失敗した場合。
    *   **機能**: `pyautogui.locateOnScreen`や`pytesseract`を利用してボタンを特定し、`pyautogui.click`で操作を実行します。失敗時にはデバッグ情報を保存します。

*   **`check_for_updates(current_dir: str, config: dict)` (src/gh_pr_phase_monitor/monitor/auto_updater.py 内)**
    *   **役割**: Gitリポジトリとしてデプロイされている自身のツールの更新をチェックし、利用可能な更新があれば自動的に`git pull`を実行してツールを再起動します。
    *   **引数**:
        *   `current_dir`: ツールが実行されているカレントディレクトリ。
        *   `config`: アプリケーションの読み込まれた設定。
    *   **戻り値**: `True`を更新して再起動した場合、`False`を更新がなかったか自動更新が無効な場合。
    *   **機能**: `git fetch`でリモートの変更を確認し、`git pull`でローカルを更新後、`os.execv`で自身を再起動します。

## 関数呼び出し階層ツリー
```
run_monitor()
├── load_config()
├── check_for_updates()
│   └── (git pull & os.execv(自身を再起動))
└── (メイン監視ループ)
    ├── fetch_all_user_repos_with_prs()
    │   └── github_client.query_graphql()
    │       └── rate_limit_handler.handle_rate_limit()
    ├── for each repository with open PRs:
    │   ├── for each PR:
    │   │   ├── fetch_pr_html() (必要に応じて)
    │   │   ├── comment_fetcher.fetch_comments()
    │   │   ├── detect_pr_phase()
    │   │   │   └── pr_html_analyzer.analyze_html() (HTML解析が必要な場合)
    │   │   ├── execute_pr_actions()
    │   │   │   ├── comment_manager.post_comment() (Phase2コメントなど)
    │   │   │   ├── pr_actions.mark_pr_as_ready() (Phase1 Ready化)
    │   │   │   ├── notifier.send_notification() (Phase3通知)
    │   │   │   │   └── (ntfy.sh APIコール)
    │   │   │   ├── pr_actions.merge_pr() (Phase3自動マージ)
    │   │   │   │   └── button_clicker.click_button_by_image()
    │   │   │   │       ├── pyautogui.locateOnScreen()
    │   │   │   │       └── (pytesseractによるOCRフォールバック)
    │   │   │   └── browser_automation.open_pr_in_browser()
    │   │   └── display.print_pr_status()
    │   └── issue_fetcher.fetch_issues_for_repos_without_open_prs() (PRがないリポジトリの場合)
    │       └── pr_actions.assign_issue_to_copilot() (自動割り当てが有効な場合)
    │           └── button_clicker.click_button_by_image()
    │               ├── pyautogui.locateOnScreen()
    │               └── (pytesseractによるOCRフォールバック)
    ├── local_repo_watcher.watch_local_repositories() (自動pullが有効な場合)
    │   └── (git fetch & git pull)
    └── wait_handler.wait_for_next_interval() (省電力モードへの移行管理含む)

---
Generated at: 2026-03-08 07:01:58 JST
