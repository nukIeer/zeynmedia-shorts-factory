import base64
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


def wikipedia_image(title, lang="en"):
    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "thumbnail",
        "pithumbsize": 500,
        "redirects": 1,
        "titles": title,
    }
    try:
        r = requests.get(f"https://{lang}.wikipedia.org/w/api.php", params=params, headers=UA, timeout=30)
        r.raise_for_status()
        for page in r.json().get("query", {}).get("pages", {}).values():
            src = page.get("thumbnail", {}).get("source")
            if src:
                return src
    except requests.RequestException as e:
        print(f"[assets] wikipedia hatası {title}: {e}")
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


def enrich_players(players):
    for pid, p in players.items():
        search = p.get("searchName") or p["name"]
        image_url = wikipedia_image(search) or sportsdb_image(search)
        p["image"] = _data_url(image_url) if image_url else ""

        country = (p.get("country") or "").lower()
        if len(country) == 2 and country.isalpha():
            p["logo"] = _data_url(f"https://flagcdn.com/w160/{urllib.parse.quote(country)}.png")
        else:
            p["logo"] = p["image"]
        print(f"[assets] {pid} {search}: image={'ok' if p['image'] else 'yok'} logo={'ok' if p['logo'] else 'yok'}")
    return players
