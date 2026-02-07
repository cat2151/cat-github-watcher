Last updated: 2026-02-08

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのPRを監視し、効率的な開発フローを支援するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、PRのドラフト状態からレビュー待ちまでを自動判定します。
- GraphQL APIとブラウザ自動化を組み合わせ、通知、コメント投稿、PRのReady化、自動マージなどのアクションを実行します。

## 技術スタック
- フロントエンド: PyAutoGUI (ブラウザ自動操縦、画像認識)、Pillow (画像処理)、pygetwindow (ウィンドウ操作)、pytesseract (OCRフォールバック)、Tesseract-OCR (OCRエンジン、システムレベル)
- 音楽・オーディオ: 該当なし
- 開発ツール: Python 3.x (主要開発言語)、GitHub CLI (`gh`、GitHub認証・APIアクセス)、pytest (テストフレームワーク)
- テスト: pytest (Python向けテストフレームワーク)
- ビルドツール: pip (Pythonパッケージ管理)
- 言語機能: Python (スクリプト言語)、GraphQL API (GitHub APIへの効率的なアクセス)
- 自動化・CI/CD: GitHub Actions (README自動生成に利用)、ntfy.sh (モバイル通知サービス)
- 開発標準: .editorconfig (コードスタイル統一)、Ruff (高性能Pythonリンター/フォーマッター)

## ファイル階層ツリー
```
cat-github-watcher/
├── .editorconfig
├── .gitignore
├── .vscode/
│   └── settings.json
├── LICENSE
├── MERGE_CONFIGURATION_EXAMPLES.md
├── PHASE3_MERGE_IMPLEMENTATION.md
├── README.ja.md
├── README.md
├── STRUCTURE.md
├── _config.yml
├── cat-github-watcher.py
├── config.toml.example
├── demo_automation.py
├── docs/
│   ├── IMPLEMENTATION_SUMMARY.ja.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PR67_IMPLEMENTATION.md
│   ├── RULESETS.md
│   ├── VERIFICATION_GUIDE.en.md
│   ├── VERIFICATION_GUIDE.md
│   ├── browser-automation-approaches.en.md
│   ├── browser-automation-approaches.md
│   ├── button-detection-improvements.ja.md
│   └── window-activation-feature.md
├── generated-docs/
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
│       ├── browser_automation.py
│       ├── colors.py
│       ├── comment_fetcher.py
│       ├── comment_manager.py
│       ├── config.py
│       ├── display.py
│       ├── github_auth.py
│       ├── github_client.py
│       ├── graphql_client.py
│       ├── issue_fetcher.py
│       ├── main.py
│       ├── monitor.py
│       ├── notifier.py
│       ├── phase_detector.py
│       ├── pr_actions.py
│       ├── pr_data_recorder.py
│       ├── pr_fetcher.py
│       ├── repository_fetcher.py
│       ├── state_tracker.py
│       ├── time_utils.py
│       └── wait_handler.py
└── tests/
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_check_process_before_autoraise.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_contamination_bug.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
    ├── test_max_llm_working_parallel.py
    ├── test_no_change_timeout.py
    ├── test_no_open_prs_issue_display.py
    ├── test_notification.py
    ├── test_phase3_merge.py
    ├── test_phase_detection.py
    ├── test_post_comment.py
    ├── test_post_phase3_comment.py
    ├── test_pr_actions.py
    ├── test_pr_actions_rulesets_features.py
    ├── test_pr_actions_with_rulesets.py
    ├── test_pr_data_recorder.py
    ├── test_repos_with_prs_structure.py
    ├── test_show_issues_when_pr_count_less_than_3.py
    ├── test_status_summary.py
    ├── test_validate_phase3_merge_config.py
    └── test_verbose_config.py
```

## ファイル詳細説明
-   `.editorconfig`: 複数のエディタやIDE間で一貫したコーディングスタイルを定義するための設定ファイルです。
-   `.gitignore`: Gitがバージョン管理の対象としないファイルやディレクトリを指定するファイルです。
-   `.vscode/settings.json`: VS Codeエディタのワークスペース固有の設定を定義します。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）を記載しています。
-   `MERGE_CONFIGURATION_EXAMPLES.md`: マージ設定に関する具体的な設定例をまとめたドキュメントです。
-   `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3での自動マージ機能の実装詳細に関するドキュメントです。
-   `README.ja.md`, `README.md`: プロジェクトの概要、機能、使い方などを説明する多言語のドキュメントです。
-   `STRUCTURE.md`: プロジェクトの全体的な構造や設計に関するドキュメントです。
-   `_config.yml`: Jekyllなどの静的サイトジェネレーターでドキュメントサイトを構築する際の設定ファイルです。
-   `cat-github-watcher.py`: アプリケーションのエントリーポイントとなるスクリプトです。メインの実行ロジックを呼び出します。
-   `config.toml.example`: ユーザーが設定を行うためのTOML形式の設定ファイルの例です。
-   `demo_automation.py`: 自動化機能のデモンストレーションやテストに用いられるスクリプトです。
-   `docs/`: プロジェクトに関する詳細なドキュメントを格納するディレクトリです。
    -   `IMPLEMENTATION_SUMMARY.ja.md`, `IMPLEMENTATION_SUMMARY.md`: 実装の概要を説明するドキュメントです。
    -   `PR67_IMPLEMENTATION.md`: 特定のプルリクエスト（PR67）に関連する実装詳細のドキュメントです。
    -   `RULESETS.md`: 監視ルールセットの設定方法と利用例に関するドキュメントです。
    -   `VERIFICATION_GUIDE.en.md`, `VERIFICATION_GUIDE.md`: 機能の検証方法を説明するガイドです。
    -   `browser-automation-approaches.en.md`, `browser-automation-approaches.md`: ブラウザ自動化の様々なアプローチに関する考察をまとめたドキュメントです。
    -   `button-detection-improvements.ja.md`: ボタン検出機能の改善点に関するドキュメントです。
    -   `window-activation-feature.md`: ウィンドウアクティベーション機能に関するドキュメントです。
-   `generated-docs/`: AIなどによって自動生成されたドキュメントを格納するディレクトリです。
-   `pytest.ini`: Pythonのテストフレームワークであるpytestの設定ファイルです。
-   `requirements-automation.txt`: ブラウザ自動化機能に必要なPythonパッケージの依存関係をリストアップしたファイルです。
-   `ruff.toml`: コードリンターおよびフォーマッターであるRuffの設定ファイルです。
-   `screenshots/`: ブラウザ自動化（PyAutoGUI）で使用するボタンのスクリーンショット画像が保存されるディレクトリです。
    -   `assign.png`: "Assign" ボタンのスクリーンショット。
    -   `assign_to_copilot.png`: "Assign to Copilot" ボタンのスクリーンショット。
-   `src/`: プロジェクトのソースコード本体を格納するディレクトリです。
    -   `__init__.py`: Pythonパッケージであることを示すファイルです。
    -   `gh_pr_phase_monitor/`: プルリクエストフェーズ監視の主要ロジックを格納するパッケージです。
        -   `browser_automation.py`: PyAutoGUIなどを用いてブラウザ操作を自動化する機能を提供します。
        -   `colors.py`: コンソール出力の色付けに使用するANSIカラーコードと関連ユーティリティを定義します。
        -   `comment_fetcher.py`: GitHubのプルリクエストからコメント情報を取得するロジックを扱います。
        -   `comment_manager.py`: プルリクエストへのコメント投稿や管理に関する機能を提供します。
        -   `config.py`: `config.toml`から設定を読み込み、解析し、アプリケーション全体で利用可能な形式で提供します。
        -   `display.py`: 監視状況やPRの状態をコンソールに表示するためのユーティリティ関数群です。
        -   `github_auth.py`: GitHub CLI (`gh`) を利用した認証処理を担当します。
        -   `github_client.py`: GitHubのREST APIおよびGraphQL APIと連携するための高レベルなクライアントを提供します。
        -   `graphql_client.py`: GitHub GraphQL APIへの低レベルなリクエスト処理を扱います。
        -   `issue_fetcher.py`: GitHubのIssue情報を取得するロジックを扱います。
        -   `main.py`: メインの監視ループと全体的なアプリケーションフローを管理します。`cat-github-watcher.py`から呼び出されます。
        -   `monitor.py`: リポジトリとPRの状態を定期的に監視し、検出されたフェーズに基づいてアクションをトリガーするコアロジックを含みます。
        -   `notifier.py`: ntfy.shなどのサービスを利用して通知を送信する機能を提供します。
        -   `phase_detector.py`: プルリクエストの現在のフェーズ（Draft, レビュー指摘対応中, レビュー待ち, LLM working）を判定するロジックを実装します。
        -   `pr_actions.py`: プルリクエストをReady状態にする、ブラウザで開く、自動マージするなどの具体的なアクションを実行します。
        -   `pr_data_recorder.py`: 各プルリクエストの状態変化を記録し、長期的な傾向分析や省電力モードの制御に利用します。
        -   `pr_fetcher.py`: GitHubからオープンなプルリクエストの情報を効率的に取得します。
        -   `repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリの一覧を取得します。
        -   `state_tracker.py`: アプリケーションの監視状態や過去のPR状態、監視間隔などを追跡・管理します。
        -   `time_utils.py`: 時間に関するユーティリティ関数（例: 時間文字列のパース）を提供します。
        -   `wait_handler.py`: 監視間隔や省電力モードでの待機時間を計算し、アプリケーションの動作を一時停止させる機能を提供します。
-   `tests/`: pytestを使用したユニットテストおよび統合テストのスイートを格納するディレクトリです。

## 関数詳細説明
このプロジェクトはPythonで実装されており、各ファイルは単一責任の原則に従ってモジュール化されています。以下に主要な関数の役割と機能について説明します。具体的な引数や戻り値は提供情報からは判断できませんが、一般的な設計パターンに基づいて説明します。

-   **`main()` (`src/gh_pr_phase_monitor/main.py`内)**
    -   **役割と機能**: アプリケーションの主要な実行フローを制御するエントリポイントです。設定の読み込み、GitHubクライアントの初期化、リポジトリとPRの定期的な監視ループの開始、状態の追跡、およびエラーハンドリングなど、全体のオーケストレーションを担当します。
-   **`fetch_repositories()` (`src/gh_pr_phase_monitor/repository_fetcher.py`内)**
    -   **役割と機能**: 認証済みGitHubユーザーが所有するリポジトリの一覧をGitHub APIから取得します。監視対象となるリポジトリの発見に使用されます。
-   **`fetch_pull_requests()` (`src/gh_pr_phase_monitor/pr_fetcher.py`内)**
    -   **役割と機能**: 指定されたリポジトリ内のすべてのオープンなプルリクエストに関する詳細情報をGitHub GraphQL APIを利用して効率的に取得します。各PRの最新の状態（コメント、レビュー状況、ラベルなど）を含みます。
-   **`detect_phase()` (`src/gh_pr_phase_monitor/phase_detector.py`内)**
    -   **役割と機能**: 取得したプルリクエストのデータに基づき、PRが現在どの開発フェーズにあるかを判定します（例: Draft状態、レビュー指摘対応中、レビュー待ち、LLM作業中）。この判定ロジックはプロジェクトの核となる部分です。
-   **`perform_pr_action()` (`src/gh_pr_phase_monitor/pr_actions.py`内)**
    -   **役割と機能**: 判定されたプルリクエストのフェーズと設定されたルールに基づいて、具体的なアクションを実行します。これには、PRをReady状態に変更する、ブラウザでPRページを開く、自動マージを実行するなどの操作が含まれます。
-   **`post_comment()` (`src/gh_pr_phase_monitor/comment_manager.py`内)**
    -   **役割と機能**: 特定のプルリクエストに対してコメントを投稿します。主に、フェーズの進捗に応じた自動コメント（例: Phase2での変更適用依頼コメント）に使用されます。
-   **`send_notification()` (`src/gh_pr_phase_monitor/notifier.py`内)**
    -   **役割と機能**: ntfy.shなどの外部通知サービスを利用して、ユーザーのモバイル端末などに通知を送信します。Phase3（レビュー待ち）になったPRの通知などに利用されます。
-   **`automate_browser_action()` (`src/gh_pr_phase_monitor/browser_automation.py`内)**
    -   **役割と機能**: PyAutoGUIライブラリなどを用いて、ウェブブラウザの特定の要素（ボタンなど）を識別し、クリックするなどの自動操作を行います。PRの自動マージやIssueの自動割り当て機能で活用されます。
-   **`track_state_changes()` (`src/gh_pr_phase_monitor/state_tracker.py`または`pr_data_recorder.py`内)**
    -   **役割と機能**: 監視対象の各プルリクエストのフェーズや状態の変化を継続的に記録し、管理します。これにより、省電力モードへの切り替えやステータス表示の更新が行われます。
-   **`fetch_issues()` (`src/gh_pr_phase_monitor/issue_fetcher.py`内)**
    -   **役割と機能**: オープンなプルリクエストがないリポジトリから、特定の条件（例: "good first issue"ラベル）に合致するIssue情報を取得し、Copilotへの割り当て候補などを提示します。
-   **`parse_config()` (`src/gh_pr_phase_monitor/config.py`内)**
    -   **役割と機能**: TOML形式の設定ファイル（`config.toml`）を読み込み、アプリケーションが利用しやすいPythonのデータ構造に解析・変換します。ルールセットの適用などもここで行われます。

## 関数呼び出し階層ツリー
```
main.py (アプリケーションのエントリーポイント、監視ループ)
├── config.py (設定の読み込みと解析)
│   └── time_utils.py (時間間隔のパース)
├── github_auth.py (GitHub CLI認証確認)
├── repository_fetcher.py (ユーザー所有リポジトリの取得)
│   └── github_client.py (GitHub API操作の抽象化)
│       └── graphql_client.py (GraphQLリクエストの実行)
├── pr_fetcher.py (オープンPRの取得)
│   └── github_client.py
│       └── graphql_client.py
├── issue_fetcher.py (Issue情報の取得)
│   └── github_client.py
│       └── graphql_client.py
├── phase_detector.py (PRフェーズの判定)
├── state_tracker.py (PR状態と監視間隔の管理)
│   └── pr_data_recorder.py (PRデータ変化の記録)
├── pr_actions.py (PRに対するアクションの実行)
│   ├── comment_manager.py (コメントの投稿)
│   │   └── github_client.py
│   ├── notifier.py (ntfy.sh通知の送信)
│   ├── browser_automation.py (ブラウザ自動操縦)
│   │   └── (PyAutoGUI, Pillow, pygetwindow, pytesseractなどの外部ライブラリ)
├── display.py (コンソール出力の整形)
│   └── colors.py (ANSIカラーコードの適用)
└── wait_handler.py (監視間隔の制御、省電力モード)

---
Generated at: 2026-02-08 07:03:06 JST
