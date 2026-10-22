import argparse
import json
import os
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from assets import enrich_players, pixabay_background  # noqa: E402
from render import render_video  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TOPICS = json.loads((ROOT / "config" / "topics.json").read_text(encoding="utf-8"))
HISTORY = ROOT / "data" / "history.json"
OUT = ROOT / "output"

SAMPLE = {
    "topic": "sample: Messi vs Ronaldo goals",
    "headerTitle": "GOL YARIŞI",
    "headerSubtitle": "MESSI VS RONALDO (2015-2022)",
    "players": {
        "p1": {"name": "Messi", "searchName": "Lionel Messi", "country": "ar", "color": "#60a5fa"},
        "p2": {"name": "Ronaldo", "searchName": "Cristiano Ronaldo", "country": "pt", "color": "#dc2626"},
        "p3": {"name": "Lewandowski", "searchName": "Robert Lewandowski", "country": "pl", "color": "#9f1239"},
        "p4": {"name": "Suarez", "searchName": "Luis Suárez", "country": "uy", "color": "#0ea5e9"},
    },
    "statsData": [
        {"label": str(2015 + i), "p1": a, "p2": b, "p3": c, "p4": d}
        for i, (a, b, c, d) in enumerate(
            [(52, 61, 42, 25), (59, 55, 43, 59), (54, 42, 43, 37), (45, 44, 41, 31), (51, 31, 40, 25), (31, 37, 55, 21), (38, 36, 69, 21), (35, 24, 54, 22)]
        )
    ],
    "youtube": {
        "title": "Messi mi Ronaldo mu? Gol Yarışı 2015-2022 #shorts",
        "description": "Yıllara göre gol sayıları. #messi #ronaldo #futbol #barchartrace #shorts",
        "tags": ["messi", "ronaldo", "bar chart race", "futbol", "gol kralı"],
    },
}


def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def pick_preset(history):
    presets = json.loads((ROOT / "config" / "presets.json").read_text(encoding="utf-8"))
    used = [h["topic"] for h in history]
    unused = [p for p in presets if p["topic"] not in used]
    if unused:
        return random.choice(unused)
    # All used: reuse the one uploaded longest ago
    return min(presets, key=lambda p: max(i for i, t in enumerate(used) if t == p["topic"]))


def slugify(text):
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text[:60] or "short"


def main():
    ap = argparse.ArgumentParser(description="ZeynMedia YouTube Shorts factory")
    ap.add_argument("--topic", default=os.environ.get("INPUT_TOPIC") or None)
    ap.add_argument("--category", default=None)
    ap.add_argument("--privacy", default=os.environ.get("YT_PRIVACY", "public"), choices=["public", "unlisted", "private"])
    ap.add_argument("--no-upload", action="store_true", default=os.environ.get("SKIP_UPLOAD", "").lower() == "true")
    ap.add_argument("--sample", action="store_true", help="NIM yerine örnek veri kullan (test)")
    args = ap.parse_args()

    history = load_history()
    if args.sample:
        content = json.loads(json.dumps(SAMPLE))
    elif not (os.environ.get("NVIDIA_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        print("[main] AI key yok -> hazır içerik (config/presets.json) kullanılıyor")
        content = pick_preset(history)
    else:
        from generate import generate_content

        category = args.category or random.choice(TOPICS["categories"])
        print(f"[main] kategori: {category}")
        try:
            content = generate_content(category, [h["topic"] for h in history], args.topic)
        except Exception as e:
            print(f"[main] AI başarısız ({e}); hazır içeriğe geçiliyor")
            content = pick_preset(history)

    print(f"[main] konu: {content['topic']}")
    print(f"[main] başlık: {content['youtube']['title']}")

    enrich_players(content["players"])
    c1, c2 = random.choice(TOPICS["palettes"])
    content["style"] = {"bgType": "gradient", "bgColor1": c1, "bgColor2": c2}
    bg = pixabay_background(content.get("backgroundQuery") or "")
    if bg:
        content["style"].update({"bgMedia": bg, "bgMediaType": "image"})

    steps = len(content["statsData"])
    duration = max(15.0, min(40.0, steps * 2.4))

    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    video_path = OUT / f"{stamp}-{slugify(content['topic'])}.mp4"
    render_video(content, video_path, duration)
    print(f"[main] video: {video_path} ({video_path.stat().st_size / 1e6:.1f} MB)")

    video_id = None
    if args.no_upload:
        print("[main] yükleme atlandı")
    else:
        from upload import upload_video

        video_id = upload_video(video_path, content["youtube"], privacy=args.privacy)

    meta = {k: v for k, v in content.items() if k not in ("players", "style")}
    meta["players"] = {pid: {k: p.get(k) for k in ("name", "searchName", "country", "color")} for pid, p in content["players"].items()}
    meta["video_id"] = video_id
    video_path.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if not args.sample:
        history.append({
            "date": stamp,
            "topic": content["topic"],
            "title": content["youtube"]["title"],
            "video_id": video_id,
        })
        HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"### {content['youtube']['title']}\n\n- Konu: {content['topic']}\n")
            f.write(f"- YouTube: https://youtube.com/shorts/{video_id}\n" if video_id else "- YouTube: yüklenmedi\n")


if __name__ == "__main__":
    main()
