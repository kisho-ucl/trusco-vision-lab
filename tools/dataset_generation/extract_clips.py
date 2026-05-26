#!/usr/bin/env python3
import os
import cv2
import json
import argparse
import pickle
from glob import glob
from datetime import datetime, timedelta, timezone
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract per-track person crops from tracking JSON and generate manifest.json"
    )
    parser.add_argument("--result_id", type=str, required=True,
                        help="Result ID (e.g. 77)")
    parser.add_argument("--use_frame", type=int, default=5,
                        help="Sample every N tracking frames (default: 5 = 1fps)")
    parser.add_argument("--limit_tracks", type=int, default=None,
                        help="Limit number of tracks for debug runs")
    parser.add_argument("--min_frames", type=int, default=5,
                        help="Skip tracks with fewer than N saved frames (default: 5)")
    parser.add_argument("--mapping_config", type=str,
                        default="tools/annotation/config/dataset_mapping.json")
    parser.add_argument("--output_base", type=str, default="task_annotation_clips")
    return parser.parse_args()


def load_config(config_path, result_id):
    with open(config_path) as f:
        config = json.load(f)
    if result_id not in config:
        raise ValueError(f"Result ID '{result_id}' not found in {config_path}")
    return config[result_id]


def load_ts_cache(path):
    with open(path, "rb") as f:
        return pickle.load(f)


# Video capture cache: (cam, vid_idx) → {"cap": VideoCapture, "last_frm": int}
_caps = {}


def get_frame(cam, orig_frame, ts_cache, start_time_sec, undis_dir):
    cur_in_sec = start_time_sec + orig_frame * 0.2
    ts_list = ts_cache[0].get(cam)
    if ts_list is None:
        return None
    cam_offset = ts_cache[1].get(cam, 0)
    idx = int(5 * (cur_in_sec - cam_offset))
    if idx < 0 or idx >= len(ts_list):
        return None
    vid_idx, frm_idx = ts_list[idx]

    key = (cam, vid_idx)
    if key not in _caps:
        # release any old capture for this camera
        for k in [k for k in _caps if k[0] == cam]:
            _caps[k]["cap"].release()
            del _caps[k]
        vid_pattern = os.path.join(undis_dir, f"camera{cam}", f"video_??-??-??_{vid_idx:02d}.mp4")
        matches = glob(vid_pattern)
        if not matches:
            return None
        _caps[key] = {"cap": cv2.VideoCapture(matches[0]), "last_frm": -1}

    cap_info = _caps[key]
    cap = cap_info["cap"]

    # seek only when not sequential
    if cap_info["last_frm"] + 1 != frm_idx:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frm_idx)

    ret, frame = cap.read()
    if not ret:
        # retry once with explicit seek
        cap.set(cv2.CAP_PROP_POS_FRAMES, frm_idx)
        ret, frame = cap.read()
    if not ret:
        return None

    cap_info["last_frm"] = frm_idx
    return frame


def crop_person(frame, bbox):
    """bbox is (cx, cy, w, h) in local camera coordinates."""
    cx, cy, w, h = map(float, bbox)
    h_img, w_img = frame.shape[:2]
    x1 = max(0, int(round(cx - w / 2)))
    y1 = max(0, int(round(cy - h / 2)))
    x2 = min(w_img, int(round(cx + w / 2)))
    y2 = min(h_img, int(round(cy + h / 2)))
    if x2 <= x1 or y2 <= y1:
        return None
    return frame[y1:y2, x1:x2]


def release_all():
    for cap_info in _caps.values():
        cap_info["cap"].release()
    _caps.clear()


def main():
    args = parse_args()
    config = load_config(args.mapping_config, args.result_id)

    date = config["date"]
    start_time = config["start_time"]
    undis_dir = config["undis_dir"]
    track_json_path = config["track_json"]

    ts_cache = load_ts_cache(config["ts_cache_file"])
    start_time_sec = int(
        (datetime.strptime(start_time, "%H:%M:%S") - datetime(1900, 1, 1)).total_seconds()
    )

    print(f"Loading: {track_json_path}")
    with open(track_json_path) as f:
        tracking_data = json.load(f)
    print(f"Frames in JSON: {len(tracking_data)}")

    # Collect sampled frames per (track_id, cam)
    clips_data = {}
    for frame in tracking_data:
        json_frame_id = frame.get("frame_id")
        if json_frame_id is None or json_frame_id % args.use_frame != 0:
            continue
        for track in frame.get("tracks", []):
            track_id = str(track.get("track_id", ""))
            if not track_id:
                continue

            dup_cams = track.get("src_cam_duplicate_list", [])
            dup_bboxes = track.get("bbox_list", [])
            if dup_cams and dup_bboxes:
                cam = dup_cams[0]
                bbox = dup_bboxes[0]
            else:
                cam = track.get("src_cam", "unknown")
                bbox = track.get("original_bbox")
                if bbox is None:
                    continue

            clips_data.setdefault((track_id, cam), []).append((json_frame_id, bbox))

    sorted_keys = sorted(
        clips_data.keys(),
        key=lambda x: (int(x[0]) if x[0].isdigit() else x[0], x[1])
    )
    if args.limit_tracks is not None:
        sorted_keys = sorted_keys[:args.limit_tracks]
        print(f"Debug: limiting to {args.limit_tracks} tracks (of {len(clips_data)} total)")

    output_dir = os.path.join(args.output_base, args.result_id)
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)

    tz_jst = timezone(timedelta(hours=9))
    base_dt = datetime.strptime(
        f"{date} {start_time}", "%Y-%m-%d %H:%M:%S"
    ).replace(tzinfo=tz_jst)

    manifest_clips = []
    total_saved = 0

    for track_id, cam in tqdm(sorted_keys, desc="Tracks"):
        frame_list = clips_data[(track_id, cam)]
        clip_folder = f"track_{track_id}_{cam}"
        clip_dir = os.path.join(clips_dir, clip_folder)
        os.makedirs(clip_dir, exist_ok=True)

        saved_indices = []
        for seq_idx, (json_frame_id, bbox) in enumerate(frame_list, start=1):
            orig_frame = json_frame_id
            frame_img = get_frame(cam, orig_frame, ts_cache, start_time_sec, undis_dir)
            if frame_img is None:
                continue
            crop = crop_person(frame_img, bbox)
            if crop is None:
                continue
            cv2.imwrite(os.path.join(clip_dir, f"{seq_idx:06d}.jpg"), crop)
            saved_indices.append(orig_frame)

        if len(saved_indices) < args.min_frames:
            # remove the directory if it was created but has too few frames
            for f in os.listdir(clip_dir):
                os.remove(os.path.join(clip_dir, f))
            os.rmdir(clip_dir)
            continue

        start_orig, end_orig = saved_indices[0], saved_indices[-1]
        manifest_clips.append({
            "clip_id": f"{args.result_id}_track_{track_id}_{cam}",
            "batch_id": args.result_id,
            "person_id": f"track-{track_id}",
            "original_tracking_id": track_id,
            "camera_id": cam,
            "start_time": (base_dt + timedelta(seconds=start_orig * 0.2)).isoformat(),
            "end_time":   (base_dt + timedelta(seconds=end_orig   * 0.2)).isoformat(),
            "duration_sec": round((end_orig - start_orig) * 0.2, 2),
            "image_folder": f"clips/{clip_folder}",
            "frame_count": len(saved_indices),
            "frame_indices": saved_indices,
            "zone_hint": "unknown",
        })
        total_saved += len(saved_indices)

    manifest = {
        "version": 1,
        "labels": ["Inspect", "Sort", "Transport", "Other", "Unclear"],
        "clips": manifest_clips,
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    release_all()
    print(f"\nDone: {len(manifest_clips)} clips, {total_saved} frames total")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
