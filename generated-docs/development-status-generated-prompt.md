Last updated: 2026-01-07

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
- MERGE_CONFIGURATION_EXAMPLES.md
- PHASE3_MERGE_IMPLEMENTATION.md
- README.ja.md
- README.md
- STRUCTURE.md
- _config.yml
- cat-github-watcher.py
- config.toml.example
- demo_automation.py
- demo_comparison.py
- docs/IMPLEMENTATION_SUMMARY.ja.md
- docs/IMPLEMENTATION_SUMMARY.md
- docs/PR67_IMPLEMENTATION.md
- docs/RULESETS.md
- docs/VERIFICATION_GUIDE.en.md
- docs/VERIFICATION_GUIDE.md
- docs/browser-automation-approaches.en.md
- docs/browser-automation-approaches.md
- generated-docs/project-overview-generated-prompt.md
- pytest.ini
- requirements-automation.txt
- ruff.toml
- src/__init__.py
- src/gh_pr_phase_monitor/__init__.py
- src/gh_pr_phase_monitor/browser_automation.py
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
- tests/test_all_phase3_timeout.py
- tests/test_browser_automation.py
- tests/test_config_rulesets.py
- tests/test_elapsed_time_display.py
- tests/test_hot_reload.py
- tests/test_integration_issue_fetching.py
- tests/test_interval_parsing.py
- tests/test_issue_fetching.py
- tests/test_no_open_prs_issue_display.py
- tests/test_notification.py
- tests/test_phase3_merge.py
- tests/test_phase_detection.py
- tests/test_post_comment.py
- tests/test_post_phase3_comment.py
- tests/test_pr_actions.py
- tests/test_pr_actions_with_rulesets.py
- tests/test_status_summary.py
- tests/test_verbose_config.py

## 現在のオープンIssues
## [Issue #94](../issue-notes/94.md): Add assign_lowest_number_issue option to assign issues by number instead of "good first issue" label
## Implementation Plan for Issue Assignment by Lowest Number Feature

- [x] Explore repository structure and understand current implementation
- [x] Add new configuration option `assign_lowest_number_issue` in `config.toml.example` (default: false)
- [x] Update `config.py` to display the new configu...
ラベル: 
--- issue-notes/94.md の内容 ---

```markdown

```

## [Issue #93](../issue-notes/93.md): toml rulesets repositories について、ownerは不要なので削除し、リポジトリ名だけを書くようにして、userの混乱を減らす

ラベル: 
--- issue-notes/93.md の内容 ---

```markdown

```

## [Issue #92](../issue-notes/92.md): tomlについて、enable_execution_phase1_to_phase2 , enable_execution_phase2_to_phase3 , enable_execution_phase3_send_ntfy , enable_execution_phase3_to_merge はrulesetsの内部でのみ記述できるようにし、userの混乱を減らす

ラベル: 
--- issue-notes/92.md の内容 ---

```markdown

```

## [Issue #91](../issue-notes/91.md): tomlについて、phase3_merge と assign_to_copilot は rulesetsごとに定義可能にする

ラベル: 
--- issue-notes/91.md の内容 ---

```markdown

```

## [Issue #87](../issue-notes/87.md): 大幅な仕様変更をしたのでドッグフーディングする

ラベル: 
--- issue-notes/87.md の内容 ---

```markdown

```

## [Issue #85](../issue-notes/85.md): all_phase3_timeout  のデフォルトは安全性優先で30mにする

ラベル: 
--- issue-notes/85.md の内容 ---

```markdown

```

## [Issue #83](../issue-notes/83.md): 「Goot first issue有無に関わらず、最も番号の小さいissueを1つAssignする機能」を新たにtomlでon/offできるようにする。デフォルトはoff

ラベル: 
--- issue-notes/83.md の内容 ---

```markdown

```

## [Issue #80](../issue-notes/80.md): 「すべてphase3」になったら、ntfyで通知を送る。文言はtomlで指定する

ラベル: 
--- issue-notes/80.md の内容 ---

```markdown

```

## [Issue #32](../issue-notes/32.md): 「Posting comment for phase2... / Comment already exists, skipping / Comment posted successfully」と表示され、userが混乱する。skippingのあとはpostedを表示しないようにする

ラベル: good first issue
--- issue-notes/32.md の内容 ---

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

### .github/actions-tmp/issue-notes/3.md
```md
{% raw %}
# issue GitHub Actions「issue note生成」を共通ワークフロー化する #3
[issues #3](https://github.com/cat2151/github-actions/issues/3)

- 前提
  - userは、translateのworkflowを共通ワークフロー化し、動くようにしたので、共通ワークフロー化の知識がある
  - よって、今回は、promptでplanさせ、そのplanをuserがレビューし、planの改善を指示できるので、ハルシネーションのリスクを下げることができる

- prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlはまだ共通ワークフロー化されず、
呼び出し元からコピーされたままの状態です。
このymlファイル名のまま、
中身を共通ワークフロー化してください。
呼び出し元ymlは別途書きますので気にしないでください。
まずplanしてください
```

- plan 生成結果
```
共通ワークフロー化のためのplanは以下の通りです。

1. 目的
現在の issue-note.yml を「共通ワークフロー」として再設計し、他リポジトリや他ワークフローから workflow_call で呼び出せるようにする。
2. 主な変更点
on: トリガーを workflow_call に変更（直接イベントで起動しない）。
必要な入力（inputs）やシークレット（secrets）を workflow_call セクションで定義。
github.event.issue などのイベント依存部分を、inputs経由で受け取る形に修正。
既存の処理（issueノート生成、コミット、issue body更新）はそのまま活かすが、パラメータ化する。
3. 具体的な修正内容
on: issues: → on: workflow_call: に変更。
inputs で必要な値（例: issue_title, issue_number, issue_body, issue_url など）を受け取る。
スクリプト内の ${{ github.event.issue.xxx }} を ${{ inputs.xxx }} に置換。
github-script ステップも同様にinputsを参照。
必要に応じて secrets も workflow_call で受け取れるようにする。
4. ファイル名・配置
ファイル名はそのまま issue-note.yml。
配置場所は workflows でOK（共通ワークフローとしてもこの場所で良い）。
5. 呼び出し元への影響
呼び出し元ワークフローで uses: <repo>/.github/workflows/issue-note.yml@main のように参照し、inputsを渡す形になる。
このplanで進めます。次に、実際の共通ワークフロー化のためのyml修正案を作成しますか？
```

- userがplanレビューし、OKを出した
- agentに生成結果ymlをレビューさせた、OKとなった
  - userはこのレビューは認知負荷が高いのでskipとする（単純な細かい間違い探し作業になるので、それはagentに任せた）
-  エラー。呼び出し元ymlのエラーがあり修正。共通ワークフローのエラー指摘があり、共通ワークフロー側の修正が必要となった
```
原因の分析：

呼び出し元（tonejs-mml-to-jsonのissue-note.yml）は、reusable workflow（cat2151/github-actions/.github/workflows/issue-note.yml@main）をusesで呼び出し、inputsをwithで渡しています。
共通ワークフロー（reusable workflow）は inputs を workflow_call で受け取り、各ステップで ${{ inputs.xxx }} で参照しています。
しかし、エラーが発生したのは actions/github-script@v7 の script 内です。
エラーの本質的な原因：

actions/github-script の script: で ${{ inputs.issue_number }} のような式を直接 JavaScript テンプレートリテラル内で使っていますが、これはサポートされていません。
script: の中は JavaScript であり、YAMLの ${{ ... }} は展開されません（または意図通りに展開されません）。
そのため、inputs 変数は script 内の JavaScript で未定義となり、ReferenceError になります。
正しい書き方：

actions/github-script の script: でワークフローの inputs を使いたい場合は、with: で input を environment 変数や script の引数として渡し、JavaScript で process.env から取得するか、github-script の input 機能を使う必要があります。
例（修正版）：

このように、inputs の値を env で渡し、script 内では process.env で参照してください。

まとめ：

actions/github-script の script 内で ${{ inputs.xxx }} を直接使うと ReferenceError になる
env: で値を渡し、process.env で参照するのが正しい
修正が必要です。修正版のワークフローが必要な場合はお知らせください。
```

- test green
- closeとする

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

### config.toml.example
```example
{% raw %}
# GitHub PR Phase Monitor Configuration

# Check interval - how often to check the repositories
# Supported formats:
#   - "30s" = 30 seconds
#   - "1m"  = 1 minute
#   - "5m"  = 5 minutes
#   - "1h"  = 1 hour
#   - "1d"  = 1 day
interval = "1m" # default

# Number of issues to display from repositories without open PRs
# Default is 10, but can be changed to any positive number (e.g., 5, 15, 20)
issue_display_limit = 10

# Timeout for "all PRs in phase3" state
# If all PRs remain in phase3 for this duration, the application will exit
# to prevent wasting API usage. Set to empty string "" to disable.
# Supported formats: "30s", "1m", "5m", "30m", "1h", "1d"
# Default: "" (disabled)
all_phase3_timeout = ""

# Verbose mode - Print detailed configuration information
# When enabled, prints all settings at startup and per-repository settings during execution
# This helps detect configuration mistakes
# Default: false
verbose = false

# Note: This tool monitors user-owned repositories under the current GitHub user account
# It uses GraphQL API to efficiently fetch all repositories with open PRs
# Organization repositories are NOT included (YAGNI principle - keeping it simple)
# No need to specify repository directories!

# Execution control flags - Dry-run mode by default
# Set these to true to enable actual actions (marking PRs ready, posting comments, sending notifications)
# These global flags are used when no rulesets are defined or when rulesets don't apply
enable_execution_phase1_to_phase2 = false  # Set to true to mark draft PRs as ready
enable_execution_phase2_to_phase3 = false  # Set to true to post phase2 comments
enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
enable_execution_phase3_to_merge = false   # Set to true to merge phase3 PRs

# Rulesets - Fine-grained control per repository or group of repositories
# Rulesets are applied in order, with later rulesets overriding earlier ones
# Each ruleset can specify different execution settings for different repositories
#
# Example configurations:
#
# [[rulesets]]
# name = "All repositories default"
# repositories = ["all"]  # "all" matches all repositories
# enable_execution_phase1_to_phase2 = false
# enable_execution_phase2_to_phase3 = false
# enable_execution_phase3_send_ntfy = false
# enable_execution_phase3_to_merge = false
#
# [[rulesets]]
# name = "Enable automation for test repository"
# repositories = ["owner/test-repo"]  # Specific repository with owner/name format
# enable_execution_phase1_to_phase2 = true
# enable_execution_phase2_to_phase3 = true
# enable_execution_phase3_send_ntfy = true
# enable_execution_phase3_to_merge = true
#
# [[rulesets]]
# name = "Enable only notifications for production repos"
# repositories = ["owner/prod-repo1", "owner/prod-repo2"]  # Multiple repositories
# enable_execution_phase1_to_phase2 = false
# enable_execution_phase2_to_phase3 = false
# enable_execution_phase3_send_ntfy = true
# enable_execution_phase3_to_merge = false
#
# You can also use just the repository name without the owner (matches any owner):
# [[rulesets]]
# name = "Example with repo name only"
# repositories = ["my-repo"]  # Matches any owner/my-repo
# enable_execution_phase1_to_phase2 = true
# enable_execution_phase3_to_merge = true

# ntfy.sh notification settings (optional)
# Sends mobile notifications when phase3 is detected
# Notifications include a clickable action button to open the PR
[ntfy]
enabled = false  # Set to true to enable notifications
topic = "<your-ntfy.sh-topic-name>" # Use a hard-to-guess topic name for security
message = "PR is ready for review: {url}"  # Message template, {url} will be replaced with PR URL
priority = 4  # Optional: notification priority (1=min, 3=default, 4=high, 5=max)

# Phase3 merge settings (optional)
# Automatically merge PRs when they reach phase3 (ready for review)
# Before merging, a comment defined below will be posted to the PR
[phase3_merge]
enabled = false  # Set to true to enable automatic merging (also requires enable_execution_phase3_to_merge = true)
comment = "All checks passed. Merging PR."  # Comment to post before merging
automated = false  # Set to true to use browser automation to click the merge button
automation_backend = "selenium"  # Backend to use: "selenium" or "playwright" (automated mode only)
wait_seconds = 10  # How long to wait after opening the browser before clicking (automated mode only)
browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
headless = false  # Run browser in headless mode (no visible window, automated mode only)
# Note: Feature branch is automatically deleted after successful merge

# Auto-assign "good first issue" issues to Copilot (optional)
# When enabled, the tool will automatically open the issue in your browser.
# You can then manually click the "Assign to Copilot" button on the GitHub issue page.
# 
# Automated mode (requires Selenium or Playwright):
# If 'automated' is set to true, the tool will use browser automation to
# automatically click the buttons after waiting for the specified time.
# 
# Selenium backend:
#   Install: pip install selenium webdriver-manager
#   Browsers: "edge", "chrome", or "firefox"
# 
# Playwright backend:
#   Install: pip install playwright && playwright install
#   Browsers: "chromium", "firefox", or "webkit"
[assign_to_copilot]
enabled = false  # Set to true to enable auto-assignment feature
automated = false  # Set to true to enable automated button clicking
automation_backend = "selenium"  # Backend to use: "selenium" or "playwright"
wait_seconds = 10  # How long to wait after opening the browser before clicking (automated mode only)
browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
headless = false  # Run browser in headless mode (no visible window, automated mode only)

{% endraw %}
```

### src/gh_pr_phase_monitor/config.py
```py
{% raw %}
"""
Configuration loading and parsing utilities
"""

import os
import re
from typing import Any, Dict

import tomli


def parse_interval(interval_str: str) -> int:
    """Parse interval string like '1m', '30s', '2h' to seconds

    Args:
        interval_str: String like '1m', '30s', '2h', '1d'

    Returns:
        Number of seconds

    Raises:
        ValueError: If the interval string format is invalid
    """
    # Type validation for common misconfiguration
    if not isinstance(interval_str, str):
        raise ValueError(
            f"Interval must be a string (e.g., '1m', '30s'), got {type(interval_str).__name__}: {interval_str}"
        )

    interval_str = interval_str.strip().lower()

    # Match pattern like "30s", "1m", "2h", "1d"
    match = re.match(r"^(\d+)([smhd])$", interval_str)

    if not match:
        raise ValueError(
            f"Invalid interval format: '{interval_str}'. "
            "Expected format: <number><unit> (e.g., '30s', '1m', '2h', '1d')"
        )

    value = int(match.group(1))
    unit = match.group(2)

    # Convert to seconds
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:  # unit == "d"
        return value * 86400


def _validate_boolean_flag(value: Any, flag_name: str) -> bool:
    """Validate that a configuration flag is a boolean value

    Args:
        value: The value to validate
        flag_name: Name of the flag for error messages

    Returns:
        The boolean value

    Raises:
        ValueError: If the value is not a boolean
    """
    if not isinstance(value, bool):
        raise ValueError(
            f"Configuration flag '{flag_name}' must be a boolean (true/false), "
            f"got {type(value).__name__}: {value}"
        )
    return value


def get_config_mtime(config_path: str = "config.toml") -> float:
    """Get the modification time of the configuration file

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Modification time as a timestamp (seconds since epoch)

    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    return os.path.getmtime(config_path)


def load_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Load configuration from TOML file

    Args:
        config_path: Path to the TOML configuration file

    Returns:
        Dictionary containing configuration data

    Raises:
        FileNotFoundError: If the configuration file is not found
    """
    with open(config_path, "rb") as f:
        return tomli.load(f)


def print_config(config: Dict[str, Any]) -> None:
    """Print all configuration settings in a readable format

    Args:
        config: Configuration dictionary loaded from TOML
    """
    print("\n" + "=" * 50)
    print("Configuration Settings:")
    print("=" * 50)
    
    # Print main settings
    print("\n[Main Settings]")
    print(f"  interval: {config.get('interval', '1m')}")
    print(f"  issue_display_limit: {config.get('issue_display_limit', 10)}")
    print(f"  all_phase3_timeout: {config.get('all_phase3_timeout', '')}")
    print(f"  verbose: {config.get('verbose', False)}")
    
    # Print execution flags
    print("\n[Global Execution Flags]")
    print(f"  enable_execution_phase1_to_phase2: {config.get('enable_execution_phase1_to_phase2', False)}")
    print(f"  enable_execution_phase2_to_phase3: {config.get('enable_execution_phase2_to_phase3', False)}")
    print(f"  enable_execution_phase3_send_ntfy: {config.get('enable_execution_phase3_send_ntfy', False)}")
    print(f"  enable_execution_phase3_to_merge: {config.get('enable_execution_phase3_to_merge', False)}")
    
    # Print rulesets
    rulesets = config.get("rulesets", [])
    if rulesets and isinstance(rulesets, list):
        print("\n[Rulesets]")
        for i, ruleset in enumerate(rulesets, 1):
            if isinstance(ruleset, dict):
                print(f"\n  Ruleset #{i}:")
                print(f"    name: {ruleset.get('name', 'N/A')}")
                print(f"    repositories: {ruleset.get('repositories', [])}")
                print(f"    enable_execution_phase1_to_phase2: {ruleset.get('enable_execution_phase1_to_phase2', 'not set')}")
                print(f"    enable_execution_phase2_to_phase3: {ruleset.get('enable_execution_phase2_to_phase3', 'not set')}")
                print(f"    enable_execution_phase3_send_ntfy: {ruleset.get('enable_execution_phase3_send_ntfy', 'not set')}")
                print(f"    enable_execution_phase3_to_merge: {ruleset.get('enable_execution_phase3_to_merge', 'not set')}")
    else:
        print("\n[Rulesets]")
        print("  No rulesets configured")
    
    # Print ntfy settings
    ntfy = config.get("ntfy")
    if ntfy and isinstance(ntfy, dict):
        print("\n[ntfy.sh Notification Settings]")
        print(f"  enabled: {ntfy.get('enabled', False)}")
        if ntfy.get('enabled', False):
            print(f"  topic: {ntfy.get('topic', 'N/A')}")
            print(f"  message: {ntfy.get('message', 'N/A')}")
            print(f"  priority: {ntfy.get('priority', 4)}")
    
    # Print phase3_merge settings
    phase3_merge = config.get("phase3_merge")
    if phase3_merge and isinstance(phase3_merge, dict):
        print("\n[Phase3 Merge Settings]")
        print(f"  enabled: {phase3_merge.get('enabled', False)}")
        if phase3_merge.get('enabled', False):
            print(f"  comment: {phase3_merge.get('comment', 'N/A')}")
            print(f"  automated: {phase3_merge.get('automated', False)}")
            if phase3_merge.get('automated', False):
                print(f"  automation_backend: {phase3_merge.get('automation_backend', 'selenium')}")
                print(f"  wait_seconds: {phase3_merge.get('wait_seconds', 10)}")
                print(f"  browser: {phase3_merge.get('browser', 'edge')}")
                print(f"  headless: {phase3_merge.get('headless', False)}")
    
    # Print assign_to_copilot settings
    assign_to_copilot = config.get("assign_to_copilot")
    if assign_to_copilot and isinstance(assign_to_copilot, dict):
        print("\n[Auto-assign to Copilot Settings]")
        print(f"  enabled: {assign_to_copilot.get('enabled', False)}")
        if assign_to_copilot.get('enabled', False):
            print(f"  automated: {assign_to_copilot.get('automated', False)}")
            if assign_to_copilot.get('automated', False):
                print(f"  automation_backend: {assign_to_copilot.get('automation_backend', 'selenium')}")
                print(f"  wait_seconds: {assign_to_copilot.get('wait_seconds', 10)}")
                print(f"  browser: {assign_to_copilot.get('browser', 'edge')}")
                print(f"  headless: {assign_to_copilot.get('headless', False)}")
    
    print("\n" + "=" * 50)


def resolve_execution_config_for_repo(
    config: Dict[str, Any], repo_owner: str, repo_name: str
) -> Dict[str, bool]:
    """Resolve execution configuration for a specific repository using rulesets

    This function applies rulesets in order, with later rulesets overriding earlier ones.
    First applies global settings, then applies matching rulesets.

    Args:
        config: Configuration dictionary loaded from TOML
        repo_owner: Repository owner
        repo_name: Repository name

    Returns:
        Dictionary with execution flags:
        - enable_execution_phase1_to_phase2
        - enable_execution_phase2_to_phase3
        - enable_execution_phase3_send_ntfy
        - enable_execution_phase3_to_merge
    """
    # Full repository identifier
    repo_full_name = f"{repo_owner}/{repo_name}"

    # Start with global defaults (backward compatibility) with validation
    def get_validated_flag(flag_name: str, default: bool = False) -> bool:
        """Get and validate a global configuration flag"""
        value = config.get(flag_name, default)
        # Only validate if the value was actually provided in config (not using default)
        if flag_name in config:
            return _validate_boolean_flag(value, flag_name)
        return value

    result = {
        "enable_execution_phase1_to_phase2": get_validated_flag("enable_execution_phase1_to_phase2", False),
        "enable_execution_phase2_to_phase3": get_validated_flag("enable_execution_phase2_to_phase3", False),
        "enable_execution_phase3_send_ntfy": get_validated_flag("enable_execution_phase3_send_ntfy", False),
        "enable_execution_phase3_to_merge": get_validated_flag("enable_execution_phase3_to_merge", False),
    }

    # Apply rulesets if they exist
    rulesets = config.get("rulesets", [])
    if not isinstance(rulesets, list):
        return result

    for ruleset in rulesets:
        if not isinstance(ruleset, dict):
            continue

        # Get target repositories for this ruleset
        repositories = ruleset.get("repositories", [])
        if not isinstance(repositories, list):
            continue

        # Check if this ruleset applies to the current repository
        applies = False
        for repo_pattern in repositories:
            if not isinstance(repo_pattern, str):
                continue
            # "all" matches all repositories
            if repo_pattern.lower() == "all":
                applies = True
                break
            # Exact match with full name (owner/repo)
            if repo_pattern == repo_full_name:
                applies = True
                break
            # Match just the repo name (for backward compatibility)
            if repo_pattern == repo_name:
                applies = True
                break

        # If this ruleset applies, override execution flags with validation
        if applies:
            if "enable_execution_phase1_to_phase2" in ruleset:
                result["enable_execution_phase1_to_phase2"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase1_to_phase2"], "enable_execution_phase1_to_phase2"
                )
            if "enable_execution_phase2_to_phase3" in ruleset:
                result["enable_execution_phase2_to_phase3"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase2_to_phase3"], "enable_execution_phase2_to_phase3"
                )
            if "enable_execution_phase3_send_ntfy" in ruleset:
                result["enable_execution_phase3_send_ntfy"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase3_send_ntfy"], "enable_execution_phase3_send_ntfy"
                )
            if "enable_execution_phase3_to_merge" in ruleset:
                result["enable_execution_phase3_to_merge"] = _validate_boolean_flag(
                    ruleset["enable_execution_phase3_to_merge"], "enable_execution_phase3_to_merge"
                )

    return result


def print_repo_execution_config(
    repo_owner: str, repo_name: str, exec_config: Dict[str, bool]
) -> None:
    """Print execution configuration for a specific repository

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        exec_config: Execution configuration dictionary
    """
    print(f"    [Execution Config for {repo_owner}/{repo_name}]")
    print(f"      enable_execution_phase1_to_phase2: {exec_config.get('enable_execution_phase1_to_phase2', False)}")
    print(f"      enable_execution_phase2_to_phase3: {exec_config.get('enable_execution_phase2_to_phase3', False)}")
    print(f"      enable_execution_phase3_send_ntfy: {exec_config.get('enable_execution_phase3_send_ntfy', False)}")
    print(f"      enable_execution_phase3_to_merge: {exec_config.get('enable_execution_phase3_to_merge', False)}")

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
5a33c59 Merge pull request #90 from cat2151/copilot/implement-hot-reload-functionality
e357667 Clean up imports - move threading to top level
9ada7a4 Address PR review feedback - fix tests, improve countdown logic, and add integration tests
89dfe1e Improve exception handling specificity and remove unused variable
611a049 Fix elapsed time tracking and improve test portability
be049e6 Improve exception handling and add code review feedback
9a5a3d5 Add hot reload functionality to detect and reload config changes during wait
4f5845d Initial plan
493a6ac Merge pull request #88 from cat2151/copilot/add-verbose-print-configuration
463fedf Remove unused sys import from test_verbose_config.py

### 変更されたファイル:
MERGE_CONFIGURATION_EXAMPLES.md
PHASE3_MERGE_IMPLEMENTATION.md
README.ja.md
README.md
config.toml.example
src/gh_pr_phase_monitor/__init__.py
src/gh_pr_phase_monitor/browser_automation.py
src/gh_pr_phase_monitor/comment_manager.py
src/gh_pr_phase_monitor/config.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/pr_actions.py
tests/test_all_phase3_timeout.py
tests/test_browser_automation.py
tests/test_elapsed_time_display.py
tests/test_hot_reload.py
tests/test_phase3_merge.py
tests/test_post_phase3_comment.py
tests/test_verbose_config.py


---
Generated at: 2026-01-07 07:02:07 JST
