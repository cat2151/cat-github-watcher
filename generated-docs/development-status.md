Last updated: 2026-02-05

# Development Status

## 現在のIssues
- [Issue #143](../issue-notes/143.md)では、自動assign機能の再有効化と、失敗時に生成されるスクリーンショットを利用した原因特定が必要です。
- [Issue #87](../issue-notes/87.md)は、大規模な仕様変更が実施されたため、実際の運用環境でのテスト（ドッグフーディング）を通じて全体的な動作検証を行う必要があります。
- これらのオープンIssueは、既存機能の安定性向上と、新機能導入後の実運用テストに焦点を当てています。

## 次の一手候補
1. [Issue #143](../issue-notes/143.md): 自動assignを改めてonにし、失敗時に生成されるスクリーンショットを利用して調査する
   - 最初の小さな一歩: `config.toml.example`を確認し、自動assignを有効にするための設定項目を特定し、一時的に`True`に設定する変更案を作成する。
   - Agent実行プロンプト:
     ```
     対象ファイル: `config.toml.example`, `src/gh_pr_phase_monitor/config.py`, `src/gh_pr_phase_monitor/browser_automation.py`

     実行内容: 自動assign機能を制御する設定項目を`config.py`内で特定し、`config.toml.example`におけるその設定方法を分析してください。次に、`browser_automation.py`内で自動assignの呼び出し箇所および失敗時にスクリーンショットが生成されるロジック（ファイルパス、条件など）を特定してください。

     確認事項: 自動assign機能のON/OFFを切り替える既存の設定項目があるか、またその設定が`browser_automation.py`にどのように伝達されているかを確認してください。関連する既存のテストケースも参照してください。

     期待する出力:
     1. 自動assignを有効にするための具体的な設定変更方法（`config.toml`のどの項目を`True`にするか）をmarkdown形式で記述してください。
     2. 自動assignが失敗した際にスクリーンショットが生成されるロジックについて、`browser_automation.py`から抽出した情報をmarkdown形式で記述してください。
     ```

2. [Issue #87](../issue-notes/87.md): 大幅な仕様変更をしたのでドッグフーディングする
   - 最初の小さな一歩: 最近のコミット履歴と関連ドキュメントを確認し、大幅な仕様変更によって影響を受けた主要な機能領域を特定する。
   - Agent実行プロンプト:
     ```
     対象ファイル: `docs/IMPLEMENTATION_SUMMARY.md`, `docs/PR67_IMPLEMENTATION.md`, `docs/button-detection-improvements.ja.md`, `src/gh_pr_phase_monitor/browser_automation.py`, `src/gh_pr_phase_monitor/main.py`, `src/gh_pr_phase_monitor/monitor.py`

     実行内容: 最近のコミット履歴と関連ドキュメント（特に`docs`ディレクトリ内の変更に関するもの）を基に、大幅な仕様変更によって影響を受けた主要な機能領域（例: ブラウザ自動化、PRフェーズ検出、コメント管理、通知）を特定してください。これに基づいて、ドッグフーディングで検証すべき主要な機能と、その検証観点を3点以上提案してください。

     確認事項: 最近の変更がどの機能に集中しているか、またそれらの変更がユーザー体験にどのような影響を与える可能性があるかを確認してください。既存のテストスイートがこれらの変更を十分にカバーしているかどうかも考慮に入れてください。

     期待する出力:
     1. ドッグフーディングで重点的に検証すべき機能領域とその理由をmarkdown形式でリストアップしてください。
     2. 各機能領域に対して、具体的な検証観点（例: 「ボタン検出の精度」「コメント投稿の安定性」「通知の即時性」など）をmarkdown形式で記述してください。
     3. ドッグフーディング計画の最初のステップとして、これらの検証観点に基づいたテストケースの簡単な記述（例: 「〇〇機能をXXのデータでYYの操作を行い、ZZを確認する」）を提案してください。
     ```

3. 共通ワークフローの利用状況とメンテナンスを確認する
   - 最初の小さな一歩: プロジェクトの`.github/workflows`ディレクトリにある`call-*.yml`ファイル群と、`.github/actions-tmp/.github/workflows/`にある対応する共通ワークフローファイル（例: `call-issue-note.yml`と`issue-note.yml`）を比較し、最新性と整合性を確認する。
   - Agent実行プロンプト:
     ```
     対象ファイル:
     - 呼び出し元: `.github/workflows/call-daily-project-summary.yml`, `.github/workflows/call-issue-note.yml`, `.github/workflows/call-translate-readme.yml`
     - 共通ワークフロー: `.github/actions-tmp/.github/workflows/daily-project-summary.yml`, `.github/actions-tmp/.github/workflows/issue-note.yml`, `.github/actions-tmp/.github/workflows/translate-readme.yml`
     - ドキュメント: `.github/actions-tmp/issue-notes/3.md`

     実行内容: 各呼び出し元ワークフロー（`.github/workflows/call-*.yml`）が対応する共通ワークフロー（`.github/actions-tmp/.github/workflows/*.yml`）を正しく参照しているか、および必要な`inputs`と`secrets`を適切に渡しているかを確認してください。特に、[Issue #3](../issue-notes/3.md)で指摘された`actions/github-script`内での`inputs`参照の問題が他の共通ワークフローで再発していないかをチェックしてください。

     確認事項:
     1. 呼び出し元ワークフローと共通ワークフロー間で`inputs`/`secrets`の定義と利用が一致しているか確認してください。
     2. `actions/github-script`を使用している共通ワークフローが存在する場合、`inputs`の参照方法が[Issue #3](../issue-notes/3.md)で修正された「`env`で渡して`process.env`で参照する」パターンになっているか確認してください。
     3. 共通ワークフローが想定通りに実行されているか（過去の実行ログを参照できる場合は参照する）確認してください。

     期待する出力:
     1. 各共通ワークフローについて、呼び出し元からの`inputs`/`secrets`の渡し方と、共通ワークフロー内での受け取り方の整合性に関する評価をmarkdown形式で記述してください。
     2. もし不整合や潜在的な問題が発見された場合、具体的な修正提案をmarkdown形式で記述してください。
     3. 特に、[Issue #3](../issue-notes/3.md)の教訓が他の共通ワークフローに適用されているかのチェック結果を明記してください。

---
Generated at: 2026-02-05 07:02:42 JST
