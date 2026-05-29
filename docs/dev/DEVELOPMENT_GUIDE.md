# Development Guide

このプロジェクトでは、AIと一緒に軽量な仕様駆動開発を行う。

目的は、仕様を書くこと自体ではなく、実装前に「何を作るか」「どこまで作るか」「何を見て完了とするか」を確認し、研究用ツールを再現可能な形で育てること。

## Document Roles

- `DASHBOARD.md`: 現在地、仮説、次の判断を置く。
- `docs/dev/specs/<thing>/SPEC.md`: 作りたいもの単位の親仕様を置く。
- `docs/dev/specs/<thing>/MINI_SPECS.md`: 実装単位のMini Specを地続きで置く。
- `docs/dev/implementation_backlog.md`: まだSpec化していない実装候補を置く。
- `tools/<tool>/README.md`: 完成したツールの実行手順・出力仕様を置く。
- `logs/YYYY-MM-DD.md`: 方針転換、重要なフィードバック、実験結果、あとで引用したい判断だけを任意で残す。

## Workflow

1. `DASHBOARD.md` で今日扱う対象を決める。
2. 対象の `SPEC.md` を読む。なければ先に作る。
3. `MINI_SPECS.md` に今回の実装単位を書く。
4. AIは実装前に確認論点を最大3つ出す。
5. ユーザーがGo / Reviseを判断する。
6. 必要ならVisual Draftを作り、完成イメージを確認する。
7. Mini Specの成功条件だけを満たすように実装する。
8. 成功条件で検証する。
9. 重要な判断や結果だけを必要に応じてlogへ残す。

## Conversation Before Spec Changes

大きな方向修正は、いきなりSpecへ反映しない。

特にユーザーの発言が「必要かもしれない」「こういう可能性がある」「難しいかも」のように仮説・問いかけの段階である場合、AIはまずチャットで整理する。

AIが先にやること:

- 確定していることと未確定のことを分ける。
- 選択肢を2-4個に整理する。
- それぞれの利点、リスク、後回しにした場合の影響を短く説明する。
- 「Specに反映する」「Open Questionに留める」「今は何もしない」のどれがよいか確認する。

AIが避けること:

- 仮説を確定要件としてSpecに書き込む。
- UIやデータ構造を大きく変えるpatchを、合意前に入れる。
- 「たぶん必要そう」だけでMini SpecのScopeを増やす。

例:

```text
User: tracking IDが不安定なので、person ID correctionが必要なのかもしれない。

AI should respond:
- 確定: tracking IDが不安定な可能性がある。
- 未確定: correction toolが必要か、v1に入れるか、別工程にするか。
- Options:
  A. v1ではtracking IDをそのまま使う。
  B. suspicious IDだけflagできるようにする。
  C. person ID correctionを別前処理にする。
  D. clip-level annotationから始め、person単位は後回しにする。
- まずどれをSpecに反映しますか？
```

Specに入れる場合も、確定していないものは `Open Questions`、`Possible Future Step`、`Needs Data Discovery` として弱く書く。

## Spec Shape

親Specには、作りたいもの全体の方向を置く。

- Purpose
- Background
- Users / Use Cases
- Core Workflow
- Design Principles
- Data / Interfaces
- High-level Implementation Path
- Non-goals

親Specにも大まかな実装ステップは置いてよい。ただし、詳細な実装範囲、UI、成功条件はMini Spec側で決める。

## Mini Spec Shape

Mini Specは、実装に入る直前の合意文書にする。

- Goal
- Scope
- UX / Operation
- Data / Interfaces
- Success Criteria
- Open Questions
- Visual Draft
- Implementation Gate

毎回すべてを重く書く必要はない。UIやワークフローのズレが起きやすい時だけ、Visual Draftを入れる。

## Visual Draft

UI、workflow、data flowの完成イメージにズレが出そうな場合だけ使う。

候補:

- Mermaid: 全体フローやデータフロー。
- ASCII layout: 画面構成の軽い確認。
- HTML mock: UIをちゃんと確認したい時。

Visual Draftは実装ではない。ユーザーがGo / Reviseを判断するための下書きとして扱う。

## Implementation Gate

実装に入る前に、最低限これだけ確認する。

- Goalに納得している。
- In / Outに納得している。
- Success Criteriaで動作確認できる。
- 未決事項が今回の実装を止めない。

## Logs Policy

logsは毎回書かない。

残す価値があるもの:

- 先生や共同研究者からの重要フィードバック。
- 方針転換。
- 実験結果や失敗例。
- あとで修論や引き継ぎに使う判断。

日々の細かい実装メモは、必要ならMini SpecやREADMEに反映する。

## Python Environment

このプロジェクトの実行環境は pyenv で管理する。

- venv名: `.venv_trusco-vision`
- Python: 3.10.11
- 実行パス: `/home/kisho_ucl/.pyenv/versions/.venv_trusco-vision/bin/python`
- パッケージ: `opencv-python`, `tqdm`, `flask`（必要に応じて追加）

リポジトリルートに `.python-version` ファイルがあり、`pyenv virtualenv-init` が `.bashrc` に設定済みのため、`trusco-vision-lab/` 配下では **自動的にvenvが有効** になる。`which python` で `/home/kisho_ucl/.pyenv/shims/python` が返れば正常。

新しいパッケージを追加する場合は、venvが有効な状態で `pip install <package>` を使う。

## Design Draft Method

UIやワークフローの完成イメージをすり合わせる際は、以下の形式をMini Specに直接書く。

- **ASCII layout**: 画面構成の確認。markdownプレビューで見られる。
- **Mermaid**: フロー・データフロー。VS Codeでレンダリングされる。
- **HTML mock**: インタラクションを確認したいときはファイルをブラウザで開く。

Visual Draftは実装ではない。ユーザーがGo / Reviseを判断してから実装に入る。

## Collaboration Style

AIは実装の前に確認論点を最大3つ出し、ユーザーのGo / Revise判断を待つ。

「全投げ」にしない。設計の合意と実装を分けることで、後から気づく手戻りを減らす。

具体的には:
- 仕様が曖昧なときはチャットで選択肢を整理する。
- 実装に入る前に Mini Spec の Implementation Gate を確認する。
- 大きな方向修正はSpecに反映する前にチャットで議論する。

## Read-Only Data Policy

- `/mnt/bigdata` および `/mnt/gazania` は、倉庫実データ用の参照専用マウントであり、**完全読み込み専用（Read-only）のトップレベル保護対象**です。
- AIアシスタントおよび開発中のスクリプト・ツールは、これらのディレクトリに対してファイルの作成・変更・削除などの書き込み処理を絶対に行ってはなりません。
- 中間生成物や切り出し画像、アノテーションデータ等の作業ファイルは、すべてワークスペース側（`/home/kisho_ucl/kisho_ws/` 配下）に保存し、マウント先データへはシンボリックリンク（例: `dataset -> /mnt/...`）経由でアクセスしてください。
