# Research Dashboard

Last updated: 2026-05-22

## Current Thesis Direction

実環境の物流倉庫において、少ないアノテーションコストで作業認識を実現する。

Vision側では、TRUSCOの多数天井カメラ統合top-view tracking基盤から得られるworker trajectoryを、Inspection / Sorting / Transportationの作業ラベルへ接続する。

実装フェーズでは、認識モデルだけでなく、TRUSCO映像処理基盤を再利用可能なSkill / moduleとして整理し、clip抽出・annotation・特徴量抽出・モデル学習までを継続的に使える研究基盤として育てる。

## Current Working Hypothesis

単純なperson crop / RGB / CLIP特徴だけでは、人IDや背景を拾いやすく、作業そのものを捉えにくい可能性がある。

そのため、以下を明示的に使う方向が有望。

- worker trajectory
- zone / area transition
- nearby objects
- worker-object-zone relation
- orientation if available
- temporal context
- IMU-derived weak labels if available
- object / scene state transition

報告会フィードバックを踏まえると、「人がどう動いたか」だけでなく、「人の周辺環境がどう変化したか」も作業認識に使える可能性がある。

例:

> ある時刻で閉じていた目の前の物体が、その後開いた。

このような時空間的な環境状態変化をCLIPやvision-language model等で抽出できれば、作業内容推定の補助特徴になる可能性がある。

また、TRUSCOの映像処理基盤技術をSkill / moduleとして整理し、YOLO、SAM、calibration、stitching、multi-camera trackingなどを組み合わせ可能な部品として扱う方向も重要になりそう。

さらに、少量ラベル問題に対しては、いきなり高性能モデルを作るだけでなく、tracking結果から作業者clipを抽出し、人間が効率よくラベル付けできる半自動annotation workflowを作ることも重要。

## Current Survey Conclusion

warehouse multi-camera top-view trackingに近い研究は存在する。
logistics / factoryの作業認識研究も存在する。
constructionでは俯瞰・監視カメラを用いたworker activity recognitionがかなり進んでいる。

ただし、TRUSCOのようなwarehouse-wide top-view tracking基盤から、per-workerの長時間task segmentを少量ラベルで推定する研究はまだ限定的に見える。

## Active Questions

- Transportはtrajectory + zoneだけで認識できるか。
- InspectとSortはtrajectoryだけで区別できるか。
- object / zone / orientation contextはどれだけ効くか。
- object / scene state transitionは作業ラベル推定に効くか。
- RGB / VideoMAE / LART風tracklet featureは、背景・IDバイアスにどれだけ弱いか。
- IMU task estimationをVision側のweak labelとして使えるか。
- Pose推定を入れる価値はあるか、それとも修論では重すぎるか。
- TRUSCO映像処理基盤をSkill / moduleとして整理すると、どの範囲まで再利用可能になるか。
- 半自動annotation workflowを作ると、どれだけ効率的に作業ラベル付きデータを増やせるか。
- 特徴量抽出やクラスタリングを使って、annotation候補提示を効率化できるか。

## Work Menu

作業開始時は、このdashboardを見て、その日の気分と残り時間に合わせて1つ選ぶ。

| Mode | When | Candidate Task |
|---|---|---|
| Survey | 論文を読みたい日 | STAD / VideoMAE / construction系の重要論文を1本読み、`survey/findings.md`に短く足す |
| Design | 頭を整理したい日 | 半自動annotation workflowやSkill / module構成を図・箇条書きで整理する |
| Implementation | 手を動かしたい日 | worker clip extractionの最小実装を進める |
| Experiment | データを見たい日 | 既存tracking outputを確認し、trajectory + zoneで何が取れそうか見る |
| Writing | 文章化したい日 | `docs/project/research_plan.md`や`docs/project/vision_context.md`を後輩が読める形に整える |
| Maintenance | 軽く進めたい日 | logs整理、docs index更新、古いworking notesの避難 |

## Next Decisions

1. 精読する論文を絞る。
2. 実装前に使うbaseline候補を決める。
3. データアクセス・サンプル映像・既存tracking出力の所在を確認する。
4. 最初の実験単位を決める。
5. TRUSCO映像処理基盤のSkill / module化で、まず何を部品として定義するか決める。
6. 半自動annotation toolの最小構成を決める。

Implementation candidates are tracked in [Implementation Backlog](docs/dev/implementation_backlog.md).
Development process is tracked in [Development Guide](docs/dev/DEVELOPMENT_GUIDE.md).

## Current Reading Priority

See [survey/reading_priority.md](survey/reading_priority.md).

Top items:

1. Multi-Camera Worker Tracking in Logistics Warehouse Considering Wide-Angle Distortion
2. OpenPack
3. MoIL for complex work activity recognition
4. Top-View Surveillance for Pedestrian Analysis and Public Safety Management
5. Vision-Based Construction Activity Recognition via Attention and Re-Identification
6. Automated Work Sampling via Two-Stream CNNs for Site Surveillance
7. LART
8. VideoMAE

## This Week

### Done

- TRUSCO設定を明示したDeep Researchを実施。
- construction / top-view / STAD / group activity / logistics関連の調査カードを整理。
- surveyの入口READMEを整理。
- 5月進捗報告を実施。

### In Progress

- SOTA寄りのbaseline候補整理。
- LART / VideoMAE / STAD系の位置づけ確認。
- TRUSCO映像処理基盤のSkill / module化構想。
- object / scene state transitionを使った作業認識の構想。
- 半自動annotation workflowの構想とprototype v0。

### Next

- 報告会フィードバックを整理する。
- 重要論文の精読とbaseline候補絞り込みへ進む。
- TRUSCO映像処理基盤のSkill / module棚卸しを行う。
- 環境状態変化を使う特徴設計を具体化する。
- 半自動annotation toolの最小実装案を作る。

## Important Links

- [Survey README](survey/README.md)
- [TRUSCO Survey Update](survey/trusco_research_update.md)
- [Survey Findings](survey/findings.md)
- [Reading Priority](survey/reading_priority.md)
- [Vision Context](docs/project/vision_context.md)
- [Hands-on Investigation Plan](docs/dev/hands_on_investigation_plan.md)
- [Implementation Backlog](docs/dev/implementation_backlog.md)
- [Development Guide](docs/dev/DEVELOPMENT_GUIDE.md)
- [Semi-auto Annotation Spec](docs/dev/specs/semi_auto_annotation/SPEC.md)
- [Semi-auto Annotation Mini Specs](docs/dev/specs/semi_auto_annotation/MINI_SPECS.md)
