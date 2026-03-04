Last updated: 2026-03-05

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト（PR）を監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、PRのフェーズ判定と適切なアクションを実行します。
- GraphQL APIを活用し、Dry-runモード、自動マージ、モバイル通知などの豊富な自動化機能を提供します。

## 技術スタック
- フロントエンド: **Webブラウザ自動操作**: PyAutoGUI（ブラウザのUI要素を画像認識で操作）、Pillow（画像処理）、PyGetWindow（ウィンドウ操作）、Pytesseract（OCRによるテキスト検出）、Tesseract-OCR（OCRエンジン）を使用し、GitHub上のUIを自動操作します。
- 音楽・オーディオ: 該当する技術はありません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub認証とAPI連携の基盤として利用されます。
    - **Git**: ローカルリポジトリの監視と自動プル機能に利用されます。
    - **.editorconfig**: 複数人での開発におけるコーディングスタイルを統一します。
    - **VS Code**: `.vscode/settings.json`で開発環境の推奨設定を定義します。
    - **TOML**: 設定ファイル（`config.toml`）の記述形式として使用されます。
- テスト:
    - **Pytest**: Pythonアプリケーションの単体テストおよび統合テストフレームワークとして利用されます。
- ビルドツール:
    - **Python (pyproject.toml)**: Pythonプロジェクトの依存関係管理、パッケージング、ビルド設定に利用されます。
- 言語機能:
    - **Python 3.11+**: アプリケーション本体の開発言語として利用されており、現代的なPythonの機能とパフォーマンスを活用しています。
- 自動化・CI/CD:
    - **ntfy.sh**: PRの状態変化（特にレビュー待ち）をモバイルデバイスに通知するために利用されるプッシュ通知サービスです。
    - **自己更新機能**: GitHubリポジトリの更新を定期的に検知し、作業ツリーがクリーンな場合に自動で`git pull`と再起動を行います。
    - **ローカルリポジトリ自動Pull**: 設定により、親ディレクトリ内のローカルリポジトリを定期的にスキャンし、`git pull`可能な場合に自動で更新します。
    - **GitHub Actions**: 過去に一部機能の実装が試みられましたが、PR監視の目的に合わないためPython版に移行しました（現在はこのプロジェクトのCI/CDには直接使用されていませんが、プロジェクトの背景技術として言及）。
- 開発標準:
    - **Ruff**: コードのリンティングとフォーマットに使用され、コード品質の維持と統一されたコーディングスタイルを強制します。

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
- `.editorconfig`: エディタの基本的な設定（インデントスタイル、文字コードなど）を定義し、プロジェクト全体のコーディングスタイルを統一します。
- `.gitignore`: Gitのバージョン管理から除外するファイルやディレクトリを指定します。
- `.vscode/`: Visual Studio Codeのワークスペース設定を格納するディレクトリです。
    - `settings.json`: Visual Studio Codeのワークスペース固有の設定を定義し、開発環境の統一を支援します。
- `LICENSE`: プロジェクトのライセンス情報（MIT License）を記述しています。
- `MERGE_CONFIGURATION_EXAMPLES.md`: マージ設定の具体的な例を示すドキュメントです。
- `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3での自動マージ機能の実装詳細に関するドキュメントです。
- `README.ja.md`, `README.md`: プロジェクトの概要、機能、使い方、設定方法などを説明する日本語および英語のメインドキュメントです。
- `STRUCTURE.md`: プロジェクトのアーキテクチャやモジュール構造を説明するドキュメントです。
- `_config.yml`: Jekyllなどの静的サイトジェネレーターで利用される可能性のある設定ファイルです。
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントであり、設定の読み込みと監視ループの開始を担います。
- `config.toml.example`: プロジェクトの設定ファイル`config.toml`の作成例を提供するテンプレートです。
- `demo_automation.py`: ブラウザ自動操作機能のデモンストレーション用スクリプトです。
- `docs/`: プロジェクトの追加ドキュメントを格納するディレクトリです。
    - `RULESETS.md`: ルールセット設定の詳細と使用例を説明するドキュメントです。
    - `button-detection-improvements.ja.md`: ボタン検出改善に関する日本語ドキュメントです。
    - `window-activation-feature.md`: ウィンドウアクティベーション機能に関するドキュメントです。
- `fetch_pr_html.py`: プルリクエストのHTMLコンテンツを取得するための補助スクリプトです。
- `generated-docs/`: 自動生成されたドキュメントを格納するディレクトリです。
- `pyproject.toml`: Pythonプロジェクトのメタデータ、依存関係、ビルド設定を定義するファイルです（PEP 517/518準拠）。
- `pytest.ini`: pytestテストフレームワークの設定ファイルです。
- `requirements-automation.txt`: 自動化機能（PyAutoGUI, pytesseractなど）に必要なPythonパッケージのリストです。
- `ruff.toml`: コードリンターおよびフォーマッターであるRuffの設定ファイルです。
- `screenshots/`: PyAutoGUIによる画像認識で使用されるボタンのスクリーンショット画像を格納するディレクトリです。
    - `assign.png`, `assign_to_copilot.png`: GitHub UI上の「Assign」および「Assign to Copilot」ボタンのスクリーンショット画像です。
- `src/`: プロジェクトの主要なソースコードを格納するディレクトリです。
    - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
    - `gh_pr_phase_monitor/`: プロジェクトの主要なアプリケーションロジックを格納するパッケージです。
        - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
        - `actions/`: プルリクエストに対するアクション関連のモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `pr_actions.py`: プルリクエスト（PR）に対する特定のアクション（例: Ready化、コメント投稿、ntfy通知、自動マージ）を実行する機能を提供します。
        - `browser/`: Webブラウザ自動操作関連のモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `browser_automation.py`: PyAutoGUIやOCRなどを用いてWebブラウザ（GitHub UI）を自動操作するための高レベルなインターフェースを提供します。
            - `browser_cooldown.py`: ブラウザ操作間のクールダウン時間（待機時間）を管理し、APIレート制限やUIのロード時間を考慮します。
            - `button_clicker.py`: 画像認識やOCRを用いて画面上の特定のボタンを検出し、クリックする機能を提供します。
            - `click_config_validator.py`: 自動クリック機能の設定が適切であるかを検証します。
            - `window_manager.py`: ブラウザウィンドウの管理（アクティブ化、最大化など）を行う機能を提供します。
        - `core/`: プロジェクトのコアユーティリティおよび共通機能のモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `colors.py`: ターミナル出力のためのANSIカラーコードと色付け機能を提供します。
            - `config.py`: `config.toml`ファイルからの設定を読み込み、解析し、プロジェクト全体で利用可能な形式で提供します。
            - `config_printer.py`: 起動時やverboseモードで、現在の設定内容を整形して表示する機能を提供します。
            - `interval_parser.py`: 設定ファイルで指定された時間間隔（例: "30s", "1m"）を内部処理用の秒数に変換します。
            - `process_utils.py`: プロセス関連のユーティリティ関数（例: 実行中のプロセスの確認）を提供します。
            - `time_utils.py`: 時間関連のユーティリティ関数（例: 経過時間計算、タイムスタンプ処理）を提供します。
        - `github/`: GitHub APIとの連携に関連するモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `comment_fetcher.py`: GitHubのプルリクエストコメントを取得する機能を提供します。
            - `comment_manager.py`: プルリクエストへのコメント投稿や、既存コメントの有無の確認を管理します。
            - `github_auth.py`: GitHub CLI (`gh`) を利用した認証処理を管理します。
            - `github_client.py`: GitHub API（主にGraphQL）との通信を抽象化し、データ取得や操作のインターフェースを提供します。
            - `graphql_client.py`: GitHub GraphQL APIへのリクエスト送信とレスポンス処理を直接担当します。
            - `issue_fetcher.py`: GitHubリポジトリからIssue情報を取得する機能を提供します。
            - `pr_fetcher.py`: GitHubリポジトリからプルリクエスト情報を取得する機能を提供します。
            - `rate_limit_handler.py`: GitHub APIのレート制限を監視し、制限超過を回避するための処理を実装します。
            - `repository_fetcher.py`: GitHubユーザーが所有するリポジトリの一覧を取得する機能を提供します。
        - `main.py`: プロジェクトの主要な実行ロジックを含み、メインの監視ループと全体の制御フローを管理します。
        - `monitor/`: 監視機能と状態管理に関連するモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `auto_updater.py`: プロジェクト自身のGitHubリポジリの更新を監視し、自動で`git pull`および再起動を行う機能を提供します。
            - `local_repo_watcher.py`: 親ディレクトリ内のローカルGitリポジトリを監視し、リモートからの`pull`が可能かどうかの状態を検知し、オプションで自動`pull`を実行します。
            - `monitor.py`: プロジェクトの主要な監視ロジックと状態管理の中心となるモジュールです。
            - `pages_watcher.py`: GitHub Pagesのデプロイ状況などを監視する機能を提供する可能性があります。
            - `snapshot_markdown.py`: スナップショットデータをMarkdown形式で生成する機能を提供します。
            - `snapshot_path_utils.py`: スナップショットファイルのパス管理ユーティリティを提供します。
            - `state_tracker.py`: 監視対象のPRの状態変化を追跡し、変更がない期間を記録する機能を提供します（省電力モードのトリガーなど）。
        - `phase/`: プルリクエストのフェーズ判定に関連するモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `llm_status_extractor.py`: プルリクエストのコメントやコンテキストから、LLMエージェントの作業状態を抽出する機能を提供します。
            - `phase_detector.py`: プルリクエストの各種情報（Draft状態、レビューコメント、エージェントコメントなど）に基づいて、現在のフェーズ（phase1/2/3, LLM working）を判定するロジックを実装します。
            - `phase_detector_graphql.py`: GraphQL APIからのデータに基づいてフェーズ判定を行う機能を提供します。
            - `pr_data_recorder.py`: プルリクエストのデータを記録し、履歴管理やデバッグに利用します。
            - `pr_html_analyzer.py`: プルリクエストページのHTMLコンテンツを解析し、特定の情報を抽出する機能を提供します。
            - `pr_html_fetcher.py`: プルリクエストページのHTMLコンテンツを取得する機能を提供します。
            - `pr_html_saver.py`: プルリクエストのHTMLコンテンツを保存する機能を提供します。
        - `ui/`: ユーザーインターフェース（ターミナル表示、通知）関連のモジュールを格納します。
            - `__init__.py`: Pythonパッケージであることを示す空ファイルです。
            - `display.py`: ターミナルへの情報表示（PRの状態、要約など）を整形して出力する機能を提供します。
            - `notification_window.py`: ブラウザ自動操作中に表示される小さなデスクトップ通知ウィンドウを管理します。
            - `notifier.py`: ntfy.shサービスを介してモバイル通知を送信する機能を提供します。
            - `wait_handler.py`: プログラムの特定の待機（クールダウン）処理を管理します。
- `tests/`: プロジェクトのテストファイルを格納するディレクトリです。
    - `test_*.py`: プロジェクトの各機能に対するPytestテストファイル群です。各ファイルは特定のモジュールや機能のテストケースを定義しています。

## 関数詳細説明
提供された情報からは具体的な関数名とその引数、戻り値を特定することができませんでした。
しかし、プロジェクトのモジュール構成に基づき、主要な機能を提供する関数群について、その役割を説明します。

- **設定管理機能**: `src/gh_pr_phase_monitor/core/config.py`や`src/gh_pr_phase_monitor/core/interval_parser.py`に実装されており、`config.toml`からの設定値の読み込み、解析、型変換、および時間間隔文字列の秒数への変換などを担当する関数群を提供します。
- **GitHub APIクライアント機能**: `src/gh_pr_phase_monitor/github/github_client.py`や`src/gh_pr_phase_monitor/github/graphql_client.py`に実装されており、認証済みユーザーの所有リポジトリ、プルリクエスト、Issue、コメントなどの情報をGitHub GraphQL APIを介して取得・操作する関数群を提供します。レート制限ハンドリングも含まれます。
- **PRフェーズ判定機能**: `src/gh_pr_phase_monitor/phase/phase_detector.py`に実装されており、プルリクエストのタイトル、ドラフト状態、レビューコメント、LLMエージェントのコメントなどの情報に基づいて、PRが現在どの開発フェーズ（phase1, phase2, phase3, LLM working）にあるかを判定する関数群を提供します。
- **PRアクション実行機能**: `src/gh_pr_phase_monitor/actions/pr_actions.py`に実装されており、フェーズ判定結果に基づき、PRのDraft解除（Ready化）、特定のコメント投稿、ntfy.sh経由の通知送信、PRの自動マージ、ブラウザでのPRページ開示などのアクションを実行する関数群を提供します。
- **ブラウザ自動操作機能**: `src/gh_pr_phase_monitor/browser/browser_automation.py`や`src/gh_pr_phase_monitor/browser/button_clicker.py`に実装されており、PyAutoGUIやOCRを利用してWebブラウザ上のGitHub UI要素（例: マージボタン、アサインボタン）を検出・クリックする関数群を提供します。ウィンドウ管理や画像認識の信頼度調整、デバッグ情報の保存機能も含まれます。
- **監視ループと状態管理機能**: `src/gh_pr_phase_monitor/main.py`や`src/gh_pr_phase_monitor/monitor/monitor.py`に実装されており、定期的なPR情報のフェッチ、フェーズ判定、アクション実行、省電力モードへの切り替え、自己更新、ローカルリポジトリ監視などの主要な監視ロジックと全体的なフローを制御する関数群を提供します。
- **通知・表示機能**: `src/gh_pr_phase_monitor/ui/notifier.py`や`src/gh_pr_phase_monitor/ui/display.py`に実装されており、ntfy.shを介したモバイル通知の送信、ターミナルへの整形された情報出力、ブラウザ自動操作中のデスクトップ通知ウィンドウ表示などを担当する関数群を提供します。
- **ローカルリポジトリ監視機能**: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`に実装されており、設定されたディレクトリ内のGitリポジトリを監視し、リモートの変更を検知して自動で`git pull`を実行する関数群を提供します。

## 関数呼び出し階層ツリー
```
提供された情報からは、プロジェクト全体の関数呼び出し階層ツリーを分析できませんでした。

---
Generated at: 2026-03-05 07:04:48 JST
