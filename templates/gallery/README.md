# gallery

An image board in the Pinterest register: a staggered masonry of artwork, a floating preview that
follows the cursor over a list, a pinned horizontal band dragged by the scroll, and a lab of six
micro-interactions. **The most motion-dense template in the set** — thirteen distinct behaviours on
one page, all vanilla.

Open `index.html` directly, or serve the repo root. No build step, no libraries.

## What moves

| Where | Behaviour | Technique |
|---|---|---|
| Nav | link underline draws in, brand text scrambles on hover, sound toggle | `::after` scaleX, rAF glyph loop |
| Page | 3px scroll progress bar | `scaleX` on a fixed element |
| Hero | headline rises out of a line mask | `overflow: hidden` + `translateY` |
| Hero | keyword ticker, pauses on hover | `translateX` keyframes |
| Cursor | ring + dot follow the pointer, ring grows and reads a label over targets | lerped `translate3d` |
| Board | cards rise in as they enter, filter chips re-stagger them | IntersectionObserver |
| Board | **six hover treatments**: zoom, desaturate→colour, blur, caption reveal, 3D tilt, glare sweep | `data-fx` |
| Board | arrow appears bottom-right on hover | `::after` opacity + translate |
| Types | floating image follows the cursor over a list row | lerped `translate3d` + `scale` |
| Strip | pinned section, band dragged horizontally by vertical scroll | `position: sticky` + `translate3d` |
| Lab | magnetic button, flip card, glare border, elastic toggle, underline draw, text scramble | see below |
| Footer | outlined wordmark fills with ink as it enters | `-webkit-text-stroke` → `color` |

## The six hover treatments

One markup shape, one attribute. Change `data-fx` to switch behaviour:

```html
<article class="pin" data-fx="tilt" data-cursor="View">
  <figure class="pin__media"><img src="…" alt="…" width="640" height="800"></figure>
  <div class="pin__meta"><span class="mono">01 · Light</span><h3>Chrome study</h3></div>
</article>
```

`zoom` · `desat` · `blur` · `caption` · `tilt` · `glare` (the glare layer is on every card; `caption`
and `tilt` expose it). Add `data-h="1"` for the taller 3:4.7 crop — the stagger is what makes the
board read as a board.

## Images

Twelve WebPs in `assets/`, 640×800, 6–41 KB each, 252 KB total. Replace them with your own work:
export 4:5 and 3:4.7 crops, keep each under ~60 KB, and always set `width`/`height` so the board
never shifts while loading.

This is the one image-led template — the recipes and the other templates stay asset-free by design.

## Motion rules

- Only `transform`, `opacity`, `filter` and `-webkit-text-stroke-color` animate.
- Every rAF loop stops when it settles; listeners are passive; the cursor never runs on coarse pointers.
- `prefers-reduced-motion`: no cursor, no parallax, the strip un-pins into a wrapping row, all
  reveals resolve instantly.

## QA

```bash
python3 tools/qa.py templates/gallery/ --out qa/gallery
python3 tools/design_lint.py templates/gallery/ --out qa/lint-gallery
```

Passes both with no warnings: LCP ~740 ms, 434 KB total.
