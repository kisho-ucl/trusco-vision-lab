#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory, abort


def parse_args():
    p = argparse.ArgumentParser(description="Clip annotation server")
    p.add_argument("--result_id", required=True, help="Result ID (e.g. 77)")
    p.add_argument("--port", type=int, default=8080)
    return p.parse_args()


def load_annotations(path: Path) -> dict:
    annotations = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    annotations[entry["clip_id"]] = entry
    return annotations


def save_annotations(path: Path, annotations: dict):
    with open(path, "w") as f:
        for entry in annotations.values():
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def create_app(result_id: str, clips_base: Path) -> Flask:
    static_dir = Path(__file__).parent / "static"
    app = Flask(__name__, static_folder=None)

    manifest_path = clips_base / result_id / "manifest.json"
    annotations_path = clips_base / result_id / "annotations.jsonl"
    clips_dir = clips_base / result_id / "clips"

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(static_dir, filename)

    @app.route("/api/manifest")
    def get_manifest():
        if not manifest_path.exists():
            abort(404, description=f"manifest.json not found for result_id={result_id}")
        with open(manifest_path) as f:
            return jsonify(json.load(f))

    @app.route("/api/annotations")
    def get_annotations():
        return jsonify(load_annotations(annotations_path))

    @app.route("/api/save", methods=["POST"])
    def save_annotation():
        data = request.get_json()
        if not data or not data.get("clip_id"):
            return jsonify({"error": "clip_id required"}), 400
        data["annotated_at"] = datetime.now(timezone.utc).isoformat()
        annotations = load_annotations(annotations_path)
        annotations[data["clip_id"]] = data
        save_annotations(annotations_path, annotations)
        return jsonify({"ok": True})

    @app.route("/clips/<path:filepath>")
    def serve_clip(filepath):
        return send_from_directory(clips_dir, filepath)

    return app


if __name__ == "__main__":
    args = parse_args()
    repo_root = Path(__file__).parent.parent.parent
    clips_base = repo_root / "task_annotation_clips"

    app = create_app(args.result_id, clips_base)

    print(f"result_id : {args.result_id}")
    print(f"manifest  : {clips_base / args.result_id / 'manifest.json'}")
    print(f"clips dir : {clips_base / args.result_id / 'clips'}")
    print(f"Open      : http://localhost:{args.port}/")

    app.run(host="0.0.0.0", port=args.port, debug=False)
