# Survey Findings

NotebookLMなどでざっと確認した論文・データセットの調査カード。

目的:

- 後で進捗報告や関連研究整理に使えるようにする。
- 「こういう既存研究ではここまでできている」「ただし自分の研究設定とはここが違う」を短く残す。
- 精読候補と参考程度のものを分ける。

## Finding Cards

### STEP: Spatio-Temporal Progressive Learning for Video Action Detection

Status: 参考程度。Spatio-temporal action detectionの基礎把握用。

#### 何の論文か

少数の粗い初期proposalから出発し、空間的な位置補正と時間的な範囲拡張を段階的に行うことで、action tubeletの分類と位置特定を行うspatio-temporal action detection手法。

#### タスク

- Spatio-temporal action detection。
- 映像中のどこで、いつ、何が行われているかを推定する。

#### 入力・出力

- Input: video clip、RGB、optical flow、少数の初期proposal。
- Output: action class label、spatio-temporal bounding boxes / action tubelets。

#### 主な特徴表現

- RGB特徴。
- Optical flow特徴。
- Two-stream fusion。
- Tubelet / short tracklet。

#### 私の研究に近い点

- 複数人物がいる場合に、人物領域ごとのaction tubeletを扱える。
- フレーム単位ではなく、時空間的な塊として行動を扱う点が近い。
- bbox系列やtubeletを時間方向にリンクしてaction tubeを構成する発想は、worker trajectoryからtask segmentを作る際の参考になる。

#### 私の研究とズレる点

- 俯瞰固定カメラや倉庫環境は扱わない。
- UCF101やAVAなど、一般動画・映画・スポーツ系が中心。
- 長時間worker ID trackingではなく、短〜中時間のaction tubelet検出が中心。
- 少量ラベルではなく、通常の教師あり学習。
- initial proposalが少数という意味であり、annotationが少ないという意味ではない。

#### 既存技術でできることとして示唆される点

- 人物の動きに合わせてbboxを更新しながら、action regionを時空間的に追跡・分類できる。
- tubeletを使うことで、単一フレームよりも動作の時間的連続性を扱える。

#### まだ難しいこと・限界

- 少量アノテーションでの学習。
- 物流倉庫の長時間ID維持。
- 検品・仕分けのようなfine-grained work semantics。
- worker-object-zone contextの利用。

#### Citation Decision

参考程度。

spatio-temporal action detectionの一般的な考え方を理解するために使う。
本研究の主要比較対象としては弱い。

### ACT-Detector: Spatio-Temporal Action Localization via Anchor Cuboids

Status: 参考程度。Tubelet-based action localizationの基礎把握用。

#### 何の論文か

複数フレームにまたがるanchor cuboidを用いて、動画内のaction tubeletを検出し、時空間的に行動をlocalizeする手法。

#### タスク

- Spatio-temporal action localization。
- 動画内のどこで、誰が、何をしているかを推定する。

#### 入力・出力

- Input: 短いフレーム列、RGB、optical flow。
- Output: action tubelet、action class confidence。

#### 主な特徴表現

- RGB特徴。
- Optical flow特徴。
- Anchor cuboid。
- Tubelet。

#### 私の研究に近い点

- 複数フレームをまとめて扱うことで、単一フレームでは曖昧な行動を識別する。
- 人物の短いbbox系列をaction unitとして扱う。
- 複数人物がいる場合にも、候補領域ごとにaction localizationできる。

#### 私の研究とズレる点

- 倉庫や産業環境ではなく、一般action datasetが中心。
- 俯瞰固定カメラ特有の歪み、遮蔽、ID switchは扱わない。
- 少量ラベルではなく、密なbbox/action annotationに依存する。
- 長時間task segmentではなく、短いaction tubeletが中心。

#### 既存技術でできることとして示唆される点

- 短い動画シーケンスから人物bbox系列とaction labelを同時に推定できる。
- tubelet表現により、動きのある行動を時空間的にlocalizeできる。

#### まだ難しいこと・限界

- 少量ラベルでの学習。
- 長時間ID tracking。
- 手元の微細な作業認識。
- worker-object-zone relationの扱い。

#### Citation Decision

参考程度。

古典的・基礎的なSTAD/tubelet手法として把握する。

### Spatio-Temporal Action Detection Under Large Motion / Track Aware Action Detector

Status: 部分的な精読候補。Track-aware action modelingの参考。

#### 何の論文か

大きな動きやカメラ動きがある動画において、人物trackに沿って特徴を集約するTrack Aware Action Detectorを提案したspatio-temporal action detection論文。

#### タスク

- Spatio-temporal action detection。
- 複数人物のtrack / tubeに対してaction labelを推定する。

#### 入力・出力

- Input: video clip、RGB frame、YOLOv5 + DeepSORT等で得たperson tracks。
- Output: 各人物track / tubeとaction label。

#### 主な特徴表現

- RGB特徴。
- Tracklet / person track。
- TOI-Align。
- Temporal feature aggregation。

#### 私の研究に近い点

- 複数人物をtrackingし、そのtrackに沿って特徴を集約してactionを推定する。
- YOLOv5 + DeepSORTのようなtracking-by-detection pipelineを使う。
- track-awareに特徴を切り出す考え方は、worker trajectoryからtask recognitionへ接続する際にかなり参考になる。
- multi-person action recognitionのSOTA寄りの流れを理解する材料になる。

#### 私の研究とズレる点

- 対象は主にスポーツ映像。
- 固定俯瞰カメラや倉庫環境ではない。
- 研究主眼はlarge motionへの対応であり、少量ラベルやwarehouse task semanticsではない。
- dense bbox/action annotationを前提とする。
- object / zone / worker interaction contextは弱い。

#### 既存技術でできることとして示唆される点

- person trackを作り、そのtrackに沿ってRGB特徴を抽出・時間集約してaction classificationできる。
- tracking結果を使うことで、無効なproposalを減らし、人物ごとの行動特徴を扱える。

#### まだ難しいこと・限界

- worker-object interactionや周囲コンテキストの利用。
- 少量ラベル条件。
- top-view warehouse domainへの適用。
- 長時間task segment recognition。

#### 報告で使える一言

一般のspatio-temporal action detectionでは、人物trackやtubeletに沿ってRGB特徴を集約し、人物ごとのactionを推定する研究がある。これは本研究のtracklet-based作業認識に近いが、主にスポーツや一般動画を対象としており、倉庫top-view、少量ラベル、作業領域・物体文脈までは扱っていない。

#### Citation Decision

部分的な精読候補。

TOI-Alignやtrack-aware temporal aggregationなど、tracking結果をaction recognitionに接続する実装上の参考として重要。
ただし本研究の主要比較対象にするにはdomain gapが大きい。

### SBGAR: Semantics Based Group Activity Recognition

Status: 参考程度。Group activity recognitionの幅を知るため。

#### 何の論文か

CNNとLSTMを用いて、映像から中間表現としてtext captionを生成し、その意味情報に基づいてgroup activityを認識する手法。

#### タスク

- Group activity recognition。
- 画面全体または複数人物の集団行動ラベルを推定する。

#### 入力・出力

- Input: RGB video frames、dense optical flow。
- Output: group activity category。
- Intermediate: text caption / semantic description。

#### 主な特徴表現

- RGB特徴。
- Optical flow特徴。
- CNN特徴。
- LSTMによるcaption / semantic representation。
- Multimodal / semantic intermediate representation。

#### 私の研究に近い点

- 複数人物が存在する映像を扱う。
- 少し引いた固定カメラ視点のデータセットを扱う。
- 映像から直接低次特徴だけでなく、意味的な中間表現を使う発想は参考になる。

#### 私の研究とズレる点

- ID追跡を行わない。
- 各人物IDごとの作業ラベル推定ではなく、グループ全体のactivityを推定する。
- 少量ラベルではなく、caption annotationが必要でannotation costが高い。
- 物流倉庫のtask recognitionではなく、スポーツ・集団行動が中心。

#### 既存技術でできることとして示唆される点

- 複数人物シーンから、個別trackingなしにscene-level / group-level activityを分類できる。
- 意味表現を中間に挟むことで、画像特徴だけではない推論が可能。

#### まだ難しいこと・限界

- IDごとの長時間task recognition。
- 少量アノテーション。
- worker-level activity labeling。
- 倉庫のfine-grained task semantics。

#### Citation Decision

参考程度。

本研究の中心であるper-worker task recognitionとは方向が違う。
ただし、追跡を避けてscene-level semanticsを見る別アプローチとして把握しておく価値はある。

### Actor Relation Graphs for Group Activity Recognition

Status: 参考程度。人物間関係モデリングの参考。

#### 何の論文か

複数人物シーンにおいて、人物間の相対位置や外観特徴をActor Relation Graphとして表現し、Graph Convolutional Networkで個人行動とグループ活動を認識する手法。

#### タスク

- Group activity recognition。
- Individual action recognition。
- Multi-person relation modeling。

#### 入力・出力

- Input: sampled RGB frames、person bounding boxes、場合によりtracklet。
- Output: group activity label、individual action labels。

#### 主な特徴表現

- RGB person appearance features。
- Person bounding box coordinates。
- Relative position / relation features。
- Graph representation。
- Tracklet補間。

#### 私の研究に近い点

- 複数人物を同時に扱う。
- 個人行動ラベルも出力する。
- person box / trackletを前提にする点は、tracking済みwarehouse workerに近い。
- 人物間の関係性を明示的にモデル化する点は、共同作業や混雑、干渉の分析に参考になる。

#### 私の研究とズレる点

- 主目的はグループ全体のactivity recognition。
- 倉庫作業ではなく、スポーツやcollective activity datasetが中心。
- ID trackingを解くわけではなく、検出済みboxやtrackletを前提にする。
- 少量ラベルへの対応はない。
- worker-object-zone relationではなく、主にactor-actor relation。

#### 既存技術でできることとして示唆される点

- 人物外観と位置関係から、複数人物間のinteractionをグラフとして学習できる。
- 個人行動とグループ活動を同時に推定できる。
- 周囲人物との関係が行動認識に効く場合がある。

#### まだ難しいこと・限界

- 長時間ID維持。
- 少量ラベル。
- 倉庫のfine-grained work labels。
- 物体・zone・設備とのinteraction。

#### 報告で使える一言

Group activity recognitionでは、複数人物の位置や外観の関係をグラフで表現し、個人行動や集団活動を認識する研究がある。本研究の中心はIDごとの作業認識なので直接の比較対象ではないが、共同搬送や作業者間の干渉を扱う場合には、人物間関係モデリングの考え方が参考になる。

#### Citation Decision

参考程度。

本研究の主軸はworker-object-zone interactionだが、actor-actor interactionを扱う補助文献として有用。

### Computer Vision in Logistics - viso.ai article

Status: 参考資料。Industry / web source。

#### 何の資料か

物流分野におけるcomputer visionの応用を概説したWeb記事。
AI・deep learning・edge AIを用いて、サプライチェーン全体の自動化・可視化・最適化を行うという実務寄りの内容。

#### 主な対象

- 物流・サプライチェーン。
- 倉庫。
- 輸送。
- 検査。
- 監視。
- 自動化システム。

#### 紹介されている応用

- Object traceability and tracking。
- Barcode / OCR / container number / license plate recognition。
- Parcel / pallet volumetric measurement。
- Inspection and quality control。
- Equipment monitoring。
- Occupancy analysis。
- Security and surveillance。
- Crowd and behavior analysis。
- Anomaly detection。
- Process modeling and optimization。
- Picking and packing optimization。
- Human error detection。
- Assisted manual handling。
- Automated handling systems。
- Risk management and documentation。

#### 私の研究に近い点

- 物流分野でcomputer visionが実務的に重要になっていることを示す背景資料になる。
- 倉庫内の人、物、車両、設備を視覚的に追跡・認識する需要が整理されている。
- Crowd / behavior analysis、process modeling、picking / packing optimization、human error detectionなど、本研究のVision Trackに近い応用が含まれる。
- process metrics、throughput、flow direction、processing timeを抽出してsimulation / optimizationに使うという方向は、将来の倉庫シミュレータ連携と近い。
- tracking + behavior recognition + task modelingをつなぐ余地がある、という研究機会の説明に使える。

#### 私の研究とズレる点

- 学術論文ではなく、企業・実務向けの概説記事。
- 具体的なアルゴリズム評価、データセット、再現可能な実験はない。
- 倉庫作業者IDごとの長時間作業認識や少量ラベル学習を直接扱うわけではない。
- 研究ギャップの根拠としては、論文調査と組み合わせて使う必要がある。

#### 既存技術でできることとして示唆される点

- 物流では、物体検出、OCR、追跡、寸法測定、検査、監視、異常検知などのCV応用が実務的に広がっている。
- 安価なカメラとdeep learningにより、現場映像を使った自動分析が進んでいる。
- Edge AIにより、低遅延・プライバシー保護・オフライン処理が重視されている。

#### まだ難しいこと・限界

- 実務応用は多いが、tracking、behavior recognition、task modelingを統合して作業理解まで行う研究はまだ十分に見えていない。
- 混雑環境、遮蔽、複数人物ID維持、workflowとの統合が課題。
- 物流作業の意味理解は、単なる検出精度だけではなく、現場プロセスとの接続が必要。

#### 報告で使える一言

実務側では、物流分野でcomputer visionを用いた物体追跡、検査、監視、ピッキング支援、行動分析、プロセス最適化への期待が高い。一方で、学術的には、作業者tracking、行動認識、作業モデル化をつなぎ、少ないアノテーションで倉庫作業を理解する部分がまだ十分に整理されていない可能性がある。

#### Citation Decision

参考資料。

研究背景や実務ニーズの説明には使える。
Related Workや技術的主張の主要根拠にはせず、学術論文と組み合わせて扱う。

### Suspicious Human Activity Recognition: A Review

Status: 参考程度

#### 何の論文か

監視カメラ映像から、人間の不審行動・異常イベントを検出・分類する技術について、過去10年間程度の研究動向をまとめたレビュー論文。

対象例:

- 置き去り荷物
- 盗難
- 転倒
- 交通事故
- 暴力
- 火災
- その他の不審・異常イベント

#### タスク

- 監視カメラ映像における異常・不審イベント検出。
- 正常行動と異常行動の分類。
- 不審イベント検出に基づくアラート生成。

#### 入力・出力

- Input: 主に固定監視カメラ映像。一部動的カメラも含む。
- Output: 正常/異常カテゴリ、不審行動カテゴリ、アラーム。

#### 主な特徴表現

- RGB特徴。
- 背景差分による前景・オブジェクト抽出。
- trajectory / tracking特徴。
- silhouette / shape特徴。
- poseや姿勢情報。
- optical flowなどの動き特徴。

古典的な画像処理・機械学習手法が中心。

#### 私の研究に近い点

- 監視カメラ映像を用いる。
- 空港、駅、ショッピングモールなど、見下ろし型・固定カメラに近い映像が多い。
- 複数人物や群衆環境での人物・物体検出を扱う。
- カルマンフィルタやパーティクルフィルタなどを用いたtracking-based approachが紹介されている。
- 軌跡、形状、動き特徴を用いた行動分類という流れは、倉庫映像での作業認識にも部分的に関係する。
- オクルージョン、照明変化、影、ノイズなど、実環境映像の課題を整理する材料になる。

#### 私の研究とズレる点

- 対象は盗難、転倒、暴力、放置物などの異常検知であり、検品・仕分け・搬送のような日常的作業ラベルではない。
- 2017年頃のレビューで、背景差分、optical flow、SVM、HMM、KNNなど古典的手法が中心。
- 近年のdeep learning-based action recognition、pose estimation、self-supervised learning、weak supervisionは十分に扱っていない。
- 少量アノテーションで詳細な作業区間を認識する問題とは直接つながらない。

#### 既存技術でできることとして示唆される点

- 背景差分を用いた動的オブジェクトや放置物の抽出。
- カルマンフィルタやパーティクルフィルタによる複数人物・物体のtracking。
- 軌跡、形状、色ヒストグラム、動き特徴を使ったSVM / KNN / HMMによる行動分類。
- 監視映像における検出・追跡・特徴抽出・分類の古典的pipeline。

#### まだ難しいこと・限界

- 混雑環境における人物同士のオクルージョン。
- 背景による部分的・完全な隠れ。
- 急激な照明変化、影、画像ノイズによる誤検出。
- 複雑な背景での高精度検出とリアルタイム処理の両立。
- 長時間IDを維持した作業区間認識。
- 少量ラベル・弱教師あり・自己教師あり条件での作業認識。

#### 報告で使える一言

監視カメラ映像から異常行動を検出する研究では、背景差分、追跡、軌跡や形状特徴を使った行動分類のpipelineが古くから整理されている。一方で、対象は異常検知が中心であり、物流倉庫の日常的な作業ラベルを、長時間IDと少量ラベル条件で推定する問題とは異なる。

#### Citation Decision

参考程度。

実環境映像におけるオクルージョン、照明変化、影、ノイズなどの課題を説明するためには使える。
ただし、最新SOTAや本研究の主要比較対象としては弱い。

### Vision-Based Construction Worker Activity Analysis via Body Posture

Status: 参考程度。パイプライン構築としては精読候補。

#### 何の論文か

建設現場のRGBビデオ映像から、作業員の2D姿勢推定とtrackingを行い、フレーム単位で作業内容を自動分類する深層学習ベースの行動分析に関する論文。

#### タスク

- RGB映像からの2D作業員姿勢推定。
- 作業員のpose tracking。
- フレーム単位の作業行動認識・作業セグメンテーション。
- 作業時間や生産性の分析。

#### 入力・出力

- Input: 建設現場のRGBビデオ映像。
- Examples: レンガ積み、左官工事など。
- Output: 2D姿勢情報、tracking ID、フレームごとの作業ラベル、作業時間分析。

#### 主な特徴表現

- RGB特徴。
- Pose特徴。
- Object特徴。
- YOLOv3による物体検出。
- AlphaPoseによる2D姿勢推定。
- i3DによるRGB / optical flow特徴。
- 姿勢特徴と時系列モデルの統合。

#### 私の研究に近い点

- 実作業現場の映像を用いた作業認識である。
- 人物検出、pose推定、ID tracking、時系列行動認識を組み合わせたpipelineになっている。
- AlphaPoseは複数人物対応であり、手法としては複数人映像へ拡張可能とされている。
- i3DとMS-TCNにより、映像・pose特徴からフレーム単位の作業カテゴリを予測する。
- 産業現場での作業時間・生産性分析という応用目的が近い。

#### 私の研究とズレる点

- 対象は物流倉庫ではなく建設作業。
- 検品・仕分け・搬送ではなく、レンガ積みや左官などの建設作業ラベル。
- 少量アノテーションには対応しておらず、詳細な教師ラベルを前提とする。
- 評価データは主に単一作業者であり、複数人が入り乱れる倉庫環境でのtracking評価は弱い。
- 完全な真上俯瞰ではなく、横・斜めなど関節の動きを捉えやすい視点を利用している。

#### 既存技術でできることとして示唆される点

- YOLOv3 + AlphaPoseで作業者の人物領域と2D poseを取得できる。
- Pose bounding boxのIoUやORB特徴を用いて、フレーム間のpose trackingができる。
- RGB / optical flow特徴とpose特徴を組み合わせ、MS-TCNで細かい作業セグメンテーションを行える。
- 作業映像からフレーム単位の作業時間分析が可能。

#### まだ難しいこと・限界

- アノテーションコストが高い。
- 長時間のオフライン学習を要する。
- 俯瞰カメラでは手足や関節のオクルージョンによりpose推定精度が低下する可能性がある。
- 複数人物が密集・交差する状況でのID維持は十分に評価されていない。
- 物流倉庫の完全俯瞰映像や少量ラベル条件には直接対応していない。

#### 報告で使える一言

建設現場では、YOLO、AlphaPose、i3D、MS-TCNを組み合わせて、人物検出・姿勢推定・tracking・作業セグメンテーションを行う研究がある。これは作業認識pipelineとして参考になるが、詳細な教師ラベルを前提としており、複数人が入り乱れる俯瞰倉庫映像や少量ラベル条件はまだ扱っていない。

#### Citation Decision

参考程度。ただしpipeline設計としては精読候補。

本研究でRGB + pose + tracking + temporal segmentationのbaselineを考える場合、構成の参考になる。

### Social Scene Understanding and Collective Activity Recognition

Status: 参考程度。ネットワーク設計の参考。

#### 何の論文か

外部の検出・追跡アルゴリズムに依存せず、1つのニューラルネットワークで複数人物の検出、個人行動認識、シーン全体の集団活動認識を同時に行うend-to-end手法に関する論文。

#### タスク

- 複数人物検出。
- 個人行動認識。
- 集団活動認識。
- フレーム間の人物対応づけ。

#### 入力・出力

- Input: RGB画像シーケンス。
- Output: 複数人物のbounding box、各人物の行動ラベル、集団活動ラベル。

#### 主な特徴表現

- RGB特徴。
- Fully Convolutional Networkによる画像特徴。
- RNNによる時間方向の情報伝播と人物マッチング。

#### 私の研究に近い点

- 複数人物を同時に扱う。
- 各人物の行動ラベルを推定する。
- 斜め上からコート全体を見下ろすような固定カメラ映像を扱う。
- 外部trackerに依存せず、RNNでフレーム間の人物を対応づける。
- 他者の振る舞いや全体状況を考慮して個人行動を推定する点は、倉庫内の複数人作業文脈にも関係する。

#### 私の研究とズレる点

- 対象は物流倉庫ではなく、主にスポーツや集団活動。
- 検品・仕分け・搬送のような作業認識ではない。
- 十分な位置・行動ラベルを前提とする教師ありend-to-end学習。
- 少量アノテーションには対応していない。
- フレーム間マッチングは短い時間窓が中心で、長時間ID追跡ではない。

#### 既存技術でできることとして示唆される点

- RGB画像シーケンスから、複数人物の検出と個人行動認識を同時に行える。
- 検出と行動認識で特徴マップを共有できる。
- RNNにより、短期的な人物対応づけと時間コンテキストの利用が可能。
- 個人行動と集団活動を同時に認識する枠組みがある。

#### まだ難しいこと・限界

- 長時間IDを明示的に保持し続けること。
- 少量ラベル条件での学習。
- 実倉庫の作業ラベルへの適用。
- 遮蔽・退出再入場を含む長期tracking。

#### 報告で使える一言

複数人物の検出と個人行動認識、さらに集団活動認識をend-to-endで行う研究もある。ただし、対象はスポーツなどの短いシーンが中心で、長時間IDを維持して倉庫作業区間を認識する問題や少量ラベル条件には直接対応していない。

#### Citation Decision

参考程度。

複数人物の個人行動認識と集団文脈を同時に扱うネットワーク設計として参考になるが、本研究の主要比較対象ではない。

### Automated Work Sampling via Two-Stream Convolutional Networks for Site Surveillance

Status: 精読候補

#### 何の論文か

建設現場の俯瞰的な監視カメラ映像から、Two-stream Convolutional Networksを用いて作業員の連続的な作業・活動を認識し、労働生産性評価のためのwork samplingを自動化・客観化する手法を提案した論文。

#### タスク

- 建設作業員の連続的な活動認識。
- 型枠工・鉄筋工などの作業を対象にする。
- 運搬、組み立て、休憩など16クラスの作業ラベルを扱う。
- 認識結果を生産的・半生産的・非生産的な時間割合へ集計する。

#### 入力・出力

- Input: 建設現場の高所監視カメラ映像。
- Camera: 実現場、高所約15m、低解像度、遮蔽やカメラ揺れあり。
- Feature inputs: RGBフレームとoptical flow。
- Output: 視野内の個別作業員に対する連続的な作業・活動ラベル。

#### 主な特徴表現

- RGB特徴。
- Optical flow特徴。
- Two-stream CNN。
- Worker trackingによる人物clip切り出し。
- Fusion strategyによるRGB streamとtemporal streamの統合。

#### 私の研究に近い点

- 実環境の俯瞰監視カメラ映像を使っている。
- 複数作業者が存在する建設現場を対象としている。
- 作業者をtrackingし、個別作業者ごとに作業ラベルを推定するpipelineである。
- 単なる異常検知ではなく、運搬・配置・加工作業など意味のある作業ラベルを扱う。
- 作業認識結果をwork sampling / productivity analysisに使う点が、倉庫作業のデータ化や作業モデル化と近い。
- 低解像度、オクルージョン、カメラ揺れなど実環境映像の問題を扱っている。

#### 私の研究とズレる点

- 対象は物流倉庫ではなく建設現場。
- 検品・仕分け・搬送ではなく、建設作業ラベル。
- 少量アノテーションには対応していない。
- 3秒ごとのclipに手作業でラベルを付与する教師あり学習。
- 複数物体追跡MOTではなく、手動初期化したbounding boxからsingle object trackingを各作業者に回す構成。

#### 既存技術でできることとして示唆される点

- 実環境の俯瞰監視カメラ映像から、作業者tracking、clip切り出し、行動認識、作業時間集計までのpipelineを構築できる。
- RGB + optical flowのtwo-stream networkで、具体的な作業ラベルを分類できる。
- 低解像度・遮蔽・カメラ揺れがある映像でも、fusion strategyにより作業認識性能を改善できる可能性がある。
- 16種類の作業ラベルを約80.5%の精度で分類できると報告されている。

#### まだ難しいこと・限界

- tracking開始時のbounding box初期化が手動であり、完全自動ではない。
- MOTを導入すると、誤検出やID switchが問題になるため、論文ではSOTを用いている。
- 未定義の作業クラスには対応しにくい。
- 少量ラベル条件では評価されていない。
- 倉庫の検品・仕分けのような細かい作業意味には、object / zone contextが必要になる可能性がある。

#### 報告で使える一言

建設現場では、俯瞰監視カメラ映像から作業者をtrackingし、RGBとoptical flowのtwo-stream CNNで作業ラベルを推定し、work samplingに使う研究がある。これは倉庫映像で作業者ごとの作業状態をデータ化する方向にかなり近い。ただし、trackingの初期化は手動で、少量ラベル条件や複数人物の完全自動MOTまでは扱っていない。

#### Citation Decision

精読候補。

本研究のVision側で、既存研究に近いpipelineとして重要。
特に「俯瞰監視カメラ + worker tracking + work activity recognition + productivity analysis」の比較対象として使える。

### Vision-Based Construction Activity Recognition via Attention and Re-Identification

Status: 精読候補。システム設計のベースラインとして重要。

#### 何の論文か

建設現場の固定カメラ映像を用いて、複数作業員のIDごとの姿勢・向き・作業対象物との関係を推定し、作業行動を認識する論文。

#### タスク

- 複数作業員検出。
- 作業員IDのReID / tracking。
- 姿勢推定または姿勢カテゴリ推定。
- 身体・頭部の向き推定。
- 作業対象物の検出。
- 各作業員IDごとの作業ラベル推定。

#### 入力・出力

- Input: 建設現場に設置された固定カメラのRGB画像フレーム。
- Output: 各作業員のID、姿勢、向き、作業対象物との関係、作業ラベル。

#### 主な特徴表現

- RGB特徴。
- Object detection。
- Person Re-Identification。
- Pose / posture特徴。
- Orientation / attention direction。
- Object / worker spatial relation。
- Tracklet / ID情報。
- Rule-based action definition。

#### 私の研究に近い点

- 実産業現場の固定カメラ映像を用いている。
- 複数人物を同時に扱う。
- ReIDにより作業員IDを維持しようとしている。
- 作業員の姿勢、向き、周辺物体との関係から作業内容を推定する。
- 行動そのものを大量に教師あり学習するのではなく、人・姿勢・向き・物体を個別に検出し、空間的関係のルールで行動を定義する。
- 少量アノテーションで作業認識を実現したい本研究の問題意識にかなり近い。
- 物流倉庫でも、検品台、棚、台車、商品、作業ゾーンとの関係に置き換えられる可能性がある。

#### 私の研究とズレる点

- 対象は物流倉庫ではなく建設現場。
- 作業内容は足場、鉄筋、木材など建設資材に関する作業。
- 最終的な行動判定は時系列深層モデルではなく、フレームごとの検出結果と空間関係に基づくルールベース。
- 長時間の作業区間認識や作業境界推定は主目的ではない可能性がある。
- 少量ラベルという点では近いが、弱教師あり学習や自己教師あり学習ではなく、構造化・ルール化によるアノテーション削減。

#### 既存技術でできることとして示唆される点

- YOLOv5により、作業員、作業対象物、姿勢・向きカテゴリを検出できる。
- Transformer-based ReIDであるTransReIDにより、複数作業員のID照合が可能。
- 人物、物体、姿勢、向きの空間的関係をルール化することで、行動そのものの大量ラベルなしに作業ラベルを推定できる。
- 実建設現場の作業員行動を、現場生産性管理に使える形へ構造化できる。

#### まだ難しいこと・限界

- カメラ視差により、実際には関係していない人物と物体のbounding boxが重なり、作業中と誤判定される可能性がある。
- 向き推定の誤りが、そのまま行動認識の誤りにつながる。
- ルールベースであるため、作業定義や現場レイアウトが変わると調整が必要になる可能性がある。
- 作業区間の長時間文脈や境界の曖昧さは十分に扱っていない可能性がある。
- 物流倉庫の検品・仕分けのように、同じ場所・同じ姿勢で意味が変わる作業では追加情報が必要になる可能性がある。

#### 報告で使える一言

建設現場では、作業行動そのものを大量ラベルで学習するのではなく、作業員・物体・姿勢・向き・ReIDを組み合わせ、空間的な関係性ルールで作業を推定する研究がある。これは、物流倉庫でも検品台、棚、台車、商品、作業ゾーンとの関係を用いて、少ない行動ラベルで作業認識する方向につながる可能性がある。

#### Citation Decision

精読候補。場合によっては必読。

少量アノテーションに対する構造化アプローチとして、本研究のVision側とかなり近い。
直接の比較対象というより、システム設計・問題設定・アノテーション削減の参考として重要。

#### Detailed Reading Note

この論文の重要な設計思想は、行動を直接end-to-endに分類するのではなく、検出可能な構成要素から組み立てる点にある。

行動定義:

> action = person x object x orientation x spatial relation

主なpipeline:

- YOLOによるperson / object detection。
- 姿勢・向き推定。
- body orientationとhead orientationからattention directionを推定。
- Person ReIDにより作業者IDを対応づける。
- 人・物体・向き・位置関係に基づくルールでactivityを判定する。

特徴:

- frame-basedな判定が中心。
- 約3秒ごとの判定。
- 時系列はほぼ使わず、使ってもtとt-1程度。
- action classifierというより、symbolic / rule-based activity inferenceに近い。

強み:

- 解釈可能。
- 行動ラベルを大量に集めなくても始められる。
- person-object interactionを明示的に扱う。
- 物流倉庫でも、作業者、台車、商品、棚、検品台、仕分けエリアの関係へ置き換えやすい。

弱み:

- 距離やIoUなどの閾値に依存する。
- 現場やレイアウトが変わるとルール調整が必要になる可能性。
- 時系列文脈が弱く、作業境界が曖昧な場合に弱い。
- 複雑な作業や、同じ場所・同じ姿勢で意味が変わる作業には追加情報が必要。

#### Implication For Warehouse Task Recognition

物流倉庫の対象作業に当てはめると、以下のように見える。

- Transport: 長距離移動 + 台車/荷物との関係があり、trajectoryやルールで比較的取りやすい可能性。
- Inspect: 低移動 + 検品台/商品/注文書周辺での滞在。Sortとの区別が難しい。
- Sort: 中程度の移動 + 商品や仕分け先とのinteraction。Inspectとの境界が曖昧。

このため、本研究ではTransportをまず取り、その後Inspect / Sortの区別にobject / zone / orientation / temporal contextを足していく設計が自然。

#### Early Experiment Insight

CNNやCLIP embeddingをそのまま使うと、人ごとのクラスタができ、作業よりも作業者ID差が強く出る可能性がある。

原因候補:

- ビブス色など、作業者IDに強く対応する外観特徴。
- 作業場所が固定されることによる背景バイアス。
- モデルが「作業」ではなく「人」や「場所」を学習する。

不要な情報:

- 人ID。
- ビブス色。
- 固定背景。

必要な情報:

- 姿勢。
- 動き。
- 近傍物体。
- 人と物体・作業領域のinteraction。

#### Candidate Design Inspired By This Paper

Baseline:

- person crop / person mask -> CNN -> activity classification。

Improvement 1:

- person maskを使って背景依存を減らす。
- SAMなどでbboxからperson maskを抽出する。

Improvement 2:

- grayscale / color jitter / HSV変換などでビブス色依存を抑制する。

Improvement 3:

- person feature + object one-hot / object featureを入力する。

Improvement 4:

- object label、距離、相対位置、zone proximityをinteraction featureとして入れる。

Improvement 5:

- [t-k, ..., t] の時系列をTransformerやTCNで扱い、作業境界の曖昧さを吸収する。

#### Possible Core Concept

> Interaction-aware vision-based activity recognition

人単体の見た目ではなく、人、周囲物体、作業領域、時系列文脈から作業を認識する。

従来の単純な発想:

> person appearance -> activity

本研究で狙う方向:

> person + nearby objects + zone + trajectory + temporal context -> activity

### Top-View Surveillance for Pedestrian Analysis and Public Safety Management

Status: 精読候補。俯瞰映像研究の辞書として重要。

#### 何の論文か

公共空間や交通ハブなどに設置されたtop-view / overhead camera映像を用いた、人物検出、追跡、行動認識、姿勢認識、公共安全管理に関するレビュー論文。

#### タスク

- Top-view映像からの人物検出。
- Pedestrian tracking。
- Re-identification。
- Pose / posture recognition。
- Action / behavior recognition。
- Public safety management。

#### 入力・出力

- Input: top-view camera映像。
- Modalities: RGB, depth, fisheye, omnidirectional cameraなど。
- Output: bounding box、trajectory、ID、pose / posture、行動クラス、異常検知結果など。

#### 主な特徴表現

- RGB特徴。
- Depth特徴。
- Pose特徴。
- Trajectory特徴。
- Multimodal特徴。
- Multi-camera / ReID特徴。

#### 私の研究に近い点

- top-view / overhead cameraに特化している。
- 複数人物の検出・追跡・群衆ダイナミクスを扱う。
- 顔情報が少ない俯瞰映像でのReIDやtrajectory linkingの課題を扱う。
- pose、trajectory、行動認識の既存手法を整理している。
- 購買行動、日常動作、荷物運搬など、作業・行動認識に近い事例も含む。
- 俯瞰映像データの不足、weak supervision、self-supervision、synthetic dataの活用に言及している。
- 工場、小売、建設現場など実環境応用も関連文献として含む。

#### 私の研究とズレる点

- 物流倉庫の検品・仕分け・搬送に特化した論文ではない。
- レビュー論文であり、特定の新規アルゴリズムを提案しているわけではない。
- 公共安全・交通ハブ・歩行者分析が中心で、倉庫作業認識とは目的が異なる部分がある。

#### 既存技術でできることとして示唆される点

- top-view RGB / depthカメラから人物検出とtrajectory抽出が可能。
- poseやtrajectoryを使って、転倒、歩行、物を押す、荷物運搬などの大きな行動を認識できる。
- multi-cameraやReIDにより、top-view環境でのID追跡を試みる研究がある。
- top-view映像特有の課題と、使われているデータセット・手法を体系的に把握できる。

#### まだ難しいこと・限界

- top-viewでは頭部や肩が中心に映り、手元や細かいジェスチャーが見えにくい。
- 検品や仕分けのようなfine-grained作業認識は難しい可能性が高い。
- 顔情報が使いづらく、ReIDが難しい。
- 密集環境でのオクルージョンが残る。
- 高品質なtop-view annotated datasetが不足している。
- 少量ラベル・弱教師あり・自己教師ありは課題として言及されるが、特定の解法は別途確認が必要。

#### 報告で使える一言

俯瞰映像に特化したレビューでは、top-viewカメラからの人物検出・追跡・ReID・pose・行動認識の研究が整理されている。人物の位置や大きな動作の認識は進んでいる一方で、俯瞰では手元が見えにくく、顔情報も使いづらいため、検品・仕分けのような細かい作業認識やID維持、アノテーション不足が課題として残る。

#### Citation Decision

精読候補。背景・関連研究整理では必読に近い。

本研究の「俯瞰映像から何ができて何が難しいか」を説明する基盤文献として重要。

### iSafetyBench: A Video-Language Benchmark for Industrial Safety

Status: 参考程度。VLM / zero-shot industrial action understandingの参考。

#### 何の論文か

産業環境における日常業務および危険事象について、Vision-Language Modelの動画理解能力を評価するためのvideo-language benchmarkを提案し、最新VLMをzero-shotで評価した論文。

対象環境:

- 工場
- 倉庫
- 建設現場
- その他の産業・安全環境

#### タスク

- Video-language question answering。
- 行動認識に関するmultiple-choice question。
- Single-answer / multi-answer MCQ。
- Zero-shot VLM evaluation。

#### 入力・出力

- Input: 4から8秒程度の短いvideo clipとテキスト質問。
- Output: 選択肢から選ばれる行動・状況ラベル。

#### 主な特徴表現

- RGB video。
- Text。
- Multimodal / vision-language representation。
- VLMによるzero-shot video understanding。

#### 私の研究に近い点

- 産業環境を明示的に対象としている。
- 倉庫、工場、建設現場などが含まれる。
- Material Handling & MovementやAssembly & Production Tasksなど、作業ラベルのtaxonomyが参考になる。
- 追加学習なしのzero-shot評価であり、少量ラベル・低アノテーションという問題意識に近い。
- 最新VLMで産業作業がどこまで認識できるかを見る材料になる。

#### 私の研究とズレる点

- 俯瞰固定カメラに限定されていない。
- YouTube由来など、多様な視点・カメラワークのclipが混ざる。
- 人物ID追跡は行わない。
- 各IDに紐付けた作業認識ではなく、clip全体に対する質問応答。
- 長時間作業区間認識ではなく、短いclipの理解。

#### 既存技術でできることとして示唆される点

- GPT-4oやOvis2-8BなどのVLMにより、追加学習なしでも一部の産業作業を認識できる。
- 物体中心で明確な組立作業や車両関連タスクは比較的認識しやすい可能性がある。
- VLMを使うことで、産業動画に対してzero-shotな作業理解を試せる。

#### まだ難しいこと・限界

- Material Handling & Movementや人同士のinteractionなど、物流倉庫に近い微妙な動作は精度が低いとされる。
- 複数行動が同時に発生するmulti-label scenarioは難しい。
- 稀な危険事象の認識も難しい。
- ID追跡や人物ごとの作業ラベル推定には対応していない。
- 俯瞰固定カメラ・長時間・少量ラベル作業区間認識とはタスク構造が異なる。

#### 報告で使える一言

産業環境向けのvideo-language benchmarkでは、最新VLMを使えば一部の明確な作業はzero-shotで認識できる一方、物流倉庫に近いMaterial Handlingや複数人物のinteractionはまだ精度が低いと報告されている。VLMは低アノテーション化の参考にはなるが、人物IDごとの長時間作業認識を直接解くものではない。

#### Citation Decision

参考程度。

産業作業ラベルのtaxonomy、VLMのzero-shot限界、低アノテーション化の周辺文献として使える。
主要なtracking / per-ID work recognitionの比較対象ではない。

### Video dataset for the detection of safe and unsafe behaviours in workplaces

Status: 参考程度

#### 何の論文か

実際の製造工場に設置された俯瞰固定IPカメラ映像を用いて、労働者の安全・不安全行動を検出・分類するためのビデオデータセットを提案する論文。

#### タスク

- 工場内の作業者行動を安全/不安全行動として分類する。
- 8クラスの行動ラベルを扱う。
- 例: 安全通路の歩行、パネル操作、フォークリフトでの運搬、安全/不安全行動。

#### 入力・出力

- Input: 工場内の俯瞰固定IPカメラからのRGB動画。
- Camera: 地上約4m、1920 x 1080、24fps。
- Output: クリップ動画ごとの行動ラベル。

#### 主な特徴表現

- RGB動画。
- データセット論文であり、特定の特徴抽出手法やモデル提案が主目的ではない。

#### 私の研究に近い点

- 実産業環境で撮影された俯瞰固定カメラ映像を扱っている。
- 作業者の行動ラベルを扱っている。
- 工場・作業現場における実用的な行動認識という点で近い。
- フォークリフトでの運搬など、物流・倉庫に近い行動も一部含まれる。

#### 私の研究とズレる点

- 物流倉庫の検品・仕分け・搬送ではなく、安全/不安全行動が対象。
- アルゴリズム提案ではなく、データセット公開が主目的。
- 人物IDの継続的な追跡、bounding box、trajectory、trackletは主対象ではない。
- 少量ラベル、弱教師あり、自己教師あり学習は扱っていない。
- クリップ単位の行動分類が中心で、長時間IDごとの作業区間認識ではない。

#### 既存技術でできることとして示唆される点

実産業環境の俯瞰固定カメラ映像から、特定の作業者行動をクリップ単位でラベル付けし、行動分類データセットとして整備することは可能。

YOLOやConvLSTMなどの一般的な深層学習モデルを用いて、安全/不安全行動の分類・検出を評価する基盤として使える。

#### まだ難しいこと・限界

- クラス不均衡がある。
- 俯瞰映像の2次元投影により、実際の位置関係と映像上の位置関係がずれる空間的曖昧さがある。
- ID追跡なしでは、長時間にわたって同じ作業者の作業状態を追うことはできない。
- フレーム単位・人物ID単位の密な作業認識ではない。
- 少量アノテーション条件での有効性は確認できない。

#### 報告で使える一言

実工場の俯瞰固定カメラ映像を用いた安全/不安全行動認識データセットは存在しており、実環境映像から作業者行動を分類する研究は進んでいる。一方で、この研究はクリップ単位の行動ラベルが中心で、人物IDを長時間追跡しながら少量ラベルで作業区間を認識する設定までは扱っていない。

#### Citation Decision

参考程度。

実産業環境の俯瞰映像データセット例としては使える。
ただし、本研究の主要比較対象や手法上の直接的な先行研究ではない。
