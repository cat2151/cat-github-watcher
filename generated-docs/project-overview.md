Last updated: 2026-03-09

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト（PR）を効率的に監視するPythonツールです。
- PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動検知し、適切なタイミングで通知やアクションを実行します。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIとブラウザ自動操作を活用して運用を支援します。

## 技術スタック
- フロントエンド: PyAutoGUI (Pythonライブラリを使用し、ブラウザのボタンクリックやウィンドウ操作を自動化します)
- 音楽・オーディオ: 該当なし
- 開発ツール:
    - GitHub CLI (`gh`): GitHub認証やリポジトリ操作に利用されるコマンドラインツールです。
    - `pytest`: Pythonコードのテストフレームワークです。
    - `ruff`: 高速なPythonリンターおよびフォーマッターです。
- テスト: `pytest` (プロジェクトの品質を保証するためのテストスイートに使用されます)
- ビルドツール:
    - Python (`pip`): パッケージのインストールと管理に使用されます。
    - `pyproject.toml`: Pythonプロジェクトのメタデータとビルド設定を定義するファイルです。
- 言語機能: Python 3.11+ (本プロジェクトの基盤となるプログラミング言語バージョンです)
- 自動化・CI/CD:
    - GitHub Actions: READMEドキュメントの自動生成などに利用される継続的インテグレーション/デプロイメントサービスです。
    - `ntfy.sh`: モバイル端末への通知を送信するためのシンプルなパブリッシュ/サブスクライブサービスです。
    - `PyAutoGUI`: マウス、キーボード、画面操作を自動化し、ブラウザベースのタスクを実行します。
    - `tesseract-ocr`: PyAutoGUIのOCRフォールバック機能で使用されるオープンソースの光学文字認識エンジンです。
- 開発標準:
    - `.editorconfig`: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
    - `ruff.toml`: Ruffリンターの設定ファイルで、コード品質とスタイルを統一します。

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
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントとなるスクリプトで、監視ツールを起動します。
- `src/gh_pr_phase_monitor/main.py`: 監視ツールの中核となる実行ロジックが含まれており、PRのフェッチ、フェーズ判定、アクション実行のループを管理します。
- `src/gh_pr_phase_monitor/core/colors.py`: ターミナル出力の色付けに使用されるANSIカラーコードとスキームを定義します。
- `src/gh_pr_phase_monitor/core/config.py`: `config.toml`ファイルから設定を読み込み、解析し、アプリケーション全体で利用できるようにします。
- `src/gh_pr_phase_monitor/github/github_client.py`: GitHub GraphQL APIとの主要なインターフェースを提供し、PRやリポジトリ情報の取得を担当します。
- `src/gh_pr_phase_monitor/github/comment_manager.py`: PRへのコメント投稿や既存コメントの確認ロジックを管理します。
- `src/gh_pr_phase_monitor/actions/pr_actions.py`: PRをReady状態にする、コメントを投稿する、PRをマージするなどの具体的なアクションを実行します。
- `src/gh_pr_phase_monitor/phase/phase_detector.py`: GitHub PRの現在の状態を分析し、`phase1`から`LLM working`までの定義されたフェーズのいずれかを判定するロジックが含まれています。
- `src/gh_pr_phase_monitor/browser/browser_automation.py`: PyAutoGUIを利用して、ブラウザ内の特定のボタンを画像認識やOCRで検出し、クリックする自動操作機能を提供します。
- `src/gh_pr_phase_monitor/browser/button_clicker.py`: `browser_automation.py`が依存する、ボタンクリックの低レベルな実装を含みます。
- `src/gh_pr_phase_monitor/browser/window_manager.py`: ブラウザウィンドウのアクティブ化や最大化など、ウィンドウ操作を管理します。
- `src/gh_pr_phase_monitor/github/graphql_client.py`: GitHub GraphQL APIへの直接的なクエリ実行を扱うモジュールです。
- `src/gh_pr_phase_monitor/github/pr_fetcher.py`: GitHubからプルリクエストのデータを取得する具体的なロジックを担います。
- `src/gh_pr_phase_monitor/monitor/monitor.py`: 監視ループの全体的な制御と、状態管理、間隔調整（省電力モードなど）を行います。
- `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`: 親ディレクトリ内のローカルリポジトリを監視し、`git pull`が必要なリポジトリを検出する機能を提供します。
- `src/gh_pr_phase_monitor/ui/notifier.py`: `ntfy.sh`サービスを通じて、モバイル端末に通知を送信する機能を提供します。
- `src/gh_pr_phase_monitor/ui/notification_window.py`: ブラウザ自動操作中に表示される小さな通知ウィンドウを管理します。
- `config.toml.example`: `config.toml`を作成する際のテンプレートとなる設定ファイルのサンプルです。
- `requirements-automation.txt`: PyAutoGUIやPillowなど、ブラウザ自動化機能に必要なPythonパッケージの一覧です。
- `screenshots/`: ブラウザ自動化機能で使用する、クリック対象のボタンのスクリーンショット画像が保存されます。
- `tests/`: プロジェクトの各モジュールや機能に対する単体テスト、結合テストが格納されています。

## 関数詳細説明
- `main.run_monitor()`: メイン監視ループを開始し、GitHub PRのフェッチ、フェーズ判定、アクション実行を定期的に繰り返します。
- `config.load_config(config_path)`: 指定されたパスから`config.toml`設定ファイルを読み込み、解析してアプリケーション設定を初期化します。
- `github_client.fetch_user_repositories()`: 認証済みGitHubユーザーが所有するすべてのリポジトリのリストを取得します。
- `github_client.fetch_pull_requests(repo_name)`: 指定されたリポジトリのオープンなプルリクエスト情報をGitHub GraphQL APIから取得します。
- `phase_detector.detect_phase(pr_data)`: プルリクエストのメタデータとコメント履歴を分析し、そのPRが現在どのフェーズ（Draft、レビュー指摘対応中など）にあるかを判定します。
- `pr_actions.execute_pr_action(pr_info, action_type, ...)`: プルリクエストに対する具体的なアクション（例: Draft解除、コメント投稿、マージ）を、設定されたルールに基づいて実行します。
- `browser_automation.click_button(button_name, ...)`: ブラウザ内で、指定された名称のボタンを画像認識またはOCR技術を用いて検出し、クリック操作を実行します。
- `notifier.send_notification(message, url, ...)`: `ntfy.sh`サービスを利用して、指定されたメッセージとURLを含む通知をモバイル端末に送信します。
- `local_repo_watcher.check_local_repos_for_pull()`: ローカルファイルシステム上のリポジトリをスキャンし、リモートに変更があり`git pull`が可能な状態かどうかを判別します。
- `auto_updater.check_and_update()`: プロジェクトの自己更新機能として、リモートリポジトリの変更をチェックし、更新があれば自動的に`git pull`して再起動します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。

---
Generated at: 2026-03-09 07:01:32 JST
