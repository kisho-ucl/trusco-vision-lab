# Visual Draft v0.5: Batch-first Annotation UI

Last updated: 2026-05-22

Related mini spec: [MINI_SPECS.md](MINI_SPECS.md#v05-visual-draft-refresh)

## Goal

半自動annotation UIの完成イメージを、実装前にすり合わせる。

今の方針は、任意のcameraや時間帯を選んで作業するUIではなく、提供された30分程度のJSON batchを読み込み、そのbatch内のclip、person ID、annotation coverageを管理しながら進めるUIにすること。

## Updated Constraints

- cameraを跨ぐclipがありうるため、`select camera_id` を主導線にしない。
- ユーザーが任意時間を指定してdataを引くのではなく、30分程度のJSON batchが提供される想定。
- trackingだけで同じ人に安定したIDを付けるのは難しい。
- activity annotationの前処理として、clipから人の特徴を見てperson ID assignment / correctionを行う必要があるかもしれない。
- 途中でブラウザを閉じても再開できる必要がある。autosaveでも手動saveでもよい。

## Core Idea

UIの中心は `source session` ではなく `annotation batch` にする。

1. annotation batch JSONを開く。
2. batch内のclip、person candidate、coverageを見る。
3. 必要ならperson ID assignmentを確認・修正する。
4. ラベル未付与または曖昧なclipを選ぶ。
5. clip全体またはclip内のwork segmentにlabelを付ける。
6. 途中結果を保存し、再開できるようにする。
7. ある程度埋まったbatchをdataset candidateにする。

## Top-level Layout

```text
+--------------------------------------------------------------------------------+
| Batch: 2026-05-01 AM batch       Load JSON   Save Progress   Export   Settings |
+----------------------------+-----------------------------------+---------------+
| Batch Progress             | Clip Viewer                       | Clip Details  |
|                            |                                   |               |
| Overall: 64% labeled       |  +-----------------------------+  | clip_id       |
| Person IDs                 |  |                             |  | person_id     |
|  P-01  [########--] 82%    |  |          video              |  | tracking_id   |
|  P-02  [#####-----] 51%    |  |                             |  | camera_id(s)  |
|  P-03  [##--------] 23%    |  +-----------------------------+  | source video  |
|                            |                                   | start / end   |
| ID Review                  |  Timeline                         | zone hint     |
|  Uncertain: 12 clips       |  00:00          00:30              | track summary |
|  Possible merge: P03/P07   |  |---Transport---|--Sort?--|       |               |
|                            |                                   | Notes         |
| Queue                      |  Work Segment Editor              |               |
|  Next unlabeled            |  [Transport] [Inspect] [Sort]     |               |
|  Ambiguous                 |  [Other] [Unclear]                |               |
|  Cluster suggestions       |                                   |               |
+----------------------------+-----------------------------------+---------------+
| Bottom bar: saved 14:52 / 42 clips left / 18 ambiguous / 12 ID uncertain       |
+--------------------------------------------------------------------------------+
```

## Main Panels

### 1. Batch Progress Panel

Purpose:

- 「いつ終わるのか分からない」感を減らす。
- batch単位でannotation progressを見せる。
- 次にラベル付けすべき対象を選びやすくする。
- person IDが怪しいclipを見つけやすくする。

Displays:

- loaded annotation batch
- overall coverage
- person-level coverage
- unlabeled clips
- ambiguous clips
- uncertain person IDs
- suggested next clips

Useful actions:

- select person ID
- jump to next unlabeled
- jump to ambiguous
- jump to ID review
- jump to cluster suggestion

### 2. Person ID Review Panel / Mode

Purpose:

- tracking IDが不安定な場合に、同じ人らしいclipを同じperson IDへ寄せる。
- activity labelを付ける前に、最低限のidentity consistencyを整える。

Displays:

- current person ID
- original tracking ID
- representative thumbnails or short previews
- possible same-person candidates
- possible split / merge warnings

Useful actions:

- merge person IDs
- split person ID
- assign selected clip to another person ID
- mark uncertain
- accept suggested grouping

### 3. Clip Viewer Panel

Purpose:

- 対象clipを見て、作業内容を判断する。
- 1 clip内で作業が切り替わる場合、work segmentを切れるようにする。

Displays:

- video
- playback controls
- current timestamp
- timeline
- existing work segments
- worker track overlay if available

Useful actions:

- play / pause
- frame step
- set work segment start
- set work segment end
- assign label to selected range
- split segment at current time
- mark unclear

### 4. Clip Details Panel

Purpose:

- 元データの由来を常に見えるようにする。
- 後で追跡・検証できるannotationにする。

Displays:

- `clip_id`
- `batch_id`
- `source_video_id`
- `camera_id` or `camera_ids`
- `person_id`
- `original_tracking_id`
- `start_time`
- `end_time`
- `zone_hint`
- `track_summary`
- `candidate_reason`
- note

### 5. Cluster Suggestions

Purpose:

- 先行研究のcluster-level labelingをactivity annotationへ拡張する。
- v1で本格実装しなくても、UI上の入口を設計しておく。

Displays:

- similar clips group
- representative thumbnails
- proposed label if available
- cluster size
- mixed / noisy flag

Useful actions:

- apply label to cluster
- exclude specific clips
- send clip to ambiguous queue
- open cluster review mode

## Save / Resume

途中でブラウザを閉じても再開できる必要がある。

Minimum:

- localStorage autosave
- manual export of progress JSON
- manual import of progress JSON

Preferred:

- save status in bottom bar
- last saved timestamp
- dirty state indicator
- recovery prompt on reload

Progress JSON should include:

- loaded batch ID
- annotation results
- work segments
- person ID corrections
- ambiguous flags
- excluded clips
- UI progress state if useful

## Work Segment Labeling Interaction

Basic single-label case:

```text
1. clipを見る
2. label buttonを押す
3. clip全体にlabelが付く
4. 次のclipへ進む
```

Multi-segment case:

```text
1. timeline上でstartを置く
2. timeline上でendを置く
3. labelを選ぶ
4. work segmentとして保存する
5. 残り区間を続けてlabelする
```

Keyboard candidates:

- `Space`: play / pause
- `I`: set in point
- `O`: set out point
- `1`: Inspect
- `2`: Sort
- `3`: Transport
- `4`: Other
- `5`: Unclear
- `Enter`: save current work segment
- `N`: next unlabeled clip
- `A`: send to ambiguous queue
- `R`: open person ID review

## Annotation Modes

### Mode A: Batch Fill

提供されたannotation batch内のperson / clip coverageを埋める。

Best for:

- 30分程度のJSON単位でまとまった作業ラベルを作りたい時。
- datasetとしてまとまったbatchを作りたい時。

### Mode B: Fast Queue

未ラベルclipをテンポよく処理する。

Best for:

- ラベル定義を試す時。
- とにかく作業例を増やしたい時。

### Mode C: Person ID Review

clipから人の特徴を見て、同じ人に同じperson IDが割り振られているか確認・修正する。

Best for:

- tracking IDがcameraや時間を跨いで安定しない時。
- activity annotation前にperson identityをある程度整えたい時。

### Mode D: Cluster Review

似たclipをまとめて見て、cluster単位でlabelを付ける。

Best for:

- annotation効率化。
- 先行研究の知見を活かす時。

## What To Keep From v0 Prototype

- manifest import
- simple clip viewer
- label buttons
- confidence
- note
- JSONL export
- localStorage autosave
- keyboard shortcuts

## What To Change From v0 Prototype

- clip queue中心ではなく、annotation batch中心にする。
- camera selectorやtime selectorを主導線にしない。
- provenance fieldsを常に表示する。
- 1 clip 1 labelだけでなく、work segmentを扱えるようにする。
- progressをclip数だけでなくcoverageとして見せる。
- person ID assignment / correctionの入口を作る。
- 手動保存またはautosaveで、ブラウザを閉じても再開できるようにする。
- cluster-level labelingの入口を作る。

## Open Design Questions

1. 最初の正式UIは `Batch Fill` を主画面にするか、`Fast Queue` を主画面にするか。
2. work segment編集はv1から入れるか、まずはclip全体label + noteに留めるか。
3. person ID reviewはactivity annotationの前工程として分けるか、同じUI内に軽く入れるか。
4. cluster suggestionsはv1 UIに入口だけ置くか、v2まで完全に待つか。
5. coverageは時間ベースで測るか、clip数ベースで測るか。
6. annotation結果は単一JSONLでよいか、batch summaryも別に出すか。
7. 途中保存はlocalStorageで十分か、progress JSONを手動保存・再読込できる形を必須にするか。

## Proposed First UI Direction

最初の正式UIは `Batch Fill` を主軸にする。

理由:

- 実際に提供できる入力が30分程度のJSON batchになりそう。
- 任意camera / 任意時間選択を前提にすると、実データ接続とズレる。
- 「いつ終わるのか分からない」問題を避けやすい。
- person / clip coverageが見えるため、作業効率が上がる。
- person ID correctionの必要性をUI上で扱える。

ただし、annotation作業が重くなりすぎないように、`Next unlabeled` を常に置き、Fast Queue的にも進められるようにする。
