Last updated: 2026-01-07

# Development Status

## 現在のIssues
- `config.toml`の`rulesets`におけるリポジトリ名の指定方法の簡素化（[#93](../issue-notes/93.md)）、実行制御フラグの定義範囲の限定（[#92](../issue-notes/92.md)）、`phase3_merge`と`assign_to_copilot`設定の`rulesets`ごとの定義化（[#91](../issue-notes/91.md)）に関する改善がオープン中。
- 特定の条件（全てPhase3など）でのタイムアウト設定のデフォルト値変更（[#85](../issue-notes/85.md)）やntfy通知機能の追加（[#80](../issue-notes/80.md)）、PRの自動割り当て機能の拡張（[#94](../issue-notes/94.md), [#83](../issue-notes/83.md)）といった新機能・改善も進行中。
- 大規模な仕様変更後のドッグフーディング（[#87](../issue-notes/87.md)）や、ユーザーが混乱するメッセージの修正（[#32](../issue-notes/32.md)）も今後の課題として認識されている。

## 次の一手候補
1.  [Issue #93](../issue-notes/93.md): toml rulesets repositories から owner を削除し、リポジトリ名のみで指定できるようにする
    -   最初の小さな一歩: `config.toml.example` の `rulesets` 例から `owner/` の記述を削除し、`src/gh_pr_phase_monitor/config.py` の `resolve_execution_config_for_repo` 関数を修正してリポジトリ名のみでマッチングできるようにする。
    -   Agent実行プロンプト:
        ```
        対象ファイル: `config.toml.example`, `src/gh_pr_phase_monitor/config.py`

        実行内容:
        1. `config.toml.example` 内の `[[rulesets]]` セクションの `repositories = ["owner/test-repo"]` などの例から `owner/` の記述を削除し、`repositories = ["test-repo"]` の形式に修正してください。
        2. `repositories = ["owner/prod-repo1", "owner/prod-repo2"]` の例も同様に、リポジトリ名のみの形式に修正してください。
        3. 関連するコメント（例: "Specific repository with owner/name format" や "Example with repo name only"）を、リポジトリ名のみを推奨する内容に更新してください。
        4. `src/gh_pr_phase_monitor/config.py` の `resolve_execution_config_for_repo` 関数を修正し、`repositories` にリポジトリ名のみが指定された場合に正しくマッチングされるようにロジックを調整してください。特に、`repo_pattern == repo_full_name` のチェックを削除するか、`repo_pattern == repo_name` のチェックを優先するようにしてください。

        確認事項:
        - `config.toml.example` の変更がTOMLの構文に準拠していること。
        - `src/gh_pr_phase_monitor/config.py` の変更が、`"all"` マッチングと `repo_name` マッチングの両方で正しく動作すること。
        - 既存のテスト (`tests/test_config_rulesets.py` など) に影響がないか、必要であれば新しいテストケースを追加すること。

        期待する出力:
        - `config.toml.example` の更新された内容。
        - `src/gh_pr_phase_monitor/config.py` の更新された内容。
        - 変更点のサマリーと、既存機能への影響分析をMarkdown形式で出力してください。
        ```

2.  [Issue #92](../issue-notes/92.md): tomlの実行制御フラグをrulesetsの内部でのみ記述できるようにし、userの混乱を減らす
    -   最初の小さな一歩: `config.toml.example` からグローバルな `enable_execution_phaseX_to_phaseY` 設定を削除し、`src/gh_pr_phase_monitor/config.py` の `resolve_execution_config_for_repo` 関数からグローバル設定の読み込みと適用ロジックを削除する。
    -   Agent実行プロンプト:
        ```
        対象ファイル: `config.toml.example`, `src/gh_pr_phase_monitor/config.py`

        実行内容:
        1. `config.toml.example` から `enable_execution_phase1_to_phase2 = false` などのグローバルな実行制御フラグの記述を完全に削除してください。
        2. `rulesets` の説明セクションに、これらのフラグは `rulesets` 内でのみ定義可能であることを追記してください。
        3. `src/gh_pr_pr_phase_monitor/config.py` の `print_config` 関数からグローバル実行フラグの表示を削除してください。
        4. `src/gh_pr_phase_monitor/config.py` の `resolve_execution_config_for_repo` 関数内で、グローバル設定からこれらのフラグを初期化するロジック（`get_validated_flag` を含む部分）を削除し、デフォルト値（全て `false`）を直接設定した上で、`rulesets` の設定を適用するように修正してください。
        5. `_validate_boolean_flag` の呼び出し箇所についても、グローバル設定に関連する部分は削除してください。

        確認事項:
        - `config.toml.example` が意図通り簡素化され、誤解を招かない説明になっていること。
        - `src/gh_pr_phase_monitor/config.py` の変更により、`rulesets` が定義されていない場合に全ての実行フラグが `false` になることを確認すること。
        - `rulesets` が定義されている場合に、`rulesets` 内のフラグが正しく適用されることを確認すること。
        - 既存のテストに影響がないか、必要であれば新しいテストケースを追加すること。

        期待する出力:
        - `config.toml.example` の更新された内容。
        - `src/gh_pr_phase_monitor/config.py` の更新された内容。
        - 変更点のサマリーと、既存機能への影響分析をMarkdown形式で出力してください。
        ```

3.  [Issue #91](../issue-notes/91.md): tomlのphase3_merge と assign_to_copilot は rulesetsごとに定義可能にする
    -   最初の小さな一歩: `config.toml.example` の `[[rulesets]]` セクションに `phase3_merge` と `assign_to_copilot` の設定例を追加し、`src/gh_pr_phase_monitor/config.py` の `resolve_execution_config_for_repo` 関数でこれらの設定を `rulesets` から読み込み、リポジトリ固有の設定として適用できるように拡張する。
    -   Agent実行プロンプト:
        ```
        対象ファイル: `config.toml.example`, `src/gh_pr_phase_monitor/config.py`

        実行内容:
        1. `config.toml.example` の `[[rulesets]]` の説明と例に、`phase3_merge` (enabled, comment, automated など) と `assign_to_copilot` (enabled, automated など) の各設定を `rulesets` 内で定義できることを示す新しい例を追加してください。
        2. `[phase3_merge]` と `[assign_to_copilot]` のグローバル設定を `rulesets` で上書きできるように、`src/gh_pr_phase_monitor/config.py` の `resolve_execution_config_for_repo` 関数を拡張してください。具体的には、`ruleset` 内にこれらのセクションが存在する場合、そのリポジトリに対してはグローバル設定ではなく `ruleset` の設定を優先して適用するようにロジックを追加してください。
        3. `print_repo_execution_config` 関数も更新し、リポジトリ固有の `phase3_merge` と `assign_to_copilot` の設定も表示できるようにしてください。

        確認事項:
        - `config.toml.example` の例が明確で、`rulesets` での設定方法が分かりやすいこと。
        - `src/gh_pr_phase_monitor/config.py` の変更により、`rulesets` で `phase3_merge` や `assign_to_copilot` が設定された場合に、グローバル設定よりも優先されることを確認すること。
        - `rulesets` で設定されていない場合は、引き続きグローバル設定が適用されることを確認すること。
        - 既存のテストに影響がないか、必要であれば新しいテストケースを追加すること。

        期待する出力:
        - `config.toml.example` の更新された内容。
        - `src/gh_pr_phase_monitor/config.py` の更新された内容。
        - 変更点のサマリーと、既存機能への影響分析をMarkdown形式で出力してください。
        ```

---
Generated at: 2026-01-07 07:02:33 JST
