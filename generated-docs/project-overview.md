Last updated: 2026-02-02

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト(PR)を効率的に監視するツールです。
- 認証済みGitHubユーザーが所有するリポジトリを対象に、PRのフェーズを自動判定します。
- フェーズに応じた自動通知、コメント投稿、PRのReady化、自動マージ、Issue割り当てなどのアクションを実行します。

## 技術スタック
- フロントエンド: 本プロジェクトはCLIツールであり、GUIは持ちません。PyAutoGUIによるブラウザ自動操作が特定の機能で利用されます。
- 音楽・オーディオ: ntfy.sh: モバイル端末へのプッシュ通知サービスで、PRの状態変化をリアルタイムでユーザーに通知するために利用されます。
- 開発ツール:
    - GitHub CLI (gh): GitHubとの認証やAPI連携を行うためのコマンドラインインターフェースです。
    - PyAutoGUI: スクリーンショットマッチングとキーボード/マウス操作により、ブラウザ上のボタンクリックなどのタスクを自動化します。
    - pytest: Pythonアプリケーションのテストを効率的に記述・実行するためのフレームワークです。
- テスト: pytest: コードの品質と信頼性を確保するための、様々なテスト（単体テスト、結合テストなど）の実行に用いられます。
- ビルドツール: Python 3.x: プロジェクトの実行環境としてPythonの標準機能を使用します。特定のビルドツールは明示されていません。
- 言語機能:
    - Python 3.x: プロジェクトの主要なプログラミング言語です。
    - GraphQL API: GitHub APIの中でも特に効率的なデータ取得が可能なGraphQLエンドポイントを利用してPR情報を取得します。
- 自動化・CI/CD:
    - GitHub Actions: READMEの翻訳など、ドキュメント生成や一部の自動化タスクに利用されます。
    - ntfy.sh: 特定のPRフェーズになった際に自動でモバイル通知を送信する機能を提供します。
    - PyAutoGUI: ブラウザ操作の自動化により、PRのマージやIssueの割り当てといった手動操作を自動化します。
- 開発標準:
    - ruff: Pythonコードのリンティング（構文チェックとスタイルガイド違反の検出）を行い、コード品質を均一に保ちます。
    - .editorconfig: 異なるエディタやIDE間でコードのスタイル（インデント、改行コードなど）を統一するための設定ファイルです。
    - 単一責任の原則 (SRP): コードの設計原則の一つで、各モジュールやクラスが単一の明確な責任を持つように設計されています。

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
- **cat-github-watcher.py**: このプロジェクトの主要なエントリーポイントです。アプリケーションの起動とメイン処理の開始を担います。
- **src/gh_pr_phase_monitor/main.py**: プロジェクトの主要な実行ループと、PR監視の全体的なフローを制御します。定期的な監視処理を調整し、他のモジュールと連携してアクションを実行します。
- **src/gh_pr_phase_monitor/config.py**: `config.toml`ファイルからアプリケーションの設定（監視間隔、通知設定、自動化フラグなど）を読み込み、解析し、管理します。設定の検証も行います。
- **src/gh_pr_phase_monitor/github_client.py**: GitHub REST APIとの主要なインタラクションを担当します。認証済みユーザーのリポジトリやPRに関する情報を取得するための低レベルなAPI呼び出しをカプセル化します。
- **src/gh_pr_phase_monitor/graphql_client.py**: GitHub GraphQL APIを利用して、PRやリポジトリに関する情報を効率的に取得します。複雑なクエリを実行し、必要なデータを一度にまとめて取得することでAPI呼び出し回数を削減します。
- **src/gh_pr_phase_monitor/repository_fetcher.py**: 認証済みユーザーが所有するGitHubリポジトリの一覧と関連情報を取得する役割を担います。
- **src/gh_pr_phase_monitor/pr_fetcher.py**: 特定のリポジトリ内のプルリクエスト（PR）の詳細情報を取得します。PRのタイトル、ステータス、コメントなどのデータを提供します。
- **src/gh_pr_phase_monitor/issue_fetcher.py**: 特定のリポジトリ内のIssue情報を取得します。特に、オープンPRがない場合に表示するIssueのリストを取得するために使用されます。
- **src/gh_pr_phase_monitor/comment_fetcher.py**: プルリクエストに投稿されたコメントの履歴を取得し、特定のコメント（例: Copilotレビューコメント）の有無を判定するために利用されます。
- **src/gh_pr_phase_monitor/phase_detector.py**: プルリクエストの現在の状態に基づいて、それがどのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中など）にあるかを判定するロジックを提供します。
- **src/gh_pr_phase_monitor/comment_manager.py**: プルリクエストへの自動コメント投稿機能に関連する処理を管理します。フェーズに応じた定型コメントの投稿などを担当します。
- **src/gh_pr_phase_monitor/pr_actions.py**: プルリクエストを「Ready for review」状態にしたり、ブラウザでPRページを開いたりするなどの直接的なアクションを実行します。
- **src/gh_pr_phase_monitor/browser_automation.py**: PyAutoGUIライブラリを利用して、ブラウザ上での操作（ボタンクリック、ページのURLオープンなど）を自動化するための機能を提供します。
- **src/gh_pr_phase_monitor/notifier.py**: ntfy.shサービスを通じて、モバイル端末にプッシュ通知を送信する機能を提供します。PRの重要な状態変化をユーザーに知らせます。
- **src/gh_pr_phase_monitor/monitor.py**: 定期的な監視ロジックと、検出されたPRの状態変化に応じたアクションのトリガーを管理する中心的なモジュールです。
- **src/gh_pr_phase_monitor/state_tracker.py**: 各リポジトリやPRの過去の状態を追跡し、状態変化がない期間を監視します。これにより、省電力モードへの移行などを制御します。
- **src/gh_pr_phase_monitor/time_utils.py**: 時間のパース（文字列から時間オブジェクトへの変換）や、間隔の計算など、時間に関連するユーティリティ機能を提供します。
- **src/gh_pr_phase_monitor/wait_handler.py**: GitHub APIのレート制限や一時的なエラーに対するリトライ処理、および監視間隔における待機を管理します。
- **src/gh_pr_phase_monitor/display.py**: コンソール出力の色付け、整形、進捗状況の表示など、ユーザーへの情報提示に関する処理を行います。
- **src/gh_pr_phase_monitor/colors.py**: コンソール出力にANSIカラーコードを適用し、視覚的に分かりやすい出力を生成するためのカラー定義とユーティリティを提供します。
- **config.toml.example**: ユーザーが設定を行うための`config.toml`のテンプレートファイルです。監視間隔、通知設定、自動化フラグなどの設定例が含まれています。
- **requirements-automation.txt**: ブラウザ自動化機能（PyAutoGUIなど）を使用するために必要なPythonパッケージとそのバージョンをリストアップしています。
- **screenshots/**: PyAutoGUIによるブラウザ自動化で必要となる、クリック対象のボタンなどのスクリーンショット画像を保存するディレクトリです。
- **tests/**: `pytest`フレームワークを使用して記述された、プロジェクトの単体テスト、統合テスト、機能テストのコードを含むディレクトリです。
- **.editorconfig**: 異なる開発環境でコードスタイル（インデント、文字コードなど）を統一するための設定ファイルです。
- **.gitignore**: Gitのバージョン管理から除外すべきファイルやディレクトリ（例: ログファイル、キャッシュ、機密設定ファイルなど）を指定します。
- **LICENSE**: プロジェクトのライセンス情報（MIT License）を記載したファイルです。
- **README.md / README.ja.md**: プロジェクトの概要、特徴、セットアップ方法、使い方、注意点などを説明するドキュメント（英語および日本語）。
- **docs/**: プロジェクトのより詳細な実装ガイド、設計思想、特定の機能に関する情報などを格納するディレクトリです。

## 関数詳細説明
このプロジェクトでは、以下の主要な機能を持つ関数群が各モジュールで定義されています。具体的な関数名や引数はプロジェクト情報に明示されていませんが、各ファイルの役割から一般的な機能を推測して説明します。

- **`main.py`**:
    - `run_monitoring_loop()`: メインの監視処理を継続的に実行するループを開始します。設定された間隔でPRの状態をチェックし、必要に応じてアクションをトリガーします。
    - `load_and_validate_config()`: `config.py`を利用して設定ファイルを読み込み、その内容が正しいか検証します。
- **`config.py`**:
    - `load_config(config_path)`: 指定されたパスから`config.toml`ファイルを読み込み、設定オブジェクトを返します。
    - `validate_rulesets(rulesets)`: `config.toml`内の`[[rulesets]]`セクションの設定が適切であるか検証します。
- **`github_client.py` / `graphql_client.py`**:
    - `query_github_api(query, variables)`: GitHub API（RESTまたはGraphQL）に対してクエリを送信し、結果を返します。認証処理やエラーハンドリングを含みます。
    - `fetch_open_prs(repo_name)`: 指定されたリポジトリのオープンなプルリクエスト情報を取得します。
- **`phase_detector.py`**:
    - `detect_pr_phase(pr_info)`: 特定のプルリクエスト情報（`pr_info`）を分析し、そのPRが現在どのフェーズ（phase1, phase2, phase3, LLM workingなど）にあるかを判定して返します。
- **`comment_manager.py`**:
    - `post_comment_to_pr(pr_id, comment_body)`: 指定されたプルリクエスト（`pr_id`）に、指定された内容（`comment_body`）のコメントを投稿します。
    - `has_agent_comment(pr_id, agent_name)`: 特定のエージェント（例: `copilot-pull-request-reviewer`）がPRにコメントを投稿しているかを確認します。
- **`pr_actions.py`**:
    - `mark_pr_as_ready(pr_id)`: 指定されたドラフトプルリクエストを「Ready for review」状態に変更します。
    - `open_pr_in_browser(pr_url)`: 指定されたPRのURLをユーザーのデフォルトブラウザで開きます。
- **`browser_automation.py`**:
    - `click_button_by_screenshot(image_path, confidence)`: 指定されたスクリーンショット画像（`image_path`）に一致するボタンを画面上で探し、クリックします。`confidence`は一致度の閾値です。
    - `open_url(url)`: 指定されたURLをデフォルトブラウザで開きます。
- **`notifier.py`**:
    - `send_ntfy_notification(topic, message, url, priority)`: ntfy.shサービスを利用して、指定されたトピックにメッセージやURLを含むプッシュ通知を送信します。
- **`monitor.py`**:
    - `process_repository(repo_info, config)`: 個々のリポジトリを処理し、その中のPRの状態をチェックし、フェーズ判定に基づいて必要なアクション（コメント投稿、通知など）を決定・実行します。
- **`state_tracker.py`**:
    - `update_pr_state(pr_id, new_phase)`: 特定のPRのフェーズが変更されたことを記録し、状態変化がない期間を追跡します。
    - `should_enter_reduced_frequency_mode()`: 一定期間PRの状態に変化がなかった場合、API呼び出し頻度を減らす「省電力モード」に入るべきかを判定します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。

---
Generated at: 2026-02-02 07:02:10 JST
