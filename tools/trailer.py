#!/usr/bin/env python3
"""Record a 15-second site trailer — a title card, a scroll-through, an end card.

    python3 tools/trailer.py http://localhost:8080/ --out trailer.webm
    python3 tools/trailer.py templates/portfolio/ --out trailer.mp4 --title "ACME" --subtitle "Design that moves"
    python3 tools/trailer.py http://localhost:8080/ --out trailer.mp4 --duration 15 --width 1280 --height 720

Output is WebM from Playwright; converted to MP4 when ffmpeg is on PATH and --out ends in .mp4.
The title card uses the page's own accent colour when it can read one, otherwise a neutral dark card.

No audio (add music in an editor). Keep the scroll slow enough to read — 15 s is a trailer, not a tour.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sys.exit("trailer.py needs Playwright: pip install playwright && python3 -m playwright install chromium")

CARD_CSS = """
#mf-trailer-card { position: fixed; inset: 0; z-index: 2147483000; display: grid; place-content: center; gap: 10px;
  text-align: center; background: #070d1a; color: #e8eff9; font: 600 clamp(36px, 8vw, 110px)/1 -apple-system,
  "Segoe UI", Inter, sans-serif; letter-spacing: -.04em; transition: opacity .5s ease; padding: 6vw; }
#mf-trailer-card small { font: 500 clamp(11px, 1.4vw, 16px)/1.4 ui-monospace, monospace; letter-spacing: .18em;
  text-transform: uppercase; opacity: .6; }
#mf-trailer-card.is-out { opacity: 0; pointer-events: none; }
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Record a 15 s scroll trailer of a page.")
    ap.add_argument("target", help="URL or local file/folder (served automatically)")
    ap.add_argument("--out", default="trailer.webm", help="output video (mp4 if ffmpeg, else webm)")
    ap.add_argument("--title", default="", help="title card text (default: page <title>)")
    ap.add_argument("--subtitle", default="", help="title card subtitle (default: page description)")
    ap.add_argument("--duration", type=float, default=15, help="total seconds (default 15)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()

    url, httpd = a.target, None
    if not url.startswith(("http://", "https://", "file://")):
        if not Path(url).exists():
            ap.error(f"not a URL and not a local path: {url}")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from qa import serve_local
        url, httpd = serve_local(url)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="trailer-"))
    hold_title, hold_end = 1.6, 1.8
    scroll_s = max(4.0, a.duration - hold_title - hold_end)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": a.width, "height": a.height}, device_scale_factor=1,
                                  record_video_dir=str(tmp), record_video_size={"width": a.width, "height": a.height})
        page = ctx.new_page()
        page.goto(url, wait_until="load", timeout=a.timeout * 1000)
        page.wait_for_timeout(1200)

        title = a.title or page.title() or "Motion Field"
        subtitle = a.subtitle or page.evaluate("() => document.querySelector('meta[name=description]')?.content || ''")
        accent = page.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#3fdcff'")
        page.add_style_tag(content=CARD_CSS)
        page.evaluate("""({ title, subtitle, accent }) => {
          const card = document.createElement('div');
          card.id = 'mf-trailer-card';
          card.innerHTML = `<div>${title}</div><small>${subtitle}</small>`;
          card.style.borderBottom = `6px solid ${accent}`;
          document.body.appendChild(card);
        }""", {"title": title, "subtitle": subtitle, "accent": accent})

        page.wait_for_timeout(int(hold_title * 1000))
        page.evaluate("() => document.getElementById('mf-trailer-card').classList.add('is-out')")
        page.wait_for_timeout(500)
        page.evaluate("() => document.getElementById('mf-trailer-card').remove()")

        total = page.evaluate("() => Math.max(0, document.documentElement.scrollHeight - innerHeight)")
        steps = 110
        for i in range(steps + 1):
            p = i / steps
            eased = p * p * (3 - 2 * p)  # smoothstep: slow start, slow end
            page.evaluate("""y => {
              if (window.lenis && window.lenis.scrollTo) window.lenis.scrollTo(y, { immediate: true });
              else window.scrollTo({ top: y, behavior: 'instant' });
            }""", total * eased)
            page.wait_for_timeout(int(scroll_s * 1000 / steps))

        # end card
        page.evaluate("""({ accent }) => {
          const card = document.createElement('div');
          card.id = 'mf-trailer-card';
          card.innerHTML = `<div>Made with Motion Field</div><small>Recipes for agents · vanilla HTML/CSS/JS</small>`;
          card.style.borderTop = `6px solid ${accent}`;
          document.body.appendChild(card);
        }""", {"accent": accent})
        page.wait_for_timeout(int(hold_end * 1000))

        video = page.video
        ctx.close()
        src = Path(video.path()) if video else None
        browser.close()

    if httpd:
        httpd.shutdown()
    if not src or not src.exists():
        raise SystemExit("no video was recorded")
    if shutil.which("ffmpeg") and out.suffix.lower() == ".mp4":
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(out)], check=False)
        if out.exists():
            src.unlink(missing_ok=True)
            print("wrote", out, f"({out.stat().st_size / 1024 / 1024:.1f} MB)")
            return
    dest = out.with_suffix(".webm")
    shutil.move(str(src), str(dest))
    print("wrote", dest, f"({dest.stat().st_size / 1024 / 1024:.1f} MB)" + ("" if shutil.which("ffmpeg") else "  (install ffmpeg for MP4)"))


if __name__ == "__main__":
    main()
