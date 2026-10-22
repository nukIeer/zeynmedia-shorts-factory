import base64
import os
import random
import re
import urllib.parse

import requests

UA = {"User-Agent": "ZeynMediaShortsFactory/1.0 (https://github.com/nukIeer/zeynmedia-shorts-factory)"}


def _data_url(url):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "image/jpeg").split(";")[0]
        if not ctype.startswith("image/"):
            return ""
        return f"data:{ctype};base64,{base64.b64encode(r.content).decode()}"
    except requests.RequestException as e:
        print(f"[assets] indirilemedi {url}: {e}")
        return ""


def _wiki_pages(params, lang):
    base = {"action": "query", "format": "json", "prop": "pageimages", "piprop": "thumbnail",
            "pithumbsize": 500, "pilicense": "any", "redirects": 1}
    try:
        r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params={**base, **params}, headers=UA, timeout=30)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {}).values()
        return sorted(pages, key=lambda p: p.get("index", 0))
    except (requests.RequestException, ValueError) as e:
        print(f"[assets] wikipedia hatası: {e}")
        return []


def wikipedia_image(title, lang="en"):
    # Exact title first; fall back to search, which also resolves disambiguation pages
    for params in ({"titles": title}, {"generator": "search", "gsrsearch": title, "gsrlimit": 5}):
        for page in _wiki_pages(params, lang):
            src = page.get("thumbnail", {}).get("source")
            if src:
                return src
    return None


def sportsdb_image(name):
    try:
        r = requests.get(
            "https://www.thesportsdb.com/api/v1/json/3/searchplayers.php",
            params={"p": name},
            headers=UA,
            timeout=30,
        )
        hit = (r.json().get("player") or [None])[0]
        if hit:
            return hit.get("strCutout") or hit.get("strThumb")
    except (requests.RequestException, ValueError):
        pass
    return None


def pixabay_background(query):
    key = os.environ.get("PIXABAY_API_KEY")
    if not key or not query:
        return ""
    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={"key": key, "q": query[:100], "image_type": "photo", "orientation": "vertical",
                    "safesearch": "true", "per_page": 20, "order": "popular"},
            timeout=30,
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
    except (requests.RequestException, ValueError) as e:
        print(f"[assets] pixabay hatası: {e}")
        return ""
    if not hits:
        print(f"[assets] pixabay sonuç yok: {query}")
        return ""
    hit = random.choice(hits[:10])
    print(f"[assets] arka plan: '{query}' -> {hit.get('pageURL')}")
    return _data_url(hit["largeImageURL"])


def enrich_players(players):
    for pid, p in players.items():
        search = p.get("searchName") or p["name"]
        image_url = wikipedia_image(search) or sportsdb_image(search)
        p["image"] = _data_url(image_url) if image_url else ""

        country = (p.get("country") or "").lower()
        if re.fullmatch(r"[a-z]{2}(-[a-z]{3})?", country):
            p["logo"] = _data_url(f"https://flagcdn.com/w160/{urllib.parse.quote(country)}.png")
        else:
            p["logo"] = p["image"]
        print(f"[assets] {pid} {search}: image={'ok' if p['image'] else 'yok'} logo={'ok' if p['logo'] else 'yok'}")
    return players
