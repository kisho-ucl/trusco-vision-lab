# Semi-automatic Annotation Mini Specs

Last updated: 2026-05-22

親仕様: [SPEC.md](SPEC.md)

## v0 Exploratory Manual Manifest Annotation

### Goal

clip manifestを読み込み、作業者clipにInspect / Sort / Transportなどのラベルを付け、annotation結果をJSONLとしてexportできる最小annotation UIを作る。

今の目的は、完成版annotation systemではない。まずはclip単位のラベル付け作業の流れ、manifest schema、annotation outputを確認できる状態にする。

### Scope

#### In

- JSON manifest import。
- clip viewer。
- metadata, zone hint, track summary表示。
- Inspect / Sort / Transport / Other / Unclearのlabel selection。
- high / medium / lowのconfidence。
- optional note。
- annotation結果のJSONL export。
- localStorage autosave。
- sample manifest。

#### Out

- tracking outputからのclip自動抽出。
- clusteringやcandidate ordering。
- feature extraction。
- dataset split / model input export。
- 複数人annotation。
- user accountやDB。

### UX / Operation

画面はannotation作業を速くすることを優先する。

- 左: clip viewer。
- 中央: metadata, trajectory / zone hints, note。
- 右: queue and progress。
- 上部: manifest import, export, progress。
- ラベルボタン: Inspect / Sort / Transport / Other / Unclear。
- confidence: high / medium / low。

Keyboard shortcuts:

- `1`: Inspect
- `2`: Sort
- `3`: Transport
- `4`: Other
- `5`: Unclear
- `ArrowRight`: next clip
- `ArrowLeft`: previous clip

### Data / Interfaces

`SPEC.md` のClip ManifestとAnnotation Outputに従う。

### Success Criteria

- sample manifestを読み込める。
- 3件程度のsample clip queueを表示できる。
- 1件のclipにlabel、confidence、noteを保存できる。
- 保存後にprogressとqueue表示が更新される。
- JSONLをexportできる。
- 実clipが未接続でもmetadataだけでUI確認できる。

### Visual Draft

v0はUIの完成イメージが重要なため、本来はHTML mockまたはASCII layoutを確認してから実装するべきだった。

今回の初期prototypeは、Spec-driven workflowを固める前に先行して実装したexploratory prototypeとして扱う。

そのため、このv0 prototypeをそのまま完成形とはみなさない。現在のSpecでは、annotation batch単位のcoverage、person ID correction、clip内のwork segment、先行研究に基づくcluster-level labelingなど、当初prototypeになかった重要要件が増えている。

次にUIを進める前に、改めてVisual Draftを作り、Go / Reviseを確認する。

### Open Questions

- 実tracking outputの形式は何か。
- `clip_id` はどの粒度で一意にするか。
- annotation labelの定義をどこまで明文化するか。
- noteには曖昧さだけでなく、object / scene state transitionの観察も書くか。

### Implementation Gate

- [x] Goal / Scope / Success Criteriaを確認した。
- [x] 未決事項がv0 prototypeを止めない。
- [ ] 次回以降、UIを大きく作る前はVisual Draftを確認する。

### Status

Exploratory prototype implemented in `tools/annotation`.

This prototype is useful for checking manifest import, simple labeling, localStorage autosave, and JSONL export, but it is not the final UI direction.

## v0.5 Visual Draft Refresh

### Goal

実装を進める前に、現在のSpecに沿ったannotation UIの完成イメージを作り直す。

v0 exploratory prototypeから学んだことを踏まえつつ、annotation batch単位のcoverage、clip provenance、person ID correction、clip内work segment labeling、先行研究のcluster-level labelingをどうUIに入れるかを確認する。

### Status

Draft.

### Scope

#### In

- ASCII layoutまたはHTML mock。
- batch loader。
- person ID / original tracking ID / clip coverageの表示。
- clip metadata panel。
- clip viewer。
- work segment labeling interaction。
- coverage progress view。
- save / resume flow。
- person ID correction flow。
- cluster-level labelingの入口案。

#### Out

- 実データ接続。
- tracking output parser。
- 本実装UI。
- clustering実装。
- model training。

### Design Questions

- 最初の画面は「clip queue」ではなく「annotation batchを読み込む画面」にするべきか。
- 30分JSON batch内で、person IDごとのcoverageをどう見せるか。
- 1 clip内の複数work segmentを、どれくらい簡単な操作で付けられるか。
- person ID correctionはactivity annotationの前工程にするか、同じUI内に軽く入れるか。
- 先行研究のcluster labelingは、v1 UIに入れるか、v2まで待つか。
- 途中保存はlocalStorageで十分か、progress JSONの手動保存・再読込を必須にするか。
- 「効率的で楽しい」をUI上でどう実現するか。例: 残り量、達成率、連続labeling、迷いclipの一時退避。

### Success Criteria

- ユーザーが完成イメージを見てGo / Reviseを判断できる。
- v1 server handoff時に、実装側がUIの方向性を誤解しない。
- v0 exploratory prototypeから引き継ぐもの / 捨てるものが明確になる。

### Implementation Gate

- [ ] Visual Draftを作成した。
- [ ] UserがGo / Reviseを判断した。
- [ ] Mini Spec v1に必要なUI要件を反映した。

## v1 Clip Extraction and Coverage Planning

### Goal

既存または今後得られるtracking outputから、person IDごとのclip manifestを生成する。

v1の目的は動画処理を完成させることではなく、annotation UIへ渡せるmanifestを実データ由来で作れるようにすること。

また、適当にpick upされたclipへバラバラにラベルを付けるのではなく、提供された30分程度のannotation batch単位で「どのperson ID・どのclipがどれだけラベル済みか」を見ながら進められる土台を作る。

trackingで同じ人に常に正しいIDが付くとは限らないため、activity annotationの前処理としてperson ID assignment / correctionが必要になる可能性がある。

### Status

Draft, needs server data discovery.

### Discovery First

サーバ上で実装前に以下を確認する。

- raw video path。
- tracking output path。
- tracking output format。
- timestamp format。
- camera ID naming。
- tracking ID naming。
- person ID assignmentに使えそうな情報。
- bbox / world coordinate / zone availability。
- raw videoとtracking timestampの同期方法。
- 30分JSONなど、annotation batchとして提供される単位。
- 人が画面内にいる時間帯をどう抽出できるか。
- cameraを跨ぐclipがどのように表現されるか。
- 同一人物らしさを推定するために使えるappearance / trajectory / time continuity情報。

### Scope

#### In

- tracking output形式の確認。
- manifest生成に必要な最小フィールドの決定。
- batch ID、source video ID、camera ID、person ID、original tracking ID、start / end time、video pathを含むmanifest生成。
- 可能ならzone hintとtrajectory summaryを追加。
- batch単位のcoverage summary。
- person ID assignment / correctionに必要なcandidate情報。
- 最初にラベル付けするbatch候補を選ぶための情報。

#### Out

- 高度なclip品質判定。
- 自動ラベル推定。
- clustering。
- dataset split。
- 完全なtimeline annotation UI。

### UX / Operation

v1ではUIを大きく作り直す前に、Visual Draftを作る。

理想の操作感:

- annotation batch JSONを読み込む。
- batch内のperson ID、original tracking ID、clip coverageが一覧で見える。
- clipを選ぶと、batch ID、source video ID、camera ID、person ID、original tracking ID、start / end time、zone hintが必ず見える。
- 必要ならperson ID assignmentを修正できる。
- 必要なら1つのclip内に複数のwork segmentをサッと付けられる。
- annotation coverageが見える。例: `person-03: batch内の 72% labeled`。
- 手動保存またはautosaveで、ブラウザを閉じても途中から再開できる。
- 「あとどれくらいでこのbatchが埋まるか」が分かる。

### Data / Interfaces

Minimum clip fields:

- `clip_id`
- `batch_id`
- `source_video_id`
- `camera_id`
- `person_id`
- `original_tracking_id`
- `start_time`
- `end_time`
- `video_url` or source video reference

Preferred fields:

- `duration_sec`
- `zone_hint`
- `track_summary`
- `candidate_reason`
- `source_tracking_file`

Annotation outputは、1 clip 1 labelだけでなく、複数work segmentを持てる形も許容する。

### Success Criteria

- 実tracking outputまたは小さなサンプルからclip manifestを生成できる。
- 生成manifestをv0 annotation UIで読み込める。
- 少なくとも10-30件のclip候補をannotation queueとして確認できる。
- 各clipについて、batch ID、source video ID、camera ID、person ID、original tracking ID、start / end timeを表示できる。
- batch単位のcoverage summaryを生成できる。
- 手動保存またはautosaveにより、途中から再開できる。
- person IDが不確かなclipをreview対象として表示できる。
- 最初にラベル付けすべきbatch候補を1つ提案できる。

### Open Questions

- tracking outputはどのサーバ・どの形式で保存されているか。
- raw camera videoとtracking timestampはどう同期するか。
- clipは固定長か、停止・zone滞在などで切るか。
- 提供される30分JSONには、どの粒度のclip / track / camera情報が含まれるか。
- cameraを跨ぐclipやperson IDはどう表現するか。
- person ID correctionはactivity annotation前に別工程にするか、同じUI内に入れるか。
- 画面内の全作業者へ連続ラベルを付ける運用と、候補clipにだけラベルを付ける運用をどう使い分けるか。
- `Other` と `Unclear` の違いをどう定義するか。
- 効率的で楽しいannotationをどう測るか。例: 1時間あたり件数、迷った件数、途中離脱しにくさ、進捗の見やすさ。

### Visual Draft

Required before implementation if v1 changes the UI.

Draft should include:

- batch loader。
- person ID / original tracking ID / clip coverage list。
- clip metadata panel。
- work segment labeling interaction。
- coverage progress view。
- save / resume flow。
- person ID correction flow。

Current draft:

- [VISUAL_DRAFT_v0_5.md](VISUAL_DRAFT_v0_5.md)

### Implementation Gate

- [ ] Server data discoveryが終わっている。
- [ ] 実tracking outputのsample rowまたはschemaが記録されている。
- [ ] v1で作るmanifest schemaが決まっている。
- [ ] batch単位のcoverageをどう出すか決まっている。
- [ ] save / resume方式が決まっている。
- [ ] person ID correctionをv1に入れるか決まっている。
- [ ] UIを触る場合はVisual Draftを確認している。

## v2 Annotation Efficiency

### Goal

特徴量抽出やclusteringを使い、似たclipを近くに並べてannotation効率を上げる。

研究室の先行研究 `Semi-Automated Framework for Digitalizing Multi-Product Warehouses with Large Scale Camera Arrays` の `segmentation -> encoding -> clustering -> manual labeling` の考え方を、worker activity annotationへ移植する。

### Candidate Scope

- trajectory feature extraction。
- CLIP feature / VideoMAE feature extraction。
- 類似clip ordering。
- cluster-level labeling。
- cluster内の例外clipを除外・修正するUI。
- 同じラベルを連続適用するbulk labeling。

### Success Criteria

- ランダム順よりも、似たclipがまとまって表示される。
- annotation速度またはラベル一貫性の改善を簡単に測れる。
- cluster単位でlabel候補を付け、混入clipだけを除外・修正できる。
- 先行研究と同様に、annotation timeを比較指標として記録できる。

### Open Questions

- activity clipのembeddingにはtrajectory、zone transition、visual featureのどれが効くか。
- object annotationのcluster labeling UIをどこまで再利用できるか。
- worker activityでは、cluster内に複数ラベルが自然に混ざる可能性がどれくらいあるか。
- 先行研究のBitbucket codeで再利用できるmoduleはあるか。

### Status

Candidate.

## v3 Dataset Export

### Goal

annotation結果を実験に使えるdataset formatへ変換する。

### Candidate Scope

- train / val / test split。
- per-worker split。
- per-day split。
- model input manifest。
- label distribution summary。

### Success Criteria

- annotation済みclipをbaseline実験の入力へ変換できる。
- split条件とlabel分布が再現可能に残る。

### Status

Candidate.
