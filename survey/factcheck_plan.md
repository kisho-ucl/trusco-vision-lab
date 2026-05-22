# SOTA Fact-check Plan

## Purpose

実装に入る前に、Deep Researchで得た研究地図が本当に妥当かを確認する。

特に、以下をファクトチェックする。

- 俯瞰・複数人物・長時間ID・作業認識を同時に扱う研究が本当に少ないか。
- 既存のSOTA手法を組み合わせれば本研究設定が解けるのか。
- tracking、action recognition、industrial HARの研究領域が本当に分断されているか。
- RGB、pose、trajectory、object / zone contextのどれが本研究に近いか。
- 修論で主張できる研究ギャップがどこにあるか。

## Why This Phase Is Needed

以前の査読対応で、手法の新規性や既存研究との差分を明確に説明する必要があった。

そのため、映像ベース作業認識では、いきなり実装に入らず、まず重要なsurvey論文と代表手法を自分で確認する。
Deep Researchは入口として使うが、最終的な主張はsurvey論文、代表論文、公式ベンチマーク、データセット仕様で裏取りする。

## Questions To Verify

### Q1. Multi-person trackingはどこまで成熟しているか

確認したいこと:

- 現在のMOTの主流はtracking-by-detectionなのか。
- ByteTrack、BoT-SORT、OC-SORTなどはどの条件で強いのか。
- 類似外観、遮蔽、長時間occlusion、退出・再入場はどこまで扱えるのか。
- 単一カメラMOTとmulti-camera trackingの限界は何か。

読むもの:

- MOT survey
- ByteTrack
- BoT-SORT
- OC-SORT
- DanceTrack
- WILDTRACK / multi-view tracking papers

### Q2. Multi-camera / BEV trackingは倉庫俯瞰映像に近いか

確認したいこと:

- 複数固定カメラからBEV上の人物軌跡を得る研究はどこまで進んでいるか。
- WILDTRACK, MultiviewX, TrackTacular, MVTrajecterなどの前提は何か。
- 実倉庫の俯瞰映像に適用する場合、camera calibrationやlayout差がどれくらい問題になるか。

読むもの:

- multi-camera tracking survey / review
- WILDTRACK
- TrackTacular
- MVTrajecter
- EarlyBird or related BEV multi-view tracking papers

### Q3. Action recognition / action detectionはどのタスクに分かれているか

確認したいこと:

- action classification, temporal action localization, spatio-temporal action detection, temporal action segmentationの違い。
- 本研究の「IDごとの長時間作業区間認識」はどのタスクに一番近いか。
- SlowFast, VideoMAE, TubeR, EVAD, STAR, LARTはそれぞれ何を入力し、何を出力するか。
- RGB特徴、pose特徴、trajectory特徴のどれが中心か。

読むもの:

- action recognition / action understanding survey
- SlowFast
- VideoMAE
- TubeR or STAR
- LART

### Q4. Weak / sparse supervisionは本当に使えるか

確認したいこと:

- video-level label、point label、timestamp label、作業区間ラベルで何ができるか。
- weakly supervised temporal action localizationは、長時間作業区間認識に使えるか。
- 少量ラベルでの限界は何か。

読むもの:

- weakly supervised temporal action localization survey or recent overview
- representative WTAL / point-supervised TAL papers
- VideoMAE and self-supervised video pretraining papers

### Q5. Industrial / retail HARは本研究設定にどこまで近いか

確認したいこと:

- 工場、組立、小売、倉庫に近い公開データセットは何か。
- それらは俯瞰、複数人物、長時間ID、作業ラベル、少量ラベルを満たすか。
- MERL Shopping, RetailAction, IKEA ASM, Assembly101, HA4M, CarDAなどの違い。

読むもの:

- industrial / manufacturing HAR survey
- MERL Shopping
- RetailAction
- IKEA ASM
- Assembly101
- HA4M
- CarDA

## Priority Survey Papers

まずはsurvey / reviewを読んで、領域の地図を自分で確認する。
以下は候補であり、本文確認後に重要度を更新する。

| Priority | Area | Survey / Review | Why Read It | Status |
|---|---|---|---|---|
| high | Action understanding | About Time: Advances, Challenges, and Outlooks of Action Understanding | action classification, TAL, STAD, temporal segmentationなどの全体像確認 | candidate |
| high | Action recognition | Action recognition: A comprehensive survey of tasks, methods, and challenges | action recognition系タスクの分類と近年手法の整理 | candidate |
| high | MOT | Deep Learning-Based Multi-Object Tracking: A Comprehensive Survey from Foundations to State-of-the-Art | MOTの主流、SOTA、tracking-by-detectionの整理 | candidate |
| medium | Multi-camera tracking | Multi-Object Multi-Camera Tracking Based on Deep Learning for Intelligent Transportation: A Review | multi-camera trackingの基本構成、評価、課題確認 | candidate |
| medium | HAR general | A Comprehensive Survey on Deep Learning Methods in Human Activity Recognition | sensor/vision含むHAR全体像と産業応用の確認 | candidate |
| medium | HAR general | Machine Learning for Human Activity Recognition: State-of-the-Art Techniques and Emerging Trends | vision/sensor/hybrid HARの最近の概観 | candidate |
| low | Sports action | A survey of video-based human action recognition in team sports | 多人数・時空間行動認識の参考。ただし倉庫とは領域差あり | candidate |

## Reading Output Template

各surveyを読んだら、以下を `survey/notes.md` に追記する。

```md
## Survey Reading Note: paper title

### Scope

このsurveyが扱う範囲:

### Task Taxonomy

本研究に関係するタスク分類:

### Important Methods

本研究に関係する代表手法:

### What Seems Solved

既存技術でできそうなこと:

### Remaining Gaps

本研究に関係する未解決課題:

### Relevance To Warehouse Setting

倉庫俯瞰映像との近さ:

### Citation Decision

- cite / maybe / no
- 理由:
```

## Stop Condition Before Implementation

実装に入る前に、最低限以下を満たす。

- high priority surveyを2本以上読む。
- MOT系の代表手法を2本以上読む。
- action recognition / action detection系の代表手法を2本以上読む。
- industrial / retail datasetを2つ以上確認する。
- 「既存技術でできること」「まだ難しいこと」を1ページで説明できる。
- 実装するbaselineを1つから2つに絞る。

## Expected Baseline Decision

ファクトチェック後に、以下のいずれかへ進む。

1. tracking baseline only:
   既存trackerで倉庫映像のID軌跡がどこまで取れるか確認する。

2. tracklet / trajectory baseline:
   既存trackerの出力から作業区間認識を行う。

3. RGB / tubelet baseline:
   人物cropまたはtubeletに対して既存action recognition特徴を使う。

4. pose baseline:
   俯瞰映像でpose推定が使えそうならpose系列を使う。

5. zone / object context baseline:
   作業エリア、棚、台車、検品台などの文脈を使う。

