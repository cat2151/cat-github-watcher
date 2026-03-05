Last updated: 2026-03-06

# Development Status

## 現在のIssues
- [Issue #346](../issue-notes/346.md) と [Issue #345](../issue-notes/345.md) は、HTMLベースのステータス検出リファクタリングにおいて、`logs/pr` ディレクトリにPRのHTMLが限定的にしか保存されない問題を指摘しています。特に `PHASE_LLM_WORKING` 以外のPRのHTMLがスキップされてしまうことが課題です。
- [Issue #335](../issue-notes/335.md) では、PRのPHASE1～3の扱いと検出ロジックの見直しが求められており、これによりシステム全体のPRフェーズ管理の精度向上が期待されます。
- [Issue #319](../issue-notes/319.md) は、GitHub GraphQL APIのクエリが過剰に消費されている現状を改善し、効率的なAPI利用とレート制限への対応を最適化する必要があることを示唆しています。

## 次の一手候補
1.  [Issue #346](../issue-notes/346.md) と [Issue #345](../issue-notes/345.md): 全てのオープンPRのHTMLを `logs/pr` に確実に保存する
    -   最初の小さな一歩: `src/gh_pr_phase_monitor/monitor/monitor.py` 内のPR処理ループを分析し、各PRが処理される際に、そのHTMLコンテンツが`PHASE_LLM_WORKING`に依存せず、常に`src/gh_pr_phase_monitor/phase/pr_html_saver.py`の`save_html_to_logs`関数を使って`logs/pr`に保存されるように修正点を検討する。
    -   Agent実行プロンプト:
        ```
        対象ファイル: src/gh_pr_phase_monitor/monitor/monitor.py, src/gh_pr_phase_monitor/phase/pr_html_fetcher.py, src/gh_pr_phase_monitor/phase/pr_html_saver.py

        実行内容: `src/gh_pr_phase_monitor/monitor/monitor.py` のPRループ内で、全てのオープンPRについて、そのHTMLコンテンツを`src/gh_pr_phase_monitor/phase/pr_html_fetcher.py`の`_fetch_pr_html`で取得し、その後`src/gh_pr_phase_monitor/phase/pr_html_saver.py`の`save_html_to_logs`を呼び出して`logs/pr`ディレクトリに保存するロジックを追加・修正してください。この保存は、PRの現在のフェーズや`record_reaction_snapshot`の呼び出し条件に依存しない独立した処理として実装されるべきです。

        確認事項:
        1. HTMLフェッチと保存が、全体のパフォーマンスやAPIレート制限に過度な影響を与えないこと。
        2. `save_html_to_logs`に渡される`analysis`データが、PRの状態（`is_draft`、`llm_statuses`）を正確に反映していること。
        3. 既存のPR処理フロー（特にフェーズ検出やスナップショット記録）の意図しない変更がないこと。
        4. 同じHTMLコンテンツが不必要に何度も再保存されないような軽微な最適化を検討すること。

        期待する出力: `monitor.py` への追加または修正されるコードの差分（diff）形式、および変更の理由、新しいHTML保存フローの説明をMarkdown形式で出力してください。
        ```

2.  [Issue #335](../issue-notes/335.md): PRのPHASE1～3の検出ロジックを改善する
    -   最初の小さな一歩: 現在の `src/gh_pr_phase_monitor/phase/pr_html_analyzer.py` 内の `_determine_html_status` 関数と関連するフェーズ検出ロジックを分析し、PHASE1-3の定義と現在の実装における状態遷移のギャップを特定する。
    -   Agent実行プロンプト:
        ```
        対象ファイル: src/gh_pr_phase_monitor/phase/phase_detector.py, src/gh_pr_phase_monitor/phase/pr_html_analyzer.py, src/gh_pr_phase_monitor/phase/llm_status_extractor.py

        実行内容: PRのPHASE1～3の検出ロジック（`phase_detector.py` と `pr_html_analyzer.py` 内の `_determine_html_status`）が現状どうなっているかを分析し、現在の定義（例：PRの状態、コメント、レビュー状況、LLMステータスなど）と期待されるPHASE1-3の挙動との間にどのようなギャップがあるか、markdown形式で出力してください。特に、`llm_status_extractor.py` からのLLMステータスがどのようにフェーズ検出に利用されているかを詳しく調べてください。

        確認事項:
        1. 既存の `PHASE_LLM_WORKING` 検出ロジックに影響を与えないこと。
        2. `is_draft` などのPRメタデータがフェーズ検出に適切に考慮されているか。
        3. 各フェーズへの遷移条件が明確に定義されているか。

        期待する出力: 現在のフェーズ検出ロジックの詳細な分析と、PHASE1-3の扱いにおける具体的な改善点をMarkdown形式で提案してください。
        ```

3.  [Issue #319](../issue-notes/319.md): GraphQLクエリの過剰消費を最適化する
    -   最初の小さな一歩: `src/gh_pr_phase_monitor/github/graphql_client.py` と `src/gh_pr_phase_monitor/github/pr_fetcher.py` を分析し、どのGraphQLクエリが頻繁に実行されているか、また、不要なデータフェッチが行われている箇所がないか特定する。
    -   Agent実行プロンプト:
        ```
        対象ファイル: src/gh_pr_phase_monitor/github/graphql_client.py, src/gh_pr_phase_monitor/github/pr_fetcher.py, src/gh_pr_phase_monitor/github/rate_limit_handler.py

        実行内容: GitHub APIのGraphQLクエリ消費量を削減するための改善策を提案してください。具体的には、`pr_fetcher.py` や `graphql_client.py` で実行されているクエリの中から、不要なフィールドの取得や、キャッシュ可能な情報の再取得が行われている箇所がないか分析し、効率的なクエリ設計やデータ取得戦略の変更点をMarkdown形式で提案してください。`rate_limit_handler.py` がどのようにクエリ消費を管理しているかも考慮に入れてください。

        確認事項:
        1. 必要なPR情報が失われないこと。
        2. 既存の機能（例: フェーズ検出、コメント処理）の動作に悪影響を与えないこと。
        3. APIレート制限の管理が引き続き適切に行われること。

        期待する出力: GraphQLクエリの最適化に関する具体的なコード修正案（擬似コードまたは差分形式）と、それによって期待されるクエリ消費削減効果をMarkdown形式で記述してください。

---
Generated at: 2026-03-06 07:04:20 JST
