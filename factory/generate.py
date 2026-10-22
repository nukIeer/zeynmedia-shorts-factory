import json
import os
import random
import re

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


def generate_content(category, recent_topics, topic=None):
    api_key = os.environ["NVIDIA_API_KEY"]
    model = os.environ.get("NIM_MODEL") or "meta/llama-3.3-70b-instruct"
    lang = LANG_NAMES.get(os.environ.get("CONTENT_LANG", "tr"), "Turkish")
    prompt = PROMPT.format(
        category=category,
        topic_line=f"Specific topic requested: {topic}" if topic else "Choose a specific topic yourself.",
        recent=", ".join(recent_topics[-30:]) or "none",
        lang=lang,
    )

    last_err = None
    for attempt in range(3):
        resp = requests.post(
            NIM_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
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
        text = resp.json()["choices"][0]["message"]["content"]
        try:
            return _validate(_extract_json(text))
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            print(f"[generate] deneme {attempt + 1} başarısız: {e}")
    raise RuntimeError(f"NIM geçerli içerik üretemedi: {last_err}")
