# 進捗共有: 物流倉庫top-view映像に基づく作業認識の調査

## 0. 要約

TRUSCOの倉庫では、天井に設置した多数の固定カメラをキャリブレーション・スティッチングし、倉庫全体をtop-view的に把握する基盤がある。
multi-camera trackingにより、作業者の長時間trajectoryや動線はある程度取得できる。

現在は、このtrajectoryを単なる動線ではなく、検品・仕分け・搬送のような作業ラベルへ接続する方法を検討している。

関連研究を調べると、以下はそれぞれ存在する。

- logistics / factoryの作業認識
- constructionのworker activity recognition
- spatio-temporal action detection
- video representation learning
- group activity recognition

一方で、TRUSCOのようなwarehouse-wide top-view tracking基盤から、worker IDごとの長時間task segmentを少量ラベルで推定する研究は、まだ限定的に見える。

## 1. 研究設定

対象:

- Inspect / 検品: 商品と注文書を照合する作業
- Sort / 仕分け: 商品を適切な場所に振り分ける作業
- Transport / 搬送: 荷物を載せた台車を運搬する作業

目標:

> 多数カメラ統合top-view tracking基盤から得られるworker trajectoryを、少ないアノテーションで作業ラベルへ接続する。

将来的には、作業者の行動データを蓄積し、人の行動モデル化、倉庫digital twin、シミュレーション、レイアウト最適化へつなげたい。

## 2. なぜ関連研究を調べているか

以前の査読対応で、手法の新規性や既存研究との差分を十分に説明する必要性を感じた。

そのため、実装に入る前に以下を確認している。

- 既存技術でどこまでできているか
- 自分の研究設定に近い先行研究はあるか
- どこに未解決課題が残るか
- どの手法をbaselineとして試すべきか
- どの特徴表現を使うべきか

## 3. 映像ベース行動認識の種類

映像ベースの行動認識は、大きく見ると以下のように分けられる。
特に重要なのは、「映像全体に何のラベルを付けるか」と「映像中のどこで、誰が、何をしているかを推定するか」は、かなり違う問題だという点である。

| 系統 | 何を予測するか | 代表例 | 所感 |
|---|---|---|---|
| Video-level action recognition | 短い動画クリップ全体に1つ、または複数の行動ラベルを付ける | [SlowFast Networks (2019)](https://arxiv.org/abs/1812.03982), [VideoMAE (2022)](https://arxiv.org/abs/2203.12602), [InternVideo2 (2024)](https://arxiv.org/abs/2403.15377) | 近年かなり強い。動画表現学習や大規模事前学習の研究が進んでおり、worker cropを分類するbaselineとして使いやすい。ただし、誰が・どこで・どの区間で作業しているかは直接扱わない。 |
| Spatio-temporal action detection / localization | 映像中の人物領域や時間区間に対して、行動ラベルを付ける | [AVA Dataset (2017)](https://arxiv.org/abs/1705.08421), [STAR (2024)](https://openaccess.thecvf.com/content/CVPR2024/html/Gritsenko_End-to-End_Spatio-Temporal_Action_Localisation_with_Video_Transformers_CVPR_2024_paper.html), [TAAD (2023)](https://openaccess.thecvf.com/content/WACV2023/html/Singh_Spatio-Temporal_Action_Detection_Under_Large_Motion_WACV_2023_paper.html) | 本研究の「誰が、何をしているか」に近い。ただし、一般動画・スポーツ・映画などが中心で、密なbbox/action annotationを前提にすることが多い。Video-level action recognitionほど、汎用的な基盤モデルをそのまま使えばよい、という形にはまだ見えない。 |
| Group activity recognition | 複数人物の関係性やシーン全体から、集団としての活動を認識する | [Actor Relation Graphs (2019)](https://arxiv.org/abs/1904.10117), [Social Scene Understanding (2016)](https://arxiv.org/abs/1607.04593) | スポーツや群衆行動でよく扱われる。主目的はシーン全体やグループ活動の認識だが、複数人の関係性を扱う点は、倉庫内での協調作業や人同士の干渉を考える上で参考になる。 |

現時点では、video-level action recognitionは強力なbaselineとして試せそうである。
一方で、本研究が目指すのは単に「この動画は搬送である」と分類することではなく、warehouse-wide top-view映像の中で、各worker IDについて作業区間を推定することである。
そのため、最終的にはspatio-temporal action detection / localizationに近い問題設定になるが、既存研究をそのまま適用するには、top-view、長時間tracking、少量アノテーション、作業領域や物体との関係といった条件が異なる。

## 4. 応用領域として見た関連研究

技術的な分類とは別に、応用領域として近い研究も整理した。
なお、研究室内のwarehouse multi-camera trackingは今回の「現状」として扱い、関連研究紹介では主に外部研究を見る。

| 応用領域 | 代表例 | 本研究との関係 |
|---|---|---|
| Warehouse digital twin / monitoring | Real-Time Warehouse Monitoring with Ceiling Cameras and Digital Twin [11] | ceiling cameraとdigital twin接続が近い。ただしper-worker task recognitionではない |
| Logistics / factory HAR | OpenPack [12], LARa [13], InHARD [14], MoIL [15] | 作業認識はあるが、wearable / IoT / RGB-D / workstation camera寄り |
| Construction worker activity recognition | Automated Work Sampling [16], Construction Worker Activity Analysis [17], Construction Activity Recognition [7] | 監視カメラ映像から作業認識・生産性分析を行う点でかなり参考になる |
| Top-view surveillance | Top-View Surveillance review [18] | 俯瞰映像における人物検出・追跡・ReID・行動認識の課題整理として参考になる |

## 5. 現時点の調査結果

### 5.1 Warehouse / logistics

倉庫のmulti-camera trackingやdigital twin monitoringに近い研究は存在する。
ただし、多くはworker trajectory、asset tracking、scene analysisまでであり、作業者IDごとの作業ラベル推定までは薄い。

一方、物流・工場の作業認識研究は存在するが、OpenPackやLARaのように、wearable sensor、IoT、RGB-D、作業台カメラ、motion captureなどに寄るものが多い。

### 5.2 Construction

建設分野では、surveillance videoを用いたworker activity recognitionやautomated work samplingが比較的多い。

理由として、建設現場では高所カメラで現場全体を監視し、生産性や安全性を評価する需要が強いと考えられる。

一方で、物流倉庫や工場では、手元、商品、棚、台車、注文書などが作業意味に強く関係するため、近接カメラやセンサに寄りやすい。

### 5.3 一般的なaction recognition / detection

一般的なvideo-level action recognitionでは、動画クリップ全体に行動ラベルを付ける強力なモデルが提案されている。
一方、spatio-temporal action detection / localizationでは、映像中の人物領域や時間区間にaction labelを付ける枠組みがある。

ただし、後者は主にスポーツ・映画・一般動画が対象であり、warehouse top-view、長時間ID維持、少量ラベル、作業領域・物体文脈までは扱っていない。

## 6. ピックアップした論文

### 6.1 Top-View Surveillance for Pedestrian Analysis and Public Safety Management [18]

top-view / overhead cameraにおける人物検出、追跡、ReID、pose、行動認識を整理したreview。

示唆:

- top-viewでは人物位置や大きな動作は扱いやすい。
- 一方で、顔情報や手元情報が弱く、fine-grainedな作業認識は難しい。
- high-quality annotated top-view datasetの不足も課題。

### 6.2 Automated Work Sampling via Two-Stream CNNs for Site Surveillance [16]

建設現場の俯瞰的な監視カメラ映像から、作業者をtrackingし、RGB + optical flowのtwo-stream CNNで作業ラベルを推定する研究。

示唆:

- 監視映像からworker activityを推定し、生産性評価に使うpipelineは存在する。
- ただし、tracking初期化は手動で、少量ラベルではない。

### 6.3 Construction Activity Recognition Method Based on Object Detection, Attention Orientation Estimation, and Person Re-Identification [7]

建設現場の固定カメラ映像を対象に、作業員・資材の検出、作業員の姿勢・向き推定、Person Re-IDを組み合わせ、作業員と物体の位置関係や注意方向から作業内容を推定する研究。

特徴:

> action = person x object x orientation x spatial relation

行動をRGB特徴から直接分類するのではなく、検出可能な構成要素からルールベースに作業を定義している。

示唆:

- 倉庫でも、作業者、台車、商品、棚、検品台、仕分けエリアの関係を使って作業認識する発想につながる。
- 一方で、ルールや閾値に依存し、時系列文脈は弱い。

### 6.4 LART [6]

人物の追跡結果やposeを利用してaction recognitionを行う研究。

示唆:

- 複数personを含む映像から、人物ごとのactionを認識する方向性として参考になる。
- ただし、pose推定を使うため実装コストが高く、top-view倉庫映像で安定するかは不明。

### 6.5 VideoMAE [2]

自己教師あり動画表現学習の代表的手法。

示唆:

- worker crop sequenceやtracklet clipから動画特徴を抽出するbaselineとして使える可能性がある。
- ただし、person cropやCLIP / CNN特徴をそのまま使うと、人IDや背景を拾う可能性がある。

## 7. 予備実験から見えている問題

CNN / CLIP embeddingをそのまま使うと、作業ではなく人ごとにクラスタができる可能性がある。

原因候補:

- ビブス色など、人IDに対応する外観特徴。
- 同じ作業者が同じ場所にいることによる背景バイアス。
- モデルが作業ではなく、人や場所を学習している。

そのため、単純な

> person appearance -> task

では弱い可能性がある。

## 8. 手法アイデア

現時点で考えている方向:

> Interaction-aware vision-based warehouse task recognition

単純な人物crop分類ではなく、

> worker trajectory + zone + nearby objects + orientation + temporal context -> task

として作業を認識する。

### 8.1 Trajectory + zone

まず、worker trajectory、speed、stop duration、dwell time、zone transitionでTransportが取れるか確認する。

Inspect / Sortがtrajectoryだけでどれだけ曖昧かも確認する。

### 8.2 Masked person crop

person maskにより背景を除去し、背景バイアスを減らす。

候補:

- SAMなどでbboxからperson maskを作る。
- grayscale / color jitter / HSV変換でビブス色依存を抑える。

### 8.3 Related item / object ID

作業者と周辺物体・設備・作業領域の関係を明示的に使う。

入力候補:

- nearby object IDs
- object labels
- distance
- relative position
- zone

例:

- 台車との近接
- 検品台への滞在
- 棚への接近
- 商品/箱とのinteraction
- 仕分けエリアでの往復

### 8.4 Temporal model

Inspect / Sortの境界は曖昧なので、過去数秒から数十秒のtrajectory / object / zone featureを使う。

候補:

- TCN
- Transformer
- HMM / HSMM

## 9. IMUとの接続

既存のIMU研究では、Inspection / Sorting / Transportationの作業推定を扱ってきた。

Vision側では、IMU task estimationを以下に使える可能性がある。

- weak label
- pseudo label
- evaluation reference
- cross-modal teacher

つまり、

> IMUで得た作業推定を、top-view映像側の少量ラベル学習に使う

という方向が考えられる。

## 10. 現時点の研究ギャップ

現時点では、以下のように整理している。

> warehouse multi-camera top-view trackingに近い研究は存在するが、その長時間worker trajectoryを、Inspection / Sorting / Transportationのようなper-worker task labelsへ少量アノテーションで接続する研究はまだ限定的である。

また、

> 一般のspatio-temporal action detection / localizationは「どこで、誰が、何をしているか」を推定する枠組みを提供するが、warehouse top-viewではperson appearanceだけではなく、trajectory、zone、object relation、IMU weak labelsを追加しないとfine-grained task semanticsを捉えにくい。

## 11. 今後やること

- 重要論文を精読する。
- VideoMAEなどのvideo-level modelと、spatio-temporal action detection系のbaselineとしての使い方を整理する。
- 既存tracking outputの形式を確認する。
- trajectory + zoneでTransportが取れるか確認する。
- masked person crop / related object IDを使った特徴設計を検討する。
- IMU task estimationをVision側のweak labelとして使えるか確認する。

## 参考文献・リンク

[1] SlowFast Networks for Video Recognition  
https://arxiv.org/abs/1812.03982

[2] VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training  
https://arxiv.org/abs/2203.12602

[3] ACT-Detector: Spatio-Temporal Action Localization via Anchor Cuboids  
https://arxiv.org/abs/1702.02911

[4] STEP: Spatio-Temporal Progressive Learning for Video Action Detection  
https://arxiv.org/abs/1904.09288

[5] Spatio-Temporal Action Detection Under Large Motion  
https://arxiv.org/abs/2303.03427

[6] On the Benefits of 3D Pose and Tracking for Human Action Recognition  
https://arxiv.org/abs/2304.01199

[7] Construction Activity Recognition Method Based on Object Detection, Attention Orientation Estimation, and Person Re-Identification  
https://www.mdpi.com/2075-5309/14/4/1014

[8] RetailAction: Dataset for Multi-View Spatio-Temporal Localization of Human-Object Interactions in Retail  
https://arxiv.org/abs/2506.07787

[9] Actor Relation Graphs for Group Activity Recognition  
https://arxiv.org/abs/1904.10117

[10] Multi-Camera Worker Tracking in Logistics Warehouse Considering Wide-Angle Distortion  
https://arxiv.org/abs/2505.16910

[11] Real-Time Warehouse Monitoring with Ceiling Cameras and Digital Twin for Asset Tracking and Scene Analysis  
https://www.mdpi.com/2305-6290/9/2/75

[12] OpenPack: A Large-Scale Dataset for Recognizing Packaging Works in IoT-Enabled Logistic Environments  
https://ieeexplore.ieee.org/document/10494448

[13] LARa: Creating a Dataset for Human Activity Recognition in Logistics Using Semantic Attributes  
https://www.mdpi.com/1424-8220/20/15/4083

[14] InHARD - Industrial Human Action Recognition Dataset in the Context of Industrial Collaborative Robotics  
https://ieeexplore.ieee.org/document/9209368

[15] Preliminary Investigation of SSL for Complex Work Activity Recognition in Industrial Domain via MoIL  
https://ieeexplore.ieee.org/document/10503440

[16] Towards Efficient and Objective Work Sampling: Recognizing Workers' Activities in Site Surveillance Videos with Two-Stream Convolutional Networks  
https://www.sciencedirect.com/science/article/pii/S0926580518300738

[17] Vision-Based Construction Worker Activity Analysis Informed by Body Posture  
https://ascelibrary.org/doi/10.1061/%28ASCE%29CP.1943-5487.0000898

[18] Top-View Surveillance for Pedestrian Analysis and Public Safety Management  
https://www.mdpi.com/1424-8220/23/2/969
