"""Pre-downloads player cutouts, club badges and flags into v2/public/assets and
turns a spec file into render-ready Remotion props.

Usage: python v2/scripts/fetch_assets.py v2/samples/specs/grid.json [more specs...]
Writes v2/samples/<name>.json next to the specs folder.

Spec entity fields: id, name, color, and any of player / team / country (ISO code like "ar", "gb-eng").
"""
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

V2 = Path(__file__).resolve().parent.parent
PUBLIC = V2 / "public"
INDEX = PUBLIC / "assets" / "index.json"
SPORTSDB = "https://www.thesportsdb.com/api/v1/json/123"
UA = {"User-Agent": "ZeynMediaShortsFactory/2.0 (github.com/nukIeer/zeynmedia-shorts-factory)"}


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def get_json(url, **params):
    if "thesportsdb" in url:
        time.sleep(2.2)  # free key allows ~30 requests/minute
    for attempt in range(5):
        r = requests.get(url, params=params, headers=UA, timeout=30)
        if r.status_code == 429:
            time.sleep(15 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"rate limited: {url}")


def download(url, dest_stem):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    ext = ".png" if r.content[:8] == b"\x89PNG\r\n\x1a\n" else ".jpg"
    dest = dest_stem.with_suffix(ext)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    return dest


def wikipedia_image(title):
    data = get_json("https://en.wikipedia.org/w/api.php", action="query", format="json", prop="pageimages",
                    piprop="thumbnail", pithumbsize=600, pilicense="any", redirects=1, titles=title)
    for page in data.get("query", {}).get("pages", {}).values():
        if page.get("thumbnail"):
            return page["thumbnail"]["source"]
    return None


def _best(items, name_key, name, keys):
    # Exact-name matches first, then any; within that, the first image key in priority order wins
    exact = [i for i in items if (i.get(name_key) or "").lower() == name.lower()]
    for pool in (exact, items):
        for key in keys:
            for i in pool:
                if i.get(key):
                    return i[key]
    return None


def player_url(name):
    players = get_json(f"{SPORTSDB}/searchplayers.php", p=name).get("player") or []
    return _best(players, "strPlayer", name, ("strCutout", "strRender", "strThumb")) or wikipedia_image(name)


def team_url(name):
    teams = get_json(f"{SPORTSDB}/searchteams.php", t=name).get("teams") or []
    soccer = [t for t in teams if t.get("strSport") == "Soccer"] or teams
    return _best(soccer, "strTeam", name, ("strBadge",)) or wikipedia_image(name)


def resolve(kind, query, index):
    key = f"{kind}:{query}"
    if key in index and (PUBLIC / index[key]).exists():
        return index[key]
    if kind == "flag":
        url = f"https://flagcdn.com/w320/{query.lower()}.png"
    elif kind == "player":
        url = player_url(query)
    else:
        url = team_url(query)
    if not url:
        print(f"  ! {key}: bulunamadı")
        return None
    dest = download(url, PUBLIC / "assets" / f"{kind}s" / slug(query))
    rel = dest.relative_to(PUBLIC).as_posix()
    index[key] = rel
    print(f"  + {key} -> {rel}")
    return rel


def build(spec_path, index):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    props = spec["props"]
    entities = []
    for e in spec["entities"]:
        out = {k: e[k] for k in ("id", "name", "color", "others") if k in e}
        if e.get("player"):
            out["image"] = resolve("player", e["player"], index)
        if e.get("team"):
            out["badge"] = resolve("team", e["team"], index)
        if e.get("country"):
            out["flag"] = resolve("flag", e["country"], index)
        entities.append({k: v for k, v in out.items() if v is not None})
    props["entities"] = entities
    out_path = Path(spec_path).parent.parent / Path(spec_path).name
    out_path.write_text(json.dumps(props, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"= {out_path}")


def main():
    index = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    try:
        for spec in sys.argv[1:]:
            build(spec, index)
    finally:
        INDEX.parent.mkdir(parents=True, exist_ok=True)
        INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
