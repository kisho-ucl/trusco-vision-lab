# Reading Priority

Deep Researchの結果と追加確認をもとにした、最初に読む候補。
まずは網羅ではなく、研究地図とbaseline選定に効くものを優先する。

## Tier 1: まず読む

| Priority | Paper | Area | Why |
|---|---|---|---|
| 1 | Multi-Camera Worker Tracking in Logistics Warehouse Considering Wide-Angle Distortion | warehouse multi-camera tracking | TRUSCO設定に最も近いtracking基盤。多数天井カメラ、wide-angle distortion、global worker trajectoryが直結 |
| 2 | OpenPack: A Large-Scale Dataset for Recognizing Packaging Works in IoT-Enabled Logistic Environments | logistics HAR dataset | logistics task semantics、IoT readings、industrial dataset構築、low-label検討の基盤 |
| 3 | Preliminary Investigation of SSL for Complex Work Activity Recognition in Industrial Domain via MoIL | industrial SSL / low-label HAR | limited labels下のindustrial work recognitionに直接関係 |
| 4 | Top-View Surveillance for Pedestrian Analysis and Public Safety Management | top-view surveillance review | 俯瞰映像での検出・追跡・ReID・pose・行動認識・データセット・課題をまとめる辞書として重要 |
| 5 | Vision-Based Construction Activity Recognition via Attention and Re-Identification | construction worker activity recognition | ReID + posture/orientation + object relation + rule-based activity recognition。少量行動ラベル問題への構造化アプローチとして近い |
| 6 | Automated Work Sampling via Two-Stream Convolutional Networks for Site Surveillance | construction worker activity recognition | 実環境俯瞰監視カメラ + worker tracking + 作業ラベル + productivity analysisでかなり近い |
| 7 | On the Benefits of 3D Pose and Tracking for Human Action Recognition / LART | trajectory-centric action recognition | tracklet + pose + appearanceで行動認識する方向が本研究にかなり近いため |
| 8 | LARa: Creating a Dataset for Human Activity Recognition in Logistics Using Semantic Attributes | logistics HAR dataset | logistics作業ラベルとsemantic attributesの設計が参考になる |
| 9 | RetailAction | retail top-view HOI / action localization | top-view multi-viewでhuman-object interactionを中心に設計する発想が近い |
| 10 | Real-Time Warehouse Monitoring with Ceiling Cameras and Digital Twin for Asset Tracking and Scene Analysis | warehouse digital twin | task recognitionではないが、ceiling camera + digital twin接続の参考 |

## Tier 2: baseline候補として確認

| Paper / Method | Area | Why |
|---|---|---|
| ByteTrack | MOT | tracking baselineとして最有力候補 |
| BoT-SORT | MOT | ReID・appearance込みのtracking baseline候補 |
| OC-SORT | MOT | motion/occlusion寄りのtracking baseline候補 |
| VideoMAE | video SSL | 少量ラベル・自己教師あり動画表現の代表 |
| TubeR or STAR | spatio-temporal action detection | 人物tubelet + action labelの代表として確認 |
| PoseC3D | pose-based action recognition | poseを使う場合の代表候補 |

## Tier 3: 近いデータセット・応用例として確認

| Paper / Dataset | Area | Why |
|---|---|---|
| MERL Shopping Dataset / Multi-Stream Bi-Directional RNN for Fine-Grained Action Detection | overhead retail action detection | static overhead camera + fine-grained shelf actions。俯瞰作業認識としてかなり近いがsingle actor |
| INHARD: Industrial Human Action Recognition Dataset | industrial action recognition | top viewを含むindustrial action dataset。RGB + skeletonで作業認識に近い |
| Action Recognition for Human-Robot Teaming using InHARD | industrial action recognition | InHARDを使った作業認識応用。frame-level action label |
| WILDTRACK | multi-camera pedestrian tracking | 複数固定カメラ・calibration・BEV的評価の参照 |
| MERL Shopping | overhead retail action | 俯瞰・棚周り行動で近い |
| RetailAction | retail human-object interaction | 店舗・棚・商品文脈が近い |
| IKEA ASM | assembly action | object-aware作業認識の参照 |
| Assembly101 | procedural action segmentation | 長時間手順作業・区間ラベルの参照 |
| CarDA | industrial behavior understanding | 実工場データ・作業進捗の参照 |
| JRDB / JRDB-Act | tracking + action annotations | trackingとaction注釈が両方ある点で重要 |
| FATIGACTION | manufacturing action / fatigue | top/front/side viewsを含むmanufacturing action datasetとして参考 |
| IXMAS / UWA3D Multiview Activity II | cross-view action recognition | top viewを含む古典的multiview action dataset。実作業ではないが俯瞰視点の参考 |
| Video dataset for the detection of safe and unsafe behaviours in workplaces | workplace safety behavior dataset | 実工場の俯瞰固定IPカメラ映像。ID追跡や少量ラベルはないが、実環境データ例として参考 |

## Current Strategy

まずTier 1をNotebookLMでざっとスクリーニングする。
「これは本当に近い」と思ったものだけ精読する。

精読候補はおそらく以下。

- LART
- MOT survey
- action understanding survey
- multi-camera tracking review
- MERL Shopping or RetailAction
