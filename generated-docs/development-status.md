Last updated: 2026-01-13

# Development Status

## 現在のIssues
- [Issue #132](../issue-notes/132.md) は、LLM自動化によるレートリミット対策として、自動assignの並列数制御をTOMLで設定可能にする。
- [Issue #131](../issue-notes/131.md) は、DeepWikiへのプロジェクト登録に伴い、README.ja.mdにDeepWikiバッジを追加する作業。
- [Issue #87](../issue-notes/87.md) は、大規模な仕様変更後のシステム全体に対するドッグフーディングが必要。

## 次の一手候補
1. [Issue #131](../issue-notes/131.md): DeepWikiバッジをREADME.ja.mdに追加する
   - 最初の小さな一歩: DeepWikiのバッジのMarkdownコード（例: `[![DeepWiki](https://img.shields.io/badge/DeepWiki-blue)](https://deepwiki.com/cat-github-watcher)`）を決定し、`README.ja.md`の既存バッジの下に追記する。
   - Agent実行プロンプ:
     ```
     対象ファイル: `README.ja.md`

     実行内容: `README.ja.md`の先頭にある既存のバッジ（日本語/英語切り替えバッジ）の下に、DeepWikiへのリンクバッジを追加してください。バッジのテキストは「DeepWiki」とし、色は「blue」、リンク先URLは`https://deepwiki.com/cat-github-watcher`とします。

     確認事項: 既存のバッジのMarkdownフォーマットと整合性を保ち、新しいバッジのURLが正確であることを確認してください。

     期待する出力: 変更後の`README.ja.md`の内容をMarkdown形式で出力してください。
     ```

2. [Issue #132](../issue-notes/132.md): LLM自動assignの並列数制御を実装する
   - 最初の小さな一歩: `config.toml.example`に`[assign_to_copilot]`セクション内に`max_parallel_assign = 3`という新しい設定項目を追加し、`src/gh_pr_phase_monitor/config.py`でこの値を読み込む処理を追加する。
   - Agent実行プロンプト:
     ```
     対象ファイル: `config.toml.example`, `src/gh_pr_phase_monitor/config.py`

     実行内容: `config.toml.example`の`[assign_to_copilot]`セクションに、LLMへの同時割り当て数を制御するための新しい設定項目`max_parallel_assign = 3`（デフォルト値）を追加してください。また、`src/gh_pr_phase_monitor/config.py`において、この`max_parallel_assign`値をパースし、`AssignToCopilotConfig`クラスの属性としてアクセス可能にするための変更を加えてください。

     確認事項: TOMLの構文が正しく、`config.py`のConfigParserが新しい設定項目を適切に処理できることを確認してください。`max_parallel_assign`が整数型として読み込まれることを保証してください。

     期待する出力: 変更後の`config.toml.example`と`src/gh_pr_phase_monitor/config.py`の内容をMarkdown形式で出力してください。
     ```

3. [Issue #87](../issue-notes/87.md): 大幅な仕様変更後のドッグフーディング実施
   - 最初の小さな一歩: `cat-github-watcher.py`を現在の最新版で起動し、Dry-runモードで各機能が想定通りに動作するかをログ出力や表示内容から確認する。
   - Agent実行プロンプト:
     ```
     対象ファイル: なし (実行環境の監視)

     実行内容: `cat-github-watcher.py`を現在の最新コードベースと既存の`config.toml`（または`config.toml.example`からコピーしたもの）を使用して実行し、システムのドッグフーディングを実施してください。特に、PRのフェーズ判定、コメント投稿、通知（Dry-runメッセージ）、自動割り当て、自動マージ（Dry-runメッセージ）の各機能が、設定に基づいて期待通りに動作しているか、またはDry-runメッセージが正しく表示されているかを詳細に観察し、記録してください。

     確認事項: `config.toml`が適切に設定されていること、必要な認証情報（GitHub CLIなど）が利用可能であること、およびツールがエラーなく起動し継続的に実行されていることを確認してください。

     期待する出力: ドッグフーディング中に発見された問題点、改善提案、または期待通りに動作している機能の具体的なリストをMarkdown形式で出力してください。特に、各フェーズにおける具体的な出力（Dry-runメッセージ含む）を詳細に報告してください。
     ```

---
Generated at: 2026-01-13 07:01:44 JST
