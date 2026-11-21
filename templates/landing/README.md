# Landing template — midnight navy + cyan

A product / launch landing page in the scrolltide.co visual language: midnight navy, one cyan accent, heavy
tight sans (Inter Tight 700–800), mono labels (JetBrains Mono), soft glass surfaces. **Every visual is CSS,
inline SVG or a 2D canvas: no image files.** No build step.

```text
templates/landing/
  index.html      markup; every editable string carries data-swap="…"
  css/style.css   tokens at the top (:root), then one block per section
  js/main.js      all motion; each move checks reduced motion + fine pointer
```

Preview: `python3 -m http.server 8080` from the repo root → `http://localhost:8080/templates/landing/`.
QA: `python3 tools/qa.py templates/landing/ --out qa/landing`.

## Sections and their moves

| # | Section | Element hooks | Move (recipe) |
|---|---|---|---|
| — | Nav (glass pill) | `[data-nav]` | hides on scroll down, returns on scroll up; entrance fade |
| 1 | Hero | `[data-hero]`, `[data-hero-stage]`, `[data-split]`, `[data-tide]`, `[data-device]` | **pinned hero shrink** (stage scales to a rounded card, copy lifts away: `pinned-hero-shrink`), **word stagger** on load (`letter-stagger`, word level), procedural tide-line canvas that bends toward the pointer, 3D glass product mock (≥1200 px) with pointer tilt and an SVG chart line that draws in |
| 2 | Marquee | `[data-marquee]` | two-row **infinite marquee**, opposite directions, pause on hover; track cloned in JS (`marquee`) |
| 3 | Features | `[data-stagger]`, `[data-glow]` | **staggered reveal** of 3 cards, headings blur in (`blur-reveal`), pointer-follow glow on hover (`hover-pulse` family) |
| 4 | Showcase | `[data-wall]`, `[data-wall-plane]`, `[data-col]` | **tilted 3D card wall**: plane un-tilts as you scroll, columns drift in opposite directions, gentle pointer tilt (`card-wall-3d`, `card-tilt`) |
| 5 | How it works | `[data-steps]`, `[data-rail]` | scrubbed progress rail + staggered step cards (swap for `svg-path-draw` if you want a drawn line) |
| 6 | CTA | `[data-magnetic]`, `[data-magnetic-label]` | **magnetic button**: the round CTA and its label follow the pointer inside a padded zone, then spring home (`magnetic-button`) |
| — | Footer | `[data-wordmark]` | big gradient wordmark with slow parallax; credit line |

Smooth scroll is **Lenis** (`window.lenis`, driven by `tools/qa.py`) synced to GSAP ScrollTrigger. CDN deps:
`gsap@3.12.5`, `ScrollTrigger`, `lenis@1.1.13`, Google Fonts. ~130 KB of minified JS (~50 KB gzipped).

## How an agent adapts it

1. **Copy** the folder to `sites/<name>/` (don't edit the template in place).
2. **Tokens.** Edit `:root` in `css/style.css`. Keep the structure: `--bg`, `--surface`, `--ink`, `--muted`, one
   `--accent` (+ `--accent-2` used only inside gradients). Change the two font families in the `<link>` and
   `--font` / `--mono`. If the brand isn't navy/cyan, also update the hard-coded rgba accents
   (search `45, 226, 255` and `45,226,255`) and the tide colours in `js/main.js` (`rgba(45,226,255` / `rgba(120,160,255`).
3. **Copy.** Every placeholder string has `data-swap="key"` (e.g. `hero.title`, `feature.2.body`, `cta.button`).
   Replace the text, keep the attribute or delete it. Copy here is deliberately generic and says
   "Placeholder": **never ship it, and never invent stats, testimonials, client logos or prices**: ask the owner.
   The hero title is split into words by JS; the **last word** is tinted cyan, so end on the word you want lit.
4. **Swap points (visuals).**
   - Hero background: `[data-tide]` canvas. Replace with the `shader-background` recipe or a poster image; keep the
     `.hero__stage::after` scrim for text contrast.
   - Hero mock `[data-device]`: replace `.dev--front` contents with a real `<img>` screenshot (WebP ≤ 150 KB,
     width/height set) or delete the block.
   - Card wall tiles (`.tile.t-*`): replace each `<div class="tile …">` with
     `<div class="tile"><img src="…" alt="" width="800" height="600" loading="lazy"></div>` and add
     `.tile img{width:100%;height:100%;object-fit:cover}`. 5 columns × 3 tiles; odd columns drift up, even down (`data-col="-1|1"`).
   - Marquee: edit row 1 (`data-swap="marquee.N"`); row 2 is decorative and `aria-hidden`. For logos, put the owner's
     real logo SVGs in `.marquee__track` with `alt` text and drop the `.o` outline class.
5. **Add / remove sections.** Each `<section>` is independent. Reveals hook onto `[data-reveal]` (single
   element) and `[data-stagger]` (animates its children). Don't add a second pinned section right after the hero.
6. **Links.** Nav anchors use `#features`, `#showcase`, `#process`, `#cta`; Lenis smooth-scrolls any `a[href^="#"]`.
7. **Credit.** Keep `Designed & built by Swapnil Agrawal (BDS intern)` in the footer unless the owner says otherwise.
8. **QA** with `tools/qa.py` and look at the contact sheet before showing anyone.

## Knobs

| What | Where | Default |
|---|---|---|
| Hero pin length | `end: desktop ? '+=90%' : '+=45%'` in `main.js` | 90 % / 45 % of viewport |
| Hero shrink amount | `scale: 0.86 / 0.92`, `borderRadius: 36 / 24` | |
| Wall tilt range | `--rx 48→22deg`, `--rz -20→-8deg` | |
| Column drift | `y: dir * ±120` | 120 px each way |
| Magnet strength | `dx * 0.35` (button), `dx * 0.18` (label), zone = `.cta__actions` padding | 30 px zone |
| Marquee speed | `.marquee__row { animation: marquee 34s … }`, row 2 `40s` | |
| Tide density | `lines = w < 600 ? 22 : 34` | |

## Accessibility, reduced motion, performance

- `prefers-reduced-motion: reduce` → no Lenis, no pin, no scrub, no marquee loop, no canvas loop (one still
  frame), no magnet; all content visible. The hero's hidden-before-entrance state only applies when a `<head>`
  script adds `html.motion`, and is removed after 2.5 s if GSAP never loads, so a CDN failure can't hide text.
- Pointer effects (tide pull, device tilt, card glow, wall tilt, magnet) only run on `(hover: hover) and (pointer: fine)`.
- Tide canvas pauses offscreen (IntersectionObserver) and on hidden tabs; DPR capped at 1.75.
- Marquee and wall sections use `overflow: clip`; `body` has `overflow-x: clip`. No horizontal overflow at 390 px.
- Skip link, visible cyan focus ring, 44 px+ tap targets, decorative layers `aria-hidden`, word-split title keeps
  an `aria-label` with the full sentence.

## Known limits

- Fonts and libraries come from CDNs; self-host them for production or offline use.
- The wall is decorative (`aria-hidden`). If you put real screenshots there that carry information, remove
  `aria-hidden` and give each image real `alt` text.
