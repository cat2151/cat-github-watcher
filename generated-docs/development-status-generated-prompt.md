Last updated: 2026-01-05

# 開発状況生成プロンプト（開発者向け）

## 生成するもの：
- 現在openされているissuesを3行で要約する
- 次の一手の候補を3つlistする
- 次の一手の候補3つそれぞれについて、極力小さく分解して、その最初の小さな一歩を書く

## 生成しないもの：
- 「今日のissue目標」などuserに提案するもの
  - ハルシネーションの温床なので生成しない
- ハルシネーションしそうなものは生成しない（例、無価値なtaskや新issueを勝手に妄想してそれをuserに提案する等）
- プロジェクト構造情報（来訪者向け情報のため、別ファイルで管理）

## 「Agent実行プロンプト」生成ガイドライン：
「Agent実行プロンプト」作成時は以下の要素を必ず含めてください：

### 必須要素
1. **対象ファイル**: 分析/編集する具体的なファイルパス
2. **実行内容**: 具体的な分析や変更内容（「分析してください」ではなく「XXXファイルのYYY機能を分析し、ZZZの観点でmarkdown形式で出力してください」）
3. **確認事項**: 変更前に確認すべき依存関係や制約
4. **期待する出力**: markdown形式での結果や、具体的なファイル変更

### Agent実行プロンプト例

**良い例（上記「必須要素」4項目を含む具体的なプロンプト形式）**:
```
対象ファイル: `.github/workflows/translate-readme.yml`と`.github/workflows/call-translate-readme.yml`

実行内容: 対象ファイルについて、外部プロジェクトから利用する際に必要な設定項目を洗い出し、以下の観点から分析してください：
1) 必須入力パラメータ（target-branch等）
2) 必須シークレット（GEMINI_API_KEY）
3) ファイル配置の前提条件（README.ja.mdの存在）
4) 外部プロジェクトでの利用時に必要な追加設定

確認事項: 作業前に既存のworkflowファイルとの依存関係、および他のREADME関連ファイルとの整合性を確認してください。

期待する出力: 外部プロジェクトがこの`call-translate-readme.yml`を導入する際の手順書をmarkdown形式で生成してください。具体的には：必須パラメータの設定方法、シークレットの登録手順、前提条件の確認項目を含めてください。
```

**避けるべき例**:
- callgraphについて調べてください
- ワークフローを分析してください
- issue-noteの処理フローを確認してください

## 出力フォーマット：
以下のMarkdown形式で出力してください：

```markdown
# Development Status

## 現在のIssues
[以下の形式で3行でオープン中のissuesを要約。issue番号を必ず書く]
- [1行目の説明]
- [2行目の説明]
- [3行目の説明]

## 次の一手候補
1. [候補1のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```

2. [候補2のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```

3. [候補3のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```
```


# 開発状況情報
- 以下の開発状況情報を参考にしてください。
- Issue番号を記載する際は、必ず [Issue #番号](../issue-notes/番号.md) の形式でMarkdownリンクとして記載してください。

## プロジェクトのファイル一覧
- .editorconfig
- .github/actions-tmp/.github/workflows/call-callgraph.yml
- .github/actions-tmp/.github/workflows/call-daily-project-summary.yml
- .github/actions-tmp/.github/workflows/call-issue-note.yml
- .github/actions-tmp/.github/workflows/call-rust-windows-check.yml
- .github/actions-tmp/.github/workflows/call-translate-readme.yml
- .github/actions-tmp/.github/workflows/callgraph.yml
- .github/actions-tmp/.github/workflows/check-recent-human-commit.yml
- .github/actions-tmp/.github/workflows/daily-project-summary.yml
- .github/actions-tmp/.github/workflows/issue-note.yml
- .github/actions-tmp/.github/workflows/rust-windows-check.yml
- .github/actions-tmp/.github/workflows/translate-readme.yml
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/callgraph.ql
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/codeql-pack.lock.yml
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/qlpack.yml
- .github/actions-tmp/.github_automation/callgraph/config/example.json
- .github/actions-tmp/.github_automation/callgraph/docs/callgraph.md
- .github/actions-tmp/.github_automation/callgraph/presets/callgraph.js
- .github/actions-tmp/.github_automation/callgraph/presets/style.css
- .github/actions-tmp/.github_automation/callgraph/scripts/analyze-codeql.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/callgraph-utils.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/check-codeql-exists.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/check-node-version.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/common-utils.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/copy-commit-results.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/extract-sarif-info.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/find-process-results.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/generate-html-graph.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/generateHTML.cjs
- .github/actions-tmp/.github_automation/check_recent_human_commit/scripts/check-recent-human-commit.cjs
- .github/actions-tmp/.github_automation/project_summary/docs/daily-summary-setup.md
- .github/actions-tmp/.github_automation/project_summary/prompts/development-status-prompt.md
- .github/actions-tmp/.github_automation/project_summary/prompts/project-overview-prompt.md
- .github/actions-tmp/.github_automation/project_summary/scripts/ProjectSummaryCoordinator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/GitUtils.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/IssueTracker.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/generate-project-summary.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/CodeAnalyzer.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectAnalysisOrchestrator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectDataCollector.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectDataFormatter.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectOverviewGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/BaseGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/FileSystemUtils.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/ProjectFileUtils.cjs
- .github/actions-tmp/.github_automation/translate/docs/TRANSLATION_SETUP.md
- .github/actions-tmp/.github_automation/translate/scripts/translate-readme.cjs
- .github/actions-tmp/.gitignore
- .github/actions-tmp/.vscode/settings.json
- .github/actions-tmp/LICENSE
- .github/actions-tmp/README.ja.md
- .github/actions-tmp/README.md
- .github/actions-tmp/_config.yml
- .github/actions-tmp/generated-docs/callgraph.html
- .github/actions-tmp/generated-docs/callgraph.js
- .github/actions-tmp/generated-docs/development-status-generated-prompt.md
- .github/actions-tmp/generated-docs/development-status.md
- .github/actions-tmp/generated-docs/project-overview-generated-prompt.md
- .github/actions-tmp/generated-docs/project-overview.md
- .github/actions-tmp/generated-docs/style.css
- .github/actions-tmp/googled947dc864c270e07.html
- .github/actions-tmp/issue-notes/10.md
- .github/actions-tmp/issue-notes/11.md
- .github/actions-tmp/issue-notes/12.md
- .github/actions-tmp/issue-notes/13.md
- .github/actions-tmp/issue-notes/14.md
- .github/actions-tmp/issue-notes/15.md
- .github/actions-tmp/issue-notes/16.md
- .github/actions-tmp/issue-notes/17.md
- .github/actions-tmp/issue-notes/18.md
- .github/actions-tmp/issue-notes/19.md
- .github/actions-tmp/issue-notes/2.md
- .github/actions-tmp/issue-notes/20.md
- .github/actions-tmp/issue-notes/21.md
- .github/actions-tmp/issue-notes/22.md
- .github/actions-tmp/issue-notes/23.md
- .github/actions-tmp/issue-notes/24.md
- .github/actions-tmp/issue-notes/25.md
- .github/actions-tmp/issue-notes/26.md
- .github/actions-tmp/issue-notes/27.md
- .github/actions-tmp/issue-notes/28.md
- .github/actions-tmp/issue-notes/29.md
- .github/actions-tmp/issue-notes/3.md
- .github/actions-tmp/issue-notes/30.md
- .github/actions-tmp/issue-notes/4.md
- .github/actions-tmp/issue-notes/7.md
- .github/actions-tmp/issue-notes/8.md
- .github/actions-tmp/issue-notes/9.md
- .github/actions-tmp/package-lock.json
- .github/actions-tmp/package.json
- .github/actions-tmp/src/main.js
- .github/workflows/call-daily-project-summary.yml
- .github/workflows/call-issue-note.yml
- .github/workflows/call-translate-readme.yml
- .gitignore
- .vscode/settings.json
- LICENSE
- README.ja.md
- README.md
- STRUCTURE.md
- _config.yml
- cat-github-watcher.py
- config.toml.example
- generated-docs/project-overview-generated-prompt.md
- pytest.ini
- ruff.toml
- src/__init__.py
- src/gh_pr_phase_monitor/__init__.py
- src/gh_pr_phase_monitor/colors.py
- src/gh_pr_phase_monitor/comment_fetcher.py
- src/gh_pr_phase_monitor/comment_manager.py
- src/gh_pr_phase_monitor/config.py
- src/gh_pr_phase_monitor/github_auth.py
- src/gh_pr_phase_monitor/github_client.py
- src/gh_pr_phase_monitor/graphql_client.py
- src/gh_pr_phase_monitor/issue_fetcher.py
- src/gh_pr_phase_monitor/main.py
- src/gh_pr_phase_monitor/notifier.py
- src/gh_pr_phase_monitor/phase_detector.py
- src/gh_pr_phase_monitor/pr_actions.py
- src/gh_pr_phase_monitor/pr_fetcher.py
- src/gh_pr_phase_monitor/repository_fetcher.py
- tests/test_integration_issue_fetching.py
- tests/test_interval_parsing.py
- tests/test_issue_fetching.py
- tests/test_no_open_prs_issue_display.py
- tests/test_notification.py
- tests/test_phase_detection.py
- tests/test_post_comment.py
- tests/test_pr_actions.py

## 現在のオープンIssues
## [Issue #65](../issue-notes/65.md): Replace gh comment with browser-based issue assignment
The previous implementation posted "Assign to Copilot" comments via `gh issue comment`, which only incremented assignee count without actually assigning Copilot, polluting issue metadata.

## Changes

**Core implementation** (`issue_fetcher.py`):
- Replace `subprocess.run(['gh', 'issue', 'comment', ...
ラベル: 
--- issue-notes/65.md の内容 ---

```markdown

```

## [Issue #64](../issue-notes/64.md): Assign to copilotを検証した結果がNG。assignees人数だけ増えて、copilotは実際にはアサインされない、となりissue情報が汚れてuserが混乱した。機能を変更し、tomlでenableのときのみ動作し、ghコマンドではなく、なんらかのブラウザ自動操縦方法で、issueを開いてAssign to Copilotボタンを押させる方法で実現とする

ラベル: 
--- issue-notes/64.md の内容 ---

```markdown

```

## [Issue #57](../issue-notes/57.md): デフォルトはdry run動作とする。tomlに enable_execution = true を書いたときだけ、phase1,phase2,phase3の検知後に「実際にPRに書き込みや、ntfy通知」とする

ラベル: good first issue
--- issue-notes/57.md の内容 ---

```markdown

```

## [Issue #39](../issue-notes/39.md): issue10件表示機能について、リポジトリlist表示を削除し、authorとupdatedを削除し、表示は10件でなく5件にして、userの認知負荷を下げる

ラベル: good first issue
--- issue-notes/39.md の内容 ---

```markdown

```

## [Issue #32](../issue-notes/32.md): 「Posting comment for phase2... / Comment already exists, skipping / Comment posted successfully」と表示され、userが混乱する。skippingのあとはpostedを表示しないようにする

ラベル: good first issue
--- issue-notes/32.md の内容 ---

```markdown

```

## [Issue #21](../issue-notes/21.md): 前回とまったく同じ表示内容であれば、表示内容を変更し、「現在、検知してから3分20秒経過」のような表示をする。さらに、その表示時と、待ち時間中は1秒ごと、エスケープシーケンスを利用し、前回の「3分19秒経過」を消して「3分20秒経過」のように書き換える

ラベル: good first issue
--- issue-notes/21.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/2.md
```md
{% raw %}
# issue GitHub Actions「関数コールグラフhtmlビジュアライズ生成」を共通ワークフロー化する #2
[issues #2](https://github.com/cat2151/github-actions/issues/2)


# prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlファイルを、以下の2つのファイルに分割してください。
1. 共通ワークフロー       cat2151/github-actions/.github/workflows/callgraph_enhanced.yml
2. 呼び出し元ワークフロー cat2151/github-actions/.github/workflows/call-callgraph_enhanced.yml
まずplanしてください
```

# 結果
- indent
    - linter？がindentのエラーを出しているがyml内容は見た感じOK
    - テキストエディタとagentの相性問題と判断する
    - 別のテキストエディタでsaveしなおし、テキストエディタをreload
    - indentのエラーは解消した
- LLMレビュー
    - agent以外の複数のLLMにレビューさせる
    - prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
以下の2つのファイルをレビューしてください。最優先で、エラーが発生するかどうかだけレビューしてください。エラー以外の改善事項のチェックをするかわりに、エラー発生有無チェックに最大限注力してください。

--- 共通ワークフロー

# GitHub Actions Reusable Workflow for Call Graph Generation
name: Generate Call Graph

# TODO Windowsネイティブでのtestをしていた名残が残っているので、今後整理していく。今はWSL act でtestしており、Windowsネイティブ環境依存問題が解決した
#  ChatGPTにレビューさせるとそこそこ有用そうな提案が得られたので、今後それをやる予定
#  agentに自己チェックさせる手も、セカンドオピニオンとして選択肢に入れておく

on:
  workflow_call:

jobs:
  check-commits:
    runs-on: ubuntu-latest
    outputs:
      should-run: ${{ steps.check.outputs.should-run }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 50 # 過去のコミットを取得

      - name: Check for user commits in last 24 hours
        id: check
        run: |
          node .github/scripts/callgraph_enhanced/check-commits.cjs

  generate-callgraph:
    needs: check-commits
    if: needs.check-commits.outputs.should-run == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      security-events: write
      actions: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set Git identity
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

      - name: Remove old CodeQL packages cache
        run: rm -rf ~/.codeql/packages

      - name: Check Node.js version
        run: |
          node .github/scripts/callgraph_enhanced/check-node-version.cjs

      - name: Install CodeQL CLI
        run: |
          wget https://github.com/github/codeql-cli-binaries/releases/download/v2.22.1/codeql-linux64.zip
          unzip codeql-linux64.zip
          sudo mv codeql /opt/codeql
          echo "/opt/codeql" >> $GITHUB_PATH

      - name: Install CodeQL query packs
        run: |
          /opt/codeql/codeql pack install .github/codeql-queries

      - name: Check CodeQL exists
        run: |
          node .github/scripts/callgraph_enhanced/check-codeql-exists.cjs

      - name: Verify CodeQL Configuration
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs verify-config

      - name: Remove existing CodeQL DB (if any)
        run: |
          rm -rf codeql-db

      - name: Perform CodeQL Analysis
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs analyze

      - name: Check CodeQL Analysis Results
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs check-results

      - name: Debug CodeQL execution
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs debug

      - name: Wait for CodeQL results
        run: |
          node -e "setTimeout(()=>{}, 10000)"

      - name: Find and process CodeQL results
        run: |
          node .github/scripts/callgraph_enhanced/find-process-results.cjs

      - name: Generate HTML graph
        run: |
          node .github/scripts/callgraph_enhanced/generate-html-graph.cjs

      - name: Copy files to generated-docs and commit results
        run: |
          node .github/scripts/callgraph_enhanced/copy-commit-results.cjs

--- 呼び出し元
# 呼び出し元ワークフロー: call-callgraph_enhanced.yml
name: Call Call Graph Enhanced

on:
  schedule:
    # 毎日午前5時(JST) = UTC 20:00前日
    - cron: '0 20 * * *'
  workflow_dispatch:

jobs:
  call-callgraph-enhanced:
    # uses: cat2151/github-actions/.github/workflows/callgraph_enhanced.yml
    uses: ./.github/workflows/callgraph_enhanced.yml # ローカルでのテスト用
```

# レビュー結果OKと判断する
- レビュー結果を人力でレビューした形になった

# test
- #4 同様にローカル WSL + act でtestする
- エラー。userのtest設計ミス。
  - scriptの挙動 : src/ がある前提
  - 今回の共通ワークフローのリポジトリ : src/ がない
  - 今回testで実現したいこと
    - 仮のソースでよいので、関数コールグラフを生成させる
  - 対策
    - src/ にダミーを配置する
- test green
  - ただしcommit pushはしてないので、html内容が0件NG、といったケースの検知はできない
  - もしそうなったら別issueとしよう

# test green

# commit用に、yml 呼び出し元 uses をlocal用から本番用に書き換える

# closeとする
- もしhtml内容が0件NG、などになったら、別issueとするつもり

{% endraw %}
```

### .github/actions-tmp/issue-notes/21.md
```md
{% raw %}
# issue project-summary の development-status 生成時、project-overviewが生成済みのproject-overview.mdもpromptに添付、を試す #21
[issues #21](https://github.com/cat2151/github-actions/issues/21)

# 何が困るの？
- project-overview.mdがpromptに添付されていたほうが、Geminiの生成品質が改善できる可能性がある。
    - メリットは、ファイル一覧、関数一覧、をGeminiにわたせること

# 検討事項
- 課題、その一覧に付記されている「ファイルや関数の要約」は、Geminiが「ファイル名や関数名を元に生成しただけ」で、「ファイル内容や関数内容を参照せずに生成した」可能性が高い
    - 対策、project-overview.mdに依存しない。
        - 方法、新規関数をagentに実装させる
            - 新規関数で、ファイル一覧と関数一覧を生成する
        - 根拠、そのほうが、シンプルに目的を達成できる可能性が高そう。
        - 根拠、project-overview.mdだと、不具合として.github 配下のymlがlistに含まれておらず、ymlに関するissue、に関する生成、をするとき不具合の可能性がありそう。そういった、別機能の不具合に影響されがち。
- 課題、早期に実施したほうが毎日好影響が出る可能性がある
    - 対策、上記検討事項の対処は後回しにして、先に実装してみる
    - agentに投げる
- 課題、ProjectSummaryCoordinator をみたところ、並列処理されている
    - なので、project-overview.mdを参照したいときに、まだ生成されていない、という可能性が高い
    - 対策、前述の、新規関数で、ファイル一覧と関数一覧を生成させる

# agentに投げるための整理
- 編集対象ファイル
    - prompt
        - .github_automation/project_summary/prompts/development-status-prompt.md
        - 編集内容
            - projectのファイル一覧を埋め込む用の、プレースホルダーを追加する
    - source
        - .github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
        - 編集内容
            - projectのファイル一覧を生成する関数、を実装し、
            - それを前述のプレースホルダーに埋め込む

# agentに投げて実装させた

# test結果
- 以下が不要
    - .git/
    - node_modules/

# どうする？
- agentに上記を変更させた
- testする

# 結果
- test greenとなった

# まとめ
- issueのtitleからは仕様変更した。
    - projectのfile一覧をpromptに含める、とした。
    - そのほうがpromptとして、よい生成結果が期待できる、と判断した。
- test greenとなった

# closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/4.md
```md
{% raw %}
# issue GitHub Actions「project概要生成」を共通ワークフロー化する #4
[issues #4](https://github.com/cat2151/github-actions/issues/4)

# prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlファイルを、以下の2つのファイルに分割してください。
1. 共通ワークフロー       cat2151/github-actions/.github/workflows/daily-project-summary.yml
2. 呼び出し元ワークフロー cat2151/github-actions/.github/workflows/call-daily-project-summary.yml
まずplanしてください
```

# 結果、あちこちハルシネーションのあるymlが生成された
- agentの挙動があからさまにハルシネーション
    - インデントが修正できない、「失敗した」という
    - 構文誤りを認識できない
- 人力で修正した

# このagentによるセルフレビューが信頼できないため、別のLLMによるセカンドオピニオンを試す
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
以下の2つのファイルをレビューしてください。最優先で、エラーが発生するかどうかだけレビューてください。エラー以外の改善事項のチェックをするかわりに、エラー発生有無チェックに最大限注力してください。

--- 呼び出し元

name: Call Daily Project Summary

on:
  schedule:
    # 日本時間 07:00 (UTC 22:00 前日)
    - cron: '0 22 * * *'
  workflow_dispatch:

jobs:
  call-daily-project-summary:
    uses: cat2151/github-actions/.github/workflows/daily-project-summary.yml
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

--- 共通ワークフロー
name: Daily Project Summary
on:
  workflow_call:

jobs:
  generate-summary:
    runs-on: ubuntu-latest

    permissions:
      contents: write
      issues: read
      pull-requests: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0  # 履歴を取得するため

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          # 一時的なディレクトリで依存関係をインストール
          mkdir -p /tmp/summary-deps
          cd /tmp/summary-deps
          npm init -y
          npm install @google/generative-ai @octokit/rest
          # generated-docsディレクトリを作成
          mkdir -p $GITHUB_WORKSPACE/generated-docs

      - name: Generate project summary
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          NODE_PATH: /tmp/summary-deps/node_modules
        run: |
          node .github/scripts/generate-project-summary.cjs

      - name: Check for generated summaries
        id: check_summaries
        run: |
          if [ -f "generated-docs/project-overview.md" ] && [ -f "generated-docs/development-status.md" ]; then
            echo "summaries_generated=true" >> $GITHUB_OUTPUT
          else
            echo "summaries_generated=false" >> $GITHUB_OUTPUT
          fi

      - name: Commit and push summaries
        if: steps.check_summaries.outputs.summaries_generated == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          # package.jsonの変更のみリセット（generated-docsは保持）
          git restore package.json 2>/dev/null || true
          # サマリーファイルのみを追加
          git add generated-docs/project-overview.md
          git add generated-docs/development-status.md
          git commit -m "Update project summaries (overview & development status)"
          git push

      - name: Summary generation result
        run: |
          if [ "${{ steps.check_summaries.outputs.summaries_generated }}" == "true" ]; then
            echo "✅ Project summaries updated successfully"
            echo "📊 Generated: project-overview.md & development-status.md"
          else
            echo "ℹ️ No summaries generated (likely no user commits in the last 24 hours)"
          fi
```

# 上記promptで、2つのLLMにレビューさせ、合格した

# 細部を、先行する2つのymlを参照に手直しした

# ローカルtestをしてからcommitできるとよい。方法を検討する
- ローカルtestのメリット
    - 素早く修正のサイクルをまわせる
    - ムダにgit historyを汚さない
        - これまでの事例：「実装したつもり」「エラー。修正したつもり」「エラー。修正したつもり」...（以降エラー多数）
- 方法
    - ※検討、WSL + act を環境構築済みである。test可能であると判断する
    - 呼び出し元のURLをコメントアウトし、相対パス記述にする
    - ※備考、テスト成功すると結果がcommit pushされる。それでよしとする
- 結果
    - OK
    - secretsを簡略化できるか試した、できなかった、現状のsecrets記述が今わかっている範囲でベストと判断する
    - OK

# test green

# commit用に、yml 呼び出し元 uses をlocal用から本番用に書き換える

# closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/7.md
```md
{% raw %}
# issue issue note生成できるかのtest用 #7
[issues #7](https://github.com/cat2151/github-actions/issues/7)

- 生成できた
- closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/9.md
```md
{% raw %}
# issue 関数コールグラフhtmlビジュアライズが0件なので、原因を可視化する #9
[issues #9](https://github.com/cat2151/github-actions/issues/9)

# agentに修正させたり、人力で修正したりした
- agentがハルシネーションし、いろいろ根の深いバグにつながる、エラー隠蔽などを仕込んでいたため、検知が遅れた
- 詳しくはcommit logを参照のこと
- WSL + actの環境を少し変更、act起動時のコマンドライン引数を変更し、generated-docsをmountする（ほかはデフォルト挙動であるcpだけにする）ことで、デバッグ情報をコンテナ外に出力できるようにし、デバッグを効率化した

# test green

# closeとする

{% endraw %}
```

### src/gh_pr_phase_monitor/issue_fetcher.py
```py
{% raw %}
"""
Issue fetching module for GitHub issues
"""

import json
import subprocess
from typing import Any, Dict, List, Optional

from .graphql_client import execute_graphql_query

# GraphQL pagination constants
REPOSITORIES_BATCH_SIZE = 10
ISSUES_PER_REPO = 50


def get_issues_from_repositories(repos: List[Dict[str, Any]], limit: int = 10, labels: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Get issues from multiple repositories, sorted by timestamp descending

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys
        limit: Maximum number of issues to return (default: 10)
        labels: Optional list of label names to filter by (e.g., ["good first issue"])

    Returns:
        List of issue data sorted by updatedAt timestamp in descending order
    """
    if not repos:
        return []

    # Build GraphQL query to fetch issues from all repositories
    # We'll batch repositories to avoid overly complex queries
    all_issues = []

    for i in range(0, len(repos), REPOSITORIES_BATCH_SIZE):
        batch = repos[i : i + REPOSITORIES_BATCH_SIZE]

        # Build query fragments for each repository
        repo_queries = []
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_name = repo["name"]
            owner = repo["owner"]

            # Escape values to prevent GraphQL injection
            owner_literal = json.dumps(owner)
            repo_name_literal = json.dumps(repo_name)

            # Build labels filter if provided
            labels_filter = ""
            if labels:
                labels_json = json.dumps(labels)
                labels_filter = f", labels: {labels_json}"

            # Fetch up to ISSUES_PER_REPO issues per repository (sorted by updated time)
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              issues(first: {ISSUES_PER_REPO}, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}{labels_filter}) {{
                nodes {{
                  title
                  url
                  number
                  createdAt
                  updatedAt
                  author {{
                    login
                  }}
                  labels(first: 10) {{
                    nodes {{
                      name
                    }}
                  }}
                }}
              }}
            }}
            """
            repo_queries.append(repo_query)

        # Combine all repository queries
        full_query = f"""
        query {{
          {" ".join(repo_queries)}
        }}
        """

        # Execute GraphQL query
        data = execute_graphql_query(full_query)

        # Extract issue data from response
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_data = data.get("data", {}).get(alias, {})

            if repo_data:
                issues = repo_data.get("issues", {}).get("nodes", [])
                repo_name = repo_data.get("name", repo["name"])
                owner = repo_data.get("owner", {}).get("login", repo["owner"])

                # Add repository info to each issue
                for issue in issues:
                    # Handle null author
                    author_data = issue.get("author")
                    if author_data is None:
                        author = {"login": "[deleted]"}
                    else:
                        author = {"login": author_data.get("login", "")}

                    # Extract label names
                    label_nodes = issue.get("labels", {}).get("nodes", [])
                    label_names = [label.get("name", "") for label in label_nodes]

                    issue_with_repo = {
                        "title": issue.get("title", ""),
                        "url": issue.get("url", ""),
                        "number": issue.get("number", 0),
                        "createdAt": issue.get("createdAt", ""),
                        "updatedAt": issue.get("updatedAt", ""),
                        "author": author,
                        "labels": label_names,
                        "repository": {"name": repo_name, "owner": owner},
                    }
                    all_issues.append(issue_with_repo)

    # Sort all issues by updatedAt timestamp in descending order
    all_issues.sort(key=lambda x: x["updatedAt"], reverse=True)

    # Return top N issues
    return all_issues[:limit]


def assign_issue_to_copilot(issue: Dict[str, Any]) -> bool:
    """Assign an issue to GitHub Copilot by posting an 'Assign to Copilot' comment

    Args:
        issue: Issue dictionary with 'repository' (name, owner), 'number' fields

    Returns:
        True if assignment was successful, False otherwise
    """
    # Validate that the issue dictionary contains the required fields before accessing them
    if "repository" not in issue or "number" not in issue:
        print("  ✗ Invalid issue data: missing required fields")
        return False

    repository = issue["repository"]
    if not isinstance(repository, dict) or "name" not in repository or "owner" not in repository:
        print("  ✗ Invalid issue data: missing repository fields")
        return False

    repo_name = repository["name"]
    owner = repository["owner"]
    issue_number = issue["number"]

    # Post a comment "Assign to Copilot" which triggers GitHub's workflow for Copilot assignment
    try:
        cmd = [
            "gh",
            "issue",
            "comment",
            str(issue_number),
            "--repo",
            f"{owner}/{repo_name}",
            "--body",
            "Assign to Copilot",
        ]

        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=30,  # 30 second timeout for the gh command
        )

        print(f"  ✓ Assigned issue #{issue_number} to Copilot in {owner}/{repo_name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to assign issue #{issue_number} to Copilot: {e}")
        if e.stderr:
            print(f"    stderr: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout while assigning issue #{issue_number} to Copilot")
        return False

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
7763490 Merge pull request #61 from cat2151/copilot/add-condition-for-no-open-prs
356725f Merge pull request #63 from cat2151/copilot/fix-phase-detection-error
5899d99 Address code review: clarify empty body in PR 61 test
c9e5821 Fix phase detection for PR 61: treat COMMENTED reviews optimistically
b5189e9 Initial plan
05a5bd6 Auto-translate README.ja.md to README.md [auto]
d3bc231 Update GitHub Copilot message in Japanese README
66b4807 Remove redundant separator lines in display_issues_from_repos_without_prs
ed45387 Auto-translate README.ja.md to README.md [auto]
576662b Update ntfy.sh topic name instruction in README

### 変更されたファイル:
README.ja.md
README.md
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/phase_detector.py
tests/test_no_open_prs_issue_display.py
tests/test_phase_detection.py


---
Generated at: 2026-01-05 07:01:26 JST
