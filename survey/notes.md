# Survey Notes

## Current Question

俯瞰固定カメラ映像から、複数人物のIDを追跡し、各IDの作業ラベルを時系列で推定することは、既存技術でどこまで可能か。

特に知りたいのは、物流倉庫のような実環境で、少ないアノテーションコストで検品・仕分け・搬送などの作業認識ができるか。

## Short Takeaway

人物検出・追跡はかなり進んでいる。
ByteTrack、BoT-SORT、OC-SORTなどを使えば、固定カメラ映像から人物boxとIDを得る基盤は作れる。

ただし、これらは基本的に作業ラベルを出さない。
一方で、action recognitionやspatio-temporal action detectionは人物ごとの行動推定に近いが、AVAなどの短いクリップ中心の評価が多く、物流倉庫の長時間・俯瞰・多人数・遮蔽・類似作業服・少量ラベルという条件とはずれがある。

したがって、Vision側の研究は「新しいtrackerを作る」より、既存trackerで得た人物軌跡やtrackletを単位に、少量ラベルで作業認識する方向が自然。

## Updated Takeaway From TRUSCO-specific Deep Research

TRUSCOの実環境設定を明示して再調査した結果、結論はより明確になった。

> multi-camera top-view warehouse trackingに近い研究は存在するが、そこからper-worker task recognitionへ接続する研究はまだ薄い。

特に近い研究として、倉庫天井に設置した多数の広角カメラから作業者を追跡する研究や、ceiling cameraとdigital twinを用いたwarehouse monitoringの研究が挙がった。
これらは、倉庫全体のworker trajectory、asset tracking、scene analysis、digital twin接続にはかなり近い。

一方で、これらは主にtracking、monitoring、asset visualization、scene analysisまでであり、各worker IDに対してInspection / Sorting / Transportationのような作業ラベルを長時間trajectoryから推定するところまでは踏み込んでいない。

物流・工場の作業認識自体は存在する。
しかし主流は、warehouse-wide top-viewではなく、OpenPack、LARa、InHARDのようなworkstation、wearable、IMU、IoT、motion capture、RGB-D、close camera中心のデータセットや手法である。

したがって、現在の最も重要な研究ギャップは以下。

> 多数の天井カメラを統合した倉庫全体のtop-view tracking基盤に対して、長時間trajectory、zone、object / equipment context、ReID、IMU由来のweak labelsを組み合わせ、少量アノテーションでper-worker task segmentsを推定する研究は限定的である。

## Main Gap

trackingはIDを出すが、作業ラベルを出さない。
action recognitionは行動ラベルを出せるが、長時間のworker ID維持を主目的にしていない。
industrial / retail HARは意味ラベルが近いが、少人数・作業台中心・限定環境のものが多い。

この切れ目に、修論のVision側の余地がある。

## Concrete Examples

### 0. Overhead and multi-person settings

俯瞰・高所固定カメラの複数人物追跡は、かなり研究が進んでいる。
単一カメラなら、一般的な人物検出とMOT手法を組み合わせることで、複数人物のbox + ID軌跡を得ることは現実的。
複数カメラの場合も、WILDTRACKのようなcalibrated multi-camera datasetや、TrackTacular、MVTrajecterのようなBEV tracking系の研究があり、複数視点を統合して地面平面上の人物軌跡を推定する方向が進んでいる。

ただし、ここで進んでいるのは主に「誰がどこにいるか」を追跡する部分。
これらの研究は通常、検品・仕分け・搬送のような作業ラベルまでは扱わない。

俯瞰映像に近い行動認識データとしては、MERL ShoppingやRetailActionのような小売・棚周りのデータが参考になる。
しかし、物流倉庫のように、広い空間で複数人物が移動・交差・退出再入場しながら、長時間の作業を行う設定とはまだ差がある。

現時点の理解:

- 複数人物の位置・軌跡推定はかなり進んでいる。
- 複数カメラを使ったBEV上の人物追跡も進んでいる。
- 俯瞰・棚周りの行動認識に近いデータセットもある。
- ただし、俯瞰固定カメラ + 複数人物 + 長時間ID + 倉庫作業ラベル + 少量ラベルを同時に満たす研究・データセットはまだ少ない。

### 1. Tracking is strong, but does not solve work recognition

ByteTrack、BoT-SORT、OC-SORTなどのMOT手法は、人物boxとIDを時系列に結び付ける技術として強い。
そのため、俯瞰映像から「誰がどこにいたか」「どの方向に移動したか」「どこで滞留したか」は既存技術でかなり扱える可能性がある。

ただし、これらの出力は基本的にbox + IDであり、「検品」「仕分け」「搬送」のような作業ラベルは出ない。
したがって、tracking結果をどう作業認識へ接続するかが別問題として残る。

### 2. Action recognition is strong, but often short-clip oriented

SlowFast、VideoMAE、TubeR、EVAD、STARなどは、映像中の行動認識や時空間行動検出に関連する代表的手法。
短いclipや人物tubeletに対して行動ラベルを付ける研究は進んでいる。

一方、物流倉庫では、作業が数分から数十分続くことがあり、作業者IDを保ったまま長時間の作業区間を推定する必要がある。
この点は、一般的な短時間clip分類やAVA系のaction detectionとは設定がずれる。

### 3. Industrial / retail datasets are close, but not identical

MERL ShoppingやRetailActionは、俯瞰・店舗・棚周りの行動という意味で近い。
IKEA ASM、Assembly101、CarDAなどは、実作業や組立作業の認識という意味で参考になる。
また、"Video dataset for the detection of safe and unsafe behaviours in workplaces" のように、実工場の俯瞰固定カメラ映像から安全/不安全行動を分類するデータセットもある。

ただし、これらは小売、組立、作業台中心、少人数、あるいは特定工程に寄ったものが多い。
また、clip単位やframe単位の行動ラベルが中心で、ID追跡や少量ラベル学習を扱わないものも多い。
物流倉庫のように、複数人物が広い空間を移動し、交差し、時々見切れながら、検品・仕分け・搬送を行う設定とは完全には一致しない。

### 4. Coarse behavior and fine-grained work labels differ

軌跡から、歩行、停止、滞留、エリア移動、台車移動らしさのようなcoarse behaviorは比較的扱いやすい可能性がある。

一方で、検品と仕分けの区別は、人物の移動軌跡だけでは難しい可能性がある。
例えば、同じ作業台付近で立ち止まっていても、注文書と商品を照合しているのか、商品を行き先ごとに分けているのかは、手元、物体、棚、台車、作業領域などの文脈が必要になる。

### 5. Low annotation is still a key difficulty

フレーム単位で全人物に作業ラベルを付ければ、教師あり学習としては扱いやすくなる。
しかし、実倉庫映像では長時間・多人数であり、密なアノテーションは高コストになる。

そのため、作業区間単位の粗いラベル、疎な時刻ラベル、video-level label、pseudo label、IMUから得た弱教師などを使って、アノテーションコストを下げる設計が必要になる。

## Useful Framing

> Coarseなworker analyticsは既存技術で実現可能になりつつあるが、俯瞰固定カメラ下のfine-grainedな倉庫作業認識では、長時間ID、作業境界の曖昧さ、物体・領域文脈、少量ラベルが未解決課題として残る。

## Emerging Observation: Construction vs Warehouse / Factory

調査を進めた結果、俯瞰映像を用いたmulti-person activity recognitionは、建設現場では比較的多く見つかる。
一方で、物流倉庫や工場では、同じような「俯瞰固定カメラで複数人物を追跡し、作業ラベルを推定する」研究は少なく見える。

物流倉庫や工場で見つかる研究は、以下に寄る傾向がある。

- 作業者に近いカメラ。
- 作業台や特定工程の近接映像。
- egocentric videoやsmart glasses。
- wearable sensor, motion capture, RGB-D。
- forkliftなど機械側のセンサ。
- 工程や作業対象物を細かく追うデータセット。

### Why Construction Has More Overhead Multi-person Work Recognition

考えられる理由:

1. 建設現場は、広い現場を高所カメラで見渡す監視・進捗管理・work samplingの需要が強い。
2. 作業者の移動、運搬、組立、休憩などが、俯瞰や斜め俯瞰でも比較的視覚的に区別しやすい場合がある。
3. productivity analysisやsafety monitoringの文脈で、作業時間の大まかな分類でも価値がある。
4. 作業者・資材・ゾーンの関係が、空間的ルールとして定義しやすい研究がある。

### Why Warehouse / Factory Often Uses Closer Views

考えられる理由:

1. 検品・仕分け・梱包・組立のような作業は、手元、商品、工具、部品、棚状態などの細かい情報が重要。
2. 俯瞰カメラでは頭部や肩、上半身が中心になり、手元の操作や対象物の状態が見えにくい。
3. 同じ場所・姿勢でも作業意味が変わるため、trajectoryだけでは区別しにくい。
4. 工場では作業台やラインが固定されていることが多く、近接カメラ、RGB-D、motion capture、wearable sensorで工程を細かく追う方が自然。
5. 倉庫では商品・レイアウト・作業内容・作業者情報が機密になりやすく、公開データ化が難しい可能性がある。

### Implication For This Thesis

この観察から、本研究では以下の立て方ができる。

> 建設分野では、俯瞰・監視カメラ映像を用いた作業者活動認識やwork samplingの研究が進んでいる。一方で、物流倉庫や工場では、近接カメラやセンサを用いて個々の工程を詳細に追う研究が多く、俯瞰映像から複数作業者を長時間追跡し、少量ラベルで作業区間を認識する研究は限定的である。

この差分は、物流倉庫の現場で日常的に蓄積される俯瞰映像を活用する研究の意義になる。

TRUSCO-specific Deep Researchでも、この認識は概ね支持された。
建設分野では、site surveillance videosを用いたautomated work sampling、worker activity recognition、pose-based analysis、multi-camera pose fusionが比較的豊富に確認された。
一方で、logistics / factoryでは、作業認識はあるものの、wearable、workstation camera、RGB-D、motion capture、IoT readingsなどに寄る傾向が強い。

この違いは、以下のように説明できる。

- constructionでは、広い現場を高所から監視し、生産性や安全を粗く評価する需要が強い。
- warehouse / factoryでは、作業意味が手元、商品、工具、棚、台車、注文書、設備状態に依存しやすい。
- top-viewでは位置や動線は取りやすいが、fine-grainedな作業意味は見えにくい。
- warehouseでは商品情報や業務情報が映るため、公開データセット化が難しい可能性がある。

### Useful Reference Directions

本研究に近い参考手法:

- Automated Work Sampling via Two-Stream Convolutional Networks for Site Surveillance
- Vision-Based Construction Activity Recognition via Attention and Re-Identification
- Top-View Surveillance for Pedestrian Analysis and Public Safety Management
- LART / trajectory-centric action recognition

これらを参考にしつつ、物流倉庫では以下の要素を検討する。

- tracklet / trajectory
- worker-object-zone relation
- ReID / ID tracking
- low annotation or rule-based activity definition
- IMUとの弱教師・補助情報としての接続

## Possible Research Questions

1. 俯瞰固定カメラ映像から得られる人物軌跡またはtrackletを用いて、作業区間単位の少量ラベルから検品・仕分け・搬送を認識できるか。
2. 人物軌跡にzoneやobject contextを加えることで、poseやtrajectoryだけでは区別しにくい倉庫作業を改善できるか。
3. 疎な時刻ラベル、作業区間ラベル、またはvideo-level labelだけで、per-IDの作業区間を推定できるか。
4. IMUで学習した作業表現または作業境界を、映像側の弱教師として利用できるか。

TRUSCO-specific Deep Research後のRQ候補:

1. Global top-view trajectoriesとzone transitionだけで、Transport / Inspect / Sortをどこまで識別できるか。
2. InspectとSortの識別に、worker orientation、object proximity、work zone、cart / shelf / inspection table contextはどれだけ効くか。
3. Smartphone IMUやIoT由来のtask estimationを、camera-side task recognitionのweak labelとして使えるか。
4. Frame-level classificationではなく、minute-scale task segment recognitionとしてモデル化することで、長時間作業と少量ラベルに対応できるか。
5. Task semanticsを付加したdigital twinは、trajectory-only digital twinよりもlayout / staffing optimizationに有利か。

## Promising Thesis Direction

第一候補:

> Track-aware weakly supervised warehouse work recognition

具体的には、既存の人物追跡手法で得たworker trackletを入力として、少量の作業区間ラベルからInspect / Sort / Transportを分類する。

この方向の良い点:

- IMU側の「少量ラベル・SSL」と研究テーマがつながる。
- 既存trackerを使えるので、Vision側で巨大な実装に巻き込まれにくい。
- 倉庫映像の日常的な蓄積という共同研究先のニーズに合う。
- 失敗しても、どの条件で既存技術が破綻するかを議論できる。

## How To Continue The Survey

Deep Research一回だけでsurvey完了とはしない。
ただし、初回の地図としては使える。

次にやること:

1. 本当に読むべき論文を5から10本に絞る。
2. それぞれについて「自分の設定に近いか」「何ができて何ができないか」だけ確認する。
3. 既存技術でできる範囲と、修論で主張できる範囲を分ける。
4. 足りない論点だけ追加でDeep ResearchまたはScholar検索する。

読む優先度:

- tracking系: ByteTrack, BoT-SORT, OC-SORT
- trajectory/action系: LART, TubeR or STAR
- video SSL系: VideoMAE
- industrial/retail系: MERL Shopping, RetailAction, CarDA or Assembly101
