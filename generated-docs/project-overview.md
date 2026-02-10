Last updated: 2026-02-11

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト（PR）を効率的に監視するPythonツールです。
- 認証済みGitHubユーザーのユーザー所有リポジトリを対象に、PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定します。
- GraphQL APIを活用し、フェーズに応じた自動コメント投稿、PRのReady化、モバイル通知、issueの自動割り当てなど多彩なアクションをDry-runモードで安全に実行可能です。

## 技術スタック
- フロントエンド: PyAutoGUI (自動ブラウザ操作), Pillow (画像処理), pygetwindow (ウィンドウ操作), pytesseract (OCRによるテキスト検出) - これらのライブラリは、Web UI上のボタンを識別し、クリックする自動化機能に使用されます。
- 音楽・オーディオ: 該当なし
- 開発ツール: GitHub CLI (GitHub認証およびコマンドライン操作をサポート), gh (GitHub CLIのコマンド)
- テスト: pytest (Pythonアプリケーションのテストフレームワーク)
- ビルドツール: 該当なし
- 言語機能: Python 3.10以上 (主要開発言語), GraphQL API (GitHubから効率的にデータを取得するためのAPIクエリ言語)
- 自動化・CI/CD: ntfy.sh (PRのフェーズが「レビュー待ち」になった際にモバイル端末へ通知を送信するサービス)
- 開発標準: Ruff (Pythonコードのリンティングおよびフォーマッター)

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
- **cat-github-watcher.py**: プロジェクトのメインエントリーポイントとなるスクリプト。このファイルを実行することで、PR監視ツールが起動します。
- **src/gh_pr_phase_monitor/main.py**: 監視ツールのメイン実行ループとロジックをカプセル化しています。`cat-github-watcher.py`から呼び出され、監視処理全体を制御します。
- **src/gh_pr_phase_monitor/colors.py**: ターミナル出力の色付けに使用されるANSIカラーコードと関連ユーティリティを定義しています。
- **src/gh_pr_phase_monitor/config.py**: `config.toml`ファイルから設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供します。
- **src/gh_pr_phase_monitor/github_client.py**: GitHubのGraphQL APIとREST APIの両方との主要な連携を管理します。リポジトリ、PR、Issueなどのデータ取得やアクションの実行を担当します。
- **src/gh_pr_phase_monitor/phase_detector.py**: プルリクエストの現在の状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を判断するロジックを実装しています。
- **src/gh_pr_phase_monitor/comment_manager.py**: プルリクエストへのコメント投稿、既存コメントの確認、コメント内容の管理など、コメント関連の操作を処理します。
- **src/gh_pr_phase_monitor/pr_actions.py**: プルリクエストをReady状態に設定する、特定のPRページをブラウザで開く、自動マージを実行するなど、PRに対する具体的なアクションを定義しています。
- **src/gh_pr_phase_monitor/browser_automation.py**: PyAutoGUIなどを用いてブラウザの自動操作（ボタンクリック、ウィンドウ操作など）を行うための機能を提供します。
- **src/gh_pr_phase_monitor/comment_fetcher.py**: 特定のプルリクエストやIssueに関連するコメントを取得する機能を提供します。
- **src/gh_pr_phase_monitor/display.py**: ターミナルへの情報表示（PRの状態、ログ、サマリーなど）を整形して出力するユーティリティ関数を含みます。
- **src/gh_pr_phase_monitor/github_auth.py**: GitHub CLI (`gh`) を使用したGitHub認証の処理を担当し、APIクライアントが認証済みであることを保証します。
- **src/gh_pr_phase_monitor/graphql_client.py**: GitHubのGraphQL APIに特化したクエリ実行クライアントを提供し、効率的なデータ取得を可能にします。
- **src/gh_pr_phase_monitor/issue_fetcher.py**: GitHubリポジトリからIssueの情報を取得する機能を提供します。
- **src/gh_pr_phase_monitor/monitor.py**: 設定された間隔でGitHubリポジトリとPRの状態を継続的に監視する主要なロジックを管理します。
- **src/gh_pr_phase_monitor/notifier.py**: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
- **src/gh_pr_phase_monitor/pr_data_recorder.py**: 監視対象のプルリクエストの状態履歴や関連データを記録、管理するための機能を提供します。
- **src/gh_pr_phase_monitor/pr_fetcher.py**: GitHubからプルリクエストの情報を取得する機能を提供します。
- **src/gh_pr_phase_monitor/repository_fetcher.py**: 認証済みユーザーが所有するリポジトリの一覧を取得する機能を提供します。
- **src/gh_pr_phase_monitor/state_tracker.py**: 監視対象のPRやリポジトリの現在の状態を追跡し、変更を検出するための機能を提供します。
- **src/gh_pr_phase_monitor/time_utils.py**: 時間間隔のパース、経過時間の計算など、時間に関連するユーティリティ関数を提供します。
- **src/gh_pr_phase_monitor/wait_handler.py**: APIレート制限や省電力モードに応じて、次の監視サイクルまでの待機時間を管理します。
- **config.toml.example**: ユーザーが設定を行うためのサンプル設定ファイルです。`config.toml`としてコピーして使用します。
- **README.ja.md / README.md**: プロジェクトの目的、機能、使い方、設定方法などを説明するドキュメントです。（日本語版と英語版）
- **tests/**: プロジェクトの各モジュールや機能の正しさを検証するためのテストスクリプトが格納されています。
- **screenshots/**: ブラウザ自動化機能で使用する、Web UI上のボタンのスクリーンショット画像が保存されます。
- **.editorconfig**: エディタのコードスタイル（インデント、改行など）を定義し、プロジェクト全体で一貫性を保ちます。
- **.gitignore**: Gitがバージョン管理の対象外とするファイルやディレクトリ（一時ファイル、ログなど）を指定します。
- **LICENSE**: プロジェクトのライセンス情報（MIT License）が記載されています。
- **pytest.ini**: `pytest`フレームワークの設定ファイルです。
- **requirements-automation.txt**: 自動化機能（PyAutoGUIなど）に必要なPythonパッケージをリストアップしています。
- **ruff.toml**: コードリンターおよびフォーマッターである`Ruff`の設定ファイルです。
- **_config.yml**: Jekyll (GitHub Pages) などでドキュメントサイトを生成する際の設定ファイルとして使用されることがあります。
- **docs/**: プロジェクトに関する追加のドキュメントが格納されています。
- **generated-docs/**: AI生成されたドキュメントが保存されるディレクトリです。
- **MERGE_CONFIGURATION_EXAMPLES.md**: 自動マージ機能の設定例に関するドキュメントです。
- **PHASE3_MERGE_IMPLEMENTATION.md**: Phase3マージ機能の実装詳細に関するドキュメントです。
- **STRUCTURE.md**: プロジェクトの全体構造に関するドキュメントです。

## 関数詳細説明
このプロジェクトは単一責任の原則に基づいてモジュール化されており、各モジュール内に特定の役割を持つ関数が実装されています。例えば、`src/gh_pr_phase_monitor/github_client.py`にはGitHub APIと連携してPRやリポジトリのデータを取得する関数群、`src/gh_pr_phase_monitor/phase_detector.py`にはPRのコメントや状態に基づいてフェーズを判定する関数、そして`src/gh_pr_phase_monitor/pr_actions.py`にはPRをReady状態にする、コメントを投稿するなどの具体的なアクションを実行する関数などが存在します。

提供された情報からは、具体的な関数名やそれぞれの詳細な引数、戻り値、機能を一覧として特定することはできませんでした。より詳細な情報については、ソースコードをご参照ください。

## 関数呼び出し階層ツリー
```
提供された情報からは、プロジェクトの具体的な関数呼び出し階層ツリーを生成することはできませんでした。

---
Generated at: 2026-02-11 07:11:29 JST
