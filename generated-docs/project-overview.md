Last updated: 2026-02-13

# Project Overview

## プロジェクト概要
- GitHub CopilotによるPRの自動実装フェーズを監視し、適切な通知やアクションを実行するPythonツールです。
- 認証済みユーザーの全リポジトリを対象に、GraphQL APIでPRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を効率的に自動判定します。
- レビュー待ち通知、Draft PRのReady化、自動コメント、issue自動割り当てなど、開発ワークフローを支援する多様な自動化機能を提供します。

## 技術スタック
- フロントエンド: CLIベースのツールであり、特定のフロントエンド技術は使用していません。ターミナル出力のカラーリングにANSIカラーコードを利用しています。
- 音楽・オーディオ: 該当する技術は使用していません。
- 開発ツール:
    - **Python 3.10+**: プロジェクトの主要なプログラミング言語および実行環境です。
    - **GitHub CLI (`gh`)**: GitHub APIとの認証や基本的な操作のために使用されます。
    - **PyAutoGUI**: ブラウザの自動操作、画像認識によるボタンクリック、ウィンドウ管理などに利用され、自動マージやissue割り当て機能の基盤となっています。
    - **Pillow**: PyAutoGUIの依存ライブラリとして画像処理機能を提供します。
    - **pygetwindow**: PyAutoGUIの依存ライブラリとしてウィンドウ情報の取得や操作を行います。
    - **tesseract-ocr (システムレベル)**: OCRフォールバック機能が有効な場合に、画像認識の補助としてボタンのテキスト検出に使用されます。
    - **pytesseract**: Pythonからtesseract-ocrを呼び出すためのラッパーライブラリです。
- テスト:
    - **pytest**: プロジェクトのテストスイートを実行するための主要なテストフレームワークです。
- ビルドツール:
    - **TOML**: 設定ファイル(`config.toml`)の読み込みと解析に使用されるフォーマットです。
- 言語機能:
    - **GraphQL API (GitHub)**: GitHubのプルリクエストやリポジトリの情報を効率的に取得するために利用されます。
- 自動化・CI/CD:
    - **ntfy.sh**: フェーズ3（レビュー待ち）のPRが検出された際に、モバイル端末への通知を送信するために使用されるサービスです。
    - **GitHub Actions**: READMEの自動翻訳など、プロジェクトの補助的な自動化（本ツール自体はPythonで実装）に利用されることがあります。
- 開発標準:
    - **.editorconfig**: 異なるエディタやIDE間でコードスタイル（インデント、文字コードなど）を統一するための設定です。
    - **ruff**: コードの品質を維持し、スタイルを統一するための高速なPythonリンターおよびフォーマッターです。

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

## ファイル詳細説明
-   **`.editorconfig`**: 異なるエディタやIDEを使用する開発者間で、インデントスタイル、改行コード、文字エンコーディングなどのコードフォーマットを自動的に統一するための設定ファイルです。
-   **`.gitignore`**: Gitがバージョン管理の対象としないファイルやディレクトリ（例: 実行ファイル、ログ、一時ファイル、設定ファイルなど）を指定するファイルです。
-   **`.vscode/settings.json`**: Visual Studio Codeエディタにおける、このプロジェクト固有のワークスペース設定を定義するファイルです。リンター、フォーマッター、Pythonインタープリターのパスなどが設定されます。
-   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記載したファイルで、ソフトウェアの利用、配布、変更に関する条件を定めます。
-   **`MERGE_CONFIGURATION_EXAMPLES.md`**: 自動マージ機能に関する設定例や利用方法を具体的に示したMarkdown形式のドキュメントです。
-   **`PHASE3_MERGE_IMPLEMENTATION.md`**: Phase3における自動マージ機能の実装の詳細、内部動作、設計思想などを説明するMarkdownドキュメントです。
-   **`README.ja.md`**: プロジェクトの概要、機能、使い方、設定方法などを日本語で説明する主要なドキュメントです。
-   **`README.md`**: プロジェクトの概要、機能、使い方、設定方法などを英語で説明する主要なドキュメントです。
-   **`STRUCTURE.md`**: プロジェクトの全体的なアーキテクチャ、モジュール構成、各コンポーネントの役割など、構造に関する詳細な情報を提供するMarkdownドキュメントです。
-   **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレーターで利用される可能性のある設定ファイルです。
-   **`cat-github-watcher.py`**: プロジェクトのルートにあるエントリーポイントスクリプトで、ツールを起動する際に直接実行されます。
-   **`config.toml.example`**: ユーザーが`config.toml`を作成する際のテンプレートとなる設定ファイルの例です。カスタマイズ可能な項目とその説明が含まれています。
-   **`demo_automation.py`**: ブラウザ自動操作機能の動作をデモンストレーションするための補助的なスクリプトです（推定）。
-   **`docs/RULESETS.md`**: `config.toml`内で定義される`[[rulesets]]`セクション（リポジトリごとのルールやアクションの有効化）について詳しく説明するドキュメントです。
-   **`docs/button-detection-improvements.ja.md`**: 自動化機能におけるボタン検出技術の改善点やその背景について日本語で説明するドキュメントです。
-   **`docs/window-activation-feature.md`**: ウィンドウの自動アクティベーション機能（ブラウザ自動操作の際にウィンドウを前面に表示する）に関するドキュメントです。
-   **`generated-docs/`**: AIによって自動生成されたドキュメントや資料が格納されるディレクトリです（推定）。
-   **`pytest.ini`**: pytestテストフレームワークの挙動をカスタマイズするための設定ファイルです。テストの検出方法、プラグイン、マーカーなどが指定されます。
-   **`requirements-automation.txt`**: PyAutoGUIなどのブラウザ自動操作機能を利用するために必要なPythonパッケージとそのバージョンを列挙したファイルです。
-   **`ruff.toml`**: 高速リンター・フォーマッターであるRuffの設定ファイルです。コードスタイル、エラーチェックルール、無視するファイルなどが定義されます。
-   **`screenshots/`**: PyAutoGUIの画像認識機能が利用する、対象となるボタンのスクリーンショット画像が保存されるディレクトリです。
    -   **`assign.png`**: GitHubの「Assign」ボタンのスクリーンショット画像。
    -   **`assign_to_copilot.png`**: GitHubの「Assign to Copilot」ボタンのスクリーンショット画像。
-   **`src/__init__.py`**: Pythonが`src`ディレクトリをパッケージとして認識するために必要なファイルです。
-   **`src/gh_pr_phase_monitor/__init__.py`**: Pythonが`gh_pr_phase_monitor`ディレクトリをサブパッケージとして認識するために必要なファイルです。
-   **`src/gh_pr_phase_monitor/browser_automation.py`**: PyAutoGUIを利用したブラウザの起動、タブ操作、画像認識によるボタンクリック、テキスト入力などの自動操作ロジックを実装しています。
-   **`src/gh_pr_phase_monitor/colors.py`**: ターミナル出力に色を付けるためのANSIカラーコードの定義と、テキストを色付けするユーティリティ関数を提供します。
-   **`src/gh_pr_phase_monitor/comment_fetcher.py`**: 特定のプルリクエスト（PR）からコメントを取得し、その内容を解析するためのロジックを実装しています。
-   **`src/gh_pr_phase_monitor/comment_manager.py`**: PRへの新しいコメントの投稿、既存コメントの確認、特定のコメント（例: エージェントのレビューコメント）の存在チェックなど、コメント関連の操作を管理します。
-   **`src/gh_pr_phase_monitor/config.py`**: `config.toml`ファイルから設定を読み込み、パースし、アプリケーション全体で利用可能な設定オブジェクトとして提供する役割を担います。設定のバリデーションも行います。
-   **`src/gh_pr_phase_monitor/display.py`**: 監視結果、PRのフェーズ、ステータス、通知メッセージなど、アプリケーションの実行状況をターミナルに整形して表示するロジックを実装しています。
-   **`src/gh_pr_phase_monitor/github_auth.py`**: GitHub CLI (`gh`) を使用してGitHubへの認証を行い、APIアクセスに必要なトークンなどを取得・管理するモジュールです。
-   **`src/gh_pr_phase_monitor/github_client.py`**: GitHub REST APIやGraphQL APIへの高レベルなインターフェースを提供し、PR情報、リポジトリ情報、Issue情報などの取得を抽象化します。
-   **`src/gh_pr_phase_monitor/graphql_client.py`**: GitHub GraphQL APIと直接通信するための低レベルなクライアントを実装し、クエリの実行とレスポンスの処理を行います。
-   **`src/gh_pr_phase_monitor/issue_fetcher.py`**: GitHubリポジトリから特定の条件（例: `good first issue`ラベル付き、`ci-failure`ラベル付きなど）に合致するIssueを取得するロジックを実装しています。
-   **`src/gh_pr_phase_monitor/main.py`**: プロジェクトのメイン実行ループを定義し、設定の初期化、監視サイクルの開始、各モジュールの協調動作をオーケストレーションする役割を担います。
-   **`src/gh_pr_phase_monitor/monitor.py`**: 監視間隔の管理、状態変化の検出、省電力モードへの移行、監視サイクルのスケジューリングなど、PR監視の中核的なロジックを実装しています。
-   **`src/gh_pr_phase_monitor/notifier.py`**: ntfy.shサービスなどを介して、アプリケーションからモバイル端末へ通知を送信する機能を提供します。PRのURLを通知に含めることも可能です。
-   **`src/gh_pr_phase_monitor/phase_detector.py`**: プルリクエストのタイトル、ドラフト状態、レビューコメントの内容などに基づき、PRの現在のフェーズ（phase1, 2, 3, LLM working）を自動的に判定するロジックを実装しています。
-   **`src/gh_pr_phase_monitor/pr_actions.py`**: PRをレビュー可能状態にする（Draft解除）、特定のコメントを投稿する、ブラウザでPRページを開く、PRを自動マージする、Issueを自動割り当てるなど、PRに対する具体的なアクションを実行します。
-   **`src/gh_pr_phase_monitor/pr_data_recorder.py`**: PRの過去の状態（フェーズ、コメントなど）を記録し、状態変化の検出や履歴管理に利用するためのデータ永続化または一時保存ロジックを実装しています。
-   **`src/gh_pr_phase_monitor/pr_fetcher.py`**: 認証済みユーザーがアクセス可能なリポジトリから、オープンなプルリクエストのリストとその詳細情報を取得するロジックをカプセル化しています。
-   **`src/gh_pr_phase_monitor/repository_fetcher.py`**: 認証済みGitHubユーザーが所有するすべて（または指定された）のリポジトリの一覧を取得するロジックを実装しています。
-   **`src/gh_pr_phase_monitor/state_tracker.py`**: 各PRの現在のフェーズや前回監視時の状態を追跡し、変更があった場合にそれを検出する役割を担います。省電力モードの制御にも利用されます。
-   **`src/gh_pr_phase_monitor/time_utils.py`**: "1m", "5h"などの時間文字列を解析し、秒単位の数値に変換するユーティリティ関数や、時間に関連する計算を行う関数を提供します。
-   **`src/gh_pr_phase_monitor/wait_handler.py`**: APIレート制限への対応、リトライメカニズム、監視間隔の動的な調整（省電力モードなど）といった待機処理を管理します。

## 関数詳細説明
プロジェクト情報に具体的な関数シグネチャが提供されていないため、モジュールの主要な機能から推測される一般的な処理について記述します。

-   **`run_monitoring_loop()`** (src/gh_pr_phase_monitor/main.py 内に存在すると推定)
    -   役割: アプリケーションのメイン実行ループを制御し、定期的なPR監視、フェーズ判定、アクション実行をオーケストレーションします。
    -   機能: 初期設定を読み込み、GitHubクライアントを初期化し、指定された間隔でリポジトリとPRの監視サイクルを繰り返します。状態変化がない場合は省電力モードに移行し、API使用量を削減します。

-   **`fetch_user_owned_repositories()`** (src/gh_pr_phase_monitor/repository_fetcher.py 内に存在すると推定)
    -   役割: 認証済みGitHubユーザーが所有するリポジトリの一覧を取得します。
    -   機能: GitHub APIを介してユーザーの所有リポジトリをすべて取得し、監視対象のリポジトリリストを準備します。

-   **`fetch_pull_requests(repository_name)`** (src/gh_pr_phase_monitor/pr_fetcher.py 内に存在すると推定)
    -   役割: 指定されたリポジトリのオープンなプルリクエストを取得します。
    -   機能: GitHub GraphQL APIを利用して、リポジトリ内のすべてのオープンPRとその詳細情報（タイトル、ドラフト状態、コメントなど）を効率的に取得します。

-   **`detect_pr_phase(pull_request_data)`** (src/gh_pr_phase_monitor/phase_detector.py 内に存在すると推定)
    -   役割: 特定のプルリクエストの現在のフェーズ（段階）を判定します。
    -   機能: PRのドラフト状態、既存のレビューコメント、特定のキーワードなどに基づき、phase1 (Draft)、phase2 (レビュー指摘対応中)、phase3 (レビュー待ち)、LLM working (コーディングエージェント作業中) のいずれかを識別します。

-   **`execute_pr_actions(pull_request, phase, config)`** (src/gh_pr_phase_monitor/pr_actions.py 内に存在すると推定)
    -   役割: PRの現在のフェーズと設定（`rulesets`）に基づき、適切なアクションを実行します。
    -   機能: Dry-runモードの制御下で、Draft PRのReady化、Copilotへのコメント投稿、ntfy.sh経由のモバイル通知送信、Phase3 PRの自動マージ、Issueの自動割り当てなどを行います。

-   **`post_comment_to_pr(pr_id, comment_body)`** (src/gh_pr_phase_monitor/comment_manager.py 内に存在すると推定)
    -   役割: 指定されたプルリクエストにコメントを投稿します。
    -   機能: GitHub APIを通じて、エージェントのメンションや特定のフェーズに応じた定型文などをPRに自動的にコメントとして追加します。

-   **`send_mobile_notification(message, url, topic, priority)`** (src/gh_pr_phase_monitor/notifier.py 内に存在すると推定)
    -   役割: モバイルデバイスに通知を送信します。
    -   機能: ntfy.shサービスを利用して、PRがレビュー待ちになった際などに、指定されたメッセージとPRのURLを含む通知をユーザーのモバイル端末へ送信します。

-   **`perform_browser_automation(action_type, target_url, config_settings)`** (src/gh_pr_phase_monitor/browser_automation.py 内に存在すると推定)
    -   役割: ブラウザを自動的に操作し、特定のUIアクションを実行します。
    -   機能: PyAutoGUIを使用してブラウザを開き、指定されたURLにアクセスし、スクリーンショットやOCRによる画像認識でボタンを特定してクリックします。自動マージやIssueの自動割り当てに使用されます。

-   **`load_configuration(config_file_path)`** (src/gh_pr_phase_monitor/config.py 内に存在すると推定)
    -   役割: アプリケーションの設定ファイル(`config.toml`)を読み込み、解析します。
    -   機能: TOML形式の設定ファイルを読み込み、監視間隔、通知設定、自動化ルール、カラーテーマなど、アプリケーションの挙動を制御するパラメータをアプリケーションで利用可能な形式で提供します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。プロジェクト情報に具体的な関数名やその呼び出し関係に関する記述がなかったため、ハルシネーションを避けるために生成を控えました。

---
Generated at: 2026-02-13 07:05:19 JST
