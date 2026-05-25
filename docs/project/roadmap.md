# Roadmap

対象期間: M2春から10月頃までの研究フェーズ。

## Principle

修論の中心問いは「実環境で、少ないアノテーションコストにより作業認識をどう実現するか」とする。
IMUは定量評価の主軸、Visionは現場映像データ活用に向けた実証または設計軸として含める。

Vision側では、単一の認識モデルだけでなく、TRUSCO映像処理基盤を再利用可能なSkill / moduleとして整理する。
特に、clip抽出、半自動annotation、特徴量抽出、dataset exportを研究資産として育てる。

## May 2026

- [ ] 既存IMU論文・実験結果・コード・データの棚卸し
- [ ] 修論の中心Research Questionを1文に固定
- [ ] 既存結果で不足している比較実験を洗い出す
- [x] Vision関連研究の初期surveyを行う
- [x] 5月進捗報告を行い、教授フィードバックをlogに残す
- [ ] 映像データの利用可能範囲を確認
- [ ] Vision Trackの修論内での最小成果物を定義
- [x] docsの入口を整理し、progress report系をworking notesとして位置付ける

Deliverable:

- 実験一覧
- 修論ストーリー案
- 画像データ棚卸しメモ
- 報告会フィードバックlog
- docs index

## June 2026

- [ ] IMUの再現実験環境を固定
- [ ] LOSO評価を整理
- [ ] Macro-F1 / Weighted-F1の表を作る
- [ ] ラベル削減実験を設計
- [ ] 映像データのサンプル確認と前処理方針を決める
- [ ] 既存tracking outputの形式を確認する
- [ ] worker IDごとのclip extractionを最小実装する
- [ ] 半自動annotation toolの最小構成を決める
- [ ] Skill / module化するTRUSCO映像処理基盤を棚卸しする
- [ ] Vision baselineを「trajectory」「RGB/video crop」「object / scene state transition」のどこから始めるか決める

Deliverable:

- IMU baseline table
- evaluation script
- vision data note
- vision baseline design
- clip extraction prototype
- annotation workflow design
- TRUSCO module inventory

## July 2026

- [ ] SimCLR + Transformerの本実験
- [ ] ablation study
- [ ] ラベル削減実験
- [ ] 失敗例・混同行列の分析
- [ ] 半自動annotationで小規模な作業ラベル付きclip datasetを作る
- [ ] trajectory + zone baselineを試す
- [ ] RGB / VideoMAE等のvideo-level baselineを試す
- [ ] object / scene state transition featureの小実験を行う

Deliverable:

- main result table
- ablation table
- confusion matrix
- first vision baseline
- labeled clip dataset report
- annotation tool note

## August 2026

- [ ] 追加実験を最小限に絞る
- [ ] Related Workを修論向けに再構成
- [ ] IMU章のドラフト
- [ ] Vision章のドラフト
- [ ] Skill / module docsを後輩が読める形に整える

Deliverable:

- thesis chapter drafts
- result figures
- supervisor discussion memo
- reusable module docs

## September 2026

- [ ] 修論本文の主要章を完成
- [ ] 図表を整える
- [ ] 研究の限界と今後の展望を明確化
- [ ] 発表資料の骨子を作る

Deliverable:

- near-complete thesis draft
- presentation outline

## October 2026

- [ ] 最終実験の凍結
- [ ] 修論の整合性確認
- [ ] 発表練習用スライド
- [ ] 共同研究先向けの今後の提案整理

Deliverable:

- frozen results
- thesis final draft
- next-step proposal for vision-based research

## Weekly Review Template

### This Week

- Done:
- Blocked:
- Next:

### Research Risk

- Biggest risk:
- Mitigation:

### Thesis Asset

- New figure/table/text created:

### Project Asset

- New reusable doc/tool/module created:
