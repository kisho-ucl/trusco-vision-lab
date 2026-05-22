# Semi-auto Annotation Prototype

Browser-only prototype for labeling worker clips.

## Use

Open `index.html` in a browser, then load `sample_manifest.json`.

The tool stores in-progress annotations in `localStorage` and exports final annotations as JSONL.

## Manifest

The UI expects a JSON file with this shape:

```json
{
  "version": 1,
  "labels": ["Inspect", "Sort", "Transport", "Other", "Unclear"],
  "clips": [
    {
      "clip_id": "sample-001",
      "worker_id": "worker-01",
      "camera_id": "cam-01",
      "start_time": "2026-05-01T10:00:00+09:00",
      "end_time": "2026-05-01T10:00:30+09:00",
      "duration_sec": 30,
      "video_url": "",
      "thumbnail_url": "",
      "zone_hint": "inspection_table",
      "track_summary": {
        "distance_m": 2.8,
        "dominant_zone": "inspection_table",
        "zone_transitions": ["aisle", "inspection_table"]
      }
    }
  ]
}
```

`video_url` and `thumbnail_url` may be empty while designing the workflow.

## Shortcuts

- `1`: Inspect
- `2`: Sort
- `3`: Transport
- `4`: Other
- `5`: Unclear
- `ArrowRight`: next clip
- `ArrowLeft`: previous clip
