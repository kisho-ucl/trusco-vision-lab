# Experiment Log

このファイルは、実験の再現性と修論執筆時の記憶補助のために使う。

## Template

```md
## YYYY-MM-DD: short experiment name

### Purpose


### Dataset

- subjects:
- classes:
- window size:
- stride:
- split:

### Method

- encoder:
- pretraining:
- temporal model:
- classifier:

### Config

- seed:
- batch size:
- learning rate:
- epochs:
- augmentations:

### Results

- Macro-F1:
- Weighted-F1:
- Notes:

### Interpretation


### Next Action


```

## Running Questions

- IMUのwindow size / strideは、作業単位のラベルとどの程度整合しているか。
- SSL augmentationは倉庫作業の意味を壊していないか。
- LOSOで落ちる被験者に共通する特徴はあるか。
- Visionでは、作業認識を直接狙うべきか、まず姿勢・軌跡・滞在領域を中間表現にするべきか。
- Visionにおけるアノテーション単位は、フレーム単位・秒単位・作業区間単位のどれが妥当か。
- IMUで得た時間構造や作業ラベルを、Vision側の弱教師として利用できるか。
