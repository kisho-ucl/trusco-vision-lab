# Vision Thesis Options

## Position

Vision Trackは修論に含める。
ただし、目的は「IMUと同等の完成度で大規模映像認識モデルを作ること」ではなく、実環境で低アノテーションコストな作業認識を行うための映像データ活用を示すことに置く。

中心Research Question:

> 実環境の物流倉庫において、IMU時系列および映像データを用いて、少ないアノテーションコストで作業認識を実現するにはどうすればよいか。

## Why Vision Belongs in the Thesis

- 共同研究先では映像データが日常的に蓄積されている。
- IMUは実証実験時のみ取得されるため、継続的な現場応用には映像データの活用が重要。
- 作業ラベルをフレーム単位で密に付与するのは高コストであり、低アノテーション化という研究課題はIMU Trackと一貫する。
- 先行研究で人の軌跡推定が進んでいるため、映像から直接作業を分類するだけでなく、軌跡・姿勢・滞在領域などの中間表現を使える。

## Option A: Pose or Trajectory Baseline

### Question

映像から抽出した姿勢系列または人物軌跡を用いて、少数の作業区間ラベルからInspect / Sort / Transportを分類できるか。

### Method

- person detection / tracking
- pose estimation or trajectory extraction
- temporal feature aggregation
- lightweight classifier

### Pros

- アノテーションコスト削減という主題と相性が良い。
- IMUの時系列分類と構造が近く、修論内で比較・接続しやすい。
- 先輩研究の軌跡推定成果とも接続しやすい。

### Risks

- カメラ位置や遮蔽の影響を受ける。
- 作業者が複数いる場合、個人ID追跡が必要になる。
- 姿勢だけではInspectとSortの区別が弱い可能性がある。

### Thesis Fit

High.

## Option B: RGB Video Action Recognition

### Question

短い映像クリップからInspect / Sort / Transportを直接分類できるか。

### Method

- frame sampling
- pretrained video model
- clip-level fine-tuning or feature extraction
- weak clip labels

### Pros

- 行動認識として分かりやすい。
- pretrained modelを使えば短期間でもbaselineを作れる可能性がある。

### Risks

- ラベル数が少ないとfine-tuningが不安定。
- 背景や作業場所に過適合しやすい。
- 低アノテーション性を主張するには設計を工夫する必要がある。

### Thesis Fit

Medium.

## Option C: RGB-D / Open3D Structuring

### Question

RGB-Dデータから作業空間・人物位置・物体配置を構造化し、作業認識やシミュレータ連携に使える表現を作れるか。

### Method

- RealSense data collection
- depth preprocessing
- point cloud generation
- human / workspace localization
- simple rule or classifier

### Pros

- 将来のシミュレータ連携との相性が良い。
- レイアウト最適化のビジョンにつながる。

### Risks

- 修論の分類評価から離れやすい。
- センサ設置・キャリブレーション・欠損処理が重い。
- 10月までの成果としては広がりすぎる可能性がある。

### Thesis Fit

Medium to Low unless the data is already clean.

## Recommended Direction

第一候補はOption A。

理由:

- IMU Trackと同じく時系列認識として扱える。
- 「低アノテーションコスト」という中心軸に自然に入る。
- Visionを修論に含めつつ、過大な映像モデル開発に巻き込まれにくい。
- 先輩研究の軌跡推定と接続し、将来のシミュレータ連携にも伸ばしやすい。

## Minimum Viable Vision Study

最低限の成果物:

1. 実映像から人物軌跡または姿勢系列を抽出する。
2. 作業区間単位の粗いラベルを付与する。
3. Inspect / Sort / Transportの3分類baselineを作る。
4. フレーム単位アノテーションを必要としない点を整理する。
5. IMU Trackと同じResearch Questionのもとで、低アノテーション作業認識の別モダリティとして議論する。

## Boundary

やらないこと:

- 映像モデルの大規模fine-tuningを主成果にしない。
- 物体認識・3D再構成・姿勢推定・軌跡推定を全部同時に主張しない。
- Visionだけで完璧な作業認識を実現する論調にしない。

やること:

- Visionを現場実装に近いデータ活用軸として入れる。
- アノテーションコスト削減の設計を明示する。
- IMUで作った問題設定・評価軸と揃える。

