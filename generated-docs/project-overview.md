Last updated: 2026-02-07

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト（PR）を効率的に監視するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定します。
- フェーズに応じた自動コメント投稿、PRのReady化、モバイル通知、issue表示、省電力監視、ブラウザ自動化によるPRマージ・issue割り当てなどの多様なアクションをサポートします。

## 技術スタック
- フロントエンド: CLIベースのツールであるため、特定のフロントエンド技術は使用していません。
- 音楽・オーディオ: 音楽・オーディオ関連の技術は使用していません。
- 開発ツール:
    - GitHub CLI (`gh`): GitHubとの認証およびAPI操作に利用されます。
    - pytest: プロジェクトの単体テストおよび結合テストフレームワークとして採用されています。
- テスト:
    - pytest: Pythonのテストフレームワーク。プロジェクトの品質保証のために広範なテストスイートで使用されています。
- ビルドツール: Pythonスクリプトとして直接実行されるため、特定のビルドツールは使用していません。
- 言語機能:
    - Python 3.x: プロジェクトの主要なプログラミング言語です。
    - TOML: `config.toml`ファイルとして設定管理に使用されています。
    - GraphQL API: GitHub APIとの効率的なデータ取得のために使用されています。
- 自動化・CI/CD:
    - PyAutoGUI: ブラウザ自動化（画面上のボタン検出とクリック）に使用されます。
    - pillow, pygetwindow: PyAutoGUIの依存ライブラリとして画像処理とウィンドウ管理に利用されます。
    - tesseract-ocr / pytesseract: 画像認識が失敗した場合のOCR（光学文字認識）フォールバックに使用されます。
    - ntfy.sh: フェーズ3（レビュー待ち）のPRをモバイル端末に通知するためのサービスです。
- 開発標準:
    - `.editorconfig`: 複数の開発環境でコードの書式設定を一貫させるために使用されます。
    - Ruff: Pythonコードの品質と一貫性を保つためのリンターおよびフォーマッターです。

## ファイル階層ツリー
```
cat-github-watcher/
├── .editorconfig
├── .gitignore
├── .vscode/
│   └── settings.json
├── LICENSE
├── MERGE_CONFIGURATION_EXAMPLES.md
├── PHASE3_MERGE_IMPLEMENTATION.md
├── README.ja.md
├── README.md
├── STRUCTURE.md
├── _config.yml
├── cat-github-watcher.py
├── config.toml.example
├── demo_automation.py
├── docs/
│   ├── IMPLEMENTATION_SUMMARY.ja.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PR67_IMPLEMENTATION.md
│   ├── RULESETS.md
│   ├── VERIFICATION_GUIDE.en.md
│   ├── VERIFICATION_GUIDE.md
│   ├── browser-automation-approaches.en.md
│   ├── browser-automation-approaches.md
│   ├── button-detection-improvements.ja.md
│   └── window-activation-feature.md
├── generated-docs/
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
│       ├── browser_automation.py
│       ├── colors.py
│       ├── comment_fetcher.py
│       ├── comment_manager.py
│       ├── config.py
│       ├── display.py
│       ├── github_auth.py
│       ├── github_client.py
│       ├── graphql_client.py
│       ├── issue_fetcher.py
│       ├── main.py
│       ├── monitor.py
│       ├── notifier.py
│       ├── phase_detector.py
│       ├── pr_actions.py
│       ├── pr_fetcher.py
│       ├── repository_fetcher.py
│       ├── state_tracker.py
│       ├── time_utils.py
│       └── wait_handler.py
└── tests/
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_check_process_before_autoraise.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_contamination_bug.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
    ├── test_max_llm_working_parallel.py
    ├── test_no_change_timeout.py
    ├── test_no_open_prs_issue_display.py
    ├── test_notification.py
    ├── test_phase3_merge.py
    ├── test_phase_detection.py
    ├── test_post_comment.py
    ├── test_post_phase3_comment.py
    ├── test_pr_actions.py
    ├── test_pr_actions_rulesets_features.py
    ├── test_pr_actions_with_rulesets.py
    ├── test_repos_with_prs_structure.py
    ├── test_show_issues_when_pr_count_less_than_3.py
    ├── test_status_summary.py
    ├── test_validate_phase3_merge_config.py
    └── test_verbose_config.py
```

## ファイル詳細説明
- **`.editorconfig`**: エディタの設定を定義し、コーディングスタイルの一貫性を保つためのファイルです。
- **`.gitignore`**: Gitがバージョン管理の対象外とするファイルやディレクトリを指定します。
- **`.vscode/settings.json`**: VS Codeエディタのワークスペース固有の設定ファイルです。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記述しています。
- **`MERGE_CONFIGURATION_EXAMPLES.md`**: PRマージ設定の具体例を示すドキュメントです。
- **`PHASE3_MERGE_IMPLEMENTATION.md`**: フェーズ3におけるPR自動マージ機能の実装詳細に関するドキュメントです。
- **`README.ja.md`**: プロジェクトの日本語版の概要、特徴、使い方などを説明するメインドキュメントです。
- **`README.md`**: プロジェクトの英語版の概要、特徴、使い方などを説明するメインドキュメントです。
- **`STRUCTURE.md`**: プロジェクトの全体的な構造や設計思想に関するドキュメントです。
- **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレータで利用される可能性のある設定ファイルです。
- **`cat-github-watcher.py`**: プロジェクトのメインエントリーポイントとなるスクリプトで、ツールを起動するために使用されます。
- **`config.toml.example`**: ユーザーが`config.toml`を作成する際のテンプレートとなる設定ファイルの例です。
- **`demo_automation.py`**: 自動化機能の動作をデモンストレーションするためのスクリプトです。
- **`docs/`**: プロジェクトに関する詳細なドキュメントを格納するディレクトリです。
    - **`docs/IMPLEMENTATION_SUMMARY.ja.md` / `docs/IMPLEMENTATION_SUMMARY.md`**: 実装の概要を日本語と英語でまとめたドキュメントです。
    - **`docs/PR67_IMPLEMENTATION.md`**: 特定のプルリクエスト（PR #67）の実装に関する詳細ドキュメントです。
    - **`docs/RULESETS.md`**: 設定ファイルにおけるルールセットの定義と使用方法に関するドキュメントです。
    - **`docs/VERIFICATION_GUIDE.en.md` / `docs/VERIFICATION_GUIDE.md`**: ツールの検証方法を英語と日本語で説明するガイドです。
    - **`docs/browser-automation-approaches.en.md` / `docs/browser-automation-approaches.md`**: ブラウザ自動化のアプローチについて英語と日本語で考察するドキュメントです。
    - **`docs/button-detection-improvements.ja.md`**: ボタン検出機能の改善点について日本語で解説するドキュメントです。
    - **`docs/window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメントです。
- **`generated-docs/`**: AI生成など、自動で生成されたドキュメントを格納するディレクトリです。
- **`pytest.ini`**: pytestテストフレームワークの設定ファイルです。
- **`requirements-automation.txt`**: ブラウザ自動化機能に必要な追加のPythonライブラリ（PyAutoGUI, pytesseractなど）をリストアップしたファイルです。
- **`ruff.toml`**: PythonコードのリンティングおよびフォーマットツールであるRuffの設定ファイルです。
- **`screenshots/`**: PyAutoGUIによるブラウザ自動化で使用されるボタンのスクリーンショット画像が保存されます。
    - **`screenshots/assign.png`**: 「Assign」ボタンのスクリーンショット。
    - **`screenshots/assign_to_copilot.png`**: 「Assign to Copilot」ボタンのスクリーンショット。
- **`src/`**: プロジェクトの主要なPythonソースコードを格納するディレクトリです。
    - **`src/gh_pr_phase_monitor/`**: PR監視ツールの中核となるモジュール群です。
        - **`src/gh_pr_phase_monitor/browser_automation.py`**: ブラウザの自動操作（ボタンクリックなど）に関連する機能を提供します。
        - **`src/gh_pr_phase_monitor/colors.py`**: ターミナル出力に色を付けるためのANSIカラーコードと関連ユーティリティを定義します。
        - **`src/gh_pr_phase_monitor/comment_fetcher.py`**: GitHub PRのコメントを取得するロジックを扱います。
        - **`src/gh_pr_phase_monitor/comment_manager.py`**: PRへのコメント投稿や管理のロジックをカプセル化します。
        - **`src/gh_pr_phase_monitor/config.py`**: `config.toml`から設定を読み込み、解析し、バリデーションを行うモジュールです。
        - **`src/gh_pr_phase_monitor/display.py`**: 監視結果やステータス情報をコンソールに整形して表示するための機能を提供します。
        - **`src/gh_pr_phase_monitor/github_auth.py`**: GitHub CLIを用いた認証フローを管理します。
        - **`src/gh_pr_phase_monitor/github_client.py`**: GitHub REST APIおよびGraphQL APIと連携するための高レベルなインターフェースを提供します。
        - **`src/gh_pr_phase_monitor/graphql_client.py`**: GitHub GraphQL APIへの直接的なリクエスト処理を扱います。
        - **`src/gh_pr_phase_monitor/issue_fetcher.py`**: GitHubからIssue情報を取得するロジックを実装します。
        - **`src/gh_pr_phase_monitor/main.py`**: アプリケーションのメイン実行ループと、監視プロセス全体の調整を行います。
        - **`src/gh_pr_phase_monitor/monitor.py`**: 定期的なPR監視サイクルを管理し、状態の変化を検出します。
        - **`src/gh_pr_phase_monitor/notifier.py`**: ntfy.shサービスを通じてモバイル通知を送信する機能を提供します。
        - **`src/gh_pr_phase_monitor/phase_detector.py`**: PRの現在のフェーズ（phase1, phase2, phase3, LLM working）を判定するロジックを含みます。
        - **`src/gh_pr_phase_monitor/pr_actions.py`**: PRのReady化、ブラウザ起動、自動マージといった具体的なアクションを実行します。
        - **`src/gh_pr_phase_monitor/pr_fetcher.py`**: GitHubからプルリクエストの情報を取得するロジックを扱います。
        - **`src/gh_pr_phase_monitor/repository_fetcher.py`**: 認証済みユーザーが所有するGitHubリポジトリのリストを取得します。
        - **`src/gh_pr_phase_monitor/state_tracker.py`**: 各PRの状態（フェーズ）の変化を追跡し、タイムアウトや省電力モードの基準を管理します。
        - **`src/gh_pr_phase_monitor/time_utils.py`**: 時間間隔のパース、タイムスタンプの生成など、時間に関するユーティリティ関数を提供します。
        - **`src/gh_pr_phase_monitor/wait_handler.py`**: 監視間隔の待機処理を制御し、省電力モードへの切り替えロジックを管理します。
- **`tests/`**: プロジェクトのテストコードを格納するディレクトリです。
    - **`tests/test_*.py`**: 各機能のテストケースを定義するファイル群です。

## 関数詳細説明
このプロジェクトでは、各モジュールが単一責任の原則に従って設計されており、主要な機能はそれぞれのファイル内で関数として実装されています。具体的な関数名やシグネチャは明示されていませんが、各モジュールの役割から以下の様な関数群が推測されます。

- **`config.py`**
    - `load_config(config_path: str) -> dict`: 指定されたパスからTOML形式の設定ファイルを読み込み、解析して辞書形式で返します。設定値のバリデーションやデフォルト値の適用も行います。
    - `parse_interval(interval_str: str) -> int`: "1m", "30s"のような文字列形式の時間間隔を秒単位の整数に変換します。
- **`github_client.py` / `graphql_client.py`**
    - `fetch_user_repositories() -> list`: 認証済みユーザーが所有する全リポジトリのリストを取得します。
    - `fetch_prs_for_repo(repo_name: str) -> list`: 指定されたリポジトリのオープンなプルリクエスト情報を取得します。
    - `post_comment_to_pr(pr_id: str, comment_body: str) -> bool`: 指定されたPRにコメントを投稿します。
    - `mark_pr_as_ready(pr_id: str) -> bool`: ドラフト状態のPRをレビュー可能な状態に設定します。
    - `merge_pr(pr_id: str) -> bool`: 指定されたPRをマージします。
- **`phase_detector.py`**
    - `detect_pr_phase(pr_data: dict) -> str`: プルリクエストのデータに基づいて、現在のフェーズ（`phase1`, `phase2`, `phase3`, `LLM working`）を判定し、文字列で返します。
- **`comment_manager.py`**
    - `post_phase2_comment(pr_id: str) -> bool`: Phase2のPRに対して、Copilotに変更適用を依頼するコメントを投稿します。
- **`pr_actions.py`**
    - `open_pr_in_browser(pr_url: str)`: 指定されたPRのURLをデフォルトのウェブブラウザで開きます。
    - `execute_phase3_merge(pr_id: str, config: dict) -> bool`: Phase3のPRを自動的にマージする処理を実行します。ブラウザ自動化を利用する場合があります。
- **`notifier.py`**
    - `send_ntfy_notification(topic: str, message: str, url: str, priority: int)`: ntfy.shサービスを使用してモバイル通知を送信します。
- **`issue_fetcher.py`**
    - `fetch_issues_for_repo(repo_name: str, limit: int) -> list`: 指定されたリポジトリのオープンなIssueを、指定された数の上限で取得します。
- **`browser_automation.py`**
    - `find_and_click_button(button_name: str, confidence: float) -> bool`: スクリーンショットと画像認識を用いて、画面上の特定のボタンを検出しクリックします。OCRフォールバック機能も持ちます。
- **`main.py` / `monitor.py`**
    - `run_monitor_loop(config: dict)`: メインの監視ループを実行します。設定された間隔でPR情報の取得、フェーズ判定、アクション実行を繰り返します。
    - `process_repository(repo_data: dict, config: dict)`: 単一のリポジトリ内のPRを処理し、各PRのフェーズに応じたアクションを実行します。

## 関数呼び出し階層ツリー
```
提供された情報では、具体的な関数呼び出し階層の分析はできませんでした。
しかし、プロジェクトのアーキテクチャ概要と各ファイルの役割に基づき、以下のような主要な呼び出しフローが想定されます。

run_monitor_loop (main.py/monitor.py)
├── load_config (config.py)
├── fetch_user_repositories (repository_fetcher.py/github_client.py)
├── process_repository (monitor.py)
│   ├── fetch_prs_for_repo (pr_fetcher.py/github_client.py)
│   ├── detect_pr_phase (phase_detector.py)
│   ├── post_phase2_comment (comment_manager.py)
│   ├── mark_pr_as_ready (pr_actions.py/github_client.py)
│   ├── open_pr_in_browser (pr_actions.py)
│   ├── send_ntfy_notification (notifier.py)
│   ├── execute_phase3_merge (pr_actions.py)
│   │   └── find_and_click_button (browser_automation.py)
│   ├── fetch_issues_for_repo (issue_fetcher.py)
│   └── find_and_click_button (browser_automation.py) - for issue assignment
└── parse_interval (time_utils.py)

---
Generated at: 2026-02-07 07:02:08 JST
