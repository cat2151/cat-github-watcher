Last updated: 2026-03-04

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動生成するプルリクエスト（PR）のフェーズを効率的に監視するPythonツールです。
- PRの状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定し、通知や自動アクションを実行します。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIとブラウザ自動化を活用して開発ワークフローを効率化します。

## 技術スタック
- フロントエンド: このプロジェクトはCLIツールであり、特定のフロントエンド技術は使用していません。ターミナル出力の視認性を高めるためにANSIカラーコードが利用されています。
- 音楽・オーディオ: 該当する技術はありません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub APIとの認証済み連携と基本的な操作のために使用されます。
    - **Git**: リポジトリのクローン、更新検知（`git fetch`）、自動プル（`git pull`）のために利用されます。
    - **PyAutoGUI**: ブラウザのUIを自動操作し、ボタンクリックなどのアクションを実行するために使用されます。
    - **Pillow**: PyAutoGUIの依存関係として、画像処理（スクリーンショットの読み込み、操作）に必要です。
    - **Pygetwindow**: PyAutoGUIの依存関係として、ウィンドウ管理（アクティブ化、最大化など）に使用されます。
    - **pytesseract**: OCR（光学文字認識）フォールバックのために使用され、画面上のテキストからボタンを検出します。
    - **tesseract-ocr**: pytesseractのシステムレベルの依存ツールで、実際のOCR処理を行います。
    - **pytest**: プロジェクトのテストスイートを実行するために使用されるPythonのテスティングフレームワークです。
    - **ruff**: Pythonコードの整形と品質チェックを行うための高速リンター・フォーマッターです。
    - **VS Code**: 開発環境として推奨され、`.vscode/settings.json`で設定が提供されています。
- テスト:
    - **pytest**: Pythonアプリケーションの単体テストおよび統合テストを記述・実行するために使用されます。
- ビルドツール:
    - **Python 3.10+**: プロジェクトの実行環境および主要言語です。
    - **pip**: Pythonパッケージのインストールと管理に使用されます。
- 言語機能:
    - **Python 3.10+**: 型ヒント、f-string、構造化パターンマッチングなど、モダンなPython言語機能が活用されています。
- 自動化・CI/CD:
    - **GitHub Actions**: README.mdの自動生成など、一部のCI/CDプロセスに利用されています（監視ツール本体とは別）。
    - **Git (自動pull機能)**: 自身のツールやローカルリポジトリの自動更新のために使用されます。
    - **PyAutoGUI**: ブラウザベースのGitHub操作（PRマージ、Issue割り当てなど）の自動化を可能にします。
- 開発標準:
    - **ruff**: コードのスタイルガイド強制とエラーチェックを通じて、コード品質と一貫性を保ちます。
    - **EditorConfig**: 異なるエディタやIDE間でのコードスタイルの統一を支援します。
    - **TOML**: 設定ファイル（`config.toml`）の記述形式として使用され、人間が読み書きしやすい構造化された設定を提供します。

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
- **`cat-github-watcher.py`**:
    - このプロジェクトのメインエントリーポイントとなるスクリプトです。コマンドライン引数から設定ファイルを読み込み、監視ツールの中核となる`main.py`の実行を起動します。
- **`config.toml.example`**:
    - ユーザーが独自の`config.toml`を作成する際のテンプレートファイルです。監視間隔、通知設定、自動化ルール、カラーテーマなど、様々な設定オプションの例と説明が含まれています。
- **`requirements-automation.txt`**:
    - ブラウザ自動化機能（PyAutoGUI、OCRなど）に必要な追加のPythonライブラリをリストアップしたファイルです。このファイルを使って関連する依存関係をインストールできます。
- **`src/gh_pr_phase_monitor/main.py`**:
    - 監視ツールの中心的な実行ロジックを含むファイルです。設定の初期化、GitHubクライアントのセットアップ、メインの監視ループの実行、および各種モジュールの連携を管理します。
- **`src/gh_pr_phase_monitor/config.py`**:
    - プロジェクトの設定（`config.toml`）を読み込み、解析、バリデーションする役割を担います。様々な設定値やルールセットを適切に管理し、他のモジュールが利用できるように提供します。
- **`src/gh_pr_phase_monitor/github_client.py`**:
    - GitHub API（RESTおよびGraphQL）との連携を担当するクライアントモジュールです。リポジトリ、プルリクエスト、Issueなどの情報をGitHubから取得・更新するための高レベルなインターフェースを提供します。
- **`src/gh_pr_phase_monitor/graphql_client.py`**:
    - GitHubのGraphQL APIに特化した低レベルなクライアントです。効率的なクエリの構築と実行を通じて、必要なデータを最小限のAPIコールで取得します。
- **`src/gh_pr_phase_monitor/github_auth.py`**:
    - GitHub CLI (`gh`) を利用した認証情報の管理と、GitHub APIへのアクセス権限の確保を担当します。
- **`src/gh_pr_phase_monitor/repository_fetcher.py`**:
    - 認証済みユーザーが所有するすべてのリポジトリをGitHubから取得するロジックを実装しています。監視対象となるリポジトリの特定に利用されます。
- **`src/gh_pr_phase_monitor/pr_fetcher.py`**:
    - 特定のリポジトリまたはすべての監視対象リポジトリから、オープンなプルリクエストの詳細情報を取得する役割を担います。
- **`src/gh_pr_phase_monitor/issue_fetcher.py`**:
    - オープンなIssueを取得し、特定のラベル（`good first issue`、`ci-failure`など）に基づいてフィルタリングする機能を提供します。Issueの自動割り当て機能で利用されます。
- **`src/gh_pr_phase_monitor/phase_detector.py`**:
    - プルリクエストのステータス、タイトル、レビューコメントの有無などに基づき、PRが現在どのフェーズ（Draft状態、レビュー指摘対応中、レビュー待ち、LLM working）にあるかを判定する中心的なロジックを実装しています。
- **`src/gh_pr_phase_monitor/comment_manager.py`**:
    - プルリクエストにコメントを投稿したり、既存のコメントを解析したりする機能を提供します。特に、フェーズに応じた自動コメント投稿やエージェントへのメンション処理を管理します。
- **`src/gh_pr_phase_monitor/pr_actions.py`**:
    - プルリクエストに対する具体的なアクション（例: DraftからReadyへの変更、ブラウザでのPRページ起動、自動マージ、コメント投稿）を実行するモジュールです。
- **`src/gh_pr_phase_monitor/notifier.py`**:
    - ntfy.shサービスを利用して、モバイルデバイスへの通知を送信する機能を提供します。PRがレビュー待ちになった際などにユーザーにアラートを送ります。
- **`src/gh_pr_phase_monitor/browser_automation.py`**:
    - PyAutoGUIを用いたブラウザの自動操作に関する共通ロジックをカプセル化しています。ボタンクリック、ウィンドウのアクティブ化、スクリーンショット撮影、OCR検出などを担当します。
- **`src/gh_pr_phase_monitor/button_clicker.py`**:
    - `browser_automation.py`から利用され、具体的なボタン検出とクリック操作に特化した機能を提供します。
- **`src/gh_pr_phase_monitor/notification_window.py`**:
    - ブラウザ自動操作中に、画面上に小さな情報通知ウィンドウを表示する機能を提供します。
- **`src/gh_pr_phase_monitor/window_manager.py`**:
    - 実行中のアプリケーションウィンドウ（特にブラウザ）を管理し、適切なフォーカスや状態を維持するためのヘルパー機能を提供します。
- **`src/gh_pr_phase_monitor/click_config_validator.py`**:
    - ブラウザ自動化に関連する設定（スクリーンショットパス、信頼度、OCR有効化など）のバリデーションを行います。
- **`src/gh_pr_phase_monitor/auto_updater.py`**:
    - ツール自身のGitHubリポジトリを監視し、新しい更新がある場合に自動的に`git pull`を行い、ツールを再起動する機能を提供します。
- **`src/gh_pr_phase_monitor/local_repo_watcher.py`**:
    - 親ディレクトリにあるユーザーのローカルGitリポジトリを監視し、リモートに変更がある場合に`git pull`が利用可能かどうかを検知し、設定に応じて自動実行します。
- **`src/gh_pr_phase_monitor/display.py`**:
    - ターミナルへの情報出力のフォーマットと表示を担当します。カラースキームや詳細表示モードなどを考慮し、見やすい出力を生成します。
- **`src/gh_pr_phase_monitor/colors.py`**:
    - ターミナル出力で使用するANSIカラーコードと、それらを適用するユーティリティ関数を提供します。異なるカラースキーム（`monokai`、`classic`）をサポートします。
- **`src/gh_pr_phase_monitor/config_printer.py`**:
    - 起動時やverboseモードで、現在の設定内容を詳細にターミナルに出力する機能を提供し、設定ミスのデバッグを支援します。
- **`src/gh_pr_phase_monitor/state_tracker.py`**:
    - 各PRの状態変化を追跡し、一定期間変化がない場合に省電力モードへの移行などを判断するロジックを管理します。
- **`src/gh_pr_phase_monitor/time_utils.py`**:
    - 時間に関するユーティリティ関数（期間のパース、経過時間計算など）を提供します。
- **`src/gh_pr_phase_monitor/interval_parser.py`**:
    - "30s", "1m", "1h" といった文字列形式の監視間隔を数値（秒）に変換するパーサーです。
- **`src/gh_pr_phase_monitor/rate_limit_handler.py`**:
    - GitHub APIのレート制限に関する情報を表示し、必要に応じてリクエストをスロットル（間隔調整）することで、制限超過を防ぐ役割を担います。
- **`src/gh_pr_phase_monitor/wait_handler.py`**:
    - 非同期処理における待機（スリープ）を管理し、中断シグナル（Ctrl+C）に適切に対応するユーティリティです。
- **`src/gh_pr_phase_monitor/browser_cooldown.py`**:
    - ブラウザを頻繁に開くことによる過負荷を防ぐため、ブラウザ起動間のクールダウン（冷却期間）を管理します。
- **`src/gh_pr_phase_monitor/process_utils.py`**:
    - 外部プロセス（例: `gh`コマンド）の実行や管理に関連するユーティリティ関数を提供します。
- **`src/gh_pr_phase_monitor/llm_status_extractor.py`**:
    - PRのコメントや説明から、LLM（大規模言語モデル）エージェントの作業状況を示す特定のキーワードやパターンを抽出し、フェーズ判定に役立てます。
- **`src/gh_pr_phase_monitor/pages_watcher.py`**:
    - GitHub Pagesのデプロイ状況などを監視する機能（詳細は明示されていないが、名前から推測）を提供します。
- **`src/gh_pr_phase_monitor/pr_data_recorder.py`**:
    - PRのデータをJSON形式やHTML形式で記録し、デバッグや履歴管理に利用する機能を提供します。
- **`src/gh_pr_phase_monitor/pr_html_analyzer.py`**:
    - PRのHTMLコンテンツを解析し、特定の要素（ボタン、コメントなど）を検出する機能を提供します。
- **`src/gh_pr_phase_monitor/pr_html_fetcher.py`**:
    - 特定のPRページのHTMLコンテンツをダウンロードする機能を提供します。
- **`src/gh_pr_phase_monitor/pr_html_saver.py`**:
    - 取得したPRのHTMLコンテンツをローカルに保存する機能を提供します。
- **`src/gh_pr_phase_monitor/snapshot_markdown.py`**:
    - HTMLスナップショットをMarkdown形式に変換する機能を提供します。
- **`src/gh_pr_phase_monitor/snapshot_path_utils.py`**:
    - スナップショットファイルのパスを管理するユーティリティです。
- **`screenshots/`**:
    - ブラウザ自動化機能がPyAutoGUIでボタンを検出するために使用する、ボタンのスクリーンショット画像（例: `assign.png`, `merge_pull_request.png`）を保存するディレクトリです。
- **`tests/`**:
    - プロジェクトの単体テストおよび統合テストスクリプトが格納されているディレクトリです。各テストファイルは特定のモジュールや機能の動作を検証します。
- **`.editorconfig`**:
    - さまざまなエディタやIDEでコードのインデントスタイル、文字コード、行末文字などを統一するための設定ファイルです。
- **`.gitignore`**:
    - Gitがバージョン管理の対象としないファイルやディレクトリを指定するファイルです（例: ログファイル、キャッシュ、仮想環境など）。
- **`.vscode/settings.json`**:
    - Visual Studio Codeエディタのプロジェクト固有の設定ファイルです。リンター（ruff）やフォーマッター、Pythonインタープリタのパスなどが設定されます。
- **`LICENSE`**:
    - プロジェクトのライセンス情報（MIT License）が記述されたファイルです。
- **`MERGE_CONFIGURATION_EXAMPLES.md`**:
    - PRの自動マージに関する設定例や詳細なガイダンスを提供するドキュメントです。
- **`PHASE3_MERGE_IMPLEMENTATION.md`**:
    - Phase3でのPR自動マージ機能の実装に関する技術的な詳細や背景を説明するドキュメントです。
- **`README.ja.md`**:
    - プロジェクトの日本語版説明書です。概要、特徴、使い方、設定方法などが記載されています。
- **`README.md`**:
    - プロジェクトの英語版説明書です。日本語版READMEを基に自動生成されます。
- **`STRUCTURE.md`**:
    - プロジェクトのディレクトリ構成やアーキテクチャに関する概要を説明するドキュメントです。
- **`docs/`**:
    - 追加のドキュメントが格納されるディレクトリです。
    - **`docs/RULESETS.md`**:
        - 設定ファイルにおける「rulesets」機能の詳細な説明と使用例を提供するドキュメントです。
    - **`docs/button-detection-improvements.ja.md`**:
        - ブラウザ自動化におけるボタン検出機能の改善点や技術詳細を説明する日本語ドキュメントです。
    - **`docs/window-activation-feature.md`**:
        - ブラウザ自動化におけるウィンドウアクティベーション機能について説明するドキュメントです。
- **`pytest.ini`**:
    - pytestテストランナーの設定ファイルです。テストの発見方法やプラグインなどが指定されます。
- **`ruff.toml`**:
    - `ruff`リンター・フォーマッターの設定ファイルです。適用するルール、除外するファイル、フォーマットオプションなどが定義されています。

## 関数詳細説明
このプロジェクトは多くのモジュールで構成されており、それぞれが特定の役割を担っています。以下に、主要なモジュールで中心的な役割を果たすと思われる関数の説明を、一般的な引数と戻り値の形式で記述します。

- **`run_monitor(config: dict, github_client: object) -> None`**
    - **役割**: プロジェクトのメイン監視ループを開始します。設定された間隔でPRの状態を定期的にチェックし、必要なアクションをトリガーします。
    - **引数**:
        - `config`: プロジェクト全体の設定を保持する辞書または設定オブジェクト。
        - `github_client`: GitHub APIと連携するためのクライアントインスタンス。
    - **戻り値**: なし。ループ内で継続的に動作します。
    - **機能**: 監視の心臓部であり、PRデータの取得、フェーズ判定、アクション実行、通知、自己更新などの全ての主要機能を連携させ、全体の処理フローを制御します。

- **`load_config(config_path: str) -> dict`**
    - **役割**: 指定されたパスのTOMLファイルから設定を読み込み、解析します。
    - **引数**:
        - `config_path`: 設定ファイル（例: `config.toml`）への文字列パス。
    - **戻り値**: 解析された設定データを保持する辞書オブジェクト。
    - **機能**: ユーザーが定義した監視間隔、Dry-runモード、通知設定、自動化ルールなど、アプリケーション全体の動作を制御する設定値をロードし、提供します。

- **`fetch_pull_requests(owner: str, github_client: object) -> list`**
    - **役割**: 指定されたGitHubユーザーが所有するリポジトリから、オープンなプルリクエストのリストを取得します。
    - **引数**:
        - `owner`: GitHubのユーザー名。
        - `github_client`: GitHub APIと連携するためのクライアントインスタンス。
    - **戻り値**: 各プルリクエストの詳細情報を含む辞書のリスト。
    - **機能**: 監視対象となるすべてのプルリクエストの基本情報をGitHubから収集し、後続のフェーズ判定やアクション実行の基盤データを提供します。

- **`detect_pr_phase(pr_data: dict, comments: list) -> str`**
    - **役割**: プルリクエストの現在のステータス、コメント履歴、レビュー状況などに基づいて、PRのフェーズ（例: "phase1", "phase2", "phase3", "LLM working"）を判定します。
    - **引数**:
        - `pr_data`: 特定のプルリクエストの詳細データ。
        - `comments`: そのプルリクエストに関連するコメントのリスト。
    - **戻り値**: 判定されたフェーズ名を表す文字列。
    - **機能**: 各PRの状態を自動的に分類し、その分類結果に応じて適切な自動アクションをトリガーするための重要なロジックを提供します。

- **`execute_pr_action(pr_data: dict, phase: str, ruleset: dict, github_client: object) -> bool`**
    - **役割**: PRのフェーズと適用されるルールセットに基づき、PRの「Ready化」、コメント投稿、自動マージ、ブラウザでのPRページ表示などの具体的なアクションを実行します。
    - **引数**:
        - `pr_data`: アクションの対象となるプルリクエストの詳細データ。
        - `phase`: 現在判定されたPRのフェーズ。
        - `ruleset`: 現在のリポジトリまたは全体に適用される自動化ルールを含む辞書。
        - `github_client`: GitHub APIと連携するためのクライアントインスタンス。
    - **戻り値**: アクションが正常に実行された場合は`True`、それ以外は`False`。
    - **機能**: フェーズ判定結果とユーザー設定に従って、GitHub上のプルリクエストに対して具体的な操作を行い、開発ワークフローの自動化を実現します。

- **`send_notification(topic: str, message: str, url: str = None, priority: int = 3) -> bool`**
    - **役割**: ntfy.shサービスを利用して、指定されたトピックに通知メッセージを送信します。
    - **引数**:
        - `topic`: ntfy.shの通知トピック名。
        - `message`: 通知として送信するテキストメッセージ。
        - `url`: (オプション) 通知に関連するURL。クリック可能なアクションボタンとして提供されます。
        - `priority`: (オプション) 通知の優先度（1:低〜5:最高）。
    - **戻り値**: 通知が正常に送信された場合は`True`、失敗した場合は`False`。
    - **機能**: 重要なPRの状態変化（特にレビュー待ち）をユーザーにリアルタイムで知らせ、モバイルデバイスを介して素早い対応を促します。

- **`click_button_in_browser(button_name: str, screenshot_paths: list, config: dict) -> bool`**
    - **役割**: PyAutoGUIを使用して、ブラウザ画面上の特定のボタン（スクリーンショットで定義）を検出し、クリック操作を実行します。OCRによるテキスト検出をフォールバックとしてサポートします。
    - **引数**:
        - `button_name`: クリックしようとしているボタンの識別名（デバッグログ用）。
        - `screenshot_paths`: ボタンの画像テンプレートへのパスのリスト。
        - `config`: 自動化に関する設定（信頼度、OCR有効化、デバッグディレクトリなど）。
    - **戻り値**: ボタンが正常にクリックされた場合は`True`、見つからなかったりクリックに失敗した場合は`False`。
    - **機能**: ブラウザを介した手動操作（PRのマージボタンクリック、Issueの割り当てボタンクリックなど）を自動化し、繰り返しの作業負荷を軽減し、効率を向上させます。

## 関数呼び出し階層ツリー
```
関数呼び出し階層は、提供された情報からは詳細に分析できませんでした。
しかし、プロジェクトの構造とファイル説明から、一般的な呼び出しフローは以下のようになると推測されます：

cat-github-watcher.py (エントリーポイント)
└── run_monitor() (src/gh_pr_phase_monitor/main.py)
    ├── load_config() (src/gh_pr_phase_monitor/config.py)
    ├── fetch_pull_requests() (src/gh_pr_phase_monitor/github_client.py)
    │   └── graphql_client.execute_query() (src/gh_pr_phase_monitor/graphql_client.py)
    ├── detect_pr_phase() (src/gh_pr_phase_monitor/phase_detector.py)
    │   └── llm_status_extractor.extract_status() (src/gh_pr_phase_monitor/llm_status_extractor.py)
    ├── execute_pr_action() (src/gh_pr_phase_monitor/pr_actions.py)
    │   ├── comment_manager.post_comment() (src/gh_pr_phase_monitor/comment_manager.py)
    │   ├── send_notification() (src/gh_pr_phase_monitor/notifier.py)
    │   └── click_button_in_browser() (src/gh_pr_phase_monitor/browser_automation.py)
    │       ├── button_clicker.find_and_click_button() (src/gh_pr_phase_monitor/button_clicker.py)
    │       └── notification_window.show_notification() (src/gh_pr_phase_monitor/notification_window.py)
    ├── auto_updater.check_and_update() (src/gh_pr_phase_monitor/auto_updater.py)
    └── local_repo_watcher.watch_local_repos() (src/gh_pr_phase_monitor/local_repo_watcher.py)

---
Generated at: 2026-03-04 07:04:14 JST
