Last updated: 2026-01-15

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動実装を行うPull Request (PR) のフェーズを効率的に監視するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIを利用して高速なPR監視を実現します。
- PRの状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定し、通知や自動Ready化、コメント投稿、マージ、issue割り当てなどのアクションを実行します。

## 技術スタック
- フロントエンド: 該当なし（本ツールはCLIベースであり、GUI操作はブラウザ自動化によって間接的に行われます）
- 音楽・オーディオ: 該当なし
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub APIへの認証とアクセスに使用されます。
    - **VS Code (`.vscode/settings.json`)**: 開発時のエディタ設定を共有し、コードの一貫性を保ちます。
- テスト:
    - **pytest**: Pythonアプリケーションのテストフレームワークとして利用され、機能の正確性を検証します。
- ビルドツール: 該当なし（Pythonスクリプトとして直接実行されます）
- 言語機能:
    - **Python 3.x**: プロジェクトの主要なプログラミング言語です。
    - **TOML**: 設定ファイル（`config.toml`）の記述形式として使用され、可読性の高い設定管理を可能にします。
- 自動化・CI/CD:
    - **PyAutoGUI**: ブラウザ操作の自動化（ボタンクリックなど）に使用され、特定のGitHubアクションをシミュレートします。
    - **Pillow**: PyAutoGUIと連携し、スクリーンショットを介した画像認識ベースの自動化をサポートします。
    - **ntfy.sh**: モバイル端末への通知（Push通知）機能を提供し、PRの重要な状態変化をユーザーに伝えます。
- 開発標準:
    - **`.editorconfig`**: 異なるエディタやIDE間で一貫したコーディングスタイル（インデント、改行コードなど）を維持するための設定ファイルです。
    - **ruff.toml**: Pythonコードのリントおよびフォーマットツールである`Ruff`の設定ファイルで、コード品質とスタイルを自動的に統一します。

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
.editorconfig
.gitignore
.vscode/
  settings.json
LICENSE
MERGE_CONFIGURATION_EXAMPLES.md
PHASE3_MERGE_IMPLEMENTATION.md
README.ja.md
README.md
STRUCTURE.md
_config.yml
cat-github-watcher.py
config.toml.example
demo_automation.py
docs/
  IMPLEMENTATION_SUMMARY.ja.md
  IMPLEMENTATION_SUMMARY.md
  PR67_IMPLEMENTATION.md
  RULESETS.md
  VERIFICATION_GUIDE.en.md
  VERIFICATION_GUIDE.md
  browser-automation-approaches.en.md
  browser-automation-approaches.md
generated-docs/
pytest.ini
requirements-automation.txt
ruff.toml
screenshots/
  assign.png
  assign_to_copilot.png
src/
  __init__.py
  gh_pr_phase_monitor/
    __init__.py
    browser_automation.py
    colors.py
    comment_fetcher.py
    comment_manager.py
    config.py
    github_auth.py
    github_client.py
    graphql_client.py
    issue_fetcher.py
    main.py
    notifier.py
    phase_detector.py
    pr_actions.py
    pr_fetcher.py
    repository_fetcher.py
tests/
  test_batteries_included_defaults.py
  test_browser_automation.py
  test_check_process_before_autoraise.py
  test_config_rulesets.py
  test_config_rulesets_features.py
  test_elapsed_time_display.py
  test_hot_reload.py
  test_integration_issue_fetching.py
  test_interval_parsing.py
  test_issue_fetching.py
  test_max_llm_working_parallel.py
  test_no_change_timeout.py
  test_no_open_prs_issue_display.py
  test_notification.py
  test_phase3_merge.py
  test_phase_detection.py
  test_post_comment.py
  test_post_phase3_comment.py
  test_pr_actions.py
  test_pr_actions_rulesets_features.py
  test_pr_actions_with_rulesets.py
  test_status_summary.py
  test_verbose_config.py
```

## ファイル詳細説明
- **`.editorconfig`**: 異なる開発環境間でコードのスタイル（インデント、エンコーディングなど）を統一するための設定ファイルです。
- **`.gitignore`**: Gitがバージョン管理の対象としないファイルやディレクトリを指定します。
- **`.vscode/settings.json`**: Visual Studio Codeエディタのワークスペース固有の設定を定義し、開発者間の設定の一貫性を保ちます。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記載したファイルです。
- **`MERGE_CONFIGURATION_EXAMPLES.md`**: マージに関する設定例を説明するドキュメントです。
- **`PHASE3_MERGE_IMPLEMENTATION.md`**: Phase3マージ機能の実装詳細に関するドキュメントです。
- **`README.ja.md`**: プロジェクトの日本語版説明書です。
- **`README.md`**: プロジェクトの英語版説明書です。
- **`STRUCTURE.md`**: プロジェクトの全体的な構造や設計に関するドキュメントです。
- **`_config.yml`**: GitHub Pagesなどの設定ファイルである可能性がありますが、本プロジェクトでは直接使用されていないようです。
- **`cat-github-watcher.py`**: プロジェクトのエントリーポイントとなるPythonスクリプトで、ツールの実行を開始します。
- **`config.toml.example`**: ユーザーがコピーして編集するための設定ファイルのサンプルです。
- **`demo_automation.py`**: 自動化機能のデモンストレーション用スクリプトである可能性があります。
- **`docs/`**: プロジェクトに関する詳細なドキュメントを格納するディレクトリです。
    - **`IMPLEMENTATION_SUMMARY.ja.md` / `IMPLEMENTATION_SUMMARY.md`**: 実装の概要を説明するドキュメント（日本語/英語）。
    - **`PR67_IMPLEMENTATION.md`**: 特定のPull Request (PR #67) の実装に関する詳細ドキュメント。
    - **`RULESETS.md`**: ルールセット機能の詳細を説明するドキュメント。
    - **`VERIFICATION_GUIDE.en.md` / `VERIFICATION_GUIDE.md`**: 動作検証ガイド（英語/日本語）。
    - **`browser-automation-approaches.en.md` / `browser-automation-approaches.md`**: ブラウザ自動化のアプローチに関するドキュメント（英語/日本語）。
- **`generated-docs/`**: 自動生成されたドキュメントを格納するディレクトリであると推測されます。
- **`pytest.ini`**: pytestテストフレームワークの設定ファイルです。
- **`requirements-automation.txt`**: 自動化機能に必要なPythonパッケージをリストアップしたファイルです。
- **`ruff.toml`**: Pythonコードのリンター・フォーマッターであるRuffの設定ファイルです。
- **`screenshots/`**: PyAutoGUIによるブラウザ自動化で使用するボタンなどのスクリーンショット画像を格納するディレクトリです。
    - **`assign.png`**: "Assign" ボタンのスクリーンショット。
    - **`assign_to_copilot.png`**: "Assign to Copilot" ボタンのスクリーンショット。
- **`src/`**: プロジェクトのソースコードを格納する主要なディレクトリです。
    - **`__init__.py`**: Pythonパッケージとして認識させるためのファイル。
    - **`gh_pr_phase_monitor/`**: PR監視ロジックの主要モジュール群です。
        - **`__init__.py`**: Pythonサブパッケージとして認識させるためのファイル。
        - **`browser_automation.py`**: PyAutoGUIを用いたブラウザ操作（ボタンクリック、スクリーンショット比較など）のロジックを提供します。
        - **`colors.py`**: コンソール出力にANSIカラーコードを適用し、視認性を向上させるためのユーティリティ関数を提供します。
        - **`comment_fetcher.py`**: GitHub APIを通じてPRコメントを取得する機能を提供します。
        - **`comment_manager.py`**: PRへのコメント投稿や既存コメントの管理に関連するロジックを提供します。
        - **`config.py`**: `config.toml`から設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供するモジュールです。
        - **`github_auth.py`**: GitHub CLI (`gh`) を利用した認証情報の取得や管理に関連する機能を提供します。
        - **`github_client.py`**: GitHub REST APIとのHTTP通信を抽象化し、一般的なリクエスト処理を行います。
        - **`graphql_client.py`**: GitHub GraphQL APIと連携し、効率的なデータ取得を行うためのクエリ実行機能を提供します。
        - **`issue_fetcher.py`**: GitHub APIを通じてIssue情報を取得する機能を提供します。
        - **`main.py`**: アプリケーションのメイン実行ループと、PR監視・アクション実行の全体的なフローを制御する役割を担います。
        - **`notifier.py`**: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
        - **`phase_detector.py`**: PRのステータスやコメント内容に基づいて、プロジェクト独自のフェーズ（phase1, phase2, phase3, LLM working）を判定するロジックを提供します。
        - **`pr_actions.py`**: PRを"Ready for review"に変更する、ブラウザでPRを開く、自動マージを実行するなどの具体的なPR関連アクションを定義・実行します。
        - **`pr_fetcher.py`**: GitHub APIを通じてPull Requestのリストや詳細情報を取得する機能を提供します。
        - **`repository_fetcher.py`**: 認証済みユーザーが所有するGitHubリポジトリの情報を取得する機能を提供します。
- **`tests/`**: pytestフレームワークを使用した単体テストおよび結合テストのスクリプトを格納するディレクトリです。各`test_*.py`ファイルが特定の機能に対するテストケースを含みます。

## 関数詳細説明
提供されたプロジェクト情報からは具体的な関数名、引数、戻り値のシグネチャは特定できませんでしたが、各モジュールの役割と機能に基づいて、主要な処理を担う関数について以下に説明します。

- **`src/gh_pr_phase_monitor/main.py`**
    - **機能**: アプリケーションのメイン監視ループを制御し、定期的にPRの状態をチェックし、必要に応じてアクションを実行します。
    - **推測される主要関数**: `run_monitoring_loop()`
        - **役割**: 設定に基づいてGitHubリポジトリとPRをフェッチし、各PRのフェーズを判定し、定義されたルールセットに従ってアクション（通知、コメント、マージなど）を実行する一連の流れを繰り返します。省電力モードへの切り替えも管理します。
        - **引数（推測）**: `config` (dict) - アプリケーション全体の設定データ
        - **戻り値（推測）**: なし

- **`src/gh_pr_phase_monitor/config.py`**
    - **機能**: `config.toml`から設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供します。
    - **推測される主要関数**: `load_config(config_path: str)`
        - **役割**: 指定されたパスからTOML形式の設定ファイルを読み込み、それをPythonの辞書またはオブジェクトにパースし、アプリケーションが利用しやすい形式で返却します。
        - **引数（推測）**: `config_path` (str) - 設定ファイルのパス
        - **戻り値（推測）**: `dict` - 解析された設定データ

- **`src/gh_pr_phase_monitor/github_client.py`**
    - **機能**: GitHub REST APIとの基本的なHTTP通信を処理します。
    - **推測される主要関数**: `post_rest_api(endpoint: str, data: dict)`
        - **役割**: 指定されたGitHub REST APIエンドポイントに対してPOSTリクエストを送信し、データを更新したり、コメントを投稿したりします。
        - **引数（推測）**: `endpoint` (str) - APIエンドポイントのURLパス, `data` (dict) - リクエストボディ
        - **戻り値（推測）**: `dict` - APIからのレスポンスデータ

- **`src/gh_pr_phase_monitor/graphql_client.py`**
    - **機能**: GitHub GraphQL APIにクエリを送信し、PRやリポジトリの情報を効率的に取得します。
    - **推測される主要関数**: `query_graphql(query: str, variables: dict)`
        - **役割**: 指定されたGraphQLクエリ文字列と変数を使用して、GitHub GraphQL APIエンドポイントにリクエストを送信し、取得したデータを返します。
        - **引数（推測）**: `query` (str) - GraphQLクエリ文字列, `variables` (dict) - クエリ変数
        - **戻り値（推測）**: `dict` - APIからのレスポンスデータ

- **`src/gh_pr_phase_monitor/phase_detector.py`**
    - **機能**: PRの現在の状態（ドラフト、レビュー待ち、LLM作業中など）を判定するロジックを提供します。
    - **推測される主要関数**: `detect_pr_phase(pr_data: dict)`
        - **役割**: GitHub APIから取得したPull Requestのデータ（ステータス、コメント、レビュー状況など）を分析し、定義されたフェーズ判定ルールに基づいて、そのPRがどのフェーズにあるかを決定します。
        - **引数（推測）**: `pr_data` (dict) - 単一のPull Requestに関するデータ
        - **戻り値（推測）**: `str` - 判定されたフェーズ名（例: "phase1", "phase2", "LLM working"）

- **`src/gh_pr_phase_monitor/pr_actions.py`**
    - **機能**: PRのReady化、自動マージ、ブラウザでのPRページ表示など、PRに対する具体的なアクションを実行します。
    - **推測される主要関数**: `perform_pr_action(pr_url: str, action_type: str, config: dict)`
        - **役割**: 指定されたPRに対して、フェーズに応じたアクション（例: `mark_as_ready`, `merge_pr`, `open_in_browser`）を実行します。ブラウザ自動化やAPIコールを用いてアクションを完遂します。
        - **引数（推測）**: `pr_url` (str) - PRのURL, `action_type` (str) - 実行するアクションの種類, `config` (dict) - アプリケーション設定
        - **戻り値（推測）**: `bool` - アクションが成功したかどうか

- **`src/gh_pr_phase_monitor/notifier.py`**
    - **機能**: ntfy.shサービスを利用してモバイル端末に通知を送信します。
    - **推測される主要関数**: `send_notification(message: str, topic: str, pr_url: str = None)`
        - **役割**: 指定されたメッセージとトピックを使用してntfy.shに通知をプッシュします。オプションで、通知にPRへのリンクを含めることができます。
        - **引数（推測）**: `message` (str) - 通知メッセージ, `topic` (str) - ntfy.shのトピック名, `pr_url` (str, optional) - 通知に関連するPRのURL
        - **戻り値（推測）**: `bool` - 通知送信が成功したかどうか

- **`src/gh_pr_phase_monitor/browser_automation.py`**
    - **機能**: PyAutoGUIを使用してブラウザ内の特定のボタンを画像認識で探し、クリックするなどの自動操作を行います。
    - **推測される主要関数**: `click_button_by_screenshot(screenshot_name: str, wait_seconds: int, debug_dir: str)`
        - **役割**: 指定されたスクリーンショット画像（`screenshots/`ディレクトリ内）に基づいて、現在開いているブラウザウィンドウ内で一致するボタンを見つけ、クリックします。認識が失敗した場合はデバッグ情報を保存します。
        - **引数（推測）**: `screenshot_name` (str) - ボタンのスクリーンショットファイル名, `wait_seconds` (int) - ボタンが表示されるまでの待機時間, `debug_dir` (str) - デバッグ情報の保存先ディレクトリ
        - **戻り値（推測）**: `bool` - ボタンのクリックが成功したかどうか

## 関数呼び出し階層ツリー
```
提供されたプロジェクト情報からは、関数の具体的な呼び出し階層を分析できませんでした。

---
Generated at: 2026-01-15 07:02:01 JST
