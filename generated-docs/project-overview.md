Last updated: 2026-01-10

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装PRのフェーズを効率的に監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIでPR情報を取得し、その状態を判定します。
- PRの状態に応じた通知、コメント投稿、Ready化、自動マージなどのアクションを自動で実行します。

## 技術スタック
- フロントエンド: 直接的なユーザーインターフェースは持ちませんが、`selenium`や`playwright`を用いたブラウザ自動操縦機能により、GitHub Web UI上での操作を実現します。
- 音楽・オーディオ: 該当する技術は使用されていません。
- 開発ツール: `GitHub CLI (gh)`はGitHub認証と操作に利用され、`pytest`はテストフレームワーク、`ruff`はコード品質維持のためのリンター/フォーマッターとして使用されています。`.editorconfig`はコードスタイルの統一を支援し、`.vscode/settings.json`は開発環境の設定を提供します。
- テスト: `pytest`が主要なテストフレームワークとして採用されており、各モジュールの機能検証に使用されます。
- ビルドツール: Pythonスクリプトとして直接実行されるため、特定のビルドツールは使用されていません。Python 3.x環境が前提となります。
- 言語機能: `Python 3.x`が主要なプログラミング言語として使用されています。設定ファイルには`TOML`形式が採用されています。
- 自動化・CI/CD: `ntfy.sh`サービスを利用してモバイル通知を送信します。`selenium`と`playwright`は、特定のGitHub操作（例：自動マージ）を自動化するためのブラウザ自動操縦に用いられます。READMEファイルの自動生成にはGitHub Actionsが利用されています。
- 開発標準: `.editorconfig`によりエディタ間の設定統一を図り、`ruff`によってコードの品質とスタイルの一貫性を保っています。

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
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントであり、スクリプトの起動と主要な実行フローを制御します。
- `src/gh_pr_phase_monitor/main.py`: GitHub PR監視ツールのメイン実行ループを定義し、設定の読み込み、リポジトリ・PRのフェッチ、フェーズ判定、およびそれに応じたアクションの調整を行います。
- `src/gh_pr_phase_monitor/config.py`: `config.toml`ファイルから設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供します。監視間隔、Dry-run設定、通知オプションなどが含まれます。
- `src/gh_pr_phase_monitor/github_client.py`: GitHub API（主にGraphQL）との通信を抽象化するクライアント。認証情報の管理やAPIリクエストの実行を担当します。
- `src/gh_pr_phase_monitor/graphql_client.py`: 実際のGitHub GraphQL APIクエリの実行と結果の処理を担当する低レベルなクライアントです。
- `src/gh_pr_phase_monitor/repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリのリストを取得する機能を提供します。
- `src/gh_pr_phase_monitor/pr_fetcher.py`: 特定のリポジトリからオープンなプルリクエスト(PR)の情報を取得する機能を提供します。
- `src/gh_pr_phase_monitor/phase_detector.py`: 各プルリクエストの状態を分析し、`phase1` (Draft), `phase2` (レビュー指摘対応中), `phase3` (レビュー待ち), `LLM working` (AI作業中) のいずれかのフェーズを判定するロジックを実装しています。
- `src/gh_pr_phase_monitor/comment_fetcher.py`: 指定されたプルリクエストから既存のコメントを効率的に取得する機能を提供します。
- `src/gh_pr_phase_monitor/comment_manager.py`: プルリクエストへのコメント投稿や、特定のコメントが存在するかどうかの確認といったコメント関連の操作を管理します。
- `src/gh_pr_phase_monitor/pr_actions.py`: プルリクエストをDraftからReadyに変更する、特定のPRのURLをブラウザで開く、PRをマージするといった実際のアクションを実行します。
- `src/gh_pr_phase_monitor/browser_automation.py`: SeleniumやPlaywrightといったライブラリを使用して、Webブラウザを自動操作する機能を提供します。PRの自動マージやCopilotへのIssue割り当てなどの場面で使用されます。
- `src/gh_pr_phase_monitor/notifier.py`: `ntfy.sh`サービスを利用して、モバイルデバイスへの通知を送信する機能を提供します。特に`phase3`のPRが検出された際に利用されます。
- `src/gh_pr_phase_monitor/issue_fetcher.py`: オープンPRが存在しないリポジトリに対して、上位のオープンIssueをフェッチする機能を提供します。
- `src/gh_pr_phase_monitor/colors.py`: ターミナル出力にANSIカラーコードを適用し、ログやステータス表示の視認性を高めるためのユーティリティ関数を提供します。
- `src/gh_pr_phase_monitor/github_auth.py`: GitHub CLI (`gh`) を利用して、GitHub APIへの認証トークンを取得・管理する機能を提供します。
- `config.toml.example`: アプリケーションの設定例を示すTOML形式のファイルです。ユーザーが`config.toml`を作成する際のテンプレートとなります。
- `requirements-automation.txt`: ブラウザ自動操縦機能（SeleniumやPlaywright）を使用する際に必要なPython依存ライブラリをリストアップしています。
- `pytest.ini`: `pytest`テストフレームワークの設定ファイル。テストの実行方法や検出ルールを定義します。
- `ruff.toml`: `ruff`Linter/Formatterの設定ファイル。コードの品質維持とスタイル統一のためのルールを定義します。
- `.editorconfig`: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
- `tests/`: 各モジュールの機能が期待通りに動作するかを検証するための単体テストおよび結合テストのコレクションを格納するディレクトリです。

## 関数詳細説明
- `main.run_monitoring_loop(config)`:
  - 役割: プロジェクト全体の監視プロセスを駆動するメインループを実行します。設定された間隔でリポジトリとPRの状態を継続的にチェックし、適切なアクションをトリガーします。
  - 引数: `config` (dict): アプリケーション設定を含む辞書。
  - 戻り値: なし。
- `config.load_configuration(file_path)`:
  - 役割: 指定されたパスからTOML形式の設定ファイルを読み込み、解析してアプリケーション設定として返します。
  - 引数: `file_path` (str): 設定ファイルへのパス。
  - 戻り値: `dict`: 解析された設定データ。
- `github_client.fetch_user_repositories()`:
  - 役割: 認証済みGitHubユーザーが所有するすべてのリポジトリの基本的な情報を取得します。
  - 引数: なし。
  - 戻り値: `list[dict]`: リポジトリ情報のリスト。
- `pr_fetcher.get_open_pull_requests(repository_owner, repository_name)`:
  - 役割: 指定されたリポジトリのオープンなプルリクエスト（PR）の詳細情報を取得します。
  - 引数: `repository_owner` (str): リポジトリの所有者名。`repository_name` (str): リポジトリ名。
  - 戻り値: `list[dict]`: 各PRの詳細情報を含む辞書のリスト。
- `phase_detector.determine_pr_phase(pull_request_data)`:
  - 役割: プルリクエストのデータに基づいて、現在のフェーズ（Draft, レビュー指摘対応中, レビュー待ち, LLM working）を判定します。
  - 引数: `pull_request_data` (dict): 単一のプルリクエストに関する詳細情報。
  - 戻り値: `str`: 判定されたフェーズ名。
- `comment_manager.add_comment_to_pr(pull_request_id, comment_body)`:
  - 役割: 指定されたプルリクエストに新しいコメントを投稿します。
  - 引数: `pull_request_id` (str): コメントを投稿するPRのID。`comment_body` (str): 投稿するコメントのテキスト。
  - 戻り値: `bool`: コメント投稿が成功したか否か。
- `pr_actions.set_pr_ready_for_review(pull_request_id)`:
  - 役割: Draft状態のプルリクエストを「レビュー準備完了（Ready for Review）」状態に変更します。
  - 引数: `pull_request_id` (str): 状態を変更するPRのID。
  - 戻り値: `bool`: 状態変更が成功したか否か。
- `notifier.send_mobile_notification(topic, message, pr_url)`:
  - 役割: `ntfy.sh`サービスを通じて、指定されたトピックにモバイル通知を送信します。PRへのリンクが含まれます。
  - 引数: `topic` (str): ntfy.shのトピック名。`message` (str): 通知メッセージ。`pr_url` (str): 関連するPRのURL。
  - 戻り値: `bool`: 通知送信が成功したか否か。
- `browser_automation.perform_browser_action(url, target_selector, browser_type)`:
  - 役割: 指定されたURLをブラウザで開き、特定のCSSセレクタにマッチする要素をクリックするなどの自動操作を実行します。
  - 引数: `url` (str): 開くURL。`target_selector` (str): 操作対象の要素のCSSセレクタ。`browser_type` (str): 使用するブラウザ（例: "chrome", "edge"）。
  - 戻り値: `bool`: 操作が成功したか否か。

## 関数呼び出し階層ツリー
```
cat-github-watcher.py (エントリーポイント)
└── src.gh_pr_phase_monitor.main.run_monitoring_loop()
    ├── src.gh_pr_phase_monitor.config.load_configuration()
    ├── (監視ループ開始)
    │   ├── src.gh_pr_phase_monitor.repository_fetcher.fetch_user_repositories()
    │   ├── src.gh_pr_phase_monitor.pr_fetcher.get_open_pull_requests()
    │   │   └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   │       └── src.gh_pr_phase_monitor.graphql_client.query_graphql_api()
    │   ├── src.gh_pr_phase_monitor.phase_detector.determine_pr_phase()
    │   │   └── src.gh_pr_phase_monitor.comment_fetcher.get_comments_for_pr()
    │   │       └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   ├── (判定されたフェーズに応じたアクション実行)
    │   │   ├── src.gh_pr_phase_monitor.pr_actions.set_pr_ready_for_review()
    │   │   │   └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   │   ├── src.gh_pr_phase_monitor.comment_manager.add_comment_to_pr()
    │   │   │   └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   │   ├── src.gh_pr_phase_monitor.notifier.send_mobile_notification()
    │   │   ├── src.gh_pr_phase_monitor.pr_actions.merge_pull_request()
    │   │   │   └── src.gh_pr_phase_monitor.browser_automation.perform_browser_action()
    │   │   └── src.gh_pr_phase_monitor.issue_fetcher.fetch_top_issues_for_repos()
    │   │       └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   └── (監視ループ終了)
    └── (プログラム終了処理)
```

---
Generated at: 2026-01-10 07:02:01 JST
