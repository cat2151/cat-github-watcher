Last updated: 2026-03-20

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのPRを監視し、その状態に応じて適切な通知やアクションを実行するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GitHub GraphQL APIを利用して効率的にプルリクエストを監視します。
- PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定し、自動コメント投稿、PR Ready化、モバイル通知、自動マージなどの機能を提供します。

## 技術スタック
- フロントエンド: PyAutoGUI (ブラウザ自動操作), PyGetWindow (ウィンドウ管理), Pillow (画像処理), pytesseract (OCRによるテキスト検出), tesseract-ocr (OCRエンジン)。これらはGitHubのWeb UIを自動操作するために使用されます。
- 開発ツール: GitHub CLI (`gh`, GitHub認証と一部操作に利用), git (バージョン管理), ruff (高速なPythonリンタ・フォーマッタ), TOML (設定ファイル形式), pytest (テストフレームワーク)。
- テスト: pytest (Pythonコードの単体テストおよび結合テストに使用)。
- ビルドツール: pip (Pythonパッケージ管理), cargo (Rustプロジェクトのバイナリ自動更新に利用)。
- 言語機能: Python 3.11+ (プロジェクトの主要な開発言語およびランタイム)。
- 自動化・CI/CD: GitHub Actions (READMEファイルの自動生成などに利用), auto_git_pull (ローカルリポジトリの自動更新機能), cargo install --force (Rustバイナリの自動更新機能)。
- 開発標準: .editorconfig (エディタの設定を統一), ruff.toml (ruffリンタ・フォーマッタの設定)。
- 通知サービス: ntfy.sh (モバイル端末への通知送信に利用)。
- GitHub API: GraphQL API (PR、リポジトリ、Issue情報の効率的な取得に利用)。

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
(※提供された情報が上記の簡略形と、詳細なファイル階層リストが混在していたため、詳細なファイル階層ツリーを再構成します)
```
cat-github-watcher/
├── .editorconfig
├── .gitignore
├── .vscode/
│   └── settings.json
├── LICENSE
├── README.ja.md
├── README.md
├── _config.yml
├── cat-github-watcher.py
├── config.toml.example
├── demo_automation.py
├── docs/
│   ├── RULESETS.md
│   ├── button-detection-improvements.ja.md
│   └── window-activation-feature.md
├── fetch_pr_html.py
├── generated-docs/
├── pyproject.toml
├── pytest.ini
├── requirements-automation.txt
├── ruff.toml
├── screenshots/
│   ├── assign.png
│   └── assign_to_copilot.png
├── src/
│   ├── __init__.py
│   └── gh_pr_phase_monitor/
│       ├── __init__.py
│       ├── actions/
│       │   ├── __init__.py
│       │   └── pr_actions.py
│       ├── browser/
│       │   ├── __init__.py
│       │   ├── browser_automation.py
│       │   ├── browser_cooldown.py
│       │   ├── button_clicker.py
│       │   ├── click_config_validator.py
│       │   ├── issue_assigner.py
│       │   └── window_manager.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── colors.py
│       │   ├── config.py
│       │   ├── config_printer.py
│       │   ├── config_ruleset.py
│       │   ├── interval_parser.py
│       │   ├── process_utils.py
│       │   └── time_utils.py
│       ├── github/
│       │   ├── __init__.py
│       │   ├── comment_fetcher.py
│       │   ├── comment_manager.py
│       │   ├── etag_checker.py
│       │   ├── github_auth.py
│       │   ├── github_client.py
│       │   ├── graphql_client.py
│       │   ├── issue_etag_checker.py
│       │   ├── issue_fetcher.py
│       │   ├── pr_fetcher.py
│       │   ├── rate_limit_handler.py
│       │   └── repository_fetcher.py
│       ├── main.py
│       ├── monitor/
│       │   ├── __init__.py
│       │   ├── auto_updater.py
│       │   ├── error_logger.py
│       │   ├── iteration_runner.py
│       │   ├── local_repo_cargo.py
│       │   ├── local_repo_checker.py
│       │   ├── local_repo_git.py
│       │   ├── local_repo_watcher.py
│       │   ├── monitor.py
│       │   ├── pages_watcher.py
│       │   ├── pr_processor.py
│       │   ├── snapshot_path_utils.py
│       │   └── state_tracker.py
│       ├── phase/
│       │   ├── __init__.py
│       │   ├── html/
│       │   │   ├── __init__.py
│       │   │   ├── html_status_processor.py
│       │   │   ├── llm_status_extractor.py
│       │   │   ├── pr_html_analyzer.py
│       │   │   ├── pr_html_fetcher.py
│       │   │   └── pr_html_saver.py
│       │   └── phase_detector.py
│       └── ui/
│           ├── __init__.py
│           ├── display.py
│           ├── notification_window.py
│           ├── notifier.py
│           └── wait_handler.py
└── tests/
    ├── test_assign_issue_to_copilot.py
    ├── ... (多数のテストファイル)
    └── test_wait_handler_callback.py
```

## ファイル詳細説明
-   `cat-github-watcher.py`: プロジェクトのメインエントリーポイントとなるスクリプトで、監視ツールを起動します。
-   `src/gh_pr_phase_monitor/main.py`: プロジェクトのコアロジックを含むメイン実行ループを定義し、各モジュールの協調動作をオーケストレーションします。
-   `src/gh_pr_phase_monitor/core/config.py`: アプリケーションの設定ファイル (`config.toml`) を読み込み、解析、検証する役割を担います。
-   `src/gh_pr_phase_monitor/github/github_client.py`: GitHub GraphQL APIとの主要なインターフェースを提供し、認証やリクエストの送信を管理します。
-   `src/gh_pr_phase_monitor/phase/phase_detector.py`: プルリクエストの現在のフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を判定するロジックを実装しています。
-   `src/gh_pr_phase_monitor/actions/pr_actions.py`: プルリクエストに対する具体的なアクション（例: Draft PRのReady化、コメント投稿、PRマージ、ブラウザでのPRページ開設）を実行します。
-   `src/gh_pr_phase_monitor/github/comment_manager.py`: PRへのコメント投稿や既存コメントの確認を行います。
-   `src/gh_pr_phase_monitor/github/pr_fetcher.py`: GitHubからプルリクエストの情報を取得する機能を提供します。
-   `src/gh_pr_phase_monitor/github/repository_fetcher.py`: GitHubユーザーが所有するリポジトリの一覧を取得する機能を提供します。
-   `src/gh_pr_phase_monitor/browser/browser_automation.py`: ブラウザを介したUI操作の自動化ロジックを統括します。
-   `src/gh_pr_phase_monitor/browser/button_clicker.py`: 画像認識やOCRを用いてブラウザ上の特定のボタンを検出し、クリックする処理を担当します。
-   `src/gh_pr_phase_monitor/browser/issue_assigner.py`: 特定の条件を満たすIssueをCopilotなどのエージェントに自動的に割り当てるためのブラウザ操作を管理します。
-   `src/gh_pr_phase_monitor/monitor/auto_updater.py`: ツール自身が最新版に更新されているかチェックし、必要に応じて自動的にgit pullして再起動する機能を提供します。
-   `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`: 親ディレクトリ内のローカルGitリポジトリのpull可能状態を監視し、必要に応じて自動pullを行います。
-   `src/gh_pr_phase_monitor/ui/notifier.py`: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
-   `config.toml.example`: ユーザーがカスタマイズできる設定ファイルの例と、各設定項目の説明を含んでいます。
-   `screenshots/`: ブラウザ自動化機能で使用する、ボタンのスクリーンショット画像が保存されるディレクトリです。
-   `tests/`: プロジェクトの各機能が正しく動作するか検証するためのテストスイートが格納されています。

## 関数詳細説明
プロジェクト情報には個別の関数に関する詳細情報（引数、戻り値など）は含まれていませんが、主要な機能モジュールが提供する役割に基づいて、以下に主な機能カテゴリと関連する関数群の役割を説明します。

-   **メイン監視ループ関連**:
    -   `gh_pr_phase_monitor.main.py` に含まれる関数群は、プロジェクト全体の監視ループを開始し、一定間隔でGitHubのプルリクエストやローカルリポジトリの状態をチェックし、各サブコンポーネントを調整する役割を担います。
-   **設定管理関連**:
    -   `gh_pr_phase_monitor.core.config.py` に含まれる関数群は、`config.toml` ファイルの読み込み、設定値の解析、バリデーション、およびルールセットの適用といった設定管理全般を担います。
-   **GitHub API連携関連**:
    -   `gh_pr_phase_monitor.github.github_client.py` を中心とする `github/` ディレクトリ内の関数群は、GitHub GraphQL APIへの認証、クエリの構築、リクエストの送信、PRやリポジトリ、Issue情報の取得、ETagによるキャッシュ管理、レートリミットのハンドリングなど、GitHub APIとの全てのインタラクションを処理します。
-   **PRフェーズ判定関連**:
    -   `gh_pr_phase_monitor.phase.phase_detector.py` を中心とする `phase/` ディレクトリ内の関数群は、PRのタイトル、ラベル、レビューコメント、レビューの状態（未解決のスレッドの有無など）を分析し、PRがどの開発フェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）にあるかを判定するロジックを提供します。
-   **PRアクション実行関連**:
    -   `gh_pr_phase_monitor.actions.pr_actions.py` に含まれる関数群は、判定されたPRフェーズに基づいて、Draft PRのReady化、指定されたコーディングエージェントへのコメント投稿、PRの自動マージなどの具体的なGitHub上の操作を実行します。
-   **ブラウザ自動化関連**:
    -   `gh_pr_phase_monitor.browser/` ディレクトリ内の関数群は、`PyAutoGUI` を用いてブラウザウィンドウを操作し、GitHubのWeb UI上で特定のボタン（例: "Assign to Copilot", "Merge pull request"）を検出してクリックしたり、ウィンドウを管理したりする機能を提供します。OCRによるテキスト検出をフォールバックとして使用することもあります。
-   **通知関連**:
    -   `gh_pr_phase_monitor.ui.notifier.py` に含まれる関数群は、`ntfy.sh` サービスを利用して、PRがレビュー待ちフェーズに移行した際などにモバイル端末へ通知を送信する機能を提供します。
-   **自己更新・ローカルリポジトリ監視関連**:
    -   `gh_pr_phase_monitor.monitor/` ディレクトリ内の関数群は、ツールの自動更新チェック、ローカルGitリポジトリのpull可能状態の監視と自動pull、およびRustプロジェクトのバイナリを自動更新する機能などを担います。

## 関数呼び出し階層ツリー
```
プロジェクト情報に具体的な関数呼び出し階層のデータが提供されていないため、詳細なツリーは生成できません。しかし、プロジェクトは単一責任の原則に基づいてモジュール化されており、`src/gh_pr_phase_monitor/main.py` が全体の監視ループとオーケストレーションを担い、各モジュール（例: `github_client.py`, `phase_detector.py`, `pr_actions.py`）内の関数がそれぞれの専門機能を提供し、相互に連携する構造になっています。

---
Generated at: 2026-03-20 07:03:34 JST
