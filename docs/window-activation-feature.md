# ウィンドウ活性化機能 (Window Activation Feature)

## 概要

PyAutoGUIによる自動ボタンクリック機能において、ブラウザウィンドウが裏で開いてアクティブにならない問題を解決するため、ボタンをクリックする前にウィンドウをアクティブ化する機能を実装しました。

## 問題

- 自動assignが失敗する
- ブラウザウィンドウが裏で開いてしまい、アクティブになっていない
- PyAutoGUIはアクティブでないウィンドウのボタンをクリックできない

## 解決策

1. ブラウザを開く
2. 設定された待機時間の後、1秒待つ
3. TOMLで指定したtitleのウィンドウをアクティブにする
4. ボタンをクリックする

## 設定方法

`config.toml` の `[assign_to_copilot]` または `[phase3_merge]` セクションに `window_title` を追加します：

```toml
[assign_to_copilot]
wait_seconds = 2
window_title = "GitHub"  # ウィンドウタイトルに "GitHub" を含むウィンドウをアクティブ化

[phase3_merge]
comment = "..."
automated = false
wait_seconds = 10
window_title = "GitHub"  # ウィンドウタイトルに "GitHub" を含むウィンドウをアクティブ化
```

## 依存関係

`pygetwindow` ライブラリが必要です：

```bash
pip install -r requirements-automation.txt
```

または

```bash
pip install pygetwindow
```

## 動作

1. **部分一致**: ウィンドウタイトルの部分一致で検索します（例: "GitHub" は "GitHub - Issues" や "github.com - Google Chrome" にマッチ）
2. **大文字小文字を区別しない**: "GitHub" と "github" は同じように扱われます
3. **最小化されたウィンドウの復元**: ウィンドウが最小化されている場合、自動的に復元してからアクティブ化します
4. **Fail-fast原則**: `window_title`が設定されているにもかかわらずpygetwindowが利用できない場合、アプリケーションはエラーメッセージを表示して終了します（サイレント失敗を防ぎ、設定ミスを早期に検出）

## 注意事項

- `window_title` が設定されていない場合、ウィンドウの活性化はスキップされます（下位互換性）
- **重要**: `window_title`を設定した場合、pygetwindowライブラリは必須です。ライブラリがインストールされていない場合、アプリケーションはエラーで終了します
- ウィンドウが見つからない場合、警告が表示されますが処理は継続されます

## テスト

```bash
# ウィンドウ活性化機能のテスト
pytest tests/test_browser_automation.py::TestActivateWindowByTitle -v

# 統合テスト
pytest tests/test_browser_automation.py::TestAssignWithWindowActivation -v
pytest tests/test_browser_automation.py::TestMergeWithWindowActivation -v
```

## トラブルシューティング

### ウィンドウが見つからない

ログに「No window found with title containing: 'XXX'」と表示される場合：

1. ブラウザが実際に開いているか確認
2. `window_title` の設定が正しいか確認（部分一致なので、短い文字列でも可）
3. 利用可能なウィンドウのリストがログに表示されるので、適切なタイトルを選択

### pygetwindowが利用できない

`window_title`を設定しているにもかかわらず、以下のエラーが表示される場合：

```
ERROR: PyGetWindow library is not available
```

**解決方法**：

```bash
pip install -r requirements-automation.txt
```

または

```bash
pip install pygetwindow
```

**注意**: このエラーはfail-fast原則に基づいて設計されています。`window_title`を設定した場合、pygetwindowは必須です。ライブラリがない状態で実行を継続すると、ボタンクリックが失敗し、サイレント失敗につながるためです。

### Linux環境での注意

pygetwindowはLinux環境では追加のセットアップが必要な場合があります。Xorg環境が必要です。

## 実装の詳細

- `browser_automation.py` の `_activate_window_by_title()` 関数が実装されています
- `assign_issue_to_copilot_automated()` と `merge_pr_automated()` がウィンドウ活性化をサポートしています
- ボタンクリックの1秒前にウィンドウを活性化します
