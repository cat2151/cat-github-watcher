Last updated: 2026-02-05

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動実装を行うPull Requestのフェーズを監視するPythonツールです。
- 認証済みGitHubユーザーの全所有リポジトリを対象に、PRの状態変化に応じた通知や自動アクションを実行します。
- GraphQL APIとブラウザ自動化を活用し、PRのDraft/レビュー中/レビュー待ちなどを効率的に検知・制御します。

## 技術スタック
- フロントエンド: (直接的なGUIフレームワークは使用せず、既存のGitHub Web UIをブラウザ自動化で操作します)
- 音楽・オーディオ: (該当なし)
- 開発ツール:
    - GitHub CLI (`gh`): GitHubへの認証とCLI操作を提供します。
    - .vscode/settings.json: Visual Studio Codeのワークスペース設定を定義します。
- テスト:
    - pytest: Pythonの単体・結合テストフレームワークとして使用されます。
- ビルドツール:
    - Python 3.x: プロジェクトの主要な実行環境であり、インタプリタです。
- 言語機能:
    - Python: プロジェクトの主要開発言語です。
- 自動化・CI/CD:
    - PyAutoGUI: GUI自動化ツールで、マウス・キーボード操作やスクリーンショットベースの画像認識を行います。
    - pygetwindow: PyAutoGUIの依存関係として、ウィンドウ管理機能を提供します。
    - pytesseract: 画像内のテキスト認識 (OCR) のためのPythonラッパーです。
    - Tesseract-OCR: OCRエンジンの本体で、システムレベルでインストールされます。
    - GitHub Actions: READMEの自動翻訳など、プロジェクトのCI/CDプロセスの一部で使用されます。
- 開発標準:
    - ruff: Pythonコードのリンティングとフォーマットに使用されるツールです。
    - .editorconfig: エディタ設定の統一を支援し、一貫したコーディングスタイルを保ちます。
- API連携・通知:
    - GraphQL API: GitHub APIとの効率的なデータ連携に利用されます。
    - ntfy.sh: モバイル端末への通知サービスとして活用されます。
- 設定管理:
    - TOML: 設定ファイル (`config.toml`) の記述形式として採用されています。
- 画像処理:
    - Pillow: Python Imaging Library (PIL) のフォークであり、PyAutoGUIの画像処理機能をサポートします。

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
- `cat-github-watcher.py`: プロジェクトのエントリーポイントとなるスクリプトで、監視ツールを起動します。
- `config.toml.example`: ユーザーが設定ファイルを作成する際のテンプレートとして提供される、設定例ファイルです。
- `src/gh_pr_phase_monitor/__init__.py`: Pythonパッケージとして `gh_pr_phase_monitor` ディレクトリを認識させるための初期化ファイルです。
- `src/gh_pr_phase_monitor/browser_automation.py`: Webブラウザを自動操作し、GitHubのUI要素（ボタンなど）をクリックする機能を提供します。PyAutoGUIやOCRを利用した画像認識を行います。
- `src/gh_pr_phase_monitor/colors.py`: ターミナル出力を見やすくするため、ANSIカラーコードを定義し、文字列に色を付けるユーティリティ関数を提供します。
- `src/gh_pr_phase_monitor/comment_fetcher.py`: GitHubのPull Requestからコメント情報を取得するためのロジックを実装しています。
- `src/gh_pr_phase_monitor/comment_manager.py`: Pull Requestへのコメント投稿や、特定のコメントの有無を確認する機能など、コメント関連の操作を管理します。
- `src/gh_pr_phase_monitor/config.py`: `config.toml` ファイルの読み込み、パース、そして設定値のバリデーションを行う責任を負います。
- `src/gh_pr_phase_monitor/display.py`: 監視結果やステータス情報をコンソールに表示するための関数群を提供し、ユーザーへの情報提示を担います。
- `src/gh_pr_phase_monitor/github_auth.py`: GitHub CLI (`gh`) を利用してGitHubへの認証を行い、認証情報を管理する機能を提供します。
- `src/gh_pr_phase_monitor/github_client.py`: GitHubのREST APIとのやり取りを抽象化し、一般的なAPI操作を簡易化するクライアントです。
- `src/gh_pr_phase_monitor/graphql_client.py`: GitHubのGraphQL APIに特化したクライアントで、効率的なデータ取得クエリを実行します。
- `src/gh_pr_phase_monitor/issue_fetcher.py`: GitHubのリポジトリからIssue情報を取得し、特に「good first issue」や古いIssueを識別する機能を提供します。
- `src/gh_pr_phase_monitor/main.py`: メインの実行ループと監視ロジックをオーケストレートし、各モジュール間の連携を調整します。
- `src/gh_pr_phase_monitor/monitor.py`: 一定間隔でGitHubリポジトリとPull Requestの状態を定期的に監視する中核的なロジックを実装しています。
- `src/gh_pr_phase_monitor/notifier.py`: `ntfy.sh` サービスを利用して、特定のイベント発生時にモバイル端末へ通知を送信する機能を提供します。
- `src/gh_pr_phase_monitor/phase_detector.py`: Pull Requestがどの開発フェーズ（Draft状態、レビュー指摘対応中、レビュー待ち、LLM working）にあるかを判定するロジックを実装しています。
- `src/gh_pr_phase_monitor/pr_actions.py`: PRをReady状態にする、コメントを投稿する、ブラウザでPRページを開くなど、具体的なPR操作を実行する機能を提供します。
- `src/gh_pr_phase_monitor/pr_fetcher.py`: オープン状態のPull Request情報をGitHubから取得する役割を担います。
- `src/gh_pr_phase_monitor/repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリの一覧を取得する機能を提供します。
- `src/gh_pr_phase_monitor/state_tracker.py`: 各Pull Requestやリポジトリの現在の状態を追跡し、状態変化に応じて省電力モードへの移行などを管理します。
- `src/gh_pr_phase_monitor/time_utils.py`: 時間間隔のパース、経過時間の計算、タイムアウト処理など、時間関連のユーティリティ関数を提供します。
- `src/gh_pr_phase_monitor/wait_handler.py`: APIレート制限や省電力モード時など、プログラムが待機する必要がある状況での待機処理を管理します。
- `tests/`: プロジェクトの各機能の正確性を検証するためのpytestテストスイートが格納されています。
- `screenshots/`: ブラウザ自動化機能がWeb上のボタンを識別するために使用する、ボタンのスクリーンショット画像が格納されます。
- `requirements-automation.txt`: ブラウザ自動化など、特定の機能で必要となるPythonパッケージの依存関係リストです。
- `pytest.ini`: pytestテストフレームワークの挙動を設定するためのファイルです。
- `ruff.toml`: コードの品質とスタイルを維持するための、Pythonリンター/フォーマッター`ruff`の設定ファイルです。

## 関数詳細説明
本ツールは単一責任の原則に基づき、各モジュールが特定の機能を提供するように設計されています。具体的な関数シグネチャは多岐にわたりますが、ここでは主要な機能を提供する関数群について、その役割を概説します。

- **監視ループ関連関数群 (`monitor.py` など)**
    - **役割**: GitHubリポジトリとPRを定期的に監視し、状態の変化を検知するメインの監視処理を実行します。
    - **機能**: GitHub APIからのデータ取得をスケジューリングし、`phase_detector`や`pr_actions`モジュールと連携してPRの状態に応じた処理をトリガーします。
- **フェーズ判定関数群 (`phase_detector.py`)**
    - **役割**: Pull Requestがどのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM working）にあるかを判定します。
    - **機能**: PRのステータス、ラベル、レビューコメントの内容などを分析し、定義されたフェーズに分類します。
- **アクション実行関数群 (`pr_actions.py`)**
    - **役割**: PRの状態変化に応じて、具体的なアクション（例: DraftをReadyにする、コメントを投稿する、通知を送信する、ブラウザを開く）を実行します。
    - **機能**: `github_client`や`browser_automation`モジュールと連携し、GitHub上での操作や外部サービスへの通知を行います。
- **ブラウザ自動操作関数群 (`browser_automation.py`)**
    - **役割**: Webブラウザを自動操作して特定のGitHubページでボタンをクリックするなどのGUI操作を行います。
    - **機能**: PyAutoGUIとTesseract-OCRを利用して画面上の要素を識別し、マージ、Issue割り当てなどのアクションを実行します。
- **設定読み込み・解析関数群 (`config.py`)**
    - **役割**: 外部設定ファイル (`config.toml`) を読み込み、設定値を検証してアプリケーション全体で利用可能な形式に変換します。
    - **機能**: TOML形式の解析、データ型の変換、デフォルト値の適用、設定の有効性チェックなどを行います。

## 関数呼び出し階層ツリー
```
cat-github-watcher.py (エントリポイント)
└── src/gh_pr_phase_monitor/main.py (メイン実行ループ)
    └── src/gh_pr_phase_monitor/monitor.py (メイン監視ループ)
        ├── src/gh_pr_phase_monitor/repository_fetcher.py (ユーザーリポジトリ取得)
        ├── src/gh_pr_phase_monitor/pr_fetcher.py (オープンPR取得)
        ├── src/gh_pr_phase_monitor/state_tracker.py (監視状態の追跡)
        └── (各PRに対して)
            ├── src/gh_pr_phase_monitor/phase_detector.py (PRフェーズ判定)
            └── src/gh_pr_phase_monitor/pr_actions.py (PRアクション実行)
                ├── src/gh_pr_phase_monitor/comment_manager.py (コメント投稿/確認)
                │   └── src/gh_pr_phase_monitor/github_client.py (GitHub REST API連携)
                ├── src/gh_pr_phase_monitor/notifier.py (ntfy.sh通知送信)
                ├── src/gh_pr_phase_monitor/browser_automation.py (ブラウザ自動操作)
                │   └── (PyAutoGUI, pytesseract/Tesseract-OCRを利用)
                └── src/gh_pr_phase_monitor/issue_fetcher.py (Issue情報取得/割り当て関連)

---
Generated at: 2026-02-05 07:02:50 JST
