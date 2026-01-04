Last updated: 2026-01-05

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト(PR)の進捗を監視し、適切なアクションを自動実行するPythonツールです。
- PRのフェーズ（ドラフト、レビュー指摘対応中、レビュー待ち、コーディング中）を自動判定し、ドラフトPRのReady化、自動コメント投稿、モバイル通知などを行います。
- 認証済みGitHubユーザーが所有するリポジトリを対象とし、GraphQL APIを活用して効率的な監視と管理を実現します。

## 技術スタック
- フロントエンド: このツールはCLI（コマンドラインインターフェース）アプリケーションであり、特定のフロントエンド技術は使用していません。
- 音楽・オーディオ: 音楽やオーディオに関連する技術は使用していません。
- 開発ツール:
    - GitHub CLI (`gh`): GitHub APIとの認証と連携に利用されるコマンドラインツール。
    - pytest: Pythonで書かれたテストコードを実行するためのフレームワーク。
    - ruff: 高速なPythonリンターおよびフォーマッターで、コード品質の維持に貢献します。
- テスト:
    - pytest: プロジェクトのテストスイートの実行に用いられ、機能の正確性を検証します。
- ビルドツール:
    - Python 3.x: プロジェクトがPython言語で書かれており、実行環境としてPythonインタープリタを使用します。
- 言語機能:
    - Python 3.x: プロジェクトの主要な開発言語。
    - GitHub GraphQL API: GitHubからPRやリポジトリの情報を効率的に取得するために利用されるAPI。
- 自動化・CI/CD:
    - GitHub Actions: READMEの自動翻訳生成など、一部のCI/CDタスクに利用されていますが、主要なPR監視ロジックはPython版で実行されます。
    - ntfy.sh: フェーズ3（レビュー待ち）を検知した際に、モバイル端末に通知を送信するためのサービス。
- 開発標準:
    - .editorconfig: 異なるエディタやIDE間でコードの書式設定を統一するための設定ファイル。
    - ruff: コードの静的解析とフォーマットを自動化し、一貫したコードスタイルと品質を維持します。

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
-   `cat-github-watcher.py`: プロジェクトのエントリーポイント。アプリケーションの実行を開始します。
-   `src/gh_pr_phase_monitor/__init__.py`: Pythonパッケージの初期化ファイル。
-   `src/gh_pr_phase_monitor/main.py`: メインの実行ループを管理し、リポジトリの監視、PRの処理、アクションの実行をオーケストレーションします。
-   `src/gh_pr_phase_monitor/config.py`: アプリケーションの設定ファイル（`config.toml`）を読み込み、解析し、設定値へのアクセスを提供します。監視間隔やntfy.sh通知設定などが含まれます。
-   `src/gh_pr_phase_monitor/github_auth.py`: GitHub CLI (`gh`) を使用して、GitHub認証の状態を確認し、必要に応じて認証プロセスを促します。
-   `src/gh_pr_phase_monitor/graphql_client.py`: GitHub GraphQL APIへの低レベルなリクエスト送信を担当します。クエリの実行と結果のハンドリングを行います。
-   `src/gh_pr_pr_phase_monitor/github_client.py`: `graphql_client` を利用し、PR情報取得、コメント投稿、PRステータス変更など、より高レベルなGitHub API連携機能を提供します。
-   `src/gh_pr_phase_monitor/repository_fetcher.py`: 認証済みユーザーが所有するリポジトリの一覧を取得する機能を提供します。
-   `src/gh_pr_phase_monitor/pr_fetcher.py`: 指定されたリポジトリ内のオープンなプルリクエストの詳細情報を取得する機能を提供します。
-   `src/gh_pr_phase_monitor/comment_fetcher.py`: 特定のプルリクエストに投稿されたコメントを取得する機能を提供します。
-   `src/gh_pr_phase_monitor/issue_fetcher.py`: オープンなPRがないリポジトリの上位イシューを取得し、表示する機能を提供します。
-   `src/gh_pr_phase_monitor/phase_detector.py`: プルリクエストの現在の状態（Draft、レビューコメントの有無など）を分析し、`phase1`、`phase2`、`phase3`、`LLM working` のいずれかのフェーズを判定するロジックを実装しています。
-   `src/gh_pr_phase_monitor/comment_manager.py`: PRへの自動コメント投稿、および特定のボットによる既存コメントの確認・管理を行います。
-   `src/gh_pr_phase_monitor/pr_actions.py`: Draft PRを「Ready for review」状態に変更したり、PRのURLをWebブラウザで開いたりするなど、PRに対する具体的なアクションを実行します。
-   `src/gh_pr_phase_monitor/notifier.py`: ntfy.shサービスを通じてモバイル端末に通知を送信する機能を提供します。PRのレビュー準備完了時などに利用されます。
-   `src/gh_pr_phase_monitor/colors.py`: コンソール出力にANSIカラーコードを適用し、ログやメッセージを見やすくするためのユーティリティ関数を提供します。
-   `tests/`: プロジェクトの各機能が正しく動作するかを検証するためのテストファイル群が格納されています。
-   `.editorconfig`: 異なる開発環境間でのコーディングスタイル（インデント、改行コードなど）を統一するための設定ファイルです。
-   `.gitignore`: Gitによってバージョン管理の対象外とするファイルやディレクトリを指定します。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）が記述されています。
-   `README.ja.md`: プロジェクトの概要、機能、使い方などを日本語で説明する主要なドキュメントです。
-   `README.md`: `README.ja.md`の英語版で、GitHub Actionsにより自動生成されています。
-   `STRUCTURE.md`: プロジェクトの構造に関する追加情報が記述されている可能性があります。
-   `_config.yml`: Jekyllなどの静的サイトジェネレータで使用される設定ファイルですが、このプロジェクトではドキュメント生成に関連している可能性があります。
-   `config.toml.example`: 設定ファイル（`config.toml`）のサンプルで、ユーザーが設定を作成する際のテンプレートとなります。
-   `generated-docs/`: AIエージェントによって生成された追加のドキュメントが格納されるディレクトリです。
-   `pytest.ini`: `pytest`の設定ファイルで、テスト実行時のオプションなどを指定します。
-   `ruff.toml`: `ruff`リンター/フォーマッターの設定ファイルです。
-   `.vscode/settings.json`: Visual Studio Codeエディタのワークスペース固有の設定を定義します。

## 関数詳細説明
-   **`cat-github-watcher.py`**
    -   `main()`: エントリポイントとしてアプリケーションの起動処理を担い、監視ループの開始を呼び出します。
-   **`src/gh_pr_phase_monitor/main.py`**
    -   `start_monitoring(config_path)`: 設定ファイルを読み込み、GitHub認証を確認した後、定期的にリポジトリを監視するメインループを開始します。
    -   `process_repositories(config)`: GitHubから認証済みユーザーのリポジトリとPRを取得し、各PRのフェーズを判定して適切なアクションを実行します。
-   **`src/gh_pr_phase_monitor/config.py`**
    -   `load_config(config_path)`: 指定されたパスからTOML形式の設定ファイルを読み込み、設定オブジェクトを返します。
    -   `parse_interval(interval_str)`: "1m", "5s"のような文字列形式の間隔設定を、秒単位の数値に変換します。
-   **`src/gh_pr_phase_monitor/github_auth.py`**
    -   `ensure_gh_authenticated()`: GitHub CLIがシステムにインストールされ、ユーザーが認証済みであることを確認します。
-   **`src/gh_pr_phase_monitor/graphql_client.py`**
    -   `execute_query(query, variables=None)`: GitHub GraphQL APIに対してクエリを実行し、その結果をJSON形式で返します。
-   **`src/gh_pr_phase_monitor/github_client.py`**
    -   `get_current_user_login()`: 現在認証されているGitHubユーザーのログイン名を取得します。
    -   `get_repositories_with_open_prs(user_login)`: 指定されたユーザーが所有し、オープンなPRを持つリポジトリのリストを取得します。
    -   `get_pr_details(repo_owner, repo_name, pr_number)`: 特定のPRの詳細情報（タイトル、ステータス、コメントなど）を取得します。
    -   `post_comment_to_pr(repo_id, pr_id, comment_body)`: 指定されたPRに新しいコメントを投稿します。
    -   `mark_pr_as_ready(pr_id)`: ドラフト状態のPRを「レビュー準備完了」状態に変更します。
-   **`src/gh_pr_phase_monitor/repository_fetcher.py`**
    -   `fetch_user_repositories(github_client, user_login)`: 指定されたGitHubクライアントとユーザーログイン情報を使用して、所有リポジトリをフェッチします。
-   **`src/gh_pr_phase_monitor/pr_fetcher.py`**
    -   `fetch_open_prs(github_client, repo_owner, repo_name)`: 指定されたリポジトリのすべてのオープンなPRをフェッチします。
-   **`src/gh_pr_phase_monitor/comment_fetcher.py`**
    -   `fetch_pr_comments(github_client, pr_id)`: 指定されたPRのすべてのコメントをフェッチします。
-   **`src/gh_pr_phase_monitor/issue_fetcher.py`**
    -   `fetch_top_issues_for_repo(github_client, repo_owner, repo_name, count=10)`: 特定のリポジトリのオープンイシューから上位`count`件を取得します。
-   **`src/gh_pr_phase_monitor/phase_detector.py`**
    -   `detect_pr_phase(pr_data, comments_data)`: PRのデータとコメント履歴を分析し、そのPRがどのフェーズ（phase1, 2, 3, LLM working）にあるかを判定します。
-   **`src/gh_pr_phase_monitor/comment_manager.py`**
    -   `post_phase_comment(github_client, pr_id, current_phase)`: 現在のPRフェーズに応じて、適切な自動コメントをPRに投稿します。
    -   `has_comment_from_bot(comments_data, bot_name, keyword)`: 特定のボットが特定のキーワードを含むコメントを投稿しているかを確認します。
-   **`src/gh_pr_phase_monitor/pr_actions.py`**
    -   `make_pr_ready_for_review(github_client, pr_id)`: 指定されたPRをドラフト状態からレビュー可能な状態に移行させます。
    -   `open_pr_in_browser(pr_url)`: 指定されたPRのURLを既定のウェブブラウザで開きます。
-   **`src/gh_pr_phase_monitor/notifier.py`**
    -   `send_ntfy_notification(config, pr_url)`: ntfy.shサービスを利用して、指定されたURLを含む通知をモバイル端末に送信します。
-   **`src/gh_pr_phase_monitor/colors.py`**
    -   `colorize_text(text, color_code)`: 指定されたテキストにANSIカラーコードを適用し、色付きの文字列を返します。

## 関数呼び出し階層ツリー
```
cat-github-watcher.py (エントリーポイント)
└── src/gh_pr_phase_monitor/main.py::start_monitoring
    ├── src/gh_pr_phase_monitor/config.py::load_config
    ├── src/gh_pr_phase_monitor/github_auth.py::ensure_gh_authenticated
    └── src/gh_pr_phase_monitor/main.py::process_repositories (ループ内で継続的に呼び出し)
        ├── src/gh_pr_phase_monitor/repository_fetcher.py::fetch_user_repositories
        │   └── src/gh_pr_phase_monitor/github_client.py::get_current_user_login
        │   └── src/gh_pr_phase_monitor/github_client.py::get_repositories_with_open_prs
        │       └── src/gh_pr_phase_monitor/graphql_client.py::execute_query
        ├── src/gh_pr_phase_monitor/pr_fetcher.py::fetch_open_prs
        │   └── src/gh_pr_phase_monitor/github_client.py::get_pr_details
        │       └── src/gh_pr_phase_monitor/graphql_client.py::execute_query
        ├── src/gh_pr_phase_monitor/comment_fetcher.py::fetch_pr_comments
        │   └── src/gh_pr_phase_monitor/github_client.py::get_pr_details (コメント部分の取得)
        │       └── src/gh_pr_phase_monitor/graphql_client.py::execute_query
        ├── src/gh_pr_phase_monitor/phase_detector.py::detect_pr_phase
        ├── src/gh_pr_phase_monitor/comment_manager.py::post_phase_comment
        │   └── src/gh_pr_phase_monitor/github_client.py::post_comment_to_pr
        │       └── src/gh_pr_phase_monitor/graphql_client.py::execute_query
        ├── src/gh_pr_phase_monitor/pr_actions.py::make_pr_ready_for_review
        │   └── src/gh_pr_phase_monitor/github_client.py::mark_pr_as_ready
        │       └── src/gh_pr_phase_monitor/graphql_client.py::execute_query
        ├── src/gh_pr_phase_monitor/pr_actions.py::open_pr_in_browser
        ├── src/gh_pr_phase_monitor/notifier.py::send_ntfy_notification
        └── src/gh_pr_phase_monitor/issue_fetcher.py::fetch_top_issues_for_repo (特定の条件下で呼び出し)
            └── src/gh_pr_phase_monitor/github_client.py::get_repository_issues
                └── src/gh_pr_phase_monitor/graphql_client.py::execute_query

---
Generated at: 2026-01-05 07:01:56 JST
