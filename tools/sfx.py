#!/usr/bin/env python3
"""Motion Field UI sound kit — procedural SFX, no sample files.

    python3 tools/sfx.py --out sfx            # write every .wav
    python3 tools/sfx.py --out sfx --only pop,tick,whoosh
    python3 tools/sfx.py --list
    python3 tools/sfx.py --timeline "0.2:pop,2:whoosh,9.5:chime" --seconds 11 --out soundtrack.wav

`render_timeline()` is what `tools/trailer.py --sfx` and `tools/promo.py` use to score a video: a quiet
procedural pad (`bed()`) plus a sound on every beat (whoosh on a scroll, swish on a zoom, chime on the
end card).

The same recipes are implemented in WebAudio in `assets/ui-sound.js`, so a site can ship zero audio
files and still have pop / tick / whoosh on hover and click. Sound is **muted by default**; the visitor
opts in with the toggle (`data-sfx-toggle`).

Requires numpy for the WAV renderer only — the WebAudio version needs nothing.
"""
from __future__ import annotations

import argparse
import wave
from pathlib import Path

import numpy as np

SR = 44100
_r = np.random.default_rng(7)


def _env(sec, decay):
    t = np.arange(int(sec * SR)) / SR
    return t, np.exp(-t * decay)


def _sine(f, t):
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def pop():
    t, e = _env(.12, 38)
    f = 520 * np.exp(-t * 9) + 180
    return _sine(f, t) * e * .18


def tick():
    t, e = _env(.04, 150)
    return _sine(2500 * np.ones_like(t), t) * e * .08


def whoosh():
    L = int(.45 * SR)
    k = np.convolve(_r.standard_normal(L), np.ones(30) / 30, "same")
    t = np.arange(L) / L
    return k * np.sin(np.pi * t) ** 2 * .5


def plip():
    t, e = _env(.15, 30)
    f = 900 + 1400 * np.exp(-t * 40)
    return _sine(f, t) * e * .12


def boing():
    t, e = _env(.35, 8)
    f = 220 + 120 * np.sin(t * 60) * np.exp(-t * 6)
    return _sine(f, t) * e * .2


def dab():
    t, e = _env(.06, 70)
    return _r.standard_normal(len(t)) * e * .05


def ring():
    t = np.arange(int(.5 * SR)) / SR
    gate = (np.sin(2 * np.pi * 22 * t) > 0).astype(np.float32)
    return (np.sin(2 * np.pi * 1300 * t) + .6 * np.sin(2 * np.pi * 1700 * t)) * gate * np.exp(-t * 1.5) * .07


def success():
    out = np.zeros(int(.5 * SR), np.float32)
    for i, f in enumerate((523.25, 783.99)):
        t, e = _env(.3, 9)
        tone = (_sine(f * np.ones_like(t), t) + .3 * _sine(f * 2 * np.ones_like(t), t)) * e * .12
        start = int(i * .1 * SR)
        L = min(len(tone), len(out) - start)
        out[start:start + L] += tone[:L]
    return out


def error():
    out = np.zeros(int(.4 * SR), np.float32)
    for i, f in enumerate((220, 174.61)):
        t, e = _env(.28, 10)
        tone = _sine(f * np.ones_like(t), t) * e * .12
        start = int(i * .12 * SR)
        L = min(len(tone), len(out) - start)
        out[start:start + L] += tone[:L]
    return out


def chime():
    """End-card chime: a soft major triad, bell-ish partials, long tail."""
    out = np.zeros(int(1.6 * SR), np.float32)
    for i, f in enumerate((659.25, 830.61, 987.77, 1318.5)):
        t, e = _env(1.4, 3.2)
        tone = (_sine(f * np.ones_like(t), t) + .25 * _sine(f * 2.76 * np.ones_like(t), t) * np.exp(-t * 6)) * e * .1
        start = int(i * .07 * SR)
        L = min(len(tone), len(out) - start)
        out[start:start + L] += tone[:L]
    return out


def swish():
    """A short airy swish for zooms and cuts (a quieter, brighter whoosh)."""
    L = int(.3 * SR)
    n = _r.standard_normal(L)
    k = n - np.convolve(n, np.ones(6) / 6, "same")  # high-passed
    t = np.arange(L) / L
    return k * np.sin(np.pi * t) ** 3 * .35


FX = {"pop": pop, "tick": tick, "whoosh": whoosh, "plip": plip, "boing": boing,
      "dab": dab, "ring": ring, "success": success, "error": error, "chime": chime, "swish": swish}


def bed(seconds: float, root: float = 196.0) -> np.ndarray:
    """A quiet procedural pad (I-vi-IV-V) so a trailer is never dead air. Original, no licence needed."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    chords = [(1, 5 / 4, 3 / 2), (5 / 6, 1, 5 / 4), (4 / 3, 5 / 3, 2), (3 / 2, 15 / 8, 9 / 4)]
    bar = max(1.0, seconds / 4) if seconds < 8 else 2.0
    for k in range(int(np.ceil(seconds / bar))):
        a, b = int(k * bar * SR), min(n, int((k + 1) * bar * SR) + int(.25 * SR))
        if a >= n:
            break
        tt = t[a:b] - t[a]
        env = np.minimum(1, tt / .35) * np.minimum(1, (tt[-1] - tt + 1e-3) / .35)
        for r in chords[k % 4]:
            f = root * r
            out[a:b] += (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.003 * tt)) * env * .03
    fade = np.minimum(1, np.minimum(t / 1.0, (seconds - t) / 1.2))
    return out * np.clip(fade, 0, 1)


def render_timeline(events, seconds: float, path: Path, with_bed: bool = True) -> Path:
    """Mix named sounds at times into one WAV. events = [(t_seconds, name, gain), ...]."""
    out = bed(seconds) if with_bed else np.zeros(int(seconds * SR), np.float32)
    out = out.astype(np.float32)
    for t, name, gain in events:
        if name not in FX or t < 0 or t >= seconds:
            continue
        s = FX[name]().astype(np.float32) * gain
        a = int(t * SR)
        L = min(len(s), len(out) - a)
        out[a:a + L] += s[:L]
    peak = float(np.abs(out).max()) or 1.0
    out = out / max(peak, 1.0) * .8 if peak > 1.0 else out / peak * .8
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (out * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def write_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.abs(samples).max()) or 1.0
    pcm = (samples / peak * 0.85 * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the Motion Field UI sound kit as WAV files.")
    ap.add_argument("--out", default="sfx", help="output folder (default sfx/)")
    ap.add_argument("--only", default="", help="comma-separated names (default: all)")
    ap.add_argument("--list", action="store_true", help="list the available sounds and exit")
    ap.add_argument("--timeline", default="", help="t:name[,t:name...] -> one mixed WAV at --out (a file)")
    ap.add_argument("--seconds", type=float, default=10, help="timeline length (default 10)")
    ap.add_argument("--no-bed", action="store_true", help="timeline without the background pad")
    a = ap.parse_args()
    if a.timeline:
        ev = []
        for item in a.timeline.split(","):
            t, name = item.split(":")
            ev.append((float(t), name.strip(), 1.0))
        out = Path(a.out if a.out.endswith(".wav") else a.out + ".wav")
        render_timeline(ev, a.seconds, out, with_bed=not a.no_bed)
        print(f"wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")
        return
    if a.list:
        print(", ".join(FX))
        return
    names = [n.strip() for n in a.only.split(",") if n.strip()] or list(FX)
    for name in names:
        if name not in FX:
            raise SystemExit(f"unknown sound: {name} (available: {', '.join(FX)})")
        out = Path(a.out) / f"{name}.wav"
        write_wav(out, FX[name]())
        print(f"wrote {out}  ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
