# Dataset Generation

トラッキングJSONと非歪み補正済み動画から、人物ごとのクロップ画像シーケンスを生成する。

## スクリプト一覧

| スクリプト | 用途 |
|-----------|------|
| `extract_clips.py` | **メイン**。`dataset_mapping.json` の設定を使い `manifest.json` + クリップ画像を生成 |
| `generate_clips.py` | 旧スクリプト。Market-1501形式で出力（パスを直接引数指定） |

---

## extract_clips.py（推奨）

### 前提

- `tools/annotation/config/dataset_mapping.json` に対象 `result_id` のエントリがあること
- トラッキングJSON・タイムスタンプキャッシュ（`.pkl`）・非歪み補正動画へのアクセスがあること

### 実行コマンド

```bash
# trusco-vision-lab/ から実行
# 通常実行（result_id=77, 5フレームに1枚）
python tools/dataset_generation/extract_clips.py --result_id 77

# フレームサンプリング間隔を変更（デフォルト: 5 = 1fps）
python tools/dataset_generation/extract_clips.py --result_id 77 --use_frame 5

# デバッグ用（最初の10トラックのみ）
python tools/dataset_generation/extract_clips.py --result_id 77 --limit_tracks 10

# フレーム数が少ないクリップの除外閾値（デフォルト: 5）
python tools/dataset_generation/extract_clips.py --result_id 77 --min_frames 5
```

仮想環境を使う場合：

```bash
/home/kisho_ucl/.pyenv/versions/.venv_trusco-vision/bin/python \
    tools/dataset_generation/extract_clips.py --result_id 77
```

長時間ジョブは tmux 上で実行推奨：

```bash
tmux new -s extract
python tools/dataset_generation/extract_clips.py --result_id 77
# Ctrl-b d でデタッチ
```

### 引数

| 引数 | デフォルト | 説明 |
|------|-----------|------|
| `--result_id` | （必須） | 処理対象のresult ID（例: `77`） |
| `--use_frame` | `5` | トラッキングJSONを何フレームおきにサンプリングするか |
| `--min_frames` | `5` | 保存フレーム数がこれ未満のクリップは除外 |
| `--limit_tracks` | `None` | デバッグ用。処理トラック数の上限 |
| `--mapping_config` | `tools/annotation/config/dataset_mapping.json` | 設定ファイルパス |
| `--output_base` | `task_annotation_clips` | 出力ルートディレクトリ |

### 出力

```
task_annotation_clips/
└── {result_id}/
    ├── manifest.json              # クリップ一覧 + 軌跡データ
    └── clips/
        ├── track_{id}/            # カメラをまたいだ1人分の連続クリップ
        │   ├── 000001.jpg
        │   ├── 000002.jpg
        │   └── ...
        └── ...
```

> **注意**: 以前は `track_{id}_{cam}` でカメラ単位に分割していたが、1人が複数カメラにまたがって  
> 存在する場合にクリップが分断されてしまう問題を修正し、`track_{id}` 単位（人単位）に統合した。  
> フレームごとに最適カメラ（`src_cam_duplicate_list[0]`）から切り出す。

**manifest.json の主要フィールド：**

```json
{
  "version": 1,
  "labels": ["Inspect", "Sort", "Transport", "Other", "Unclear"],
  "clips": [
    {
      "clip_id": "77_track_3",
      "person_id": "track-3",
      "cameras": ["A4", "A2"],     // 使用カメラ一覧（フレームをまたいで変わる場合あり）
      "start_time": "2024-10-03T09:00:...",
      "duration_sec": 12.4,
      "frame_count": 62,
      "trajectory": [[cx, cy], ...],   // フロアプラン座標（px）
      ...
    }
  ]
}
```

### フロアプラン座標の変換

`trajectory` の座標は以下の変換で計算される：

```
cx = bbox[0] - offset_x + bbox[2] / 2   # TLWH → 中心x
cy = bbox[1] - offset_y + bbox[3] / 2   # TLWH → 中心y
```

`offset_x`, `offset_y` は `dataset_mapping.json` で設定（デフォルト: 3885.36, 812.703）。  
倉庫フロアプラン（3932×2312px）の座標系に対応。

---

## generate_clips.py（旧）

Market-1501形式でのクロップ画像生成。パスをすべて引数で指定する旧バージョン。

```bash
python tools/dataset_generation/generate_clips.py \
    --track_json path/to/tracking.json \
    --output_dir path/to/output/ \
    --start_time "11:00:00" \
    --use_frame 5
```

> **注意**: このスクリプトは `orig_frame = json_frame_id * 2 + 1` というステッチ動画前提の計算をしている（`extract_clips.py` では修正済み）。
