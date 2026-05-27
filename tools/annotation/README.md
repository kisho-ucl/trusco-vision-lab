# Annotation Tool

倉庫作業者クリップに対してアクティビティラベルを付けるWebアノテーションツール。

## 概要

- Flaskサーバ + ブラウザUI（HTML/CSS/JS）
- クリップ単位でフレームをめくりながら作業区間を分割 → ラベル付け
- フロアプラン上の軌跡表示・サムネイルストリップ・セグメントバー付き

## 前提

`extract_clips.py` で生成した以下のディレクトリが存在すること：

```
task_annotation_clips/
└── {result_id}/
    ├── manifest.json
    └── clips/
        ├── track_1/           # カメラをまたいだ1人分の連続クリップ
        │   ├── 000001.jpg
        │   └── ...
        └── ...
```

## 実行コマンド

```bash
# trusco-vision-lab/ から実行
python tools/annotation/server.py --result_id 77

# ポート指定（デフォルト: 8080）
python tools/annotation/server.py --result_id 77 --port 8888
```

起動後 → ブラウザで `http://localhost:8080/` を開く

## キーボードショートカット

| キー | 操作 |
|------|------|
| `←` / `→` | フレーム移動 |
| `1` 〜 `5` | 選択セグメントにラベル付け |
| `E` | Exception サブパネルを開閉 |
| `B` | 現在フレームに境界を追加 |
| `Escape` | セグメント選択解除 / ライトボックスを閉じる |

## ラベル一覧

**通常ラベル（セグメント単位）**

| # | ラベル | 意味 |
|---|--------|------|
| 1 | Inspect | 検品・確認作業 |
| 2 | Sort | 仕分け |
| 3 | Transport | 搬送・移動 |
| 4 | Other | その他作業 |
| 5 | Unclear | 判断困難 |

**Exceptionラベル（`E`キー → サブパネル）**

| ラベル | 意味 |
|--------|------|
| No Person | 人が写っていない・誤検出 |
| Tracking Lost | トラッキングが途中で途切れている |
| ID Switch | 別の人物にIDが切り替わっている |
| Exception | その他の例外（Noteに詳細を記載） |

## 出力

### annotations.jsonl（サーバ側・自動保存）

```
task_annotation_clips/{result_id}/annotations.jsonl
```

クリップ間を移動するたびに自動保存される。1行1クリップのJSONL形式。

### フォーマット

```json
{
  "clip_id": "77_track_3",
  "person_id": 5,
  "work_segments": [
    {
      "start_frame": 1,
      "end_frame": 30,
      "label": "Inspect",
      "note": ""
    },
    {
      "start_frame": 31,
      "end_frame": 62,
      "label": "Transport",
      "note": "カートを使用"
    }
  ],
  "annotated_at": "2024-10-03T12:34:56+00:00"
}
```

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `clip_id` | string | `{result_id}_track_{track_id}` |
| `person_id` | int \| null | アノテータが付けた実際の人物ID（0–38）。未設定時は `null` |
| `work_segments` | array | 作業区間のリスト（1-based フレーム番号） |
| `work_segments[].start_frame` | int | 区間開始フレーム（1始まり） |
| `work_segments[].end_frame` | int | 区間終了フレーム（1始まり、含む） |
| `work_segments[].label` | string \| null | ラベル名。未設定時は `null` |
| `work_segments[].note` | string | 自由記述メモ |
| `annotated_at` | string | 保存時刻（ISO 8601 UTC） |

> **注意**: manifest.json の各クリップにも `person_id: "track-3"` というフィールドがあるが、
> これはトラッキングIDベースの文字列であり、annotation の `person_id`（実際の人物ID・整数）とは別物。

### Export JSONL

「Export JSONL」ボタンで現在の全アノテーションをブラウザからダウンロードできる（現クリップも自動保存してから出力）。

### Import

過去にExportしたJSONLファイルを「Import」ボタンで読み込むと作業を再開できる。  
※ 同じ `--result_id` でサーバを再起動した場合は `annotations.jsonl` が自動で読み込まれるため、通常は Import 不要。

## ファイル構成

```
annotation/
├── server.py              # Flaskサーバ
├── config/
│   └── dataset_mapping.json  # result_id → 各種パスのマッピング
└── static/
    ├── index.html
    ├── styles.css
    ├── app.js
    ├── warehouse.png      # フロアプラン画像（3932×2312px）
    └── bibs.png           # ビブス番号 → 人物ID 対応表
```
