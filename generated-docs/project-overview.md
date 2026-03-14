Last updated: 2026-03-15

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト(PR)監視に特化したPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIでPRのフェーズを効率的に監視します。
- PRの状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）に応じた通知や自動アクションを実行し、開発ワークフローを支援します。

## 技術スタック
- フロントエンド: 直接的なGUIはありませんが、ブラウザ自動操作には`PyAutoGUI`と`PyGetWindow`を使用。ユーザーへのモバイル通知には`ntfy.sh`を利用し、主なUIはターミナル出力で行われます。
- 音楽・オーディオ: このプロジェクトでは音楽・オーディオ関連技術は使用されていません。
- 開発ツール: GitHubとの連携には`GitHub CLI (gh)`、ローカルリポジトリ操作には`git`が前提です。ブラウザ自動操作における画像認識とOCRには`PyAutoGUI`、`pillow`、`pygetwindow`、`tesseract-ocr`が利用されます。
- テスト: Pythonのテストフレームワークである`pytest`が使用され、プロジェクトの各機能に対する単体・統合テストが実装されています。
- ビルドツール: Pythonプロジェクトのパッケージ管理には標準的な`pip`と`pyproject.toml`を使用。また、Rustプロジェクトのバイナリを自動更新する機能として`cargo install`が組み込まれています。
- 言語機能: `Python 3.11`以上を推奨環境としており、GitHubとの効率的な連携のために`GraphQL API`を活用。設定ファイルには`TOML`形式を採用しています。
- 自動化・CI/CD: ドキュメント生成や翻訳プロセスに`GitHub Actions`を活用。モバイル通知には`ntfy.sh`、ブラウザ自動操作には`PyAutoGUI`を使用し、ツール自身の自動更新やローカルリポジトリの自動`git pull`機能も提供されます。
- 開発標準: コードの品質と一貫性を保つため、Pythonリンター/フォーマッタの`ruff`およびコードエディタの設定を統一する`.editorconfig`ファイルを利用しています。

## ファイル階層ツリー
```
cat-github-watcher/
├── cat-github-watcher.py
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py
│       ├── config.py
│       ├── github_client.py
│       ├── phase_detector.py
│       ├── comment_manager.py
│       ├── pr_actions.py
│       └── main.py
└── tests/
```

## ファイル詳細説明
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントとなるスクリプト。ツールの起動と主要な処理の呼び出しを行います。
- `config.toml.example`: ユーザーがプロジェクト設定を行うためのサンプルファイル。監視間隔、通知設定、自動化ルールなどが記述されています。
- `src/gh_pr_phase_monitor/main.py`: アプリケーションのメイン実行ロジックを格納し、監視ループの管理、主要な処理モジュールの連携を行います。
- `src/gh_pr_phase_monitor/core/config.py`: アプリケーションの設定ファイル（`config.toml`）の読み込み、解析、検証を担当するモジュールです。
- `src/gh_pr_phase_monitor/core/colors.py`: ターミナル出力に色を付けるためのANSIカラーコード定義と、テキストを色付けするユーティリティ機能を提供します。
- `src/gh_pr_phase_monitor/github/github_client.py`: GitHub APIと連携するための中心的なクライアント。認証情報の管理やAPIリクエストの調整を行います。
- `src/gh_pr_phase_monitor/github/graphql_client.py`: GitHubのGraphQL APIに対してクエリを送信し、PRやリポジトリの情報を効率的に取得する機能を提供します。
- `src/gh_pr_phase_monitor/github/pr_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリから、オープンなプルリクエストの情報を取得するロジックをカプセル化しています。
- `src/gh_pr_phase_monitor/phase/phase_detector.py`: プルリクエストの現在の状態を分析し、`phase1` (Draft)、`phase2` (レビュー指摘対応中)、`phase3` (レビュー待ち)、`LLM working` (コーディングエージェント作業中) のいずれかのフェーズを判定する主要なロジックです。
- `src/gh_pr_phase_monitor/actions/pr_actions.py`: 判定されたPRのフェーズとユーザー設定に基づいて、Draft PRのReady化、ブラウザ起動、コメント投稿、自動マージなどの具体的なアクションを実行します。
- `src/gh_pr_phase_monitor/github/comment_manager.py`: GitHubプルリクエストへのコメント投稿や、既存のレビューコメントの確認を管理する機能を提供します。
- `src/gh_pr_phase_monitor/ui/display.py`: ターミナルへの情報表示（PRステータス、ログ、進捗状況など）を整形し、ユーザーフレンドリーに出力します。
- `src/gh_pr_phase_monitor/ui/notifier.py`: ntfy.shサービスを利用して、特定のイベント（例: PRがレビュー待ちになった際）に関するモバイル通知を送信する機能を提供します。
- `src/gh_pr_phase_monitor/monitor/monitor.py`: 監視ループ全体のオーケストレーションと、アプリケーションの状態管理（省電力モードへの切り替えなど）を行います。
- `src/gh_pr_phase_monitor/monitor/auto_updater.py`: プロジェクト自身のGitリポジトリの更新を定期的にチェックし、新しいバージョンがあれば自動的に`git pull`してアプリケーションを再起動します。
- `src/gh_pr_phase_monitor/browser/browser_automation.py`: PyAutoGUIなどのライブラリを用いて、ブラウザの自動操作（ウィンドウ管理、座標特定、クリックなど）を行う共通ロジックを提供します。
- `src/gh_pr_phase_monitor/browser/button_clicker.py`: 画像認識（PyAutoGUI）やOCR（tesseract-ocr）を用いてブラウザ画面上の特定のボタンを検出し、自動的にクリックする処理を実装しています。
- `src/gh_pr_phase_monitor/browser/window_manager.py`: ブラウザウィンドウの検索、アクティブ化、最大化などのOSレベルのウィンドウ管理機能を提供します。
- `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`: ローカルファイルシステム上のGitリポジトリを監視し、リモートからの`pull`が必要な状態を検知して表示、または設定に応じて自動で`git pull`を実行します。
- `src/gh_pr_phase_monitor/monitor/local_repo_cargo.py`: `cargo install`でインストールされたRustプロジェクトのバイナリを、関連するローカルリポジトリが`pull`された際に自動更新する機能を提供します。
- `src/gh_pr_phase_monitor/phase/html/pr_html_analyzer.py`: プルリクエストのHTMLコンテンツを解析し、LLMエージェントのステータスや、レビューコメント、その他の関連情報を抽出する役割を担います。
- `tests/`: プロジェクトの各モジュールと機能に対する単体テスト、統合テスト、およびシステムテストを格納するディレクトリです。

## 関数詳細説明
- `run_monitor()`: メインの監視ループを開始し、設定された間隔でGitHubプルリクエストの状態をチェックし、フェーズ判定と適切なアクションをトリガーします。
- `load_config()`: `config.toml`ファイルからアプリケーション設定を読み込み、解析して、プロジェクト全体で使用可能な設定オブジェクトとして提供します。これにより、ユーザーは柔軟にツールの動作をカスタマイズできます。
- `query_github()`: GitHub GraphQL APIに対してクエリを送信し、プルリクエスト、リポジトリ、イシューに関する詳細な情報を効率的に取得します。APIレート制限の管理も行います。
- `fetch_pull_requests()`: 認証済みユーザーが所有するGitHubリポジトリから、現在オープン状態にあるプルリクエストの一覧を取得し、処理のために準備します。
- `detect_phase()`: 特定のプルリクエストのタイトル、ステータス、コメントなどの情報を基に、それがDraft状態、レビュー指摘対応中、レビュー待ち、またはLLMが作業中のどのフェーズにあるかをインテリジェントに判定します。
- `execute_pr_action()`: 判定されたPRのフェーズと、`config.toml`で定義されたルールセット（`rulesets`）に基づいて、プルリクエストのReady化、指定コメントの投稿、ntfy.sh通知の送信、または自動マージなどの具体的なアクションを実行します。
- `post_comment()`: 指定されたプルリクエストに対して、設定ファイルに基づいて自動生成された、または特定のフェーズに対応するコメントをGitHubに投稿します。
- `send_notification()`: ntfy.shサービスを利用して、特定の重要なイベント（例: プルリクエストがレビュー待ちになった際）に関するモバイル通知をユーザーのデバイスに送信します。
- `check_and_update()`: このツール自身のGitリポジトリに新しいコミットがないかを定期的にチェックし、更新があれば自動的に`git pull`を実行して最新バージョンに自己更新し、アプリケーションを再起動します。
- `monitor_local_repos()`: ローカルファイルシステム上のGitリポジトリを監視し、リモートリポジトリからの`pull`が必要な状態を検知した場合に、その旨を表示するか、設定に応じて自動で`git pull`を実行します。
- `click_button()`: PyAutoGUIなどの自動化ライブラリと、画像認識またはOCR技術を組み合わせて、ブラウザ画面上の特定のボタン（例: "Merge pull request", "Assign to Copilot"）をプログラムによって自動的にクリックします。
- `analyze_pr_html()`: プルリクエストのHTMLコンテンツを深く解析し、LLMエージェントの作業ステータス、特定のレビューコメント、その他の詳細な情報を抽出することで、フェーズ判定の精度を高めます。

## 関数呼び出し階層ツリー
```
関数呼び出し階層の情報は提供されていません。

---
Generated at: 2026-03-15 07:02:17 JST
