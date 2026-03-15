Last updated: 2026-03-16

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト（PR）のライフサイクルを監視するツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIを用いて効率的にPRの状態を追跡します。
- PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定し、状況に応じた通知や自動アクションを実行します。

## 技術スタック
- フロントエンド: CLIベースのインターフェースと、PyAutoGUIによるブラウザ自動操作でGitHubウェブUIと連携します。
- 音楽・オーディオ: 該当する技術はありません。
- 開発ツール:
    - **GitHub CLI (gh)**: GitHub API認証とインタラクションに利用されます。
    - **Pytest**: プロジェクトの単体テストおよび統合テストに利用されるテストフレームワークです。
    - **Ruff**: Pythonコードのリンティングとフォーマットに使用され、コード品質を維持します。
- テスト:
    - **Pytest**: 豊富なテスト機能とプラグインエコシステムにより、堅牢なテストスイートを構築しています。
- ビルドツール:
    - **pip**: Pythonパッケージのインストールと管理に使用されます。`requirements-automation.txt` を用いた依存関係管理が行われます。
    - **TOML**: 設定ファイル `config.toml` の形式として利用されます。
- 言語機能:
    - **Python 3.11以上**: プロジェクトの主要なプログラミング言語であり、最新の言語機能とパフォーマンスを活用しています。
- 自動化・CI/CD:
    - **GitHub Actions**: READMEの自動生成など、プロジェクトの特定のCI/CDプロセスに利用されています。
    - **ntfy.sh**: PRの重要なフェーズ（レビュー待ちなど）をモバイル端末に通知するために利用される公開型プッシュ通知サービスです。
    - **PyAutoGUI**: ブラウザの自動操作（PRのReady化、Issueの自動割り当て、PRの自動マージにおけるボタンクリックなど）を実現します。
    - **Pillow**: PyAutoGUIの画像認識機能で利用される画像処理ライブラリです。
    - **pygetwindow**: PyAutoGUIと連携し、ウィンドウの管理（アクティブ化、最大化など）を行います。
    - **pytesseract / Tesseract-OCR**: PyAutoGUIの画像認識が失敗した場合のフォールバックとして、ボタンのテキストをOCR（光学文字認識）で検出するために利用されます。
- 開発標準:
    - **.editorconfig**: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
    - **Ruff**: Pythonコードのフォーマットとリンティングを自動化し、コードの統一性と品質を保証します。

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

-   `.editorconfig`: 複数の開発者が異なるエディタを使用しても、インデントスタイルや文字コードなどの基本的なコーディングルールを統一するための設定ファイルです。
-   `.gitignore`: Gitによってバージョン管理されるべきでないファイルやディレクトリ（例: ログファイル、Pythonのバイトコード、依存関係のディレクトリ）を指定します。
-   `.vscode/settings.json`: VS Codeエディタ固有の設定ファイルで、プロジェクトのワークスペースにおける特定の挙動や拡張機能の設定を定義します。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）を記載したファイルです。
-   `README.ja.md`: プロジェクトの日本語版の概要、使い方、機能などを説明する主要なドキュメントです。
-   `README.md`: プロジェクトの英語版の概要、使い方、機能などを説明する主要なドキュメントです。
-   `_config.yml`: GitHub Pagesのサイト設定ファイルです。
-   `cat-github-watcher.py`: プロジェクトのエントリーポイントとなるスクリプトで、監視ツールを起動します。
-   `config.toml.example`: 設定ファイル `config.toml` のテンプレートです。ユーザーはこのファイルをコピーしてカスタマイズします。
-   `demo_automation.py`: 自動化機能のデモンストレーション用スクリプトです。
-   `docs/RULESETS.md`: `rulesets` 設定オプションに関する詳細な説明ドキュメントです。
-   `docs/button-detection-improvements.ja.md`: ボタン検出改善に関する日本語のドキュメントです。
-   `docs/window-activation-feature.md`: ウィンドウアクティベーション機能に関するドキュメントです。
-   `fetch_pr_html.py`: プルリクエストのHTMLコンテンツを取得するためのスクリプトです。
-   `generated-docs/`: 自動生成されたドキュメントを格納するディレクトリです。
-   `pyproject.toml`: Pythonプロジェクトのビルドシステムとプロジェクトメタデータを定義するファイルです（PoetryやFlitなどで使用）。
-   `pytest.ini`: pytestテストフレームワークの設定ファイルです。
-   `requirements-automation.txt`: ブラウザ自動化機能に必要なPythonパッケージのリストを定義します。
-   `ruff.toml`: コードリンターおよびフォーマッターであるRuffの設定ファイルです。
-   `screenshots/`: ブラウザ自動化で使用されるボタンの画像認識用スクリーンショットを格納するディレクトリです。
    -   `assign.png`: "Assign"ボタンのスクリーンショット。
    -   `assign_to_copilot.png`: "Assign to Copilot"ボタンのスクリーンショット。
-   `src/__init__.py`: Pythonパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/__init__.py`: `gh_pr_phase_monitor`パッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/actions/__init__.py`: `actions`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/actions/pr_actions.py`: プルリクエスト（PR）に対する様々なアクション（Ready化、ブラウザ起動、マージなど）を実行するロジックを実装しています。
-   `src/gh_pr_phase_monitor/browser/__init__.py`: `browser`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/browser/browser_automation.py`: PyAutoGUIなどを用いてブラウザの自動操作（画面上の要素の検出とクリック）を行うための全体的な調整ロジックが含まれています。
-   `src/gh_pr_phase_monitor/browser/browser_cooldown.py`: ブラウザ操作後に一定のクールダウン期間を設けることで、APIレート制限やシステム負荷を管理します。
-   `src/gh_pr_phase_monitor/browser/button_clicker.py`: 画像認識またはOCRを通じて特定のボタンを検出し、クリックする機能を提供します。
-   `src/gh_pr_phase_monitor/browser/click_config_validator.py`: ボタンクリック設定の正当性を検証する機能を提供します。
-   `src/gh_pr_phase_monitor/browser/window_manager.py`: ブラウザウィンドウのアクティブ化、最大化、位置調整など、ウィンドウ関連の操作を管理します。
-   `src/gh_pr_phase_monitor/core/__init__.py`: `core`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/core/colors.py`: ターミナル出力に色を付けるためのANSIカラーコードと色付け関数を定義します。
-   `src/gh_pr_phase_monitor/core/config.py`: `config.toml`ファイルから設定を読み込み、アプリケーション内で使用可能な形式に解析します。
-   `src/gh_pr_phase_monitor/core/config_printer.py`: 詳細表示（verbose）モードで、現在の設定内容を整形してターミナルに出力します。
-   `src/gh_pr_phase_monitor/core/interval_parser.py`: "1m" や "30s" といった文字列形式の監視間隔を、アプリケーションが処理できる時間単位に解析します。
-   `src/gh_pr_phase_monitor/core/process_utils.py`: プロセス関連のユーティリティ関数を提供します。
-   `src/gh_pr_phase_monitor/core/time_utils.py`: 時間計算やフォーマットなど、時間に関連するユーティリティ関数を提供します。
-   `src/gh_pr_phase_monitor/github/__init__.py`: `github`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/github/comment_fetcher.py`: GitHubのプルリクエストからコメントを取得する機能を提供します。
-   `src/gh_pr_phase_monitor/github/comment_manager.py`: プルリクエストにコメントを投稿したり、既存のコメントを管理したりする機能を提供します。
-   `src/gh_pr_phase_monitor/github/etag_checker.py`: ETagを利用してGitHub APIからのデータが変更されているかを確認し、APIリクエスト回数を削減します。
-   `src/gh_pr_phase_monitor/github/github_auth.py`: GitHub CLI (`gh`) を使用して、GitHub APIへの認証を処理します。
-   `src/gh_pr_phase_monitor/github/github_client.py`: GitHubのGraphQL APIとインタラクトするための主要なクライアント機能を提供します。
-   `src/gh_pr_phase_monitor/github/graphql_client.py`: GraphQLクエリの構築と実行を担当し、GitHub APIからデータを効率的に取得します。
-   `src/gh_pr_phase_monitor/github/issue_etag_checker.py`: Issue情報に対してETagを利用して変更をチェックする機能を提供します。
-   `src/gh_pr_phase_monitor/github/issue_fetcher.py`: GitHubリポジトリからIssue情報を取得する機能を提供します。
-   `src/gh_pr_phase_monitor/github/pr_fetcher.py`: GitHubリポジトリからプルリクエスト（PR）情報を取得する機能を提供します。
-   `src/gh_pr_phase_monitor/github/rate_limit_handler.py`: GitHub APIのレート制限情報を監視し、適切に処理することで、API利用が制限されないようにします。
-   `src/gh_pr_phase_monitor/github/repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリのリストを取得します。
-   `src/gh_pr_phase_monitor/main.py`: プロジェクトのメイン実行ループを制御し、監視、フェーズ判定、アクション実行のサイクルを調整します。
-   `src/gh_pr_phase_monitor/monitor/__init__.py`: `monitor`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/monitor/auto_updater.py`: ツール自身の自動更新（Gitリポジトリからのプルと再起動）を管理します。
-   `src/gh_pr_phase_monitor/monitor/error_logger.py`: 監視中に発生したエラーを記録し、問題のデバッグを支援します。
-   `src/gh_pr_phase_monitor/monitor/iteration_runner.py`: 監視ループの各イテレーション（繰り返し）において、必要な処理（データ取得、判定、アクション）を実行します。
-   `src/gh_pr_phase_monitor/monitor/local_repo_cargo.py`: `cargo install`コマンドを利用して、監視対象のローカルリポジトリのバイナリを自動更新する機能を提供します。
-   `src/gh_pr_phase_monitor/monitor/local_repo_checker.py`: ローカルリポジトリの状態をチェックし、GitHub上の最新の状態と比較してプル可能かどうかなどを判断します。
-   `src/gh_pr_phase_monitor/monitor/local_repo_git.py`: Gitコマンドを実行してローカルリポジトリを操作（例: `git pull`）する機能を提供します。
-   `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`: ローカルのGitHubリポジトリを監視し、自動プルや関連するアクションを実行します。
-   `src/gh_pr_phase_monitor/monitor/monitor.py`: プロジェクト全体のリポジトリ監視ロジックを統括する高レベルなモジュールです。
-   `src/gh_pr_phase_monitor/monitor/pages_watcher.py`: GitHub Pagesのデプロイ状態などを監視する機能を提供します。
-   `src/gh_pr_phase_monitor/monitor/pr_processor.py`: 各プルリクエストの情報を詳細に処理し、フェーズ判定や必要なアクションのトリガーに備えます。
-   `src/gh_pr_phase_monitor/monitor/snapshot_path_utils.py`: スナップショット（状態の保存）に関連するファイルパスを管理するユーティリティです。
-   `src/gh_pr_phase_monitor/monitor/state_tracker.py`: 監視対象のプルリクエストやリポジトリの状態変化を追跡し、変更があった場合にのみ処理を実行するための状態管理を行います。
-   `src/gh_pr_phase_monitor/phase/__init__.py`: `phase`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/phase/html/__init__.py`: `html`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/phase/html/html_status_processor.py`: PRのHTMLコンテンツから特定のステータス情報（例: LLMの作業状況）を抽出・処理します。
-   `src/gh_pr_phase_monitor/phase/html/llm_status_extractor.py`: HTMLコンテンツを解析し、LLMエージェントの作業ステータス（例: "LLM working"）を抽出します。
-   `src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py`: プルリクエストのHTMLコンテンツを解析し、詳細な情報を抽出します。
-   `src/gh_pr_phase_monitor/phase/html/pr_html_fetcher.py`: 指定されたプルリクエストのHTMLコンテンツを取得します。
-   `src/gh_pr_phase_monitor/phase/html/pr_html_saver.py`: 取得したプルリクエストのHTMLコンテンツをローカルに保存します。
-   `src/gh_pr_phase_monitor/phase/phase_detector.py`: プルリクエストの現在のフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を論理的に判定します。
-   `src/gh_pr_phase_monitor/ui/__init__.py`: `ui`サブパッケージを識別するための空ファイルです。
-   `src/gh_pr_phase_monitor/ui/display.py`: 監視結果やPRのステータスなどをターミナルに分かりやすく表示する機能を提供します。
-   `src/gh_pr_phase_monitor/ui/notification_window.py`: ブラウザ自動操作時などに、ユーザーに状況を知らせる小さな通知ウィンドウを表示します。
-   `src/gh_pr_phase_monitor/ui/notifier.py`: ntfy.shサービスを利用して、設定されたトピックにモバイル通知を送信します。
-   `src/gh_pr_phase_monitor/ui/wait_handler.py`: プログラムの実行を一時停止させ、ユーザーからの入力や特定のイベントを待機する処理を管理します。
-   `tests/`: プロジェクトのテストファイル群を格納するディレクトリです。

## 関数詳細説明

具体的な関数シグネチャは提供されていませんが、各モジュールの役割から推測される主要な関数の役割を説明します。

-   **`main` 実行関連**:
    -   `run_monitor()`: メイン監視ループを起動し、定期的なPRチェックとアクション実行を調整します。
    -   `load_config(config_path)`: 指定されたパスから設定ファイル（`config.toml`）を読み込み、解析して設定オブジェクトを返します。
-   **GitHub API関連**:
    -   `fetch_repositories()`: 認証済みユーザーの所有する全リポジトリのリストをGitHub APIから取得します。
    -   `fetch_pull_requests(repository_name)`: 特定のリポジトリのオープンなプルリクエスト情報をGitHub APIから取得します。
    -   `post_comment(pr_id, comment_body)`: 指定されたプルリクエストにコメントを投稿します。
    -   `mark_pr_as_ready(pr_id)`: ドラフト状態のプルリクエストを「レビュー準備完了」状態に変更します。
    -   `merge_pull_request(pr_id, merge_message)`: 指定されたプルリクエストをマージします。
    -   `check_etag(url, etag)`: ETagを使用して、指定されたURLのリソースが前回取得時から変更されたかを確認します。
-   **フェーズ判定関連**:
    -   `detect_pr_phase(pr_info)`: プルリクエストの現在の状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を判定し、フェーズを返します。
    -   `is_draft(pr_info)`: プルリクエストがドラフト状態かどうかを判定します。
    -   `has_unresolved_comments(pr_info)`: 未解決のレビューコメントがあるかどうかを判定します。
    -   `is_llm_working(pr_info)`: コーディングエージェント（LLM）が作業中であると判定される条件を満たすか確認します。
-   **アクション実行関連**:
    -   `perform_pr_actions(pr_info, current_phase, ruleset_config)`: プルリクエストのフェーズと設定に基づいて、コメント投稿、通知送信、PRのReady化、マージなどのアクションを実行します。
    -   `send_notification(message, url)`: ntfy.sh経由でモバイル通知を送信します。
    -   `open_browser(url)`: 指定されたURLをデフォルトブラウザで開きます。
-   **ブラウザ自動操作関連**:
    -   `click_button_by_screenshot(image_path, confidence)`: スクリーンショット画像に基づいて画面上のボタンを検出し、クリックします。
    -   `click_button_by_ocr(text_to_find)`: OCRを使用して画面上の特定のテキストを検出し、クリックします。
    -   `activate_browser_window(title_or_process_name)`: 指定されたブラウザウィンドウをアクティブ化（前面に表示）します。
-   **ローカルリポジトリ監視関連**:
    -   `check_local_repositories(base_dir)`: 指定されたベースディレクトリ以下のローカルリポジトリをスキャンし、GitHub上の状態と比較して同期状態を確認します。
    -   `git_pull_repository(repo_path)`: 指定されたパスのローカルリポジトリで `git pull` を実行します。
    -   `cargo_install_force(repo_name)`: 指定されたリポジトリに対して `cargo install --force` を実行し、バイナリを更新します。
-   **ユーティリティ関連**:
    -   `parse_interval_string(interval_str)`: "1m" や "30s" のような間隔文字列を秒数に変換します。
    -   `log_error(error_message)`: エラーメッセージをログに記録します。
    -   `print_colored_message(message, color_code)`: 指定された色でメッセージをターミナルに表示します。

## 関数呼び出し階層ツリー
```
[関数間の呼び出し関係をツリー形式で表現]

---
Generated at: 2026-03-16 07:03:22 JST
