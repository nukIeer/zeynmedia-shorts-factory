"""Finds the most replayed section of each song from YouTube's "Most replayed" heatmap.

Reads/writes v2/music/tracks.json: [{"file": "without-me.mp3", "title": "...", "youtube": "<id>"}, ...]
and fills "start" (seconds) = beginning of the WINDOW-second segment with the highest replay intensity.
Audio files go to v2/public/music/<file>; the renderer plays them from "start".

Usage: python v2/scripts/music_hooks.py [--window 18]
"""
import argparse
import json
import re
from pathlib import Path

import requests

TRACKS = Path(__file__).resolve().parent.parent / "music" / "tracks.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
SKIP_INTRO = 0.06  # every heatmap spikes at 0:00 because playback starts there


def heatmap(video_id):
    html = requests.get(f"https://www.youtube.com/watch?v={video_id}", headers=HEADERS, cookies={"CONSENT": "YES+1"}, timeout=30).text
    m = re.search(r'"markerType":"MARKER_TYPE_HEATMAP","markers":(\[.*?\])', html)
    if not m:
        return []
    return [(int(x["startMillis"]) / 1000, int(x["durationMillis"]) / 1000, float(x["intensityScoreNormalized"])) for x in json.loads(m.group(1))]


def best_window(markers, window):
    if not markers:
        return None
    total = markers[-1][0] + markers[-1][1]
    seg = markers[0][1]
    first = int(len(markers) * SKIP_INTRO)
    n = max(1, round(window / seg))
    best_i, best_score = first, -1.0
    for i in range(first, len(markers) - n + 1):
        score = sum(m[2] for m in markers[i : i + n])
        if score > best_score:
            best_i, best_score = i, score
    # Start a beat early so the hook lands just after the video opens
    start = max(0.0, markers[best_i][0] - 1.0)
    return round(min(start, total - window), 1), round(best_score / n, 2)


def loudest_window(path, window):
    """Fallback without a heatmap: the most energetic WINDOW seconds of the audio file (usually the chorus/drop)."""
    import array
    import subprocess

    import imageio_ffmpeg

    rate = 4000
    raw = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(rate), "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    pcm = array.array("h", raw)
    energy = [sum(s * s for s in pcm[i : i + rate]) / rate for i in range(0, len(pcm) - rate, rate)]
    n = int(window)
    first = int(len(energy) * SKIP_INTRO)
    if len(energy) <= n:
        return 0.0
    best = max(range(first, len(energy) - n), key=lambda i: sum(energy[i : i + n]))
    return float(max(0, best - 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=float, default=18)
    args = ap.parse_args()
    tracks = json.loads(TRACKS.read_text(encoding="utf-8"))
    for t in tracks:
        markers = heatmap(t["youtube"])
        result = best_window(markers, args.window)
        if result is None:
            audio = TRACKS.parent.parent / "public" / "music" / t["file"]
            if audio.exists():
                t["start"], t["hookScore"] = loudest_window(audio, args.window), None
                print(f"~ {t['title']}: heatmap yok, ses enerjisinden {int(t['start'])} sn")
            else:
                print(f"! {t['title']}: heatmap yok ve dosya henüz yok (v2/public/music/{t['file']})")
                t.setdefault("start", 0)
            continue
        t["start"], t["hookScore"] = result
        mm, ss = divmod(int(t["start"]), 60)
        print(f"{t['title']}: {mm}:{ss:02d} (yoğunluk {t['hookScore']})")
    TRACKS.write_text(json.dumps(tracks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
