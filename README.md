# HAR Warehouse Research

物流倉庫における作業認識を、スマートフォンIMUおよび画像データを用いて実現する研究プロジェクト。

## Research Goal

実環境の物流倉庫において、少ないアノテーションコストで人手作業を認識する方法を検討する。
特に、IMU時系列と映像データを対象に、自己教師あり学習・弱いラベル・長時間文脈モデリングを活用する。

対象作業:

- Inspect: 商品と注文書を照合する検品作業
- Sort: 商品を適切な場所に振り分ける仕分け作業
- Transport: 荷物を載せた台車を運搬する搬送作業

これらの作業には一定の役割分担があるが、現場状況に応じて柔軟に交替される。
作業は数分で切り替わる場合もあれば、数十分継続する場合もある。

## Tracks

### Track 1: IMU-based HAR

既存論文・既存実験を土台に、少量ラベル下の作業認識を定量評価する主な実証軸。

- Input: 加速度 + 角速度の6軸時系列
- Method: CNN with SimCLR pretraining + Transformer
- Concept: IMU -> CNN SSL -> Transformer -> activity classification
- Evaluation: Macro-F1, Weighted-F1, LOSO, reduced-label experiments

### Track 2: Vision-based HAR

共同研究先の今後のニーズに合わせた拡張軸。
毎日蓄積される映像データを活用し、アノテーションコストを抑えた作業認識へ接続する。

- Input: RGB / RGB-D
- Candidate methods:
  - 2D/video action recognition
  - pose-based recognition
  - 3D reconstruction with Open3D
- Longer-term vision:
  - real data-driven human behavior modeling
  - simulator integration
  - warehouse layout optimization

## Current Thesis Strategy

修論全体の中心問いを「実環境で、少ないアノテーションコストにより作業認識をどう実現するか」に置く。
IMUは既存成果を活かして定量的に深掘りし、Visionは現場データ活用に向けた実践的な拡張として組み込む。

推奨する修論ストーリー:

1. 倉庫作業認識では、作業が長時間・複合的で、切り替わりも柔軟であるため、密なアノテーションが高コストになる。
2. IMUでは、短期動作表現をCNN SSLで学習し、長期文脈をTransformerで扱うことで、少量ラベルでも作業分類性能を改善できる。
3. Visionでは、現場で継続的に蓄積される映像を用い、姿勢・軌跡・時間文脈などの中間表現を通じて、低アノテーションな作業認識へ拡張する。

## Project Docs

- [Research Dashboard](DASHBOARD.md)
- [Docs Index](docs/README.md)
- [Roadmap](docs/project/roadmap.md)
- [Vision Context](docs/project/vision_context.md)
- [Survey](survey/README.md)
- [Logs](logs/README.md)

For new readers, start from `DASHBOARD.md`, then read `docs/project/roadmap.md` and `docs/project/vision_context.md`.
Progress reports and exploratory notes are kept as working notes, not as the main entry point.
