Last updated: 2026-02-12

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動実装を行うPull Requestのフェーズを効率的に監視するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIを用いてPRの状態を自動判定し、通知や特定のアクションを実行します。
- Dry-runモード、自動コメント投稿、モバイル通知、Issue自動割り当て機能などを備え、開発ワークフローをサポートします。

## 技術スタック
- フロントエンド: CLIベースのツールであるため、特定のフロントエンド技術は使用していません。
- 音楽・オーディオ: 音楽・オーディオ関連の技術は使用していません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub認証およびリポジトリ操作のCLIツールとして利用されています。
    - **PyAutoGUI**: ブラウザの自動操縦、画面上の画像認識（ボタンの検出とクリック）、ウィンドウ操作に使用されます。
    - **Pillow**: PyAutoGUIの依存ライブラリとして画像処理に利用されます。
    - **pygetwindow**: PyAutoGUIの依存ライブラリとしてウィンドウ操作に利用されます。
    - **pytesseract**: 画像認識が失敗した場合のOCRフォールバックとして、テキスト検出に使用されます。
    - **tesseract-ocr**: pytesseractが利用するOCRエンジン（システムへのインストールが必要）。
- テスト:
    - **pytest**: プロジェクトの各種機能の単体テストおよび統合テストに使用されるPythonのテストフレームワークです。
- ビルドツール: Pythonスクリプトであるため、特別なビルドツールは使用していません。
- 言語機能:
    - **Python 3.10 以上**: プロジェクトの基盤となるプログラミング言語です。
    - **TOML**: 設定ファイル (`config.toml`) の記述形式として採用されています。
    - **GraphQL API**: GitHub APIとの連携において、効率的なデータ取得のために使用されます。
- 自動化・CI/CD:
    - **GitHub Actions**: READMEの自動翻訳など、開発プロセスの自動化に利用されています（プロジェクト本体の動作ではありません）。
    - **ntfy.sh**: Pull Requestのフェーズが「レビュー待ち」になった際のモバイル通知サービスとして活用されます。
- 開発標準:
    - **ruff**: コードのフォーマットとリンティングを自動化し、コード品質と統一性を保つために使用されます。
    - **.editorconfig**: 異なるエディタやIDE間でのコーディングスタイルの一貫性を維持するための設定ファイルです。

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
- `cat-github-watcher.py`: プロジェクトのメインエントリーポイントとなるスクリプトで、監視ツールを起動します。
- `src/gh_pr_phase_monitor/`: プロジェクトの主要なロジックがモジュール化されて格納されているPythonパッケージです。
    - `__init__.py`: Pythonパッケージを定義するための初期化ファイルです。
    - `browser_automation.py`: `PyAutoGUI` を使用して、Webブラウザの操作（ボタンの検出、クリック、ウィンドウの最大化など）を自動化する機能を提供します。
    - `colors.py`: ターミナル出力に色を付けるためのANSIカラーコードと関連ユーティリティを定義しています。
    - `comment_fetcher.py`: GitHubのPull Requestからコメント情報を取得するための機能を提供します。
    - `comment_manager.py`: Pull Requestへのコメント投稿や、既存のコメントの有無を確認するロジックを管理します。
    - `config.py`: `config.toml` ファイルから設定値を読み込み、解析し、アプリケーション全体で利用可能にする機能です。
    - `display.py`: コンソールに監視状況やPRの状態、Issueリストなどを分かりやすく表示するための出力ロジックを扱います。
    - `github_auth.py`: GitHub CLI (`gh`) を利用してGitHubへの認証を行うための機能を提供します。
    - `github_client.py`: GitHub REST APIと連携し、汎用的なGitHub操作を行うためのクライアントです。
    - `graphql_client.py`: GitHub GraphQL APIを介して、Pull Requestやリポジトリの詳細情報を効率的に取得するためのクライアントです。
    - `issue_fetcher.py`: GitHubリポジトリからIssue情報を取得し、表示・割り当て候補を決定する機能です。
    - `main.py`: 監視ツールの中核となる実行ループを管理し、他のモジュールを協調させてPR監視、フェーズ判定、アクション実行を行います。
    - `monitor.py`: Pull Requestの監視サイクルを管理し、設定された間隔で定期的にGitHubの状態をチェックします。
    - `notifier.py`: ntfy.shサービスを利用して、特定のイベント（例: PRがレビュー待ちになった場合）をモバイルデバイスに通知する機能を提供します。
    - `phase_detector.py`: Pull Requestの現在のフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を判定するロジックを実装しています。
    - `pr_actions.py`: Pull Requestに対する具体的なアクション（Draft PRのReady化、ブラウザでのPRページ起動、自動マージなど）を実行する機能を提供します。
    - `pr_data_recorder.py`: 各Pull Requestの状態変化や詳細情報を記録し、追跡するための機能です。
    - `pr_fetcher.py`: GitHubからPull Requestのリストと詳細情報を取得する機能です。
    - `repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリの情報を取得する機能です。
    - `state_tracker.py`: 監視ツールの全体的な状態（例: 連続して状態変化がない時間、現在の監視間隔など）を管理し、省電力モードへの切り替えなどを制御します。
    - `time_utils.py`: 時間に関するユーティリティ関数（例: 時間文字列のパース）を提供します。
    - `wait_handler.py`: プロセス間やAPIリクエスト間の待機時間を管理する機能です。
- `config.toml.example`: ユーザーが設定を行う際のテンプレートとなるTOML形式の設定ファイルです。
- `requirements-automation.txt`: 自動化機能（PyAutoGUIなど）に必要なPythonライブラリをリストアップしています。
- `ruff.toml`: Pythonコードのリンティングとフォーマットを管理する`ruff`ツールの設定ファイルです。
- `screenshots/`: ブラウザ自動化機能 (`PyAutoGUI`) がボタンを認識するために使用する、事前に撮影されたボタンのスクリーンショット画像が格納されます。
- `tests/`: プロジェクトのテストコードを格納するディレクトリで、`pytest`を使用して実行されます。
- `.editorconfig`: 異なる開発環境間でのコーディングスタイル（インデント、改行コードなど）を統一するための設定ファイルです。
- `.gitignore`: Gitがバージョン管理の対象から除外するファイルやディレクトリを指定するファイルです。
- `.vscode/settings.json`: Visual Studio Codeエディタのプロジェクト固有の設定が記述されています。
- `LICENSE`: プロジェクトがMITライセンスであることを示すファイルです。
- `MERGE_CONFIGURATION_EXAMPLES.md`: PRの自動マージ機能に関する設定例をまとめたドキュメントです。
- `PHASE3_MERGE_IMPLEMENTATION.md`: Phase3でのPR自動マージ機能の実装に関する詳細な説明ドキュメントです。
- `README.ja.md`: プロジェクトの日本語版説明書です。
- `README.md`: プロジェクトの英語版説明書です。
- `STRUCTURE.md`: プロジェクトのディレクトリ構成やモジュール間の関係について説明したドキュメントです。
- `_config.yml`: 一般的にGitHub Pagesなどの静的サイトジェネレータの設定に使用されるファイルですが、このプロジェクトでの具体的な使途は不明です。
- `demo_automation.py`: 自動化機能の動作を確認するためのデモンストレーション用スクリプトである可能性があります。
- `docs/`: プロジェクトの追加ドキュメントを格納するディレクトリです。
    - `RULESETS.md`: 監視ルールセットの設定方法について説明するドキュメントです。
    - `button-detection-improvements.ja.md`: ボタン検出機能の改善に関する日本語ドキュメントです。
    - `window-activation-feature.md`: ウィンドウアクティベーション機能に関するドキュメントです。
- `generated-docs/`: AIなどによって自動生成されたドキュメントを格納するディレクトリです。
- `pytest.ini`: pytestテストフレームワークの実行設定ファイルです。

## 関数詳細説明
提供されたプロジェクト情報には、各関数の具体的な名称、引数、戻り値、機能についての詳細が含まれていません。そのため、個々の関数の詳細な説明は生成できません。

## 関数呼び出し階層ツリー
```
提供されたプロジェクト情報からは、関数呼び出し階層ツリーを生成できませんでした。

---
Generated at: 2026-02-12 07:05:29 JST
