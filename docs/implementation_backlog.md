# Implementation Backlog

実装・実験・ツール化の候補を置く場所。

`DASHBOARD.md` は今日何をするかを決める軽い入口にして、候補一覧や細かい案はここに置く。

## Candidate Baselines

| Baseline | Input | Goal | Status |
|---|---|---|---|
| Trajectory + zone | worker trajectory, zone map | Transport / non-Transport and coarse task classification | candidate |
| RGB crop / VideoMAE | worker-centered clips | visual feature baseline | candidate |
| Masked person crop | person mask sequence | reduce background bias | candidate |
| Interaction features | object label, distance, relative position, zone | distinguish Inspect vs Sort | candidate |
| Environment state transition | object / zone visual state before-after | capture task evidence from scene changes | new candidate |
| LART-style tracklet | tracklet + appearance + optional pose | SOTA-ish tracklet baseline | candidate |
| IMU weak label | camera track + IMU task estimate | low-annotation supervision | candidate |

## Candidate Tools / Modules

| Module | Purpose | Status |
|---|---|---|
| Clip extractor | tracking resultからworker IDごとの時系列clipを切り出す | candidate |
| Annotation UI | clipを提示し、Inspect / Sort / Transport等のラベルを付ける | prototype v0 |
| Feature extractor | CLIP / VideoMAE / trajectory featureを抽出する | candidate |
| Clustering assistant | 類似clipをまとめて提示し、annotation効率を上げる | candidate |
| Dataset exporter | annotation済みデータを学習・評価用formatへ変換する | candidate |
| TRUSCO skill docs | calibration / stitching / tracking / detection等の基盤技術を使える形で文書化する | candidate |

## First Implementation Candidates

### 1. Clip Extraction

tracking結果から、worker IDごとの短いclipを切り出す。

Minimum output:

- worker ID
- start / end time
- bbox crop sequence
- global position / zone if available
- metadata json

### 2. Annotation Workflow

clipを提示し、ラベル候補を選ぶだけでannotationできる最小UIを作る。

Minimum labels:

- Inspect
- Sort
- Transport
- Other / unclear

Current assets:

- Spec: [specs/semi_auto_annotation/SPEC.md](specs/semi_auto_annotation/SPEC.md)
- Mini Specs: [specs/semi_auto_annotation/MINI_SPECS.md](specs/semi_auto_annotation/MINI_SPECS.md)
- Prototype: [tools/annotation](../tools/annotation/README.md)

### 3. Trajectory + Zone Baseline

映像特徴に入る前に、trajectoryだけでどこまで作業が分かるか確認する。

Features:

- speed
- stop duration
- dwell time
- zone transition
- distance traveled

### 4. Visual Baseline

worker crop sequenceから動画特徴を抽出し、作業分類を試す。

Candidate features:

- CNN / CLIP frame features
- VideoMAE features
- masked person crop

### 5. Environment State Transition

作業者周辺のscene / object stateのbefore-afterを特徴として使う。

Examples:

- box / shelf / cart / gate / container state change
- nearby object appearance change
- zone occupancy change
