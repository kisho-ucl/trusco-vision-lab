import os
import cv2
import json
import argparse
import numpy as np
import pickle
from glob import glob
from datetime import datetime, timezone, timedelta
from tqdm import tqdm

BASE_X = 3885.356
BASE_Y = 812.703

# Video Capture Cache
caps = {}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract sequential JPG crops from tracking JSON and create manifest.json"
    )
    parser.add_argument("--result_id", type=str, required=True, help="Tracking Result ID (e.g. 78)")
    parser.add_argument("--use_frame", type=int, default=5, help="Frame sampling interval")
    parser.add_argument("--limit_tracks", type=int, default=None, help="Limit number of tracks to process for testing")
    parser.add_argument("--mapping_config", type=str, default="tools/annotation/config/dataset_mapping.json",
                        help="Path to mapping config JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug logs")
    return parser.parse_args()

def load_config(config_path, result_id):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Mapping config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    if result_id not in config:
        raise ValueError(f"Result ID {result_id} not found in config {config_path}")
    return config[result_id]

def load_ts_cache(ts_cache_path):
    if not os.path.exists(ts_cache_path):
        raise FileNotFoundError(f"Timestamp cache file not found: {ts_cache_path}")
    with open(ts_cache_path, "rb") as f:
        return pickle.load(f)

def get_frame(cam, vid_idx, frm_idx, date, undis_dir, debug=False):
    global caps
    cache_key = cam
    
    # Release previous capture if the video index changes
    if cache_key in caps and caps[cache_key]["vid_idx"] != vid_idx:
        caps[cache_key]["cap"].release()
        del caps[cache_key]
        
    if cache_key not in caps:
        # Find video matching the pattern
        vid_pattern = os.path.join(undis_dir, f"camera{cam}", f"video_??-??-??_{vid_idx:02d}.mp4")
        vid_files = glob(vid_pattern)
        if not vid_files:
            if debug:
                print(f"[Warning] Video not found: {vid_pattern}")
            return None
        video_file = vid_files[0]
        cap = cv2.VideoCapture(video_file)
        caps[cache_key] = {
            "cap": cap,
            "vid_idx": vid_idx,
            "cur_frm": -1
        }
        
    cap_info = caps[cache_key]
    cap = cap_info["cap"]
    
    # Seek frame if not sequential
    current_pos = cap_info["cur_frm"]
    if current_pos != frm_idx:
        if current_pos + 1 != frm_idx:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frm_idx)
            
    ret, frame_img = cap.read()
    if ret:
        cap_info["cur_frm"] = frm_idx + 1
        return frame_img
    else:
        # Retry once by setting position explicitly
        if debug:
            print(f"[Warning] Seek read failed, retrying camera {cam} frame {frm_idx}")
        cap.set(cv2.CAP_PROP_POS_FRAMES, frm_idx)
        ret, frame_img = cap.read()
        if ret:
            cap_info["cur_frm"] = frm_idx + 1
            return frame_img
        return None

def crop_and_save(frame_img, bbox, output_path):
    h_img, w_img = frame_img.shape[:2]
    cx, cy, w, h = bbox
    
    x1 = int(round(cx - w / 2))
    y1 = int(round(cy - h / 2))
    x2 = int(round(cx + w / 2))
    y2 = int(round(cy + h / 2))
    
    # Bound check
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w_img, x2)
    y2 = min(h_img, y2)
    
    if x2 <= x1 or y2 <= y1:
        return False
        
    crop = frame_img[y1:y2, x1:x2]
    cv2.imwrite(output_path, crop)
    return True

def main():
    args = parse_args()
    debug = args.debug
    result_id = args.result_id
    use_frame = args.use_frame
    limit_tracks = args.limit_tracks
    
    # Load configuration
    try:
        config = load_config(args.mapping_config, result_id)
    except Exception as e:
        print(f"[Error] Failed to load config: {e}")
        return
        
    date = config["date"]
    start_time = config["start_time"]
    ts_cache_file = config["ts_cache_file"]
    undis_dir = config["undis_dir"]
    track_json_path = config["track_json"]
    
    output_dir = f"task_annotation_clips/{result_id}"
    
    # Load timestamp cache
    try:
        ts_cache = load_ts_cache(ts_cache_file)
    except Exception as e:
        print(f"[Error] Failed to load ts_cache: {e}")
        return
        
    # Parse start time to seconds
    start_time_dt = datetime.strptime(start_time, "%H:%M:%S")
    start_time_sec = int((start_time_dt - datetime(1900, 1, 1)).total_seconds())
    
    # Load tracking result JSON
    if not os.path.exists(track_json_path):
        print(f"[Error] Tracking result JSON not found: {track_json_path}")
        return
        
    print(f"Loading tracking result: {track_json_path}")
    with open(track_json_path, "r", encoding="utf-8") as f:
        tracking_data = json.load(f)
        
    # Group tracking frames by (track_id, camera)
    # clips_data = { (track_id, cam): [ (json_frame_id, bbox), ... ] }
    clips_data = {}
    
    for frame in tracking_data:
        json_frame_id = frame.get("frame_id")
        if json_frame_id is None:
            continue
            
        for track in frame.get("tracks", []):
            subj_id = track.get("subj_id")
            if subj_id is None or str(subj_id) == "None":
                subj_id = track.get("track_id")
            if subj_id is None:
                continue
                
            track_id = str(subj_id)
            
            # Identify Camera
            dup_cams = track.get("src_cam_duplicate_list", [])
            if dup_cams and len(dup_cams) > 0:
                cam = dup_cams[0]
            else:
                cam = track.get("src_cam", "unknown")
                
            # Identify BBox
            dup_bboxes = track.get("bbox_list", [])
            if dup_bboxes and len(dup_bboxes) > 0:
                bbox = dup_bboxes[0]
            elif "original_bbox" in track and track["original_bbox"]:
                bbox = track["original_bbox"]
            elif "bbox" in track and track["bbox"]:
                # Convert global to local coords
                g_cx, g_cy, w, h = track["bbox"]
                bbox = [g_cx - BASE_X, g_cy - BASE_Y, w, h]
            else:
                continue
                
            key = (track_id, cam)
            if key not in clips_data:
                clips_data[key] = []
            clips_data[key].append((json_frame_id, bbox))
            
    # Process clips
    sorted_keys = sorted(clips_data.keys(), key=lambda x: (int(x[0]) if x[0].isdigit() else x[0], x[1]))
    if limit_tracks is not None:
        sorted_keys = sorted_keys[:limit_tracks]
        print(f"Limiting execution to first {limit_tracks} tracks.")
        
    # Build list of crop tasks grouped by (cam, vid_idx, frm_idx)
    frames_to_process = {}
    
    for track_id, cam in sorted_keys:
        frames_list = clips_data[(track_id, cam)]
        
        # Filter frame sampling step
        sampled_frames = [item for item in frames_list if item[0] % use_frame == 0]
        if not sampled_frames:
            continue
            
        for seq_idx, (json_frame_id, bbox) in enumerate(sampled_frames, start=1):
            orig_frame = json_frame_id * 2 + 1
            
            # ts_cache lookup
            cur_in_sec = start_time_sec + (orig_frame * 0.2)
            ts_list = ts_cache[0].get(cam)
            if ts_list is None:
                continue
                
            cam_offset = ts_cache[1].get(cam, 0)
            idx = int(5 * (cur_in_sec - cam_offset))
            
            if idx < 0 or idx >= len(ts_list):
                continue
                
            vid_idx, frm_idx = ts_list[idx]
            
            key = (cam, vid_idx, frm_idx)
            if key not in frames_to_process:
                frames_to_process[key] = []
            
            frames_to_process[key].append({
                "track_id": track_id,
                "bbox": bbox,
                "seq_idx": seq_idx,
                "orig_frame": orig_frame
            })
            
    # Group by camera, then sort by (vid_idx, frm_idx)
    cams_tasks = {}
    for (cam, vid_idx, frm_idx), tasks in frames_to_process.items():
        if cam not in cams_tasks:
            cams_tasks[cam] = []
        cams_tasks[cam].append((vid_idx, frm_idx, tasks))
        
    for cam in cams_tasks:
        cams_tasks[cam].sort(key=lambda x: (x[0], x[1]))
        
    manifest_tracker = {}
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    
    # Process sequential reads camera by camera
    print(f"Processing crops sequentially for {len(cams_tasks)} cameras...")
    for cam, frame_list in cams_tasks.items():
        cap = None
        cur_vid_idx = -1
        cur_frm_idx = -1
        
        for vid_idx, frm_idx, tasks in tqdm(frame_list, desc=f"Cam {cam}"):
            # Check if we need to switch video file
            if cap is None or cur_vid_idx != vid_idx:
                if cap is not None:
                    try:
                        cap.release()
                    except Exception:
                        pass
                vid_pattern = os.path.join(undis_dir, f"camera{cam}", f"video_??-??-??_{vid_idx:02d}.mp4")
                vid_files = glob(vid_pattern)
                if not vid_files:
                    if debug:
                        print(f"[Warning] Video not found: {vid_pattern}")
                    cap = None
                    continue
                video_file = vid_files[0]
                cap = cv2.VideoCapture(video_file)
                cur_vid_idx = vid_idx
                cur_frm_idx = 0  # Initial seek position for next read is frame 0
                
            if cap is None:
                continue
                
            # Read or seek to frm_idx
            if cur_frm_idx != frm_idx:
                if cur_frm_idx == -1 or cur_frm_idx > frm_idx or frm_idx - cur_frm_idx > 10:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frm_idx)
                    cur_frm_idx = frm_idx
                else:
                    # Skip frame sequentially
                    while cur_frm_idx < frm_idx:
                        ret, _ = cap.read()
                        if not ret:
                            break
                        cur_frm_idx += 1
                        
            # Read target frame
            ret, frame_img = cap.read()
            if not ret:
                cur_frm_idx = -1  # invalidate position on failure
                continue
            cur_frm_idx += 1
            
            # Crop all bboxes for this frame
            for task in tasks:
                track_id = task["track_id"]
                clip_folder_name = f"track_{track_id}_{cam}"
                clip_save_dir = os.path.join(clips_dir, clip_folder_name)
                os.makedirs(clip_save_dir, exist_ok=True)
                filename = f"{task['seq_idx']:06d}.jpg"
                output_path = os.path.join(clip_save_dir, filename)
                
                success = crop_and_save(frame_img, task["bbox"], output_path)
                if success:
                    key = (track_id, cam)
                    if key not in manifest_tracker:
                        manifest_tracker[key] = {
                            "frame_indices": [],
                            "count": 0
                        }
                    manifest_tracker[key]["frame_indices"].append(task["orig_frame"])
                    manifest_tracker[key]["count"] += 1
                    
        # Release final camera capture
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass
                
    # Build manifest
    clips_manifest_list = []
    tz_jst = timezone(timedelta(hours=9))
    base_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz_jst)
    
    sorted_manifest_keys = sorted(manifest_tracker.keys(), key=lambda x: (int(x[0]) if x[0].isdigit() else x[0], x[1]))
    for track_id, cam in sorted_manifest_keys:
        info = manifest_tracker[(track_id, cam)]
        frame_indices = sorted(info["frame_indices"])
        saved_frames_count = info["count"]
        
        clip_folder_name = f"track_{track_id}_{cam}"
        start_orig = frame_indices[0]
        end_orig = frame_indices[-1]
        
        start_dt = base_dt + timedelta(seconds=start_orig * 0.2)
        end_dt = base_dt + timedelta(seconds=end_orig * 0.2)
        duration = (end_orig - start_orig) * 0.2
        
        clip_id = f"{result_id}_track_{track_id}_{cam}"
        
        clip_manifest = {
            "clip_id": clip_id,
            "batch_id": result_id,
            "person_id": f"track-{track_id}",
            "original_tracking_id": track_id,
            "camera_id": cam,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_sec": round(duration, 2),
            "image_folder": f"clips/{clip_folder_name}",
            "frame_count": saved_frames_count,
            "frame_indices": frame_indices,
            "zone_hint": "unknown"
        }
        clips_manifest_list.append(clip_manifest)
        
    # Write manifest.json
    manifest_data = {
        "version": 1,
        "labels": ["Inspect", "Sort", "Transport", "Other", "Unclear"],
        "clips": clips_manifest_list
    }
    
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
    print(f"\nProcessing Complete. Created {len(clips_manifest_list)} clips.")
    print(f"Manifest output file: {manifest_path}")
    
    # Release captures
    for cam_key in list(caps.keys()):
        try:
            caps[cam_key]["cap"].release()
        except Exception:
            pass

if __name__ == "__main__":
    main()
