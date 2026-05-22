# 俯瞰固定カメラ映像における複数人物のID追跡と行動認識の研究調査

## 結論

結論だけ先に述べると、**俯瞰視点または高所固定カメラから、複数人物の長時間ID追跡と、各IDに対する fine-grained な作業ラベルの時系列推定を、物流倉庫や工場の実環境で一体的に解く技術は、公開研究ではまだ十分に確立していません**。既存研究は、概ね **追跡は MOT/MPT 系、行動認識は AVA 系の spatio-temporal action detection、産業応用は assembly/retail の限定的 HAR** に分かれており、これらが同一ベンチマーク上で統合されている例は少ないです。MOT 側は ByteTrack・BoT-SORT・OC-SORT・FairMOT などでかなり成熟していますが、これらは基本的に **box+ID** を出すだけで行動は出しません。一方、TubeR・WOO・EVAD・STAR などの action detection は **人物ごとの box/tubelet と action** を出力できますが、評価は短〜中尺クリップ中心で、**物流現場の長時間ID維持、画角外再入場、似た作業服、遮蔽、作業ラベル不足**までを同時に扱う設定とはズレがあります。citeturn24view2turn40view4turn40view5turn40view0turn26view12turn39view6turn39view5turn24view8

また、**公開データセットの不足が、モデルそのもの以上に大きなボトルネック**です。tracking 側には MOT17/MOT20/DanceTrack/WILDTRACK、action 側には AVA/JRDB-Act/MultiSports/MEVA、産業・小売側には IKEA ASM、Assembly101、HA4M、CarDA、MERL Shopping、RetailAction がありますが、**「天井付近の固定カメラ」「複数人物」「長時間ID」「物流・製造作業ラベル」「遮蔽・交差・退出再入場」「少量ラベル」**を同時に満たす公開ベンチマークは、私が確認した範囲では見当たりませんでした。むしろ最近の AI City Challenge が retail/warehouse を明示的に扱いながら、MTMC 側では synthetic indoor data を使っていることは、**実環境データの不足が現在進行形の課題**であることを示しています。citeturn35view0turn34view8turn36view0turn25view8turn32view0turn30search0turn31view6turn25view7turn25view0turn25view2turn25view5turn25view4turn25view6turn8search3turn33view3turn18search7

したがって、修士研究としては、**新しい汎用 tracker を一から作る**よりも、**trajectory-centric な作業認識**、**multi-camera BEV tracking と作業ラベルの接続**、**少量アノテーション・弱教師あり・自己教師あり**、**IMU と映像のクロスモーダル学習**、**レイアウト差・カメラ差への汎化**に新規性を置く方が、現状の研究地図に対して自然で、かつ成立しやすいと考えられます。citeturn18search9turn18search10turn39view3turn38search3turn14search13turn14search0turn10search2turn9search6

## 領域の見取り図

このテーマは、一見すると「tracking + action recognition」の単純な足し算に見えますが、実際には研究領域がかなり分かれています。特に重要なのは、**どの領域が何を出力し、何を前提にし、あなたの設定にどこまで近いか**を見誤らないことです。

| 領域 | 何を解くか | 典型的な入出力 | 倉庫・工場設定との距離 | 出典 |
|---|---|---|---|---|
| Multi-object tracking / multi-person tracking | 各フレームの人物 box を時系列で同一 ID に結び付ける | 入力: 画像列または detections、出力: box+ID 軌跡 | **最重要な基盤**。ただし多くは行動ラベルを出さない | FairMOT, ByteTrack, BoT-SORT, OC-SORT, TrackFormer citeturn40view0turn24view2turn40view4turn40view5turn24view1 |
| Person re-identification | 異なるフレーム・カメラ間で同一人物かを判定する | 入力: cropped person images、出力: embedding / match score | **単一カメラの再入場・複数カメラ handoff に重要**。ただし標準 ReID は前/側面寄りで、俯瞰には弱い | TransReID citeturn40view7 |
| Overhead / top-view ReID | 俯瞰映像特有の識別を扱う | RGB-D / depth+intensity / top-view RGB | **直接関連**だが文献数が少なく、しばしば depth 依存。RGB-only ceiling camera とはずれがある | TVPR top-view RGB-D ReID、overhead depth/intensity ReID citeturn16search1turn16search12 |
| Multi-view pedestrian tracking / BEV tracking | 複数カメラを地面平面や 3D に統合して人物を追跡する | 入力: 同期複数カメラ、出力: BEV occupancy / world-coordinate tracks | **複数の高所固定カメラに最も近い**。遮蔽や交差への耐性が高いが、行動は通常扱わない | WILDTRACK, TrackTacular, MVTrajecter citeturn25view8turn18search9turn18search10 |
| Video action recognition | クリップ全体に単一または複数ラベルを付ける | 入力: clip / pose sequence、出力: clip-level label(s) | 追跡済み tracklet ごとに使えば有効。ただし **ID は自動では維持しない** | SlowFast, VideoMAE, PoseC3D citeturn11search1turn39view3turn12search0 |
| Spatio-temporal action detection | 人物の位置と行動を空間・時間で同時検出する | 入力: video clip、出力: person box/tubelet + action label | **各人物に action を付ける点で最も近い**。ただし benchmark は AVA/MultiSports 中心で、長時間 ID 管理は主目的でない | AVA, TubeR, WOO, EVAD, STAR citeturn32view0turn26view12turn39view6turn39view5turn24view8 |
| Group activity recognition / social understanding | シーン全体または group 単位の活動を認識する | 入力: 多人物 scene、出力: scene/group label | 協調作業や相互作用には有益だが、**個人 ID ごとの作業ラベル**とは別問題 | GroupFormer, JRDB-Social citeturn21search3turn21search2 |
| Weakly / self- / semi-supervised video understanding | ラベル不足での表現学習・時間区間学習 | 入力: unlabeled or sparsely labeled videos、出力: pretrained representation / weakly localized segments | **アノテーションコストを下げる上で本命**。ただし多くは一般動画・単一主体前提 | VideoMAE, semi-supervised VAD, weakly supervised TAL, timestamp-supervised segmentation, STEPs citeturn39view3turn38search3turn14search13turn10search3turn14search0turn10search2 |
| Industrial / warehouse / retail HAR | 実際の工程・作業の理解 | 入力: 固定カメラ / RGB-D / multimodal、出力: activity / posture / progress | **意味ラベルは最も近い**が、多くは workstation 単位・少人数・追跡非中心 | IKEA ASM, Assembly101, HA4M, CarDA, MERL Shopping, RetailAction, production-floor studies citeturn25view0turn25view2turn25view5turn25view4turn25view6turn8search3turn23search3 |

この整理から重要なのは、**あなたの設定に本当に近いのは「MOT」でも「action recognition」でも単独ではなく、multi-camera BEV tracking と per-track action modeling を、industrial/retail HAR のラベル設計と接続した領域**だという点です。現状の SOTA はその接点が細く、したがって研究ギャップが残っています。citeturn18search9turn18search10turn27view9turn25view6turn25view4

## 主要手法と代表論文

現状の手法は、大きく分けると **tracking 重視**, **action 重視**, **industrial application 重視**に分かれます。実運用を考えると、最も再現しやすいのは **tracking-by-detection + per-track action head** の modular pipeline です。一方、研究的には **tubelet-based end-to-end action detection** や **trajectory-centric action modeling** が、ID と行動の統合に近い方向を向いています。citeturn24view2turn40view4turn26view12turn24view8turn41view4

| 年 | 論文・著者 | 手法の要点 | タスク | 主なデータ | 倉庫設定での限界 | 出典 |
|---|---|---|---|---|---|---|
| 2020 | **FairMOT** — Zhang et al. | 検出と ReID を同じ encoder-decoder で扱う one-shot tracker。tracking と detection の “fairness” を意識した設計 | single-camera MOT | MOT17/MOT20 | 行動ラベルなし。単一カメラ人物追跡に強いが、作業認識は別途必要 | citeturn40view0turn40view2 |
| 2022 | **ByteTrack** — Zhang et al. | 低信頼 detection まで association に使う単純かつ強力な tracking-by-detection。MOT17 test で 80.3 MOTA / 77.3 IDF1 / 63.1 HOTA | single-camera MOT | MOT17, MOT20 | 行動なし。appearance が弱くても強いが、長時間 re-entry や multi-camera は未解決 | citeturn24view2 |
| 2022 | **BoT-SORT** — Aharon et al. | Robust association + motion compensation + ReID。MOT17/MOT20 の主要指標で上位 | single-camera MOT | MOT17, MOT20 | benchmark では強いが、やはり action は別問題 | citeturn40view4 |
| 2023 | **OC-SORT** — Cao et al. | 観測中心の motion update により occlusion と non-linear motion へ強くした SORT 系。700+ FPS on CPU | online MOT | MOT17, MOT20, DanceTrack | 類似外観や短期遮蔽には有効だが、作業ラベル・multi-camera handoff は扱わない | citeturn40view5 |
| 2022 | **TrackFormer** — Meinhardt et al. | Transformer の track queries で identity を持続。短期 re-identification を attention 内で行う | end-to-end MOT | MOT benchmarks | 論文自体が **large movement を伴う長期 occlusion には不向き**と示しており、広い倉庫での退出再入場には弱い | citeturn24view1turn40view6 |
| 2024 | **TrackTacular** — Teepe et al. | 複数視点特徴を BEV に lift して detection/tracking。appearance と motion を併用 | multi-view pedestrian tracking | WILDTRACK, MultiviewX, Synthehicle | action を出さない。既存 multiview pedestrian datasets が one-scene で overfit しやすい問題も指摘 | citeturn18search9turn18search0 |
| 2025 | **MVTrajecter** — Yamane et al. | 過去複数時刻の trajectory motion / appearance cost を使う end-to-end BEV pedestrian tracking | multi-view pedestrian tracking | public MVPT benchmarks | 俯瞰 multi-camera tracking には近いが、作業認識なし | citeturn18search10 |
| 2019 | **SlowFast** — Feichtenhofer et al. | 低 FPS の spatial semantics と高 FPS の motion を分けて処理する強力な video backbone | video action recognition | Kinetics 等 | per-ID 追跡や action localization は別途必要 | citeturn11search1 |
| 2022 | **VideoMAE** — Tong et al. | 高 masking 率で self-supervised video pretraining。小規模データでも有効 | self-supervised video representation | Kinetics, SSv2, UCF101 等 | 直接的な box-level / ID-level 出力はないが、少量ラベル設定で有望 | citeturn39view3 |
| 2022 | **TubeR** — Zhao et al. | 人物 detector や proposal を使わず、動画から直接 tubelets と action labels を出力 | spatio-temporal action detection | AVA, UCF101-24, JHMDB | **person-centric action** には近いが、長時間 ID 管理や multi-camera 連結は主対象でない | citeturn26view12 |
| 2021 | **WOO** — Chen et al. | “watch once” の unified backbone が actor localization と action classification を同時出力 | end-to-end video action detection | AVA, UCF101-24, JHMDB | tubelet/action 側の統合であり、倉庫の tracking benchmark とは直接つながらない | citeturn39view6 |
| 2023 | **EVAD** — Chen et al. | ViT ベースの efficient action detector。AVA v2.2 で 39.7 mAP を報告 | video action detection | AVA v2.2 | 効率は高いが、industrial labels でも long-term IDs でもない | citeturn39view5 |
| 2024 | **STAR** — Gritsenko et al. | end-to-end で predicted tubelets を出す video transformer。proposal 不要の action localisation | spatio-temporal action localisation | AVA 等 | 短い時空間管（tube）には強いが、施設全体での worker identity persistence は範囲外 | citeturn24view8turn26view13 |
| 2023 | **LART** — Rajasegaran et al. | tracking + 3D pose + appearance を **Lagrangian** に扱う trajectory-centric action recognition。tracking が action 認識に有益と示す | action recognition on tracklets | AVA, Kinetics-400 | **人の動き**には強いが、object manipulation を含む fine-grained work semantics をそれだけで十分には捉えられない | citeturn41view4turn41view2turn41view0 |
| 2023 | **Human worker activity recognition in a production floor** — Mastakouris et al. | production floor 上で 2 人の worker の manual assembly / part handling を認識 | industrial activity recognition | production-floor data | 現場に近いが、少人数かつ tracking 主体ではなく、混雑した multi-person ceiling-view とは距離がある | citeturn23search3 |
| 2025 | **CarDA framework** — Papoutsakis et al. | 実工場ラインで 3D pose, posture, action, task progress を扱う枠組み。CarDA を導入 | industrial behavior understanding | CarDA | real industrial line という点は強いが、主眼はライン作業・姿勢・進捗で、物流倉庫の多人数 ceiling-view 作業とは一部異なる | citeturn25view4turn24view14 |
| 2026 | **Real-time multi-worker identification and action recognition** — Lee et al. | 固定 CCTV から pose estimation と facial embeddings を用いて worker identification と activity recognition を統合 | applied industrial HAR | industrial site CCTV | コンセプトは近いが、顔埋め込み依存は俯瞰・遠距離・遮蔽下で不利。公開 benchmark としての一般性も未検証 | citeturn23search7 |

この表から見える現実はかなり明快です。**tracking の代表手法は ID を出すが action を出さない**。**action detection の代表手法は person-centric action を出すが、長時間 worker ID を安定維持する benchmark では評価されない**。そして **industrial studies は意味ラベルが近い代わりに、人数・視点・データ規模が小さい**。この三つの切れ目こそが、あなたの研究テーマの核心です。citeturn24view2turn40view4turn26view12turn24view8turn23search3turn24view14

特に重要なのは、**「tracklet を action の単位にする」発想が有望**だという点です。LART は tracking を使うことで “actions を dense に学習できる” と明示し、AVA/Kinetics 上で 100 万超の tracks を使って trajectory-centric な action modeling の有効性を示しています。これは、倉庫作業のような **連続的・長時間・曖昧境界**の task に対して、単発 frame classification より自然です。citeturn41view0turn41view1turn41view4

## データセットと評価設計

### データセット

公開データセットを整理すると、**tracking**, **spatio-temporal action**, **industrial/retail** の三群に分かれ、いずれか一群には強いが、三群を同時に満たすものがありません。これは研究ギャップであると同時に、修士研究の実験設計上の制約でもあります。citeturn35view0turn32view0turn25view4turn25view6

| データセット | 視点・カメラ | 主な注釈 | 倉庫設定との近さ | 主な弱点 | 出典 |
|---|---|---|---|---|---|
| **MOT17** | 単一カメラ、街路/広場/モール、移動/固定混在 | pedestrian boxes + IDs | ID tracking の標準基盤 | 行動ラベルなし、industrial scene ではない | citeturn35view0 |
| **MOT20** | 単一カメラ、極端な crowd | boxes + IDs | 高混雑 occlusion の耐性検証に有効 | 行動なし、屋内倉庫 ceiling-view ではない | citeturn34view7turn34view8 |
| **DanceTrack** | 単一カメラ、群舞・複雑 motion | boxes + IDs | **似た服・交差・occlusion** の proxy として非常に有用 | 倉庫ではない、行動ラベルなし | citeturn36view0turn36view2 |
| **WILDTRACK** | 7 台の静止カメラ、公共空間 | calibrated multiview detection / positions | 複数固定カメラ・空間校正の基礎 | 1 scene で小規模、作業ラベルなし | citeturn25view8 |
| **JRDB / JRDB-Act** | mobile robot の 360° RGB/3D、屋内外キャンパス | 2D/3D boxes, tracking, **2.8M+ action labels**, social groups, per-group social activity | **統合注釈という意味で最重要** | 固定 overhead ではない。作業ラベルも industrial ではなく日常/social 中心 | citeturn27view7turn30search0turn27view9 |
| **AVA / AVA v2.x** | 映画映像、主に第三者視点 | person boxes, 80 atomic actions, 1Hz dense labels, short temporal linking | per-person action benchmark の本流 | industrialではない。長時間ID評価より frame/tube action が主 | citeturn32view0turn39view5 |
| **MEVA** | 多視点 surveillance、屋内外、RGB/thermal/UAV | 37 activity types, actors/props bounding boxes, long untrimmed video | surveillance 的な continuous video に近い | coarse activity 寄りで industrial tasks ではない | citeturn25view7turn26view3 |
| **VIRAT** | surveillance, ground/aerial | event/activity annotations | carrying/loading など coarse task の参照に有用 | 古く、視点・ラベル粒度が粗い | citeturn8search0turn8search4 |
| **Okutama-Action** | aerial video | multiple concurrent human action detection | top-down 的発想の補助にはなる | drone 移動カメラで、固定 ceiling-view ではない | citeturn25view13turn22search4 |
| **MultiSports** | sports broadcast / fixed and dynamic views | 3200 clips, 37701 action instances, 902k boxes, 66 actions | multi-person spatio-temporal action の難しさを見るには良い | sports の fine-grained rules であり warehouse task ではない | citeturn31view6 |
| **MERL Shopping** | 固定 overhead、grocery store | 106 videos, ~2 min, action detection 用 | **固定 overhead + retail interaction** という点で近い | 規模が小さく、tracking benchmark としては弱い | citeturn25view6 |
| **RetailAction** | real convenience stores, multiview | human-object interaction の spatio-temporal localization | **現実店舗・棚 interaction** という意味でかなり近い | 2025 workshop で新しく、標準 benchmark 化はこれから | citeturn8search3turn8search11 |
| **IKEA ASM** | multi-view third-person + pose/object | 3M frames, furniture assembly actions/objects/pose | workstation assembly の fine-grained labelsに有用 | 多人数 floor monitoring ではない | citeturn25view0turn24view12 |
| **Assembly101** | 8 static + 4 ego | 4321 videos, 100K+ coarse / 1M fine segments, 18M hand poses | procedural action segmentation の非常に強いベンチマーク | crowded multi-worker ceiling-view とは離れる | citeturn25view2turn25view3 |
| **HA4M** | RGB-D camera, assembly task | RGB, depth, IR, point cloud, skeleton など 6 modalities | manufacturing HAR の multimodal 基盤 | 単一 assembly task 中心で多人数 tracking ではない | citeturn25view5 |
| **CarDA** | real industrial assembly line, multi-camera RGB-D + MoCap | worker behavior, posture, ergonomic risk, activity, task progress | 実工場データとして重要 | ライン作業中心で warehouse aisle の多人数 tracking とは違う | citeturn25view4turn24view14 |

この一覧から導ける最も重要な判断は、**修士研究で「公開データだけで全問題を一気通貫に評価する」ことは難しい**ということです。現実的には、  
**tracking は MOT17/MOT20/DanceTrack/WILDTRACK 系で検証し、action は AVA/JRDB-Act/MERL/Assembly 系で検証し、最後に小規模な自前データで統合評価する**、という段階的設計が堅実です。これは遠回りに見えますが、研究としてはむしろ説得力があります。citeturn35view0turn34view8turn36view0turn25view8turn32view0turn30search0turn25view6turn25view2turn25view4

### 評価指標

tracking と action を同時に扱う場合、**単一の万能指標はありません**。したがって、評価は分解して設計すべきです。

| 指標 | 元タスク | 何を測るか | 本テーマでの使い方 | 出典 |
|---|---|---|---|---|
| **MOTA** | MOTChallenge | 検出 miss / FP / ID switch をまとめた tracking accuracy | 参考値としては有用だが、ID 維持の質は十分に表さない | citeturn33view1 |
| **IDF1** | MTMC / MOT | ID 一致を重視した F1 | **worker ID を保てているか**の主要指標 | citeturn20search0turn33view1 |
| **HOTA** | MOT | detection・association・localization をバランスよく評価 | **本テーマの tracking 主指標として最も適切**。MOTA より association を見やすい | citeturn19search0turn19search1turn33view1 |
| **frame mAP@IoU 0.5** | AVA 型 action detection | key frame 上で person box と action label の同時正解率 | per-person action labeling の基礎評価に使える | citeturn32view0turn39view5 |
| **video/tube mAP** | spatio-temporal action detection | tubelet と action の時空間整合性 | 短い作業区間の person-centric 評価に有効 | citeturn26view12turn24view8 |
| **mAP over tIoU thresholds** | temporal action localization | 区間の開始・終了境界をどれだけ合せられるか | 作業区間単位の認識に最も自然。ActionFormer は THUMOS14 / ActivityNet でこの形式を採用 | citeturn39view0turn39view2turn15search1 |
| **Action mAP / G-Act mAP** | JRDB-Act | individual action と group activity の AP | multi-person scene での action を見る補助指標として有用 | citeturn27view5turn28view1 |

修士研究として現実的な評価設計は、**三層の分離評価**です。  
第一に **trajectory quality** として HOTA を主指標、IDF1 を副指標に置きます。第二に **per-ID action labeling** として、matched track 上で frame-level AP または mAP を取ります。第三に **work-segment evaluation** として、ピッキング・棚入れ・検品などの区間に対して tIoU ベースの interval AP を報告します。さらに、tracking 誤差と action 誤差を切り分けるために、**GT tracks 上での action 性能**と**predicted tracks 上での action 性能**を両方報告すると、研究として非常に見通しが良くなります。これは既存 benchmark の単純流用ではなく、HOTA と AVA/TAL の評価思想を合わせた**研究設計上の提案**です。citeturn19search0turn20search0turn32view0turn39view0turn27view5

もう一つ重要なのは、**split の切り方**です。TrackTacular は WILDTRACK や MultiviewX のような既存 multiview pedestrian datasets が **one-scene で train/test が overfit しやすい**ことを明示的に問題視しています。したがって、倉庫研究では **camera split**, **zone split**, **layout split**, 可能なら **site split** を取る方が、学術的価値は高いです。citeturn18search0turn18search9

## 現状で可能なことと残る壁

### できること

追跡については、**人物検出 + online MOT** の組合せで、固定カメラの複数人物 tracking 自体はかなり高い水準まで実現できます。ByteTrack や BoT-SORT は MOT17/MOT20 で強い成績を示し、OC-SORT は occlusion と非線形 motion に対する robustness と実時間性を両立しています。したがって、**歩行・停止・移動方向・滞留・基本的な搬送移動**のような coarse behavior を追跡する基盤は、既存技術の組合せで十分に構築可能です。citeturn24view2turn40view4turn40view5

複数カメラについても、**BEV への lift と camera calibration を使った multiview pedestrian tracking** はかなり前進しています。WILDTRACK は calibrated static multi-camera データを提供しており、TrackTacular や MVTrajecter は BEV 空間で detection/tracking を行う設計により、遮蔽や miss detection に対する改善を目指しています。したがって、**高所固定カメラが複数ある環境で worker の world-coordinate trajectory を得る**こと自体は、研究として十分射程に入っています。citeturn25view8turn18search9turn18search10

行動認識についても、**人の大きな運動に依存するラベル**は比較的扱いやすいです。LART は tracking + 3D pose を使う trajectory-centric action recognition を提案し、AVA 上で **person movement** に強い性能を示しました。PoseC3D も pose estimation noise への robustness と multi-person 対応のしやすさを報告しており、俯瞰視点で appearance が弱い場合の有力候補です。つまり、**walking / standing / sitting / moving / idle** のような運動主体ラベルは、track + pose 系でかなり見込めます。citeturn41view4turn41view2turn12search0

少量ラベルの観点でも、希望はあります。VideoMAE は小規模データでも有効な self-supervised pretraining を示し、semi-supervised video action detection や timestamp-supervised action segmentation の研究も進んでいます。したがって、**ゼロから大量ラベルを作る**以外にも、**自己教師あり pretraining、疎な時刻ラベル、weak labels、擬似ラベル**を土台にした研究設計は十分に現実的です。citeturn39view3turn38search3turn14search13turn14search0turn10search3

### まだ難しいこと

本テーマで本当に難しいのは、**fine-grained work semantics** です。LART の結果は、3D pose が person movement には強い一方で、object manipulation を含む全体の action 認識とはギャップがあることを示しています。AVA 自体も、開閉や pick up / put down のような fine-grained な action には短い temporal context が必要だと述べています。倉庫作業の **検品・ピッキング・仕分け・棚入れ**は、まさに **手先・対象物・棚状態**を見ないと区別しにくいため、**人物だけを見るモデルでは足りない**可能性が高いです。citeturn41view4turn32view0turn25view6turn8search3

次に難しいのは、**ID 維持と action labeling の同時最適化**です。tracking 側は人物 box と identity の整合に、action 側は動作・文脈・物体の解釈に最適化されており、benchmark も分かれています。TrackFormer のような end-to-end tracker でも、論文中で **large movement を伴う長期 occlusion には弱い**ことが述べられていますし、TubeR や STAR のような tubelet action detector は短〜中尺の tube を出すものの、**施設全体で数分〜数十分の worker identity continuity**をベンチマークしているわけではありません。つまり、**joint model を作れば自動的に全部解ける段階ではない**です。citeturn40view6turn26view12turn24view8

さらに、**似た外観・交差・遮蔽**は依然として tracking の急所です。DanceTrack は、近年の MOT が appearance matching に偏りすぎていることを批判的に示し、**uniform appearance + diverse motion** 条件で performance が大きく落ちることを示しました。倉庫や工場で似た作業服を着る worker 群は、まさにこの設定に似ています。ここでは detection はそこまでボトルネックではなく、**association** が難所になります。citeturn36view0turn36view1

また、**俯瞰特有の ReID** は標準 person ReID より未成熟です。TransReID のような一般 ReID は強力ですが、overhead/top-view 側の研究は RGB-D や depth/intensity を使うものが多く、これは ceiling RGB カメラだけで運用したい物流現場とはやや前提が異なります。したがって、**front/side-view ReID をそのまま ceiling-view に持ち込む**のは危険です。citeturn40view7turn16search1turn16search12

最後に、**産業データのスケールと多様性**が不足しています。IKEA ASM、Assembly101、HA4M、CarDA は有用ですが、多くは workstation centered, procedural, small-to-medium scale で、**多人数が同時に動き、交差し、時々見切れ、工程間を移動する**物流倉庫の floor-level complexity とは一致しません。公開研究で exact match に近いのは MERL Shopping や RetailAction ですが、前者は小規模、後者は登場したばかりです。ここが未解決課題の温床です。citeturn25view0turn25view2turn25view5turn25view4turn25view6turn8search3

## 修士研究として有望なギャップ

以下では、質問された論点に直接答えます。回答は、上の文献群を総合した**研究判断**です。

| 問い | 判断 | 根拠 |
|---|---|---|
| **「俯瞰映像から複数人物のIDと行動を認識する」ことは、既存技術の組み合わせでどこまで可能か？** | **coarse behavior まではかなり可能**。単一カメラなら detector + ByteTrack/BoT-SORT/OC-SORT、複数カメラなら BEV tracking を使い、その上に pose/RGB-based action head を載せれば、歩行・停止・搬送移動・滞留・一部の棚前作業は狙える | Tracking は成熟し、trajectory-centric action modeling も有望。だが fine-grained work semantics と long-term identity continuity は未統合 citeturn24view2turn40view4turn40view5turn18search9turn18search10turn41view4 |
| **既存手法をそのまま物流倉庫に適用したときの限界は何か？** | **似た作業服・遮蔽・退出再入場・俯瞰での手元不可視・棚/箱の object state 不可視・ラベル不足**が主限界 | DanceTrack は similar appearance と complex motion を難所として示し、top-view ReID は depth 依存が多い。pose 系は movement に強いが object manipulation には限界 | citeturn36view0turn36view1turn16search1turn16search12turn41view2turn32view0 |
| **新規性を出すなら、どこに置くべきか？** | tracker 自体より、**track-aware action segmentation**, **multi-camera BEV + action**, **object-aware top-view work recognition**, **low-label learning**, **domain generalization** に置く方が自然 | tracking 単体も action 単体も benchmark は成熟しつつあるが、両者の統合と industrial transfer は未成熟 | citeturn24view2turn26view12turn24view8turn25view4turn25view6turn18search9 |
| **少ないアノテーションコストという観点で、どの課題が研究として有望か？** | **self-supervised pretraining + sparse temporal labels + pseudo labels on tracks** が有望。特に「ID 付き軌跡」に対して、弱い action labels を付ける研究は筋が良い | VideoMAE、semi-supervised VAD、timestamp supervision、weakly supervised TAL が下地になる | citeturn39view3turn38search3turn14search13turn14search0turn10search3 |
| **IMUベースの自己教師あり作業認識研究と接続するなら、どのような位置づけが自然か？** | **IMU は時系列境界と個体内モーション、映像はID・位置・相互作用・物体文脈**を与えるので、cross-modal teacher-student / contrastive alignment / pseudo-label transfer が自然 | manufacturing では camera+EMG 等の sensor fusion 研究があり、assembly 側でも self-/semi-supervised recognition が出ている | citeturn9search6turn25view5turn14search9turn38search3 |

上の表を研究課題に落とし込むと、**「tracking はできる」「action もできる」「だが倉庫・工場の俯瞰固定カメラで worker-centric に integrate するところが弱い」**というのが全体像です。ここで重要なのは、**新規性を “全部を一度に解く巨大 end-to-end モデル” に置かなくてもよい**ことです。むしろ、**どの誤差をどこで潰すか**を明確にした方が、修士研究としては強いです。citeturn24view2turn26view12turn41view4turn25view4

最後に、修士研究として成立しそうな Research Question を提案します。

| Research Question | 研究の核 | 少量ラベル性 | IMU との接続 | 実験設計の現実性 |
|---|---|---|---|---|
| **Trajectory-centric weakly supervised work recognition from ceiling cameras** | detector+tracker で得た worker 軌跡に対し、疎な時刻ラベルや video-level ラベルだけで作業区間を推定する | 高い。timestamp supervision や weak TAL を流用できる | IMU から action boundary の pseudo labels を与えやすい | 公開 action benchmark で予備実験し、自前倉庫データへ転移しやすい citeturn14search0turn10search3turn39view3 |
| **Multi-camera BEV worker tracking with zone- and object-aware action labeling** | BEV tracking に棚・作業台・搬送エリアなどの zone prior を加えて、per-ID action を安定化する | 中程度。 zone annotation は比較的安い | IMU は zone 内の micro-action を補える | WILDTRACK/TrackTacular 系で tracking、Retail/warehouse 自前データで action を足す設計が可能 citeturn25view8turn18search9turn18search10turn25view6 |
| **Object-aware top-view work recognition beyond pose** | pose だけでなく、棚・箱・台車・工具・商品の state change を joint に見ることで picking / sorting / inspection / shelving を分離する | 中程度。 object state は sparse annotation でも始められる | IMU は手元モーション、映像は object state を担当 | pose-only の限界が既に示されており、研究動機が立てやすい citeturn41view2turn32view0turn25view6turn8search3 |
| **Cross-modal self-supervised worker representation learning from video and IMU** | 同一 worker の IMU と video track を対比学習し、少ラベルで作業識別を行う | 非常に高い。自己教師ありが主戦場 | 中心テーマそのもの | industrial sensor fusion と self-supervised video の両文脈に自然に乗る citeturn9search6turn25view5turn39view3 |
| **Cross-layout and cross-camera generalization for industrial worker analytics** | 倉庫 A で学習して倉庫 B にどこまで通るかを、camera / layout split で測る | 中程度。ラベル転用より generalization 研究 | IMU を target-site adaptation の weak teacher にできる | one-scene benchmark の限界を突くので、学術的な価値が高い | citeturn18search0turn18search9turn25view4 |

私見を明確に述べると、**最も筋が良い修士テーマは**次のどちらかです。  
ひとつは、**「track-aware weakly supervised work recognition」**です。これは既存 tracker を活かしながら、action 側に新規性を置けるため、実装・評価・論文化のバランスが良いです。もうひとつは、**「video-IMU cross-modal self-supervision」**です。これはあなたが言及した IMU ベース研究と自然に接続でき、さらに公開データ不足という産業映像研究の最重要課題にも真正面から応えられます。前者は vision 側の論文として、後者は multimodal industrial sensing として位置づけやすいです。citeturn39view3turn38search3turn14search0turn9search6

総合すると、修士研究の主張として最も説得力があるのは、**「既存技術の単純な組合せで coarse worker analytics は可能だが、俯瞰固定カメラ下の fine-grained 作業認識は、trajectory・object context・weak/self-supervision・cross-modal cues を使わないと実環境では破綻しやすい」**という立て方です。この主張は、benchmarks の分断、industrial datasets の不足、tracking と action の評価軸の分離、そして recent low-label learning の進展のすべてと整合しています。citeturn35view0turn36view0turn32view0turn27view9turn25view4turn25view6turn39view3turn38search3