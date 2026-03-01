Last updated: 2026-03-02

# Project Overview

## プロジェクト概要
- GitHub CopilotなどAIエージェントによる自動実装のプルリクエスト(PR)監視に特化したPythonツールです。
- 認証済みユーザーの全リポジトリを対象に、PRの進捗フェーズを自動検知し、適切な通知やアクションを実行します。
- GraphQL APIによる効率的な監視と、Dry-runモードや自動更新などの豊富な機能で開発フローを支援します。

## 技術スタック
- フロントエンド: PyAutoGUI (ブラウザ自動操作), Pillow (画像処理), PyGetWindow (ウィンドウ管理), Pytesseract (OCRによるテキスト検出), Tesseract-OCR (OCRエンジン)
- 音楽・オーディオ: 該当なし
- 開発ツール: GitHub CLI (`gh`コマンドラインツール), Git (バージョン管理システム), pytest (テストフレームワーク)
- テスト: pytest (Python向けテストフレームワーク)
- ビルドツール: Python (実行環境), pip (パッケージ管理。特定のビルドツールは使用せず、Python標準の実行環境で動作)
- 言語機能: Python 3.10以上 (主要開発言語)
- 自動化・CI/CD: ntfy.sh (モバイル通知サービス), 自己更新機能 (Gitベースの自動アップデート), ブラウザ自動化 (PRマージ、Issue割り当て)
- 開発標準: Ruff (Pythonコードリンター・フォーマッター), EditorConfig (コードスタイル定義)

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
- **`.editorconfig`**: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイル。
- **`.gitignore`**: Gitがバージョン管理の対象としないファイルやディレクトリを指定するファイル。
- **`.vscode/settings.json`**: Visual Studio Codeのワークスペース固有の設定ファイル。
- **`LICENSE`**: このプロジェクトのライセンス情報（MIT License）を記載したファイル。
- **`MERGE_CONFIGURATION_EXAMPLES.md`**: 自動マージ機能の設定例を説明するドキュメント。
- **`PHASE3_MERGE_IMPLEMENTATION.md`**: Phase3マージ機能の実装詳細に関するドキュメント。
- **`README.ja.md`**: プロジェクトの日本語版READMEファイル。
- **`README.md`**: プロジェクトの英語版READMEファイル。
- **`STRUCTURE.md`**: プロジェクトのアーキテクチャや構造に関するドキュメント。
- **`_config.yml`**: GitHub Pagesなどのサイト設定に使われる可能性のある設定ファイル。
- **`cat-github-watcher.py`**: プログラムのメインエントリーポイントとなるスクリプト。
- **`config.toml.example`**: ユーザーが`config.toml`を作成する際のテンプレートとなる設定ファイルの例。
- **`demo_automation.py`**: 自動化機能のデモンストレーション用スクリプト。
- **`docs/`**: プロジェクトに関する追加ドキュメントを格納するディレクトリ。
    - **`RULESETS.md`**: 設定ファイルにおけるルールセットの定義と使用方法に関するドキュメント。
    - **`button-detection-improvements.ja.md`**: ボタン検出改善に関する日本語ドキュメント。
    - **`window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメント。
- **`generated-docs/`**: 自動生成されたドキュメントを格納するディレクトリ（もしあれば）。
- **`pytest.ini`**: pytestのテスト設定ファイル。
- **`requirements-automation.txt`**: 自動化機能に必要なPythonパッケージのリスト。
- **`ruff.toml`**: Pythonのリンター/フォーマッターであるRuffの設定ファイル。
- **`screenshots/`**: ブラウザ自動操作で使用するボタンのスクリーンショット画像を格納するディレクトリ。
    - **`assign.png`**: "Assign"ボタンのスクリーンショット。
    - **`assign_to_copilot.png`**: "Assign to Copilot"ボタンのスクリーンショット。
- **`src/`**: プロジェクトの主要なソースコードを格納するディレクトリ。
    - **`__init__.py`**: Pythonパッケージとして認識させるためのファイル。
    - **`gh_pr_phase_monitor/`**: PR監視ロジックの中核をなすパッケージ。
        - **`auto_updater.py`**: アプリケーション自身の自動更新ロジックを管理するファイル。
        - **`browser_automation.py`**: PyAutoGUIなどを用いたブラウザ操作の共通ロジックを定義するファイル。
        - **`browser_cooldown.py`**: ブラウザ自動操作後に一定時間待機するクールダウン処理を管理するファイル。
        - **`button_clicker.py`**: 画像認識やOCRを駆使してブラウザ上の特定のボタンをクリックする機能を提供するファイル。
        - **`colors.py`**: ターミナル出力の色付けに使用するANSIカラーコードと関連ユーティリティを定義するファイル。
        - **`comment_fetcher.py`**: GitHubのプルリクエストコメントを取得するためのロジックを格納するファイル。
        - **`comment_manager.py`**: プルリクエストへのコメント投稿や管理を行うファイル。
        - **`config.py`**: `config.toml`から設定を読み込み、解析し、プログラム全体で利用可能な形式にするファイル。
        - **`config_printer.py`**: verboseモードで現在の設定情報をターミナルに出力する機能を提供するファイル。
        - **`display.py`**: ターミナルに監視状況やPRの状態を表示するためのユーティリティ関数を集めたファイル。
        - **`github_auth.py`**: GitHub CLI (`gh`) を利用した認証プロセスを管理するファイル。
        - **`github_client.py`**: GitHubのGraphQL APIと連携し、高レベルなリクエストを処理するクライアント。
        - **`graphql_client.py`**: 低レベルなGraphQL APIリクエストの送信を担当するファイル。
        - **`interval_parser.py`**: "30s", "1m"のような文字列で指定された時間間隔を解析するファイル。
        - **`issue_fetcher.py`**: GitHub Issueの情報を取得するロジックを格納するファイル。
        - **`llm_status_extractor.py`**: PRコメントからLLM（大規模言語モデル）の作業状況（例: "LLM working"）を抽出するファイル。
        - **`local_repo_watcher.py`**: ローカルのGitリポジトリを監視し、`git pull`が必要な場合に通知または自動実行する機能を提供するファイル。
        - **`main.py`**: `gh_pr_phase_monitor`パッケージの主要な実行ロジックと監視ループを定義するファイル。
        - **`monitor.py`**: GitHubリポジトリとPRの監視、フェーズ判定、アクション実行の中心的な調整を行うファイル。
        - **`notification_window.py`**: ブラウザ自動操作中に画面に一時的に表示される通知ウィンドウを管理するファイル。
        - **`notifier.py`**: ntfy.shサービスを利用してモバイル通知を送信する機能を提供するファイル。
        - **`pages_watcher.py`**: GitHub Pagesのデプロイ状況などを監視する機能を提供するファイル。
        - **`phase_detector.py`**: プルリクエストの現在のフェーズ（phase1, phase2, phase3, LLM working）を判定するコアロジックを格納するファイル。
        - **`pr_actions.py`**: プルリクエストに対する様々なアクション（Ready化、ブラウザ起動、マージなど）を実行するファイル。
        - **`pr_data_recorder.py`**: PRデータを記録し、スナップショットなどの形式で保存するファイル。
        - **`pr_fetcher.py`**: GitHubからプルリクエストのリストとその詳細情報を取得するロジックを格納するファイル。
        - **`pr_html_fetcher.py`**: プルリクエストページのHTMLコンテンツを取得するファイル（ブラウザ自動操作の補助など）。
        - **`process_utils.py`**: プロセス管理に関するユーティリティ関数を集めたファイル。
        - **`repository_fetcher.py`**: 認証済みユーザーが所有するGitHubリポジトリのリストを取得するファイル。
        - **`snapshot_markdown.py`**: PRデータのスナップショットをMarkdown形式で生成するファイル。
        - **`snapshot_path_utils.py`**: スナップショットファイルやディレクトリのパス管理ユーティリティ。
        - **`state_tracker.py`**: PRの監視状態を追跡し、変更がない場合の省電力モード移行などを管理するファイル。
        - **`time_utils.py`**: 時間計算やフォーマットに関するユーティリティ関数。
        - **`wait_handler.py`**: 非同期処理や指定された待機時間を処理するためのハンドラ。
        - **`window_manager.py`**: オペレーティングシステム上のウィンドウを操作（アクティブ化、最大化など）する機能を提供するファイル。
- **`tests/`**: プロジェクトのユニットテストおよび結合テストを格納するディレクトリ。
    - **`test_*.py`**: 各機能に対応するテストスクリプト。

## 関数詳細説明
- **`main()`** (src/gh_pr_phase_monitor/main.py):
    - **役割**: プログラムのエントリーポイントとして、設定の読み込み、GitHubクライアントの初期化、そして中心となるPR監視ループの開始を調整します。
    - **引数**: なし (または設定ファイルのパスなど)
    - **戻り値**: なし
    - **機能**: プログラムの実行フローを制御し、各モジュールの初期化と連携を行います。
- **`monitor_prs()`** (src/gh_pr_phase_monitor/monitor.py):
    - **役割**: GitHubリポジトリ内のプルリクエストを定期的に監視する主要なループを実装します。
    - **引数**: 設定オブジェクト、GitHubクライアント、状態トラッカーなど
    - **戻り値**: なし
    - **機能**: リポジトリとPRのフェッチ、各PRのフェーズ判定、そしてそのフェーズに応じたアクションの実行を調整します。
- **`detect_phase()`** (src/gh_pr_phase_monitor/phase_detector.py):
    - **役割**: 与えられたプルリクエストの現在の状態（ドラフト、レビューコメントの有無、特定のコメントの存在など）に基づいて、そのPRがどのフェーズ（phase1, phase2, phase3, LLM working）にあるかを判定します。
    - **引数**: プルリクエストデータ、関連するコメント情報など
    - **戻り値**: 判定されたフェーズを示す文字列
    - **機能**: 複雑なルールと条件に基づいてPRの進行状況を分類します。
- **`perform_pr_actions()`** (src/gh_pr_phase_monitor/pr_actions.py):
    - **役割**: 特定のプルリクエストが特定のフェーズに達した際に、設定に基づいて定義されたアクション（PRをReady状態にする、コメントを投稿する、通知を送信する、マージする、ブラウザでPRを開くなど）を実行します。Dry-runモードの制御も行います。
    - **引数**: プルリクエストデータ、現在のフェーズ、設定オブジェクト、GitHubクライアントなど
    - **戻り値**: 実行されたアクションの結果
    - **機能**: フェーズ判定結果に基づき、PRのライフサイクルを自動化します。
- **`send_notification()`** (src/gh_pr_phase_monitor/notifier.py):
    - **役割**: ntfy.shサービスを利用して、指定されたメッセージとPR URLを含むモバイル通知を送信します。
    - **引数**: メッセージ、URL、トピック、優先度など
    - **戻り値**: なし
    - **機能**: PRの状態変化（特にレビュー待ち）をユーザーのモバイルデバイスに通知します。
- **`post_comment()`** (src/gh_pr_phase_monitor/comment_manager.py):
    - **役割**: 指定されたプルリクエストに、特定のコーディングエージェント（例: `@codex[agent]`, `@copilot`）をメンションしたコメントを投稿します。
    - **引数**: リポジトリID、PR番号、コメント本文、エージェント名など
    - **戻り値**: 投稿されたコメントのIDなど
    - **機能**: AIエージェントへの指示やフィードバックを自動でPRにコメントします。
- **`click_button()`** (src/gh_pr_phase_monitor/button_clicker.py):
    - **役割**: PyAutoGUIと画像認識（またはOCR）を使用して、ブラウザ画面上の特定のボタン（例: "Merge pull request", "Assign to Copilot"）を特定し、クリックします。
    - **引数**: ボタン画像ファイルパス、OCRテキスト、信頼度、タイムアウトなど
    - **戻り値**: 成功/失敗を示すブール値
    - **機能**: GitHubウェブUI上の操作を自動化し、自動マージやIssue割り当てを実現します。
- **`fetch_repositories()`** (src/gh_pr_phase_monitor/repository_fetcher.py):
    - **役割**: 認証済みGitHubユーザーが所有するリポジトリのリストをGitHub GraphQL API経由で取得します。
    - **引数**: GitHubクライアント
    - **戻り値**: リポジトリのリスト
    - **機能**: 監視対象となるリポジトリを動的に取得します。
- **`fetch_prs()`** (src/gh_pr_phase_monitor/pr_fetcher.py):
    - **役割**: 指定されたリポジトリのオープンなプルリクエストのリストとその詳細情報をGitHub GraphQL API経由で取得します。
    - **引数**: リポジトリID、GitHubクライアント
    - **戻り値**: プルリクエストのリストと関連データ
    - **機能**: 各PRの最新の状態を把握するための基本データを提供します。
- **`fetch_issues()`** (src/gh_pr_phase_monitor/issue_fetcher.py):
    - **役割**: 特定の基準（例: "good first issue" ラベル、"ci-failure" ラベル）に合致するGitHub Issueを取得します。
    - **引数**: リポジトリID、GitHubクライアント、ラベル、表示上限数など
    - **戻り値**: 関連するIssueのリスト
    - **機能**: コーディングエージェントに割り当てるべきIssueを特定します。
- **`auto_update()`** (src/gh_pr_phase_monitor/auto_updater.py):
    - **役割**: 自身のGitリポジトリ（`cat-github-watcher`）の更新を定期的に検知し、作業ツリーがクリーンでfast-forward可能な場合に自動で`git pull`を実行し、プロセスを再起動します。
    - **引数**: 設定オブジェクト
    - **戻り値**: なし
    - **機能**: ツール自身を最新の状態に保ちます。
- **`auto_git_pull()`** (src/gh_pr_phase_monitor/local_repo_watcher.py):
    - **役割**: 親ディレクトリ内にあるローカルGitリポジトリを監視し、リモートに変更があり`git pull`が可能と判断された場合に、そのリポジトリを自動でpullします（Dry-runモードもサポート）。
    - **引数**: ベースディレクトリ、設定オブジェクト
    - **戻り値**: なし
    - **機能**: ローカル開発環境のリポジトリを常に最新の状態に同期します。
- **`load_config()`** (src/gh_pr_phase_monitor/config.py):
    - **役割**: TOML形式の設定ファイルを読み込み、プログラム全体で使用する設定オブジェクトを生成します。デフォルト値の適用や、環境変数からの上書きも処理します。
    - **引数**: 設定ファイルのパス
    - **戻り値**: 解析された設定オブジェクト
    - **機能**: ユーザー定義の設定をプログラムに適用します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。

---
Generated at: 2026-03-02 07:01:51 JST
