Last updated: 2026-02-10

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのPRを効率的に監視し、適切な通知やアクションを実行するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIを活用してPRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定します。
- 必要に応じてDraft PRのReady化、自動コメント投稿、モバイル通知、自動マージ、issue自動割り当てなどの自動化機能を提供し、開発ワークフローを支援します。

## 技術スタック
- フロントエンド: N/A (本プロジェクトはCLIツールであり、直接的なフロントエンド技術は使用していません。)
- 音楽・オーディオ: N/A
- 開発ツール:
    - **Python (3.10以上)**: プロジェクトの主要な実装言語。
    - **GitHub CLI (`gh`)**: GitHub認証情報の取得とGitHub APIへのアクセスに使用。
    - **GitHub GraphQL API**: PRやリポジトリの情報を効率的に取得するために利用。
    - **toml**: 設定ファイル (`config.toml`) のフォーマットとして使用。
    - **PyAutoGUI**: ブラウザの自動操作（ボタンクリックなど）を実現するためのライブラリ。
    - **Pillow**: PyAutoGUIの依存ライブラリとして画像処理に使用。
    - **pygetwindow**: PyAutoGUIの依存ライブラリとしてウィンドウ操作に使用。
    - **pytesseract**: 画像認識が失敗した場合のOCRフォールバックに使用されるPythonラッパー。
    - **tesseract-ocr**: OCR機能のバックエンドとして、システムレベルでインストールされるエンジン。
    - **Git**: バージョン管理システムとしてプロジェクトの管理に使用。
- テスト:
    - **pytest**: Pythonアプリケーションのテストフレームワークとして利用。
- ビルドツール: N/A (主にPythonスクリプトで構成されており、専用のビルドツールは使用していません。)
- 言語機能:
    - **Python (3.10以降の言語機能)**: モダンなPythonの機能と構文を活用して開発されています。
- 自動化・CI/CD:
    - **ntfy.sh**: PRの状態変化（特にレビュー待ち）をモバイル端末に通知するサービス。
    - **Pythonスクリプトによる各種自動化**: PRのReady化、コメント投稿、マージ、issue割り当てなど、コードによるワークフロー自動化を実現。
- 開発標準:
    - **Ruff**: コードのフォーマットとリンティングを行い、コード品質と一貫性を保つためのツール。
    - **.editorconfig**: 異なるエディタやIDE間でコードスタイルを統一するための設定ファイル。

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
│   ├── RULESETS.md
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
    ├── test_pr_title_fix.py
    ├── test_repos_with_prs_structure.py
    ├── test_show_issues_when_pr_count_less_than_3.py
    ├── test_status_summary.py
    ├── test_validate_phase3_merge_config.py
    └── test_verbose_config.py
```

## ファイル詳細説明
-   **`.editorconfig`**: さまざまなエディタで一貫したコーディングスタイルを維持するための設定ファイル。
-   **`.gitignore`**: Gitが追跡しないファイルやディレクトリを指定する設定ファイル。
-   **`.vscode/settings.json`**: VS Codeエディタのワークスペース固有の設定を定義。
-   **`LICENSE`**: 本ソフトウェアのライセンス情報（MIT License）が記述されています。
-   **`MERGE_CONFIGURATION_EXAMPLES.md`**: マージ設定の具体的な例を示すドキュメント。
-   **`PHASE3_MERGE_IMPLEMENTATION.md`**: Phase3の自動マージ機能の実装詳細に関するドキュメント。
-   **`README.ja.md`**: プロジェクトの日本語による概要、使い方、機能などの説明書。
-   **`README.md`**: プロジェクトの英語による概要、使い方、機能などの説明書。
-   **`STRUCTURE.md`**: プロジェクトのアーキテクチャや構造に関するドキュメント。
-   **`_config.yml`**: GitHub Pagesなどの設定ファイル（プロジェクト情報からは具体的な用途不明）。
-   **`cat-github-watcher.py`**: プロジェクトのエントリーポイントとなるスクリプト。ツールの起動とメイン処理への橋渡しをします。
-   **`config.toml.example`**: ユーザーがコピーして使用するための設定ファイル (`config.toml`) のテンプレート。
-   **`demo_automation.py`**: 自動化機能のデモンストレーション用スクリプト。
-   **`docs/RULESETS.md`**: ルールセットの設定と使用方法に関するドキュメント。
-   **`docs/button-detection-improvements.ja.md`**: ボタン検出機能の改善点に関する日本語ドキュメント。
-   **`docs/window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメント。
-   **`generated-docs/`**: 自動生成されたドキュメントを格納するためのディレクトリ。
-   **`pytest.ini`**: pytestテストランナーの設定ファイル。
-   **`requirements-automation.txt`**: ブラウザ自動化機能に必要なPythonライブラリの一覧。
-   **`ruff.toml`**: コードリンター/フォーマッターであるRuffの設定ファイル。
-   **`screenshots/`**: PyAutoGUIによる自動化で使用される、ボタンのスクリーンショット画像が保存されるディレクトリ。
-   **`src/__init__.py`**: `src`ディレクトリがPythonパッケージであることを示すファイル。
-   **`src/gh_pr_phase_monitor/__init__.py`**: `gh_pr_phase_monitor`ディレクトリがPythonパッケージであることを示すファイル。
-   **`src/gh_pr_phase_monitor/browser_automation.py`**: PyAutoGUIを使用してブラウザの特定の要素（ボタンなど）を検出・操作するロジックを実装。
-   **`src/gh_pr_phase_monitor/colors.py`**: コンソール出力にANSIカラーコードを適用し、視認性を高めるためのユーティリティを提供。
-   **`src/gh_pr_phase_monitor/comment_fetcher.py`**: GitHub APIを通じてPRのコメントを取得する機能を提供。
-   **`src/gh_pr_phase_monitor/comment_manager.py`**: PRへのコメント投稿、既存コメントの確認など、コメント関連の操作を管理。
-   **`src/gh_pr_phase_monitor/config.py`**: `config.toml`ファイルから設定を読み込み、解析し、アプリケーション全体で利用可能な形式で提供。
-   **`src/gh_pr_phase_monitor/display.py`**: CLIへの情報出力（PRのステータス、ログなど）を整形し、表示するための機能を提供。
-   **`src/gh_pr_phase_monitor/github_auth.py`**: GitHub CLI (`gh`) を利用してGitHub認証情報（トークンなど）を取得・管理。
-   **`src/gh_pr_phase_monitor/github_client.py`**: GitHub REST APIとの連携を担当し、PR情報の取得やアクション実行などの一般的なGitHub操作をカプセル化。
-   **`src/gh_pr_phase_monitor/graphql_client.py`**: GitHub GraphQL APIに特化したクライアントとして、効率的なデータ取得クエリを実行。
-   **`src/gh_pr_phase_monitor/issue_fetcher.py`**: GitHub APIからリポジトリのissue情報を取得する機能を提供。
-   **`src/gh_pr_phase_monitor/main.py`**: アプリケーションのメイン実行ループを定義し、各種モジュールを連携させてPR監視のプロセスをオーケストレーション。
-   **`src/gh_pr_phase_monitor/monitor.py`**: PR監視のコアロジックを実装し、設定された間隔でPRの状態をチェックする役割を担う。
-   **`src/gh_pr_phase_monitor/notifier.py`**: `ntfy.sh`サービスを利用して、PRの特定の状態変化をモバイルデバイスに通知する機能を提供。
-   **`src/gh_pr_phase_monitor/phase_detector.py`**: PRの現在の状態に基づいて、プロジェクトが定義する「フェーズ」（phase1, phase2, phase3, LLM working）を判定するロジックを実装。
-   **`src/gh_pr_phase_monitor/pr_actions.py`**: PRをDraftからReady状態に変更したり、ブラウザでPRページを開いたり、PRをマージしたりといった具体的なアクションを実行。
-   **`src/gh_pr_phase_monitor/pr_data_recorder.py`**: 各PRの履歴データや状態を記録し、後続の処理や状態追跡に利用。
-   **`src/gh_pr_phase_monitor/pr_fetcher.py`**: GitHub APIを介して、ユーザー所有リポジトリ内のPull Requestに関する詳細情報を取得。
-   **`src/gh_pr_phase_monitor/repository_fetcher.py`**: GitHub APIを利用して、認証済みユーザーが所有する全リポジトリのリストを取得。
-   **`src/gh_pr_phase_monitor/state_tracker.py`**: PRやリポジトリの状態変化を継続的に追跡し、省電力モードの制御や状態の再評価をトリガー。
-   **`src/gh_pr_phase_monitor/time_utils.py`**: 時間間隔のパース、タイマー管理など、時間に関連するユーティリティ関数を提供。
-   **`src/gh_pr_phase_monitor/wait_handler.py`**: 監視ループ内での待機処理や、APIレート制限に対応するための遅延処理を管理。
-   **`tests/`**: pytestフレームワークを使用した単体テストおよび結合テストが格納されたディレクトリ。

## 関数詳細説明
提供されたプロジェクト情報には、個々の関数の詳細な名前、引数、戻り値に関する具体的な記述がないため、ハルシネーションを避けるため、各ファイルの主要な機能として説明します。

-   **`src/gh_pr_phase_monitor/browser_automation.py`**:
    -   ブラウザウィンドウを操作し、特定のボタン（例: "Assign to Copilot", "Merge pull request"）を画面上で検出してクリックする機能を提供します。画像認識やOCRフォールバックを使用します。
-   **`src/gh_pr_phase_monitor/colors.py`**:
    -   ANSIエスケープコードを生成し、テキストに色を付けてターミナルに出力するユーティリティ機能を提供します。
-   **`src/gh_pr_phase_monitor/comment_fetcher.py`**:
    -   指定されたPull Requestのコメント履歴を取得し、特定の条件（例: 特定のエージェントからのコメント）でフィルタリングする機能を提供します。
-   **`src/gh_pr_phase_monitor/comment_manager.py`**:
    -   Pull Requestに対して新しいコメントを投稿したり、既存のコメントを検索・確認したりする機能を提供します。
-   **`src/gh_pr_phase_monitor/config.py`**:
    -   `config.toml`ファイルから設定値を読み込み、構造化されたデータとしてアクセス可能にする機能を提供します。また、設定値のバリデーションも行います。
-   **`src/gh_pr_phase_monitor/display.py`**:
    -   Pull Requestの現在のフェーズ、リポジトリ名、URLなどの情報を整形し、ユーザーフレンドリーな形式でコンソールに出力する機能を提供します。
-   **`src/gh_pr_phase_monitor/github_auth.py`**:
    -   GitHub CLI (`gh`) を利用して、GitHub APIにアクセスするための認証トークンを取得・更新する機能を提供します。
-   **`src/gh_pr_phase_monitor/github_client.py`**:
    -   GitHub REST APIの一般的なエンドポイント（Pull Requestの詳細取得、ステータス更新など）を叩くためのクライアント機能を提供します。
-   **`src/gh_pr_phase_monitor/graphql_client.py`**:
    -   GitHub GraphQL APIに対するクエリを構築し、実行するためのクライアント機能を提供します。複数の情報を一度に効率的に取得することに特化しています。
-   **`src/gh_pr_phase_monitor/issue_fetcher.py`**:
    -   指定されたリポジトリのオープンなIssue情報を取得し、特定のラベル（例: "good first issue", "ci-failure"）を持つIssueをフィルタリングする機能を提供します。
-   **`src/gh_pr_phase_monitor/main.py`**:
    -   アプリケーションの起動点であり、監視ループ全体を調整する主要な機能を提供します。設定の読み込み、モニターの初期化、定期的な実行などを担当します。
-   **`src/gh_pr_phase_monitor/monitor.py`**:
    -   GitHubリポジトリとPull Requestの状態を定期的にチェックし、状態の変化を検知する中核的な監視機能を提供します。監視間隔や省電力モードの管理も行います。
-   **`src/gh_pr_phase_monitor/notifier.py`**:
    -   ntfy.shサービスを利用して、カスタマイズ可能なメッセージと共にモバイル端末に通知を送信する機能を提供します。
-   **`src/gh_pr_phase_monitor/phase_detector.py`**:
    -   Pull Requestのタイトル、ドラフト状態、コメント履歴などに基づいて、そのPRがどのフェーズ（phase1, phase2, phase3, LLM working）にあるかを判定するロジックを提供します。
-   **`src/gh_pr_phase_monitor/pr_actions.py`**:
    -   Pull RequestをDraft状態からReady状態に変更する、指定されたPRのURLをブラウザで開く、またはPRをマージするといった具体的なアクションを実行する機能を提供します。
-   **`src/gh_pr_phase_monitor/pr_data_recorder.py`**:
    -   監視対象のPull Requestのメタデータや状態の履歴を記録し、後の分析や状態変化の検出に使用する機能を提供します。
-   **`src/gh_pr_phase_monitor/pr_fetcher.py`**:
    -   GitHub APIから特定のユーザーが所有するリポジトリ内のオープンなPull Requestのリストと詳細情報を取得する機能を提供します。
-   **`src/gh_pr_phase_monitor/repository_fetcher.py`**:
    -   認証されたGitHubユーザーが所有するすべてのリポジトリのリストを取得する機能を提供します。
-   **`src/gh_pr_phase_monitor/state_tracker.py`**:
    -   監視対象の各Pull Requestおよびリポジトリの状態変化を追跡し、長時間変化がない場合に省電力モードへの移行を管理する機能を提供します。
-   **`src/gh_pr_phase_monitor/time_utils.py`**:
    -   時間間隔の文字列（例: "1m", "30s"）を秒数に変換する、時間計測、スリープなどの時間関連ユーティリティ機能を提供します。
-   **`src/gh_pr_phase_monitor/wait_handler.py`**:
    -   APIレート制限や監視間隔に従って、プログラムの実行を一時停止（待機）させるための機能を提供します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。提供されたプロジェクト情報には、具体的な関数間の呼び出し関係に関する記述がないため、ハルシネーションを避けるために生成を控えました。

---
Generated at: 2026-02-10 07:09:09 JST
