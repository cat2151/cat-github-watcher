Last updated: 2026-01-09

# Development Status

## 現在のIssues
- [Issue #93](../issue-notes/93.md) は、`config.toml`のrulesets repositories設定から`owner`フィールドを削除し、リポジトリ名のみで指定するよう改善し、ユーザーの混乱を軽減することを目指しています。
- [Issue #87](../issue-notes/87.md) は、最近の大幅な仕様変更を受けて、実際の運用環境での動作確認（ドッグフーディング）を通じてシステムの安定性と機能性を検証する必要があることを示しています。
- これらのIssueは、設定ファイルの明確化と、主要機能の総合的なテスト・検証が喫緊の課題であることを示唆しています。

## 次の一手候補
1. [Issue #93](../issue-notes/93.md) `config.toml.example`から`rulesets.repositories`の`owner`フィールドを削除する
   - 最初の小さな一歩: `config.toml.example`ファイルを開き、`[rulesets.repositories]`セクション内の`owner = "..."`の行を削除し、`repository = "..."`の形式のみが残るように修正する。
   - Agent実行プロンプ:
     ```
     対象ファイル: `config.toml.example`

     実行内容: `config.toml.example`の`[rulesets.repositories]`セクションにおいて、`owner = "..."`の行を削除し、`repository = "..."`の形式でリポジトリ名が指定されるように修正してください。例えば、`repository = "my-org/my-repo"`を`repository = "my-repo"`のようにしてください。

     確認事項: 既存の`[rulesets.repositories]`の構造が壊れていないこと。TOMLファイルの構文規則に則っていること。

     期待する出力: 修正後の`config.toml.example`ファイルの内容をmarkdown形式で出力してください。
     ```

2. [Issue #87](../issue-notes/87.md) 大幅な仕様変更後のドッグフーディングに向けた初期設定と実行フローの確認
   - 最初の小さな一歩: `config.toml.example`を参考に、最新の仕様（特にルールセット関連）を反映した`config.toml`を作成し、`src/gh_pr_phase_monitor/main.py`を手動で実行する準備を行う。
   - Agent実行プロンプ:
     ```
     対象ファイル: `src/gh_pr_phase_monitor/main.py`, `config.toml.example` (参考)

     実行内容:
     1. `config.toml.example`を参考に、現在の仕様（特にルールセット関連の変更）を反映した`config.toml`を新規作成または更新するためのガイダンスを提供してください。
     2. `src/gh_pr_phase_monitor/main.py`をローカル環境で実行するための最低限の手順（依存ライブラリのインストール、環境変数の設定など）を記述してください。
     3. 上記手順で実行した場合に、どのようなログ出力や動作が期待されるか、一般的なシナリオを説明してください。

     確認事項: 必須設定項目（GitHubトークン、リポジトリ設定など）が適切に記述されていること。依存パッケージがインストールされていること。

     期待する出力: `config.toml`の雛形と、`main.py`をローカルで実行し、基本的な動作を確認するための手順書をmarkdown形式で出力してください。
     ```

3. [Issue #87](../issue-notes/87.md) 大幅な仕様変更のドッグフーディング - テストスイートのレビューと拡張
   - 最初の小さな一歩: `tests/test_config_rulesets.py`と`tests/test_pr_actions_rulesets_features.py`をレビューし、[Issue #93](../issue-notes/93.md)で指摘された`owner`フィールドの削除がこれらのテストに影響を与えないか確認する。
   - Agent実行プロンプ:
     ```
     対象ファイル: `tests/test_config_rulesets.py`, `tests/test_pr_actions_rulesets_features.py`, `src/gh_pr_phase_monitor/config.py` (参照用)

     実行内容:
     1. `tests/test_config_rulesets.py`および`tests/test_pr_actions_rulesets_features.py`を分析し、これらのテストが`[rulesets.repositories]`設定における`owner`フィールドの有無にどのように依存しているかを確認してください。
     2. `owner`フィールドが不要になった新しい仕様 ([Issue #93](../issue-notes/93.md)) に基づき、既存のテストコードが適切に機能するか、または更新が必要か評価してください。
     3. 必要であれば、新しい仕様に準拠するようテストコードの修正案を提案してください。

     確認事項: `src/gh_pr_phase_monitor/config.py`で`rulesets.repositories`がどのようにパースされるかを理解していること。

     期待する出力: 分析結果と、もし必要であればテストコードの修正案をmarkdown形式で出力してください。

---
Generated at: 2026-01-09 07:01:52 JST
