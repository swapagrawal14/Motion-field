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
| A browser-capable shell: `python3` + `pip install playwright && playwright install chromium` (or Node + `npx playwright`) | screenshots and QA gates (`tools/qa.py`) | `python3 tools/qa.py --help` |
| A static server | preview | `python3 -m http.server 8080` |
| An **image generator** that takes **reference images** (first ref = style to copy) | hero art, section art, textures, product shots in ONE consistent style | generate one test image first |
| `cwebp` or Pillow / ImageMagick | convert every raster to WebP/AVIF under budget | `cwebp -version` or `python3 -c "import PIL"` |
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
2. **Art direction (write it down in `DESIGN.md`).** Palette (bg, surface, ink, muted, 1 accent, 1 support),
   type pair + scale (clamp() sizes), radius + border + shadow rules, image style prompt, motion language
   (3–5 named moves you will reuse, their durations and easings). One system, used everywhere.
3. **Assets.** Generate the hero image first, check it, then pass it as the **first reference** to every later
   image so the set matches. Export WebP/AVIF at the size it displays (×2 for retina, max ~2400 px), hero
   ≤ 250 KB, others ≤ 150 KB, video ≤ 2 MB with a poster. Give every image `width`/`height` and `alt`.
4. **Build section by section.** Static layout and real content first, all breakpoints, no motion. Use the
   layout map in SKILL.md. Screenshot each section at 1440 and 390 before moving on.
5. **Motion pass.** Add moves from `recipes/` (each has a demo, README and `prompt.md`). Every move needs a
   reason (guide the eye, show cause and effect, reward an action). One hero-scale moment per screen, the rest
   quiet. Wire `prefers-reduced-motion` as you go, not at the end.
6. **QA** (§4), fix, repeat. Then show the human screenshots + a local link or a preview build, and wait.

Send progress (art direction, first section screenshots, motion pass). An hour of silence then a finished site
is worse than three check-ins.

## 4. QA gates (every page, before the human sees it)

Run `python3 tools/qa.py http://localhost:8080/ --out qa/` (screens at 1440×900 and 390×844, at 0 / 25 / 50 /
75 / 100 % scroll, plus a reduced-motion pass and a contact sheet). Then **open the contact sheet and look at it.**
Fail a gate → fix it, don't hide it.

**A. Visual.** Nothing clipped, overlapping or cut mid-word; headings don't orphan one word; images not
stretched; sections look designed at both widths, not just stacked. Compare side by side with the reference
screenshots: same visual system?

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
templates/          starter pages that combine recipes (landing, portfolio)
tools/qa.py         screenshot + QA gate runner (playwright)
index.html, app.js, styles.css, assets/   the Motion Field showcase site itself
```
