# product-launch

A launch page for a product that does not exist yet: hero + device mock, a pinned three-stop feature
tour, a spec switcher, a roadmap and a waitlist form. **Warm paper and vermilion**, Instrument Serif
for display and JetBrains Mono for labels — the only light template in the set.

Live demo: `index.html` (open directly, or serve the repo root). Vanilla HTML/CSS/JS, no build step,
no images: the device, link graph and sync bars are CSS and SVG.

## Sections

| Section | What moves | Recipe |
|---|---|---|
| Nav + progress | sticky blur bar, underline slide, 3px scroll progress | — |
| Hero | letter stagger, count-up stats, floating spec chips, device rows cascade, 3D tilt on hover | `letter-stagger`, `count-up` |
| Marquee | capability ticker, pauses on hover | `marquee` |
| Tour (01–03) | sticky copy rail, tree nodes stagger in, link-graph wires draw, sync bars fill | `svg-path-draw` |
| Specs | tab switcher with sliding ink, animated pane swap | — |
| Roadmap | timeline items rise in sequence | — |
| CTA | waitlist form, magnetic button | `magnetic-button` |

## Before you ship

1. Replace every `data-swap` value — product name, dates, prices, platform lists. Nothing here is real.
2. Point the waitlist `<form>` at your own endpoint. The demo only hides the form; it stores nothing.
3. Swap the CSS device for a real screenshot if you have one — keep it under ~120 KB and give it
   explicit `width`/`height` so LCP stays put.

## Motion rules

- Only `transform`, `opacity`, `filter` and `stroke-dashoffset` animate — never `width`/`height`/`top`.
- Every loop stops itself; listeners are passive; the tab ink is positioned with `transform`.
- `prefers-reduced-motion` turns all of it off and shows the full page immediately.

## QA

```bash
python3 tools/qa.py templates/product-launch/ --out qa/product-launch
python3 tools/design_lint.py templates/product-launch/ --out qa/lint-product-launch
```
