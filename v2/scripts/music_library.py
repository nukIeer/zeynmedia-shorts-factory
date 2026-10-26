"""Scans a music folder and writes library.json with the best start second for each track.

How the start is chosen (per track):
  1. If the track has a YouTube id in v2/music/tracks.json -> YouTube "Most replayed" heatmap (music_hooks.py).
  2. Otherwise audio analysis: the WINDOW-second segment with the highest loudness that also
     *opens on a drop* (sharp energy rise), so the video starts exactly where the beat hits.

Non-music files (Quran recitations, voice-overs, engine sounds...) are skipped.
Usage: python v2/scripts/music_library.py C:/path/to/zeynmedia-music [--window 18]
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

RATE = 11025
HOP = 0.1  # seconds per energy frame
EXT = {".mp3", ".m4a", ".wav", ".ogg", ".opus", ".webm"}
SKIP_PATTERNS = re.compile(r"sure(si)?\b|suresi|imam|pure.?sound|motovlog|motoblog|nasil|nasıl|sezen|benim_yerime", re.I)


def decode(path):
    raw = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(RATE), "-f", "f32le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32)


def energy_curve(pcm):
    n = int(RATE * HOP)
    frames = len(pcm) // n
    e = np.sqrt((pcm[: frames * n].reshape(frames, n) ** 2).mean(axis=1))
    return e / (e.max() + 1e-9)


def best_start(e, window):
    w = int(window / HOP)
    look = int(2.0 / HOP)
    dur = len(e)
    if dur <= w + look:
        return 0.0, "short"
    csum = np.concatenate([[0], np.cumsum(e)])
    mean_at = lambda a, b: (csum[b] - csum[a]) / max(1, b - a)  # noqa: E731
    first = max(look, int(dur * 0.04))
    best_t, best_score = first, -1.0
    gmean = e.mean() + 1e-9
    for t in range(first, dur - w, 2):
        loud = mean_at(t, t + w) / gmean
        rise = mean_at(t, t + look) / (mean_at(t - look, t) + 1e-3)
        score = loud + 0.35 * min(rise, 3.0)
        if score > best_score:
            best_t, best_score = t, score
    # Snap to the sharpest onset within ±1 s so the first frame lands on the hit
    lo, hi = max(1, best_t - 10), min(dur - 1, best_t + 10)
    onset = lo + int(np.argmax(np.diff(e[lo - 1 : hi + 1])[: hi - lo]))
    return round(max(0.0, onset * HOP - 0.15), 2), "drop"


YT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def _video_renderers(obj):
    if isinstance(obj, dict):
        if "videoRenderer" in obj:
            yield obj["videoRenderer"]
        for v in obj.values():
            yield from _video_renderers(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _video_renderers(v)


def _seconds(text):
    parts = [int(x) for x in text.split(":")]
    return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))


def youtube_match(stem, duration):
    """Finds the YouTube upload this file was ripped from: same title search, length within 2.5 s."""
    import time

    import requests

    query = re.sub(r"\(\d+\)$", "", stem).replace("_", " ").strip()
    time.sleep(1)
    html = requests.get("https://www.youtube.com/results", params={"search_query": query}, headers=YT_HEADERS, cookies={"CONSENT": "YES+1"}, timeout=30).text
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html)
    if not m:
        return None
    for v in list(_video_renderers(json.loads(m.group(1))))[:8]:
        length = v.get("lengthText", {}).get("simpleText")
        if length and abs(_seconds(length) - duration) <= 2.5:
            return v["videoId"]
    return None


def main():
    import sys

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--window", type=float, default=18)
    ap.add_argument("--youtube", action="store_true", help="match each file to its YouTube upload and use the Most-replayed heatmap")
    args = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    folder = Path(args.folder)
    lib_path = folder / "library.json"
    old = {t["file"]: t for t in json.loads(lib_path.read_text(encoding="utf-8"))} if lib_path.exists() else {}

    tracks, skipped = [], []
    for p in sorted(folder.iterdir(), key=lambda x: x.name.lower()):
        if p.suffix.lower() not in EXT:
            continue
        if SKIP_PATTERNS.search(p.stem) or p.suffix == ".MP3":
            skipped.append(p.name)
            continue
        if p.name in old and (old[p.name].get("manual") or old[p.name].get("excluded")):
            tracks.append(old[p.name])  # choices made in tools/hook-picker.html win
            continue
        e = energy_curve(decode(p))
        duration = round(len(e) * HOP, 1)
        if duration < 30:
            skipped.append(p.name)
            continue
        start, method = best_start(e, args.window)
        entry = {"file": p.name, "duration": duration, "start": start, "method": method, "slowed": bool(re.search(r"slow", p.stem, re.I))}
        if args.youtube:
            from music_hooks import best_window, heatmap

            vid = old.get(p.name, {}).get("youtube") or youtube_match(p.stem, duration)
            hm = best_window(heatmap(vid), args.window) if vid else None
            if vid:
                entry["youtube"] = vid
            if hm:
                entry.update(start=hm[0], method="heatmap", hookScore=hm[1], audioStart=start)
        tracks.append(entry)
        print(f"{entry['start']:6.1f}s / {duration:5.1f}s  {entry['method']:7s} {p.name}")

    lib_path.write_text(json.dumps(tracks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(tracks)} parça kütüphaneye yazıldı, {len(skipped)} dosya atlandı:")
    for s in skipped:
        print("  -", s)


if __name__ == "__main__":
    main()
