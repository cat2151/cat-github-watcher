Last updated: 2026-04-07

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト (PR) を効率的に監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定します。
- フェーズに応じたコメント投稿、PRのReady化、モバイル通知、自動マージ、issue自動割り当てなどのアクションを実行可能です。

## 技術スタック
- フロントエンド: （本プロジェクトはCLIツールであり、専用のフロントエンド技術は使用していません。ただし、PyAutoGUIを用いたブラウザ自動操作機能は含まれます。）
- 音楽・オーディオ: 本プロジェクトでは音楽・オーディオ関連の技術は使用していません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub認証およびAPIアクセスに使用されます。
    - **PyAutoGUI, Pillow, PyGetWindow**: ブラウザの自動操作（ボタンクリック、ウィンドウ管理）に利用されます。
    - **pytesseract, tesseract-ocr**: ブラウザ自動操作時のOCR（光学文字認識）フォールバックに使用されます。
- テスト:
    - **pytest**: プロジェクトのテストスイートを実行するためのフレームワークです。
- ビルドツール:
    - **cargo install**: Rustベースのリポジトリを監視対象とする場合に、そのバイナリを自動更新するために使用されます。
- 言語機能:
    - **Python 3.11以上**: プロジェクトの主要な開発言語です。
    - **GraphQL API**: GitHubのPRおよびリポジトリ情報を効率的に取得するために使用されます。
- 自動化・CI/CD:
    - **ntfy.sh**: フェーズ3（レビュー待ち）のPRを検知した際にモバイル通知を送信するために使用されます。
    - **Git pull**: ローカルリポジトリの自動更新機能に利用されます。
- 開発標準:
    - **.editorconfig**: 複数のエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
    - **ruff**: Pythonコードのリンティングおよびフォーマットを行う高速なツールです。

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
- **`.editorconfig`**: コードエディタ間でインデントスタイルや文字コードなどの基本的な書式設定を統一するためのファイルです。
- **`.gitignore`**: Gitが追跡しないファイルやディレクトリを指定するファイルです。
- **`.vscode/settings.json`**: Visual Studio Code用のワークスペース固有の設定ファイルで、プロジェクトの推奨設定を定義します。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記載したファイルです。
- **`README.ja.md` / `README.md`**: プロジェクトの概要、機能、使い方などを説明するドキュメント（日本語版と英語版）です。
- **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレーターで利用される設定ファイルです。
- **`cat-github-watcher.py`**: プロジェクトの主要なエントリーポイントとなるPythonスクリプトです。
- **`config.toml.example`**: ユーザーがコピーして編集するための設定ファイル（TOML形式）のテンプレートです。
- **`demo_automation.py`**: 自動化機能のデモンストレーション用スクリプトです。
- **`docs/`**: プロジェクトに関する追加ドキュメントが格納されています。
    - **`RULESETS.md`**: ルールセットの設定方法に関するドキュメント。
    - **`button-detection-improvements.ja.md`**: ボタン検出改善に関する日本語ドキュメント。
    - **`window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメント。
- **`fetch_pr_html.py`**: PRのHTMLコンテンツを取得するための補助スクリプトです。
- **`generated-docs/`**: 自動生成されたドキュメントが格納されるディレクトリです。
- **`pyproject.toml`**: Pythonプロジェクトのビルドシステムや依存関係を定義する標準ファイルです。
- **`pytest.ini`**: pytestテストフレームワークの設定ファイルです。
- **`requirements-automation.txt`**: ブラウザ自動化機能に必要なPythonライブラリのリストです。
- **`ruff.toml`**: ruffリンターおよびフォーマッターの設定ファイルです。
- **`screenshots/`**: ブラウザ自動化機能で使用するボタンのスクリーンショット画像が保存されます。
    - **`assign.png`**: "Assign" ボタンのスクリーンショット。
    - **`assign_to_copilot.png`**: "Assign to Copilot" ボタンのスクリーンショット。
- **`src/`**: プロジェクトの主要なソースコードが格納されているディレクトリです。
    - **`__init__.py`**: Pythonパッケージとして認識させるためのファイルです。
    - **`gh_pr_phase_monitor/`**: プロジェクトのコアロジックを含むPythonパッケージです。
        - **`actions/`**: PRに対する具体的なアクションを定義するモジュール群です。
            - **`pr_actions.py`**: PRをReady状態にしたり、ブラウザを開いたりするアクションを実装しています。
        - **`browser/`**: ブラウザの自動操作に関連するモジュール群です。
            - **`browser_automation.py`**: ブラウザ自動操作の全体を制御します。
            - **`button_clicker.py`**: 画像認識やOCRを用いて画面上のボタンをクリックするロジックを実装します。
            - **`issue_assigner.py`**: GitHub IssueをCopilotに自動割り当てする処理を実装します。
            - **`window_manager.py`**: ウィンドウの管理（アクティブ化、最大化など）を行います。
        - **`core/`**: プロジェクトの基本的なコア機能を提供するモジュール群です。
            - **`colors.py`**: ターミナル出力の色付けに使用されるANSIカラーコードを定義します。
            - **`config.py`**: `config.toml`ファイルから設定を読み込み、解析します。
            - **`interval_parser.py`**: 時間間隔の文字列を解析するユーティリティです。
            - **`time_utils.py`**: 時間関連のユーティリティ関数を提供します。
        - **`github/`**: GitHub APIとの連携を担当するモジュール群です。
            - **`github_client.py`**: GitHub GraphQL APIとの主要なインターフェースを提供します。
            - **`graphql_client.py`**: GraphQLクエリの実行とレート制限のハンドリングを行います。
            - **`pr_fetcher.py`**: PR情報を取得するロジックが含まれます。
            - **`comment_manager.py`**: PRへのコメント投稿や既存コメントの確認を行います。
            - **`repository_fetcher.py`**: 監視対象のリポジトリ情報を取得します。
        - **`main.py`**: プロジェクトのメイン実行ループと監視ロジックが含まれています。
        - **`monitor/`**: 監視ループの実行、リポジトリの状態追跡、自動更新などを管理するモジュール群です。
            - **`monitor.py`**: 監視の全体フローと状態管理を担います。
            - **`auto_updater.py`**: ツールの自己更新ロジックを管理します。
            - **`local_repo_watcher.py`**: ローカルリポジトリの変更を監視し、自動で`git pull`を実行します。
            - **`pr_processor.py`**: 取得したPRを処理し、フェーズ判定やアクションをトリガーします。
        - **`phase/`**: PRのフェーズを判定するロジックを含むモジュール群です。
            - **`phase_detector.py`**: PRの現在の状態に基づいてフェーズ（phase1, phase2, phase3, LLM working）を判定します。
            - **`html/`**: PRのHTMLコンテンツを解析してLLMの状態などを検出します。
                - **`pr_html_analyzer.py`**: PRのHTMLを解析し、特定の情報（LLMのステータスなど）を抽出します。
        - **`ui/`**: ユーザーインターフェース（コンソール表示、通知）を管理するモジュール群です。
            - **`display.py`**: 監視結果をターミナルに整形して表示します。
            - **`notifier.py`**: ntfy.shを介してモバイル通知を送信します。
            - **`notification_window.py`**: 自動操作中に小さな通知ウィンドウを表示します。
- **`tests/`**: プロジェクトの各モジュールおよび機能に対するテストコードが格納されています。

## 関数詳細説明
このプロジェクト情報では、個々の関数の具体的な名前、引数、戻り値、機能に関する詳細な説明は提供されていません。そのため、具体的な関数詳細を生成することはできません。

## 関数呼び出し階層ツリー
```
（関数呼び出し階層は分析できませんでした）

---
Generated at: 2026-04-07 07:07:05 JST
