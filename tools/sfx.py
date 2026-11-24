#!/usr/bin/env python3
"""Motion Field UI sound kit — procedural SFX, no sample files.

    python3 tools/sfx.py --out sfx            # write every .wav
    python3 tools/sfx.py --out sfx --only pop,tick,whoosh
    python3 tools/sfx.py --list

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


FX = {"pop": pop, "tick": tick, "whoosh": whoosh, "plip": plip, "boing": boing,
      "dab": dab, "ring": ring, "success": success, "error": error}


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
    a = ap.parse_args()
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
