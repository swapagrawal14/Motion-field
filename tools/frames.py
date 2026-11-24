#!/usr/bin/env python3
"""Turn a video (or the built-in demo turntable) into a scroll-scrub frame sequence.

    python3 tools/frames.py video hero.mp4 --out recipes/scroll-scrub-hero/frames --count 24
    python3 tools/frames.py demo --out recipes/scroll-scrub-hero/frames --count 24 --width 720

Writes f-000.webp … f-023.webp, poster.webp and manifest.json:

    { "width": 720, "height": 450, "count": 24, "frames": ["f-000.webp", …] }

Video mode needs ffmpeg + ffprobe on PATH. Demo mode needs Playwright (chromium) and Pillow,
and renders a deterministic 3D dot torus — useful when you have no footage yet.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEMO_HTML = r"""<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#070d1a;overflow:hidden}
canvas{display:block}</style><canvas id="c"></canvas><script>
const c = document.getElementById('c'), ctx = c.getContext('2d');
let W = 720, H = 450;
const TAU = Math.PI * 2;
function frame(i, n) {
  const t = i / n;
  ctx.clearRect(0, 0, W, H);
  const bg = ctx.createRadialGradient(W * 0.5, H * 0.46, 20, W * 0.5, H * 0.5, W * 0.72);
  bg.addColorStop(0, '#123a7a'); bg.addColorStop(0.55, '#0a1630'); bg.addColorStop(1, '#070d1a');
  ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

  const R = Math.min(W, H) * 0.30, r = R * 0.42;
  const ay = t * TAU, ax = 0.55 + Math.sin(t * TAU) * 0.12;
  const ca = Math.cos(ay), sa = Math.sin(ay), cb = Math.cos(ax), sb = Math.sin(ax);
  const f = Math.min(W, H) * 1.6;
  const pts = [];
  const NU = 84, NV = 34;
  for (let iu = 0; iu < NU; iu++) {
    const u = iu / NU * TAU;
    for (let iv = 0; iv < NV; iv++) {
      const v = iv / NV * TAU;
      const rr = R + r * Math.cos(v);
      let x = rr * Math.cos(u), y = rr * Math.sin(u), z = r * Math.sin(v);
      let x1 = x * ca + z * sa, z1 = -x * sa + z * ca;
      let y1 = y * cb - z1 * sb, z2 = y * sb + z1 * cb;
      const s = f / (f - z2);
      pts.push({ x: W / 2 + x1 * s, y: H / 2 + y1 * s, z: z2, s, u, v });
    }
  }
  pts.sort((a, b) => a.z - b.z);
  const zmin = pts[0].z, zmax = pts[pts.length - 1].z, zr = Math.max(0.001, zmax - zmin);
  for (const p of pts) {
    const depth = (p.z - zmin) / zr;              // 0 far → 1 near
    const a = 0.18 + depth * 0.72;
    const rad = Math.max(0.25, (0.9 + depth * 2.4) * p.s);
    const g = Math.round(120 + depth * 135);
    ctx.beginPath();
    ctx.fillStyle = `rgba(${Math.round(40 + depth * 120)}, ${g}, 255, ${a.toFixed(3)})`;
    ctx.arc(p.x, p.y, rad, 0, TAU);
    ctx.fill();
  }
  // specular band
  const gl = ctx.createRadialGradient(W * 0.5, H * 0.42, 4, W * 0.5, H * 0.46, R * 1.5);
  gl.addColorStop(0, 'rgba(143,239,255,0.20)'); gl.addColorStop(1, 'rgba(143,239,255,0)');
  ctx.fillStyle = gl; ctx.fillRect(0, 0, W, H);
  return true;
}
window.renderFrame = (i, n) => frame(i, n);
window.setSize = (w, h) => { W = w; H = h; c.width = w; c.height = h; };
</script>"""


def video_frames(src: Path, out: Path, count: int, width: int) -> None:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        sys.exit("video mode needs ffmpeg and ffprobe on PATH (or use `demo` mode)")
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(src)
    ]).decode().strip())
    fps = max(1.0, count / max(dur, 0.001))
    tmp = Path(tempfile.mkdtemp(prefix="frames-"))
    subprocess.check_call([
        "ffmpeg", "-v", "error", "-i", str(src),
        "-vf", f"fps={fps:.4f},scale={width}:-2:flags=lanczos",
        "-q:v", "4", str(tmp / "f-%03d.png"),
    ])
    pngs = sorted(tmp.glob("f-*.png"))[:count]
    _write(pngs, out, width)


def demo_frames(out: Path, count: int, width: int) -> None:
    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image
    except ImportError:
        sys.exit("demo mode needs: pip install playwright pillow && python3 -m playwright install chromium")
    height = round(width * 450 / 720)
    tmp = Path(tempfile.mkdtemp(prefix="frames-"))
    (tmp / "index.html").write_text(DEMO_HTML, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        page.goto((tmp / "index.html").as_uri())
        page.evaluate(f"setSize({width}, {height})")
        for i in range(count):
            page.evaluate(f"renderFrame({i}, {count})")
            page.screenshot(path=str(tmp / f"f-{i:03d}.png"))
        browser.close()
    _write(sorted(tmp.glob("f-*.png")), out, width)


def _write(pngs, out: Path, width: int) -> None:
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    names = []
    for i, png in enumerate(pngs):
        name = f"f-{i:03d}.webp"
        im = Image.open(png).convert("RGB")
        im.save(out / name, "WEBP", quality=72, method=6)
        names.append(name)
    poster = Image.open(pngs[0]).convert("RGB")
    poster.save(out / "poster.webp", "WEBP", quality=80, method=6)
    w, h = Image.open(out / names[0]).size
    (out / "manifest.json").write_text(
        json.dumps({"width": w, "height": h, "count": len(names), "frames": names}, indent=1), encoding="utf-8"
    )
    total = sum((out / n).stat().st_size for n in names) / 1024
    print(f"wrote {len(names)} frames to {out}  ({w}x{h}, {total:.0f} KB total + poster)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a scroll-scrub WebP frame sequence.")
    ap.add_argument("mode", choices=["video", "demo"], help="`video <file>` (ffmpeg) or `demo` (built-in turntable)")
    ap.add_argument("source", nargs="?", help="video file for `video` mode")
    ap.add_argument("--out", required=True, help="output folder for the frames")
    ap.add_argument("--count", type=int, default=24, help="number of frames (default 24)")
    ap.add_argument("--width", type=int, default=720, help="frame width (default 720)")
    a = ap.parse_args()
    out = Path(a.out)
    if a.mode == "video":
        if not a.source:
            sys.exit("video mode needs a source file")
        video_frames(Path(a.source), out, a.count, a.width)
    else:
        demo_frames(out, a.count, a.width)


if __name__ == "__main__":
    main()
