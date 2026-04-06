## ブラウザ自動化の制約

### Playwright/Seleniumは使用不可
- **理由**: GitHubの認証認可を通過できない
- **詳細**: 
  - curlやブラウザ自動化ツール単体では、認証済みセッションでGitHubのボタンにアクセスできない
  - リモートデバッグ接続（`--remote-debugging-port=9222`）を使用すれば既存セッションに接続可能だが、環境依存が大きく実用的でない
- **対応策**: 
  - PyAutoGUIによる画像認識（confidence=0.8）
  - OCRフォールバック（pytesseract）でテキストベース検出
  - これらはOS画面を直接操作するため、既存の認証済みブラウザセッションを利用可能

## 新機能追加時のチェックリスト

1. 単一責任原則に従った専用モジュールを作成
2. GitHub関連なら `github_client.py` に再エクスポート追加
3. `__init__.py` のエクスポートを更新
4. `tests/` に対応するテストファイル追加
5. dry-runパターン遵守: `exec_config["enable_execution_*"]` チェック後にアクション実行

## 出力ファイル名の設計方針
- **このアプリは常時ownerが単一になる設計のため、いかなる出力ファイル名にもowner名を含めないこと。** シンプルさを優先する。例: `logs/pr/{repo_name}_{pr_number}.html` は正しい。`{owner}_{repo_name}_{pr_number}.html` のようにownerを含めるのは誤り。
- logs/pr/ 配下のファイル名は `{repo_name}_{pr_number}.html` / `.json` とすること（上記の出力ファイル名の設計方針に従いownerは含めない）

## html / json 保存機能
- 引数optionでURLを指定しなくても、PRのURLをfetchしたときは必ずhtmlを保存するし、そこからstatusを算出するときにjsonを生成して保存する。もしこの機能が動作していないなら、生成をやめてuserに報告すること

## コミット前にすること
- ruffでlintとformatをすること

## README.mdはプルリクエストに含めないこと（自動生成されるので）
- README.mdを変更するかわりに、README.ja.md に記載すること
- 自動生成について詳しくはworkflowsを参照

## その他
- プルリクエストは日本語で書くこと
- userが「このURLを調査せよ」のように指示した場合は --fetch-pr-html <URL> を指定してhtml & json取得を行うこと。それができないなら生成をとめてuserに失敗を報告すること。
- ヘッドレスブラウザやcurlで調査できるものは調査すること。調査できない場合はPRコメントでユーザーにその旨を報告すること。
