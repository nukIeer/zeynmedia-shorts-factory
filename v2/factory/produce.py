"""V2 production run: topic -> assets -> music hook -> Remotion render -> Release files -> YouTube.

Usage: python v2/factory/produce.py [--topic SLUG] [--music-dir PATH] [--skip-upload]
Topics live in v2/topics/*.json (verified data + SKILLER-style title). Music comes from the
private zeynmedia-music checkout; each track's start second is read from its library.json.
"""
import argparse
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

V2 = Path(__file__).resolve().parent.parent
ROOT = V2.parent
sys.path.insert(0, str(V2 / "scripts"))
sys.path.insert(0, str(ROOT / "factory"))

from fetch_assets import build_props, load_index, save_index  # noqa: E402

TOPICS = V2 / "topics"
HISTORY = ROOT / "data" / "history.json"
OUT = ROOT / "output"
PUBLIC_MUSIC = V2 / "public" / "music"
MUSIC_REPEAT_GAP = 12


def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def pick_topic(history, forced):
    topics = sorted(p.stem for p in TOPICS.glob("*.json"))
    if forced:
        if forced not in topics:
            sys.exit(f"konu yok: {forced} (var olanlar: {', '.join(topics)})")
        return forced
    # Least recently used first; never-used topics win, ties broken randomly
    last_used = {t: -1 for t in topics}
    for i, h in enumerate(history):
        slug = (h.get("topic") or "").removeprefix("v2:")
        if slug in last_used and h.get("video_id"):
            last_used[slug] = i
    oldest = min(last_used.values())
    return random.choice([t for t, i in last_used.items() if i == oldest])


def pick_music(history, music_dir):
    if not music_dir:
        return None
    lib = json.loads((music_dir / "library.json").read_text(encoding="utf-8"))
    tracks = [t for t in lib if not t.get("excluded") and (music_dir / t["file"]).exists()]
    if not tracks:
        return None
    recent = {h.get("music") for h in history[-MUSIC_REPEAT_GAP:]}
    pool = [t for t in tracks if t["file"] not in recent] or tracks
    track = random.choice(pool)
    PUBLIC_MUSIC.mkdir(parents=True, exist_ok=True)
    # Fixed ASCII name: track titles carry spaces/unicode that would need URL escaping in staticFile
    shutil.copy2(music_dir / track["file"], PUBLIC_MUSIC / f"current{Path(track['file']).suffix.lower()}")
    return track


def render(props, out_path):
    props_path = OUT / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    cmd = ["npx", "remotion", "render", "src/index.ts", "Short", str(out_path), f"--props={props_path}", "--log=warn"]
    subprocess.run(cmd, cwd=V2, check=True, shell=os.name == "nt")
    props_path.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default=os.environ.get("INPUT_TOPIC") or None)
    ap.add_argument("--music-dir", default=os.environ.get("MUSIC_DIR"))
    ap.add_argument("--skip-upload", action="store_true", default=os.environ.get("SKIP_UPLOAD", "").lower() == "true")
    args = ap.parse_args()

    history = load_history()
    slug = pick_topic(history, args.topic)
    spec = json.loads((TOPICS / f"{slug}.json").read_text(encoding="utf-8"))
    print(f"[v2] konu: {slug} ({spec['props']['template']})")

    index = load_index()
    try:
        props = build_props(spec, index)
    finally:
        save_index(index)

    track = pick_music(history, Path(args.music_dir) if args.music_dir else None)
    if track:
        props.update(music=f"music/current{Path(track['file']).suffix.lower()}", musicStart=track["start"])
        print(f"[v2] müzik: {track['file']} @ {track['start']}s ({track.get('method')})")
    else:
        print("[v2] müzik yok, sadece efektlerle render")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    OUT.mkdir(exist_ok=True)
    video = OUT / f"{stamp}-{slug}.mp4"
    render(props, video)
    print(f"[v2] render bitti: {video} ({video.stat().st_size / 1e6:.1f} MB)")

    yt = spec["youtube"]
    video_id = None
    if not args.skip_upload:
        from upload import upload_video

        video_id = upload_video(video, yt, privacy=os.environ.get("YT_PRIVACY", "public"))

    meta = {
        "topic": f"v2:{slug}",
        "headerTitle": props["title"],
        "headerSubtitle": props["subtitle"],
        "template": props["template"],
        "music": track["file"] if track else None,
        "musicStart": track["start"] if track else None,
        "youtube": yt,
        "video_id": video_id,
    }
    (OUT / f"{stamp}-{slug}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    if not os.environ.get("GITHUB_ACTIONS") and not video_id:
        return  # local preview renders don't count as published videos
    history.append({"date": stamp, "topic": meta["topic"], "title": yt["title"], "video_id": video_id, "music": meta["music"]})
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
