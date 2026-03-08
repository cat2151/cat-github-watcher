Last updated: 2026-03-09

# Development Status

## 現在のIssues
- [Issue #406](../issue-notes/406.md) は、`src/gh_pr_phase_monitor/main.py` が500行を超過しているため、リファクタリングを推奨しています。
- このファイルはPRのHTML取得、Phase判定、処理、レートリミット制御、各種監視機能のオーケストレーションなど、多岐にわたる主要ロジックを内包しています。
- リファクタリングは単一責任の原則に基づき、関連機能を分離することでコード品質を向上させ、変更容易性を高めることを目的とします。

## 次の一手候補
1. [Issue #406](../issue-notes/406.md): `_process_open_prs` 関数を独立したモジュールに切り出す
   - 最初の小さな一歩: `src/gh_pr_phase_monitor/processor/pr_processor.py` を新規作成し、`main.py` 内の `_process_open_prs` 関数とその関連インポートを移動する。その後、`main.py` から新モジュールの関数を呼び出すように変更する。
   - Agent実行プロンプト:
     ```
     対象ファイル:
     - src/gh_pr_phase_monitor/main.py
     - src/gh_pr_phase_monitor/processor/pr_processor.py (新規作成)
     - src/gh_pr_phase_monitor/processor/__init__.py (新規作成)

     実行内容:
     1. `src/gh_pr_phase_monitor/processor` ディレクトリと `__init__.py` を作成する。
     2. `src/gh_pr_phase_monitor/processor/pr_processor.py` を新規作成し、`main.py` 内の `_process_open_prs` 関数をこのファイルに移動する。
     3. `_process_open_prs` 関数が依存する `fetch_and_analyze_pr_html`, `determine_phase`, `process_pr`, `PHASE_3`, `PHASE_LLM_WORKING`, `is_llm_working`, `log_error_to_file` などのインポートを `pr_processor.py` に適切に追加する。
     4. `main.py` から移動した `_process_open_prs` の呼び出し箇所を、新モジュールの関数呼び出しに変更する（例: `pr_processor.process_open_prs(...)`）。
     5. `main.py` から不要になったインポートを削除し、新モジュールへのインポートを追加する。

     確認事項:
     - `_process_open_prs` 関数の移動後も、PRのHTML取得、phase判定、PR処理が正しく行われることを確認する。
     - `phase3_repo_names` のリストが正しく更新されることを確認する。
     - テストコード `tests/` ディレクトリ内のファイル群 (特に `tests/test_phase_detection_real_prs.py` や `tests/test_html_status_processor.py` など、PR処理に関連するテスト) が引き続きパスすることを確認する。

     期待する出力:
     - `src/gh_pr_phase_monitor/processor/pr_processor.py` の新規ファイルの内容。
     - `src/gh_pr_phase_monitor/main.py` の変更された内容。
     - 上記変更により、`main.py` の行数が減少すること。
     ```

2. [Issue #406](../issue-notes/406.md): `log_error_to_file` 関数を共通ユーティリティに切り出す
   - 最初の小さな一歩: `src/gh_pr_phase_monitor/core/error_logger.py` ファイルを新規作成し、`main.py` 内の `log_error_to_file` 関数とその関連インポートを移動する。
   - Agent実行プロンプト:
     ```
     対象ファイル:
     - src/gh_pr_phase_monitor/main.py
     - src/gh_pr_phase_monitor/core/error_logger.py (新規作成)

     実行内容:
     1. `src/gh_pr_phase_monitor/core/error_logger.py` を新規作成し、`main.py` 内の `log_error_to_file` 関数をこのファイルに移動する。
     2. `log_error_to_file` 関数が依存する `datetime`, `UTC`, `Path`, `traceback` などのインポートを `error_logger.py` に適切に追加する。
     3. `main.py` 内の `LOG_DIR` 定数を `error_logger.py` に移動し、`main.py` からは `error_logger` モジュールから利用するように変更する。
     4. `main.py` 内の `log_error_to_file` の呼び出し箇所を、新モジュールの関数呼び出しに変更する（例: `error_logger.log_error_to_file(...)`）。
     5. `main.py` から不要になったインポートを削除し、新モジュールへのインポートを追加する。

     確認事項:
     - エラーが発生した際に `logs/error.log` に正しくログが記録されることを確認する。
     - エラーロギングがメインループの実行を妨げないことを確認する。

     期待する出力:
     - `src/gh_pr_phase_monitor/core/error_logger.py` の新規ファイルの内容。
     - `src/gh_pr_phase_monitor/main.py` の変更された内容。
     - 上記変更により、`main.py` の行数が減少すること。
     ```

3. [Issue #406](../issue-notes/406.md): メイン監視ループのインターバル管理ロジックを整理する
   - 最初の小さな一歩: `main` 関数内のレートリミットによるスロットリング、PR状態変化による頻度低下、および設定ホットリロードが適用されるインターバル決定ロジックを `src/gh_pr_phase_monitor/core/interval_manager.py` に切り出す。
   - Agent実行プロンプト:
     ```
     対象ファイル:
     - src/gh_pr_phase_monitor/main.py
     - src/gh_pr_phase_monitor/core/interval_manager.py (新規作成)

     実行内容:
     1. `src/gh_pr_phase_monitor/core/interval_manager.py` を新規作成する。
     2. `main.py` 内の以下のロジックを `interval_manager.py` 内の新しい関数（例: `determine_current_interval` および `update_normal_interval_on_reload`）に移動する:
        - `_check_rate_limit_throttle` の呼び出しと `should_throttle`, `throttled_interval` の決定部分。
        - `check_no_state_change_timeout` の呼び出しと `use_reduced_frequency` の決定部分。
        - `use_reduced_frequency` と `should_throttle` に基づいて `current_interval_seconds` と `current_interval_str` を決定するロジック。
        - `config_reloaded` 時の `normal_interval_seconds` と `normal_interval_str` の更新ロジック。
     3. 新しい関数は `config`, `before_rate_limit`, `after_rate_limit`, `normal_interval_seconds`, `normal_interval_str`, `all_prs` などを引数として受け取るように設計する。
     4. `main.py` 内の該当箇所から、新モジュールの関数を呼び出すように変更する。
     5. `main.py` から不要になったインポートを削除し、新モジュールへのインポートを追加する。

     確認事項:
     - インターバルが、レートリミット、PR状態変化、設定変更に応じて正しく調整されることを確認する。
     - `tests/test_interval_parsing.py` や `tests/test_rate_limit_throttle.py`, `tests/test_no_change_timeout.py` など、関連するテストが引き続きパスすることを確認する。

     期待する出力:
     - `src/gh_pr_phase_monitor/core/interval_manager.py` の新規ファイルの内容。
     - `src/gh_pr_phase_monitor/main.py` の変更された内容。
     - 上記変更により、`main.py` の行数が減少すること。

---
Generated at: 2026-03-09 07:01:40 JST
