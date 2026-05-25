# Research Plan

## One-line Theme

物流倉庫における人手作業を、少ないアノテーションコストで認識するためのマルチモーダル作業認識手法の検討。

## Core Research Question

実環境の物流倉庫において、IMU時系列および映像データを用いて、少ないアノテーションコストで作業認識を実現するにはどうすればよいか。

## Sub Questions

1. IMU時系列に対して、SimCLRによる自己教師あり事前学習はラベル削減時の分類性能を改善するか。
2. CNNによる短期特徴抽出とTransformerによる長期文脈モデリングは、作業時間が数分から数十分に変動する検品・仕分け・搬送の分類に有効か。
3. 継続的に蓄積される映像データに対して、姿勢・軌跡・時間文脈などの中間表現を用いることで、少ないアノテーションで作業認識へ接続できるか。

## Thesis Main Claim

実環境の物流倉庫における作業認識では、密な人手アノテーションを前提にせず、自己教師あり学習や中間表現を活用することで、IMU時系列および映像データから低アノテーションコストで作業ラベルを推定できる。

## Contribution Candidates

- 数分から数十分継続し、現場状況に応じて切り替わる倉庫作業を対象にした問題設定。
- IMU時系列におけるSimCLR事前学習によるラベル不足への対応。
- CNNとTransformerを組み合わせた、短期動作と長期文脈の分離モデリング。
- 映像データに対する低アノテーション作業認識の初期検討。
- IMUとVisionを、アノテーションコスト削減という共通軸で整理した実環境作業認識の研究設計。

## Evaluation Design

Primary metrics:

- Macro-F1
- Weighted-F1

Validation:

- LOSO: Leave-One-Subject-Out
- Data reduction: 使用ラベル量を段階的に削減

Recommended comparisons:

- supervised CNN
- supervised CNN + Transformer
- SimCLR CNN + classifier
- SimCLR CNN + Transformer
- optional: simple statistical / classical ML baseline

## Track 1: IMU

### Input

- accelerometer x/y/z
- gyroscope x/y/z
- fixed-size windows
- subject-level split

### Labels

- Inspect: 商品と注文書を照合する作業
- Sort: 商品を適切な場所に振り分ける作業
- Transport: 荷物を載せた台車を運搬する作業

作業は数分で切り替わる場合もあれば、数十分継続する場合もある。
一定の役割分担は存在するが、現場状況に応じて柔軟に交替される。

### Model

1. CNN encoder learns local motion representation.
2. SimCLR pretrains the encoder using unlabeled IMU windows.
3. Transformer aggregates sequential window embeddings.
4. Classifier predicts Inspection, Transport, or Sorting.

### Main Risks

- 長時間ラベルと短時間ウィンドウの対応が曖昧になる。
- 被験者差が大きく、LOSOで性能が下がる。
- SSLのaugmentation設計がタスクと合わない。

### Risk Controls

- window size / strideの感度分析を最小限入れる。
- supervised baselineを必ず置く。
- augmentationごとの効果を、全部ではなく代表条件で確認する。

## Track 2: Vision

### Position in Thesis

修論内に含める。ただし、IMUと同じ完成度の大規模分類実験を無理に狙うのではなく、低アノテーション作業認識のための現場映像活用として位置づける。

### Candidate Directions

- video action recognition
- pose estimation + temporal classification
- RGB-D based spatial understanding
- Open3D reconstruction for environment and motion context

### Thesis-feasible Outputs

修論に入れるなら、以下のいずれかを明確な成果物にする。

1. 映像データのアノテーションコストを下げるためのデータ設計。
2. 姿勢推定や人物軌跡を中間表現とした作業認識の小規模baseline。
3. RGB-DまたはOpen3Dを用いた、作業領域・動線・人の動きの構造化。
4. IMUで得た作業認識ラベルや時間構造を、映像側の弱教師として利用する設計。

### Recommended Minimum Vision Study

最小構成としては、「映像から人の軌跡または姿勢系列を抽出し、少数区間ラベルでInspect / Sort / Transportを分類する」方向が修論と接続しやすい。

この場合の主張は、映像そのものを直接分類することではなく、実環境映像から得られる中間表現を使うことで、アノテーション対象を短いフレーム単位から作業区間単位へ粗くできる点に置く。

## Recommended Thesis Structure

1. Introduction
2. Related Work
3. Problem Setting and Dataset
4. IMU-based Method
5. Experiments
6. Vision-based Extension for Low-annotation Activity Recognition
7. Discussion
8. Conclusion
