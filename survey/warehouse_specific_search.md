# Warehouse-specific Search Notes

Codex側で、warehouse / logistics に絞ってvision-based activity recognitionを検索したメモ。

## Search Summary

現時点では、以下を同時に満たす学会論文・arXiv論文はあまり見つかっていない。

- warehouse / logistics domain
- fixed or overhead camera
- multiple workers
- ID tracking
- worker-level activity / task recognition
- low annotation / weak supervision

見つかる研究は、以下に分散する傾向がある。

1. warehouse / logisticsだが、wearable sensorやmotion capture中心。
2. warehouse pickingだが、egocentric video + smartwatchなど作業者装着型。
3. forkliftなど機械活動認識だが、CAN信号や車載センサ中心。
4. smart warehouse surveyでvision-based HARの可能性は述べられるが、具体的な映像SOTAではない。
5. industrial / constructionではvision-based worker activity recognitionが比較的多い。

## Found Candidates

### Recognizing Grabbing Actions from Inertial and Video Sensor Data in a Warehouse Scenario

Type: Conference / Procedia Computer Science, 2017

Relevance:

- warehouse order picking scenario。
- egocentric video + smartwatch inertial data。
- grabbing action recognition。
- videoとIMUのsensor fusion。

Limitations:

- fixed / overhead cameraではない。
- participantsは少数。
- picking中のgrabbing action中心。
- 複数人物ID追跡ではない。

Use:

- warehouseにおけるvideo + inertial activity recognitionの初期例。
- IMUとVisionの接続文献として参考。

### LARa: Creating a Dataset for Human Activity Recognition in Logistics Using Semantic Attributes

Type: Sensors, 2020

Relevance:

- logistics / order picking / packingを対象にしたHAR dataset。
- logistics activity recognition datasetとして重要。
- semantic attributesを用いて作業を構造化する方向が近い。

Limitations:

- motion capture / wearable sensor寄り。
- fixed overhead video-based recognitionではない。
- 複数人物ID trackingではない。

Use:

- logistics domainの公開HAR datasetとして重要。
- 作業ラベル・semantic attribute設計の参考。

### Context-Aware Human Activity Recognition in Industrial Processes

Type: Sensors, 2022

Relevance:

- production and logisticsにおけるHAR。
- order picking and packaging activities。
- context informationを使うことでactivity recognition performanceが上がる。
- object / location / process contextの重要性を示す。

Limitations:

- sensor / motion capture中心。
- vision-based worker trackingではない。
- fixed camera / overhead cameraではない。

Use:

- 倉庫作業はcontext-dependentであり、動きだけでなく対象物・場所・工程文脈が重要という根拠。

### Exploring Semi-Supervised Methods for Labeling Support in Multimodal Datasets

Type: Sensors, 2018

Relevance:

- warehouse picking activitiesを含む。
- smartwatch acceleration and egocentric video。
- small labeled setからannotation supportを行う。
- labeling cost reductionに近い。

Limitations:

- fixed overhead cameraではない。
- action recognition model本体というよりannotation support。
- 複数人物ID trackingではない。

Use:

- 少量ラベル・annotation supportの先行例。
- IMUとvideoを使ってラベル付けを支援する方向として参考。

### CPS-Based Smart Warehouse for Industry 4.0: A Survey of the Underlying Technologies

Type: Computers, 2018

Relevance:

- smart warehouseにおけるHARの必要性をsurvey内で扱う。
- vision-based HAR, sensor-based HAR, RF-based HARを分類。
- sorting and delivering goodsのactivity detectionに言及。

Limitations:

- smart warehouse全体の技術survey。
- specific vision-based worker activity recognition手法ではない。
- SOTA比較や実験はない。

Use:

- warehouseでHARが必要になる背景文献。
- ただし主要技術根拠にはしにくい。

### Semi-Supervised Learning for Forklift Activity Recognition from Controller Area Network Signals

Type: Sensors, 2022

Relevance:

- warehouse / logistics centerで重要なforklift activity recognition。
- unlabeled field operation dataを使うsemi-supervised learning。
- 実倉庫サイトのデータ。
- load-handling activityを高精度に認識。

Limitations:

- computer visionではなくCAN signals。
- human worker activityではなくmachine activity。
- camera-based per-person recognitionではない。

Use:

- warehouse domainではactivity recognitionがあるが、視覚ではなく機械センサに寄っている例。
- low-label / semi-supervisedの参考。

### Semi-automated computer vision-based tracking of multiple industrial entities

Type: EURASIP Journal on Image and Video Processing, 2024

Relevance:

- industrial environment such as warehouseで、entitiesをcontinuous tracking / classification / identificationする必要性を述べる。
- multiple industrial entities tracking。
- dataset creation approach。

Limitations:

- activity recognitionというよりtracking / dataset creation。
- worker task label recognitionではない。

Use:

- 倉庫などの産業環境ではtracking対象が複数であり、ID維持が課題という根拠。

## Current Interpretation

Warehouse / logisticsに限定すると、vision-based worker activity recognitionはconstructionほど豊富には見つからない。

特に、固定/俯瞰カメラから複数作業者をID追跡し、検品・仕分け・搬送のような作業ラベルを低アノテーションで推定する研究は、少なくとも初期検索では見つかりにくい。

一方で、周辺には以下の関連研究がある。

- logistics HAR dataset and semantic attributes
- warehouse picking with egocentric video + IMU
- annotation support using multimodal data
- forklift activity recognition with semi-supervised learning
- smart warehouse survey
- industrial entity tracking

このため、研究ギャップは以下のように置ける可能性がある。

> Constructionではvision-based worker activity recognitionが進んでいるが、warehouse / logisticsではsensor-based HARやegocentric picking支援、machine activity recognitionに分散しており、固定/俯瞰カメラからworker IDごとの作業認識を行う研究はまだ限定的である。

