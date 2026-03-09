Last updated: 2026-03-10

# Development Status

## 現在のIssues
- [Issue #411](../issue-notes/411.md) と [Issue #410](../issue-notes/410.md) は、PRクローズ後にリポジトリの自動pullが実行されないという共通の問題を指摘しています。
- この問題は、`src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` 内の `notify_phase3_detected` が、PRがクローズされてオープンPR数が0になった際に適切にリポジトリの状態更新をトリガーできていないことに起因している可能性があります。
- 具体的には、`phase3A` 後のPRクローズ時に`notify_phase3_detected`が呼ばれないか、`_repo_states`の状態管理によって意図せずスキップされている疑いがあります。

## 次の一手候補
1. [Issue #411](../issue-notes/411.md) の問題再現テストのスケルトン作成
   - 最初の小さな一歩: `tests/` ディレクトリ配下に、Issue #411 で説明されているシナリオ（phase3A後PRクローズ時にauto pullが実行されない）を再現する単体テストまたは結合テストのスケルトンを作成します。
   - Agent実行プロンプト:
     ```
     対象ファイル: `tests/test_local_repo_watcher_phase3_pull.py` (新規作成)

     実行内容: `local_repo_watcher.py` の `notify_phase3_detected` が正しく機能しないシナリオを検証するテストファイルのスケルトンを作成してください。具体的には、
     1. モックを使ってGitHub PRの状態をシミュレートし、`phase3A` に移行したと仮定する。
     2. その後PRがクローズされたと仮定し、`notify_phase3_detected` が呼ばれる状況をシミュレートする。
     3. `notify_phase3_detected` が `local_repo_watcher.py` 内の`_check_repo` や `_accumulate_result` を正しくトリガーするか（またはその意図しないスキップが発生するか）を検証するテスト関数を追加する。
     テストファイルには最小限の構造（import、テストクラス、テストメソッドの定義）を含めてください。

     確認事項: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` の現在の実装、特に`_repo_states` の利用方法と`notify_phase3_detected`のロジックを把握してください。また、既存のテストファイル（`tests/test_local_repo_watcher.py`など）を参考に、モックやテストヘルパーの適切な利用方法を確認してください。

     期待する出力: `tests/test_local_repo_watcher_phase3_pull.py` という新しいファイル名で、上記実行内容を満たすPythonテストコードのスケルトンを生成してください。
     ```

2. [Issue #411](../issue-notes/411.md) の `notify_phase3_detected` ロジック修正検討
   - 最初の小さな一歩: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` の `notify_phase3_detected` 関数において、`_repo_states` の状態遷移ロジックを見直し、PRクローズ後にリポジトリの再チェックが必ずトリガーされるように修正の必要箇所を特定し、コメントアウトでその意図を記述します。
   - Agent実行プロンプト:
     ```
     対象ファイル: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`

     実行内容: `notify_phase3_detected` 関数内の`_repo_states` の状態管理ロジックを分析し、PRがクローズされた後にリポジトリの状態が `REPO_STATE_NEEDS_CHECK` に確実に遷移するか、あるいは直接 `REPO_STATE_CHECKING` に移行するかどうかを検証するための修正案をコメントで追記してください。具体的には、以下の行の変更可能性を検討し、コメントで提案を記述してください。
         ```python
         if current_state in (REPO_STATE_STARTUP_CHECKING, REPO_STATE_NEEDS_CHECK, REPO_STATE_CHECKING, REPO_STATE_DONE):
             return  # 既に検査済み・検査中または待機中
         ```
     このreturn文を削除した場合の影響や、特定の条件（例: `current_state == REPO_STATE_DONE`の場合のみ再チェックを許可するなど）を追加する可能性をコメントで示してください。

     確認事項: `notify_phase3_detected`がどのようなライフサイクルで呼び出されるか、また`_repo_states`が全体でどのように利用されているかを理解してください。特に、PRクローズ後に再度pullableチェックが必要になる要件を満たすことを重視してください。

     期待する出力: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` の更新された内容。変更箇所には具体的なコード修正案と、その理由を説明するコメントを含めてください。
     ```

3. [Issue #411](../issue-notes/411.md) の `_repos_awaiting_post_phase3_check` 導入と追跡ロジックの初期実装
   - 最初の小さな一歩: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` に `_repos_awaiting_post_phase3_check: Set[str]` を追加し、`notify_phase3_detected` が呼ばれた際に該当リポジトリ名をこのセットに追加する初期実装を行います。
   - Agent実行プロンプト:
     ```
     対象ファイル: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py`

     実行内容:
     1. モジュールレベル変数として `_repos_awaiting_post_phase3_check: Set[str]` を `threading.Lock` の直後あたりに追加してください。
     2. `notify_phase3_detected` 関数内で、PRが `phase3` に移行したと検知された際に、`_repo_states` を更新する前に、`_repos_awaiting_post_phase3_check` に該当するリポジトリ名を追加するロジックを `_state_lock` のスコープ内で実装してください。
     3. このセットへの追加は、PRクローズ後の自動pullを保証するための追跡メカニズムの第一歩であることを示すコメントを追加してください。

     確認事項: `_state_lock` の適切な利用法を確認し、スレッドセーフティを確保してください。また、`notify_phase3_detected` の既存のロジックに影響を与えないよう注意してください。

     期待する出力: `src/gh_pr_phase_monitor/monitor/local_repo_watcher.py` の更新された内容。`_repos_awaiting_post_phase3_check` の定義と、`notify_phase3_detected` 内でのその利用例を含めてください。

---
Generated at: 2026-03-10 07:03:50 JST
