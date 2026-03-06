Last updated: 2026-03-07

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト (PR) を効率的に監視するPythonツールです。
- PRのフェーズ（Draft、レビュー対応中、レビュー待ちなど）を自動判定し、通知や自動コメント投稿、Ready化、マージといった適切なアクションを実行します。
- 全ユーザー所有リポジトリを対象にGraphQL APIを活用して高速監視し、安全なDry-runモードや省電力機能も備えています。

## 技術スタック
- フロントエンド: このプロジェクトはバックエンドツールであり、直接的なフロントエンド技術は使用していません。CLIベースで動作します。
- 音楽・オーディオ: 音楽・オーディオ関連の技術は使用していません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub認証とAPIアクセスに利用されるコマンドラインツールです。
    - **Git**: ローカルリポジトリの更新チェックや自動pull機能で利用されます。
- テスト:
    - **pytest**: Pythonアプリケーションの単体テストおよび結合テストフレームワークです。
- ビルドツール: このプロジェクトはPythonスクリプトとして直接実行されるため、特定のビルドツールは使用していません。
- 言語機能:
    - **Python 3.11+**: プロジェクトの主要なプログラミング言語および実行環境です。
- 自動化・CI/CD:
    - **GraphQL API**: GitHubのデータを効率的に取得するためのAPIです。
    - **PyAutoGUI**: GUI自動化（ブラウザ操作、ボタンクリックなど）に使用されるPythonライブラリです。
    - **Pillow**: PyAutoGUIが使用する画像処理ライブラリです。
    - **PyGetWindow**: ウィンドウ管理（アクティブ化、最大化など）に使用されるPythonライブラリです。
    - **pytesseract**: OCR (光学文字認識) に使用されるPythonラッパーで、ボタン検出のフォールバックとして利用されます。
    - **tesseract-ocr**: pytesseractが依存するOCRエンジンです。
    - **ntfy.sh**: モバイル端末への通知送信サービスです。
- 開発標準:
    - **TOML**: 設定ファイル (`config.toml`) の記述形式です。
    - **Ruff**: 高速なPythonリンターおよびフォーマッターです。

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
-   **cat-github-watcher.py**: このツールのメインエントリーポイントです。アプリケーションの起動と基本的な設定読み込みを担当します。
-   **config.toml.example**: ユーザーが`config.toml`を作成する際のテンプレートとなる設定ファイルです。様々なオプションの例が記述されています。
-   **demo_automation.py**: ブラウザ自動操作機能のデモンストレーションまたはテスト用のスクリプトであると推測されます。
-   **fetch_pr_html.py**: PRのHTMLコンテンツを取得するための補助スクリプトである可能性があります。
-   **pyproject.toml**: Pythonプロジェクトのビルドシステム設定、依存関係、ツール設定などを定義する標準ファイルです。
-   **pytest.ini**: pytestテストフレームワークの設定ファイルです。
-   **requirements-automation.txt**: 自動化機能（PyAutoGUIなど）に必要なPythonライブラリのリストです。
-   **ruff.toml**: Pythonコードのリンティングとフォーマットに使用されるRuffツールの設定ファイルです。
-   **screenshots/**: ブラウザ自動操作で使用するボタンの画像認識用スクリーンショットを保存するディレクトリです。
    -   **assign.png**: "Assign"ボタンのスクリーンショット。
    -   **assign_to_copilot.png**: "Assign to Copilot"ボタンのスクリーンショット。
-   **src/gh_pr_phase_monitor/main.py**: アプリケーションの主要な実行ロジックと監視ループが含まれています。
-   **src/gh_pr_phase_monitor/colors.py**: ターミナル出力の色付けに使用するANSIカラーコードとスキームを管理します。
-   **src/gh_pr_phase_monitor/config.py**: `config.toml`からの設定を読み込み、パースし、アプリケーション全体で利用可能な設定オブジェクトとして提供します。
-   **src/gh_pr_phase_monitor/github_client.py**: GitHub APIとの基本的な連携を確立し、認証やリクエストの送信を行います。
-   **src/gh_pr_phase_monitor/phase_detector.py**: GitHub PRの現在の状態を分析し、`phase1`から`LLM working`までの定義されたフェーズのいずれかを判定するロジックを実装しています。
-   **src/gh_pr_phase_monitor/comment_manager.py**: PRへのコメント投稿、既存コメントの確認、編集などの機能を提供します。
-   **src/gh_pr_phase_monitor/actions/pr_actions.py**: PRを「Ready for review」にする、マージする、ブラウザでPRページを開くなど、PRに対する具体的なアクションを定義し実行します。
-   **src/gh_pr_phase_monitor/browser/browser_automation.py**: PyAutoGUIなどを用いてブラウザのUIを自動操作するための上位レベルの機能を提供します。
-   **src/gh_pr_phase_monitor/browser/browser_cooldown.py**: ブラウザ操作の頻度を制御し、クールダウン期間を管理することで過度な操作を防ぎます。
-   **src/gh_pr_phase_monitor/browser/button_clicker.py**: 画像認識やOCRを使用して特定のボタンを検出し、クリックする機能を提供します。
-   **src/gh_pr_phase_monitor/browser/click_config_validator.py**: ボタンクリック関連の設定（`assign_to_copilot`、`phase3_merge`など）の有効性を検証します。
-   **src/gh_pr_phase_monitor/browser/window_manager.py**: ターゲットブラウザウィンドウを管理し、必要に応じて前面に表示したり最大化したりします。
-   **src/gh_pr_phase_monitor/core/config_printer.py**: 起動時やverboseモードで、現在の設定内容をターミナルに整形して表示します。
-   **src/gh_pr_phase_monitor/core/interval_parser.py**: "30s", "1m"といった文字列形式の時間を秒数に変換する機能を持ちます。
-   **src/gh_pr_phase_monitor/core/process_utils.py**: プロセス関連のユーティリティ関数（例: gh CLIが実行中かどうかのチェックなど）を提供します。
-   **src/gh_pr_phase_monitor/core/time_utils.py**: 時間関連のユーティリティ関数（タイムスタンプの取得、経過時間の計算など）を提供します。
-   **src/gh_pr_phase_monitor/github/comment_fetcher.py**: GitHub PRからコメントを取得する機能を提供します。
-   **src/gh_pr_phase_monitor/github/github_auth.py**: GitHub CLI (`gh`) を使用して認証情報を取得・管理します。
-   **src/gh_pr_phase_monitor/github/graphql_client.py**: GitHub GraphQL APIにクエリを送信し、そのレスポンスを処理するクライアントを提供します。
-   **src/gh_pr_phase_monitor/github/issue_fetcher.py**: GitHubリポジトリからIssue情報を取得する機能を提供します。
-   **src/gh_pr_phase_monitor/github/pr_fetcher.py**: GitHubリポジトリからプルリクエストの情報を取得する機能を提供します。
-   **src/gh_pr_phase_monitor/github/rate_limit_handler.py**: GitHub APIのレート制限を検知し、適切に処理するロジックを実装します。
-   **src/gh_pr_phase_monitor/github/repository_fetcher.py**: ユーザーが所有するGitHubリポジトリの一覧を取得する機能を提供します。
-   **src/gh_pr_phase_monitor/monitor/auto_updater.py**: ツールの自己更新機能（git pullと再起動）を管理します。
-   **src/gh_pr_phase_monitor/monitor/local_repo_watcher.py**: ローカルのGitリポジトリを監視し、pull可能な更新があるかを検知します。
-   **src/gh_pr_phase_monitor/monitor/monitor.py**: メインの監視ロジックをカプセル化し、PRのフェッチ、フェーズ判定、アクション実行のサイクルを調整します。
-   **src/gh_pr_phase_monitor/monitor/pages_watcher.py**: GitHub Pagesのデプロイ状態などを監視する機能である可能性があります。
-   **src/gh_pr_phase_monitor/monitor/snapshot_markdown.py**: 監視状態のスナップショットをMarkdown形式で生成する機能です。
-   **src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py**: スナップショットファイルのパス管理ユーティリティです。
-   **src/gh_pr_phase_monitor/monitor/state_tracker.py**: 各PRやリポジトリの状態を追跡し、変更があった場合にのみアクションをトリガーする役割を担います。
-   **src/gh_pr_phase_monitor/phase/html/html_status_processor.py**: HTMLコンテンツからPRの状態や特定の情報を処理する機能です。
-   **src/gh_pr_phase_monitor/phase/html/llm_status_extractor.py**: PRのHTMLからLLM（Copilotなど）の作業状態に関する情報を抽出します。
-   **src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py**: PRページのHTMLコンテンツを解析し、フェーズ判定に必要な情報を抽出します。
-   **src/gh_pr_phase_monitor/phase/html/pr_html_fetcher.py**: PRのWebページからHTMLコンテンツを安全に取得します。
-   **src/gh_pr_phase_monitor/phase/html/pr_html_saver.py**: 取得したPRのHTMLコンテンツを保存する機能です。デバッグなどに利用されます。
-   **src/gh_pr_phase_monitor/ui/display.py**: ターミナルにPRの状態、ログ、メッセージなどを整形して表示する役割を担います。
-   **src/gh_pr_phase_monitor/ui/notification_window.py**: 自動化プロセス中に小さな通知ウィンドウを表示する機能を提供します。
-   **src/gh_pr_phase_monitor/ui/notifier.py**: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
-   **src/gh_pr_phase_monitor/ui/wait_handler.py**: 特定のイベントや条件が満たされるまで待機する機能（例: クールダウン期間の待機）を提供します。
-   **tests/**: プロジェクトのテストコードが格納されているディレクトリです。各ファイルは特定の機能のテストケースを含みます。

## 関数詳細説明
このプロジェクトは多くのモジュールに分割されており、それぞれのファイルが特定の機能を担う関数群を提供します。主要な機能とそれを担う関数の概念的な説明は以下の通りです。具体的な引数や戻り値はコードベースで詳細に定義されますが、ここではその役割を説明します。

-   **`main.py`の`run_monitor_loop()`**:
    -   **役割**: アプリケーションのメイン監視ループを実行します。設定された間隔でPR情報をフェッチし、フェーズ判定、アクション実行を繰り返します。
    -   **引数**: `config` (設定オブジェクト), `state_tracker` (PR状態追跡オブジェクト)。
    -   **戻り値**: なし。ループはユーザーが停止するまで継続。
-   **`config.py`の`load_config()`**:
    -   **役割**: `config.toml`ファイルから設定を読み込み、パースしてアプリケーション全体で使用できる設定オブジェクトを生成します。
    -   **引数**: `config_path` (設定ファイルのパス)。
    -   **戻り値**: `Config`オブジェクト。
-   **`github/pr_fetcher.py`の`fetch_pull_requests()`**:
    -   **役割**: 認証済みユーザーの所有リポジトリから全てのオープンなプルリクエスト情報をGitHub GraphQL API経由で取得します。
    -   **引数**: `graphql_client` (GraphQLクライアントインスタンス)。
    -   **戻り値**: PR情報を含むリスト。
-   **`phase_detector.py`の`detect_pr_phase()`**:
    -   **役割**: 与えられたPRの情報とHTML解析結果に基づいて、そのPRがどのフェーズ（phase1, phase2, phase3, LLM working）にあるかを判定します。
    -   **引数**: `pr_info` (PR詳細情報), `html_analyzer` (HTMLアナライザーインスタンス), `rulesets` (ルールセット設定)。
    -   **戻り値**: 判定されたフェーズを示す文字列。
-   **`actions/pr_actions.py`の`perform_pr_actions()`**:
    -   **役割**: 判定されたPRのフェーズに基づいて、コメント投稿、PRのReady化、自動マージ、ブラウザ起動、通知送信などのアクションを実行します。Dry-runモードの制御も行います。
    -   **引数**: `pr_info` (PR詳細情報), `current_phase` (現在のフェーズ), `config` (設定オブジェクト), `ruleset` (適用されるルールセット)。
    -   **戻り値**: なし。アクションを実行。
-   **`browser/button_clicker.py`の`click_button()`**:
    -   **役割**: スクリーンショットやOCRを使用して画面上の特定のボタンを検出し、自動的にクリックします。
    -   **引数**: `button_name` (ボタンの名前), `image_path` (ボタンのスクリーンショットパス), `action_name` (実行するアクション名), `config_section` (設定セクション)。
    -   **戻り値**: 成功した場合は`True`、失敗した場合は`False`。
-   **`ui/notifier.py`の`send_ntfy_notification()`**:
    -   **役割**: ntfy.shサービスを利用して、指定されたメッセージとPR情報を含むモバイル通知を送信します。
    -   **引数**: `topic` (ntfy.shトピック), `message` (通知メッセージ), `pr_url` (PRのURL), `priority` (通知優先度)。
    -   **戻り値**: なし。

## 関数呼び出し階層ツリー
```
main.py (エントリポイント)
└── gh_pr_phase_monitor.main.run_monitor_loop() (メイン監視ループ)
    ├── gh_pr_phase_monitor.monitor.auto_updater.check_and_update() (自己更新チェック)
    ├── gh_pr_phase_monitor.github.repository_fetcher.fetch_user_repositories() (リポジトリ取得)
    ├── gh_pr_phase_monitor.github.pr_fetcher.fetch_pull_requests_for_repos() (PR情報取得)
    │   └── gh_pr_phase_monitor.github.graphql_client.GraphQLClient.execute_query() (GraphQLクエリ実行)
    ├── gh_pr_phase_monitor.monitor.local_repo_watcher.watch_local_repositories() (ローカルリポジトリ監視)
    ├── gh_pr_phase_monitor.phase.phase_detector.detect_pr_phase() (PRフェーズ判定)
    │   └── gh_pr_phase_monitor.phase.html.pr_html_analyzer.PRHTMLAnalyzer.analyze_pr_html() (PR HTML解析)
    │       └── gh_pr_phase_monitor.phase.html.pr_html_fetcher.fetch_pr_html() (PR HTML取得)
    ├── gh_pr_phase_monitor.actions.pr_actions.perform_pr_actions() (PRアクション実行)
    │   ├── gh_pr_phase_monitor.github.comment_manager.post_comment() (コメント投稿)
    │   ├── gh_pr_phase_monitor.browser.browser_automation.BrowserAutomation.open_browser_for_pr() (ブラウザ起動)
    │   ├── gh_pr_phase_monitor.browser.button_clicker.ButtonClicker.click_button() (ボタンクリック)
    │   ├── gh_pr_phase_monitor.ui.notifier.send_ntfy_notification() (ntfy通知送信)
    │   └── gh_pr_phase_monitor.github.issue_fetcher.assign_issue_to_copilot() (issue自動割り当て)
    ├── gh_pr_phase_monitor.monitor.state_tracker.update_state() (状態追跡更新)
    └── gh_pr_phase_monitor.ui.display.update_display() (ターミナル表示更新)

---
Generated at: 2026-03-07 07:03:22 JST
