Last updated: 2026-01-13

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのPull Request (PR) を監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、PRのフェーズを効率的に検知し、適切な通知やアクションを実行します。
- ドライランモード、自動コメント投稿、Draft PRのReady化、モバイル通知、issue表示、省電力モードなどの機能を備えています。

## 技術スタック
- フロントエンド: CLIベースのため、特定のフロントエンド技術は使用していません。
- 音楽・オーディオ: 該当する技術は使用していません。
- 開発ツール:
    - **Python 3.x**: プロジェクトの主要なプログラミング言語です。
    - **GitHub CLI (`gh`)**: GitHubへの認証およびAPIアクセスに使用されます。
    - **PyAutoGUI**: ブラウザ操作の自動化（ボタンクリックなど）に使用されるPythonライブラリです。
    - **Selenium / Playwright**: 設定に応じてブラウザ自動操縦のバックエンドとして選択可能で、WebUI操作を自動化します。
- テスト:
    - **pytest**: Pythonコードの単体テストおよび結合テストを行うためのフレームワークです。
- ビルドツール: Pythonスクリプトとして直接実行されるため、特定のビルドツールは使用していません。
- 言語機能:
    - **Python**: スクリプト言語としての機能と豊富なライブラリエコシステムを活用しています。
    - **TOML**: `config.toml`ファイルで使用される、人間にとって読みやすい設定ファイル形式です。
- 自動化・CI/CD:
    - **ntfy.sh**: フェーズ3（レビュー待ち）のPRに関するモバイル通知を送信するために利用される公開型通知サービスです。
    - **GitHub GraphQL API**: GitHubのデータを効率的に取得するためのAPIで、PRやリポジトリ情報の監視に利用されます。
- 開発標準:
    - **.editorconfig**: 異なるエディタやIDE間で一貫したコーディングスタイルを定義します。
    - **ruff**: Pythonコードのリントとフォーマットを高速に行い、コード品質と一貫性を保ちます。

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
│   └── browser-automation-approaches.md
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
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
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
    ├── test_status_summary.py
    └── test_verbose_config.py
```

## ファイル詳細説明

*   **.editorconfig**: さまざまなエディタやIDEで一貫したコーディングスタイル（インデント、改行コードなど）を維持するための設定ファイル。
*   **.gitignore**: Gitがバージョン管理の対象としないファイルやディレクトリのパターンを定義するファイル。
*   **.vscode/settings.json**: Visual Studio Codeエディタのワークスペース固有の設定を定義するファイル。
*   **LICENSE**: プロジェクトのライセンス情報（MIT License）が記載されています。
*   **MERGE_CONFIGURATION_EXAMPLES.md**: PRの自動マージ設定に関する追加の例や詳細情報を提供するドキュメント。
*   **PHASE3_MERGE_IMPLEMENTATION.md**: Phase3での自動マージ機能の実装詳細について説明するドキュメント。
*   **README.ja.md**: プロジェクトの日本語版概要ドキュメント。
*   **README.md**: プロジェクトの英語版概要ドキュメント。
*   **STRUCTURE.md**: プロジェクトの構造に関する詳細な情報を提供します。
*   **_config.yml**: GitHub Pagesなどの静的サイトジェネレータの設定ファイルとして一般的に使用されます（このプロジェクトでは具体的な利用方法は明示されていません）。
*   **cat-github-watcher.py**: プロジェクトのメインエントリーポイントとなるスクリプト。ツールの起動と主要な処理フローを制御します。
*   **config.toml.example**: `config.toml`を作成する際のテンプレートとなる設定ファイルのサンプル。各種機能の有効/無効、監視間隔、通知設定などが記述されています。
*   **demo_automation.py**: ブラウザ自動操縦機能の動作をデモンストレーションするためのスクリプト、またはそのテスト用スクリプト。
*   **docs/**: プロジェクトに関する追加のドキュメントが格納されているディレクトリ。
    *   **IMPLEMENTATION_SUMMARY.ja.md**: 実装の概要（日本語版）。
    *   **IMPLEMENTATION_SUMMARY.md**: 実装の概要（英語版）。
    *   **PR67_IMPLEMENTATION.md**: 特定のプルリクエスト（PR#67）に関連する実装の詳細。
    *   **RULESETS.md**: 監視ルールセットの設定機能に関する詳細ドキュメント。
    *   **VERIFICATION_GUIDE.en.md**: 検証ガイド（英語版）。
    *   **VERIFICATION_GUIDE.md**: 検証ガイド（日本語版）。
    *   **browser-automation-approaches.en.md**: ブラウザ自動化のアプローチに関するドキュメント（英語版）。
    *   **browser-automation-approaches.md**: ブラウザ自動化のアプローチに関するドキュメント（日本語版）。
*   **generated-docs/**: 自動生成されたドキュメントを格納するディレクトリ（現在は空または将来的な利用を想定）。
*   **pytest.ini**: `pytest`テストフレームワークの設定ファイル。
*   **requirements-automation.txt**: ブラウザ自動操縦機能に必要なPythonライブラリの依存関係リスト。
*   **ruff.toml**: `ruff`ツールによるPythonコードのリントおよびフォーマットの設定ファイル。コード品質と一貫性を保つために使用されます。
*   **screenshots/**: PyAutoGUIなどのブラウザ自動操縦で使用される、Webページ上のボタンの画像ファイルが格納されているディレクトリ。
    *   **assign.png**: 「Assign」ボタンのスクリーンショット。
    *   **assign_to_copilot.png**: 「Assign to Copilot」ボタンのスクリーンショット。
*   **src/**: プロジェクトの主要なPythonソースコードが格納されているディレクトリ。
    *   **__init__.py**: Pythonパッケージであることを示すファイル。
    *   **gh_pr_phase_monitor/**: プロジェクトの中核となる監視ロジックが格納されているパッケージ。
        *   **__init__.py**: Pythonパッケージであることを示すファイル。
        *   **browser_automation.py**: Selenium、Playwright、またはPyAutoGUIを利用したブラウザ自動操縦のロジックを実装します。
        *   **colors.py**: ターミナル出力にANSIカラーコードを適用し、ログを見やすくするためのユーティリティ関数を提供します。
        *   **comment_fetcher.py**: GitHub APIを通じて特定のPRのコメント情報を取得するロジック。
        *   **comment_manager.py**: PRへのコメント投稿や、既存コメントの確認に関するロジックを管理します。
        *   **config.py**: `config.toml`から設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供するモジュール。
        *   **github_auth.py**: GitHub CLI (`gh`) を利用したGitHub認証に関するロジック。
        *   **github_client.py**: GitHub APIと連携し、Pull Request、リポジトリ、Issueなどの情報を取得するための高レベルなインターフェースを提供します。
        *   **graphql_client.py**: GitHub GraphQL APIに直接クエリを送信し、データを取得するための低レベルなクライアント。
        *   **issue_fetcher.py**: GitHub APIを通じてIssue情報を取得するロジック（特にLLM working時のissue表示用）。
        *   **main.py**: 監視ツールのメイン実行ループを含み、設定された間隔でPR監視とアクション実行を調整します。
        *   **notifier.py**: `ntfy.sh`などのサービスを利用してモバイル通知を送信するロジック。
        *   **phase_detector.py**: Pull Requestの現在の状態を分析し、それがどの開発フェーズ（phase1, phase2, phase3, LLM working）にあるかを判定するロジック。
        *   **pr_actions.py**: Pull RequestをReady状態にする、ブラウザで開く、自動マージするなどの具体的なアクションを実行するモジュール。
        *   **pr_fetcher.py**: 特定のリポジトリ内のオープンなPull Requestの情報を取得するロジック。
        *   **repository_fetcher.py**: 認証済みGitHubユーザーが所有するリポジトリの一覧を取得するロジック。
*   **tests/**: プロジェクトのテストコードが格納されているディレクトリ。
    *   **test_*.py**: 各機能モジュールに対応するテストファイル群で、`pytest`フレームワークを使用して実装されています。

## 関数詳細説明
このプロジェクトは単一責任の原則に基づき複数のモジュールに分割されており、各モジュールが特定の役割を担う関数群を提供しています。具体的な関数シグネチャは省略しますが、各モジュールの責任に応じた主要な機能は以下の通りです。

*   **`cat-github-watcher.py` (エントリーポイント)**:
    *   アプリケーションの起動、設定ファイルの読み込み、メイン監視ループの開始を担う初期化関数。

*   **`src/gh_pr_phase_monitor/main.py`**:
    *   **監視ループ関数**: 設定された間隔でリポジトリとPRの状態を周期的にチェックし、必要に応じてアクションをトリガーする。省電力モードへの切り替えロジックも含む。
    *   **PR処理関数**: 各PRの状態を評価し、フェーズ判定、アクション実行、コメント管理などのモジュールと連携して適切な処理を実行する。

*   **`src/gh_pr_phase_monitor/config.py`**:
    *   **設定読み込み関数**: TOML形式の設定ファイル (`config.toml`) を読み込み、アプリケーションが利用できる設定オブジェクトに解析する。
    *   **設定検証関数**: 読み込まれた設定の妥当性をチェックし、不足しているまたは無効な設定項目があれば警告またはエラーを発生させる。

*   **`src/gh_pr_phase_monitor/github_client.py`**:
    *   **APIリクエスト関数**: GitHub GraphQL APIへのクエリを構築し、実行するための高レベルなインターフェースを提供する。
    *   **データパース関数**: APIから返されたJSONデータをPythonオブジェクトに変換し、アプリケーションで利用しやすい形に整形する。

*   **`src/gh_pr_phase_monitor/phase_detector.py`**:
    *   **フェーズ判定関数**: 特定のPull Requestオブジェクトの様々な属性（ドラフト状態、レビューコメント、タイトルなど）を分析し、それが「phase1」「phase2」「phase3」「LLM working」のいずれであるかを判定する。

*   **`src/gh_pr_phase_monitor/comment_manager.py`**:
    *   **コメント投稿関数**: 特定のPRに対して、フェーズに応じた自動コメント（例: Copilotへの修正依頼）を投稿する。
    *   **コメント確認関数**: 特定のユーザー（例: `copilot-pull-request-reviewer`）からのレビューコメントの存在や内容を確認する。

*   **`src/gh_pr_phase_monitor/pr_actions.py`**:
    *   **PR状態変更関数**: Draft状態のPRをReady状態に変更する。
    *   **PRブラウザ起動関数**: 特定のPRのURLをブラウザで開く。
    *   **PRマージ関数**: 特定のPRを自動的にマージする（`browser_automation`モジュールと連携）。

*   **`src/gh_pr_phase_monitor/notifier.py`**:
    *   **通知送信関数**: `ntfy.sh`サービスを利用して、指定されたトピックにモバイル通知を送信する。PRのURLやメッセージを動的に含める。

*   **`src/gh_pr_phase_monitor/browser_automation.py`**:
    *   **Webブラウザ操作関数**: Selenium、Playwright、またはPyAutoGUIのバックエンドを利用して、Webページ上のボタンクリック、フォーム入力などの操作を自動化する。
    *   **スクリーンショット認識関数**: PyAutoGUIを使用して、画面上の特定のボタン画像を認識し、その座標をクリックする。

*   **`src/gh_pr_phase_monitor/github_auth.py`**:
    *   **認証情報取得関数**: GitHub CLI (`gh`) を通じてGitHubの認証トークンなどの情報を安全に取得する。

*   **`src/gh_pr_phase_monitor/graphql_client.py`**:
    *   **GraphQLクエリ実行関数**: GraphQL APIエンドポイントに対して、与えられたクエリ文字列と変数を送信し、結果を返す。

*   **`src/gh_pr_phase_monitor/issue_fetcher.py`**:
    *   **issue情報取得関数**: 特定のリポジトリからオープンなIssueのリストを取得する。

*   **`src/gh_pr_phase_monitor/pr_fetcher.py`**:
    *   **PR情報取得関数**: 特定のリポジトリからオープンなPull Requestのリストと詳細情報を取得する。

*   **`src/gh_pr_phase_monitor/repository_fetcher.py`**:
    *   **リポジトリ情報取得関数**: 認証済みユーザーが所有するリポジトリの一覧を取得する。

## 関数呼び出し階層ツリー
```
利用可能な情報からは関数呼び出し階層ツリーを特定できませんでした。
しかし、プロジェクトのアーキテクチャは単一責任の原則に基づきモジュール化されており、`src/gh_pr_phase_monitor/main.py`が全体の監視ループを調整します。`config.py`から設定を読み込み、`github_client.py`（内部で`graphql_client.py`、`repository_fetcher.py`、`pr_fetcher.py`、`comment_fetcher.py`、`issue_fetcher.py`を利用）を通じてGitHubから情報を取得します。取得した情報は`phase_detector.py`で分析され、その結果に基づいて`pr_actions.py`、`comment_manager.py`、`notifier.py`がそれぞれアクションを実行します。`browser_automation.py`は`pr_actions.py`や設定に応じて、自動マージやissue割り当ての際に利用されます。

---
Generated at: 2026-01-13 07:02:15 JST
