Last updated: 2026-04-08

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト(PR)を効率的に監視するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、PRのフェーズ判定と適切なアクション（通知、コメント投稿、Ready化、マージ）を実行します。
- GraphQL APIとブラウザ自動化を活用し、開発プロセスの自動化と省力化を支援します。

## 技術スタック
- フロントエンド: このプロジェクトはCLIツールであり、特定のフロントエンド技術は使用していません。UIはターミナル出力と、設定に応じたブラウザ自動操作で構成されます。
- 音楽・オーディオ: 音楽・オーディオ関連技術は使用していません。
- 開発ツール:
    - **GitHub CLI (gh)**: GitHub APIへの認証とアクセスに使用されます。
    - **PyAutoGUI**: ブラウザのUIを自動操作し、ボタンクリックやウィンドウ操作を実現するために使用されます。
    - **Git**: ローカルリポジトリの監視と自動pull機能に利用されます。
    - **pytesseract**: ブラウザ自動化のフォールバックとして、OCRによるボタンテキスト検出に利用されます。
- テスト:
    - **pytest**: プロジェクトのテストスイートを実行するためのPythonテストフレームワークです。
- ビルドツール:
    - **pip**: Pythonパッケージの依存関係管理とインストールに使用されます（`requirements-automation.txt`）。
    - **cargo**: 設定されたRustプロジェクトのバイナリを自動更新するために`cargo install --force`コマンドを内部的に使用します。
- 言語機能:
    - **Python 3.11+**: プロジェクトの主要な開発言語です。
    - **TOML**: `config.toml`ファイルで使用され、設定情報の記述に利用されます。
- 自動化・CI/CD:
    - **GitHub Actions**: READMEの自動翻訳など、CI/CDの一部機能で利用されます（プロジェクト自体がPR監視ツールとして自動化を提供）。
    - **ntfy.sh**: PRがレビュー待ちフェーズに達した際に、モバイル端末への通知を送信するために使用されます。
- 開発標準:
    - **.editorconfig**: エディタの設定を統一し、一貫したコーディングスタイルを維持するために使用されます。
    - **ruff**: Pythonコードのリンティングとフォーマットを enforces し、コード品質を向上させます。

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

※ 提供された簡略ツリーを使用します。詳細なツリーは以下のファイル詳細説明にて補足します。

## ファイル詳細説明
- **`.editorconfig`**: 複数のエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
- **`.gitignore`**: Gitでバージョン管理しないファイルやディレクトリを指定するファイルです。
- **`.vscode/settings.json`**: VS Codeエディタのワークスペース固有の設定ファイルです。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を記述したファイルです。
- **`README.ja.md`**: プロジェクトの概要、特徴、使い方などを日本語で説明するメインのドキュメントファイルです。
- **`README.md`**: プロジェクトの概要、特徴、使い方などを英語で説明するドキュメントファイルです。`README.ja.md`から自動生成されます。
- **`_config.yml`**: GitHub Pagesなどのサイト生成ツールで使用される設定ファイルです。
- **`cat-github-watcher.py`**: プロジェクトのメインエントリーポイントとなるスクリプトファイルです。
- **`config.toml.example`**: ユーザーが設定を行うための`config.toml`のサンプルファイルです。
- **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーション用スクリプトです。
- **`docs/`**: プロジェクトの追加ドキュメントが格納されるディレクトリです。
    - **`RULESETS.md`**: `config.toml`の`rulesets`設定に関する詳細な説明ドキュメントです。
    - **`button-detection-improvements.ja.md`**: ボタン検出機能の改善点に関する日本語ドキュメントです。
    - **`window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメントです。
- **`fetch_pr_html.py`**: プルリクエストのHTMLコンテンツを取得するための補助スクリプトです。
- **`generated-docs/`**: 自動生成されたドキュメントが格納されるディレクトリです。
- **`pyproject.toml`**: Pythonプロジェクトのビルドシステムやメタデータを設定するファイルです。
- **`pytest.ini`**: `pytest`テストランナーの設定ファイルです。
- **`requirements-automation.txt`**: 自動化機能に必要なPythonパッケージの依存関係をリストアップしたファイルです。
- **`ruff.toml`**: Pythonコードのリンター・フォーマッターであるRuffの設定ファイルです。
- **`screenshots/`**: PyAutoGUIがボタンを検出するために使用するスクリーンショット画像が格納されるディレクトリです。
    - **`assign.png`**: GitHubの「Assign」ボタンのスクリーンショットです。
    - **`assign_to_copilot.png`**: GitHubの「Assign to Copilot」ボタンのスクリーンショットです。
- **`src/`**: プロジェクトの主要なソースコードが格納されるディレクトリです。
    - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
    - **`gh_pr_phase_monitor/`**: PRフェーズ監視のコアロジックを含むPythonパッケージです。
        - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
        - **`actions/`**: PRに対する特定のアクションを処理するモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`pr_actions.py`**: PRのReady化、ブラウザ起動、コメント投稿、マージなどのアクションを実行する機能を提供します。
        - **`browser/`**: ブラウザ自動化関連のロジックを含むモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`browser_automation.py`**: ブラウザ操作の全体的なフローを管理します。
            - **`browser_cooldown.py`**: ブラウザ操作間のクールダウン時間（待機時間）を管理します。
            - **`button_clicker.py`**: PyAutoGUIを使用して指定されたボタンをクリックする機能を提供します。
            - **`click_config_validator.py`**: クリック操作に関する設定の検証を行います。
            - **`issue_assigner.py`**: GitHub issueを自動的に割り当てる機能を提供します。
            - **`window_manager.py`**: ブラウザウィンドウの管理（アクティベーション、最大化など）を行います。
        - **`core/`**: プロジェクトの基盤となる共通ユーティリティモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`colors.py`**: ターミナル出力の色付けに使用するANSIカラーコードと色付け関数を定義します。
            - **`config.py`**: `config.toml`から設定を読み込み、解析する機能を提供します。
            - **`config_printer.py`**: 現在の設定情報を整形して表示する機能を提供します。
            - **`config_ruleset.py`**: リポジトリごとのルールセット設定を管理します。
            - **`interval_parser.py`**: 時間間隔文字列（例: "1m", "5s"）を解析する機能を提供します。
            - **`process_utils.py`**: プロセス関連のユーティリティ関数を提供します。
            - **`time_utils.py`**: 時間関連のユーティリティ関数を提供します。
        - **`github/`**: GitHub APIとの連携ロジックを含むモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`comment_fetcher.py`**: PRコメントを取得する機能を提供します。
            - **`comment_manager.py`**: PRにコメントを投稿したり、既存コメントを確認したりする機能を提供します。
            - **`etag_checker.py`**: GitHub APIのETagを利用して、APIクォータを節約しながら更新をチェックする機能を提供します。
            - **`github_auth.py`**: GitHub認証（`gh` CLIを使用）を処理します。
            - **`github_client.py`**: GitHub APIの主要なクライアントとして機能し、他のGitHub関連モジュールを統合します。
            - **`graphql_client.py`**: GitHub GraphQL APIへのクエリ実行を抽象化します。
            - **`issue_etag_checker.py`**: Issueに関するETagチェック機能を提供します。
            - **`issue_fetcher.py`**: GitHub issueを取得する機能を提供します。
            - **`pr_fetcher.py`**: GitHubプルリクエストのデータを取得する機能を提供します。
            - **`rate_limit_handler.py`**: GitHub APIのレート制限を監視し、適切に処理する機能を提供します。
            - **`repository_fetcher.py`**: 監視対象のGitHubリポジトリ情報を取得する機能を提供します。
        - **`main.py`**: `src/gh_pr_phase_monitor`パッケージのメイン実行ロジックを含むファイルです。ツールの中核となる監視ループを開始します。
        - **`monitor/`**: プロジェクトの監視と状態管理に関するモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`auto_updater.py`**: ツールの自己更新機能（git pullと再起動）を管理します。
            - **`error_logger.py`**: エラーログの記録を管理します。
            - **`iteration_runner.py`**: 監視ループの各イテレーションを実行します。
            - **`local_repo_cargo.py`**: ローカルのRustリポジトリに対する`cargo install`の自動更新を処理します。
            - **`local_repo_checker.py`**: ローカルリポジトリの状態（pull可能かどうか）をチェックします。
            - **`local_repo_git.py`**: ローカルリポジトリに対するgit操作（fetch, pull）を実行します。
            - **`local_repo_watcher.py`**: 親ディレクトリ内のローカルリポジトリを監視し、自動pullを管理します。
            - **`monitor.py`**: メインの監視ロジックとループを管理します。
            - **`pages_watcher.py`**: GitHub Pagesのデプロイ状況などを監視する機能を提供します。
            - **`pr_processor.py`**: 取得したPRデータに基づき、フェーズ判定やアクション実行を行います。
            - **`snapshot_path_utils.py`**: 状態のスナップショットパスに関するユーティリティ関数を提供します。
            - **`state_tracker.py`**: 監視対象のPRやリポジトリの状態を追跡し、変更を検知します。
        - **`phase/`**: PRのフェーズ判定ロジックを含むモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`html/`**: PRページのHTMLコンテンツ解析に関連するモジュール群です。
                - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
                - **`html_status_processor.py`**: PRのHTMLからステータス情報を処理します。
                - **`llm_status_extractor.py`**: HTMLからLLMの作業状況に関する情報を抽出します。
                - **`pr_html_analyzer.py`**: PRのHTMLコンテンツを解析し、特定の情報（例：レビューコメント）を抽出します。
                - **`pr_html_fetcher.py`**: PRページのHTMLコンテンツを取得します。
                - **`pr_html_saver.py`**: 取得したPRのHTMLコンテンツを保存します。
            - **`phase_detector.py`**: PRの現在の状態（Draft, レビュー指摘対応中, レビュー待ち, LLM作業中）を判定する主要なロジックを提供します。
        - **`ui/`**: ユーザーインターフェース（ターミナル表示、通知）関連のモジュール群です。
            - **`__init__.py`**: Pythonパッケージを示すためのファイルです。
            - **`display.py`**: ターミナルにPRのステータスやその他の情報を表示する機能を提供します。
            - **`notification_window.py`**: ブラウザ自動操作中に小さな通知ウィンドウを表示する機能を提供します。
            - **`notifier.py`**: ntfy.shを介してモバイル通知を送信する機能を提供します。
            - **`wait_handler.py`**: 監視ループ間の待機時間を処理します。
- **`tests/`**: プロジェクトのテストコードが格納されるディレクトリです。各`test_*.py`ファイルが特定の機能に対するテストを含みます。

## 関数詳細説明
このプロジェクトはモジュール化されており、多くの関数が特定の役割を担っています。以下に主要な機能を提供するであろう関数の役割を説明します。具体的な引数や戻り値は、ハルシネーションを避けるため記述しません。

- **`main()`**:
    - **役割**: ツールの実行エントリーポイントとして、設定のロード、監視ループの初期化と開始を行います。
    - **機能**: プログラム全体の設定を読み込み、GitHubクライアントやその他の必要なコンポーネントを初期化し、定期的なPR監視サイクルを開始します。
- **`load_config()`**:
    - **役割**: 設定ファイル（`config.toml`）を読み込み、解析します。
    - **機能**: TOML形式の設定ファイルを読み込み、プログラムで使用できるPythonオブジェクトとして設定値を提供します。
- **`fetch_repositories()`**:
    - **役割**: 認証済みユーザーが所有するGitHubリポジトリのリストを取得します。
    - **機能**: GitHub API（GraphQL）を利用して、監視対象となるリポジトリの基本情報を取得します。
- **`fetch_pull_requests(repository)`**:
    - **役割**: 指定されたリポジトリのオープンなプルリクエストを取得します。
    - **機能**: GitHub API（GraphQL）を利用して、各PRの詳細情報（ステータス、コメント、レビュー状況など）を取得します。
- **`detect_phase(pr_data)`**:
    - **役割**: 提供されたPRデータに基づき、PRの現在のフェーズを判定します。
    - **機能**: PRのDraft状態、レビューコメントの有無、特定のBot（`copilot-pull-request-reviewer`, `copilot-swe-agent`）からのコメントや活動状況を分析し、`phase1`, `phase2`, `phase3`, `LLM working`のいずれかのフェーズを決定します。
- **`execute_pr_action(pr_info, phase, ruleset)`**:
    - **役割**: PRのフェーズと設定されたルールセットに基づいて、対応するアクションを実行します。
    - **機能**: PRをReady状態にする、レビュー指摘対応を促すコメントを投稿する、ntfy.shで通知を送信する、PRを自動マージする、ブラウザでPRページを開くなどの操作を行います。Dry-runモードでは実際には実行しません。
- **`post_comment(pr_id, repository_id, comment_body)`**:
    - **役割**: 指定されたPRにコメントを投稿します。
    - **機能**: GitHub APIを介して、指定されたPRにテキストコメントを追加します。
- **`send_notification(message, url)`**:
    - **役割**: ntfy.shサービスを通じて通知を送信します。
    - **機能**: PRがレビュー待ちになった際などに、設定されたトピックとメッセージでモバイル通知をトリガーします。
- **`open_browser(url)`**:
    - **役割**: 指定されたURLをデフォルトブラウザで開きます。
    - **機能**: PRページやissueページなどをユーザーに直接表示します。
- **`assign_issue_to_copilot(issue_url, config)`**:
    - **役割**: 特定の条件を満たすissueをCopilotに自動割り当てします。
    - **機能**: `PyAutoGUI`やOCRを利用してブラウザを自動操作し、「Assign to Copilot」ボタンをクリックしてissueの担当者を割り当てます。
- **`check_and_pull_local_repos()`**:
    - **役割**: 親ディレクトリ内のローカルリポジトリの更新状態をチェックし、必要であれば自動で`git pull`を実行します。
    - **機能**: `git fetch`を実行してリモートとの差分を確認し、`auto_git_pull`設定が有効な場合は`git pull`を実行してローカルリポジトリを最新の状態に保ちます。
- **`update_cargo_install_repos()`**:
    - **役割**: `cargo install`で管理されているリポジトリのバイナリを自動更新します。
    - **機能**: `cargo_install_repos`に設定されたリポジトリについて、`git pull`後に`cargo install --force`を実行し、バイナリを最新版に更新します。
- **`run_update_check()`**:
    - **役割**: ツールの自己更新チェックを行います。
    - **機能**: Gitを使って自身のコードベースの更新を確認し、`enable_auto_update`が有効な場合は自動で`git pull`と再起動を実行します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。

---
Generated at: 2026-04-08 07:09:55 JST
