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

### Status

In Progress (Implementation complete, undergoing testing)

### Discovery Results (Summary)
* **トラッキングJSON座標**: `"original_bbox"` または `"bbox_list"` に格納されているローカル座標 `[cx, cy, w, h]` をそのままトリミングに使用可能。
* **フレーム特定**: `orig_frame = frame_id * 2 + 1` とし、経過時間と `ts_cache` から動画内の正確な `(vid_idx, frm_idx)` を逆引き。
* **マッピングの解決**: `/mnt` が Read-Only であるため、リポジトリ内に `config/dataset_mapping.json` を設けて `Result_ID` から実験日時のマッピングを解決する。

### Scope

#### In

* **前処理スクリプトの開発**: `tools/annotation/generate_manifest.py` の新規作成。
  * 引数に `--result_id` (例: `78`), `--use_frame` (フレーム間隔), `--limit_tracks` (テスト用トラック数上限) などを取る。
  * `Result_ID` をキーにマッピング定義ファイルを読み込み、入力データ・動画・`ts_cache` の物理パスおよび開始時刻を特定する。
  * トラッキングJSON内の各 `track_id` とカメラごとに、人物が映っている区間のトリミング画像（JPG）を連番で切り出し保存する。
  * ブラウザUIがインポート可能な `manifest.json` を自動生成する。
* **マッピング定義ファイルの作成**: `tools/annotation/config/dataset_mapping.json` の作成。
  * `Result_ID="78"` に対応するメタデータ (`date="2024-10-03"`, `start_time="10:00:00"`, `ts_cache`パス等) を記述する。
* **中間・結果データの保存場所**:
  * 切り出した一時画像とマニフェストは、共有マウント空間の `/mnt/bigdata/01_projects/2024_trusco/task_annotation_clips/<Result_ID>/` に保存する。
  * 人間がアノテーションした最終成果物の JSONL は、`/mnt/bigdata/01_projects/2024_trusco/task_annotation/<Result_ID>/` に保存する。
  * 既存のデータセット（`track_result` 等）や動画ファイルは一切変更しない。

#### Out

* クリップの自動結合や時間的なセグメンテーション（まずはトラックが存在する全範囲を単純に切り出す）。
* アノテーションUI側の大幅な変更（v1のUI接続は別マイルストーンとする）。

### Data / Interfaces

#### 物理保存ディレクトリ構成
```text
dataset/
├── task_annotation_clips/          # 一時切り出しデータ（巨大）
│   └── <Result_ID>/                # 例: 78
│       ├── manifest.json           # UI用 manifest
│       └── clips/                  # トリミングされた連番画像
│           └── track_<id>_<camID>/ # トラック・カメラ別フォルダ (例: track_148_A1)
│               ├── 000001.jpg
│               └── ...
└── task_annotation/                # 最終成果物（クリーン・軽量）
    └── <Result_ID>/
        └── annotations.jsonl       # 人間がアノテーションした結果
```

#### 生成される `manifest.json` のスキーマ
```json
{
  "version": 1,
  "labels": ["Inspect", "Sort", "Transport", "Other", "Unclear"],
  "clips": [
    {
      "clip_id": "78_track_148_A1",
      "batch_id": "78",
      "person_id": "track-148",
      "original_tracking_id": "148",
      "camera_id": "A1",
      "start_time": "2024-10-03T10:00:00.2+09:00",
      "end_time": "2024-10-03T10:01:25.4+09:00",
      "duration_sec": 85.2,
      "image_folder": "clips/track_148_A1",
      "frame_count": 426,
      "frame_indices": [1, 3, 5, 7, 9],  // 連番画像の元々の動画フレーム番号
      "zone_hint": "unknown"
    }
  ]
}
```

### Success Criteria

* コマンド `python generate_manifest.py --result_id 78 --use_frame 5 --limit_tracks 3` がエラーなしで動作完了すること。
* 指定された共有空間 `/home/kisho_ucl/kisho_ws/trusco-vision-lab/dataset/task_annotation_clips/78/` ディレクトリが作成され、その下に `manifest.json` と、テスト用に指定したトラックの `clips/` ディレクトリ（連番JPG入り）が正しく配置されること。
* 生成された `manifest.json` が定義したスキーマを満たしており、画像パスやフレーム数がトラッキング結果と一致していること。

### Open Questions

1. **ブラウザUIからの画像読み込み**: Webブラウザはセキュリティ制限（CORS）のためローカルファイル（`file://`）や異なるドメインの物理ディレクトリの画像を直接読めない場合があります。アノテーションUIを起動する際に、簡易的なローカルWebサーバー（例: `python -m http.server`）を立ち上げて `task_annotation_clips/` をホストする運用にするか。
2. **切り出すフレームの間引き間隔**: トラッキングデータ自体は 0.2秒（5fps）間隔で存在しますが、アノテーション作業用としては `--use_frame 5`（1秒に1枚）程度に間引いて切り出すのが適切か。

### Implementation Gate

- [x] Server data discoveryが終わっている。
- [x] 実tracking outputのsample rowとschemaを元に切り出しロジックを設計した。
- [x] v1で作るmanifest schemaと物理フォルダ構造を決定した。
- [x] 中間データの出力先として `/mnt` 内の安全な新規ディレクトリ `task_annotation_clips/` を決定した。
- [x] ユーザーから確認論点へのフィードバック（Go）を得ている。

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
