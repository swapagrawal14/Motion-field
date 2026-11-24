#!/usr/bin/env python3
"""Read a reference (URL or screenshot) and write a DESIGN.md token sheet.

    python3 tools/style_ref.py https://example.com --out sites/acme/DESIGN.md --name acme
    python3 tools/style_ref.py ref-desktop.png --out DESIGN.md --name from-pin
    python3 tools/style_ref.py https://example.com --out DESIGN.md --mobile ref-mobile.png

What it measures
  palette      background, surface, ink, muted, accent (k-means over the screenshot)
  type         display/body families, the size ladder, letter-spacing, line-height (computed styles)
  shape        median border radius of real elements (computed styles)
  feel         a one-line read of the system + a suggested image prompt

URL mode samples the live page with Playwright. Image mode gives you the palette and asks you to
eyeball the type and radii — the tool never invents a font it cannot see.

The output is a starting point. Never copy a reference's brand, logo, copy or photography; copy the
system (contrast, spacing rhythm, motion language) and make it yours.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

SAMPLE_JS = r"""
() => {
  const med = (a) => { if (!a.length) return 0; const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
  const q1 = (a) => { if (!a.length) return 0; const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length * 0.25)]; };
  const texts = [], radii = [], leads = [], tracking = [];
  const fonts = {}, sizes = {}, colors = {}, bgs = {}, linkColors = {};
  const sel = 'h1,h2,h3,h4,p,a,button,span,li,blockquote,figcaption,label,div,article,section';
  for (const el of document.body.querySelectorAll(sel)) {
    const cs = getComputedStyle(el);
    const txt = (el.childNodes.length && [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
    const fs = parseFloat(cs.fontSize);
    if (txt && fs >= 9 && fs < 200) {
      texts.push(fs);
      const col = cs.color;
      if (col && col !== 'rgba(0, 0, 0, 0)') colors[col] = (colors[col] || 0) + 1;
      const fam = (cs.fontFamily || '').split(',')[0].replace(/["']/g, '').trim();
      if (fam) fonts[fam] = (fonts[fam] || 0) + 1;
      sizes[fs] = (sizes[fs] || 0) + 1;
      const ls = parseFloat(cs.letterSpacing);
      if (!isNaN(ls)) tracking.push(Math.round(ls * 100) / 100);
      const lh = parseFloat(cs.lineHeight);
      if (lh && fs) leads.push(Math.round((lh / fs) * 100) / 100);
    }
    if (el.children.length > 0) {
      const bgc = cs.backgroundColor;
      if (bgc && bgc !== 'rgba(0, 0, 0, 0)') bgs[bgc] = (bgs[bgc] || 0) + 1;
    }
    if (el.matches('a,button,[class*="btn"],[class*="link"],[class*="cta"]')) {
      const lc = cs.color; if (lc && lc !== 'rgba(0, 0, 0, 0)') linkColors[lc] = (linkColors[lc] || 0) + 1;
    }
    const br = parseFloat(cs.borderTopLeftRadius);
    if (br > 0 && br < 120 && el.getBoundingClientRect().width > 24) radii.push(br);
  }
  const top = (o) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([k]) => k);
  return {
    colors: Object.entries(colors).sort((a, b) => b[1] - a[1]).slice(0, 6),
    backgrounds: Object.entries(bgs).sort((a, b) => b[1] - a[1]).slice(0, 6),
    linkColors: Object.entries(linkColors).sort((a, b) => b[1] - a[1]).slice(0, 4),
    fonts: top(fonts), sizes: top(sizes).map(Number),
    radius: q1(radii), tracking: med(tracking), leading: med(leads),
    maxText: texts.length ? Math.max(...texts) : 0, minText: texts.length ? Math.min(...texts) : 0,
  };
}
"""


def contrast(a, b):
    def lum(c):
        def f(v):
            v /= 255
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        r, g, bl = (f(x) for x in c)
        return 0.2126 * r + 0.7152 * g + 0.0722 * bl
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def sat(c):
    mx, mn = max(c), min(c)
    return 0 if mx == 0 else (mx - mn) / mx


def rgb(css: str):
    m = re.findall(r"[\d.]+", css or "")
    if len(m) < 3:
        return None
    return tuple(int(float(v)) for v in m[:3])


def hexs(c):
    return "#" + "".join(f"{round(v):02x}" for v in c)


def palette_from_image(path: Path, k: int = 16):
    """Histogram of 8-step colour bins. Returns [(rgb, count)] most frequent first."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((320, 320))
    px = im.load()
    w, h = im.size
    counts = {}
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            key = ((r // 8) * 8 + 4, (g // 8) * 8 + 4, (b // 8) * 8 + 4)
            counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])[:k]


def pick_tokens(palette):
    total = sum(n for _, n in palette) or 1
    palette = [(c, n) for c, n in palette if n / total >= 0.0015] or palette
    bg = palette[0][0]
    ink = max((c for c, _ in palette), key=lambda c: contrast(c, bg))
    rest = [c for c, _ in palette if c != bg and c != ink]
    accent_pool = [c for c in rest if sat(c) > 0.15 and contrast(c, bg) > 1.6]
    accent = max(accent_pool, key=lambda c: sat(c) * 0.7 + min(contrast(c, bg), 7) / 7 * 0.3, default=None)
    if accent is None:
        accent = max(rest, key=sat) if rest else ink
    surface_pool = [c for c in rest if contrast(c, bg) < 2.2]
    surface = min(surface_pool, key=lambda c: abs(contrast(c, bg) - 1.35), default=bg)
    muted_pool = [c for c in rest if 2.2 <= contrast(c, bg) <= 6.5]
    muted = min(muted_pool, key=lambda c: abs(contrast(c, bg) - 4.5),
                default=tuple(round(bg[i] * 0.35 + ink[i] * 0.65) for i in range(3)))
    return {"bg": bg, "surface": surface, "ink": ink, "muted": muted, "accent": accent}


def pick_tokens_from_sample(sample, image_tokens):
    cols = [(rgb(c), n) for c, n in (sample.get("colors") or [])]
    cols = [(c, n) for c, n in cols if c]
    bgs = [(rgb(c), n) for c, n in (sample.get("backgrounds") or [])]
    bgs = [(c, n) for c, n in bgs if c]
    links = [(rgb(c), n) for c, n in (sample.get("linkColors") or [])]
    links = [(c, n) for c, n in links if c]
    bg = bgs[0][0] if bgs else image_tokens["bg"]
    ink = max((c for c, _ in cols), key=lambda c: contrast(c, bg), default=image_tokens["ink"])
    rest = [c for c, _ in cols if c != bg and c != ink]
    muted = min(rest, key=lambda c: abs(contrast(c, bg) - 4.5), default=image_tokens["muted"]) if rest else image_tokens["muted"]
    pool = [c for c, _ in (cols + links) if sat(c) > 0.15 and contrast(c, bg) > 1.6]
    accent = max(pool, key=sat, default=image_tokens["accent"]) if pool else image_tokens["accent"]
    surface_pool = [c for c, _ in bgs[1:] if c != bg and contrast(c, bg) < 2.2]
    surface = min(surface_pool, key=lambda c: abs(contrast(c, bg) - 1.35), default=image_tokens["surface"])
    return {"bg": bg, "surface": surface, "ink": ink, "muted": muted, "accent": accent}


def feel(bg, accent, max_text):
    dark = sum(bg) / 3 < 110
    hot = sat(accent) > 0.55
    if dark and hot:
        return ("technical / nightlife", "tight grotesque + mono labels, hard edges, glow used once",
                "neon-lit product photography on near-black, one coloured rim light, high contrast")
    if dark:
        return ("cinematic / editorial", "tight sans display with a mono for labels, wide air, soft depth",
                "low-key photography, deep navy shadows, a single warm or cyan highlight")
    if sat(accent) < 0.25:
        return ("quiet / institutional", "humanist sans body with a serif or grotesque display, generous leading",
                "natural light photography, muted tones, calm compositions")
    return ("editorial / warm", "serif display over a clean sans body, generous margins, small caps labels",
            "warm natural light, paper textures, muted earth tones with one bright accent")


def build_design(name, source, tokens, sample, feel_line):
    bg, surface, ink, muted, accent = (hexs(tokens[k]) for k in ("bg", "surface", "ink", "muted", "accent"))
    c_ink, c_muted, c_accent = contrast(tokens["ink"], tokens["bg"]), contrast(tokens["muted"], tokens["bg"]), contrast(tokens["accent"], tokens["bg"])
    sizes = sample.get("sizes") or []
    max_t = sample.get("maxText") or 0
    body = round(next((s for s in sizes if 14 <= s <= 20), 16))
    display = max_t or 64
    radius = sample.get("radius") or 16
    fonts = sample.get("fonts") or []
    display_font = fonts[0] if fonts else "Inter Tight"
    sans = [f for f in fonts if "mono" not in f.lower()]
    body_font = sans[1] if len(sans) > 1 else (sans[0] if sans else display_font)
    tracking = sample.get("tracking") or 0
    tracking_em = (tracking / display) if display else 0
    leading = sample.get("leading") or 1.5
    name_line = f" — {name}" if name else ""
    return f"""# DESIGN.md{name_line}

> Extracted from `{source}` on {dt.date.today().isoformat()} with `tools/style_ref.py`.
> A starting point, not a copy of the reference's brand. Keep the structure — background, surface, ink,
> muted, **one** accent — and change the values to the brief. Never copy the reference's logo, copy or photos.

## Palette

| Token | Value | Contrast on bg | Use |
|---|---|---|---|
| `--bg` | `{bg}` | — | page background |
| `--surface` | `{surface}` | {contrast(tokens['surface'], tokens['bg']):.2f}:1 | cards, panels, sticky bars |
| `--ink` | `{ink}` | {c_ink:.2f}:1 | headings and body |
| `--muted` | `{muted}` | {c_muted:.2f}:1 | secondary text, labels |
| `--accent` | `{accent}` | {c_accent:.2f}:1 | one accent: links, key CTA, one word in the hero |

```css
:root {{
  --bg: {bg};
  --surface: {surface};
  --ink: {ink};
  --muted: {muted};
  --accent: {accent};
  --accent-ink: {ink if contrast(tokens['ink'], tokens['accent']) >= contrast(tokens['bg'], tokens['accent']) else bg};
  --line: color-mix(in srgb, {ink} 14%, transparent);
  --font-display: "{display_font}", ui-sans-serif, system-ui, sans-serif;
  --font-body: "{body_font}", ui-sans-serif, system-ui, sans-serif;
  --text-xs: 12px;
  --text-sm: 14px;
  --text-md: {body}px;
  --text-lg: clamp(20px, 2.2vw, 28px);
  --text-xl: clamp(32px, 4.4vw, 56px);
  --text-2xl: clamp({max(40, int(display * 0.6))}px, {max(5, round(display / 14))}vw, {int(display)}px);
  --tracking-display: {tracking_em:.3f}em;
  --leading-body: {leading:.2f};
  --radius-sm: {max(4, int(radius / 2))}px;
  --radius-md: {int(radius)}px;
  --radius-lg: {max(int(radius * 1.6), 20)}px;
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --spring: cubic-bezier(.34, 1.56, .64, 1);
}}
```

## Type

- **Display:** `{display_font}`, weight 600, tracking `{tracking_em:.3f}em`, line-height ~1.02. Sizes: `{int(display)}px` hero, `clamp()` for the rest.
- **Body:** `{body_font}`, {body}px, line-height `{leading:.2f}`, max measure ~62ch.
- **Labels:** the same body family at 12 px, uppercase, `0.12em` tracking — or a mono if the reference uses one.

Measured on the reference: display ≈ {int(display)}px, body ≈ {body}px, letter-spacing ≈ {tracking:.2f}px,
median radius ≈ {int(radius)}px. Treat these as the reference's *rhythm*, not its exact values.

## Shape

- Radius: `{max(4, int(radius / 2))}` / `{int(radius)}` / `{max(int(radius * 1.6), 20)}` px. Cards and media use the middle value.
- Borders: 1 px `--line`; never a heavy drop shadow on a dark surface — a soft glow only on the one element that moves.
- Grid: 12 columns, `clamp(20px, 4vw, 48px)` gutters, `max-width: 1240px`.

## Motion language (3–5 named moves — reuse them everywhere)

| Move | Trigger | Duration | Easing | Where |
|---|---|---|---|---|
| arrive | entrance / scroll | 700–900 ms | `--ease-out` | headings, cards |
| lift | hover / focus | 300–450 ms | `--ease-out` | cards, buttons |
| settle | leave | 500–700 ms | `--spring` | magnetic CTA, tilt cards |
| scrub | scroll-linked | lerp 0.12–0.16 | linear | pinned hero, path draw |

Rules: one big moment per screen, nothing over 1.4 s, only `transform` / `opacity` / `filter`,
`prefers-reduced-motion` turns every move into a still state.

## Feel

**{feel_line[0]}.** {feel_line[1]}.

## Image style prompt

> {feel_line[2]}. Consistent art direction across the whole set; no text in images; export WebP/AVIF at
> display size, hero ≤ 250 KB, everything else ≤ 150 KB.

## Open questions for the human

- [ ] Is the accent the brand colour, or should it be?
- [ ] Which two type families are licensed for this project?
- [ ] Do we have real photography, or do we generate it in the style above?
- [ ] Any factual claims (prices, results, clients) that must be checked before launch?
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract a DESIGN.md token sheet from a reference.")
    ap.add_argument("source", help="URL or a screenshot (.png/.jpg/.webp)")
    ap.add_argument("--out", default="DESIGN.md", help="output file (default DESIGN.md)")
    ap.add_argument("--name", default="", help="project name for the heading")
    ap.add_argument("--mobile", help="optional second screenshot (mobile) to include in the palette")
    a = ap.parse_args()

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shots = []
    sample = {}
    source = a.source
    url, httpd = a.source, None
    if not url.startswith(("http://", "https://", "file://")):
        if not Path(url).exists():
            sys.exit(f"not a URL and not a local path: {url}")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from qa import serve_local
        url, httpd = serve_local(url)

    if url.startswith(("http://", "https://")):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            sys.exit("URL mode needs Playwright: pip install playwright && python3 -m playwright install chromium")
        from PIL import Image
        tmp = out.parent / "_style_ref"
        tmp.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            page = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1).new_page()
            page.goto(url, wait_until="load", timeout=45000)
            page.wait_for_timeout(1800)
            page.screenshot(path=str(tmp / "desktop.png"))
            sample = page.evaluate(SAMPLE_JS)
            b.close()
        shots.append(tmp / "desktop.png")
    else:
        p = Path(a.source)
        if not p.exists():
            sys.exit(f"not found: {p}")
        shots.append(p)

    if a.mobile and Path(a.mobile).exists():
        shots.append(Path(a.mobile))

    counts = {}
    for shot in shots:
        for c, n in palette_from_image(shot):
            counts[c] = counts.get(c, 0) + n
    palette = sorted(counts.items(), key=lambda kv: -kv[1])[:10]
    if not palette:
        sys.exit("could not read any pixels from the reference")
    tokens = pick_tokens(palette)
    if sample.get("colors"):
        tokens = pick_tokens_from_sample(sample, tokens)
    feel_line = feel(tokens["bg"], tokens["accent"], sample.get("maxText") or 64)
    text = build_design(a.name, source, tokens, sample, feel_line)
    if httpd:
        httpd.shutdown()
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}")
    print(json.dumps({k: hexs(v) for k, v in tokens.items()}, indent=1))
    print("measured:", json.dumps(sample))


if __name__ == "__main__":
    main()
