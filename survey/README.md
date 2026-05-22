# Survey

このフォルダは、修論・論文執筆・査読対応のための文献調査を管理する場所。

まず現在地を知りたいときは、このREADMEだけを見る。
詳細が必要になったら下のリンク先を見る。

## Current Question

TRUSCOのように、倉庫天井の多数カメラをキャリブレーション・スティッチングして作ったwarehouse-wide top-view tracking基盤から、作業者IDごとの長時間trajectoryを取得し、Inspection / Sorting / Transportationの作業ラベルへ少ないアノテーションで接続できるか。

## Current Answer

現時点の調査では、以下の見立て。

> warehouse multi-camera top-view trackingに近い研究は存在する。  
> logistics / factoryの作業認識研究も存在する。  
> constructionでは俯瞰・監視カメラを用いたworker activity recognitionがかなり進んでいる。  
> ただし、TRUSCOのようなwarehouse-wide top-view tracking基盤から、per-workerの長時間task segmentを少量ラベルで推定する研究はまだ限定的に見える。

つまり、研究の空白は「trackingそのもの」ではなく、**tracking済みworker trajectoryをtask recognition / task modelingへ接続する部分**にありそう。

## Today’s Structured Findings

### 1. TRUSCO設定の独自性

今回の前提は、単なる1台の俯瞰カメラではない。

- 20台以上の天井カメラ。
- 歪み補正、キャリブレーション、スティッチング。
- 倉庫全体をtop-view / floor-map的に統合。
- multi-camera trackingにより、1時間単位の作業者trajectoryや動線を取得可能。
- 最終目的は、人の行動モデル化、digital twin、simulation、layout / staffing optimization。

この設定自体が特殊なので、直接一致する関連研究が出にくい。

### 2. Warehouse / Logisticsで見つかったこと

近い研究はあるが、役割が分かれている。

- warehouse multi-camera tracking: かなり近いがtask labelなし。
- warehouse digital twin / monitoring: 近いがscene analysisやasset tracking中心。
- OpenPack / LARa / MoIL: logistics task recognitionとして重要だが、wearable、IoT、RGB-D、workstation寄り。
- warehouse-specific vision worker activity recognition: 直接刺さる例は少ない。

### 3. Constructionがかなり参考になる

建設分野では、以下が比較的多い。

- surveillance videoによるworker activity recognition。
- automated work sampling。
- productivity analysis。
- pose-based worker activity analysis。
- object / orientation / ReIDを使ったactivity recognition。

ただし、constructionは高所監視・粗い生産性分類と相性が良く、倉庫の検品・仕分けのような細かい作業とは違う。

### 4. 一般CVのSOTA寄り領域

押さえるべき周辺領域:

- spatio-temporal action detection。
- tracklet / tubelet-based action recognition。
- trajectory-centric action recognition。
- VideoMAEなどのself-supervised video representation。
- group activity recognition。

ただし、これらはスポーツ・映画・一般動画が多く、warehouse top-viewや少量ラベル、object / zone contextとはズレる。

### 5. 今日の重要な設計仮説

予備実験では、CNN / CLIP embeddingが作業ではなく人IDや背景を拾っている可能性がある。

そのため、単純な

> person appearance -> task

では弱そう。

より有望なのは、

> worker trajectory + zone + nearby objects + orientation + temporal context -> task

というinteraction-awareな設計。

特に、

- Transport: trajectory / zoneで比較的取りやすい可能性。
- Inspect vs Sort: trajectoryだけでは難しく、object / zone / orientation / temporal contextが必要そう。

### 6. Poseの位置づけ

LARTなどを見ると、poseはtracklet-centric action recognitionに効く可能性がある。

ただし、top-view倉庫映像では、

- pose推定が重い。
- 手元や関節が見えにくい。
- 実装コストが高い。

したがって、修論ではposeを主軸にしすぎず、まずは画像特徴・trajectory・zone/object contextを中心に考える。
一方で、将来的に骨格まで取れれば、人の姿勢・負荷・作業動作を含む高解像度なdigital twinにつながる。

## What To Read First

今パッと見るなら、この順番。

1. [trusco_research_update.md](trusco_research_update.md)  
   現在の調査結論。まずこれ。

2. [reading_priority.md](reading_priority.md)  
   次に精読すべき論文リスト。

3. [findings.md](findings.md)  
   NotebookLM等で読んだ個別論文カード。報告で具体例を出すときに見る。

4. [deep-research-report_truso_v1.md](deep-research-report_truso_v1.md)  
   TRUSCO設定を入れたDeep Research原文。根拠を掘るときに見る。

5. [notes.md](notes.md)  
   研究ギャップやRQ候補の作業メモ。少し雑多。

## File Roles

### Current Core

- [trusco_research_update.md](trusco_research_update.md): 最新の統合結論。
- [reading_priority.md](reading_priority.md): 次に読むべき論文。
- [findings.md](findings.md): 個別論文の調査カード。

### Raw / Background

- [deep-research-report_truso_v1.md](deep-research-report_truso_v1.md): 最新Deep Research原文。
- [2026-05-vision-multiperson-action-survey.md](2026-05-vision-multiperson-action-survey.md): 初回Deep Research原文。
- [warehouse_specific_search.md](warehouse_specific_search.md): warehouse/logisticsに絞って探した候補。

### Working Notes

- [notes.md](notes.md): 研究ギャップ、RQ、観察の雑多メモ。
- [references.md](references.md): 論文・データセット候補の一覧。
- [factcheck_plan.md](factcheck_plan.md): 実装前の調査品質確認。
- [notebooklm_prompts.md](notebooklm_prompts.md): NotebookLM用プロンプト。

## Current Research Direction

現時点で一番筋が良さそうなのは、

> Interaction-aware vision-based warehouse task recognition from multi-camera top-view worker trajectories

具体的には、

1. 既存tracking基盤からworker trajectory / trackletを得る。
2. trajectory + zoneでTransportを含むcoarse taskを分類する。
3. Inspect / Sortの区別にobject proximity、worker orientation、zone contextを追加する。
4. RGB / VideoMAE / LART風tracklet featureをbaselineとして比較する。
5. IMU task estimationをweak labelまたは補助情報として接続する可能性を検討する。

## Rule

Deep ResearchやNotebookLMの出力は入口として使う。
最終的な主張に使う文献は、必ず論文本文・公式ページ・ベンチマーク結果を確認する。
