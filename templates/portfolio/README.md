# Portfolio template — midnight navy + cyan

A creative portfolio in the Motion Field house style: midnight navy, one cyan accent, heavy tight sans
(Inter Tight 600), mono labels (JetBrains Mono). **Every visual is CSS, inline SVG or a 2D canvas — no
image files.** No build step.

```text
templates/portfolio/
  index.html      markup; every editable string carries data-swap="…"
  css/style.css   tokens at the top (:root), then one block per section
  js/main.js      all motion; each move checks reduced motion + fine pointer
```

Preview: `python3 -m http.server 8080` from the repo root → `http://localhost:8080/templates/portfolio/`.
QA: `python3 tools/qa.py templates/portfolio/ --out qa/portfolio`.
Design lint: `python3 tools/design_lint.py templates/portfolio/ --out qa/portfolio-lint`.

## Sections and their moves

| # | Section | Element hooks | Move (recipe) |
|---|---|---|---|
| — | Nav (glass) | `[data-nav]` | sticky, blurs on scroll; pill CTA |
| 1 | Hero | `[data-split]`, `.hero__orb` | **letter stagger** on load (`letter-stagger`), CSS orb as the only image |
| 2 | Marquee | `.marquee__track` | infinite **marquee**, pauses on hover, static wrap on reduced motion (`marquee`) |
| 3 | Work | `[data-hscroll]`, `[data-tilt]` | **pinned horizontal scroll** with a native swipe row on mobile (`horizontal-scroll`) + subtle **card tilt** (`card-tilt`) |
| 4 | About | `[data-count]` | count-up stats, CSS portrait art |
| 5 | Process | `[data-path]` | **SVG path draw** with steps lighting up (`svg-path-draw`) |
| 6 | Journal | `[data-distort]` | **hover distortion** on the thumbnails (`image-hover-distortion`) |
| 7 | CTA | `[data-magnetic]` | **magnetic button** (`magnetic-button`) |
| — | Footer | `.foot__word` | gradient wordmark, credit line |

No libraries: no Lenis, no GSAP, no three.js. Native `scroll-behavior: smooth` is used for anchor links
and switched off under reduced motion.

## How an agent adapts it

1. **Copy** the folder to `sites/<name>/` (don't edit the template in place).
2. **Tokens.** Edit `:root` in `css/style.css`. Keep the structure: `--bg`, `--surface`, `--ink`,
   `--muted`, one `--accent` (+ `--accent-2` inside gradients). Change the two font families in the
   `<link>` and `--sans` / `--mono`.
3. **Copy.** Every placeholder string has `data-swap="key"` (e.g. `hero.title`, `work.1.body`,
   `cta.email`). Replace each one; delete sections you don't need.
4. **Projects.** The five project cards are CSS gradients. Swap `.project__art--a…e` for real WebP/AVIF
   (`loading="lazy"`, `width`/`height`, ≤ 150 KB) and keep the aspect ratio 4:3.
5. **Stats.** `data-count` values are placeholders — replace them with real numbers or delete the block.
   Never ship invented stats.
6. **Contact.** `mailto:hello@example.com` is a placeholder; point it at a real inbox.

## Accessibility and performance

- `prefers-reduced-motion` turns off smooth scroll, the marquee, the pinned gallery, the tilt, the
  magnetic pull and the distortion; the path is fully drawn and all content is visible.
- Keyboard focus rings on every link and button; the skip link is first in the tab order.
- The horizontal gallery becomes a native swipe row under 760 px.
- No images, no fonts beyond two families, no JavaScript libraries: the page is ~30 KB of HTML/CSS/JS.

Crafted by Swapnil Agrawal (BDS intern).
