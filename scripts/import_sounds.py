"""Bir ses paketi klasöründen efekt ve müzikleri otomatik seçip assets/ altına koyar.

Kullanım: python scripts/import_sounds.py "G:\\Downloads\\paket" [--per-kind 4] [--music 10]
Dosya adına göre sınıflar (whoosh/click/impact/win), 25 sn'den uzunları müzik sayar.
"""
import argparse
import random
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
EXT = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aiff", ".aif"}
KINDS = {
    "whoosh": r"whoosh|swoosh|woosh|swish|swipe|sweep|whip|transition|riser",
    "tick": r"click|tick|tap|blip|select|button|\bui\b|pop|switch",
    "impact": r"impact|\bhit|boom|thud|punch|slam|bass.?drop|explosion|stomp",
    "win": r"win|success|level.?up|complete|achievement|reward|victory|tada|chime|coin|correct",
}
MAX_SFX_S = 2.5


def duration(path):
    out = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def convert(src, dst, max_s=None):
    fade = f"afade=t=out:st={max(0.0, max_s - 0.3):.2f}:d=0.3," if max_s else ""
    trim = ["-t", f"{max_s:.2f}"] if max_s else []
    trim += ["-af", f"{fade}loudnorm=I=-16"]
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(src), *trim, "-ar", "44100", "-ac", "2", "-b:a", "192k", str(dst)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack")
    ap.add_argument("--per-kind", type=int, default=4)
    ap.add_argument("--music", type=int, default=10)
    args = ap.parse_args()

    files = [p for p in Path(args.pack).rglob("*") if p.suffix.lower() in EXT]
    print(f"{len(files)} ses dosyası bulundu")
    sfx_dir, music_dir = ROOT / "assets" / "sfx", ROOT / "assets" / "music"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    music_dir.mkdir(parents=True, exist_ok=True)

    lengths = {p: duration(p) for p in files}
    for kind, pattern in KINDS.items():
        matches = [p for p in files if re.search(pattern, p.stem.lower().replace("_", " ")) and 0 < lengths[p] <= 6]
        random.shuffle(matches)
        for i, src in enumerate(matches[: args.per_kind], 1):
            convert(src, sfx_dir / f"{kind}_{i}.mp3", max_s=min(MAX_SFX_S, lengths[src]))
        print(f"{kind}: {min(len(matches), args.per_kind)} / {len(matches)} aday")

    songs = sorted((p for p in files if lengths[p] >= 25), key=lambda p: -lengths[p])[: args.music]
    for i, src in enumerate(songs, 1):
        convert(src, music_dir / f"track_{i}.mp3")
    print(f"müzik: {len(songs)}")


if __name__ == "__main__":
    main()
