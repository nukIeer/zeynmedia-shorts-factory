import base64
import json
import subprocess
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

from audio import audio_inputs

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "studio" / "index.html"

FPS = 30
SCALE = 3  # 360x640 stage -> 1080x1920
INTRO_S = 0.6
OUTRO_S = 2.5


def build_config(content, duration):
    return {
        "headerTitle": content["headerTitle"],
        "headerSubtitle": content["headerSubtitle"],
        "players": {
            pid: {k: p.get(k, "") for k in ("name", "searchName", "logo", "image", "color")}
            for pid, p in content["players"].items()
        },
        "statsData": content["statsData"],
        "maxPlayers": len(content["players"]),
        "duration": duration,
        "apiKey": "",
        "aiPrompt": "",
        **content.get("style", {}),
    }


def render_video(content, out_path, duration):
    config = build_config(content, duration)
    total_s = INTRO_S + duration + OUTRO_S
    audio_args, afilter, aout, adesc = audio_inputs(content, duration, INTRO_S, total_s)

    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-"]
    cmd += audio_args
    cmd += [
        "-filter_complex", afilter, "-map", "0:v", "-map", aout, "-t", f"{total_s:.2f}",
        "-vf", "scale=1080:1920:flags=lanczos,setsar=1",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path),
    ]
    print(f"[render] ses -> {adesc}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--disable-web-security", "--font-render-hinting=none"])
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.add_init_script(f"window.__RENDER_CONFIG__ = {json.dumps(config)};")
        page.goto(STUDIO.as_uri(), wait_until="networkidle", timeout=120_000)
        page.wait_for_function("window.__configLoaded === true && typeof window.__seek === 'function'", timeout=120_000)
        page.evaluate("document.fonts.ready")
        page.wait_for_function(
            "Array.from(document.querySelectorAll('#stage img')).every(i => i.complete)", timeout=60_000
        )
        page.wait_for_timeout(1000)

        box = page.locator("#stage").bounding_box()
        clip = {"x": box["x"], "y": box["y"], "width": 360, "height": 640, "scale": SCALE}
        cdp = page.context.new_cdp_session(page)
        steps = page.evaluate("window.__steps")

        def grab():
            shot = cdp.send(
                "Page.captureScreenshot",
                {"format": "jpeg", "quality": 95, "clip": clip, "captureBeyondViewport": False},
            )
            return base64.b64decode(shot["data"])

        frame_ms = 1000 / FPS
        n_intro, n_anim, n_outro = round(INTRO_S * FPS), round(duration * FPS), round(OUTRO_S * FPS)
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            page.evaluate("window.__seek(0, 0)")
            first = grab()
            for _ in range(n_intro):
                proc.stdin.write(first)
            previews = {n_anim // 4: "25", n_anim // 2: "50", n_anim: "100"}
            for i in range(1, n_anim + 1):
                t = steps * i / n_anim
                page.evaluate(f"window.__seek({t}, {frame_ms})")
                frame = grab()
                proc.stdin.write(frame)
                if i in previews:
                    Path(f"{out_path.with_suffix('')}-preview-{previews[i]}.jpg").write_bytes(frame)
                if i % (FPS * 5) == 0:
                    print(f"[render] {i}/{n_anim} kare")
            for _ in range(n_outro):
                page.evaluate(f"window.__seek({steps}, {frame_ms})")
                proc.stdin.write(grab())
        finally:
            proc.stdin.close()
            proc.wait()
            browser.close()

    if proc.returncode != 0:
        raise RuntimeError("ffmpeg başarısız oldu")
    return out_path
