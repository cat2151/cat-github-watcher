Last updated: 2026-02-15

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのPRを監視し、適切な通知とアクションを行うPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIで効率的にPRの状態を判定し、自動化されたワークフローを支援します。
- PRのReady化、コメント投稿、モバイル通知、自動マージ、Issue割り当てなど、開発プロセスを自動化・効率化する多様な機能を提供します。

## 技術スタック
- フロントエンド: なし（本プロジェクトはコマンドラインインターフェース（CLI）ツールとして動作し、直接的なGUIは持ちません。）
- 音楽・オーディオ: なし
- 開発ツール:
    - GitHub CLI (gh): GitHubの認証、API操作（GraphQL/REST）のためのコマンドラインインターフェースツール。
    - Pytest: Pythonアプリケーションのテストコードを記述し、実行するためのフレームワーク。
    - Ruff: Pythonコードのフォーマットと静的解析（リンティング）を行う高速なツール。`ruff.toml`でルールを設定。
    - Git: バージョン管理システム。自己更新機能でGitHubリポジトリの変更を検知・同期するために使用されます。
    - PyAutoGUI: マウスやキーボードの操作を自動化し、ブラウザのUI（ボタンなど）をプログラムで操作するために使用されます。
    - Pillow: PyAutoGUIの依存ライブラリとして、画像処理機能（スクリーンショットの取得、画像マッチングなど）を提供します。
    - Pygetwindow: PyAutoGUIの依存ライブラリとして、ウィンドウの検出、アクティブ化、操作を行うために使用されます。
    - PyTesseract: Tesseract OCRエンジンと連携し、画像からテキストを抽出するPythonラッパー。ブラウザ自動化のフォールバックとして使用されます。
    - Tesseract OCR: 画像からテキストを認識する光学文字認識（OCR）エンジン。PyTesseractが利用するためにシステムレベルでインストールが必要です。
- テスト:
    - Pytest: 上記の通り、プロジェクトの各種機能の単体テストや統合テストに使用されます。
- ビルドツール: なし（Pythonスクリプトとして直接実行されるため、特定のビルドツールは使用していません。）
- 言語機能:
    - Python 3.10以上: プロジェクトの主要な開発言語。
    - GraphQL API: GitHub APIとの通信に利用される効率的なデータ取得プロトコル。
    - TOML: 設定ファイル（`config.toml`）の記述形式として使用され、構造化された設定を人間が読み書きしやすい形で提供します。
- 自動化・CI/CD:
    - GitHub Actions: README.mdの自動翻訳など、プロジェクトの補助的な自動化（本プロジェクトのコア機能とは別）。
    - ntfy.sh: モバイル端末へのリアルタイム通知を送信するためのシンプルなプッシュ通知サービス。
    - 自己更新機能 (auto_updater.py): ツール自体がGitHubリポジトリの更新を検知し、自動的に最新版に更新・再起動する機能。
- 開発標準:
    - EditorConfig: 異なるエディタやIDE間で一貫したコーディングスタイル（インデント、改行コードなど）を維持するための設定ファイル。
    - Ruff: 上記の通り、コードの品質と一貫性を保つためのリンティングおよびフォーマットルール。

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
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントとなるスクリプト。アプリケーションの起動と主要な処理フローを制御します。
- `.editorconfig`: 様々なテキストエディタやIDE間でコードのインデントスタイル、文字エンコーディングなどの設定を統一するためのファイルです。
- `.gitignore`: Gitのバージョン管理から除外するファイルやディレクトリ（例: 実行時のキャッシュファイル、ローカル設定ファイルなど）を指定するファイルです。
- `.vscode/settings.json`: Visual Studio Codeエディタ用の設定ファイル。プロジェクト固有のワークスペース設定や拡張機能の設定が記述されます。
- `LICENSE`: プロジェクトがMIT Licenseで公開されていることを示すライセンス情報ファイルです。
- `MERGE_CONFIGURATION_EXAMPLES.md`: PRの自動マージ機能に関する設定例や使用方法について説明するMarkdown形式のドキュメントです。
- `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3におけるPR自動マージ機能の実装詳細や内部動作について説明するMarkdownドキュメントです。
- `README.ja.md`: プロジェクトの概要、特徴、セットアップ方法、使い方などが日本語で記述されたメインドキュメントです。
- `README.md`: `README.ja.md`の英語版であり、同様のプロジェクト情報が英語で記述されています。
- `STRUCTURE.md`: プロジェクト全体のディレクトリ構成やモジュール間の関係など、構造に関する情報を提供するMarkdownドキュメントです。
- `_config.yml`: GitHub Pagesなどで使用されるJekyllのサイト設定ファイル。ドキュメントサイトのビルド設定などが含まれることがあります。
- `config.toml.example`: `config.toml`を作成する際のテンプレートとして提供されるファイル。利用者はこれをコピーして自分の設定を記述します。
- `demo_automation.py`: ブラウザ自動化機能（PyAutoGUIなど）の動作をデモンストレーションするための補助スクリプトです。
- `docs/`: プロジェクトの追加ドキュメントを格納するディレクトリ。
    - `RULESETS.md`: 監視ルールセット（rulesets）の詳細な設定方法や機能について説明するドキュメントです。
    - `button-detection-improvements.ja.md`: ブラウザ自動化におけるボタン検出機能の改善点や技術詳細を説明するドキュメントです。
    - `window-activation-feature.md`: ウィンドウのアクティブ化機能に関する詳細情報を提供するドキュメントです。
- `generated-docs/`: 自動生成されたドキュメントやレポートを格納するためのディレクトリです。
- `pytest.ini`: pytestテストフレームワークの設定ファイル。テストの実行オプションやカバレッジ設定などが記述されます。
- `requirements-automation.txt`: ブラウザ自動化機能（PyAutoGUI, PyTesseractなど）に必要なPythonパッケージとそのバージョンを列挙したファイルです。
- `ruff.toml`: Ruffリンターおよびフォーマッターの設定ファイル。Pythonコードの品質と一貫性を保つためのルールが定義されています。
- `screenshots/`: ブラウザ自動化機能がボタンを識別するために使用するスクリーンショット画像ファイルを保存するディレクトリです。
- `src/`: プロジェクトの主要なソースコードを格納するディレクトリ。
    - `gh_pr_phase_monitor/`: プロジェクトのコアロジックを構成するPythonモジュール群。
        - `__init__.py`: Pythonパッケージであることを示すファイル。
        - `auto_updater.py`: ツールの自己更新ロジックを実装。GitHubリポジトリの更新を検知し、自動でpullして再起動します。
        - `browser_automation.py`: PyAutoGUIなどを使用してブラウザのUIを自動操作する機能（ボタンクリック、ウィンドウ操作など）を提供します。
        - `colors.py`: ターミナル出力に色付けを行うためのANSIカラーコード定義と色付けユーティリティ関数を提供します。
        - `comment_fetcher.py`: GitHub PRからコメント履歴を取得し、特定の条件（例: LLMエージェントからのコメント）に合致するコメントを抽出します。
        - `comment_manager.py`: GitHub PRへのコメント投稿、および既存コメントの存在確認を行う機能を提供します。
        - `config.py`: `config.toml`ファイルから設定を読み込み、解析、バリデーションを行う責任を持つモジュールです。
        - `display.py`: CLI（コマンドラインインターフェース）に情報を表示する際のフォーマットやレイアウト、色付けなどを管理します。
        - `github_auth.py`: GitHub CLI (`gh`) を利用してGitHubへの認証情報（トークンなど）を取得・管理する機能を提供します。
        - `github_client.py`: GitHub REST APIおよびGraphQL APIと連携するための低レベルクライアント。リクエストの送信、レスポンスの処理を行います。
        - `graphql_client.py`: GitHub GraphQL APIに特化したクライアント。効率的なPR情報やリポジトリ情報のクエリを構築し実行します。
        - `issue_fetcher.py`: GitHubリポジトリからIssueの情報を取得する機能を提供します。
        - `main.py`: アプリケーションのメイン実行ループを構築し、各モジュールをオーケストレーションして監視プロセス全体を制御します。
        - `monitor.py`: 定期的にGitHub PRの状態を監視し、`phase_detector`や`pr_actions`を呼び出す監視ロジックをカプセル化します。
        - `notifier.py`: ntfy.shなどのサービスを利用して、特定のイベント（例: PRがレビュー待ちになった際）のモバイル通知を送信します。
        - `phase_detector.py`: プルリクエストの現在の状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を詳細なロジックに基づいて判定します。
        - `pr_actions.py`: プルリクエストに対する具体的なアクション（Ready化、ブラウザ起動、自動マージ、Issue割り当てなど）を実行します。
        - `pr_data_recorder.py`: プルリクエストの履歴データや状態変化を記録し、長期的な追跡や分析に利用するための機能を提供します。
        - `pr_fetcher.py`: 指定されたリポジトリのプルリクエスト（PR）情報を取得する機能を提供します。
        - `repository_fetcher.py`: 認証済みGitHubユーザーが所有するリポジトリの一覧を取得する機能を提供します。
        - `state_tracker.py`: 各PRの現在のフェーズや以前のフェーズを追跡し、状態変化がない場合に省電力モードへ移行するロジックを管理します。
        - `time_utils.py`: 時間に関するユーティリティ関数（例: 時間間隔文字列のパース、スリープ処理）を提供します。
        - `wait_handler.py`: 監視間隔、`no_change_timeout`、`reduced_frequency_interval`などの設定に基づいて、次の監視サイクルまでの待機時間を管理します。
- `tests/`: プロジェクトのテストスイートを格納するディレクトリ。
    - `test_auto_update_config.py` 他、多数の`test_*.py`ファイル: 各モジュールや機能（設定の読み込み、フェーズ検出、PRアクション、通知など）に対する単体テストや統合テストが含まれています。

## 関数詳細説明
- `main()`: (定義元: `src/gh_pr_phase_monitor/main.py`) プログラムのエントリーポイントであり、全体の実行フローを統括します。設定の読み込み、監視ループの初期化と開始を行います。
- `load_config(config_path)`: (定義元: `src/gh_pr_phase_monitor/config.py`) 指定されたパスからTOML形式の設定ファイルを読み込み、パースして設定オブジェクトを返します。設定のバリデーションも行います。
- `fetch_repositories()`: (定義元: `src/gh_pr_phase_monitor/repository_fetcher.py`) GitHub CLIを通じて、現在認証されているユーザーが所有する全リポジトリのリストを取得します。
- `fetch_pull_requests(repository_id)`: (定義元: `src/gh_pr_phase_monitor/pr_fetcher.py`) 指定されたGitHubリポジトリIDに関連付けられたオープンなプルリクエストのリストとその詳細情報をGraphQL API経由で取得します。
- `detect_phase(pr_data, config)`: (定義元: `src/gh_pr_phase_monitor/phase_detector.py`) プルリクエストの各種データ（Draft状態、レビューリクエスト、コメント内容など）を分析し、現在のフェーズ（phase1, phase2, phase3, LLM working）を判定します。
- `post_comment(pr_id, body, config)`: (定義元: `src/gh_pr_phase_monitor/comment_manager.py`) 指定されたプルリクエストIDに対して、提供された本文（body）でコメントを投稿します。
- `mark_pr_as_ready_for_review(pr_id)`: (定義元: `src/gh_pr_phase_monitor/pr_actions.py`) 指定されたプルリクエストをDraft状態から「レビュー準備完了」状態に切り替えます。
- `send_ntfy_notification(message, url, topic, priority)`: (定義元: `src/gh_pr_phase_monitor/notifier.py`) ntfy.shサービスを利用して、指定されたメッセージとPRのURLを含む通知をモバイル端末に送信します。
- `merge_pull_request(pr_id, commit_headline, config)`: (定義元: `src/gh_pr_phase_monitor/pr_actions.py`) 指定されたプルリクエストを自動的にマージします。ブラウザ自動化機能を使用する場合もあります。
- `assign_issue_to_copilot(issue_url, config)`: (定義元: `src/gh_pr_phase_monitor/pr_actions.py`) 指定されたIssueのURLを開き、ブラウザ自動化を用いて「Assign to Copilot」ボタンをクリックし、IssueをCopilotに割り当てます。
- `check_for_updates(repo_path, config)`: (定義元: `src/gh_pr_phase_monitor/auto_updater.py`) ローカルリポジトリがクリーンであり、GitHubリモートリポジトリに新しいコミットがあるかを確認し、可能であれば自動でpullしてツールを再起動します。
- `track_pr_state(repo_full_name, pr_id, current_phase)`: (定義元: `src/gh_pr_phase_monitor/state_tracker.py`) 各プルリクエストの現在のフェーズを記録し、前回の状態と比較して変更があったかを追跡します。
- `run_monitor_loop(config)`: (定義元: `src/gh_pr_phase_monitor/monitor.py`) 監視間隔に基づいて定期的にGitHubリポジトリとPRの状態をチェックし、フェーズ判定、アクション実行、通知などを行うメインの無限ループです。
- `display_pr_status(pr_info, current_phase, config)`: (定義元: `src/gh_pr_phase_monitor/display.py`) プルリクエストのステータス情報（タイトル、フェーズ、URLなど）を整形し、設定されたカラースキームでCLIに表示します。
- `get_github_token()`: (定義元: `src/gh_pr_phase_monitor/github_auth.py`) GitHub CLI (`gh`) を使用して、現在認証されているGitHubユーザーの認証トークンを取得します。
- `click_button_by_image(image_path, confidence, debug_dir)`: (定義元: `src/gh_pr_phase_monitor/browser_automation.py`) PyAutoGUIを使用して、指定された画像ファイルに一致するボタンを画面上で探し、クリックするブラウザ自動化のコア関数です。OCRフォールバックも含まれます。
- `parse_interval_string(interval_str)`: (定義元: `src/gh_pr_phase_monitor/time_utils.py`) "30s", "1m", "5m"などの時間間隔を表す文字列を解析し、対応する秒数を返します。
- `handle_wait(last_change_time, config)`: (定義元: `src/gh_pr_phase_monitor/wait_handler.py`) 前回の状態変更からの時間や設定された`no_change_timeout`に基づいて、通常の監視間隔または省電力モードの監視間隔で待機時間を計算し、スリープを実行します。

## 関数呼び出し階層ツリー
```
[プロジェクト情報に「関数呼び出し階層を分析できませんでした」と記載があるため、具体的なツリーの生成は行いません。]

---
Generated at: 2026-02-15 07:02:03 JST
