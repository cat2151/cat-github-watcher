# ボタン検出の改善

## 概要

このドキュメントは、自動assignボタン認識の失敗に対応するために実装された改善について説明します。

## 問題

自動化機能（PyAutoGUIを使用した画像認識）でボタンが検出できない問題が発生していました。

### 原因

- ボタン画像のわずかな違い（サブピクセルレンダリング）
- ボタンの枠に対して文字の位置がわずかに異なる
- 結果として、0.8の一致度でも認識が失敗する

## 実装した解決策

### 1. OCRベースのフォールバック検出

画像認識が失敗した場合、OCR（光学文字認識）を使用してボタンのテキストを直接検出します。

**利点:**
- サブピクセルレンダリングの違いに対して頑健
- ボタンの見た目が変わっても、テキストが同じなら検出可能
- DPIスケーリングやテーマの変更に対応

**動作:**
1. 画像認識が失敗
2. 自動的にOCR検出を試行
3. 「Assign to Copilot」などのテキストを画面上から検出
4. テキスト周辺のボタン領域をクリック

**設定:**
```toml
[assign_to_copilot]
enable_ocr_detection = true  # デフォルト: true
```

**必要な依存関係:**
```bash
# システムレベル（OCRエンジン）
# Windows
choco install tesseract

# macOS
brew install tesseract

# Linux
apt-get install tesseract-ocr

# Pythonパッケージ
pip install pytesseract
```

### 2. 強化されたデバッグ機能

画像認識が失敗した場合、詳細なデバッグ情報を自動保存します。

**保存される情報:**
- 失敗時の画面全体のスクリーンショット
- 低い信頼度で見つかった候補領域（最大3つ）
  - 各候補の画像（クロップされた領域）
  - 座標、サイズ、使用された信頼度
- JSON形式のメタデータ

**候補検出の信頼度:**
```python
# 元の信頼度で失敗した場合、以下の信頼度で候補を検索
DEBUG_CANDIDATE_CONFIDENCE_THRESHOLDS = [0.7, 0.6, 0.5]
```

**デバッグファイルの例:**
```
debug_screenshots/
├── assign_to_copilot_fail_20240203_123456_789012.png    # 画面全体
├── assign_to_copilot_candidate_20240203_123456_789012_1.png  # 候補1
├── assign_to_copilot_candidate_20240203_123456_789012_2.png  # 候補2
└── assign_to_copilot_fail_20240203_123456_789012.json   # メタデータ
```

**JSONメタデータの例:**
```json
{
  "button_name": "assign_to_copilot",
  "timestamp": "2024-02-03T12:34:56.789012",
  "confidence": 0.8,
  "screenshot_path": "debug_screenshots/assign_to_copilot_fail_20240203_123456_789012.png",
  "template_screenshot": "screenshots/assign_to_copilot.png",
  "candidates_found": 2,
  "candidates": [
    {
      "confidence_used": 0.7,
      "left": 100,
      "top": 50,
      "width": 200,
      "height": 30,
      "image_path": "debug_screenshots/assign_to_copilot_candidate_20240203_123456_789012_1.png"
    }
  ]
}
```

## 使用方法

### 基本設定

OCRフォールバックは**デフォルトで有効**です。追加の設定は不要です。

```toml
[[rulesets]]
repositories = ["my-repo"]
assign_good_first_old = true

[assign_to_copilot]
wait_seconds = 10
confidence = 0.8
# enable_ocr_detection = true  # デフォルトで有効
```

### OCRを無効にする場合

画像認識のみを使用したい場合:

```toml
[assign_to_copilot]
enable_ocr_detection = false
```

### デバッグディレクトリの変更

```toml
[assign_to_copilot]
debug_dir = "my_debug_folder"
```

## トラブルシューティング

### OCRが機能しない

1. tesseract-ocrがインストールされているか確認:
   ```bash
   tesseract --version
   ```

2. pytesseractがインストールされているか確認:
   ```bash
   pip list | grep pytesseract
   ```

3. デバッグログを確認:
   ```
   → Attempting OCR-based detection for 'Assign to Copilot' button...
   ✗ Text 'Assign to Copilot' not found using OCR
   ```

### デバッグ情報を使用した分析

1. `debug_screenshots/`ディレクトリを確認
2. JSONファイルで候補が見つかっているか確認
3. 候補画像を確認して、ボタンが正しく検出されているか確認
4. 必要に応じて信頼度を調整:
   ```toml
   [assign_to_copilot]
   confidence = 0.7  # より低い値を試す
   ```

## パフォーマンスへの影響

- **画像認識が成功した場合**: 影響なし（従来通り）
- **画像認識が失敗した場合**:
  - デバッグ情報の保存: +1-2秒
  - OCR検出: +2-5秒（画面サイズとテキスト量に依存）

合計で最大7秒程度の追加時間ですが、これは画像認識が失敗した場合のみです。

## 設定例

### 推奨設定（OCR有効）

```toml
[[rulesets]]
repositories = ["my-repo"]
assign_good_first_old = true

[assign_to_copilot]
wait_seconds = 10
confidence = 0.8
enable_ocr_detection = true  # 明示的に有効化（デフォルトでも有効）
debug_dir = "debug_screenshots"
```

### 高速化優先（OCR無効）

```toml
[assign_to_copilot]
enable_ocr_detection = false
confidence = 0.7  # より低い信頼度で画像認識を試行
```

## 今後の改善予定

- [ ] EasyOCRなど、他のOCRエンジンのサポート
- [ ] 候補領域の自動選択ロジックの改善
- [ ] HTML検出の安定化
- [ ] ボタン検出のキャッシュ機能

## 関連ドキュメント

- [README.ja.md](../README.ja.md) - メインドキュメント
- [browser-automation-approaches.md](browser-automation-approaches.md) - ブラウザ自動化の実装方法
