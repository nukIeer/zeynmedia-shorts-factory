import json
import os
import random
import re
import time

import requests

NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

LANG_NAMES = {"tr": "Turkish", "en": "English"}

PROMPT = """You produce data for a vertical "bar chart race" YouTube Short.
Category: {category}
{topic_line}
Recently used topics (do NOT repeat these): {recent}

Rules:
- Pick 4 to 6 well-known competitors (people, clubs, countries or brands) for a specific, catchy comparison.
- Use 6 to 10 time steps (years or seasons), chronological.
- statsData values are the INCREMENT gained in that step (not cumulative), non-negative numbers.
  Use real-world figures as accurately as you know them. No leading all-zero row.
- headerTitle: max 22 characters, UPPERCASE. headerSubtitle: max 32 characters, UPPERCASE.
- player "name": short display name (max 12 chars). "searchName": exact English Wikipedia article title.
- "country": ISO 3166-1 alpha-2 lowercase code of the competitor's country (or null if not applicable).
- "color": a vivid hex color that matches the competitor (club/brand/flag colour), all distinct.
- All on-screen and YouTube text in {lang}.
- youtube.title: max 90 chars, hooky, ends with " #shorts". youtube.description: 2-4 sentences + 5 hashtags.
  youtube.tags: 12-20 SEO keywords (no '#').

Return ONLY valid JSON, no markdown, exactly this shape:
{{
  "topic": "short english description of the topic",
  "headerTitle": "...",
  "headerSubtitle": "...",
  "players": {{
    "p1": {{"name": "...", "searchName": "...", "country": "ar", "color": "#2563eb"}}
  }},
  "statsData": [{{"label": "2018", "p1": 12}}],
  "youtube": {{"title": "...", "description": "...", "tags": ["..."]}}
}}"""


def _extract_json(text):
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model yanıtında JSON bulunamadı")
    return json.loads(text[start : end + 1])


def _validate(data):
    players = data.get("players") or {}
    rows = data.get("statsData") or []
    if not (2 <= len(players) <= 10) or len(rows) < 3:
        raise ValueError("Yetersiz oyuncu/veri")
    for row in rows:
        row["label"] = str(row.get("label", ""))
        for pid in players:
            try:
                row[pid] = max(0.0, float(row.get(pid, 0) or 0))
            except (TypeError, ValueError):
                row[pid] = 0.0
    for pid, p in players.items():
        p["name"] = str(p.get("name") or pid)[:16]
        p.setdefault("searchName", p["name"])
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(p.get("color", ""))):
            p["color"] = "#%06x" % random.randint(0x202020, 0xEEEEEE)
    yt = data.setdefault("youtube", {})
    title = str(yt.get("title") or data.get("headerTitle", "Bar Chart Race")).strip()
    if "#shorts" not in title.lower():
        title = f"{title[:90]} #shorts"
    yt["title"] = title[:100]
    yt["description"] = str(yt.get("description") or title)
    yt["tags"] = [str(t).strip("# ")[:30] for t in (yt.get("tags") or []) if str(t).strip()][:25]
    return data


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _call_nim(prompt):
    model = os.environ.get("NIM_MODEL") or "meta/llama-3.3-70b-instruct"
    resp = requests.post(
        NIM_URL,
        headers={"Authorization": f"Bearer {os.environ['NVIDIA_API_KEY']}", "Accept": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "top_p": 0.95,
            "max_tokens": 3000,
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _gemini_text_models():
    """Currently available text models, flash/lite first (older names get retired)."""
    try:
        r = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
            params={"pageSize": 200},
            timeout=30,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"[generate] model listesi alınamadı: {e}")
        return []
    skip = ("image", "tts", "audio", "live", "embedding", "vision", "robotics", "computer", "learnlm", "gemma")
    names = [
        m["name"].removeprefix("models/")
        for m in r.json().get("models", [])
        if "generateContent" in m.get("supportedGenerationMethods", [])
        and "gemini" in m["name"]
        and not any(s in m["name"] for s in skip)
    ]
    names.sort(reverse=True)
    names.sort(key=lambda n: ("flash" not in n, "preview" in n or "exp" in n))
    print(f"[generate] mevcut Gemini modelleri: {names[:8]}")
    return names


def _call_gemini(prompt):
    models = [m for m in [os.environ.get("GEMINI_MODEL"), "gemini-flash-latest", *_gemini_text_models()] if m]
    last = None
    for model in list(dict.fromkeys(models))[:6]:
        config = {"temperature": 0.8, "responseMimeType": "application/json"}
        for attempt in range(2):
            try:
                resp = requests.post(
                    GEMINI_URL.format(model=model),
                    headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": config},
                    timeout=90,
                )
            except requests.RequestException as e:
                last = f"Gemini {model}: {e}"
                print(f"[generate] {last[:160]}")
                continue
            if resp.ok:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            last = f"Gemini {model} {resp.status_code}: {resp.text[:300]}"
            print(f"[generate] {last[:160]}")
            if resp.status_code not in (429, 500, 502, 503, 504):
                break
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(last)


def generate_content(category, recent_topics, topic=None):
    call = _call_nim if os.environ.get("NVIDIA_API_KEY") else _call_gemini
    print(f"[generate] sağlayıcı: {'NVIDIA NIM' if call is _call_nim else 'Gemini'}")
    lang = LANG_NAMES.get(os.environ.get("CONTENT_LANG", "tr"), "Turkish")
    prompt = PROMPT.format(
        category=category,
        topic_line=f"Specific topic requested: {topic}" if topic else "Choose a specific topic yourself.",
        recent=", ".join(recent_topics[-30:]) or "none",
        lang=lang,
    )

    last_err = None
    for attempt in range(2):
        text = call(prompt)
        try:
            return _validate(_extract_json(text))
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            print(f"[generate] deneme {attempt + 1} başarısız: {e}")
    raise RuntimeError(f"Model geçerli içerik üretemedi: {last_err}")
