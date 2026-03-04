Last updated: 2026-03-05

# Development Status

## 現在のIssues
- [Issue #338](../issue-notes/338.md) & [Issue #334](../issue-notes/334.md): PRごとのHTMLとJSONファイルを常に保存し、フェーズ判定の検証とデバッグに利用するための実装を進めています。
- [Issue #324](../issue-notes/324.md): 実際のPRがPhase3にもかかわらずPhase2と誤判定される問題があり、その原因を特定・修正する必要があります。
- [Issue #335](../issue-notes/335.md): PRのPHASE1～3のステータス判定ロジックの見直しと変更を検討しています。

## 次の一手候補
1. [Issue #338](../issue-notes/338.md) & [Issue #334](../issue-notes/334.md): PR HTML/JSONの常時保存機能の検証と安定化
   - 最初の小さな一歩: `src/gh_pr_phase_monitor/phase/pr_data_recorder.py` が、PR更新時に`src/gh_pr_phase_monitor/phase/pr_html_saver.py` のHTML/JSON保存機能を適切に呼び出していることを確認し、不足があれば実装する。
   - Agent実行プロンプ:
     ```
     対象ファイル: src/gh_pr_phase_monitor/phase/pr_html_saver.py, src/gh_pr_phase_monitor/phase/pr_data_recorder.py

     実行内容: `src/gh_pr_phase_monitor/phase/pr_html_saver.py` 内の `save_pr_html` 関数が、監視ループ内でPRが更新されるたびに呼び出され、HTMLとそれに伴うJSONが `logs/pr/` ディレクトリに保存されるように `src/gh_pr_phase_monitor/phase/pr_data_recorder.py` を修正してください。既存の `save_pr_html` 関数が既にHTML解析とJSON保存を行っているため、`pr_data_recorder.py` からこれを適切に呼び出すように変更します。

     確認事項: `save_pr_html` の呼び出しが既存の機能と重複しないこと、およびパフォーマンスへの影響が最小限であることを確認してください。

     期待する出力: `src/gh_pr_phase_monitor/phase/pr_data_recorder.py` の修正内容をdiff形式で出力し、変更が意図通りに動作することを確認するための簡単なテスト手順（例: `main.py` を実行して `logs/pr/` ディレクトリにPRごとのHTMLおよびJSONファイルが生成されることを確認）をmarkdown形式で記述してください。
     ```

2. [Issue #324](../issue-notes/324.md): PRのPhase3誤判定問題の原因調査
   - 最初の小さな一歩: 誤判定が発生している実際のPRのHTMLと、現在のフェーズ判定ロジック (`phase_detector.py` や `llm_status_extractor.py`) を比較し、どこで乖離が生じているかを特定する。
   - Agent実行プロンプ:
     ```
     対象ファイル: src/gh_pr_phase_monitor/phase/phase_detector.py, src/gh_pr_phase_monitor/phase/phase_detector_graphql.py, src/gh_pr_phase_monitor/phase/llm_status_extractor.py, および logs/pr/内の最新のPR HTML/JSONファイル

     実行内容: 現在Phase3であるにもかかわらずPhase2と誤判定されているPR（もしあれば `logs/pr/` から取得できる最新のPRデータを使用）のHTML/JSONデータを分析し、`src/gh_pr_phase_monitor/phase/phase_detector.py` と `src/gh_pr_phase_monitor/phase/phase_detector_graphql.py` のロジック、およびLLMによるステータス抽出 (`src/gh_pr_phase_monitor/phase/llm_status_extractor.py`) の出力と照合して、誤判定の原因となっている具体的な条件やコード箇所を特定してください。

     確認事項: 誤判定が特定のPRに限定されるのか、一般的な傾向なのかを確認し、`phase_detector_graphql.py` が現在のアクティブな判定ロジックとして使用されているかどうかも考慮に入れてください。

     期待する出力: 誤判定の原因となっている可能性のあるコード箇所（ファイル名と行番号）、およびその原因に関する仮説をmarkdown形式で記述してください。
     ```

3. [Issue #335](../issue-notes/335.md): PHASE1～3ステータス判定の新しい扱いに関する設計検討
   - 最初の小さな一歩: 現在のPHASE1～3の定義と、それがコード内でどのように利用されているかを洗い出し、変更の必要性を具体的に定義するためのドキュメント案を作成する。
   - Agent実行プロンプ:
     ```
     対象ファイル: src/gh_pr_phase_monitor/phase/phase_detector.py, src/gh_pr_phase_monitor/phase/phase_detector_graphql.py, src/gh_pr_phase_monitor/phase/llm_status_extractor.py, src/gh_pr_phase_monitor/actions/pr_actions.py, docs/RULESETS.md (もし関連定義があれば)

     実行内容: 現在のシステムにおけるPHASE1～3の定義、それぞれのフェーズへの移行条件、およびそれらが `src/gh_pr_phase_monitor/actions/pr_actions.py` など他のモジュールでどのように利用されているかを詳細に分析してください。その上で、[Issue #335](../issue-notes/335.md) の意図に基づき、これらのフェーズの扱いを変更するための設計案の概要をmarkdown形式で作成してください。変更のメリット・デメリット、既存システムへの影響についても簡潔に言及してください。

     確認事項: フェーズ定義の変更が、PRアクション（コメント投稿、マージなど）に与える影響、およびユーザーインターフェースでの表示に与える影響を考慮してください。

     期待する出力: `PHASE1～3の扱い変更設計案` と題したmarkdownドキュメント。現状のフェーズ定義のまとめ、変更の目的、主要な変更点、影響範囲の概算を含めてください。

---
Generated at: 2026-03-05 07:04:24 JST
