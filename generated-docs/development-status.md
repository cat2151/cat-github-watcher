Last updated: 2026-02-09

# Development Status

## 現在のIssues
- [Issue #220](../issue-notes/220.md) と [Issue #216](../issue-notes/216.md) は、LLMステータス表示とPRフェーズスナップショットの取得機能を、`config.toml`で有効/無効化し、デフォルトを無効にすることを提案しています。
- [Issue #219](../issue-notes/219.md) は、`README.ja.md`に、特にCodexやClaude対応といった機能の記載漏れがないか調査を求めています。
- [Issue #218](../issue-notes/218.md) は、プロジェクト内の陳腐化したドキュメントやスクリプトを特定し、削除することでコードベースの健全化を目指しています。

## 次の一手候補
1. [Issue #220](../issue-notes/220.md): LLM status timeline 表示の on/off 設定の実装
   - 最初の小さな一歩: `config.toml.example`に`enable_llm_status_timeline = false`を追加し、`src/gh_pr_phase_monitor/config.py`でこの設定を読み込むロジックを実装します。
   - Agent実行プロンプト:
     ```
     対象ファイル: `config.toml.example`, `src/gh_pr_phase_monitor/config.py`, `src/gh_pr_phase_monitor/display.py`, `src/gh_pr_phase_monitor/main.py`

     実行内容:
     1. `config.toml.example` に `enable_llm_status_timeline = false` を追加します。適切なセクション（例: `[display]` または新設）に配置してください。
     2. `src/gh_pr_phase_monitor/config.py` にて、追加した `enable_llm_status_timeline` 設定を読み込むロジックを実装します。この設定はブール値として読み込まれ、デフォルトは `false` とします。
     3. `src/gh_pr_phase_monitor/main.py` または `src/gh_pr_phase_monitor/display.py` にて、`LLM status timeline` の表示ロジックがこの新しい設定値に基づいて制御されるように変更します。`d95b9f8 feat: print llm status timeline for debugging` コミットで追加された部分を中心に修正を検討してください。

     確認事項:
     - 既存の `config.toml` の読み込みロジックとの整合性を確認してください。
     - `main.py` または `display.py` での `LLM status timeline` 表示ロジックが、新しい設定が `false` の場合に正しく無効化されることを確認してください。
     - `config.toml.example` に追記した設定が、既存の設定項目と競合しないこと。

     期待する出力:
     - `config.toml.example` の変更内容。
     - `src/gh_pr_phase_monitor/config.py` で設定を読み込む関数の変更内容。
     - `src/gh_pr_phase_monitor/display.py` または `src/gh_pr_phase_monitor/main.py` で表示ロジックを制御する変更内容。
     ```

2. [Issue #219](../issue-notes/219.md): 「README.ja.mdへの記載が漏れている機能」の調査
   - 最初の小さな一歩: `README.ja.md` と `src/gh_pr_phase_monitor/config.py` を開き、`config.py`で定義されている設定項目が`README.ja.md`に全て記載されているか、特に`[coding_agent]`セクションや`enable_ocr_detection`など、最近追加された可能性のある機能を中心に確認します。
   - Agent実行プロンプト:
     ```
     対象ファイル: `README.ja.md`, `src/gh_pr_phase_monitor/config.py`

     実行内容:
     1. `src/gh_pr_phase_monitor/config.py` を分析し、`cat-github-watcher` が提供する全ての機能および設定項目をリストアップしてください。
     2. リストアップした機能と設定項目について、`README.ja.md` の内容と照らし合わせ、特に `coding_agent` の `agent_name`（codex/claude対応を示唆する）や、ブラウザ自動操作関連の機能（`assign_to_copilot`, `phase3_merge` の詳細設定、OCR検出など）について、記載漏れがないか調査してください。
     3. 調査結果に基づき、`README.ja.md` に追記が必要な機能や設定項目、または既存の記載が不十分な箇所を具体的に示してください。

     確認事項:
     - `config.py` から機能を抽出する際、全ての関連する設定キーやデフォルト値が考慮されていること。
     - `README.ja.md` の現状の構造や記述スタイルを尊重し、追記提案が行われること。
     - 「状況」セクションに「codexとclaudeに対応したことは、記載が漏れてそう」とあるため、この点に特に注意して調査すること。

     期待する出力: Markdown形式で、以下の内容を含めてください。
     - `src/gh_pr_phase_monitor/config.py` から抽出された主要機能と設定項目の一覧。
     - `README.ja.md` の記載漏れや不十分な点に関する詳細な分析結果。
     - `README.ja.md` の該当箇所に追記すべき内容の具体的な提案（Markdown形式のスニペットを含む）。
     ```

3. [Issue #218](../issue-notes/218.md): 陳腐化したドキュメントを削除する。あわせて「もう一切使う可能性がなくなったscript」があるかlistしてPRに報告する
   - 最初の小さな一歩: プロジェクトルート直下および `.github/actions-tmp/` ディレクトリ内のドキュメントファイルやスクリプトファイルを一覧し、ファイル名や内容から現在のプロジェクトで不要と思われるものを仮に特定します。特に`MERGE_CONFIGURATION_EXAMPLES.md`, `PHASE3_MERGE_IMPLEMENTATION.md` や、`.github/actions-tmp/` に含まれるファイル群の古さや関連性を確認します。
   - Agent実行プロンプト:
     ```
     対象ファイル: プロジェクト内の全ての `.md` ファイルと、`.github/actions-tmp/` ディレクトリ以下の全てのファイル。

     実行内容:
     1. 以下の条件に基づいて、陳腐化している可能性のあるドキュメントファイルおよびスクリプトファイルを特定してください。
         - プロジェクトの現在の機能や目的と一致しない内容。
         - 他の新しいドキュメントやコードで置き換えられている、または冗長になっている。
         - テストや一時的な目的で作成されたが、現在は利用されていない（例: `_tmp` や `example` がファイル名に含まれるもの、古い実装の痕跡など）。
         - 特に、プロジェクトルート直下の `MERGE_CONFIGURATION_EXAMPLES.md`, `PHASE3_MERGE_IMPLEMENTATION.md` や、`.github/actions-tmp/` ディレクトリ以下のファイル群に着目してください。
     2. 特定した各ファイルについて、削除を推奨する理由を簡潔に説明してください。
     3. 削除対象のスクリプトについては、それが「もう一切使う可能性がなくなったscript」であるかどうかの判断も示してください。

     確認事項:
     - 削除を提案するファイルが、本当に現在および将来のプロジェクトにとって不要であることを慎重に確認してください。他のIssueや未実装の機能との関連性がないか注意深く調査すること。
     - `.github/actions-tmp/` 内のファイルは、元々はGitHub Actionsの共通ワークフロー集として外部プロジェクトから利用されることを想定している可能性があるため、その文脈も考慮に入れる必要があります。ただし、現在の `cat-github-watcher` プロジェクトの直接的なコードベースではないため、原則として削除対象になりやすい。

     期待する出力: Markdown形式で、以下の内容を含めてください。
     - 削除を推奨するファイルのリスト（ファイルパス）。
     - 各ファイルに対する削除理由。
     - 特に「もう一切使う可能性がなくなったscript」として判断されるスクリプトのリスト。

---
Generated at: 2026-02-09 07:03:09 JST
