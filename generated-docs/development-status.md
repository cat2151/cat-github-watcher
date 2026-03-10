Last updated: 2026-03-11

# Development Status

## 現在のIssues
- [Issue #414](../issue-notes/414.md) は、`local_repo_watcher.py`とそのテストファイルが500行を超えており、リファクタリングによるコード品質改善が求められています。
- [Issue #413](../issue-notes/413.md) は、設定されたRustリポジトリに対して`git pull`後に`cargo install --force`を自動実行する機能の実装を進めています。
- [Issue #412](../issue-notes/412.md) は、`cargo install`を利用するリポジトリで`git pull`だけでは最新にならないUX上の課題を指摘しており、[Issue #413](../issue-notes/413.md)がその解決策を提示しています。

## 次の一手候補
1. [Issue #414](../issue-notes/414.md): `local_repo_watcher.py`の巨大ファイルのリファクタリング計画
   - 最初の小さな一歩: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`と`tests/test_local_repo_watcher.py`の現状の機能と依存関係を詳細に分析し、リファクタリングが必要な具体的なセクションや関数を特定する。特に、テストのカバレッジを維持しつつ、どのように分割・抽象化できるかの初期案を検討する。
   - Agent実行プロンプト:
     ```
     対象ファイル: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`, `tests/test_local_repo_watcher.py`

     実行内容: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`の現在のコードベース（543行）と、関連するテストファイル`tests/test_local_repo_watcher.py`（524行）について、リファクタリングの計画を提案してください。特に以下の点を考慮してください：
     1. 役割が明確に分かれている関数やクラスの特定。
     2. テストの変更を最小限に抑えつつ、コードをモジュール化するための戦略。
     3. 行数を減らすための具体的なリファクタリング候補（例: 共通ユーティリティ関数の抽出、データ構造の改善）。
     4. リファクタリング後のファイル構造の提案。

     確認事項:
     - `_run_git`関数など、外部コマンド実行に依存する部分の副作用の扱いに注意してください。
     - スレッド処理 (`_background_startup_check`, `_background_single_repo_check`) の変更が並行処理の安全性に影響しないことを確認してください。
     - 既存のテストがリファクタリング後も引き続き機能することを前提としてください。

     期待する出力: `local_repo_watcher.py`のリファクタリング計画をMarkdown形式で出力してください。計画には、リファクタリング対象の具体的なコードブロック、提案される変更内容、および新しいファイル構成の概要を含めてください。
     ```

2. [Issue #413](../issue-notes/413.md): Rustリポジトリの`cargo install --force`自動実行機能のための設定追加
   - 最初の小さな一歩: 既存の`local_repo_watcher.py`に関連する設定ファイルに`cargo_install_repos`設定オプションを追加し、指定されたリポジトリのパスを管理する基本的なメカニズムを実装する。
   - Agent実行プロンプト:
     ```
     対象ファイル: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`, `src/gh_pr_phase_monitor/core/config.py`, `config.toml.example`

     実行内容:
     1. `src/gh_pr_phase_monitor/core/config.py`に新しい設定オプション`cargo_install_repos` (リスト型) を追加してください。デフォルト値は空のリストとしてください。
     2. `config.toml.example`に`cargo_install_repos = []`の記述を追加し、この設定の目的を説明する簡単なコメントを加えてください。
     3. `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`内で、`check_local_repos`関数およびバックグラウンドチェック関数（`_background_startup_check`, `_background_single_repo_check`）がこの`cargo_install_repos`設定を読み込み、処理に利用できるように準備してください。具体的には、設定を引数として受け取るか、グローバルにアクセスできるように、設定の読み込みフローを調整してください。

     確認事項:
     - 設定の読み込みが正しく行われ、`local_repo_watcher.py`の関連関数で利用可能になること。
     - `cargo_install_repos`リストに含まれるリポジトリのみが`cargo install`の対象となるように、後のステップで条件分岐を容易に実装できるような準備をすること。
     - 既存のコンフィグレーション読み込みロジックとの整合性を維持すること。

     期待する出力: 変更されたコードスニペット（`config.py`の新しい設定定義、`config.toml.example`の追加エントリ、`local_repo_watcher.py`での設定利用準備に関する部分）と、新しい設定オプションの動作説明を含むMarkdown形式の文書。
     ```

3. [Issue #413](../issue-notes/413.md): `cargo install`実行と多行エラーの要約機能の実装
   - 最初の小さな一歩: `local_repo_watcher.py`内に、`cargo install --force --path <path>`コマンドを実行するための汎用ヘルパー関数`_run_cargo`と、個別のインストール関数`_run_cargo_install`を定義する。
   - Agent実行プロンプト:
     ```
     対象ファイル: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`

     実行内容:
     1. `_run_git`関数を参考に、`src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`に`_run_cargo(args: list[str], cwd: str) -> tuple[int, str, str]`関数を新しく追加してください。これは`cargo`コマンドを実行するための汎用ヘルパー関数であり、`git`コマンドと同様に`capture_output`や`timeout`、`encoding`を適切に処理するものとします。
     2. その後、この`_run_cargo`関数を利用して、`_run_cargo_install(path: str) -> tuple[bool, str]`関数を実装してください。この関数は、指定されたパスのリポジトリに対して`cargo install --force --path <path>`を実行し、成功した場合は`True, "インストール成功"`、失敗した場合は`False, エラーメッセージ`を返します。エラーメッセージは、後で`_summarize_cargo_error()`で正規化される前の生のエラー出力を含んでください。
     3. これらの関数を`local_repo_watcher.py`内の適切な位置に配置し、呼び出し元からのアクセスを考慮してください。

     確認事項:
     - `_run_cargo`関数が`_run_git`と同様にタイムアウト処理やエンコーディングを適切に扱うこと。
     - `_run_cargo_install`が`--force`オプションを正しく使用し、`path`引数を`--path`オプションとして渡すこと。
     - `cargo`コマンド実行時に発生する可能性のある標準出力および標準エラー出力を適切にキャプチャし、エラー発生時にその詳細を返すこと。

     期待する出力: 変更された`local_repo_watcher.py`の該当コードスニペット（`_run_cargo`, `_run_cargo_install`の定義）と、これらの関数の利用方法、およびそれぞれの関数の役割と引数、戻り値の説明を含むMarkdown形式の文書。
     ```

---
Generated at: 2026-03-11 07:03:02 JST
