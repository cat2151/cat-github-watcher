Last updated: 2026-03-03

# Development Status

## 現在のIssues
-   [Issue #308](../issue-notes/308.md) は `src/gh_pr_phase_monitor/main.py` が500行を超過しており、リファクタリングによる機能分割とテストの実施が推奨されています。
-   [Issue #307](../issue-notes/307.md) および [Issue #304](../issue-notes/304.md) は、起動時の自己アップデートチェックが遅延するため、アプリケーション起動直後に別スレッドで実行する改善が求められています。
-   直近ではGraphQL APIの利用状況表示、レートリミットによる動的インターバル延長、およびバックグラウンドでのpullable検索最適化に関する機能が追加されました。

## 次の一手候補
1.  [Issue #308](../issue-notes/308.md): `src/gh_pr_phase_monitor/main.py` の機能分割とリファクタリング計画
    -   最初の小さな一歩: `main.py` の現在の機能ブロックを特定し、それぞれの責任範囲を文書化する。
    -   Agent実行プロンプ:
      ```
      対象ファイル: `src/gh_pr_phase_monitor/main.py`

      実行内容: `main.py` の主要な機能ブロック（例: 設定読み込み、PRフェッチ、フェーズ判定、アクション実行、レートリミット処理、サマリー表示、アップデート処理、エラーハンドリング、待機処理など）を洗い出し、それぞれの機能の役割と依存関係を分析してMarkdown形式で出力してください。将来的に別のファイルに分割することを視野に入れ、分割候補となる機能とその理由も記述してください。

      確認事項: ファイル全体のロジックフロー、既存の関数やクラスの境界、設定（config）の利用箇所、外部モジュールとの連携を確認してください。

      期待する出力: `main.py` の機能ブロックとその責任範囲、依存関係、および分割候補となる機能とその理由をまとめたMarkdownレポート。
      ```

2.  [Issue #307](../issue-notes/307.md), [Issue #304](../issue-notes/304.md): 起動時の自己アップデートチェックの別スレッド化
    -   最初の小さな一歩: `src/gh_pr_phase_monitor/auto_updater.py` に `main.py` から呼び出せるようにスレッドを開始する新しい関数を実装する。
    -   Agent実行プロンプト:
      ```
      対象ファイル: `src/gh_pr_phase_monitor/auto_updater.py`, `src/gh_pr_phase_monitor/main.py`

      実行内容:
      1. `src/gh_pr_phase_monitor/auto_updater.py` に `start_startup_self_update_check()` 関数を追加してください。この関数は、`maybe_self_update()` をデーモンスレッドで一度だけ実行し、例外を補足してログ出力（print）するロジックを含みます。
      2. `src/gh_pr_phase_monitor/main.py` にて、メインループ開始前、かつシグナルハンドラ設定後に、追加した `start_startup_self_update_check()` を呼び出すように修正してください。

      確認事項:
      * `auto_updater.py` の `maybe_self_update` がスレッドセーフに呼び出せること。
      * `main.py` の既存の `maybe_self_update()` 呼び出し（メインループ内）との競合がないこと。
      * スレッド起動時のエラーがアプリケーション全体をクラッシュさせないこと。

      期待する出力: `auto_updater.py` と `main.py` の修正後のコードと、変更点の簡単な説明。
      ```

3.  [Issue #308](../issue-notes/308.md): `main.py` リファクタリングに伴うテストカバレッジの確認と追加
    -   最初の小さな一歩: `src/gh_pr_phase_monitor/main.py` に関連する既存のテストファイル (`tests/test_*.py` の中で `main.py` の機能に関連するもの) を特定し、現在のテストカバレッジの現状を把握する。
    -   Agent実行プロンプト:
      ```
      対象ファイル: `src/gh_pr_phase_monitor/main.py` および `tests/` ディレクトリ内の関連テストファイル

      実行内容:
      1. `src/gh_pr_phase_monitor/main.py` の主要な機能（例えば、`_format_rate_limit_reset`, `_check_rate_limit_throttle`, `log_error_to_file`、`main` 関数内の各フェーズ処理の呼び出しなど）について、現在のテストカバレッジがどの程度か調査してください。
      2. もしテストカバレッジが低い、または特定の重要なロジックがテストされていない場合、不足しているテストシナリオを特定し、追加すべきテストケースの概要を提案してください。

      確認事項:
      * `pytest.ini` や `requirements-automation.txt` などのテスト環境設定。
      * `tests/` ディレクトリ内の既存のテストファイルの命名規則と構成。
      * `main.py` が依存する他のモジュール（例: `config.py`, `github_client.py`）のテスト状況は、このタスクの範囲外とします。

      期待する出力: `main.py` のテストカバレッジ現状の分析結果と、不足しているテストケースの概要（ファイル名、テスト関数名、テスト対象機能の説明）をまとめたMarkdownレポート。

---
Generated at: 2026-03-03 07:04:46 JST
