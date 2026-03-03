Last updated: 2026-03-04

# Development Status

## 現在のIssues
- [Issue #323](../issue-notes/323.md)と[Issue #314](../issue-notes/314.md)では、GraphQLの`reviewThreads`の`isResolved`が正しく反映されず、PRのフェーズがphase2と誤判定される根本的なロジック不備が確認されています。
- この誤判定により、Copilotがフィードバック対応済みでもレビューが未解決とみなされ、PRが継続的にphase2に留まってしまう問題が発生しています。
- [Issue #319](../issue-notes/319.md)ではGraphQLクエリの過剰消費が課題となっており、HTMLベースのデータ取得を活用したクエリ削減の検討が求められています。

## 次の一手候補
1.  [Issue #323](../issue-notes/323.md) fix: phase2/phase3誤検出の根本修正とllm_statuses優先への統一
    -   最初の小さな一歩: `src/gh_pr_phase_monitor/phase_detector.py`の`_phase_from_llm_statuses`関数を修正し、LLMステータスリストに"reviewing"イベントが存在し、かつその後の"finished work"がない場合に`PHASE_2`を返すロジックを追加する。
    -   Agent実行プロンプ:
        ```
        対象ファイル: `src/gh_pr_phase_monitor/phase_detector.py`

        実行内容: `_phase_from_llm_statuses`関数を修正し、LLMステータスリストに"reviewing"イベントが存在し、かつその後の"finished work"がない場合に`PHASE_2`を返すロジックを追加してください。現状は`PHASE_3`のみを返していますが、`PHASE_2`の検出も可能に拡張します。具体的には、`review_idx`、`last_started_idx`、`last_finished_idx`を適切に追跡し、"reviewing"後に"started work"があり、"finished work"がない場合に`PHASE_2`を返す条件を追加してください。

        確認事項: 既存の`PHASE_3`を返すロジックに影響を与えないこと。`determine_phase`関数や関連するテストケース（特に`tests/test_phase_detection_llm_status.py`）との整合性を確認すること。`llm_working_from_statuses`関数との役割分担を明確にすること。

        期待する出力: 修正された`src/gh_pr_phase_monitor/phase_detector.py`ファイル。
        ```

2.  [Issue #319](../issue-notes/319.md) ムダにGraphQLクエリを消費しすぎ
    -   最初の小さな一歩: `src/gh_pr_phase_monitor/pr_html_analyzer.py`が現在抽出している情報を見直し、`phase_detector.py`がGraphQLから取得している情報（特に`reviewThreads`の`isResolved`や`isOutdated`）をHTMLから抽出可能か調査する。
    -   Agent実行プロンプ:
        ```
        対象ファイル: `src/gh_pr_phase_monitor/pr_html_analyzer.py`と`src/gh_pr_phase_monitor/phase_detector.py`

        実行内容: `pr_html_analyzer.py`がPRのHTMLから、`phase_detector.py`で現在GraphQLから取得している`reviewThreads`内の`isResolved`や`isOutdated`などの情報を抽出できるか調査してください。具体的には、PRのHTMLスナップショット（例: `fetch_pr_html.py`で取得されるもの）から、未解決のレビューコメントスレッドを特定するためのDOM要素やテキストパターンを見つけてください。その結果をMarkdown形式で報告してください。

        確認事項: HTML構造がGitHubのUI変更により変化する可能性を考慮し、頑健な抽出方法を検討すること。`pr_html_analyzer.py`の既存の処理フローに影響を与えないこと。

        期待する出力: `reviewThreads`関連情報をHTMLから抽出する方法と、その際に利用可能なセレクタや正規表現パターンを記述したMarkdown形式の調査報告。
        ```

3.  [Issue #314](../issue-notes/314.md) 現在観測できるPRが、すべて現実はphase3なのに、判定結果が誤ってphase2という判定をされてしまっている
    -   最初の小さな一歩: 現在誤判定されている具体的なPRのHTMLスナップショットとGraphQLデータを収集し、`phase_detector.py`の`determine_phase`関数がどのように誤った判断を下しているか、ステップバイステップで原因を分析する。
    -   Agent実行プロンプ:
        ```
        対象ファイル: `src/gh_pr_phase_monitor/phase_detector.py`, `tests/test_phase_detection_real_prs.py` (または新しいテストファイル), 誤判定されているPRのHTML/GraphQLデータ (存在する場合)

        実行内容: 誤ってphase2と判定されている実際のPRのデータ（可能であればHTMLスナップショットとGraphQLレスポンス）を仮定し、`phase_detector.py`の`determine_phase`関数がそのデータをどのように処理し、最終的に誤った`PHASE_2`を返すのかを詳細に分析してください。特に、`has_unresolved_review_threads`や`llm_working_from_statuses`などの補助関数がどのような値を返しているか、どのパスで処理が進んでいるかをステップごとに記述してください。

        確認事項: 実際のPRデータがない場合は、典型的な誤判定を引き起こすであろう仮想的なデータ構造を想定して分析を進めること。分析結果は、[Issue #323](../issue-notes/323.md)の解決に役立つ具体的な洞察を提供すること。

        期待する出力: 誤判定の具体的な原因と、`phase_detector.py`内のどの条件分岐がその原因に関与しているかを明らかにする詳細な分析レポートをMarkdown形式で生成してください。

---
Generated at: 2026-03-04 07:03:53 JST
