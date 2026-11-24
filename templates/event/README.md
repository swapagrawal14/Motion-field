# Event / invite template — near-black + acid lime

A one-page event site in a poster-like system: near-black, one acid-lime accent, hard grotesque
(Space Grotesk 700) with IBM Plex Mono labels. **Every visual is CSS or inline SVG — no image files.**
No build step.

```text
templates/event/
  index.html      markup; every editable string carries data-swap="…"
  css/style.css   tokens at the top (:root), then one block per section
  js/main.js      countdown, scramble, drawn timeline, tilt, magnetic CTA
```

Preview: `python3 -m http.server 8080` from the repo root → `http://localhost:8080/templates/event/`.
QA: `python3 tools/qa.py templates/event/ --out qa/event`.
Design lint: `python3 tools/design_lint.py templates/event/ --out qa/event-lint`.

## Sections and their moves

| # | Section | Element hooks | Move (recipe) |
|---|---|---|---|
| — | Nav (glass) | `.nav__links a` | **text scramble** on hover/focus (`text-scramble`), lime pill CTA |
| 1 | Hero | `[data-split]`, `[data-cd]` | **letter stagger** on load (`letter-stagger`), live countdown, grid backdrop |
| 2 | Ticker | `.marquee__track` | **infinite marquee** in accent colour, static wrap on reduced motion (`marquee`) |
| 3 | Lineup | `[data-tilt]` | **3D card tilt** on six acts (`card-tilt`) |
| 4 | Schedule | `[data-path]` | **SVG path draw** with the four slots lighting up (`svg-path-draw`) |
| 5 | Venue | `.venue__map` | CSS map with a pulsing pin (stopped under reduced motion) |
| 6 | Tickets | `[data-magnetic]` | three tiers + **magnetic button** (`magnetic-button`) |
| 7 | FAQ | `details` | native accordions, animated `+` marker |

No libraries: no Lenis, no GSAP, no three.js. The countdown is a `setInterval` that stops mattering
after the date passes (it clamps at 00).

## How an agent adapts it

1. **Copy** the folder to `sites/<name>/` (don't edit the template in place).
2. **Tokens.** Edit `:root` in `css/style.css`. Keep `--bg`, `--surface`, `--ink`, `--muted` and one
   `--accent`; change the font families in the `<link>` and `--sans` / `--mono` if the brand differs.
3. **Copy.** Every placeholder string has `data-swap="key"` (e.g. `hero.title`, `lineup.1.name`,
   `tickets.2.price`). Replace each one. **The prices, dates, names and FAQ answers are placeholders —
   never ship them as real.**
4. **Date.** The countdown target is hard-coded in `js/main.js` (`2027-02-14T18:00:00+05:30`). Change it
   to the real date and timezone, or delete the countdown block.
5. **Tickets.** Point `#tickets` links at a real ticketing URL. Do not invent prices.
6. **Lineup art.** The six cards are CSS gradients. Swap `.act__art--a…f` for real portrait WebP/AVIF
   (`loading="lazy"`, `width`/`height`, ≤ 150 KB, aspect 4:5).

## Accessibility and performance

- `prefers-reduced-motion` turns off smooth scroll, the marquee, the letter stagger, the scramble, the
  tilt, the magnetic pull and the pulsing pin; the timeline is fully drawn and all content is visible.
- Keyboard focus rings on every link, button and lineup card; the skip link is first in the tab order.
- FAQ uses native `<details>` — no JS, no ARIA wiring needed.
- No images, no libraries: ~35 KB of HTML/CSS/JS.

Crafted by Swapnil Agrawal (BDS intern).
