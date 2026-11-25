#!/usr/bin/env python3
"""Record a short site trailer — a title card, a scroll-through, an end card — for any aspect ratio.

    python3 tools/trailer.py http://localhost:8080/ --out trailer.webm
    python3 tools/trailer.py templates/portfolio/ --out trailer.mp4 --title "ACME" --subtitle "Design that moves"
    python3 tools/trailer.py templates/event/ --out reel.mp4 --aspect 9:16 --sfx --end-cta "RSVP at fieldday.club"
    python3 tools/trailer.py site/ --out promo.mp4 --aspect 1:1 --bg "#F3EBDD" --fg "#2B211A" \\
        --font "Playfair Display" --accent "#D98E2B" --audio music.mp3 --sfx

Aspect presets (--aspect):  16:9 → 1280x720 (default)  ·  9:16 → 1080x1920 Reels/Shorts/TikTok (mobile layout)
                            ·  1:1 → 1080x1080.  --width/--height still override the output size.
Brand cards: --bg / --fg / --accent take a hex colour or "page" (read the page's own --bg / --ink / --accent
tokens); --font takes a family name (Google Fonts are fetched when reachable). Defaults keep the old look
(dark navy #070d1a card, the page's --accent).
Sound: --sfx scores the video with tools/sfx.py (a quiet pad, a whoosh on every scroll beat, a chime on the
end card); --audio <file> muxes your own track (mixed under the sfx when both are given). Needs ffmpeg.

Output is MP4 when ffmpeg is on PATH and --out ends in .mp4, else WebM. tools/promo.py builds directed
launch videos (acting beats, close-ups, both aspects) on the same Director class.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sys.exit("trailer.py needs Playwright: pip install playwright && python3 -m playwright install chromium "
             "(bare Linux: python3 -m playwright install-deps chromium)")

TOOLS = Path(__file__).resolve().parent

# aspect -> (css viewport w, h, device scale, output w, h). 9:16 records the phone layout at 2.4x so the
# reel is the mobile site, not a squeezed desktop.
ASPECTS = {
    "16:9": (1280, 720, 1, 1280, 720),
    "9:16": (450, 800, 2.4, 1080, 1920),
    "1:1": (720, 720, 1.5, 1080, 1080),
}

CARD_CSS = """
#mf-trailer-card { position: fixed; inset: 0; z-index: 2147483000; display: grid; place-content: center; gap: 14px;
  text-align: center; background: var(--mf-bg); color: var(--mf-fg); font: 600 clamp(34px, 8vw, 110px)/1.02 var(--mf-font);
  letter-spacing: -.04em; transition: opacity .5s ease; padding: 7vw; }
#mf-trailer-card small { font: 500 clamp(11px, 1.6vw, 16px)/1.45 ui-monospace, monospace; letter-spacing: .18em;
  text-transform: uppercase; opacity: .65; }
#mf-trailer-card .mf-cta { justify-self: center; margin-top: 10px; padding: .7em 1.3em; border-radius: 999px;
  background: var(--mf-accent); color: var(--mf-cta-ink, var(--mf-bg)); font: 700 clamp(14px, 2.2vw, 24px)/1.1 var(--mf-font);
  letter-spacing: -.01em; transform: scale(.6); opacity: 0; transition: transform .6s cubic-bezier(.34,1.56,.64,1), opacity .3s; }
#mf-trailer-card.is-in .mf-cta { transform: none; opacity: 1; }
#mf-trailer-card.is-out { opacity: 0; pointer-events: none; }
"""

COVER_JS = """(() => {
  const mk = () => {
    if (document.getElementById('mf-trailer-card')) return;
    const c = document.createElement('div'); c.id = 'mf-trailer-card';
    c.style.cssText = 'position:fixed;inset:0;z-index:2147483000;background:%s';
    (document.body || document.documentElement).appendChild(c);
  };
  if (document.documentElement) mk(); else document.addEventListener('readystatechange', mk, { once: true });
})();"""

READ_TOKEN = """([names, fallbackProp]) => {
  const cs = getComputedStyle(document.documentElement);
  for (const n of names) { const v = cs.getPropertyValue(n).trim(); if (v) return v; }
  const b = getComputedStyle(document.body)[fallbackProp];
  return b && b !== 'rgba(0, 0, 0, 0)' ? b : '';
}"""


def has_ffmpeg() -> bool:
    return bool(shutil.which("ffmpeg"))


class Director:
    """Drives one Playwright page and logs every beat with its time, so the soundtrack lands on the cut."""

    def __init__(self, page, look: dict):
        self.page, self.look, self.events = page, look, []
        self.t0 = time.time()
        self.lead = 0.0

    # ---- time
    def now(self) -> float:
        return time.time() - self.t0

    def mark(self, sound: str, gain: float = 1.0, offset: float = 0.0):
        self.events.append((self.now() + offset, sound, gain))

    def hold(self, s: float):
        self.page.wait_for_timeout(int(s * 1000))

    # ---- look
    def resolve_look(self):
        lk, p = self.look, self.page
        if lk.get("bg") == "page":
            lk["bg"] = p.evaluate(READ_TOKEN, [["--bg", "--color-bg", "--background"], "backgroundColor"]) or "#070d1a"
        if lk.get("fg") == "page":
            lk["fg"] = p.evaluate(READ_TOKEN, [["--ink", "--fg", "--text", "--color-ink"], "color"]) or "#e8eff9"
        if lk.get("accent") in ("", "page", None):
            lk["accent"] = p.evaluate(READ_TOKEN, [["--accent", "--brand", "--color-accent"], "_"]) or "#3fdcff"
        font = lk.get("font") or ""
        stack = (f'"{font}", ' if font else "") + '-apple-system, "Segoe UI", Inter, system-ui, sans-serif'
        if font and lk.get("webfont", True):
            p.evaluate("""fam => new Promise(res => { const l = document.createElement('link'); l.rel = 'stylesheet';
              l.href = `https://fonts.googleapis.com/css2?family=${fam}:wght@500;600;700&display=swap`;
              l.onload = l.onerror = res; setTimeout(res, 3000); document.head.appendChild(l); })""", font.replace(" ", "+"))
        p.add_style_tag(content=f":root{{--mf-bg:{lk['bg']};--mf-fg:{lk['fg']};--mf-accent:{lk['accent']};--mf-font:{stack};}}" + CARD_CSS)
        # CTA ink: whichever of bg / fg reads better on the accent
        p.evaluate("""() => {
          const rgb = c => { const e = document.createElement('i'); e.style.color = c; document.body.appendChild(e);
            const m = getComputedStyle(e).color.match(/[\\d.]+/g).map(Number); e.remove(); return m; };
          const lum = ([r, g, b]) => [r, g, b].map(v => (v /= 255) <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4)
            .reduce((s, v, i) => s + v * [.2126, .7152, .0722][i], 0);
          const cr = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + .05) / (y + .05); };
          const cs = getComputedStyle(document.documentElement), A = rgb(cs.getPropertyValue('--mf-accent'));
          const ink = cr(A, rgb(cs.getPropertyValue('--mf-bg'))) >= cr(A, rgb(cs.getPropertyValue('--mf-fg'))) ? 'var(--mf-bg)' : 'var(--mf-fg)';
          document.documentElement.style.setProperty('--mf-cta-ink', ink);
        }""")
        if font:
            p.evaluate("""f => Promise.race([document.fonts.load(`600 40px "${f}"`).catch(() => {}),
                                          new Promise(r => setTimeout(r, 2500))])""", font)

    # ---- cards
    def card(self, title: str, sub: str = "", cta: str = "", edge: str = "bottom"):
        self.page.evaluate("""({ title, sub, cta, edge }) => {
          let c = document.getElementById('mf-trailer-card');
          if (!c) { c = document.createElement('div'); c.id = 'mf-trailer-card'; document.body.appendChild(c); }
          c.removeAttribute('style'); c.className = '';
          const esc = s => s.replace(/[&<>]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[m]));
          c.innerHTML = `<div>${esc(title)}</div>` + (sub ? `<small>${esc(sub)}</small>` : '') +
                        (cta ? `<span class="mf-cta">${esc(cta)}</span>` : '');
          c.style[edge === 'top' ? 'borderTop' : 'borderBottom'] = '6px solid var(--mf-accent)';
          requestAnimationFrame(() => requestAnimationFrame(() => c.classList.add('is-in')));
        }""", {"title": title, "sub": sub, "cta": cta, "edge": edge})

    def card_out(self):
        self.page.evaluate("() => document.getElementById('mf-trailer-card')?.classList.add('is-out')")
        self.hold(.5)
        self.page.evaluate("() => document.getElementById('mf-trailer-card')?.remove()")

    # ---- camera
    def scroll_y(self, y: float, s: float, sound: str | None = "whoosh"):
        """Eased glide from the current scroll position to y over s seconds."""
        start = self.page.evaluate("() => scrollY")
        if sound and abs(y - start) > 40:
            self.mark(sound, .9)
        t_start = time.monotonic()
        while True:  # clock-driven, so slow evaluate() calls never stretch the shot
            p = min(1.0, (time.monotonic() - t_start) / max(s, 1e-3))
            e = p * p * (3 - 2 * p)
            self.page.evaluate("""y => { if (window.lenis && window.lenis.scrollTo) window.lenis.scrollTo(y, { immediate: true });
              else window.scrollTo({ top: y, behavior: 'instant' }); }""", start + (y - start) * e)
            if p >= 1.0:
                break
            self.page.wait_for_timeout(16)

    def max_scroll(self) -> float:
        return self.page.evaluate("() => Math.max(0, document.documentElement.scrollHeight - innerHeight)")

    def beat_targets(self, n: int) -> list[float]:
        """Section tops to stop on (data-beat, section, header, footer), thinned to n, else evenly spaced."""
        tops = self.page.evaluate("""() => [...document.querySelectorAll('[data-beat], main > section, body > section, section, footer')]
          .map(e => e.getBoundingClientRect().top + scrollY).filter(y => y > innerHeight * .4)""")
        total = self.max_scroll()
        tops = sorted({min(total, round(t)) for t in tops})
        if len(tops) > n:
            tops = [tops[round(i * (len(tops) - 1) / (n - 1))] for i in range(n)] if n > 1 else [tops[-1]]
        if len(tops) < 2:
            tops = [total * (i + 1) / n for i in range(n)]
        if tops and tops[-1] < total - 10:
            tops[-1] = total
        return tops

    def scroll_through(self, seconds: float, mode: str = "smooth"):
        total = self.max_scroll()
        if mode == "smooth" or total < 50:
            if total >= 50:
                self.mark("whoosh", .6)
            self.scroll_y(total, seconds, sound=None)
            return
        n = max(2, min(7, int(seconds / 1.5)))
        per = seconds / n
        for y in self.beat_targets(n):
            self.scroll_y(y, per * .55)
            self.hold(per * .45)

    def scroll_to(self, sel: str, s: float = 1.0, offset: float = .12):
        y = self.page.evaluate("""([sel, off]) => { const e = document.querySelector(sel); if (!e) return null;
          return Math.max(0, Math.min(e.getBoundingClientRect().top + scrollY - innerHeight * off,
                                       document.documentElement.scrollHeight - innerHeight)); }""", [sel, offset])
        if y is None:
            print(f"  ! scroll_to: no element matches {sel!r}")
            return
        self.scroll_y(y, s)

    def zoom(self, sel: str, scale: float = 1.6, s: float = .9):
        ok = self.page.evaluate("""([sel, k, s]) => { const e = document.querySelector(sel); if (!e) return false;
          const r = e.getBoundingClientRect(), h = document.documentElement;
          h.style.transformOrigin = `${r.left + r.width / 2}px ${r.top + scrollY + r.height / 2}px`;
          h.style.transition = `transform ${s}s cubic-bezier(.16,1,.3,1)`; h.style.transform = `scale(${k})`; return true; }""",
                               [sel, scale, s])
        if ok:
            self.mark("swish", .8)
            self.hold(s)
        else:
            print(f"  ! zoom: no element matches {sel!r}")

    def unzoom(self, s: float = .7):
        self.page.evaluate("""s => { const h = document.documentElement; h.style.transition = `transform ${s}s cubic-bezier(.16,1,.3,1)`;
          h.style.transform = ''; }""", s)
        self.hold(s)

    def click(self, sel: str):
        try:
            self.page.locator(sel).first.click(timeout=3000)
            self.mark("pop", .9)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! click {sel!r}: {exc.__class__.__name__}")

    def hover(self, sel: str):
        try:
            self.page.locator(sel).first.hover(timeout=3000)
            self.mark("plip", .7)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! hover {sel!r}: {exc.__class__.__name__}")

    # ---- post
    def finish(self, rec: "Recorder", out: Path, sfx: bool, audio: str | None, out_size: tuple[int, int]) -> Path:
        end = self.now()
        dur = max(1.0, end - self.lead)
        track = None
        if sfx:
            sys.path.insert(0, str(TOOLS))
            from sfx import render_timeline
            ev = [(t - self.lead, n, g) for t, n, g in self.events]
            track = render_timeline(ev, dur, rec.tmp / "sfx.wav")
        return rec.encode(out, self.t0 + self.lead, dur, track, audio, out_size)


class Recorder:
    """Sharp capture: a CDP screencast at device resolution (a 9:16 reel is real 1080x1920, not an upscale).
    Falls back to Playwright's own (viewport-sized) WebM recorder when ffmpeg is missing."""

    def __init__(self, ctx, page, out_w: int, out_h: int):
        self.tmp = Path(tempfile.mkdtemp(prefix="trailer-"))
        self.frames: list[tuple[float, Path]] = []
        self.page, self.ctx = page, ctx
        self.cdp = ctx.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._frame)
        self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 90, "maxWidth": out_w,
                                               "maxHeight": out_h, "everyNthFrame": 1})

    def _frame(self, f):
        import base64
        path = self.tmp / f"f{len(self.frames):05d}.jpg"
        path.write_bytes(base64.b64decode(f["data"]))
        self.frames.append((float(f["metadata"].get("timestamp") or time.time()), path))
        try:
            self.cdp.send("Page.screencastFrameAck", {"sessionId": f["sessionId"]})
        except Exception:  # noqa: BLE001  (page closing)
            pass

    def stop(self):
        try:
            self.cdp.send("Page.stopScreencast")
        except Exception:  # noqa: BLE001
            pass

    def encode(self, out: Path, t_start: float, dur: float, sfx_wav, music, size) -> Path:
        frames = [(t, f) for t, f in self.frames]
        if not frames:
            raise SystemExit("no frames were captured")
        # keep the last frame at or before t_start, then everything after it
        first = max([i for i, (t, _) in enumerate(frames) if t <= t_start] or [0])
        frames = frames[first:]
        lines = []
        t_end = t_start + dur
        for i, (t, f) in enumerate(frames):
            t0 = max(t, t_start)
            t1 = min(frames[i + 1][0] if i + 1 < len(frames) else t_end, t_end)
            if t1 <= t0:
                continue
            lines += [f"file '{f.as_posix()}'", f"duration {t1 - t0:.4f}"]
        lines.append(lines[-2])  # concat demuxer: repeat the last file so its duration counts
        lst = self.tmp / "frames.txt"
        lst.write_text("\n".join(lines) + "\n")
        dest = encode(lst, out, 0.0, dur, sfx_wav, music, size, concat=True)
        shutil.rmtree(self.tmp, ignore_errors=True) if dest.exists() else None
        return dest


class VideoFileRecorder:
    """No-ffmpeg fallback: Playwright's WebM, kept as is (no audio, viewport resolution)."""

    def __init__(self, page):
        self.page, self.tmp = page, Path(tempfile.mkdtemp(prefix="trailer-"))
        self.src = None

    def stop(self):
        pass

    def encode(self, out: Path, t_start: float, dur: float, sfx_wav, music, size) -> Path:
        dest = out.with_suffix(".webm")
        shutil.move(str(self.src), str(dest))
        if sfx_wav or music:
            print("  ! ffmpeg not found: audio skipped (install ffmpeg to mux --sfx / --audio)")
        return dest


def probe_duration(path: Path) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:  # webm from Playwright sometimes has no duration header; count frames instead
        r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_packets,r_frame_rate", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
        try:
            rate, n = r.stdout.strip().split(",")[:2]
            a, b = rate.split("/")
            return int(n) / (float(a) / float(b))
        except Exception:  # noqa: BLE001
            return None


def encode(src: Path, out: Path, lead: float, dur: float, sfx_wav: Path | None, music: str | None,
           size: tuple[int, int], concat: bool = False) -> Path:
    """src = a video file, or (concat=True) an ffmpeg concat list of timed frames."""
    if not concat:
        src_dur = probe_duration(src)
        if src_dur:
            dur = max(0.5, min(dur, src_dur - lead))
    mp4 = out.suffix.lower() == ".mp4"
    dest = out if mp4 or out.suffix.lower() == ".webm" else out.with_suffix(".mp4")
    mp4 = dest.suffix.lower() == ".mp4"
    w, h = size
    cmd = ["ffmpeg", "-y", "-v", "error"] + (["-f", "concat", "-safe", "0"] if concat else ["-ss", f"{lead:.3f}"]) + ["-i", str(src)]
    inputs = []
    if sfx_wav:
        cmd += ["-i", str(sfx_wav)]
        inputs.append(f"[{len(inputs) + 1}:a]")
    if music:
        cmd += ["-stream_loop", "-1", "-i", music]
        inputs.append(f"[{len(inputs) + 1}:a]")
    vf = (f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p")
    fc = [f"[0:v]{vf}[v]"]
    if inputs:
        parts = []
        for i, lab in enumerate(inputs):
            vol = "0.55" if (music and sfx_wav and i == len(inputs) - 1) else "1.0"
            parts.append(f"{lab}volume={vol},apad,atrim=0:{dur:.3f}[a{i}]")
        fc += parts
        mix = "".join(f"[a{i}]" for i in range(len(inputs)))
        fade_st = max(0, dur - 1.2)
        fc.append(f"{mix}amix=inputs={len(inputs)}:normalize=0,afade=t=in:d=0.15,afade=t=out:st={fade_st:.3f}:d=1.2[a]"
                  if len(inputs) > 1 else f"{mix}afade=t=in:d=0.15,afade=t=out:st={fade_st:.3f}:d=1.2[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]"]
    if inputs:
        cmd += ["-map", "[a]"]
    cmd += ["-t", f"{dur:.3f}"]
    if mp4:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "-movflags", "+faststart"]
        cmd += ["-c:a", "aac", "-b:a", "160k"] if inputs else []
    else:
        cmd += ["-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", "-row-mt", "1"]
        cmd += ["-c:a", "libopus", "-b:a", "128k"] if inputs else []
    cmd.append(str(dest))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not dest.exists():
        sys.stderr.write(r.stderr[-2000:])
        raise SystemExit("ffmpeg failed (see above)")
    return dest


def resolve_target(target: str, ap=None):
    if target.startswith(("http://", "https://", "file://")):
        return target, None
    if not Path(target).exists():
        msg = f"not a URL and not a local path: {target}"
        ap.error(msg) if ap else sys.exit(msg)
    sys.path.insert(0, str(TOOLS))
    from qa import serve_local
    return serve_local(target)


def open_recording(pw, url: str, aspect: str, width: int | None, height: int | None, look: dict, timeout: int):
    """Returns browser, ctx, page, director, recorder, output size."""
    vw, vh, dsf, ow, oh = ASPECTS[aspect]
    if width and height:
        ow, oh = width, height
        if aspect == "16:9" and (width, height) != (1280, 720):
            vw, vh = width, height  # old behaviour: --width/--height set the viewport too
            dsf = 1
    browser = pw.chromium.launch()
    opts = dict(viewport={"width": vw, "height": vh}, device_scale_factor=dsf,
                is_mobile=aspect == "9:16", has_touch=aspect == "9:16")
    fallback = not has_ffmpeg()
    if fallback:
        tmp = Path(tempfile.mkdtemp(prefix="trailer-"))
        opts.update(record_video_dir=str(tmp), record_video_size={"width": vw, "height": vh})
    ctx = browser.new_context(**opts)
    ctx.add_init_script(COVER_JS % (look.get("bg") if look.get("bg") not in (None, "page") else "#070d1a"))
    page = ctx.new_page()
    rec = VideoFileRecorder(page) if fallback else Recorder(ctx, page, int(vw * dsf), int(vh * dsf))
    d = Director(page, look)
    page.goto(url, wait_until="load", timeout=timeout * 1000)
    page.wait_for_timeout(900)
    return browser, ctx, page, d, rec, (ow, oh)


def close_recording(browser, ctx, page, rec):
    rec.stop()
    video = page.video
    ctx.close()
    if isinstance(rec, VideoFileRecorder):
        rec.src = Path(video.path()) if video else None
    browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Record a short title → scroll → end-card trailer of a page.")
    ap.add_argument("target", help="URL or local file/folder (served automatically)")
    ap.add_argument("--out", default="trailer.webm", help="output video (mp4 if ffmpeg, else webm)")
    ap.add_argument("--title", default="", help="title card text (default: page <title>)")
    ap.add_argument("--subtitle", default="", help="title card subtitle (default: page description)")
    ap.add_argument("--duration", type=float, default=15, help="total seconds (default 15)")
    ap.add_argument("--aspect", choices=list(ASPECTS), default="16:9", help="16:9 (default), 9:16 reels, 1:1")
    ap.add_argument("--width", type=int, default=None, help="output width (overrides the aspect preset)")
    ap.add_argument("--height", type=int, default=None, help="output height (overrides the aspect preset)")
    ap.add_argument("--bg", default="#070d1a", help='card background hex, or "page" (default #070d1a)')
    ap.add_argument("--fg", default="#e8eff9", help='card text hex, or "page" (default #e8eff9)')
    ap.add_argument("--accent", default="page", help='accent hex, or "page" = the page\'s --accent (default)')
    ap.add_argument("--font", default="", help='card font family, e.g. "Baloo 2" (Google Fonts when reachable)')
    ap.add_argument("--end-title", default="Made with Motion Field", help="end card headline")
    ap.add_argument("--end-sub", default="Recipes for agents · vanilla HTML/CSS/JS", help="end card small line")
    ap.add_argument("--end-cta", default="", help='end card button text, e.g. "Join the waitlist → paw.fm"')
    ap.add_argument("--scroll", choices=["smooth", "beats"], default=None,
                    help="smooth glide, or stop on sections (default: beats with --sfx, else smooth)")
    ap.add_argument("--sfx", action="store_true", help="score it: pad + whoosh per scroll beat + end-card chime")
    ap.add_argument("--audio", default=None, help="music/sfx file to mux (looped/trimmed to length)")
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()
    if a.audio and not Path(a.audio).exists():
        ap.error(f"--audio file not found: {a.audio}")

    url, httpd = resolve_target(a.target, ap)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    look = {"bg": a.bg, "fg": a.fg, "accent": a.accent, "font": a.font}
    hold_title, hold_end = 1.6, 1.8 + (0.6 if a.end_cta else 0)
    scroll_s = max(4.0, a.duration - hold_title - .5 - hold_end)
    mode = a.scroll or ("beats" if a.sfx else "smooth")

    with sync_playwright() as pw:
        browser, ctx, page, d, rec, size = open_recording(pw, url, a.aspect, a.width, a.height, look, a.timeout)
        title = a.title or page.title() or "Motion Field"
        subtitle = a.subtitle or page.evaluate("() => document.querySelector('meta[name=description]')?.content || ''")
        d.resolve_look()
        d.card(title, subtitle)
        d.lead = max(0.0, d.now() - .05)
        d.mark("pop", .6, offset=.05)
        d.hold(hold_title)
        d.mark("whoosh", .5)
        d.card_out()
        d.scroll_through(scroll_s, mode)
        d.card(a.end_title, a.end_sub, a.end_cta, edge="top")
        d.mark("chime", 1.0, offset=.15)
        d.hold(hold_end)
        close_recording(browser, ctx, page, rec)

    if httpd:
        httpd.shutdown()
    dest = d.finish(rec, out, a.sfx, a.audio, size)
    print("wrote", dest, f"({dest.stat().st_size / 1024 / 1024:.1f} MB)",
          "" if has_ffmpeg() else "(install ffmpeg for MP4 + audio)")
    if a.sfx:
        print("beats:", ", ".join(f"{t - d.lead:.1f}s {n}" for t, n, _ in d.events))


if __name__ == "__main__":
    main()
