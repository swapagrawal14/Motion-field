#!/usr/bin/env python3
"""Chai Chalo — a directed trailer for recipes/expression-cast (not a scroll-through).

    python3 recipes/expression-cast/promo.py --aspect 16:9 --out chai_reel_16x9.mp4
    python3 recipes/expression-cast/promo.py --aspect 9:16 --out chai_reel_9x16.mp4

Beats: cold open on Kettle Kaka's face (blink, blink, gasp) pulling back into a whistle -> title card in the
page's own type and colours, the cast springing up -> the live hero: the shutter rolls up and the counter
sings -> chorus section, push in on the choir -> CTA hover, the whole cast gasps -> click, the kettle pours,
the kulhad goes happy -> end card. Scored with tools/sfx.py (pop / whoosh / swish / chime + a kettle
whistle added here) over the procedural bed.

Built on tools/trailer.py's Director + Recorder, so it records a CDP screencast at device resolution
(the 9:16 reel is the real phone layout at 1080x1920). Every overlay shot is composed from the page's
own CSS classes, cutouts and fonts, so the cards are the brand, not a generic title slide.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "tools"))

import numpy as np  # noqa: E402
import sfx  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
from trailer import close_recording, open_recording, resolve_target  # noqa: E402


def whistle():
    """Kettle whistle: a breathy sine that slides up and wobbles, with a little noise for steam."""
    sec = 1.15
    t = np.arange(int(sec * sfx.SR)) / sfx.SR
    f = 1500 + 850 * (1 - np.exp(-t * 9)) + 40 * np.sin(2 * np.pi * 9 * t)
    ph = 2 * np.pi * np.cumsum(f) / sfx.SR
    env = np.minimum(1, t / .1) * np.clip((sec - t) / .3, 0, 1)
    breath = np.random.default_rng(3).normal(0, 1, len(t)) * .05
    return (np.sin(ph) * .16 + np.sin(2 * ph) * .03 + breath * .4) * env


sfx.FX["whistle"] = whistle

CSS = """
.sound { display: none !important; }
#tr-cold, #tr-title, #tr-end { position: fixed; inset: 0; z-index: 2147482000; overflow: hidden; }
#tr-cold { background: var(--sky); }
#tr-cold::before { content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(-12deg, transparent 0 46px, rgba(255,255,255,.25) 46px 92px); }
#tr-cold .rig { position: absolute; transform-origin: 69% 68%; transition: transform 1.25s cubic-bezier(.34, 1.3, .64, 1); }
#tr-title { background: var(--marigold-soft); display: grid; place-content: center; text-align: center; }
#tr-title .rays { opacity: .6; top: 46%; }
#tr-title .awning { z-index: 3; }
#tr-title .toran { top: 54px; z-index: 2; }
.tr-h { position: relative; z-index: 4; font-size: min(19vw, 21vh, 200px); line-height: .92; transform: scale(.3) rotate(-8deg); opacity: 0;
  transition: transform .7s cubic-bezier(.34, 1.56, .64, 1), opacity .2s; }
.tr-in .tr-h { transform: none; opacity: 1; }
.tr-h .dev { display: block; font: 800 .2em/1.3 var(--text); -webkit-text-stroke: 0; text-shadow: none; color: var(--terracotta); letter-spacing: .1em; }
.tr-sub { position: relative; z-index: 4; justify-self: center; margin-top: 14px; padding: 8px 22px 6px; border-radius: 999px; background: var(--paper);
  border: 3.5px solid var(--ink); box-shadow: 4px 4px 0 var(--ink); font: 400 min(4.2vw, 30px)/1.1 var(--display); color: var(--ink);
  transform: translateY(30px); opacity: 0; transition: transform .6s cubic-bezier(.34, 1.56, .64, 1) .25s, opacity .3s .25s; }
.tr-in .tr-sub { transform: none; opacity: 1; }
.tr-cast { position: absolute; z-index: 5; left: 0; right: 0; bottom: -4vh; display: flex; justify-content: center; align-items: flex-end; gap: 1vw; }
.tr-cast .rig { position: relative; flex: none; transform: translateY(120%); transition: transform .7s cubic-bezier(.34, 1.56, .64, 1); }
.tr-in .tr-cast .rig { transform: none; }
.tr-side { position: absolute; z-index: 5; bottom: -2vh; transform: translateX(var(--from)); transition: transform .8s cubic-bezier(.34, 1.4, .64, 1) .35s; }
.tr-in .tr-side { transform: none; }
.tr-side img { width: 100%; height: auto; }
#tr-end { background: var(--cream); display: grid; place-content: center; text-align: center; gap: 18px; }
#tr-end .toran { top: -8px; }
#tr-end .tr-h { font-size: min(16vw, 20vh, 180px); }
#tr-end .rays { opacity: .5; top: 40%; }
#tr-end { padding-bottom: 14vh; }
.tr-mf { position: relative; z-index: 4; justify-self: center; padding: 8px 24px 6px; border-radius: 999px; background: var(--ink); color: var(--marigold-soft);
  font: 400 min(4.6vw, 34px)/1.1 var(--display); letter-spacing: .03em; transform: scale(.4); opacity: 0;
  transition: transform .6s cubic-bezier(.34, 1.56, .64, 1) .3s, opacity .2s .3s; }
.tr-in .tr-mf { transform: none; opacity: 1; }
.tr-small { position: relative; z-index: 4; font: 700 min(3.4vw, 20px)/1.3 var(--text); color: var(--ink-soft); }
"""

JS = r"""
window.TR = (() => {
  const clone = (sel, w, extra = '') => {
    const src = document.querySelector(sel); const c = src.cloneNode(true);
    const ar = src.style.getPropertyValue('--ar'); c.className = 'rig'; c.removeAttribute('tabindex'); c.style.cssText = `--ar:${ar};--w:${w};${extra}`; c.dataset.face = 'neutral';
    c.querySelectorAll('.steam-src').forEach((s) => s.remove());
    return c;
  };
  const steam = (host) => { const s = document.createElement('div'); s.className = 'steam-src';
    for (let i = 0; i < 3; i++) { const p = document.createElement('img'); p.className = 'steam'; p.src = 'art/steam.webp';
      p.style.cssText = `--d:${i * .6};--dx:${-30 - i * 22}px;left:${-i * 14}px;top:0`; s.appendChild(p); }
    host.querySelector('.act').appendChild(s); };
  const face = (el, f, ms) => { el.dataset.face = f; if (ms) setTimeout(() => (el.dataset.face = 'neutral'), ms); };
  const tall = innerHeight > innerWidth;
  return {
    cold() {
      const o = document.createElement('div'); o.id = 'tr-cold';
      const W = tall ? innerWidth * 1.9 : innerWidth * 1.6, H = W * 900 / 879; this.W = W;
      const k = clone('.c-kettle', W + 'px', `left:${innerWidth / 2 - .69 * W}px;top:${innerHeight * .5 - .64 * H}px`);
      steam(k); o.appendChild(k); document.body.appendChild(o); this.k = k;
    },
    blink() { face(this.k, 'blink', 150); },
    gasp() { face(this.k, 'surprised'); },
    pull() {
      // pull back, but keep the kettle's cut edge (right) off frame: it settles bleeding in from the right, hero style
      const s = tall ? .5 : .42, cx = innerWidth / 2;
      const tx = Math.max(0, innerWidth - .31 * this.W * s + 12 - cx);
      this.k.style.transform = `translate(${tx}px, ${tall ? -40 : 30}px) scale(${s}) rotate(-6deg)`;
      setTimeout(() => face(this.k, 'sing'), 250);
    },
    title() {
      const o = document.createElement('div'); o.id = 'tr-title';
      o.innerHTML = `<div class="rays"></div><div class="awning-rail"></div><div class="awning"></div>
        <div class="toran"><img src="art/marigold.webp"><img src="art/marigold.webp"><img src="art/marigold.webp"></div>
        <h1 class="stk tr-h">Chai Chalo<span class="dev">चाय चलो</span></h1><div class="tr-sub">the tapri that sings</div>
        <div class="tr-cast"></div>`;
      const cast = o.querySelector('.tr-cast');
      const u = tall ? 'vw' : 'vh';
      [['.g-biscuit', 15], ['.g-samosa', 21], ['.g-kulhad', 23], ['.g-jalebi', 21]].forEach(([s, w], i) => {
        const c = clone(s, (tall ? w * 2.3 : w * 1.25) + u); c.style.transitionDelay = (0.35 + i * .09) + 's'; cast.appendChild(c); });
      const sideW = tall ? '46vw' : '30vh';
      const l = document.createElement('div'); l.className = 'tr-side'; l.style.cssText = `left:-${tall ? 14 : 2}vw;width:${sideW};--from:-120%`;
      l.innerHTML = '<img src="art/customer.webp" alt="">';
      const r = clone('.o-chaiwala', tall ? '52vw' : '40vh', `right:-${tall ? 16 : 3}vw;bottom:-4vh;--from:120%`);
      r.classList.add('tr-side');
      if (!tall) o.append(l, r);
      document.body.appendChild(o); this.t = o;
      requestAnimationFrame(() => requestAnimationFrame(() => o.classList.add('tr-in')));
      setTimeout(() => o.querySelectorAll('.tr-cast .rig, .tr-side.rig').forEach((c, i) => setTimeout(() => face(c, 'sing', 500), i * 110)), 1100);
    },
    titleOut() { const c = document.getElementById('tr-cold'); c && c.remove(); this.t.remove(); },
    closeShutter() { scrollTo(0, 0); document.querySelector('.hero').classList.remove('open'); },
    openShutter() { document.querySelector('.hero').classList.add('open'); },
    end() {
      const o = document.createElement('div'); o.id = 'tr-end';
      o.innerHTML = `<div class="rays" style="background: repeating-conic-gradient(from 0deg, #fbe6b0 0 7.5deg, transparent 7.5deg 15deg)"></div><div class="toran"><img src="art/marigold.webp"><img src="art/marigold.webp"><img src="art/marigold.webp"></div>
        <h2 class="stk tr-h">Chai Chalo</h2><div class="tr-mf">Motion Field</div>
        <p class="tr-small">recipes/expression-cast · one pose, many faces</p><div class="tr-cast" style="bottom:-3vh"></div>`;
      if (tall) o.querySelector('.tr-h').innerHTML = 'Chai<br>Chalo';
      if (!tall) {
        const l = document.createElement('div'); l.className = 'tr-side'; l.style.cssText = 'left:-3vw;width:34vh;--from:-120%';
        l.innerHTML = '<img src="art/customer.webp" alt="">';
        const r = clone('.o-chaiwala', '46vh', 'right:-4vw;bottom:-4vh;--from:120%'); r.classList.add('tr-side');
        o.append(l, r);
      }
      const cast = o.querySelector('.tr-cast'); const u = tall ? 'vw' : 'vh';
      (tall ? [['.g-samosa', 40], ['.g-kulhad', 46], ['.g-jalebi', 40]] : [['.g-biscuit', 19], ['.g-samosa', 26], ['.g-kulhad', 30], ['.g-jalebi', 26]]).forEach(([s, w], i) => {
        const c = clone(s, w + u); c.style.transitionDelay = (0.2 + i * .08) + 's'; cast.appendChild(c); });
      document.body.appendChild(o);
      requestAnimationFrame(() => requestAnimationFrame(() => o.classList.add('tr-in')));
      setTimeout(() => o.querySelectorAll('.tr-cast .rig, .tr-side.rig').forEach((c, i) => setTimeout(() => face(c, 'sing', 900), i * 120)), 900);
    },
  };
})();
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Directed Chai Chalo trailer.")
    ap.add_argument("--aspect", choices=["16:9", "9:16"], default="16:9")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target", default=str(HERE))
    a = ap.parse_args()
    url, httpd = resolve_target(a.target)
    if not url.endswith(".html"):
        url = url.rstrip("/") + "/index.html"
    tall = a.aspect == "9:16"
    look = {"bg": "#bcd8ec", "fg": "#2a1d17", "accent": "#d8402e", "font": "Titan One"}
    with sync_playwright() as pw:
        browser, ctx, page, d, rec, size = open_recording(pw, url, a.aspect, None, None, look, 30)
        page.wait_for_timeout(2600)            # let the page's own hero greeting finish before we roll
        d.resolve_look()
        page.add_style_tag(content=CSS)
        page.evaluate(JS)
        page.evaluate("document.fonts.ready")
        ev = page.evaluate

        # 1 · cold open: Kettle Kaka, extreme close-up
        ev("TR.cold()")
        page.wait_for_timeout(250)
        ev("() => document.getElementById('mf-trailer-card')?.remove()")
        d.lead = d.now()
        d.mark("dab", .5)
        d.hold(.55); ev("TR.blink()"); d.mark("tick", .5)
        d.hold(.7); ev("TR.blink()"); d.mark("tick", .5)
        d.hold(.45); ev("TR.gasp()"); d.mark("whistle", .9)
        d.hold(.3); ev("TR.pull()"); d.mark("swish", .6)
        d.hold(1.15)

        # 2 · title card in the page's own type, colours and cast
        ev("TR.title()"); d.mark("whoosh", .7); d.mark("pop", .9, offset=.15)
        for i in range(4):
            d.mark("pop", .45, offset=.45 + i * .09)
        ev("TR.closeShutter()")
        d.hold(2.0)

        # 3 · the live hero: shutter rolls up, the counter sings
        ev("TR.titleOut()"); d.mark("whoosh", .6, offset=.1)
        d.hold(.15); ev("TR.openShutter()")
        d.hold(1.35)
        ev("Chai.chorus(document.querySelector('.hero'))"); d.mark("whistle", .8)
        for i in range(5):
            d.mark("plip", .35, offset=.45 + i * .14)
        d.hold(1.5)

        # 4 · kettle ki seeti: push in on the choir while it sings
        d.scroll_y(page.evaluate("""() => { const c = document.querySelector('#chorus'); const r = c.getBoundingClientRect();
            return r.top + scrollY + r.height - innerHeight + 20; }"""), .9)
        d.zoom(".ch-samosa" if not tall else ".ch-samosa", 1.3 if not tall else 1.2, .55)
        ev("Chai.chorus(document.querySelector('#chorus'))"); d.mark("whistle", .8)
        for i in range(5):
            d.mark("plip", .4, offset=.45 + i * .14)
        d.hold(1.9)
        d.unzoom(.45)

        # 5 · CTA: hover and the whole cast gasps
        if tall:
            d.scroll_y(page.evaluate("() => document.querySelector('#pour-btn').getBoundingClientRect().top + scrollY - innerHeight * .16"), .9)
        else:
            d.scroll_to("#order", .9, offset=0)
        d.hold(.2)
        d.hover("#pour-btn"); ev("Chai.gaspOn()"); d.mark("swish", .8)
        d.hold(1.0)

        # 6 · click: Kettle Kaka pours, the kulhad goes happy
        ev("() => { const f = document.getElementById('nm'); f.value = 'Swapnil'; }")
        d.click("#pour-btn"); d.mark("whoosh", .8, offset=.1)
        d.zoom(".o-kulhad", 1.35 if not tall else 1.25, .6)
        d.mark("success", .8, offset=.1)
        d.hold(1.35)
        d.unzoom(.35)

        # 7 · end card
        ev("TR.end()"); d.mark("pop", .7, offset=.1); d.mark("chime", 1.0, offset=.35)
        for i in range(5):
            d.mark("plip", .3, offset=.95 + i * .12)
        d.hold(2.3)
        close_recording(browser, ctx, page, rec)
    if httpd:
        httpd.shutdown()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    dest = d.finish(rec, out, True, None, size)
    print("wrote", dest, f"({dest.stat().st_size / 1024 / 1024:.1f} MB)")
    print("beats:", ", ".join(f"{t - d.lead:.1f}s {n}" for t, n, _ in d.events if t >= d.lead))


if __name__ == "__main__":
    main()
