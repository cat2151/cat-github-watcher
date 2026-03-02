Last updated: 2026-03-03

# Project Overview

## プロジェクト概要
- GitHub CopilotなどAIエージェントによる自動実装のプルリクエスト（PR）フェーズを効率的に監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIを用いてPRの状態を判定し、適切な通知やアクションを自動実行します。
- ドライランモード、モバイル通知、自動コメント、Draft PRのReady化、PRマージ、そしてローカルリポジトリの自動同期など、豊富な自動化機能を柔軟に設定可能です。

## 技術スタック
- フロントエンド: PyAutoGUI (ブラウザUI自動操作), Pillow (画像処理), PyGetWindow (ウィンドウ操作), pytesseract (OCRフォールバック) - これらを通じてGitHub Web UIを操作します。
- 音楽・オーディオ: (該当する技術は使用されていません)
- 開発ツール: Python 3.10+ (主要な開発言語および実行環境), GitHub CLI (`gh`, GitHub認証および一部操作に利用), pytest (テストフレームワーク), ruff (コードリンター/フォーマッター)。
- テスト: pytest (Pythonコードの単体テストおよび統合テストに使用)。
- ビルドツール: Python (スクリプトとして直接実行されるため、別途ビルドツールは使用していません)。
- 言語機能: Python (Python言語の標準機能とライブラリを活用)。
- 自動化・CI/CD: GitHub Actions (ドキュメント生成やテスト自動化に利用。本プロジェクトの主要機能として、自己更新、PRの自動コメント投稿、Draft PRのReady化、自動マージ、Issue自動割り当て、ローカルリポジトリの自動`git pull`といった運用自動化機能を提供します)。
- 開発標準: .editorconfig (エディタの設定統一), ruff (コードスタイルと品質の維持), STRUCTURE.md (プロジェクトのアーキテクチャ説明)。

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
-   `.editorconfig`: さまざまなエディタやIDE間で一貫したコーディングスタイルを定義する設定ファイル。
-   `.gitignore`: Gitが追跡しないファイルやディレクトリを指定するファイル。
-   `.vscode/settings.json`: Visual Studio Codeのワークスペース設定ファイル。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）を記載したファイル。
-   `MERGE_CONFIGURATION_EXAMPLES.md`: PR自動マージ機能の設定例と使い方を説明するドキュメント。
-   `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3自動マージ機能の実装詳細に関するドキュメント。
-   `README.ja.md`: プロジェクトの概要、機能、使い方などを日本語で説明するメインのドキュメント。
-   `README.md`: プロジェクトの概要、機能、使い方などを英語で説明するメインのドキュメント（`README.ja.md`の翻訳）。
-   `STRUCTURE.md`: プロジェクトのアーキテクチャとディレクトリ構成について説明するドキュメント。
-   `_config.yml`: GitHub Pagesなどの静的サイトジェネレータで使われる設定ファイル（本プロジェクトのドキュメント用か）。
-   `cat-github-watcher.py`: プロジェクトのメインエントリーポイントとなるスクリプト。
-   `config.toml.example`: 設定ファイル`config.toml`のサンプル。ユーザーはこれをコピーして独自の設定を行う。
-   `demo_automation.py`: 自動化機能のデモンストレーション用スクリプト。
-   `docs/`: プロジェクトの追加ドキュメントを格納するディレクトリ。
    -   `RULESETS.md`: ルールセット設定の詳細を説明するドキュメント。
    -   `button-detection-improvements.ja.md`: ボタン検出機能の改善に関する日本語ドキュメント。
    -   `window-activation-feature.md`: ウィンドウアクティベーション機能に関するドキュメント。
-   `generated-docs/`: AIエージェントなどによって自動生成されたドキュメントを格納するディレクトリ。
-   `pytest.ini`: pytestの設定ファイル。
-   `requirements-automation.txt`: 自動化機能に必要なPythonパッケージとそのバージョンを記述したファイル。
-   `ruff.toml`: コードリンター/フォーマッターである`ruff`の設定ファイル。
-   `screenshots/`: ブラウザ自動操作のためのボタン画像スクリーンショットを格納するディレクトリ。
    -   `assign.png`: "Assign"ボタンのスクリーンショット。
    -   `assign_to_copilot.png`: "Assign to Copilot"ボタンのスクリーンショット。
-   `src/`: プロジェクトの主要なソースコードを格納するディレクトリ。
    -   `__init__.py`: Pythonパッケージの初期化ファイル。
    -   `gh_pr_phase_monitor/`: PR監視ロジックと関連モジュールを格納する主要なパッケージ。
        -   `__init__.py`: `gh_pr_phase_monitor`パッケージの初期化ファイル。
        -   `auto_updater.py`: プロジェクト自身をGitHubから自動更新（`git pull`）する機能を提供。
        -   `browser_automation.py`: PyAutoGUIなどを用いてブラウザのUIを自動操作する汎用機能。
        -   `browser_cooldown.py`: ブラウザ操作間の待機時間を管理し、APIレート制限などを考慮したクールダウン処理。
        -   `button_clicker.py`: 画像認識やOCRを用いて特定のボタン（例: マージボタン）を検出し、クリックするロジック。
        -   `click_config_validator.py`: ボタンクリック自動化に関する設定値の検証を行う。
        -   `colors.py`: ターミナル出力の色付けに使用されるANSIカラーコードと色付け関数。
        -   `comment_fetcher.py`: GitHub GraphQL APIを介してPRのコメントを取得する機能。
        -   `comment_manager.py`: PRへの自動コメント投稿、コメントの更新、特定のコメントの存在確認などを管理。
        -   `config.py`: `config.toml`ファイルから設定を読み込み、アプリケーション全体で利用可能な形で管理する。
        -   `config_printer.py`: 起動時や実行中に現在の設定情報を詳細にターミナルに表示する機能。
        -   `display.py`: PRリスト、フェーズ、ステータス、レート制限情報など、各種情報を整形してターミナルに出力する。
        -   `github_auth.py`: GitHub CLI (`gh`) を利用したGitHub認証プロセスの管理。
        -   `github_client.py`: GitHub REST APIエンドポイントへの高レベルなクライアントインターフェース。
        -   `graphql_client.py`: GitHub GraphQL APIへのクエリ実行を担い、効率的なデータ取得を実現。
        -   `interval_parser.py`: "1m", "30s"などの文字列形式の時間間隔をパースして秒数に変換する。
        -   `issue_fetcher.py`: GitHub GraphQL APIを介してIssue情報を取得する機能。
        -   `llm_status_extractor.py`: PRのタイトルや本文、コメントからLLM（AIエージェント）の作業状態を抽出・判定する。
        -   `local_repo_watcher.py`: ローカルに存在するGitリポジトリの状態を監視し、自動`git pull`を検知・実行。
        -   `main.py`: アプリケーションのメイン実行ループと、PR監視、フェーズ判定、アクション実行の全体的なフローを管理。
        -   `monitor.py`: GitHubのPRを定期的に監視し、状態変化を検知して適切なアクションをトリガーする。
        -   `notification_window.py`: 自動ブラウザ操作中にユーザーに状況を知らせるための小さなデスクトップ通知ウィンドウを管理。
        -   `notifier.py`: ntfy.shサービスを利用して、モバイル端末へプッシュ通知を送信する機能。
        -   `pages_watcher.py`: GitHub Pagesのデプロイステータスなどを監視する機能。
        -   `phase_detector.py`: PRの現在の状態（ドラフト、レビュー指摘対応中、レビュー待ち、LLM作業中など）を詳細なロジックに基づいて判定。
        -   `pr_actions.py`: PRに対する具体的なアクション（Draft PRをReadyにする、コメントを投稿する、PRをマージするなど）を実行する。
        -   `pr_data_recorder.py`: PRのデータや状態をスナップショットとして記録し、デバッグや履歴管理に利用。
        -   `pr_fetcher.py`: GitHub GraphQL APIを使用して、指定されたリポジトリまたはユーザーのPR情報を取得する。
        -   `pr_html_fetcher.py`: PRページのHTMLコンテンツを取得し、ブラウザ自動操作やOCRの補助に利用。
        -   `process_utils.py`: システムプロセスに関するユーティリティ関数（例: プロセスの起動、状態確認）。
        -   `repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリのリストを取得する。
        -   `snapshot_markdown.py`: PRデータのスナップショットからMarkdown形式のドキュメントを生成する。
        -   `snapshot_path_utils.py`: スナップショットファイルのパスを管理するユーティリティ。
        -   `state_tracker.py`: 各PRの状態や全体の監視状態を追跡し、省電力モードへの移行などを判断する。
        -   `time_utils.py`: 時間関連のユーティリティ関数（例: 期間のパース、時刻のフォーマット）。
        -   `wait_handler.py`: 非同期処理やUI操作における適切な待機時間を管理し、イベント駆動の応答性を保つ。
        -   `window_manager.py`: ブラウザウィンドウの操作（アクティブ化、最大化など）を管理。
-   `tests/`: プロジェクトのテストスクリプトを格納するディレクトリ。各`test_*.py`ファイルは対応するモジュールや機能のテストを含んでいます。

## 関数詳細説明
このプロジェクトは、単一責任の原則に従ってモジュール化されており、各モジュールが特定の役割を果たす関数群を提供します。具体的な関数名、引数、戻り値の詳細は提供されていませんが、各モジュールが提供する主要な機能は以下の通りです。

-   `auto_updater.py`: 自身のGitHubリポジトリの更新を確認し、`git pull`による自動更新と再起動を管理する関数。
-   `browser_automation.py`: PyAutoGUIやその他のライブラリを使用して、ウェブブラウザのUIを自動的に操作（例: ページを開く、要素を探す）する関数。
-   `browser_cooldown.py`: ブラウザ操作後の待機時間を設定し、過度な操作を防ぐためのクールダウンを管理する関数。
-   `button_clicker.py`: スクリーンショットやOCRに基づいて、特定のボタン（例: "Merge pull request", "Assign to Copilot"）を検出し、クリックする関数。
-   `click_config_validator.py`: ボタンクリック自動化に関連する設定値の妥当性を検証する関数。
-   `colors.py`: ターミナル出力にANSIカラーコードを適用し、テキストを色付けするユーティリティ関数。
-   `comment_fetcher.py`: GitHub GraphQL APIを利用して、特定のプルリクエストのコメント履歴を取得する関数。
-   `comment_manager.py`: プルリクエストにコメントを投稿したり、特定のコメントの存在を確認したりする関数。
-   `config.py`: `config.toml`ファイルから設定データを読み込み、アプリケーション全体で利用できる設定オブジェクトを提供する関数。
-   `config_printer.py`: 起動時や現在の実行設定に関する詳細情報をコンソールに出力する関数。
-   `display.py`: プルリクエストのリスト、フェーズ、リポジトリの状態、レート制限情報などを整形してコンソールに表示する関数。
-   `github_auth.py`: GitHub CLI (`gh`) を使用してGitHubへの認証状態を確認し、必要に応じて認証プロセスを促す関数。
-   `github_client.py`: GitHub REST APIのエンドポイントに対してHTTPリクエストを実行し、応答を処理する高レベルなクライアント関数。
-   `graphql_client.py`: GitHub GraphQL APIへのクエリを実行し、効率的にデータを取得する関数。
-   `interval_parser.py`: "1m", "30s"といった文字列形式の時間間隔をパースし、秒数などの数値形式に変換する関数。
-   `issue_fetcher.py`: GitHub GraphQL APIを利用して、特定のリポジトリのオープンなIssue情報を取得する関数。
-   `llm_status_extractor.py`: プルリクエストのタイトル、本文、コメントからAIエージェント（LLM）の現在の作業状態を判定するためのキーワードやパターンを抽出する関数。
-   `local_repo_watcher.py`: ローカルファイルシステム上のGitリポジトリを監視し、`git pull`可能な状態を検知したり、自動で`git pull`を実行したりする関数。
-   `main.py`: アプリケーションのメインエントリーポイントで、設定の初期化、監視ループの開始、各種モジュール間の連携を調整する主要な関数。
-   `monitor.py`: 指定された間隔でGitHubのプルリクエストを定期的にポーリングし、フェーズの変化や新たなPRを検知する中核的な監視関数。
-   `notification_window.py`: 自動ブラウザ操作中にユーザーに現在の状況を伝えるための小さなデスクトップ通知ウィンドウを表示・管理する関数。
-   `notifier.py`: ntfy.shサービスと連携し、特定イベント（例: PRがレビュー待ちになったとき）が発生した際にモバイル通知を送信する関数。
-   `pages_watcher.py`: GitHub Pagesのデプロイ状況などの変化を監視し、必要に応じてアクションをトリガーする関数。
-   `phase_detector.py`: プルリクエストのドラフト状態、レビューリクエスト、コメント内容、マージ可否などの情報に基づいて、そのPRがどの開発フェーズにあるかを判定するロジックを提供する関数。
-   `pr_actions.py`: プルリクエストをReady状態に変更したり、自動マージを実行したり、ブラウザでPRページを開いたりするなど、PRに対する具体的なアクションを実行する関数。
-   `pr_data_recorder.py`: プルリクエストの現在の状態や関連データを保存・記録し、後で参照したりデバッグに利用したりするための関数。
-   `pr_fetcher.py`: GitHub GraphQL APIを通じて、指定されたフィルター条件に合致するプルリクエストの情報を取得する関数。
-   `pr_html_fetcher.py`: プルリクエストのページからHTMLコンテンツを取得し、画像認識やOCRの補助データとして利用する関数。
-   `process_utils.py`: システムプロセス（例: `gh`コマンド）の実行、終了コードの取得、標準出力のキャプチャなどを行うユーティリティ関数。
-   `repository_fetcher.py`: 認証済みGitHubユーザーが所有するすべてのリポジトリ情報を取得する関数。
-   `snapshot_markdown.py`: 記録されたプルリクエストのスナップショットデータから、可読性の高いMarkdown形式のレポートを生成する関数。
-   `snapshot_path_utils.py`: スナップショットファイルの保存パスを生成・管理するユーティリティ関数。
-   `state_tracker.py`: 各プルリクエストの最新の状態や、監視セッション全体の状態（例: 変化がない期間）を追跡し、監視間隔の調整などに利用する関数。
-   `time_utils.py`: 日時オブジェクトのフォーマット、時間差の計算、タイムゾーン変換など、時間に関連する汎用的なユーティリティ関数。
-   `wait_handler.py`: 特定の条件が満たされるまで待機したり、指定された時間だけ処理を一時停止したりする関数。
-   `window_manager.py`: オペレーティングシステム上のウィンドウ（特にブラウザウィンドウ）を操作（例: 特定のウィンドウを前面に表示する、最大化する）する関数。

## 関数呼び出し階層ツリー
```
提供された情報では、具体的な関数呼び出し階層を分析できませんでした。

---
Generated at: 2026-03-03 07:04:55 JST
