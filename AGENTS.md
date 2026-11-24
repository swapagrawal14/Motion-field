# AGENTS.md — quickstart for AI agents

You were given this repo and asked for a website or web app. This page is the whole loop: what you need, what to
ask, the pipeline, the QA gates every page must pass, and the rules. The craft (motion principles, layout map,
art direction) is in [SKILL.md](SKILL.md); read it once before you start. Ready-made pieces are in
[recipes/](recipes/INDEX.md) and [templates/](templates/).

**Goal:** an outstanding, fast, accessible site where motion *explains and rewards* (things move because the
reader did something: scrolled, hovered, clicked), with one strong visual system from top to bottom. Not a
generic template with fade-ins sprinkled on.

---

## 1. Prerequisites

| Need | Why | Check |
|---|---|---|
| A browser-capable shell: `python3` + `pip install playwright pillow && python3 -m playwright install chromium` (on a bare Linux box also `sudo python3 -m playwright install-deps chromium`) | screenshots and QA gates (`tools/qa.py`) | `python3 tools/qa.py --help` |
| A static server | preview | `python3 -m http.server 8080` |
| An **image generator** that takes **reference images** (first ref = style to copy) | hero art, section art, textures, product shots in ONE consistent style | generate one test image first |
| `cwebp` or Pillow / ImageMagick | convert every raster to WebP/AVIF under budget | `cwebp -version` or `python3 -c "import PIL"` |
| Optional: `ffmpeg` + `ffprobe` | `tools/frames.py video` → scroll-scrub frame sequences | `ffmpeg -version` |
| Optional: `numpy` | `tools/sfx.py` → WAV previews of the sound kit | `python3 -c "import numpy"` |
| Optional: a framework (Next.js, Astro, Vite+React) | only if the human wants one; every recipe here is vanilla and ports 1:1 | |

**Never hard-code an API key** in code, commits or messages; read it from the environment. No image generator?
Say so up front and offer: real photos the human supplies, CSS/shader art, or typographic design. Never ship
broken `<img>` paths or placeholder stock you invented.

## 2. Ask the human first (one short message)

1. **Purpose + one action.** What is the site for and what should a visitor do (book, buy, sign up, hire, play)?
2. **Audience.** Who visits, on what device? (default: mobile-first, desktop-polished)
3. **Vibe + references.** 1–3 sites or images they love (e.g. "like scrolltide.co"). Ask what they like about each.
4. **Stack + hosting.** Plain HTML/CSS/JS (default, zero build) or React/Next/Astro? Where will it live?
5. **Content + assets.** Real copy, logo, photos, brand colours, credit line exactly as they want it. Anything
   factual (prices, medical, legal) they must check before launch.

Offer a default for each so a one-word answer works. Don't ask more; decide the rest yourself.

## 3. Pipeline

Work in a new folder (e.g. `sites/<name>/`) or copy the closest starter from `templates/`.

1. **Reference teardown.** For each reference: screenshot it at 1440 and 390 (`tools/qa.py <url>`), then write
   ten lines: palette (hex), type (families, sizes, weights, tracking), grid + spacing, corner radii, imagery
   style, section order, and its **motion language** (what moves, on which trigger, how fast, which easing).
2. **Art direction (write it down in `DESIGN.md`).** No reference yet? Run
   `python3 tools/treatments.py --name <slug> --brief "..."` — it writes three complete `DESIGN.md` art
   directions (A · Midnight, B · Paper, C · Pop). **Show the human all three and wait for a letter before
   building.** Have a reference? `python3 tools/style_ref.py <url-or-screenshot> --out DESIGN.md` reads its
   palette, type ladder, letter-spacing and radii into tokens — then confirm them with the human.
   The file must contain: palette (bg, surface, ink, muted, 1 accent, 1 support), type pair + scale
   (clamp() sizes), radius + border + shadow rules, image style prompt, and 3–5 named moves with durations
   and easings. One system, used everywhere.
3. **Assets.** Generate the hero image first, check it, then pass it as the **first reference** to every later
   image so the set matches. Export WebP/AVIF at the size it displays (×2 for retina, max ~2400 px), hero
   ≤ 250 KB, others ≤ 150 KB, video ≤ 2 MB with a poster. Give every image `width`/`height` and `alt`.
   For a scroll-scrub hero: `python3 tools/frames.py video hero.mp4 --out <site>/frames --count 24`
   (or `demo` to render the built-in turntable) → WebP sequence + poster + `manifest.json`; keep it under
   ~30 frames.
4. **Build section by section.** Static layout and real content first, all breakpoints, no motion. Use the
   layout map in SKILL.md. Screenshot each section at 1440 and 390 before moving on.
5. **Motion pass.** Add moves from `recipes/` (each has a demo, README and `prompt.md`). Every move needs a
   reason (guide the eye, show cause and effect, reward an action). One hero-scale moment per screen, the rest
   quiet. Wire `prefers-reduced-motion` as you go, not at the end.
6. **QA** (§4), fix, repeat. Then show the human screenshots + a local link or a preview build, and wait.
   Record a scroll-through for review and the README with `python3 tools/qa.py <target> --record qa/scroll.mp4`.
   For a launch promo, `python3 tools/trailer.py <target> --out trailer.mp4 --title "..."` records a 15 s
   title card → scroll → end card reel (MP4 needs ffmpeg; otherwise WebM).

Send progress (art direction, first section screenshots, motion pass). An hour of silence then a finished site
is worse than three check-ins.

## 4. QA gates (every page, before the human sees it)

Run `python3 tools/qa.py http://localhost:8080/ --out qa/` (or pass a local folder/file, e.g.
`python3 tools/qa.py templates/landing/`, and it serves it for you). It takes screens at 1440×900 and 390×844 at
0 / 25 / 50 / 75 / 100 % scroll, runs a reduced-motion pass, builds `qa/contact-sheet.png`, and writes
`qa/report.md` + `qa/report.json` (console errors, failed requests, overflow culprits, LCP on a throttled mobile
load, page weight). Exit code 1 = a gate failed. Then **open the contact sheet and look at it.**
Fail a gate → fix it, don't hide it. (`--ignore-host <cdn>` only for hosts your sandbox blocks, never to hide real 404s.)

**A. Visual.** Nothing clipped, overlapping or cut mid-word; headings don't orphan one word; images not
stretched; sections look designed at both widths, not just stacked. Compare side by side with the reference
screenshots: same visual system?

**A2. Design lint.** Run `python3 tools/design_lint.py <target> --out qa/lint`: accent under 10% of the
viewport, no more than one pinned section visible at once, no transition or `@keyframes` animating
`top/left/width/height/margin`, no finite motion over 1.4 s. Fix the cause; don't raise the budgets.

**B. Console clean.** Zero errors and zero failed requests (404 fonts/images, CORS). `qa.py` lists them.

**C. No horizontal overflow** at 390 and 1440 (`scrollWidth <= innerWidth`). Marquees, tilted cards and
off-canvas menus are the usual suspects: clip them with `overflow: clip` on their section.

**D. Contrast.** Body text ≥ 4.5:1, large text ≥ 3:1, including text over images/video/shaders (add a scrim).
Visible focus ring on every interactive element; tab through the page once.

**E. Reduced motion.** With `prefers-reduced-motion: reduce`: no smooth-scroll hijack, no pinning, no loops,
no parallax; content still fully visible (nothing stuck at `opacity: 0`). `qa.py` screenshots this pass.

**F. Performance budget.** LCP < 2.5 s on a fast-3G-ish profile (`qa.py` reports LCP and page weight);
first-load page weight ≤ ~2.5 MB; no image > 300 KB; fonts ≤ 2 families, `font-display: swap`;
`loading="lazy"` below the fold; **pause offscreen video, canvas and WebGL loops** (IntersectionObserver +
`visibilitychange`); cap devicePixelRatio at 1.5–2 for canvases; animate only `transform`, `opacity`, `filter`.

**G. Mobile behaviour.** Tap targets ≥ 44 px, no hover-only information, pointer effects off on touch,
pinned sections shorter on mobile, menu works.

## 5. Rules

- **Sound is opt-in.** Any audio (UI sound kit, background music) ships **muted by default** with a visible
  toggle; one sound at a time; peaks under 0.2. Never autoplay.
- **Never deploy, publish, push to a public repo, or post anything in the owner's name without asking first.**
  Show screenshots / a local preview and wait for an explicit yes.
- **When the human gives a reference, match the reference's visual system** (palette, type, spacing, motion
  language). Never reskin their old look with new colours and call it done. If they want both, ask which wins.
- When editing an existing site: keep its stack, components and content; add, don't redesign, unless asked.
- Credit exactly as the owner specifies (e.g. "Swapnil Agrawal (BDS intern)").
- Real content only: never invent testimonials, client logos, stats or prices. Use clearly marked placeholders.
- Don't commit secrets, other people's reference images, or unoptimised source art.
- Motion is never the only way to get information, and nothing traps the scroll.

## 6. Repo map

```text
SKILL.md            craft: approach, motion principles, layout map, art direction
recipes/INDEX.md    every recipe: when to use, weight, dependencies
recipes/<name>/     index.html (live demo) + README.md (when/how) + prompt.md (copy-ready prompt)
templates/          starter pages that combine recipes (landing, portfolio, event, product-launch)
tools/qa.py         screenshot + QA gate runner; --record writes a scroll MP4/WebM
tools/design_lint.py accent budget, pinned sections, layout animation, duration gates
tools/frames.py     video (ffmpeg) or built-in turntable → WebP frame sequence + poster
tools/style_ref.py  reference URL/screenshot → DESIGN.md tokens (palette, type, radii)
tools/treatments.py three art directions (A/B/C) as DESIGN.md files
tools/trailer.py     15 s site trailer: title card + scroll-through + end card (MP4 with ffmpeg)
tools/sfx.py        renders the UI sound kit to WAV (the WebAudio version is assets/ui-sound.js)
assets/ui-sound.js  procedural WebAudio sound kit, muted by default
index.html, app.js, styles.css, assets/   the Motion Field showcase site itself
```
