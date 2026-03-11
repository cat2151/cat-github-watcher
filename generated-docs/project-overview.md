Last updated: 2026-03-12

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装のプルリクエスト（PR）フェーズを効率的に監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、PRの状態に応じた通知や自動アクションを実行します。
- ブラウザ自動化によるissue割り当てやPRマージ、ローカルリポジトリの自動更新などの豊富な機能を備えています。

## 技術スタック
- フロントエンド: PyAutoGUI (画面上のボタンクリックやウィンドウ操作を自動化), Pillow (画像処理、スクリーンショットの解析), PyGetWindow (ウィンドウの管理と操作)
- 音楽・オーディオ: (該当なし)
- 開発ツール: Python 3.11+ (主要なプログラミング言語), GitHub CLI (`gh`) (GitHub認証およびAPI連携の基盤), Tesseract-OCR (OCRフォールバックによるテキスト検出), VS Code (.vscode/settings.jsonで開発環境を構成), Git (リポジトリのクローン、pull、バージョン管理)
- テスト: pytest (Pythonコードのテストフレームワーク)
- ビルドツール: (Pythonプロジェクトのため直接的なビルドツールは少ないが、依存関係管理に`pip`を使用。`cargo install`はRustプロジェクト向け機能としてサポート)
- 言語機能: TOML (設定ファイルの記述形式), GraphQL API (GitHubから効率的にデータを取得するためのクエリ言語)
- 自動化・CI/CD: ntfy.sh (モバイル端末へのプッシュ通知サービス), 自己更新機能 (Git pullによるツールの自動更新), ブラウザ自動化 (PRマージやissue割り当てのためのWeb UI操作)
- 開発標準: ruff (高速なPythonリンターおよびフォーマッター), .editorconfig (異なるエディタ・IDE間でのコーディングスタイル統一)

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
│       │   ├── local_repo_cargo.py
│       │   ├── local_repo_checker.py
│       │   ├── local_repo_git.py
│       │   ├── local_repo_watcher.py
│       │   ├── monitor.py
│       │   ├── pages_watcher.py
│       │   ├── pr_processor.py
│       │   ├── snapshot_path_utils.py
│       │   ├── state_tracker.py
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

*   **`.editorconfig`**: 異なるエディタやIDEを使用する開発者間で、インデントスタイルや文字エンコーディングなどの基本的なコーディングスタイルを統一するための設定ファイルです。
*   **`.gitignore`**: Gitがバージョン管理の対象外とするファイルやディレクトリを指定するファイルです。一時ファイルやログ、ビルド成果物などが含まれます。
*   **`.vscode/settings.json`**: Visual Studio Codeエディタ固有の設定ファイルです。プロジェクトごとにリンターやフォーマッター、その他の開発補助機能の動作をカスタマイズします。
*   **`LICENSE`**: このプロジェクトのライセンス情報（MIT License）を記述したファイルです。
*   **`README.ja.md`**: プロジェクトの目的、機能、使い方などを日本語で説明する主要なドキュメントファイルです。
*   **`README.md`**: プロジェクトの目的、機能、使い方などを英語で説明するドキュメントファイルです。`README.ja.md`から自動生成されます。
*   **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレータで使用される設定ファイルですが、このプロジェクトでは直接的な使用は明記されていません。
*   **`cat-github-watcher.py`**: プロジェクトのメインエントリーポイントとなるスクリプトファイルです。ツールの起動と主要な監視ループの実行を担います。
*   **`config.toml.example`**: 設定ファイル`config.toml`のサンプルです。監視間隔、通知設定、自動化機能の有効化など、様々なカスタマイズオプションが記述されています。
*   **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーションやテストに使用される可能性のあるスクリプトです。
*   **`docs/RULESETS.md`**: `rulesets`機能に関する詳細な説明が記述されたドキュメントです。特定のリポジトリに対するアクションのカスタマイズ方法などを説明します。
*   **`docs/button-detection-improvements.ja.md`**: ブラウザ自動化におけるボタン検出機能の改善点や仕組みについて日本語で説明したドキュメントです。
*   **`docs/window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメントです。ブラウザ自動化におけるウィンドウ操作について説明します。
*   **`fetch_pr_html.py`**: プルリクエストのHTMLコンテンツを取得するための補助スクリプト、またはテスト用スクリプトです。
*   **`generated-docs/`**: 自動生成されたドキュメントを格納するディレクトリです。
*   **`pyproject.toml`**: Pythonプロジェクトのビルドシステムや依存関係、メタデータなどを定義する標準ファイルです。
*   **`pytest.ini`**: pytestテストフレームワークの設定ファイルです。テストの実行方法やカバレッジレポートの設定などを記述します。
*   **`requirements-automation.txt`**: ブラウザ自動化機能に必要なPythonパッケージのリストを定義したファイルです。
*   **`ruff.toml`**: Pythonのリンター/フォーマッターであるRuffの設定ファイルです。コードの品質と一貫性を保つためのルールが定義されています。
*   **`screenshots/`**: ブラウザ自動化でPyAutoGUIが使用するボタンのスクリーンショット画像を格納するディレクトリです。`assign.png`や`assign_to_copilot.png`などが含まれます。
*   **`src/gh_pr_phase_monitor/`**: プロジェクトの主要なPythonソースコードを格納するパッケージです。
    *   **`__init__.py`**: Pythonパッケージの初期化ファイルです。
    *   **`actions/pr_actions.py`**: プルリクエストに対して実行される具体的なアクション（Ready化、コメント投稿、ブラウザ起動、マージなど）を定義します。
    *   **`browser/browser_automation.py`**: PyAutoGUIなどを利用したブラウザ自動化のコアロジックを実装します。
    *   **`browser/browser_cooldown.py`**: ブラウザ操作間のクールダウン時間や待機処理を管理します。
    *   **`browser/button_clicker.py`**: 画面上の特定のボタンを画像認識やOCRで探し、クリックする機能を提供します。
    *   **`browser/click_config_validator.py`**: ブラウザクリック自動化設定の有効性を検証します。
    *   **`browser/window_manager.py`**: ウィンドウの管理（アクティブ化、最大化など）を行うユーティリティです。
    *   **`core/colors.py`**: ターミナル出力の色付けに使用されるANSIカラーコードとカラースキームを定義します。
    *   **`core/config.py`**: 設定ファイル`config.toml`の読み込み、解析、および検証を行うモジュールです。
    *   **`core/config_printer.py`**: 現在の設定内容を整形して表示する機能を提供します（verboseモード用）。
    *   **`core/interval_parser.py`**: 設定ファイルで指定された時間間隔（例: "1m", "30s"）を解析し、秒数に変換するユーティリティです。
    *   **`core/process_utils.py`**: プロセス関連のユーティリティ関数を提供します。
    *   **`core/time_utils.py`**: 時間関連のユーティリティ関数（経過時間計算など）を提供します。
    *   **`github/comment_fetcher.py`**: GitHubのコメントを取得する機能を提供します。
    *   **`github/comment_manager.py`**: GitHubのプルリクエストにコメントを投稿したり、既存のコメントを管理する機能を提供します。
    *   **`github/github_auth.py`**: GitHub CLI (`gh`) を利用した認証処理を管理します。
    *   **`github/github_client.py`**: GitHub APIとの主要なインターフェースを提供し、PR情報やissue情報の取得を抽象化します。
    *   **`github/graphql_client.py`**: GitHub GraphQL APIにリクエストを送信するための低レベルクライアントです。
    *   **`github/issue_fetcher.py`**: GitHubのissue情報を取得する機能を提供します。
    *   **`github/pr_fetcher.py`**: GitHubのプルリクエスト情報を取得する機能を提供します。
    *   **`github/rate_limit_handler.py`**: GitHub APIのレート制限を監視し、制限を超えないようにリクエストを調整します。
    *   **`github/repository_fetcher.py`**: 認証済みユーザーの所有リポジトリ情報を取得する機能を提供します。
    *   **`main.py`**: `cat-github-watcher.py`から呼び出される、監視ツールのメイン実行ロジックを含むモジュールです。
    *   **`monitor/auto_updater.py`**: ツールの自己更新（Git pullと再起動）を管理します。
    *   **`monitor/error_logger.py`**: エラー発生時にログを記録する機能を提供します。
    *   **`monitor/iteration_runner.py`**: 監視ループの各イテレーションを実行し、処理の流れを制御します。
    *   **`monitor/local_repo_cargo.py`**: `cargo install`されたリポジトリの自動更新を管理します。
    *   **`monitor/local_repo_checker.py`**: ローカルリポジトリの状態（pull可能かなど）をチェックします。
    *   **`monitor/local_repo_git.py`**: ローカルリポジトリに対するGit操作（fetch, pull）を行います。
    *   **`monitor/local_repo_watcher.py`**: 親ディレクトリ内のローカルリポジトリを監視し、自動pull機能を提供します。
    *   **`monitor/monitor.py`**: 監視ループ全体の状態を管理し、主要な処理を調整します。省電力モードの制御も行います。
    *   **`monitor/pages_watcher.py`**: GitHub Pagesの状態変化を監視する機能を提供する可能性があります。
    *   **`monitor/pr_processor.py`**: 取得したプルリクエストデータに対してフェーズ判定やアクション実行などの処理を適用します。
    *   **`monitor/snapshot_path_utils.py`**: スナップショットファイルのパスを管理するユーティリティです。
    *   **`monitor/state_tracker.py`**: 監視対象のPRやリポジトリの状態を追跡し、変更を検知します。
    *   **`phase/html/html_status_processor.py`**: PRのHTMLコンテンツを解析し、特定のステータス情報を抽出します。
    *   **`phase/html/llm_status_extractor.py`**: HTMLからLLM（Copilotなど）の作業ステータスを抽出します。
    *   **`phase/html/pr_html_analyzer.py`**: PRのHTMLをより詳細に分析する機能を提供します。
    *   **`phase/html/pr_html_fetcher.py`**: 特定のPRのHTMLコンテンツをウェブから取得します。
    *   **`phase/html/pr_html_saver.py`**: 取得したPRのHTMLコンテンツを保存します。
    *   **`phase/phase_detector.py`**: プルリクエストの現在のフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中など）を判定する主要なロジックを実装します。
    *   **`ui/display.py`**: ターミナルへの情報表示（PRリスト、ステータス、ログなど）を整形して行います。
    *   **`ui/notification_window.py`**: ブラウザ自動化中に画面上に表示される小さな通知ウィンドウを管理します。
    *   **`ui/notifier.py`**: ntfy.shなどのサービスを利用してモバイル通知を送信する機能を提供します。
    *   **`ui/wait_handler.py`**: 処理の待機時間やクールダウンを管理し、ユーザー体験を損なわないようにします。
*   **`tests/`**: プロジェクトのテストスイートを格納するディレクトリです。各ファイルは特定の機能やモジュールに対するテストコードを含みます。

## 関数詳細説明

（提供された情報には具体的な関数シグネチャがないため、主要な機能を提供すると思われる関数とその役割について、プロジェクト情報から推測して説明します。）

*   **`gh_pr_phase_monitor.main.run_main_loop(config)`**:
    *   **役割**: アプリケーションのメイン監視ループを開始します。設定情報に基づいて、定期的にGitHubからPR情報を取得し、フェーズ判定、アクション実行を行います。
    *   **引数**: `config` (dict/object): ロードされた設定情報オブジェクト。
    *   **戻り値**: なし。Ctrl+Cで停止するまで継続的に実行されます。
*   **`gh_pr_phase_monitor.core.config.load_config(config_path)`**:
    *   **役割**: 指定されたパスからTOML形式の設定ファイルを読み込み、解析します。デフォルト値の適用や設定の検証も行います。
    *   **引数**: `config_path` (str): 設定ファイル`config.toml`のパス。
    *   **戻り値**: ロードされ、検証済みの設定オブジェクト。
*   **`gh_pr_phase_monitor.github.github_client.GitHubClient.fetch_user_repositories()`**:
    *   **役割**: 認証済みGitHubユーザーが所有するすべてのリポジトリのリストをGitHub GraphQL APIを通じて取得します。
    *   **引数**: なし。
    *   **戻り値**: リポジトリ情報のリスト。
*   **`gh_pr_phase_monitor.github.pr_fetcher.PRFetcher.fetch_pull_requests(repo_owner, repo_name)`**:
    *   **役割**: 指定されたリポジトリのオープンなプルリクエスト情報をGitHub GraphQL APIから取得します。
    *   **引数**: `repo_owner` (str): リポジトリの所有者名、`repo_name` (str): リポジトリ名。
    *   **戻り値**: プルリクエストオブジェクトのリスト。
*   **`gh_pr_phase_monitor.phase.phase_detector.PhaseDetector.detect_pr_phase(pr_data, html_content=None)`**:
    *   **役割**: 与えられたプルリクエストデータと（必要に応じて）そのHTMLコンテンツを分析し、現在のフェーズ（Draft状態、レビュー指摘対応中、レビュー待ち、LLM作業中など）を判定します。
    *   **引数**: `pr_data` (object): プルリクエストのデータオブジェクト、`html_content` (str, optional): PRページのHTMLコンテンツ。
    *   **戻り値**: 検出されたフェーズを示す文字列（例: "phase1", "phase2", "LLM working"）。
*   **`gh_pr_phase_monitor.actions.pr_actions.PRActions.execute_actions_for_phase(pr_data, phase, config, ruleset)`**:
    *   **役割**: 特定のプルリクエストが検出されたフェーズに基づいて、設定されたアクション（Draft PRのReady化、コメント投稿、ntfy通知、ブラウザ起動、PRマージなど）を実行します。Dry-runモードの制御も行います。
    *   **引数**: `pr_data` (object): プルリクエストデータ、`phase` (str): 現在のPRフェーズ、`config` (object): グローバル設定、`ruleset` (object): リポジトリ固有のルールセット。
    *   **戻り値**: なし。
*   **`gh_pr_phase_monitor.browser.browser_automation.BrowserAutomation.click_button(button_name, config)`**:
    *   **役割**: 指定されたボタン名に対応するスクリーンショットまたはOCRテキストを使用して、画面上のボタンを自動でクリックします。画像認識の信頼度、OCRフォールバック、デバッグ機能が含まれます。
    *   **引数**: `button_name` (str): クリックするボタンの識別名、`config` (object): ブラウザ自動化に関する設定。
    *   **戻り値**: `True` (成功) または `False` (失敗)。
*   **`gh_pr_phase_monitor.monitor.local_repo_watcher.LocalRepoWatcher.check_and_pull_local_repos()`**:
    *   **役割**: ローカルファイルシステム上のリポジトリをスキャンし、`git pull`が可能なリポジトリを特定して、必要に応じて自動で`git pull`を実行します。
    *   **引数**: なし。
    *   **戻り値**: なし。
*   **`gh_pr_phase_monitor.monitor.auto_updater.AutoUpdater.check_and_update()`**:
    *   **役割**: 現在のツールのGitリポジトリに更新があるかをチェックし、更新があれば自動的に`git pull`を実行して再起動します。
    *   **引数**: なし。
    *   **戻り値**: `True` (更新して再起動が必要) または `False` (更新なし)。
*   **`gh_pr_phase_monitor.ui.notifier.Notifier.send_ntfy_notification(message, url)`**:
    *   **役割**: ntfy.shサービスを利用して、指定されたメッセージとURLを含むモバイル通知を送信します。
    *   **引数**: `message` (str): 通知メッセージ、`url` (str): 通知に含めるURL（クリック可能）。
    *   **戻り値**: なし。

## 関数呼び出し階層ツリー
```
cat-github-watcher.py (または src/gh_pr_phase_monitor/main.py の run_main_loop)
├── load_config()
├── AutoUpdater.check_and_update()
├── GitHubClient の初期化
│   └── GitHubAuth.authenticate()
├── Monitor.run_monitoring_loop()
│   ├── IterationRunner.run_iteration()
│   │   ├── RepositoryFetcher.fetch_user_repositories()
│   │   ├── PRFetcher.fetch_pull_requests() (各リポジトリに対して)
│   │   ├── PhaseDetector.detect_pr_phase() (各PRに対して)
│   │   │   └── HTMLStatusProcessor / LLMStatusExtractor / PRHTMLAnalyzer など HTML解析関連関数
│   │   ├── PRActions.execute_actions_for_phase() (各PRとフェーズに対して)
│   │   │   ├── CommentManager.post_comment()
│   │   │   ├── Notifier.send_ntfy_notification()
│   │   │   └── BrowserAutomation.open_and_click_button() (Phase3マージ、Issue割り当て時)
│   │   │       ├── BrowserAutomation.navigate_to_url()
│   │   │       ├── WindowManager.ensure_browser_active()
│   │   │       └── ButtonClicker.click_button()
│   │   │           ├── Image recognition (PyAutoGUI)
│   │   │           └── OCR detection (Pytesseract)
│   │   ├── IssueFetcher.fetch_issues() (PRが少ないリポジトリに対して)
│   │   ├── LocalRepoWatcher.check_and_pull_local_repos()
│   │   │   ├── LocalRepoChecker.check_pull_status()
│   │   │   └── LocalRepoGit.perform_git_pull()
│   │   │   └── LocalRepoCargo.perform_cargo_install() (もし設定されていれば)
│   │   ├── StateTracker.update_state()
│   │   └── Display.display_status()
│   └── RateLimitHandler.handle_rate_limit()
└── ErrorLogger.log_error() (エラー発生時)

---
Generated at: 2026-03-12 07:03:46 JST
