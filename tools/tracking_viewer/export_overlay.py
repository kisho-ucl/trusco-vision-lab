# export_overlay_simple.py
import cv2, json, os

# 入力/出力
VIDEO = "/mnt/gazania/trusco-stitch/2024/2024-10-03/new_overlap_0900_1100_2x_nkawa1934.mp4"
JSON_TRACK = "/home/kisho_ucl/kisho_ws/trusco-vision-lab/dataset_readonly/fastops/result/77/track/modified_kalman_dtw2_adjusted_tracking_result.json"
JSON_TASK  = None  # タスクJSONなし
OUT_MP4    = "/home/kisho_ucl/kisho_ws/trusco-vision-lab/task_annotation_clips/overlay_77_debug.mp4"

# あなたの補正（結合キャンバス→元動画）
SCALE = 1.0    # 元動画に重ねるなら 1.0、縦横1/2動画なら 0.5
X_OFF = 3885.36
Y_OFF =  812.703

# Result_ID=77 は09:00-10:00（1時間, 5fps=18000frames）
# stitch動画は09:00-11:00（2時間）を18000framesに圧縮（2x）
# → tracking frame_id N は video frame N//2 に対応
VIDEO_FRAME_DIVISOR = 2

START_FID = 0   # 開始トラッキングフレーム番号（含む）
END_FID   = 2000  # デバッグ用：最初の100フレームのみ


# タスク表示（色は #667595, #d86560, #789f84）
def hex2bgr(hx: str):
    hx = hx.lstrip('#')
    return (int(hx[4:6],16), int(hx[2:4],16), int(hx[0:2],16))

task_labels = {0:"Inspecting", 1:"Transporting", 2:"Sorting"}
task_colors = {
    0: hex2bgr("#2761DE"),
    1: hex2bgr("#c94942"),
    2: hex2bgr("#35aa58"),
}

def put_text_with_bg(img, text, org, fg, scale=1.0):
    x,y = org
    cv2.putText(img, text, (x+2,y+2), cv2.FONT_HERSHEY_SIMPLEX, scale, (0,0,0), 4, cv2.LINE_AA)
    cv2.putText(img, text, (x, y),     cv2.FONT_HERSHEY_SIMPLEX, scale, fg,        2, cv2.LINE_AA)

# 読み込み
with open(JSON_TRACK, "r") as f:
    frames = json.load(f)
frame_map = {fr["frame_id"]: fr["tracks"] for fr in frames}

tasks = None
if JSON_TASK is not None:
    try:
        with open(JSON_TASK, "r") as f:
            tasks = json.load(f)
    except Exception:
        print("[WARN] タスクJSONが見つからない/読めないため、タスク表示はスキップします。")

def current_task_and_seg(worker_id, fid):
    """ 該当フレームのタスクlabelと区間(seg)を返す; 無ければ (None, None) """
    if tasks is None: return None, None
    if worker_id < 0 or worker_id >= len(tasks): return None, None
    for seg in tasks[worker_id]:
        if seg["start"] <= fid <= seg["end"]:
            return seg["label"], seg
    return None, None

# 動画入出力
cap = cv2.VideoCapture(VIDEO)
if not cap.isOpened():
    raise RuntimeError("動画を開けませんでした")

vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"[INFO] input: {vid_w}x{vid_h} @ {fps:.2f}fps, frames={total}")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(OUT_MP4, fourcc, fps, (vid_w, vid_h))
if not writer.isOpened():
    raise RuntimeError("出力ファイルを開けませんでした")

# 処理ループ（ウィンドウ無し）
# fid = video frame index
# tracking frame_id = fid * VIDEO_FRAME_DIVISOR
video_end = END_FID // VIDEO_FRAME_DIVISOR
video_start = START_FID // VIDEO_FRAME_DIVISOR
fid = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break

    if fid < video_start:
        fid += 1
        continue
    if fid > video_end:
        break

    tracks = frame_map.get(fid * VIDEO_FRAME_DIVISOR, [])
    for t in tracks:
        tid = t["track_id"]
        x,y,w,h = t["bbox"]

        # 座標補正 → スケール
        x = x - X_OFF; y = y - Y_OFF
        x1 = int(x * SCALE);          y1 = int(y * SCALE)
        x2 = int((x + w) * SCALE);    y2 = int((y + h) * SCALE)

        # クリップ＆無効除外
        ix1 = max(0, min(vid_w-1, min(x1, x2)))
        iy1 = max(0, min(vid_h-1, min(y1, y2)))
        ix2 = max(0, min(vid_w-1, max(x1, x2)))
        iy2 = max(0, min(vid_h-1, max(y1, y2)))
        if ix2 - ix1 < 2 or iy2 - iy1 < 2:
            continue

        # タスク取得
        lab, seg = current_task_and_seg(tid, fid)
        color = task_colors.get(lab, (180,180,180)) if lab is not None else (180,180,180)

        # 枠
        cv2.rectangle(frame, (ix1,iy1), (ix2,iy2), color, 3)

        # ID
        put_text_with_bg(frame, f"ID {tid}", (ix1, max(24, iy1-10)), fg=color, scale=0.95)

        # タスク＋経過時間＋進捗バー
        if lab is not None and seg is not None:
            # 経過時間
            # elapsed_f = max(0, fid - seg["start"])
            # sec = elapsed_f / fps
            # mm, ss = divmod(int(round(sec)), 60)
            # tstr = f"{task_labels.get(lab, f'label{lab}')}  {mm:02d}:{ss:02d}"
            tstr = f"{task_labels.get(lab, f'label{lab}')}"
            ty = iy2 + 28 if iy2 + 28 < vid_h else max(28, iy1 - 28)
            put_text_with_bg(frame, tstr, (ix1, ty), fg=color, scale=1.05)

            # # 進捗バー
            # length_f = max(1, seg["end"] - seg["start"])
            # p = max(0.0, min(1.0, (fid - seg["start"]) / float(length_f)))
            # bar_w, bar_h = 140, 6
            # bx, by = ix1, min(vid_h - 10, ty + 8)
            # cv2.rectangle(frame, (bx, by), (bx+bar_w, by+bar_h), (50,50,50), -1)
            # cv2.rectangle(frame, (bx, by), (bx+int(bar_w*p), by+bar_h), color, -1)

    writer.write(frame)

    # 簡易プログレス
    if fid % 10 == 0:
        print(f"[video {fid}/{video_end}] tracking_fid={fid * VIDEO_FRAME_DIVISOR}, tracks={len(tracks)}")
    fid += 1

cap.release()
writer.release()
print(f"[DONE] saved -> {os.path.abspath(OUT_MP4)}")
