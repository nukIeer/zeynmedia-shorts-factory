import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSIC_DIR = ROOT / "assets" / "music"
SFX_DIR = ROOT / "assets" / "sfx"
AUDIO_EXT = {".mp3", ".m4a", ".wav", ".ogg", ".flac"}

# Studio animates scores during the last 30% of each step (progress 0.70 -> 1.0)
SCORE_MOVE_START = 0.70
MAX_WHOOSH = 10
SFX_VOLUME = {"tick": 0.35, "whoosh": 0.7, "impact": 0.9, "win": 0.8}


def _files(directory, prefix=""):
    return [p for p in sorted(directory.glob(f"{prefix}*")) if p.suffix.lower() in AUDIO_EXT]


def _ranks(totals):
    order = sorted(totals, key=lambda pid: (-totals[pid], pid))
    return {pid: i for i, pid in enumerate(order)}


def sfx_events(stats, players, duration, intro_s):
    """(seconds, kind) cues: tick per step, whoosh on overtakes, impact+win at the end."""
    steps = len(stats)
    to_sec = lambda t: intro_s + t / steps * duration  # noqa: E731
    totals = {pid: 0.0 for pid in players}
    prev = _ranks(totals)
    events, whooshes = [], []
    for k, row in enumerate(stats):
        for pid in players:
            totals[pid] += float(row.get(pid, 0) or 0)
        ranks = _ranks(totals)
        events.append((to_sec(k + SCORE_MOVE_START), "tick"))
        if k > 0 and ranks != prev:
            whooshes.append((to_sec(k + 0.82), "whoosh"))
        prev = ranks
    if len(whooshes) > MAX_WHOOSH:
        whooshes = sorted(random.sample(whooshes, MAX_WHOOSH))
    events += whooshes
    events += [(to_sec(steps), "impact"), (to_sec(steps) + 0.15, "win")]
    return sorted(events)


def audio_inputs(content, duration, intro_s, total_s):
    """Returns (ffmpeg input args, filter_complex, output label, description); inputs start at index 1."""
    tracks = _files(MUSIC_DIR)
    music = random.choice(tracks) if tracks else None
    pools = {kind: _files(SFX_DIR, kind) for kind in SFX_VOLUME}

    args, labels, parts = [], [], []
    if music:
        args += ["-stream_loop", "-1", "-i", str(music)]
        vol = 0.55 if any(pools.values()) else 0.8
        parts.append(f"[1:a]atrim=0:{total_s:.2f},afade=t=in:d=0.5,afade=t=out:st={total_s - 1.5:.2f}:d=1.5,volume={vol}[m]")
    else:
        args += ["-f", "lavfi", "-t", f"{total_s:.2f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
        parts.append("[1:a]anull[m]")
    labels.append("[m]")

    used = 0
    for i, (sec, kind) in enumerate(sfx_events(content["statsData"], content["players"], duration, intro_s)):
        if not pools[kind] or sec >= total_s:
            continue
        idx = 2 + used
        args += ["-i", str(random.choice(pools[kind]))]
        ms = int(sec * 1000)
        parts.append(
            f"[{idx}:a]aformat=sample_rates=44100:channel_layouts=stereo,"
            f"volume={SFX_VOLUME[kind]},adelay={ms}|{ms}[s{used}]"
        )
        labels.append(f"[s{used}]")
        used += 1

    mix = f"amix=inputs={len(labels)}:normalize=0:duration=first," if len(labels) > 1 else ""
    parts.append(f"{''.join(labels)}{mix}alimiter=limit=0.95[aout]")
    desc = f"müzik: {music.name if music else 'yok'}, efekt: {used}"
    return args, ";".join(parts), "[aout]", desc
