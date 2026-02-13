Last updated: 2026-02-14

# Project Overview

## プロジェクト概要
- GitHub Copilotなどによる自動実装のプルリクエスト（PR）のフェーズを効率的に監視するPythonツールです。
- 認証済みユーザーの全所有リポジトリを対象に、GraphQL APIを用いてPRの状態を自動判定し、通知やアクションを実行します。
- Dry-runモードや省電力モード、モバイル通知、自動コメント投稿など豊富な機能を備え、開発者のレビューワークフローを支援します。

## 技術スタック
- フロントエンド: PyAutoGUI (ブラウザ自動操作), Pygetwindow (ウィンドウ管理), Pillow (画像処理) - これらは直接のUIではなく、ブラウザの自動操作に使用されます。
- 音楽・オーディオ: 該当なし
- 開発ツール: GitHub CLI (`gh`) (GitHub認証・操作), Python (メイン開発言語), .editorconfig (コーディングスタイル統一), .vscode/settings.json (VS Code設定), Ruff (Python Linter)
- テスト: pytest (テストフレームワーク)
- ビルドツール: Pythonの実行環境とpip (依存関係管理) が主体であり、専用のビルドツールは含まれません。
- 言語機能: Python 3.10以上 (実行環境)
- 自動化・CI/CD: ntfy.sh (モバイル通知サービス), GitHub Actions (READMEで言及あり、ただしPR監視には不採用、ドキュメント自動生成などに使用)
- 開発標準: .editorconfig (エディタ設定), ruff.toml (リンター設定), .vscode/settings.json (IDE設定)

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
（提供されたツリーは一部でしたので、プロジェクト情報にあるディレクトリ構成をベースに再構築しました。完全なファイル階層ツリーは下記に補足します。）
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
│   ├── RULESETS.md
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
│       ├── pr_data_recorder.py
│       ├── pr_fetcher.py
│       ├── repository_fetcher.py
│       ├── state_tracker.py
│       ├── time_utils.py
│       └── wait_handler.py
└── tests/
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_check_process_before_autoraise.py
    ├── test_color_scheme_config.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_error_logging.py
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
    ├── test_pr_data_recorder.py
    ├── test_pr_title_fix.py
    ├── test_repos_with_prs_structure.py
    ├── test_show_issues_when_pr_count_less_than_3.py
    ├── test_status_summary.py
    ├── test_validate_phase3_merge_config.py
    └── test_verbose_config.py
```

## ファイル詳細説明
-   **`.editorconfig`**: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイルです。
-   **`.gitignore`**: Gitが追跡しないファイルやディレクトリを指定する設定ファイルです。
-   **`.vscode/settings.json`**: Visual Studio Codeエディタのワークスペース固有の設定を定義します。
-   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）が記述されています。
-   **`MERGE_CONFIGURATION_EXAMPLES.md`**: マージ設定に関する設定例を説明するドキュメントです。
-   **`PHASE3_MERGE_IMPLEMENTATION.md`**: フェーズ3でのPR自動マージ機能の実装詳細に関するドキュメントです。
-   **`README.ja.md`**: プロジェクトの日本語版概要、セットアップ、使い方、機能などを説明する主要なドキュメントです。
-   **`README.md`**: プロジェクトの英語版概要ドキュメントです。
-   **`STRUCTURE.md`**: プロジェクトの全体構造について説明するドキュメントです。
-   **`_config.yml`**: おそらくGitHub Pagesなどのドキュメントサイト設定ファイルです。
-   **`cat-github-watcher.py`**: プロジェクトのメインエントリーポイントとなるPythonスクリプトです。
-   **`config.toml.example`**: ユーザーがコピーして使用できる設定ファイル（`config.toml`）のサンプルです。監視間隔、通知設定、自動化ルールなどが定義されています。
-   **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーション用スクリプトである可能性があります。
-   **`docs/`**: プロジェクトの各種ドキュメントを格納するディレクトリです。
    -   **`RULESETS.md`**: ルールセットの設定と使用方法について説明するドキュメントです。
    -   **`button-detection-improvements.ja.md`**: ボタン検出機能の改善に関する日本語ドキュメントです。
    -   **`window-activation-feature.md`**: ウィンドウアクティベーション機能に関するドキュメントです。
-   **`generated-docs/`**: AIによって生成されたドキュメントを格納するディレクトリであると推測されます。
-   **`pytest.ini`**: pytestテストフレームワークの設定ファイルです。
-   **`requirements-automation.txt`**: ブラウザ自動化（PyAutoGUIなど）に必要なPythonライブラリをリストアップしたファイルです。
-   **`ruff.toml`**: Pythonコードの品質チェックを行うLinter「Ruff」の設定ファイルです。
-   **`screenshots/`**: ブラウザ自動操作で使用するボタンの画像ファイル（スクリーンショット）を格納するディレクトリです。
    -   **`assign.png`**: 「Assign」ボタンのスクリーンショット。
    -   **`assign_to_copilot.png`**: 「Assign to Copilot」ボタンのスクリーンショット。
-   **`src/`**: プロジェクトの主要なソースコードが格納されるディレクトリです。
    -   **`__init__.py`**: Pythonパッケージを示すファイルです。
    -   **`gh_pr_phase_monitor/`**: PR監視機能の中核となるPythonパッケージです。
        -   **`__init__.py`**: `gh_pr_phase_monitor`パッケージを示すファイルです。
        -   **`browser_automation.py`**: PyAutoGUIなどを用いてブラウザを自動操作する機能を提供します。
        -   **`colors.py`**: ターミナル出力用のANSIカラーコードと色付けユーティリティを定義します。
        -   **`comment_fetcher.py`**: GitHub PRのコメント情報を取得する機能を提供します。
        -   **`comment_manager.py`**: PRへのコメント投稿、内容確認、および関連する処理を管理します。
        -   **`config.py`**: `config.toml`ファイルから設定を読み込み、解析、検証するロジックを含みます。
        -   **`display.py`**: 監視結果やステータス情報をターミナルに整形して表示する機能を提供します。
        -   **`github_auth.py`**: GitHub CLI (`gh`) を使用してGitHub認証を処理する機能を提供します。
        -   **`github_client.py`**: GitHub API（主にGraphQL）との高レベルな連携機能を提供します。
        -   **`graphql_client.py`**: GitHub GraphQL APIへのリクエストを構築し、実行するための低レベルなクライアントを提供します。
        -   **`issue_fetcher.py`**: GitHubリポジトリからIssue情報を取得する機能を提供します。
        -   **`main.py`**: 監視アプリケーションのメイン実行ループと、各モジュールのオーケストレーションを担当します。
        -   **`monitor.py`**: 実際のPR監視ロジックと、設定された間隔での定期実行を管理するコアモジュールです。
        -   **`notifier.py`**: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
        -   **`phase_detector.py`**: プルリクエストの現在の状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中など）を判定するロジックを含みます。
        -   **`pr_actions.py`**: PRのReady化、ブラウザでのPRページ開閉、自動マージなど、PRに対して実行される各種アクションを定義・実行します。
        -   **`pr_data_recorder.py`**: 各PRの状態や関連データを記録し、履歴を追跡する機能を提供します。
        -   **`pr_fetcher.py`**: オープンなプルリクエスト情報を取得する機能を提供します。
        -   **`repository_fetcher.py`**: 認証済みユーザーが所有するGitHubリポジトリのリストを取得する機能を提供します。
        -   **`state_tracker.py`**: PR全体の状態変化を追跡し、省電力モードの切り替えなどを管理します。
        -   **`time_utils.py`**: 時間間隔のパースや変換など、時間に関するユーティリティ関数を提供します。
        -   **`wait_handler.py`**: 監視ループ間隔の待機処理を管理し、省電力モードを考慮します。
-   **`tests/`**: プロジェクトの単体テスト、結合テスト、およびシステムテストを格納するディレクトリです。

## 関数詳細説明
プロジェクト情報から具体的な引数や戻り値の型まで特定は困難なため、主な機能と役割を説明します。

-   **`main.py` の `main()`**:
    -   **役割**: アプリケーションのメインエントリポイント。設定の読み込み、GitHub認証、監視ループの開始と管理を行います。
    -   **引数**: `config_path` (設定ファイルのパス、オプション)
    -   **戻り値**: なし
    -   **機能**: プログラム全体を統括し、定期的にリポジトリとPRの状態を監視し、必要なアクションを実行するサイクルを回します。

-   **`config.py` の `load_config(config_path)`**:
    -   **役割**: TOML形式の設定ファイルを読み込み、解析し、アプリケーションの設定オブジェクトを生成します。
    -   **引数**: `config_path` (読み込む設定ファイルのパス)
    -   **戻り値**: 解析された設定を表すオブジェクト
    -   **機能**: 監視間隔、通知設定、自動化ルール、カラーテーマなど、アプリケーションの挙動を定義する情報を取得します。

-   **`github_client.py` の `fetch_pull_requests(repository_id, num_prs=100)`**:
    -   **役割**: 指定されたGitHubリポジトリからオープンなプルリクエストの情報をGraphQL API経由で取得します。
    -   **引数**: `repository_id` (GitHubリポジトリのID), `num_prs` (取得するPRの最大数)
    -   **戻り値**: プルリクエストのリスト（各PRのID、タイトル、ステータス、コメントなどの情報を含む）
    -   **機能**: PR監視の基盤となる最新のPRデータをGitHubから取得します。

-   **`phase_detector.py` の `detect_phase(pr_data, rulesets)`**:
    -   **役割**: プルリクエストのデータと設定されたルールに基づいて、現在のPRフェーズ（phase1, phase2, phase3, LLM working）を判定します。
    -   **引数**: `pr_data` (単一のプルリクエストデータ), `rulesets` (適用されるルールセット)
    -   **戻り値**: 判定されたフェーズを示す文字列
    -   **機能**: PRのDraft状態、レビューコメントの有無、特定のBotからのコメントなどを分析し、その開発段階を特定します。

-   **`pr_actions.py` の `perform_actions_based_on_phase(pr_data, phase, config)`**:
    -   **役割**: 判定されたPRフェーズに基づいて、コメント投稿、PRのReady化、通知送信、自動マージなどの具体的なアクションを実行します。
    -   **引数**: `pr_data` (単一のプルリクエストデータ), `phase` (判定されたフェーズ), `config` (アプリケーション設定)
    -   **戻り値**: 実行されたアクションの結果
    -   **機能**: Dry-runモードや有効化されたルールセットに従い、GitHub上でPRの状態変更やインタラクションを自動化します。

-   **`notifier.py` の `send_ntfy_notification(topic, message, url, priority)`**:
    -   **役割**: ntfy.shサービスを利用してモバイルデバイスに通知を送信します。
    -   **引数**: `topic` (ntfy.shのトピック名), `message` (通知メッセージ), `url` (通知に含めるURL), `priority` (通知の優先度)
    -   **戻り値**: 通知送信の成否
    -   **機能**: PRがレビュー待ち（phase3）になった際などに、開発者にリアルタイムでアラートを送ります。

-   **`browser_automation.py` の `open_browser_and_click_button(url, button_name, screenshots_dir, config_section)`**:
    -   **役割**: 指定されたURLをブラウザで開き、PyAutoGUIを用いた画像認識やOCRにより特定のボタンを見つけてクリックします。
    -   **引数**: `url` (開くURL), `button_name` (クリックするボタンの名前), `screenshots_dir` (ボタン画像のディレクトリ), `config_section` (自動化設定セクション)
    -   **戻り値**: ボタンクリックの成否
    -   **機能**: Issueの自動割り当てやPRの自動マージなど、GitHub Web UI上の操作を自動化します。

-   **`state_tracker.py` の `update_pr_state(repo_full_name, pr_id, new_phase)` と `check_for_state_change(repo_full_name)`**:
    -   **役割**: 各PRの最新フェーズを記録し、全体の状態変化を追跡します。これにより、一定期間状態変化がない場合に省電力モードへの切り替えを判断します。
    -   **引数**: `repo_full_name` (リポジトリ名), `pr_id` (プルリクエストID), `new_phase` (新しいフェーズ)
    -   **戻り値**: `update_pr_state`はなし、`check_for_state_change`は状態が変化したかどうかのブール値
    -   **機能**: 監視サイクルにおけるAPI使用量を最適化し、サーバーへの負荷を軽減します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。
（提供されたプロジェクト情報から関数の具体的な呼び出し関係を自動で構築することはできませんでした。）

しかし、プロジェクトの概要とファイル構造から、以下のような主要な処理の流れが想定されます：

cat-github-watcher.py (エントリーポイント)
└── src.gh_pr_phase_monitor.main.main()
    ├── src.gh_pr_phase_monitor.config.load_config()
    ├── src.gh_pr_phase_monitor.github_auth.authenticate()
    └── (監視ループ)
        ├── src.gh_pr_phase_monitor.repository_fetcher.fetch_user_repositories()
        ├── src.gh_pr_phase_monitor.pr_fetcher.fetch_open_pull_requests()
        │   └── src.gh_pr_phase_monitor.github_client.fetch_pull_requests()
        ├── (各PRに対して)
        │   ├── src.gh_pr_phase_monitor.phase_detector.detect_phase()
        │   ├── src.gh_pr_phase_monitor.pr_actions.perform_actions_based_on_phase()
        │   │   ├── src.gh_pr_phase_monitor.comment_manager.post_comment()
        │   │   ├── src.gh_pr_phase_monitor.notifier.send_ntfy_notification()
        │   │   └── src.gh_pr_phase_monitor.browser_automation.open_browser_and_click_button() (自動マージ、Issue割り当て時)
        │   └── src.gh_pr_phase_monitor.pr_data_recorder.record_pr_state()
        ├── src.gh_pr_phase_monitor.issue_fetcher.fetch_issues() (PRがLLM workingのみの場合)
        ├── src.gh_pr_phase_monitor.state_tracker.check_for_state_change()
        └── src.gh_pr_phase_monitor.wait_handler.wait_for_next_interval()

---
Generated at: 2026-02-14 07:05:58 JST
