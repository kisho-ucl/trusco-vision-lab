# TRUSCO-specific Survey Update

Source:

- `survey/deep-research-report_truso_v1.md`
- `docs/vision_context.md`

## One-sentence Conclusion

TRUSCOのような多数天井カメラ統合top-view基盤に近いwarehouse tracking / monitoring研究は存在するが、その長時間worker trajectoryをInspection / Sorting / Transportationのようなper-worker task labelsへ低アノテーションで接続する研究はまだ限定的である。

## What Became Clear

### 1. Tracking基盤に近い研究はある

物流倉庫の天井に多数の広角カメラを設置し、歪み補正や床面基準の整列を行い、倉庫全体でworker trajectoryを追う研究がある。

また、ceiling camera、object tracking、world model、digital twinを組み合わせたwarehouse monitoring研究もある。

これらは本研究のセンシング基盤や最終応用にかなり近い。

### 2. ただしtask recognitionまでは薄い

近いwarehouse研究は、主に以下に留まる。

- worker tracking
- asset tracking
- scene analysis
- trajectory visualization
- digital twin / monitoring

一方で、各worker IDに対して長時間trajectoryからInspect / Sort / Transportのような作業ラベルを推定する部分は、公開研究ではまだ薄い。

### 3. Logistics / factoryのtask recognitionは別方向に発展している

物流・工場の作業認識自体は存在する。
しかし、多くはwarehouse-wide top-viewではなく、以下に寄る。

- wearable sensor
- smartphone / IMU
- IoT device readings
- motion capture
- RGB-D
- workstation camera
- close-up camera
- egocentric video

代表例:

- OpenPack
- LARa
- InHARD
- MoIL

### 4. Constructionはsurveillance-based worker activity recognitionが厚い

建設分野では、site surveillance videosを使った以下の研究が比較的豊富。

- automated work sampling
- productivity analysis
- worker activity recognition
- pose-based activity analysis
- orientation / object / ReID based construction activity recognition
- multi-camera pose fusion

このため、方法論としてはconstructionが非常に参考になる。
ただし、domainは異なる。

### 5. Warehouse top-viewでfine-grained taskを読む難しさがある

Transportのような移動を伴う作業はtrajectoryで比較的扱いやすい可能性がある。

一方、InspectとSortはtrajectoryだけでは曖昧になりやすい。
理由:

- 同じ場所に滞在していても作業意味が違う。
- top-viewでは手元や商品状態が見えにくい。
- 注文書、商品、棚、台車、検品台などの文脈が必要。
- worker orientationやobject / zone contextが必要になる可能性がある。

## What Manual Findings Added

NotebookLM等で個別に確認した論文カードから、Deep Researchの結論に対して具体的な裏づけが増えた。

### A. 実環境の俯瞰映像から作業・行動を認識する研究は存在する

確認した例:

- Video dataset for the detection of safe and unsafe behaviours in workplaces
- Suspicious Human Activity Recognition: A Review
- Top-View Surveillance for Pedestrian Analysis and Public Safety Management

わかったこと:

- 実工場や監視カメラ映像から行動を分類する研究・データセットはある。
- top-view / overhead cameraにおける人物検出、追跡、pose、ReID、行動認識の研究は体系化されつつある。
- ただし、多くは安全/不安全行動、異常検知、歩行者分析、大きな動作の認識が中心。
- 検品・仕分け・搬送のような日常的かつfine-grainedな倉庫作業認識とはタスクが異なる。

### B. 建設分野では、俯瞰・監視映像からのworker activity recognitionがかなり進んでいる

確認した例:

- Automated Work Sampling via Two-Stream Convolutional Networks for Site Surveillance
- Vision-Based Construction Worker Activity Analysis via Body Posture
- Vision-Based Construction Activity Recognition via Attention and Re-Identification

わかったこと:

- 建設現場では、遠景・俯瞰・監視カメラから作業者活動を認識し、生産性評価やwork samplingに使う研究がある。
- worker tracking、pose、RGB / optical flow、orientation、object detection、ReIDを組み合わせるpipelineがある。
- 特に、行動そのものを大量ラベルで学習するのではなく、人・物体・姿勢・向き・ReID・空間関係ルールで作業を定義する方向は、本研究の低アノテーション化にかなり参考になる。
- ただし、対象は建設現場であり、作業カテゴリや環境が物流倉庫とは異なる。

### C. 物流・産業領域でも作業認識やVLM評価はあるが、IDごとの長時間top-view task recognitionとはズレる

確認した例:

- iSafetyBench
- Computer Vision in Logistics - viso.ai article
- warehouse / logistics specific search notes

わかったこと:

- 物流・産業分野では、CVによる追跡、検査、監視、ピッキング支援、human error detection、process modelingへの期待がある。
- VLMでも産業作業理解やzero-shot評価が始まっている。
- ただし、VLMはclip全体の質問応答であり、worker IDごとの長時間task segment recognitionではない。
- 最新VLMでもMaterial Handlingや複数人物interactionは難しい可能性が示唆される。
- warehouse / logisticsに限定すると、固定・俯瞰カメラによるper-worker activity recognitionより、wearable、egocentric、IoT、smart glasses、forklift sensor、workstation dataに寄る研究が多い。

### D. 「使えそうな方法」の輪郭が見えた

手作業調査から、本研究で試す価値がある方法は以下に絞られてきた。

1. trajectory + zone baseline
   - Transportのような移動作業に効きそう。

2. worker-object-zone relation
   - Inspect / Sortのようなfine-grained taskに必要そう。
   - 建設のobject / orientation / ReID based activity recognitionが参考になる。

3. pose / orientation
   - 作業姿勢や身体の向きは補助情報になり得る。
   - ただしtop-viewでは手元・関節が見えにくい。

4. RGB / optical flow / tubelet
   - construction work samplingでは有効例がある。
   - ただし倉庫top-viewではdomain gapが大きい可能性。

5. IMU / IoT weak label
   - OpenPackやMoILの流れと整合する。
   - IMU TrackとVision Trackをつなぐ自然な方向。

## Current Confidence

現時点で比較的自信を持って言えること:

- 倉庫のmulti-camera top-view trackingに近い研究は存在する。
- 倉庫・物流の作業認識研究も存在する。
- しかし、それらは同じ設定で統合されていない。
- 建設分野には、俯瞰/監視映像からworker activityを認識する参考手法が多い。
- warehouse / factoryでは、細かい作業を読むために近接カメラやセンサに寄る傾向がある。
- 本研究の独自性は、既存tracking基盤からper-worker task recognitionへ接続する部分に置けそう。

まだ言い切れないこと:

- 「完全に同じ研究が存在しない」と断定するには、さらに精読とScholar確認が必要。
- どの特徴が最も効くかは、実データでbaselineを試さないと分からない。
- Inspect / Sortがtop-viewからどこまで区別できるかは未確認。
- VLMやposeが実倉庫top-viewでどこまで使えるかは未確認。

## Updated Research Gap

> 多数の天井カメラを統合した倉庫全体のtop-view tracking基盤から、worker IDごとの長時間trajectoryを取得し、zone、object / equipment context、orientation、IMU由来のweak labelsなどを組み合わせて、少量アノテーションでInspection / Sorting / Transportationの作業区間を推定する研究はまだ限定的である。

## Updated Framing For Thesis

本研究は、以下の4領域の交差点にある。

1. warehouse multi-camera top-view tracking
2. logistics / industrial HAR
3. construction surveillance-based work sampling
4. digital twin / process mining / simulation optimization

既存研究はそれぞれの要素技術を持っているが、TRUSCOのようなwarehouse-wide top-view tracking基盤からper-worker task recognitionへ接続する部分はまだ薄い。

## Baseline Candidates

### Baseline 1: Tracking-only

Input:

- multi-camera detections
- global trajectory

Output:

- worker ID trajectory

Purpose:

- 既存tracking基盤でどこまで安定して動線が取れるか確認。

### Baseline 2: Trajectory + Zone

Input:

- trajectory
- velocity
- stop duration
- zone transition
- dwell time

Output:

- coarse task label

Expected:

- Transportは比較的認識しやすい可能性。
- Inspect / Sortは曖昧な可能性。

### Baseline 3: Worker-object-zone Relation

Input:

- worker trajectory
- work zones
- cart / shelf / inspection table proximity
- object detections
- orientation if available

Output:

- symbolic task label or task segment

Purpose:

- constructionのobject / orientation / ReID based activity recognitionやRetailActionのinteraction-centric approachを倉庫に移す。

### Baseline 4: IMU Weak Label

Input:

- camera trajectory
- smartphone IMU task estimation

Output:

- weakly supervised camera-side task recognition

Purpose:

- IMU研究とVision研究を接続する。
- 少量アノテーション問題に対応する。

## Updated Method Hypothesis From Construction Activity Recognition Reading

`Vision-Based Construction Activity Recognition via Attention and Re-Identification` から、倉庫作業認識に対する重要な示唆が得られた。

この論文は、行動を直接分類するのではなく、

> action = person x object x orientation x spatial relation

として、検出可能な構成要素からルールベースで作業を推定している。

この考え方は、倉庫作業に対しても有効そうである。
特に、作業者のcropやRGB embeddingだけを使うと、ビブス色や背景に引っ張られて、作業ではなく人IDや場所を学習する可能性がある。

そのため、本研究では以下の方向が有望。

- person maskで背景を除去する。
- color jitter / grayscaleなどでビブス色依存を抑える。
- trajectoryやzone滞在を基盤にする。
- 台車、商品、棚、検品台、仕分けエリアなどのobject / zone contextを明示的に使う。
- object label、距離、相対位置、orientationをinteraction featureとして使う。
- Inspect / Sortのような境界が曖昧な作業には、短時間clipではなく時系列モデルを使う。

更新後のコア仮説:

> 倉庫のtop-view映像では、作業者単体のRGB特徴ではなく、worker-object-zone interactionとtrajectory / temporal contextを明示的に使うことで、少量ラベル下でも作業認識がしやすくなる。

## Spatio-temporal Action Detection As General Baseline Area

一般のspatio-temporal action detectionも、SOTA寄りの比較軸として押さえる必要がある。

STEP、ACT-Detector、Track Aware Action Detectorのような手法から分かること:

- actionを単一フレームではなくtubelet / trackletとして扱う。
- RGBやoptical flowを用いて、人物bbox列にaction labelを付ける。
- track-awareな特徴集約により、複数人物の行動を個別に扱える。
- これは本研究の「worker trajectoryからtask labelへ接続する」方向と構造的に近い。

一方で、本研究とのズレも大きい。

- 対象はスポーツ、映画、一般動画が中心。
- 長時間worker ID trackingではなく、短〜中時間のaction tubeletが中心。
- dense bbox / action annotationを前提とする。
- top-view warehouse特有の手元不可視、作業領域依存、object / zone contextは扱わない。
- 少量アノテーションは主目的ではない。

したがって、これらは以下の役割を持つ。

- SOTA寄りの一般的なbaseline候補。
- tracklet / tubelet-based modelingの設計参考。
- RGB / optical flow / temporal aggregationの比較対象。
- ただし、最終的にはwarehouse-specific contextを追加する必要がある。

研究の立て方:

> 一般のSTAD手法はperson tubeletにaction labelを付ける枠組みを提供するが、warehouse top-viewではperson appearanceだけではなく、trajectory、zone、object relation、IMU weak labelsを追加しないとfine-grained task semanticsを捉えにくい。

## Group Activity Recognition As Interaction Reference

Group activity recognitionは、本研究の主軸からは少し外れる。
本研究では、シーン全体のactivityよりも、worker IDごとのtask segmentを推定したい。

ただし、以下の理由で押さえる価値はある。

- 複数人物の相互作用をどう特徴化するかの参考になる。
- Actor Relation Graphのように、person-person relationをグラフで扱う研究がある。
- 倉庫でも共同搬送、リレー作業、混雑、作業者間の干渉が起きる可能性がある。
- 将来的にworker-object-zone relationだけでなく、worker-worker relationを足す拡張に使える。

一方で、現在の修論での優先度は高くない。

- SBGARのようなtracking-free group activity recognitionは、per-worker ID task recognitionという目的とズレる。
- caption annotationや十分なラベルを前提とする研究は、low annotationという目的とズレる。
- Actor Relation Graphは有用だが、対象はスポーツ・collective activityであり、warehouse task semanticsとは違う。

位置づけ:

> group activity recognitionは主要比較対象ではなく、interaction modelingの周辺知識として扱う。まずはworker-object-zone interactionを主軸にし、必要に応じてworker-worker relationを追加する。

## Report Wording

今回、TRUSCOの実環境設定を明示して再調査したところ、倉庫のmulti-camera top-view trackingやceiling cameraによるdigital twin monitoringに近い研究は存在することが分かった。
一方で、それらは主に人物や荷物のtracking、trajectory visualization、scene analysisまでであり、各worker IDに対して長時間trajectoryから検品・仕分け・搬送のような作業ラベルを推定する部分はまだ薄い。

物流・工場の作業認識自体はOpenPackやLARaのように存在するが、多くはwearable、IoT、motion capture、RGB-D、作業台カメラなどに寄っており、倉庫全体のtop-view tracking基盤とは視点やスケールが異なる。
建設分野ではsurveillance videoを用いたworker activity recognitionやwork samplingが比較的多く、方法論として参考になるが、物流倉庫の検品・仕分け・搬送とは作業内容が異なる。

したがって、本研究では、すでに得られる長時間worker trajectoryを作業ラベルへ接続する部分、特にtrajectory、zone、object context、IMU weak labelsを組み合わせた低アノテーション作業認識に研究余地があると考えている。
