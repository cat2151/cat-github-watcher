Last updated: 2026-01-07

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエストを監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、PRのフェーズ（ドラフト、レビュー中など）を自動判定します。
- GraphQL APIを活用し、フェーズに応じた自動コメント投稿、PRのReady化、モバイル通知、自動マージなどのアクションを実行します。

## 技術スタック
- フロントエンド: Selenium, Playwright (ブラウザ自動操縦によりGitHubのWebUIとインタラクションするために使用)
- 音楽・オーディオ: 該当なし
- 開発ツール: Python 3.x (主要開発言語), GitHub CLI (`gh`) (GitHub認証とAPIアクセス), Git (バージョン管理), VS Code (開発環境設定: `.vscode/settings.json`), TOML (設定ファイル形式: `config.toml`)
- テスト: Pytest (Python用テストフレームワーク)
- ビルドツール: 該当なし (Pythonスクリプトとして直接実行)
- 言語機能: Python 3.x (プロジェクトの主要な実装言語機能)
- 自動化・CI/CD: GitHub Actions (ドキュメント自動生成等に利用), ntfy.sh (モバイル通知サービス), Selenium, Playwright (ブラウザ自動操縦によるPRアクションの自動化)
- 開発標準: .editorconfig (エディタ設定の統一), Ruff (コードフォーマッターおよびリンター)

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
├── demo_comparison.py
├── docs/
│   ├── IMPLEMENTATION_SUMMARY.ja.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PR67_IMPLEMENTATION.md
│   ├── RULESETS.md
│   ├── VERIFICATION_GUIDE.en.md
│   ├── VERIFICATION_GUIDE.md
│   ├── browser-automation-approaches.en.md
│   └── browser-automation-approaches.md
├── generated-docs/
├── pytest.ini
├── requirements-automation.txt
├── ruff.toml
├── src/
│   ├── __init__.py
│   └── gh_pr_phase_monitor/
│       ├── __init__.py
│       ├── browser_automation.py
│       ├── colors.py
│       ├── comment_fetcher.py
│       ├── comment_manager.py
│       ├── config.py
│       ├── github_auth.py
│       ├── github_client.py
│       ├── graphql_client.py
│       ├── issue_fetcher.py
│       ├── main.py
│       ├── notifier.py
│       ├── phase_detector.py
│       ├── pr_actions.py
│       ├── pr_fetcher.py
│       └── repository_fetcher.py
└── tests/
    ├── test_all_phase3_timeout.py
    ├── test_browser_automation.py
    ├── test_config_rulesets.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
    ├── test_no_open_prs_issue_display.py
    ├── test_notification.py
    ├── test_phase3_merge.py
    ├── test_phase_detection.py
    ├── test_post_comment.py
    ├── test_post_phase3_comment.py
    ├── test_pr_actions.py
    ├── test_pr_actions_with_rulesets.py
    ├── test_status_summary.py
    └── test_verbose_config.py
```

## ファイル詳細説明
-   `.editorconfig`: 異なる開発環境間でのコードのスタイル（インデント、改行コードなど）を統一するための設定ファイルです。
-   `.gitignore`: Gitのバージョン管理から除外するファイルやディレクトリを指定します。
-   `.vscode/settings.json`: Visual Studio Codeでこのプロジェクトを開いた際に適用されるワークスペース固有の設定を定義します。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）を記載しています。
-   `MERGE_CONFIGURATION_EXAMPLES.md`: 自動マージ機能の設定に関する具体例をまとめたドキュメントです。
-   `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3（レビュー待ち）でのプルリクエスト自動マージ機能の実装詳細を記述したドキュメントです。
-   `README.ja.md`: プロジェクトの日本語版の概要、機能、セットアップ、使い方などを説明する主要なドキュメントです。
-   `README.md`: プロジェクトの英語版の概要、機能、セットアップ、使い方などを説明する主要なドキュメントです。
-   `STRUCTURE.md`: プロジェクトの全体的なアーキテクチャやモジュール構造に関するドキュメントです。
-   `_config.yml`: Jekyllなどの静的サイトジェネレータで使用される可能性のある設定ファイルです。
-   `cat-github-watcher.py`: プロジェクトのメインのエントリポイントとなるPythonスクリプトで、アプリケーションの実行を開始します。
-   `config.toml.example`: ユーザーが設定を行うための`config.toml`ファイルのテンプレートです。監視間隔や各種アクションの有効化フラグなどが定義されています。
-   `demo_automation.py`: ブラウザ自動操縦機能の動作を確認するためのデモンストレーション用スクリプトです。
-   `demo_comparison.py`: 何らかの比較機能を示すためのデモンストレーション用スクリプトです。
-   `docs/`: プロジェクトに関する様々な追加ドキュメントが格納されているディレクトリです。
    -   `docs/IMPLEMENTATION_SUMMARY.ja.md`: 実装の概要を日本語でまとめたものです。
    -   `docs/IMPLEMENTATION_SUMMARY.md`: 実装の概要を英語でまとめたものです。
    -   `docs/PR67_IMPLEMENTATION.md`: 特定のプルリクエスト（PR #67）に関連する実装の詳細を説明するドキュメントです。
    -   `docs/RULESETS.md`: プロジェクト内で適用されるルールセットに関するドキュメントです。
    -   `docs/VERIFICATION_GUIDE.en.md`: 検証手順を英語で説明するガイドです。
    -   `docs/VERIFICATION_GUIDE.md`: 検証手順を日本語で説明するガイドです。
    -   `docs/browser-automation-approaches.en.md`: ブラウザ自動操縦のアプローチについて英語で説明したドキュメントです。
    -   `docs/browser-automation-approaches.md`: ブラウザ自動操縦のアプローチについて日本語で説明したドキュメントです。
-   `generated-docs/`: AIによって自動生成されたドキュメントやその他の生成物を格納するディレクトリです。
-   `pytest.ini`: pytestテストフレームワークの挙動をカスタマイズするための設定ファイルです。
-   `requirements-automation.txt`: SeleniumやPlaywrightなど、ブラウザ自動操縦機能のために必要なPythonパッケージの依存関係をリストアップしています。
-   `ruff.toml`: コードのフォーマットとリンティング（静的コード解析）を行うRuffツールの設定ファイルです。
-   `src/`: プロジェクトの主要なソースコードが格納されているディレクトリです。
    -   `src/gh_pr_phase_monitor/`: GitHubプルリクエストのフェーズ監視を行うコアロジックをまとめたPythonパッケージです。
        -   `src/gh_pr_phase_monitor/__init__.py`: Pythonパッケージの初期化ファイルです。
        -   `src/gh_pr_phase_monitor/browser_automation.py`: SeleniumやPlaywrightを使用してウェブブラウザを操作し、GitHub上での自動アクションを実行します。
        -   `src/gh_pr_phase_monitor/colors.py`: コンソール出力に色を付けて視認性を高めるためのANSIカラーコードユーティリティを提供します。
        -   `src/gh_pr_phase_monitor/comment_fetcher.py`: GitHub APIからプルリクエストのコメントを取得する機能を提供します。
        -   `src/gh_pr_phase_monitor/comment_manager.py`: プルリクエストへのコメント投稿を管理し、フェーズに応じた自動コメント機能を提供します。
        -   `src/gh_pr_phase_monitor/config.py`: TOML形式の設定ファイルを読み込み、アプリケーション全体で利用可能な設定オブジェクトを提供します。
        -   `src/gh_pr_phase_monitor/github_auth.py`: GitHub CLI (`gh`) を使用してGitHub APIへの認証トークンを取得・管理します。
        -   `src/gh_pr_phase_monitor/github_client.py`: GitHubのREST APIとの汎用的な連携を処理し、様々なGitHubリソースへのアクセスを提供します。
        -   `src/gh_pr_phase_monitor/graphql_client.py`: GitHubのGraphQL APIに特化したクライアントであり、効率的なデータ取得クエリを実行します。
        -   `src/gh_pr_phase_monitor/issue_fetcher.py`: GitHubリポジトリのIssue情報を取得する機能を提供します。
        -   `src/gh_pr_phase_monitor/main.py`: 監視ツールの中核となるメイン実行ループを実装しており、PRのフェッチ、フェーズ判定、アクション実行のオーケストレーションを行います。
        -   `src/gh_pr_phase_monitor/notifier.py`: ntfy.shサービスを利用して、モバイルデバイスへの通知を送信する機能を提供します。
        -   `src/gh_pr_phase_monitor/phase_detector.py`: 各プルリクエストの現在の状態を分析し、定義されたフェーズ（phase1, phase2, phase3, LLM working）を判定するロジックを含みます。
        -   `src/gh_pr_phase_monitor/pr_actions.py`: プルリクエストに関連する具体的なアクション（ドラフト解除、ブラウザで開く、自動マージなど）を実行します。
        -   `src/gh_pr_phase_monitor/pr_fetcher.py`: GitHub APIからプルリクエストのリストとその詳細情報を取得します。
        -   `src/gh_pr_phase_monitor/repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリのリストを取得する機能を提供します。
-   `tests/`: プロジェクトの各モジュールと機能の単体テストおよび統合テストを含むディレクトリです。

## 関数詳細説明
-   `main.py::run_monitor(config)`
    -   役割: アプリケーションのメイン監視ループを開始し、定期的にGitHubリポジトリのプルリクエストをフェッチ、フェーズ判定、および設定されたアクションを実行します。
    -   引数: `config` (dict) - アプリケーションの実行設定を含む辞書オブジェクト。
    -   戻り値: なし。
    -   機能: 監視間隔に従って処理を繰り返し、Dry-runモードや各種アクションの有効化フラグに応じて動作を制御します。
-   `src/gh_pr_phase_monitor/phase_detector.py::detect_phase(pr_data, repo_name)`
    -   役割: GitHub APIから取得したプルリクエストのデータに基づいて、その現在の開発フェーズ（phase1, phase2, phase3, LLM working）を判定します。
    -   引数: `pr_data` (dict) - 単一プルリクエストの詳細情報。`repo_name` (str) - プルリクエストが属するリポジトリの名前。
    -   戻り値: `str` - 判定されたフェーズ名（例: "phase1"）。
    -   機能: ドラフト状態、レビューコメントの有無、特定のラベルなど複数の条件を評価してフェーズを特定します。
-   `src/gh_pr_phase_monitor/pr_actions.py::mark_pr_as_ready(repo_id, pr_id)`
    -   役割: 指定されたプルリクエストをドラフト状態から「レビュー準備完了」状態に変更します。
    -   引数: `repo_id` (str) - 対象リポジトリのGitHubノードID。`pr_id` (str) - 対象プルリクエストのGitHubノードID。
    -   戻り値: `bool` - アクションが成功した場合は`True`、失敗した場合は`False`。
    -   機能: GitHub GraphQL APIのミューテーションを介して、PRのドラフト状態を解除する操作を実行します。
-   `src/gh_pr_phase_monitor/pr_actions.py::open_pr_in_browser(pr_url)`
    -   役割: 指定されたプルリクエストのURLをユーザーのシステムのデフォルトブラウザで開きます。
    -   引数: `pr_url` (str) - 開くプルリクエストの完全なURL。
    -   戻り値: なし。
    -   機能: `webbrowser`モジュールを利用して、ユーザーが直接PRページにアクセスできるようにします。
-   `src/gh_pr_phase_monitor/comment_manager.py::post_comment(repo_id, pr_id, comment_body)`
    -   役割: 指定されたプルリクエストに新しいコメントを投稿します。
    -   引数: `repo_id` (str) - コメントを投稿するリポジトリのGitHubノードID。`pr_id` (str) - コメントを投稿するプルリクエストのGitHubノードID。`comment_body` (str) - 投稿するコメントの本文。
    -   戻り値: `bool` - コメント投稿が成功した場合は`True`、失敗した場合は`False`。
    -   機能: GitHub GraphQL APIのミューテーションを使用して、PRに新しいコメントを追加します。
-   `src/gh_pr_phase_monitor/notifier.py::send_ntfy_notification(topic, message, pr_url, priority)`
    -   役割: ntfy.shサービスを通じてモバイルデバイスにカスタムプッシュ通知を送信します。
    -   引数: `topic` (str) - ntfy.shの通知トピック。`message` (str) - 通知に表示されるメッセージ。`pr_url` (str) - 通知に含めるプルリクエストのURL。`priority` (int) - 通知の優先度（1-5）。
    -   戻り値: `bool` - 通知送信が成功した場合は`True`、失敗した場合は`False`。
    -   機能: `requests`ライブラリを使用してntfy.shのエンドポイントへHTTP POSTリクエストを送信し、アクションボタン付きの通知を生成します。
-   `src/gh_pr_phase_monitor/graphql_client.py::execute_query(query, variables)`
    -   役割: GitHub GraphQL APIに対して指定されたクエリを実行し、その結果を返します。
    -   引数: `query` (str) - 実行するGraphQLクエリ文字列。`variables` (dict) - クエリで使用する変数の辞書。
    -   戻り値: `dict` - APIからのJSONレスポンスをPython辞書として返します。エラーが発生した場合は`None`。
    -   機能: 認証されたHTTPクライアントを通じてGitHub GraphQLエンドポイントと通信し、PRやリポジトリに関する複雑なデータを効率的に取得します。

## 関数呼び出し階層ツリー
```
提供された情報では、詳細な関数呼び出し階層を分析できませんでした。
しかし、プロジェクトの構造から、`cat-github-watcher.py`または`src/gh_pr_phase_monitor/main.py`内の主要な関数（例: `run_monitor`）が、アプリケーションの実行フローの中心となり、以下のモジュール内の関数を呼び出して処理をオーケストレートすると考えられます。

- GitHub API連携: `src/gh_pr_phase_monitor/repository_fetcher`, `src/gh_pr_phase_monitor/pr_fetcher`, `src/gh_pr_phase_monitor/comment_fetcher`, `src/gh_pr_phase_monitor/issue_fetcher`, `src/gh_pr_phase_monitor/graphql_client`, `src/gh_pr_phase_monitor/github_client`
- フェーズ判定: `src/gh_pr_phase_monitor/phase_detector`
- アクション実行: `src/gh_pr_phase_monitor/pr_actions`, `src/gh_pr_phase_monitor/comment_manager`, `src/gh_pr_phase_monitor/notifier`, `src/gh_pr_phase_monitor/browser_automation`
- 設定管理: `src/gh_pr_phase_monitor/config`
- 認証: `src/gh_pr_phase_monitor/github_auth`

全体としては、監視ループ (`run_monitor`) が定期的にリポジトリとPRの情報を取得し、それぞれのPRに対してフェーズ判定を行い、その結果に基づいて適切なアクションを選択・実行する、という流れになります。

---
Generated at: 2026-01-07 07:02:58 JST
