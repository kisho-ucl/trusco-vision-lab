# Tracking Viewer

トラッキング結果をバウンディングボックス・軌跡付きで動画に書き出すビジュアライゼーションツール。

## スクリプト一覧

| スクリプト | 用途 |
|-----------|------|
| `make_tracking_resultmovie.py` | **メイン**。SCMOTモード（カメラ別）またはGlobalモード（stitchパノラマ）で可視化動画を生成 |
| `export_overlay.py` | デバッグ用。ハードコードされたパスで素早くオーバーレイ確認 |

---

## make_tracking_resultmovie.py

### モード

| モード | 入力 | bboxフォーマット |
|--------|------|----------------|
| `global` | グローバルtracking JSON + stitchパノラマ動画 | TLWH + offset補正 |
| `scmot` | per-camera JSON（ディレクトリ or 単ファイル）+ 各カメラ動画 | CXCYWH（カメラ座標） |

### 実行コマンド

**Global モード（stitchパノラマ動画に重ねる）：**

```bash
python tools/tracking_viewer/make_tracking_resultmovie.py global \
    --json_file  dataset_readonly/fastops/result/77/track/modified_kalman_dtw2_adjusted_tracking_result.json \
    --video_file /mnt/gazania/trusco-stitch/2024/2024-10-03/new_overlap_0900_1100_2x_nkawa1934.mp4 \
    --output_file output/tracking_global_77.mp4 \
    --offset_x 3885.36 \
    --offset_y 812.703
```

**SCMOTモード（カメラ別、ディレクトリ一括）：**

```bash
python tools/tracking_viewer/make_tracking_resultmovie.py scmot \
    --json_path  path/to/per_cam_json/ \
    --video_root /mnt/bigdata/.../movie/20241003 \
    --output_root output/scmot_movies/ \
    --video_pattern "{cam}_2024-10-03_39600_41400.mp4"
```

**SCMOTモード（単一カメラ）：**

```bash
python tools/tracking_viewer/make_tracking_resultmovie.py scmot \
    --json_path  path/to/per_cam_json/A4.json \
    --video_root /mnt/bigdata/.../movie/20241003 \
    --output_root output/scmot_movies/
```

### 引数

**global モード：**

| 引数 | 説明 |
|------|------|
| `--json_file` | グローバルtracking JSONファイル |
| `--video_file` | 入力動画（stitch） |
| `--output_file` | 出力 `.mp4` パス |
| `--offset_x` | bbox X オフセット（デフォルト: 3885.36） |
| `--offset_y` | bbox Y オフセット（デフォルト: 812.703） |

**scmot モード：**

| 引数 | 説明 |
|------|------|
| `--json_path` | per-camera JSONファイル or ディレクトリ |
| `--video_root` | 各カメラ動画のルートディレクトリ（`cameraXX/` の親） |
| `--output_root` | 出力先ディレクトリ |
| `--video_pattern` | 動画ファイル名パターン（`{cam}` がカメラIDに置換される） |

---

## export_overlay.py

デバッグ用スクリプト。パスはファイル先頭にハードコード。

```python
VIDEO      = "/mnt/gazania/trusco-stitch/2024/..."
JSON_TRACK = "dataset_readonly/fastops/result/77/track/..."
OUT_MP4    = "task_annotation_clips/overlay_77_debug.mp4"
START_FID  = 0
END_FID    = 100  # 最初の100フレームのみ
```

パスを編集してから実行：

```bash
python tools/tracking_viewer/export_overlay.py
```

タスクJSONも重ねたい場合は `JSON_TASK` にパスを指定（`None` の場合はスキップ）。

---

## 出力動画の特徴

- 各トラックにランダムカラーのバウンディングボックスと軌跡ライン
- track ID をボックス上部に表示
- フレーム番号を右上に表示
- タスクラベルが付いている場合はラベル名をボックス下部に表示
