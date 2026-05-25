import os
import cv2
import json
import argparse
import numpy as np
import pickle
from glob import glob
import os.path as path
from datetime import datetime

# ----------------------
# 固定パラメータ（デフォルト値）
# ----------------------
BASE_X = 3885.356
BASE_Y = 812.703
USE_FRAME = 1  # 例：5フレームに1枚だけ処理する
START_TIME = "11:00:00"  # 処理開始時刻
DEFAULT_UNDIS_DIR = "/mnt/gazania/trusco-undis/2024/2024-10-03"

# ----------------------
# 引数パース
# ----------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Tracking JSON と ts_cache から undistorted 動画のフレームをキャプチャし、Market-1501 形式でトリミング画像を作成する"
    )
    parser.add_argument("--track_json", type=str, required=True,
                        help="入力 tracking JSON ファイルのパス")
    parser.add_argument("--undis_dir", type=str, default=DEFAULT_UNDIS_DIR,
                        help="Undistorted 動画が保存されたディレクトリ")
    parser.add_argument("--start_time", type=str, default=START_TIME,
                        help='処理開始時刻（例："11:00:00"）')
    parser.add_argument("--use_frame", type=int, default=USE_FRAME,
                        help="使用するフレーム間隔（例：5なら5フレームに1枚）")
    parser.add_argument("--ts_cache_file", type=str, default="/mnt/bigdata/01_projects/2024_trusco/ts_result/20241003-tscaches_adjusted.pkl",
                        help="タイムスタンプキャッシュファイル（pickle形式）のパス")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="切り出した画像を保存する出力ディレクトリ")
    return parser.parse_args()

# ----------------------
# tracking JSON を読み込む
# ----------------------
def load_tracking_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ----------------------
# ts_cache の読み込み（pickle）
# ----------------------
def load_ts_cache(ts_cache_file):
    with open(ts_cache_file, "rb") as f:
        ts_cache = pickle.load(f)
    return ts_cache

# ----------------------
# capImage 関数
# undistorted 動画から指定カメラ・元のフレーム番号をキャプチャする
# ----------------------
caps = {}
def capImage(cam, orig_frame, ts_cache, START_TIME, undis_dir):
    """
    cam: カメラID（例："A10"）
    orig_frame: 元の動画上のフレーム番号（例: JSONの再インデックス後の番号 *2 + 1）
    ts_cache: タイムスタンプキャッシュ（pickleで読み込んだもの）
    START_TIME: 開始時刻文字列（例:"11:00:00"）
    undis_dir: undistorted 動画のディレクトリ
    """
    global caps
    # START_TIME を秒に変換
    cur_in_sec = int((datetime.strptime(START_TIME, "%H:%M:%S") - datetime(1900, 1, 1)).total_seconds())
    # ここでは、元のフレーム番号をそのまま使用
    cur_in_sec += orig_frame * 0.2  # 例: 0.2秒ごとに1フレーム進む

    ts_list = ts_cache[0].get(cam)
    if ts_list is None:
        print(f"[Error] ts_cache にカメラ {cam} の情報がありません")
        return None
    idx = int(5 * (cur_in_sec - ts_cache[1][cam]))
    try:
        vid_idx, frm_idx = ts_list[idx]
    except IndexError:
        print(f"[Error] ts_cache のインデックス {idx} がカメラ {cam} では範囲外")
        return None

    vid_pattern = path.join(undis_dir, f"camera{cam}", f"video_??-??-??_{vid_idx:02d}.mp4")
    vid_files = glob(vid_pattern)
    if not vid_files:
        print(f"[Error] {vid_pattern} に一致する動画ファイルが見つかりません")
        return None
    video_file = vid_files[0]

    if cam in caps and caps[cam]["vid_idx"] != vid_idx:
        caps[cam]["cap"].release()
    if cam not in caps or caps[cam]["vid_idx"] != vid_idx:
        cap = cv2.VideoCapture(video_file)
        caps[cam] = {
            "cap": cap,
            "vid_idx": vid_idx,
            "cur_frm": 0
        }
    else:
        cap = caps[cam]["cap"]

    if caps[cam]["cur_frm"] >= frm_idx:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frm_idx)
    while cap.get(cv2.CAP_PROP_POS_FRAMES) <= frm_idx:
        ret, frame_img = cap.read()
        if not ret:
            print(f"[Error] カメラ {cam} の動画 {video_file} からフレーム {frm_idx} の読み込みに失敗")
            return None
        caps[cam]["frm"] = frame_img
        caps[cam]["cur_frm"] = cap.get(cv2.CAP_PROP_POS_FRAMES)
    return caps[cam]["frm"]

def transform_cam_for_filename(cam_str):
    if not cam_str:
        return "c0"
    letter = cam_str[0].upper()
    digits = ''.join([c for c in cam_str if c.isdigit()])
    if digits == "":
        digits = "0"
    if letter == "A":
        # Aの場合はそのまま数字部分を使う
        return f"c{digits}"
    elif letter == "B":
        try:
            new_number = int(digits) + 20
        except ValueError:
            new_number = digits
        return f"c{new_number}"
    else:
        return f"c{cam_str}"




# ----------------------
# メイン処理：tracking JSON の各対象フレーム・各トラックから画像をキャプチャし、トリミング
# Market-1501 形式のファイル名で保存する
# ----------------------
def main():
    args = parse_args()
    tracking_data = load_tracking_json(args.track_json)
    ts_cache = load_ts_cache(args.ts_cache_file)
    use_frame = args.use_frame

    os.makedirs(args.output_dir, exist_ok=True)

    # tracking_data の各フレームは既に偶数フレームがスキップされ、frame_id は 0～ となっている
    # 元の動画上のフレーム番号は、json_frame_id * 2 + 1 となる
    for frame in tracking_data:
        json_frame_id = frame.get("frame_id")
        if json_frame_id is None:
            continue
        # USE_FRAME に基づいてサブサンプリング（例: use_frame=5 の場合、json_frame_id が 0,5,10,... のみ処理）
        if json_frame_id % use_frame != 0:
            continue
        # 元の動画上のフレーム番号
        orig_frame = json_frame_id * 2 + 1

        # 各トラックを処理
        for track in frame.get("tracks", []):
            subj_id = track.get("subj_id")
            if subj_id is None or str(subj_id) == "None":
                continue
            try:
                person_id = int(subj_id)
                person_str = f"{person_id:04d}"
            except Exception:
                person_str = str(subj_id)

            # 複数カメラ情報がある場合：src_cam_duplicate_list と bbox_list
            dup_cams = track.get("src_cam_duplicate_list", [])
            dup_bboxes = track.get("bbox_list", [])

            ## リストのすべてを使用する時
            # if dup_cams and dup_bboxes and (len(dup_cams) == len(dup_bboxes)):
            #     for dup_index, (cam, bbox) in enumerate(zip(dup_cams, dup_bboxes)):

            if dup_cams and dup_bboxes and len(dup_cams) > 0 and len(dup_bboxes) > 0:
                cam = dup_cams[0]
                bbox = dup_bboxes[0]

                frame_img = capImage(cam, orig_frame, ts_cache, args.start_time, args.undis_dir)
                if frame_img is None:
                    continue
                # bbox は中心形式：[cx, cy, w, h]
                cx, cy, box_w, box_h = map(float, bbox)
                # 計算: top-left = (cx - w/2, cy - h/2), bottom-right = (cx + w/2, cy + h/2)
                x1 = int(round(cx - box_w / 2))
                y1 = int(round(cy - box_h / 2))
                x2 = int(round(cx + box_w / 2))
                y2 = int(round(cy + box_h / 2))
                h_img, w_img = frame_img.shape[:2]
                # 画像範囲にクリップ
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w_img, x2)
                y2 = min(h_img, y2)
                if x2 <= x1 or y2 <= y1:
                    continue
                crop = frame_img[y1:y2, x1:x2]
                new_cam = transform_cam_for_filename(cam)
                seq = "1"
                # 出力ファイル名: "{person_str}_{new_cam}s{seq}_{orig_frame:06d}_00.jpg"
                filename = f"{person_str}_{new_cam}s{seq}_{orig_frame:06d}_00.jpg"
                output_path = os.path.join(args.output_dir, filename)
                cv2.imwrite(output_path, crop)
                print(f"Saved: {output_path}")
            else:
                cam = track.get("src_cam", "unknown")
                frame_img = capImage(cam, orig_frame, ts_cache, args.start_time, args.undis_dir)
                if frame_img is None:
                    continue
                bbox = track.get("bbox")
                if not bbox or len(bbox) != 4:
                    continue
                # ここも同様に bbox は中心形式とする
                cx, cy, box_w, box_h = map(float, bbox)
                x1 = int(round(cx - box_w / 2))
                y1 = int(round(cy - box_h / 2))
                x2 = int(round(cx + box_w / 2))
                y2 = int(round(cy + box_h / 2))
                h_img, w_img = frame_img.shape[:2]
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w_img, x2)
                y2 = min(h_img, y2)
                if x2 <= x1 or y2 <= y1:
                    continue
                crop = frame_img[y1:y2, x1:x2]
                new_cam = transform_cam_for_filename(cam)
                seq = "1"
                # 出力ファイル名: "{person_str}_{new_cam}s{seq}_{orig_frame:06d}_00.jpg"
                filename = f"{person_str}_{new_cam}s{seq}_{orig_frame:06d}_00.jpg"
                output_path = os.path.join(args.output_dir, filename)
                cv2.imwrite(output_path, crop)
                print(f"Saved: {output_path}")

if __name__ == '__main__':
    main()