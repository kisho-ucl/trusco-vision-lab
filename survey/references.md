# References To Check

Deep Researchで出た候補。
まだ最終引用リストではない。

## Tracking

| Status | Year | Paper / Method | Why It Matters | Limitation |
|---|---:|---|---|---|
| candidate | 2020 | FairMOT | detection and ReIDを統合した代表的tracker | action labelなし |
| candidate | 2022 | ByteTrack | tracking-by-detectionの強力なbaseline | action labelなし |
| candidate | 2022 | BoT-SORT | ReIDとmotion compensationを含む強力なtracker | action labelなし |
| candidate | 2023 | OC-SORT | occlusionやnon-linear motionへの頑健性 | action labelなし |
| candidate | 2022 | TrackFormer | Transformer queryによるend-to-end tracking | 長期occlusionや大移動に弱い可能性 |

## Multi-view / BEV Tracking

| Status | Year | Paper / Method | Why It Matters | Limitation |
|---|---:|---|---|---|
| candidate | 2024 | TrackTacular | 複数視点をBEVに統合したtracking | action labelなし |
| candidate | 2025 | MVTrajecter | BEV pedestrian trackingの新しい方向 | action labelなし |
| candidate | - | WILDTRACK | calibrated multi-camera tracking dataset | action labelなし、1 scene |

## Action Recognition / Detection

| Status | Year | Paper / Method | Why It Matters | Limitation |
|---|---:|---|---|---|
| candidate | 2019 | SlowFast | video action backboneの代表 | ID trackingなし |
| candidate | 2022 | VideoMAE | 少量ラベルに有望な自己教師あり動画表現 | per-ID action出力なし |
| candidate | 2022 | TubeR | tubeletとactionを出す | 長時間worker ID維持は主対象でない |
| candidate | 2023 | EVAD | efficient video action detector | industrial labelsではない |
| candidate | 2024 | STAR | proposal-free tubelet action localization | 施設全体のID維持は範囲外 |
| candidate | 2023 | LART | tracking + pose + appearanceを行動認識に使う | object manipulationの作業意味は弱い可能性 |

## Industrial / Retail Datasets And Studies

| Status | Dataset / Paper | Why It Matters | Limitation |
|---|---|---|---|
| high | Multi-Camera Worker Tracking in Logistics Warehouse Considering Wide-Angle Distortion | 多数天井カメラ・wide-angle distortion・倉庫全体worker trackingでTRUSCO設定に最も近い | task recognitionは扱わない |
| high | Real-Time Warehouse Monitoring with Ceiling Cameras and Digital Twin for Asset Tracking and Scene Analysis | ceiling camera + asset tracking + digital twinで最終応用が近い | per-worker task labelは扱わない |
| high | OpenPack | logistics packaging work recognition、IoT / IMU / depth / LiDARを含む大規模dataset | workstation / single-worker寄り、warehouse-wide top-viewではない |
| high | MoIL for complex work activity recognition | limited labels下のindustrial HAR / SSLとして重要 | vision top-view trackingではない |
| high | LARa | logistics HAR dataset、semantic attributesが参考 | motion capture / wearable寄り |
| candidate | MERL Shopping | fixed overhead + retail interactionで近い | 小規模 |
| candidate | Multi-Stream Bi-Directional RNN for Fine-Grained Action Detection | MERL Shoppingを使ったoverhead fine-grained temporal action detection | single actor、lab retail setting |
| candidate | INHARD | top viewを含むindustrial human action recognition dataset | 組立/HRI寄り、多人数trackingではない |
| candidate | Action Recognition for Human-Robot Teaming using InHARD | industrial action recognition応用として近い | InHARD依存、frame-level label前提 |
| candidate | RetailAction | 店舗・棚interactionが近い | 新しく標準性は未確認 |
| candidate | IKEA ASM | fine-grained assembly | 作業台中心、多人数trackingではない |
| candidate | Assembly101 | action segmentationに強い | ceiling-view multi-workerではない |
| candidate | HA4M | multimodal manufacturing | 単一assembly中心 |
| candidate | CarDA | 実工場データ | 倉庫floor trackingとは異なる |
| candidate | FATIGACTION | manufacturing action recognitionでtop/front/side viewsを含む | fatigue評価寄り、倉庫作業ではない |
| reference | Video dataset for the detection of safe and unsafe behaviours in workplaces | 実工場の俯瞰固定IPカメラRGB映像による安全/不安全行動データセット | 手法提案ではない、ID追跡・少量ラベルは扱わない |
| candidate | JRDB / JRDB-Act | tracking + actionの統合注釈 | mobile robot視点、industrialではない |

## Public Dataset Strategy

公開データだけで本研究設定を完全には満たしにくい。

現実的には、

1. MOT系データでtracking部分の既存技術を確認する。
2. AVA / JRDB-Act / MERL / Assembly系でaction部分の近い設定を確認する。
3. 自前の倉庫映像で、tracklet単位の作業認識として統合評価する。

## Feature / Representation View

関連研究を、作業認識に使う特徴表現の観点で整理する。
ここでは「主に何を入力・中間表現として使っているか」を見る。
最終的な分類は論文本文確認後に更新する。

| Area | Paper / Method | Main Feature Type | Uses ID / Track? | Output | Relevance to Warehouse Work Recognition | Current Read |
|---|---|---|---|---|---|---|
| MOT | FairMOT | RGB image + detection / ReID feature | yes | box + ID | tracking基盤。作業ラベルは別途必要 | candidate |
| MOT | ByteTrack | RGB image detections + motion association | yes | box + ID | 人物軌跡を作るbaseline候補。低信頼検出も使う | candidate |
| MOT | BoT-SORT | RGB detections + motion + ReID appearance | yes | box + ID | 作業服が似た環境でReIDが効くか確認したい | candidate |
| MOT | OC-SORT | RGB detections + motion / observation-centric association | yes | box + ID | 遮蔽や交差時の追跡baseline候補 | candidate |
| MOT | TrackFormer | RGB frame features + transformer track queries | yes | box + ID | end-to-end trackingの比較対象。行動は出ない | candidate |
| Multi-view tracking | WILDTRACK | multi-camera RGB + calibration / ground-plane position | yes | multi-view pedestrian location / ID | 複数固定カメラ・BEV追跡の参照 | candidate |
| Multi-view tracking | TrackTacular | multi-view RGB features lifted to BEV + motion / appearance | yes | BEV tracks | 倉庫の複数カメラ俯瞰追跡に近い。作業ラベルは出ない | candidate |
| Multi-view tracking | MVTrajecter | BEV trajectory + appearance / motion costs | yes | BEV tracks | trajectoryを明示的に使う点が近い。作業認識は別 | candidate |
| Video action recognition | SlowFast | RGB video spatio-temporal features | no | clip-level action label | RGB動画特徴の代表。per-ID化にはtrackingが必要 | candidate |
| Video SSL | VideoMAE | RGB video masked autoencoding features | no | pretrained video representation | 少量ラベル用のRGB表現学習として有望 | candidate |
| Spatio-temporal action detection | TubeR | RGB video features + action tubelets | partially | person tubelet + action label | 人物ごとの行動検出に近いが、長時間ID維持は主目的でない | candidate |
| Spatio-temporal action detection | EVAD | RGB video / ViT features | partially | person action detection | 効率的なRGB action detector。倉庫作業ラベルとはずれる | candidate |
| Spatio-temporal action localization | STAR | RGB video features + predicted tubelets | partially | action tubelet | tubelet単位のactionには近いが、worker ID継続とは別 | candidate |
| Trajectory-centric action | LART | tracklet + 3D pose + appearance feature | yes | action label on tracked person | tracking結果を行動認識に使う点がかなり近い | candidate |
| Pose-based action | PoseC3D | skeleton / pose heatmap sequence | no / optional | action label | 俯瞰で骨格が安定すれば有望。遮蔽・低解像度が懸念 | candidate |
| Retail / overhead | MERL Shopping | overhead RGB video + human-object interaction context | partially | action detection | 俯瞰・棚周りという意味で近い。規模は小さい | candidate |
| Retail / HOI | RetailAction | RGB video + human-object interaction | partially | spatio-temporal interaction / action | 店舗・棚・商品文脈が近い。倉庫作業へ転用可能性 | candidate |
| Assembly HAR | IKEA ASM | RGB video + pose / object / action annotations | no / limited | assembly action labels | object-aware作業認識の参考。多人数追跡ではない | candidate |
| Procedural action | Assembly101 | multi-view RGB + egocentric video + hand / action labels | no / limited | action segmentation | 長時間手順作業の参考。俯瞰多人数ではない | candidate |
| Manufacturing HAR | HA4M | RGB-D + skeleton + point cloud + multimodal signals | no / limited | activity label | RGB-Dや骨格を含む製造HARの参考 | candidate |
| Industrial behavior | CarDA | multi-camera RGB-D + motion capture / pose / task progress | no / limited | posture / action / task progress | 実工場に近いが、倉庫floor trackingとは異なる | candidate |
| Integrated robot dataset | JRDB / JRDB-Act | RGB / 3D boxes / tracking / action labels | yes | tracking + action / social labels | trackingとaction注釈が両方ある点で重要。固定俯瞰ではない | candidate |

## Representation Takeaways

- RGB video features are the mainstream for general video action recognition and spatio-temporal action detection.
- Tracking methods often use RGB detections, appearance features, and motion, but their output is box + ID rather than work labels.
- Pose / skeleton features are attractive for action recognition, but overhead warehouse video may make pose estimation unstable.
- Trajectory features are promising for movement-heavy labels such as transport, walking, stopping, and staying near a zone.
- Object / zone context is likely needed for fine-grained work labels such as inspect vs sort.
- For this thesis, the likely starting point is tracklet / trajectory as the backbone, then compare or add RGB crop features, pose features, and zone / object context.

## Overhead / Industrial Action Recognition Candidates

Tracking寄りではなく、俯瞰映像や産業環境の「作業認識」に近い候補。

| Candidate | Setting | Feature / Annotation | Why It Is Close | Main Gap |
|---|---|---|---|---|
| MERL Shopping Dataset | static overhead camera, grocery shelf, lab retail | RGB video, temporal action intervals | 俯瞰 + 棚周り + fine-grained action detection | single actor、短め動画、倉庫ではない |
| INHARD | industrial assembly / HRI, top + side views | RGB, skeleton, action labels | top viewを含む産業作業認識 | 組立中心、多人数ID追跡ではない |
| Action Recognition for Human-Robot Teaming using InHARD | industrial HRI action recognition | image-based cameras, frame-level labels | 実用的なworker action recognitionに近い | InHARD前提、長時間多人数trackingではない |
| RetailAction | real convenience store / retail HOI | RGB, human-object interaction / spatio-temporal localization | 棚・商品・人の相互作用が近い | 小売、標準性や入手性を要確認 |
| HA4M | manufacturing HAR | RGB-D, skeleton, point cloud, multimodal | 製造作業認識とmultimodal特徴の参考 | 単一作業・作業台寄り |
| FATIGACTION | manufacturing action / fatigue | top/front/side views | top viewありの製造作業データ | fatigue評価寄り、倉庫ではない |
| Video dataset for the detection of safe and unsafe behaviours in workplaces | real manufacturing workplace, overhead fixed IP camera | RGB clips, 8 safe/unsafe behavior labels | 実産業環境 + 俯瞰固定カメラ + 作業者行動ラベルという点で参考 | dataset paper、clip label中心、ID trackingなし、low-label手法なし |
| IXMAS / UWA3D Multiview Activity II | multiview / top-view action recognition | RGB or depth, top view included | 俯瞰視点のaction recognition検証に使える | 日常動作、作業認識ではない |
