"""Synthesizes heavy 808 / sub-bass SFX into v2/public/sfx/ so hits cut through phonk music.

Everything is generated from scratch (no samples, no licensing). Re-run to regenerate:
  python v2/scripts/make_bass_sfx.py
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "public" / "sfx"
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(SR * sec)) / SR


def glide_sine(sec, f0, f1, glide):
    t = t_axis(sec)
    f = f1 + (f0 - f1) * np.exp(-t / glide)
    return np.sin(2 * np.pi * np.cumsum(f) / SR), t


def env(t, attack, decay):
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def lowpass(x, cutoff):
    # one-pole, cutoff may be an array (sweeps)
    a = np.exp(-2 * np.pi * np.broadcast_to(cutoff, x.shape) / SR)
    y = np.zeros_like(x)
    prev = 0.0
    for i in range(len(x)):
        prev = (1 - a[i]) * x[i] + a[i] * prev
        y[i] = prev
    return y


def sat(x, drive):
    return np.tanh(x * drive) / np.tanh(drive)


def click(sec=0.012, level=0.5):
    t = t_axis(sec)
    return level * rng.standard_normal(len(t)) * np.exp(-t / 0.002)


def pad(x, sec):
    out = np.zeros(int(SR * sec))
    out[: len(x)] += x[: len(out)]
    return out


def kick808(sec, f0, f1, glide, decay, drive):
    s, t = glide_sine(sec, f0, f1, glide)
    x = sat(s * env(t, 0.002, decay), drive)
    return x + pad(click(), sec)


def bass_hit():
    return kick808(0.7, 170, 48, 0.035, 0.22, 2.2)


def deep_tick():
    s, t = glide_sine(0.18, 260, 95, 0.02)
    return sat(s * env(t, 0.001, 0.045), 1.6) * 0.8 + pad(click(0.006, 0.35), 0.18)


def sub_boom():
    body = kick808(1.8, 120, 38, 0.06, 0.65, 3.0)
    t = t_axis(1.8)
    rumble = lowpass(rng.standard_normal(len(t)), 180) * env(t, 0.005, 0.35) * 3
    return body + rumble


def bass_drop():
    """Long distorted 808 glide down — the phonk 'brrr' for the winner reveal."""
    s, t = glide_sine(2.4, 90, 32, 0.6)
    x = sat(s * env(t, 0.01, 1.1), 4.0)
    return x + pad(click(0.015, 0.6), 2.4)


def sub_whoosh():
    """Filtered-noise swell that sweeps up into a sub thump (overtakes)."""
    sec = 0.75
    t = t_axis(sec)
    rise = np.clip(t / 0.45, 0, 1)
    noise = lowpass(rng.standard_normal(len(t)), 300 + 5200 * rise**2)
    shape = np.where(t < 0.45, rise**2, np.exp(-(t - 0.45) / 0.08))
    x = noise * shape * 0.9
    hit = kick808(sec - 0.42, 140, 45, 0.03, 0.14, 2.0)
    x[int(0.42 * SR) :] += hit[: len(x) - int(0.42 * SR)]
    return x


def riser():
    """Intro: reverse-cymbal style swell with a sub glide up, lands on a hit at 0.9 s."""
    sec = 1.6
    t = t_axis(sec)
    k = np.clip(t / 0.9, 0, 1)
    noise = lowpass(rng.standard_normal(len(t)), 400 + 7000 * k**3) * np.where(t < 0.9, k**3, 0)
    s, _ = glide_sine(sec, 30, 30, 1)
    sub = np.sin(2 * np.pi * np.cumsum(35 + 45 * k) / SR) * np.where(t < 0.9, k**2, 0) * 0.7
    x = noise * 0.8 + sub
    hit = sub_boom()
    x[int(0.9 * SR) :] += hit[: len(x) - int(0.9 * SR)]
    return x


def write(name, x):
    x = x / (np.abs(x).max() + 1e-9) * 0.97
    pcm = (x * 32767).astype("<i2").tobytes()
    dst = OUT / f"{name}.mp3"
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-b:a", "192k", str(dst)],
        input=pcm,
        check=True,
    )
    print("wrote", dst.name)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [
        ("bass_hit", bass_hit),
        ("deep_tick", deep_tick),
        ("sub_boom", sub_boom),
        ("bass_drop", bass_drop),
        ("sub_whoosh", sub_whoosh),
        ("bass_riser", riser),
    ]:
        write(name, fn())
