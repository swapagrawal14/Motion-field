#!/usr/bin/env python3
"""Four art directions before you build — like the treatments menu in a video director.

    python3 tools/treatments.py --name acme --brief "A dental clinic in Udaipur" --out treatments/acme
    python3 tools/treatments.py --name acme --only midnight,pop

Writes four complete DESIGN.md token sheets (A · Midnight, B · Paper, C · Pop, D · Sunny) plus a README.md
that compares them. The human picks one; the agent builds only that one. Copy the chosen folder's
DESIGN.md to the site root and delete the rest.

Each treatment is a full system: palette, type scale, shape rules, a motion language and an image
prompt. Change the values to the brief — do not copy the reference's brand.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

TREATMENTS = {
    "midnight": {
        "label": "A · Midnight signal",
        "tagline": "Cinematic navy, one cyan accent, tight type. The Motion Field house style.",
        "works": "SaaS launches, studios, portfolios, product pages that need a strong opening.",
        "bg": "#070d1a", "surface": "#0e1830", "ink": "#e8eff9", "muted": "#95a3bf",
        "accent": "#3fdcff", "accent_ink": "#03141d", "line": "rgba(150,180,235,.14)",
        "display": "Inter Tight", "body": "Inter Tight", "mono": "JetBrains Mono",
        "display_weight": 600, "body_weight": 400, "tracking": "-0.045em", "body_tracking": "-0.01em",
        "leading": 1.6, "radius": 22, "radius_lg": 32,
        "moves": [("pinned hero shrink", "scroll", "lerp 0.14", "hero"),
                  ("marquee", "time", "34 s loop", "proof band"),
                  ("card tilt", "pointer", "0.55 s", "work cards"),
                  ("magnetic CTA", "pointer", "lerp 0.16", "primary action")],
        "image": "low-key product photography, deep navy shadows, a single cyan rim light, high contrast, "
                 "no text, consistent 35mm framing",
        "avoid": "neon purple gradients, glassmorphism everywhere, more than one glow per screen",
    },
    "paper": {
        "label": "B · Paper editorial",
        "tagline": "Warm off-white, ink black, one vermilion. Serif display, generous margins.",
        "works": "Clinics, studios, editorial sites, portfolios with a lot of writing.",
        "bg": "#f4efe6", "surface": "#fffdf8", "ink": "#1a1712", "muted": "#6b6357",
        "accent": "#d4502e", "accent_ink": "#fff8f2", "line": "rgba(26,23,18,.14)",
        "display": "Fraunces", "body": "Inter", "mono": "JetBrains Mono",
        "display_weight": 500, "body_weight": 400, "tracking": "-0.02em", "body_tracking": "0",
        "leading": 1.65, "radius": 4, "radius_lg": 8,
        "moves": [("soft-focus reveal", "entrance", "0.7 s", "sections"),
                  ("SVG path draw", "scroll", "lerp 0.12", "process"),
                  ("letter stagger", "entrance", "26 ms/char", "titles"),
                  ("hover pulse", "hover/focus", "1.15 s ring", "cards")],
        "image": "natural window light, paper texture, muted earth tones, one vermilion accent object, "
                 "editorial 50mm framing, no text",
        "avoid": "pure white backgrounds, heavy shadows, neon accents, rounded-everything",
    },
    "pop": {
        "label": "C · Signal pop",
        "tagline": "Near-black, acid lime, hard grotesque. Loud on purpose, quiet in the layout.",
        "works": "Launches, events, music and culture, anything that should feel like a poster.",
        "bg": "#0b0b0d", "surface": "#16161a", "ink": "#f5f5f2", "muted": "#8a8a90",
        "accent": "#c6ff3d", "accent_ink": "#10120a", "line": "rgba(245,245,242,.14)",
        "display": "Space Grotesk", "body": "Inter", "mono": "IBM Plex Mono",
        "display_weight": 700, "body_weight": 400, "tracking": "-0.03em", "body_tracking": "0",
        "leading": 1.55, "radius": 999, "radius_lg": 28,
        "moves": [("text scramble", "hover/entrance", "0.6 s", "nav and labels"),
                  ("infinite marquee", "time", "26 s loop", "ticker"),
                  ("shader background", "time", "pauses offscreen", "hero"),
                  ("magnetic button", "pointer", "lerp 0.16", "CTA")],
        "image": "hard flash photography, acid lime gel light on near-black, glossy surfaces, "
                 "poster framing, no text",
        "avoid": "pastel gradients, thin serif type, soft shadows, more than two accent moments per screen",
    },
    "sunny": {
        "label": "D · Sunny cast",
        "tagline": "Powder blue, cream and coral. Chunky rounded type, flat illustration, bouncy spring motion.",
        "works": "Kids, pets, food, learning, community — anything that should feel like a picture book, not a SaaS page.",
        "bg": "#a9bdd6", "surface": "#f6efe3", "ink": "#2a2118", "muted": "#5f6b7d",
        "accent": "#e2604a", "accent_ink": "#fff6f2", "line": "rgba(42,33,24,.16)",
        "display": "Baloo 2", "body": "Nunito", "mono": "DM Mono",
        "display_weight": 700, "body_weight": 400, "tracking": "-0.02em", "body_tracking": "0",
        "leading": 1.6, "radius": 26, "radius_lg": 40,
        "moves": [("choreographed cast entrance", "entrance", "spring 0.7 s, 80 ms stagger", "hero characters"),
                  ("typewriter headline", "entrance", "45 ms/char", "hero title"),
                  ("ambient bob", "time", "3–6 s loops, pauses offscreen", "floating cast"),
                  ("poke on hover", "hover/focus", "spring 0.4 s", "each character"),
                  ("sticky-tape wobble", "scroll", "lerp 0.12", "section titles")],
        "image": "flat vector illustration, thick dark outlines, flat pastel fills, cream paper background, "
                 "simple shapes, no gradients, no text",
        "avoid": "dark glass panels, thin serif type, neon glow, 3D renders, more than 5 characters on screen",
    },
}


def design_md(key: str, t: dict, brief: str) -> str:
    moves = "\n".join(f"| {m} | {tr} | {d} | {w} |" for m, tr, d, w in t["moves"])
    return f"""# DESIGN.md — {t['label']}

> Treatment **{t['label']}** for **{brief}** · generated {dt.date.today().isoformat()} by `tools/treatments.py`.
> Pick one treatment and delete the others. Change the values to the brief; never copy a reference's brand.

**{t['tagline']}**

Works for: {t['works']}

## Palette

```css
:root {{
  --bg: {t['bg']};
  --surface: {t['surface']};
  --ink: {t['ink']};
  --muted: {t['muted']};
  --accent: {t['accent']};
  --accent-ink: {t['accent_ink']};
  --line: {t['line']};
  --font-display: "{t['display']}", ui-sans-serif, system-ui, sans-serif;
  --font-body: "{t['body']}", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "{t['mono']}", ui-monospace, monospace;
  --text-xs: 12px;
  --text-sm: 14px;
  --text-md: 16px;
  --text-lg: clamp(20px, 2vw, 26px);
  --text-xl: clamp(34px, 4.6vw, 60px);
  --text-2xl: clamp(48px, 7vw, 104px);
  --tracking-display: {t['tracking']};
  --tracking-body: {t['body_tracking']};
  --leading-body: {t['leading']};
  --radius-sm: {max(2, int(t['radius'] * 0.4)) if t['radius'] < 100 else 12}px;
  --radius-md: {t['radius']}px;
  --radius-lg: {t['radius_lg']}px;
  --ease-out: cubic-bezier(.16, 1, .3, 1);
  --spring: cubic-bezier(.34, 1.56, .64, 1);
}}
```

Accent budget: the accent covers **under 10%** of any screen. It is the one thing that moves, not the
wallpaper.

## Type

- **Display** `{t['display']}` {t['display_weight']} · tracking `{t['tracking']}` · line-height 1.02 · `--text-2xl` for the hero, `--text-xl` for sections.
- **Body** `{t['body']}` {t['body_weight']} · `{t['leading']}` line-height · max 62ch · `--text-md`.
- **Labels** `{t['mono']}` 12 px uppercase, `0.12em` tracking.
- Scale: 12 / 14 / 16 / 20–26 / 34–60 / 48–104. Nothing in between; if you need another size, you need another hierarchy level.

## Shape

- Radius `{t['radius']}px` for cards and media, `{t['radius_lg']}px` for hero frames.
- Borders 1 px `--line`; shadows only on the one element that lifts.
- Grid 12 columns, `clamp(20px, 4vw, 48px)` gutters, max width 1240 px.

## Motion language

| Move | Trigger | Duration / lerp | Where |
|---|---|---|---|
{moves}

Rules: one big moment per screen; nothing over 1.4 s; only `transform` / `opacity` / `filter`;
`prefers-reduced-motion` turns every move into a still state.

## Image style prompt

> {t['image']}. Export WebP/AVIF at display size, hero ≤ 250 KB, others ≤ 150 KB, `width`/`height` on every image.

## Avoid

{t['avoid']}.

## Open questions

- [ ] Which treatment did the human pick? (delete the other two folders)
- [ ] Is the accent the brand colour?
- [ ] Real photography or generated in the style above?
- [ ] Factual claims (prices, results, credentials) checked before launch?
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Write three art-direction treatments as DESIGN.md files.")
    ap.add_argument("--name", required=True, help="project slug (used in the heading)")
    ap.add_argument("--brief", default="a new site", help="one line about the project")
    ap.add_argument("--out", default="", help="output folder (default treatments/<name>)")
    ap.add_argument("--only", default="", help="comma-separated treatment keys (default: all three)")
    a = ap.parse_args()

    out = Path(a.out) if a.out else Path("treatments") / a.name
    keys = [k.strip() for k in a.only.split(",") if k.strip()] or list(TREATMENTS)
    for k in keys:
        if k not in TREATMENTS:
            raise SystemExit(f"unknown treatment: {k} (available: {', '.join(TREATMENTS)})")
        folder = out / f"{k}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "DESIGN.md").write_text(design_md(k, TREATMENTS[k], a.brief), encoding="utf-8")
        print("wrote", folder / "DESIGN.md")

    rows = "\n".join(
        f"| **{TREATMENTS[k]['label']}** | {TREATMENTS[k]['tagline']} | {TREATMENTS[k]['works']} | [`{k}/DESIGN.md`]({k}/DESIGN.md) |"
        for k in keys)
    (out / "README.md").write_text(f"""# Treatments — {a.name}

Three art directions for **{a.brief}**. Pick **one**, copy its `DESIGN.md` to the site root, and delete
the other two folders. Do not blend them: a site with two systems has none.

| Treatment | In one line | Works for | Files |
|---|---|---|---|
{rows}

## How to choose

- **A · Midnight** if the site needs a cinematic opening and a strong product moment.
- **B · Paper** if the site is mostly writing, services or trust (clinics, studios, editorial).
- **C · Pop** if the site is an event, a launch or a cultural thing that should feel like a poster.

Reply with the letter (A / B / C). The build starts only after that.
""", encoding="utf-8")
    print("wrote", out / "README.md")


if __name__ == "__main__":
    main()
