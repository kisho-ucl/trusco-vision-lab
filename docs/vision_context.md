# Vision Context

## Source

`vision/SmartComp_Kawaguchi_letter2025upd2.pdf`

Title:

> Digitization Methods for a Logistics Warehouse Towards Digital Twin-Driven Optimization

## Project Setting

対象は、TRUSCO NAKAYAMAの大規模物流倉庫におけるデジタル化・最適化。

単一の巨大な俯瞰カメラで倉庫全体を見るのではなく、天井に多数の低コスト監視カメラを設置し、それらをキャリブレーション・歪み補正・位置合わせ・スティッチングすることで、倉庫フロア全体を俯瞰的に把握する。

この設定の重要な点:

- 実倉庫で継続運用されている。
- カメラは天井に多数設置されている。
- wide-angle cameraの歪み補正が必要。
- カメラ間の同期、位置合わせ、マスク、スティッチングが必要。
- 単なる動画解析ではなく、倉庫のdigital twin構築に向けた基盤である。
- 人・荷物・設備・作業・滞留・動線を統合して分析する。

## System Components In The Paper

### Camera Array Platform

大規模倉庫の1F inbound areaを対象に、天井カメラ群を設置してデータ収集を行う。

### Time Synchronization

低コスト監視カメラを多数用いるため、ハードウェア同期は使えない。
NTPと映像内timestampのOCRにより、フレーム時刻を補正する。

### Undistortion, Registration, Stitching

wide-angle cameraの歪みを補正し、倉庫の点群データや特徴点マッチングを用いてカメラ位置を登録する。
SuperPointとLightGlueを用いた特徴マッチングが使われている。

複数カメラ画像をマスク・alpha blendingにより統合し、倉庫全体のfloor conditionを俯瞰的に確認できるようにしている。

### Cooperative Annotation

天井カメラ・倉庫環境ではpretrained object detectorの性能が十分でないため、独自アノテーションが必要。
ただし、広角カメラと多数カメラによりannotation costが高い。

そこで、固定カメラであることを利用し、optical flowで動物体を抽出し、SimSiam、UMAP、K-Meansなどにより類似物体をまとめて提示するcooperative annotation frameworkを使う。

この枠組みにより、同程度のannotation volumeを維持しながらannotation timeを大幅に削減している。

### Synthetic Image Augmentation

動くforeground objectを背景画像に重ねることで、未ラベル物体のない自然なsynthetic imageを生成する。
天井カメラで位置が固定されていることを活用し、現実的な合成画像を作る。

### Multi-camera Object Tracking

人や荷物を複数カメラで認識・追跡する。
単一カメラ内trackingには既存手法を使えるが、wide-angle camerasを使うinter-camera trackingは通常手法の直接適用が難しい。

ByteTrackを改良し、認識結果のbounding box選択を工夫することで、実倉庫環境での追跡を実現している。
これにより、worker movement trajectoryを可視化できる。

### Smartphone IMU-based Task Estimation

カメラベースの倉庫デジタル化と並行して、作業者のスマートフォンIMUを用いた屋内測位・作業推定も行っている。

対象作業:

- inspection
- sorting
- transportation

腰に装着したスマートフォンから6軸加速度・角速度を収集し、5.12秒sliding windowで特徴量を抽出し、logistic regressionによりtask estimationを行う。

報告値:

- F1-score: 0.83

### Multi-camera Storage Area Occupancy Check

2Fから5Fでは天井が低く、天井カメラで全面を覆うには多数のカメラが必要になる。
そのため斜め上方カメラを用い、複数カメラ画像をprojective transformationでtop-down viewに変換して統合し、storage area occupancyを推定する。

### Digital Twin and Optimization

取得した作業者動線・作業情報・荷物情報をもとに、倉庫operations simulatorを構築する。
このsimulatorにworker shifts、warehouse layout、cargo informationを入力し、lead timeやlabor hoursを出力する。

さらに、Factorization Machine Quantum Annealingにより、worker shift scheduleなどをblack-box optimizationする。

報告値:

- lead time 最大37.4%削減
- residual cargo volume 最大95.5%削減
- total labor hours 最大14.3%削減

## Why This Setting Is Unique

この研究設定は、外部関連研究で多く見つかる単純な「俯瞰カメラ映像」とは異なる。

独自性:

- 倉庫天井に多数カメラを設置している。
- カメラ群から倉庫全体のtop-view表現を合成している。
- 実倉庫で継続的に運用されている。
- 人・荷物・作業・エリア滞留・動線を統合している。
- 最終目的が単なる認識ではなく、digital twinとsimulation-based optimizationである。

そのため、一般的なtop-view action recognition、construction worker activity recognition、retail action recognition、MOTとは似ている部分があるが、完全に一致する関連研究が出にくい。

## Connection To Current Thesis

現在の修論でのVision Trackは、以下の位置づけにできる。

> 既存のmulti-camera tracking基盤により、作業者の長時間trajectoryはある程度取得できる。このtrajectoryを、Inspection / Sorting / Transportationのような作業ラベルへ接続し、低アノテーションコストで倉庫作業をデータ化することが課題である。

これはIMU Trackとも自然につながる。

- IMU Track: 少量ラベル下で作業分類できるか。
- Vision Track: multi-camera top-view trajectoryや作業領域・物体文脈から、作業分類・作業区間推定ができるか。
- Future: IMUで得た作業推定を、映像側の弱教師や評価基準として使える可能性。

## Research Gap Based On This Setting

外部調査から見えていること:

- Constructionでは、俯瞰/監視カメラによるworker activity recognitionやwork samplingが比較的多い。
- Warehouse/logisticsでは、wearable sensor、egocentric video、RGB-D、作業台カメラ、forklift sensorなどに分散しやすい。
- Top-view surveillanceでは検出・追跡・大きな行動認識は進んでいるが、fine-grained warehouse task recognitionは少ない。

本研究の固有ギャップ:

> 多数の天井カメラを統合した倉庫全体のtop-view tracking基盤に対して、長時間trajectory、作業領域、物体・設備文脈、IMU由来の弱教師を組み合わせ、少量アノテーションで作業区間を認識する研究はまだ限定的である。

## Useful Wording For Progress Report

共同研究先では、倉庫天井に多数のカメラを設置し、キャリブレーションやスティッチングにより倉庫全体を真上から見たような俯瞰映像として統合している。
この基盤により、1時間単位の作業者動線や滞留を把握することはある程度可能になっている。

現在の関心は、得られたtrajectoryを単なる動線として扱うだけでなく、検品・仕分け・搬送といった作業内容と結びつけ、作業者の行動データとして蓄積することである。
将来的には、そのデータを人の行動モデル化や倉庫シミュレータに接続し、レイアウトやシフトの最適化に活用したい。

関連研究を調査すると、建設現場では俯瞰映像を用いた作業者活動認識が比較的多いが、物流倉庫において、多数カメラから統合されたtop-view trackingを用いて、作業者IDごとの長時間作業区間を少量ラベルで認識する研究はまだ直接的には見つかっていない。

