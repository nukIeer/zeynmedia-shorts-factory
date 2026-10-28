# ZeynMedia Shorts Factory

Tam otomatik **Bar Chart Race YouTube Shorts** fabrikası. GitHub Actions günde 3 kez çalışır:

1. **NVIDIA NIM** (build.nvidia.com) rastgele bir kategori için konu, veri, başlık, açıklama ve etiketleri üretir
2. Oyuncu/şirket görselleri Wikipedia'dan, bayraklar flagcdn'den çekilir
3. `studio/index.html` (Bar Chart Race Studio) headless Chromium'da **kare kare** render edilir → 1080x1920, 30fps MP4
4. Video **YouTube Data API (OAuth)** ile otomatik yüklenir
5. Konu `data/history.json`'a yazılır, böylece aynı konu tekrar edilmez

## Kurulum

### 1. Secrets (Settings → Secrets and variables → Actions → Secrets)

| Secret | Açıklama |
|---|---|
| `NVIDIA_API_KEY` | build.nvidia.com'dan alınan `nvapi-...` key (öncelikli) |
| `GEMINI_API_KEY` | Google AI Studio Gemini key'i (NVIDIA yoksa bu kullanılır) |
| `YT_CLIENT_ID` | Google Cloud OAuth client ID |
| `YT_CLIENT_SECRET` | Google Cloud OAuth client secret |
| `YT_REFRESH_TOKEN` | Aşağıdaki script ile üretilir |

Hiç AI key'i yoksa `config/presets.json` içindeki hazır içerikler sırayla kullanılır. `YT_REFRESH_TOKEN` yoksa video yalnızca üretilir ve Actions artifact olarak indirilebilir.

### 2. YouTube OAuth

1. [Google Cloud Console](https://console.cloud.google.com/) → yeni proje → **YouTube Data API v3**'ü etkinleştir
2. **OAuth consent screen** → External → kendi Google hesabını *Test users*'a ekle → sonra **Publish app** (yayınlanmazsa refresh token 7 günde ölür)
3. **Credentials → Create credentials → OAuth client ID → Desktop app** → JSON'u indir
4. Lokalde:
   ```bash
   pip install google-auth-oauthlib
   python scripts/get_refresh_token.py client_secret.json
   ```
   Tarayıcıda kanalın hesabıyla giriş yap, çıkan 3 değeri Secrets'a ekle.

> Not: Doğrulanmamış (audit edilmemiş) API projelerinden yüklenen videolar YouTube tarafından **private** olarak kilitlenebilir. Public yükleme için [YouTube API audit formu](https://support.google.com/youtube/contact/yt_api_form) doldurulmalı.

### 3. Opsiyonel Variables (Settings → Variables)

| Variable | Varsayılan | Açıklama |
|---|---|---|
| `NIM_MODEL` | `openai/gpt-oss-20b` | build.nvidia.com'daki herhangi bir chat modeli |
| `CONTENT_LANG` | `tr` | `tr` veya `en` |
| `YT_PRIVACY` | `public` | `public` / `unlisted` / `private` |

### 4. Müzik (opsiyonel)

`assets/music/` klasörüne telifsiz `.mp3` dosyaları koy; her videoda rastgele biri seçilir. Boşsa video sessiz olur.

## Çalıştırma

- **Otomatik:** 07:00, 13:00, 18:00 UTC (`.github/workflows/shorts.yml` içindeki cron'dan değiştir)
- **Manuel:** Actions → *Shorts Factory* → *Run workflow* (konu, görünürlük, sadece-render, örnek veri seçenekleri)

Lokal test:
```bash
pip install -r requirements.txt && python -m playwright install chromium
python factory/main.py --sample --no-upload      # NIM'siz örnek video
NVIDIA_API_KEY=nvapi-... python factory/main.py --no-upload --topic "Messi vs Ronaldo Şampiyonlar Ligi golleri"
```

Konu kategorileri ve arka plan renkleri: `config/topics.json`.

Studio'yu tarayıcıda manuel kullanmak için `studio/index.html`'i açman yeterli.
