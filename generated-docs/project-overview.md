Last updated: 2026-02-09

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装のプルリクエスト（PR）を効率的に監視するPythonツールです。
- 認証済みGitHubユーザーが所有するリポジトリのPRを対象に、GraphQL APIを用いて状態を把握します。
- PRの進捗フェーズ（Draft、レビュー指摘対応中、レビュー待ちなど）を自動判定し、状況に応じた通知や自動アクションを実行します。

## 技術スタック
- フロントエンド: PyAutoGUI (GUI自動化によるブラウザ操作)
  - PyAutoGUI, PyGetWindow, Pillowを利用して、ブラウザ上でのボタンクリックやウィンドウ管理などのGUI操作を自動化します。
- 音楽・オーディオ: なし
- 開発ツール: Python, GitHub CLI (gh), DeepWiki
  - Python 3.10以上を主要言語として使用。GitHub CLIで認証とリポジトリ操作を効率化。DeepWikiはプロジェクト情報の参照に利用されます。
- テスト: pytest
  - Pythonアプリケーションの機能テストを行うためのテストフレームワーク。
- ビルドツール: なし
  - Pythonスクリプトとして直接実行されるため、特定のビルドツールは使用していません。
- 言語機能: Python 3.10+
  - 堅牢なスクリプトとアプリケーション開発のための主要言語として利用。
- 自動化・CI/CD: ntfy.sh (通知), PyAutoGUI (ブラウザ自動操作)
  - ntfy.shを通じてモバイルデバイスへのリアルタイム通知を送信。PyAutoGUIはブラウザ上でのGUI操作を自動化し、PRのマージやIssueの割り当てを支援します。
- 開発標準: ruff, .editorconfig
  - Ruffリンターでコードの品質と一貫性を自動的にチェックし、.editorconfigで様々なエディタ間のコードスタイルを統一します。

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
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントであり、アプリケーションの起動と主要な処理の流れを制御します。
- `config.toml.example`: アプリケーションの設定例を示すファイルで、ユーザーが`config.toml`を作成する際のテンプレートとなります。
- `demo_automation.py`: ブラウザ自動化機能のデモンストレーション用スクリプト、またはテスト用スクリプトとして機能します。
- `pytest.ini`: `pytest`フレームワークのテスト実行設定を定義するファイルです。
- `requirements-automation.txt`: ブラウザ自動化機能に必要なPythonライブラリのリストを定義します。
- `ruff.toml`: Ruffリンターの設定ファイルで、コードの品質とスタイルチェックに関するルールが定義されています。
- `.editorconfig`: 様々なエディタやIDEでコードのインデントや文字コードなどを統一するための設定ファイルです。
- `.gitignore`: Gitがバージョン管理の対象としないファイルやディレクトリを指定するファイルです。
- `LICENSE`: プロジェクトのライセンス情報（MIT License）を記載したファイルです。
- `MERGE_CONFIGURATION_EXAMPLES.md`: マージ設定の具体的な例や使用方法を説明するドキュメントです。
- `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3でのPR自動マージ機能の実装詳細に関するドキュメントです。
- `README.ja.md`: プロジェクトの概要、使い方、特徴などを説明する日本語版のメインドキュメントです。
- `README.md`: プロジェクトの概要、使い方、特徴などを説明する英語版のメインドキュメントです。
- `STRUCTURE.md`: プロジェクトの全体的な構造や設計思想について説明するドキュメントです。
- `_config.yml`: GitHub Pagesなどでドキュメントを公開する際のサイト設定ファイルです。
- `.vscode/settings.json`: Visual Studio Codeエディタのワークスペース設定ファイルです。
- `generated-docs/`: AIによって生成されたドキュメントや一時的なドキュメントを格納するディレクトリです。
- `screenshots/`: ブラウザ自動化機能（PyAutoGUI）で使用されるボタンなどの画像テンプレートを保存するディレクトリです。
- `src/__init__.py`: Pythonパッケージの初期化ファイルです。
- `src/gh_pr_phase_monitor/__init__.py`: `gh_pr_phase_monitor`パッケージの初期化ファイルです。
- `src/gh_pr_phase_monitor/browser_automation.py`: PyAutoGUIなどのライブラリを使用して、ブラウザ上でのボタンクリックやウィンドウ操作といったGUI自動化機能を提供します。
- `src/gh_pr_phase_monitor/colors.py`: ANSIカラーコードを定義し、コンソール出力に色を付けて視認性を向上させるためのユーティリティを提供します。
- `src/gh_pr_phase_monitor/comment_fetcher.py`: 特定のプルリクエストに投稿されたコメントを取得する機能を提供します。
- `src/gh_pr_phase_monitor/comment_manager.py`: プルリクエストへのコメント投稿や既存コメントの確認など、コメント関連の操作を管理します。
- `src/gh_pr_phase_monitor/config.py`: `config.toml`ファイルから設定を読み込み、パースし、アプリケーション全体で利用可能な設定オブジェクトを提供します。
- `src/gh_pr_phase_monitor/display.py`: コンソール出力のフォーマットや色付けを管理し、ユーザーに情報を分かりやすく表示するための機能を提供します。
- `src/gh_pr_phase_monitor/github_auth.py`: GitHub CLI (`gh`) を利用した認証情報の取得など、GitHub認証に関連する機能を提供します。
- `src/gh_pr_phase_monitor/github_client.py`: GitHub GraphQL APIと連携し、リポジトリやプルリクエストに関する情報を取得・更新するための高レベルなインターフェースを提供します。
- `src/gh_pr_phase_monitor/graphql_client.py`: 低レベルなGraphQL APIリクエストの実行とレスポンスの処理を担当し、`github_client.py`に抽象化された機能を提供します。
- `src/gh_pr_phase_monitor/issue_fetcher.py`: オープンなIssueの情報を取得し、特にCopilotへの自動割り当て候補となるIssueを特定するのに利用されます。
- `src/gh_pr_phase_monitor/main.py`: アプリケーションのメイン実行ループを定義し、設定の初期化、監視プロセスの開始、エラーハンドリングなどを担当します。
- `src/gh_pr_phase_monitor/monitor.py`: プルリクエスト監視の中心的なロジックを実装し、定期的なデータ取得とフェーズ判定、アクション実行を調整します。
- `src/gh_pr_phase_monitor/notifier.py`: ntfy.shサービスを利用して、指定されたトピックに通知メッセージを送信する機能を提供します。
- `src/gh_pr_phase_monitor/phase_detector.py`: プルリクエストのタイトル、ステータス、コメントなどを分析し、そのPRがどの開発フェーズにあるかを判定するロジックを実装しています。
- `src/gh_pr_phase_monitor/pr_actions.py`: プルリクエストのDraft状態をReadyに変更したり、特定のPRページをブラウザで開いたり、PRを自動マージしたりする具体的なアクションを定義します。
- `src/gh_pr_phase_monitor/pr_data_recorder.py`: プルリクエストの履歴データや状態変化を記録し、分析や状態追跡に利用する機能を提供します。
- `src/gh_pr_phase_monitor/pr_fetcher.py`: 特定のリポジトリ内のオープンなプルリクエストに関する詳細情報を取得する機能を提供します。
- `src/gh_pr_phase_monitor/repository_fetcher.py`: ユーザーが所有するGitHubリポジトリの一覧を取得する機能を提供します。
- `src/gh_pr_phase_monitor/state_tracker.py`: 各プルリクエストの状態変化を追跡し、一定期間変化がない場合に省電力モードへ切り替えるためのロジックを管理します。
- `src/gh_pr_phase_monitor/time_utils.py`: 時間のパース、期間の計算、遅延処理など、時間に関連するユーティリティ機能を提供します。
- `src/gh_pr_phase_monitor/wait_handler.py`: アプリケーションの監視ループにおける待機時間を管理し、通常の監視間隔と省電力モードでの間隔切り替えを制御します。
- `tests/`: プロジェクトの各機能が正しく動作するかを検証するためのテストスクリプトが格納されているディレクトリです。各`test_*.py`ファイルは特定の機能やコンポーネントのテストを担当します。
- `docs/`: プロジェクトに関する追加のドキュメントが格納されているディレクトリです。各ファイルは具体的な機能や実装の詳細、検証ガイドなどを説明しています。

## 関数詳細説明
- `src/gh_pr_phase_monitor/main.py`: アプリケーションのメインループを制御する関数（例: `run_monitor`）や、初期設定と起動処理を行う関数が含まれます。
- `src/gh_pr_phase_monitor/config.py`: `config.toml`ファイルを読み込み、設定値をパースして検証する関数（例: `load_config`, `parse_interval_string`）を提供します。
- `src/gh_pr_phase_monitor/github_client.py`: GitHub GraphQL APIを呼び出す高レベルな関数群（例: `fetch_pull_requests`, `post_comment_to_pr`）を提供し、APIリクエストの構築とレスポンスの処理を抽象化します。
- `src/gh_pr_phase_monitor/graphql_client.py`: GraphQLクエリの実行、HTTPリクエストの送信、エラーハンドリングなど、低レベルなGraphQL API通信を行う関数（例: `execute_query`）が含まれます。
- `src/gh_pr_phase_monitor/phase_detector.py`: プルリクエストの現在の状態を分析し、`phase1`から`LLM working`までのいずれかのフェーズを判定するロジックを実装した関数群（例: `detect_phase`）を提供します。
- `src/gh_pr_phase_monitor/comment_manager.py`: プルリクエストにコメントを投稿する関数（例: `post_phase2_comment`）や、既存のコメントを確認する関数を提供します。
- `src/gh_pr_phase_monitor/pr_actions.py`: プルリクエストをReady状態に設定する関数（例: `mark_pr_as_ready`）、ブラウザでPRを開く関数（例: `open_pr_in_browser`）、PRをマージする関数（例: `merge_pr`）など、PRに対する具体的な操作を実行する関数が含まれます。
- `src/gh_pr_phase_monitor/browser_automation.py`: PyAutoGUIなどを用いてブラウザのGUIを操作する関数（例: `click_button_by_screenshot`, `find_and_click`）や、特定のテキストをOCRで検出する関数が含まれます。
- `src/gh_pr_phase_monitor/notifier.py`: ntfy.shサービスを通じて通知を送信する関数（例: `send_ntfy_notification`）を提供します。
- `src/gh_pr_phase_monitor/repository_fetcher.py`: 認証ユーザーが所有するリポジトリのリストを取得する関数（例: `fetch_user_repositories`）が含まれます。
- `src/gh_pr_phase_monitor/pr_fetcher.py`: 特定のリポジトリからオープンなプルリクエストの詳細情報を取得する関数（例: `fetch_prs_for_repository`）が含まれます。
- `src/gh_pr_phase_monitor/issue_fetcher.py`: リポジトリからIssue情報を取得し、特に自動割り当てに適したIssueをフィルタリングする関数（例: `fetch_issues`）を提供します。
- `src/gh_pr_phase_monitor/state_tracker.py`: プルリクエストの現在の状態を保存し、前回の状態と比較して変更を検知する関数（例: `update_state`, `has_state_changed`）や、タイムアウトを管理する関数が含まれます。
- `src/gh_pr_phase_monitor/time_utils.py`: 時間文字列をパースして秒数に変換する関数（例: `parse_interval_string`）、指定された時間だけスリープする関数などが含まれます。
- `src/gh_pr_phase_monitor/wait_handler.py`: 監視ループの待機間隔を管理し、省電力モードへの切り替えロジックを適用する関数（例: `get_current_wait_interval`, `handle_no_change_timeout`）を提供します。
- `src/gh_pr_phase_monitor/display.py`: コンソールに情報を出力する際に、色付けやフォーマットを適用する関数（例: `print_colored_status`, `format_pr_info`）を提供します。
- `src/gh_pr_phase_monitor/colors.py`: ANSIカラーコード定数や、文字列に色を適用するヘルパー関数（例: `colorize`）を提供します。
- `src/gh_pr_phase_monitor/github_auth.py`: GitHub CLI (`gh`) を利用してGitHub認証トークンを取得する関数（例: `get_github_token`）が含まれます。
- `src/gh_pr_phase_monitor/comment_fetcher.py`: 特定のPRのコメントを取得する関数（例: `fetch_comments_for_pr`）が含まれます。
- `src/gh_pr_phase_monitor/pr_data_recorder.py`: プルリクエストの状態データをファイルなどに記録する関数（例: `record_pr_state`）が含まれます。

## 関数呼び出し階層ツリー
```
提供された情報からは関数の呼び出し階層を特定できませんでした。

---
Generated at: 2026-02-09 07:03:16 JST
