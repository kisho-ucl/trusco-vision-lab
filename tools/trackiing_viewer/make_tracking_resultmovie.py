#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import random
import cv2
import numpy as np
from tqdm import tqdm
import os
import argparse
import glob

# ===== デフォルトパス =====
# SCMOT（per-cam JSON → per-cam movie）用
DEFAULT_SCMOT_JSON_PATH   = "/mnt/bigdata/00_students/ymori_ucl/trusco/multicam_tracking/for_evaluation/20241003/thesis/Master_thesis_out/new_nt_no_leg_per_cam_tracking_result_2024-10-03_39600_41400/bbox-original_bbox_skip-0_prune-0-le5/per_cam_json"
DEFAULT_SCMOT_VIDEO_ROOT  = "/mnt/bigdata/00_students/ymori_ucl/trusco/multicam_tracking/movie/20241003"
# ここは勝手に決めています：per_cam_json と同じ階層に per_cam_movie を作る想定
DEFAULT_SCMOT_OUTPUT_ROOT = "/mnt/bigdata/00_students/ymori_ucl/trusco/multicam_tracking/for_evaluation/20241003/thesis/Master_thesis_out/new_nt_no_leg_per_cam_tracking_result_2024-10-03_39600_41400/bbox-original_bbox_skip-0_prune-0-le5/per_cam_movie"

# Global（全体 JSON ＋ stitch 動画）用
DEFAULT_GLOBAL_JSON_FILE   = "/mnt/bigdata/00_students/ymori_ucl/trusco/multicam_tracking/for_evaluation/20241003/thesis/Master_thesis_json/kalman_ang2_dtw2_adjusted_no_leg_per_cam_with_new_40osnet_feature_tracking_result_2024-10-03_39600_41400_07_300_100_8500_130.0_True_130.0_3.json"
DEFAULT_GLOBAL_VIDEO_FILE  = "/mnt/gazania/trusco-stitch/2024/2024-10-03/new_overlap_1100_1200_nkawa1934.mp4"
DEFAULT_GLOBAL_OUTPUT_FILE = "/mnt/bigdata/00_students/ymori_ucl/trusco/multicam_tracking/for_evaluation/20241003/thesis/Master_thesis_json/kalman_ang2_dtw2_adjusted_no_leg_per_cam_with_new_40osnet_feature_tracking_result_2024-10-03_39600_41400_07_300_100_8500_130.0_True_130.0_3.mp4"

FRAME_INDEX_CORNER = "top-right"

# JSONデータをロード
def load_tracking_data(json_file):
    with open(json_file, "r") as file:
        data = json.load(file)
    return data


# ランダムカラーを生成する関数
def generate_random_color():
    return [random.randint(0, 255) for _ in range(3)]


# 動画にバウンディングボックスと移動軌跡を描画して保存
def create_video_with_continuous_tracking(tracking_data, video_file, output_path, bbox_key="bbox", offset_x=0.0, offset_y=0.0):
    cap = cv2.VideoCapture(video_file)

    if not cap.isOpened():
        raise RuntimeError(f"Video open failed: {video_file}. Check path/codec/FFmpeg.")

    fps   = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out    = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    track_colors    = {track["track_id"]: generate_random_color() for frame in tracking_data for track in frame.get("tracks", [])}
    track_positions = {track_id: [] for track_id in track_colors}

    if track_colors:
        min_track_id = min(track_colors.keys())
        max_track_id = max(track_colors.keys())
        print(f"Minimum track ID: {min_track_id}, Maximum track ID: {max_track_id}")
    else:
        print("No tracks found in tracking_data.")

    frame_idx    = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    pbar = tqdm(total=total_frames, desc=os.path.basename(output_path))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of video reached or cannot read the frame.")
            break

        if frame_idx < len(tracking_data):
            frame_data = tracking_data[frame_idx].get("tracks", [])

            for track in frame_data:
                bbox = track[bbox_key]

                # ★ bbox フォーマットの違いに応じて分岐
                if bbox_key == "original_bbox":
                    # (cx, cy, w, h) → 左上座標に変換
                    cx, cy, w, h = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
                    x1 = int(cx - w / 2.0 - offset_x)
                    y1 = int(cy - h / 2.0 - offset_y)
                    width_box  = int(w)
                    height_box = int(h)
                else:
                    # (lx, ly, w, h) = TLWH
                    lx, ly, w, h = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
                    x1 = int(lx - offset_x)
                    y1 = int(ly - offset_y)
                    width_box  = int(w)
                    height_box = int(h)

                color = track_colors[track["track_id"]]
                center_position = (x1 + width_box // 2, y1 + height_box // 2)

                cv2.rectangle(frame, (x1, y1), (x1 + width_box, y1 + height_box), color, 10)
                cv2.putText(frame, str(track["track_id"]), (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 2.0, color, 4)

                track_positions[track["track_id"]].append(center_position)
                if len(track_positions[track["track_id"]]) > 1:
                    cv2.polylines(frame, [np.array(track_positions[track["track_id"]], dtype=np.int32)], isClosed=False, color=color, thickness=5)

        # ★★★ ここからフレーム番号の描画 ★★★
        if frame_idx < len(tracking_data):
            frame_id_to_show = tracking_data[frame_idx].get("frame_id", frame_idx)
        else:
            frame_id_to_show = frame_idx

        text = f"{frame_id_to_show}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.0          # track_id(2.0) より小さめ
        thickness = 2
        color = (255, 255, 255)
        margin = 20

        (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)

        if FRAME_INDEX_CORNER == "top-right":
            org = (width - text_w - margin, margin + text_h)
        elif FRAME_INDEX_CORNER == "bottom-left":
            org = (margin, height - margin)
        else:
            # 万一変な値が来たときはデフォルトで右上
            org = (width - text_w - margin, margin + text_h)

        # ちょっとだけ縁取り（黒）して読みやすくしてもいいなら：
        cv2.putText(frame, text, (org[0] + 1, org[1] + 1), font, scale, (0, 0, 0), thickness + 1)
        cv2.putText(frame, text, org, font, scale, color, thickness)
        # ★★★ フレーム番号ここまで ★★★

        out.write(frame)
        frame_idx += 1
        pbar.update(1)

    pbar.close()
    cap.release()
    out.release()



def build_scmot_video_path(video_root, cam_id, video_pattern):
    """
    video_root/camera{cam_id}/{video_pattern.format(cam=cam_id)} という形で動画パスを作る。
    例: video_root=/.../movie/20241003
        cam_id="A4"
        video_pattern="{cam}_2024-10-03_39600_41400.mp4"
        -> /.../movie/20241003/cameraA4/A4_2024-10-03_39600_41400.mp4
    """
    cam_dir = os.path.join(video_root, f"camera{cam_id}")
    filename = video_pattern.format(cam=cam_id)
    return os.path.join(cam_dir, filename)


def parse_args():
    parser = argparse.ArgumentParser(description="Draw tracking results on video (SCMOT / global).")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # -------- SCMOT モード（per-camera）---------
    scmot = subparsers.add_parser("scmot", help="SCMOT-style per-camera visualization (use original_bbox).")
    scmot.add_argument("--json_path",    type=str, default=DEFAULT_SCMOT_JSON_PATH,   help=f"SCMOT の JSON ファイル or per_cam_json ディレクトリのパス (default: {DEFAULT_SCMOT_JSON_PATH})")
    scmot.add_argument("--video_root",   type=str, default=DEFAULT_SCMOT_VIDEO_ROOT,  help=f"各カメラ動画を格納しているルートディレクトリ（cameraA4/... の親） (default: {DEFAULT_SCMOT_VIDEO_ROOT})")
    scmot.add_argument("--output_root",  type=str, default=DEFAULT_SCMOT_OUTPUT_ROOT, help=f"書き出し先ディレクトリ (default: {DEFAULT_SCMOT_OUTPUT_ROOT})")
    scmot.add_argument("--video_pattern", type=str, default="{cam}_2024-10-03_39600_41400.mp4", help='各 camera{cam} ディレクトリ内の動画ファイル名パターン。{cam} がカメラID(A4など)に置き換わる (default: "{cam}_2024-10-03_39600_41400.mp4")')

    # -------- Global モード（stitch 全体動画）---------
    glob_p = subparsers.add_parser("global", help="Global stitched video visualization (use bbox with offset).")
    glob_p.add_argument("--json_file",   type=str,   default=DEFAULT_GLOBAL_JSON_FILE,   help=f"グローバル tracking JSON ファイル (default: {DEFAULT_GLOBAL_JSON_FILE})")
    glob_p.add_argument("--video_file",  type=str,   default=DEFAULT_GLOBAL_VIDEO_FILE,  help=f"グローバル動画ファイル (default: {DEFAULT_GLOBAL_VIDEO_FILE})")
    glob_p.add_argument("--output_file", type=str,   default=DEFAULT_GLOBAL_OUTPUT_FILE, help=f"出力動画ファイル (default: {DEFAULT_GLOBAL_OUTPUT_FILE})")
    glob_p.add_argument("--offset_x",    type=float, default=3885.36,                    help="global モードで bbox[0] から引く X オフセット (default: 3885.36)")
    glob_p.add_argument("--offset_y",    type=float, default=812.703,                    help="global モードで bbox[1] から引く Y オフセット (default: 812.703)")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == "global":
        # ===== Global モード =====
        print("[MODE] global")
        print(f"JSON : {args.json_file}")
        print(f"VIDEO: {args.video_file}")
        print(f"OUT  : {args.output_file}")
        tracking_data = load_tracking_data(args.json_file)
        create_video_with_continuous_tracking(tracking_data, args.video_file, args.output_file, bbox_key="bbox", offset_x=args.offset_x, offset_y=args.offset_y)

    elif args.mode == "scmot":
        # ===== SCMOT モード =====
        json_path    = args.json_path
        video_root   = args.video_root
        output_root  = args.output_root
        video_pattern = args.video_pattern

        if os.path.isdir(json_path):
            # ディレクトリ → 全カメラ処理
            os.makedirs(output_root, exist_ok=True)
            json_files = sorted(glob.glob(os.path.join(json_path, "*.json")))
            print(f"[MODE] scmot (multi-cam)  dir={json_path}")
            print(f"Found {len(json_files)} json files.")

            for jf in json_files:
                cam_id = os.path.splitext(os.path.basename(jf))[0]  # A4.json -> A4
                video_file  = build_scmot_video_path(video_root, cam_id, video_pattern)
                output_file = os.path.join(output_root, f"{cam_id}.mp4")

                print(f"[SCMOT] cam={cam_id}")
                print(f"  JSON : {jf}")
                print(f"  VIDEO: {video_file}")
                print(f"  OUT  : {output_file}")

                tracking_data = load_tracking_data(jf)
                create_video_with_continuous_tracking(tracking_data, video_file, output_file, bbox_key="original_bbox", offset_x=0.0, offset_y=0.0)
        else:
            # 単一 JSON ファイル → 1カメラだけ処理
            os.makedirs(output_root, exist_ok=True)
            cam_id = os.path.splitext(os.path.basename(json_path))[0]
            video_file  = build_scmot_video_path(video_root, cam_id, video_pattern)
            output_file = os.path.join(output_root, f"{cam_id}.mp4")

            print("[MODE] scmot (single-cam)")
            print(f"cam_id: {cam_id}")
            print(f"JSON  : {json_path}")
            print(f"VIDEO : {video_file}")
            print(f"OUT   : {output_file}")

            tracking_data = load_tracking_data(json_path)
            create_video_with_continuous_tracking(tracking_data, video_file, output_file, bbox_key="original_bbox", offset_x=0.0, offset_y=0.0)


if __name__ == "__main__":
    main()
