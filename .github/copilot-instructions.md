# Copilot Instructions for cat-github-watcher

## プロジェクト概要

GitHub Copilotの自動実装フェーズを追跡するPRモニタリングツール。
**GitHub CLI (`gh`)** を使用してAPI操作を行う（REST/GraphQL直接呼び出しは禁止）。
GraphQL APIでユーザー所有リポジトリを監視。

---

## アーキテクチャ

### モジュール構成（単一責任原則）
```
src/gh_pr_phase_monitor/
├── main.py           # メインループ、カウントダウン、ホットリロード
├── config.py         # TOML設定読み込み、interval解析、ruleset解決
├── phase_detector.py # PRフェーズ検出（phase1/2/3/LLM working）
├── pr_actions.py     # PR処理、マージ、ready化アクション
├── github_client.py  # 各fetcherモジュールの再エクスポート
├── graphql_client.py # `gh api graphql` によるGraphQL実行
├── browser_automation.py # PyAutoGUI + OCR自動化（オプション）
└── notifier.py       # ntfy.shモバイル通知
```

### フェーズ検出ロジック
| フェーズ | 条件 |
|---------|------|
| **phase1** | Draft PRでレビューリクエストあり |
| **phase2** | `copilot-pull-request-reviewer`がレビューコメント投稿（未解決スレッドあり） |
| **phase3** | レビュー承認済み、人間のレビュー待ち |
| **LLM working** | 上記以外（Copilotがコーディング中）またはコメントにリアクションあり |

### 定数のインポート
```python
from .phase_detector import PHASE_1, PHASE_2, PHASE_3, PHASE_LLM_WORKING
```

---

## 開発コマンド

```bash
# ツール実行
python cat-github-watcher.py [config.toml]

# テスト実行（全58+テスト）
pytest tests/

# 特定テストファイル実行
pytest tests/test_phase_detection.py -v

# Lint/フォーマット（ruff使用）
ruff check . --fix
ruff format .
```

---

## テストパターン

- 外部依存（`subprocess`, `webbrowser`）は `unittest.mock.patch` でモック
- テスト用PRデータ必須フィールド: `isDraft`, `reviews`, `latestReviews`, `reviewRequests`, `repository`, `title`, `url`
- 各テストの`setup_method()`で状態トラッキングをリセット:
  ```python
  pr_actions._browser_opened.clear()
  pr_actions._notifications_sent.clear()
  ```

---

## 設定システム

- TOML形式、rulesetsでリポジトリ別設定
- interval解析: `"30s"`, `"1m"`, `"5m"`, `"1h"`, `"1d"` → 秒数
- 実行フラグは `[[rulesets]]` セクション内のみ（グローバル禁止）
- `resolve_execution_config_for_repo(config, owner, repo_name)` でマージ済み設定取得

---

## コーディング規約

1. **Dry-runがデフォルト**: rulesetsで明示的に有効化しない限り全アクション無効
2. **外部呼び出しは全て `gh` CLI経由**: `subprocess.run(["gh", ...])` パターン
3. **状態追跡はモジュールレベルset**: `_browser_opened`, `_notifications_sent`, `_merged_prs`
4. **ANSIカラー**: ターミナル出力に `colorize_phase()` と `Colors` クラス使用
5. **日本語ロケール**: 一部メッセージは日本語（例: `format_elapsed_time()` → `"3分20秒"`）

---

## 新機能追加時のチェックリスト

1. 単一責任原則に従った専用モジュールを作成
2. GitHub関連なら `github_client.py` に再エクスポート追加
3. `__init__.py` のエクスポートを更新
4. `tests/` に対応するテストファイル追加
5. dry-runパターン遵守: `exec_config["enable_execution_*"]` チェック後にアクション実行

---

## 外部依存

| 種別 | 依存 |
|------|------|
| **必須** | GitHub CLI（`gh auth login`で認証） |
| **オプション** | PyAutoGUI + pytesseract（ブラウザ自動化用） |
| **設定ファイル** | `config.toml`（ntfy.sh、rulesets、phase3_merge、assign_to_copilot）|

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

## README.mdは自動生成される
- README.mdはPRに含めないこと（自動生成されるので）
- README.mdを変更するかわりに、README.ja.md に記載すること
- 自動生成について詳しくはworkflowsを参照

## PRは日本語で記載する
- このリポジトリの主要な利用者は日本語話者であるため、PRは日本語で記載すること

## コミット前にすること
- ruffでlint/フォーマットすること
