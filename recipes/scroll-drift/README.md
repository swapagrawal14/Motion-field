# Scroll drift

Rows of type and imagery slide **sideways** while their band crosses the viewport. The page moves down, the story moves across. Two rows in opposite directions at different rates give a band depth without any 3D.

Extracted from Motion Field's *Study 01 · The tide turn*. Demo: [`index.html`](index.html).

## When to use it
- Chapter breaks, manifesto lines, process bands, logo or proof strips between sections.
- When the content itself has a direction (a journey, a timeline, "from → to").
- One or two bands per page. More than that and the page feels seasick.

Avoid it for content people must read in full (body copy, pricing): drifting rows are clipped at the edges.

## How it works
1. Each moving row has `data-drift="-28"` (distance in `vw`; the sign sets direction) and sits in a band with `overflow-x: clip`.
2. On scroll, each visible band's progress is `clamp((innerHeight - rect.top) / (innerHeight + rect.height))`, from 0 (entering at the bottom) to 1 (leaving at the top).
3. Target offset = `(progress - 0.5) * drift`, so the row is centred when the band is mid-screen.
4. A small rAF loop lerps the current offset toward the target and writes `translate3d(x vw, 0, 0)`. The loop stops when settled.

## Knobs
| Knob | Where | Default | Effect |
|---|---|---|---|
| `data-drift` | row attribute | `-28`, `20`, `-16` | travel in vw over the band's full pass. 12–30 reads well. |
| `EASE` | JS | `0.12` | lerp factor. `0.08` floaty, `1` locked to scroll. |
| Opposite signs | rows | one `-`, one `+` | counter-motion = depth. |
| `rootMargin` | IntersectionObserver | `100px` | how early bands start updating. |
| Row padding / negative margin | CSS | `padding-left: 6vw`, `margin-left: -34vw` | make sure a row is long enough to cover the viewport at both ends of its travel. |

On phones `vw` is small, so the same number moves fewer pixels. If you want more travel on mobile, raise `data-drift` inside a `matchMedia("(max-width: 640px)")` check.

## Reduced motion
`prefers-reduced-motion: reduce` (mirrored to `html.reduce-motion` by the head script; the demo's toggle overrides it) sets every row's target to `0`, applied instantly with no easing. Rows sit still and stay readable from the left edge. The CSS cue arrow stops pulsing.

## Performance
- Only `transform` changes; no layout reads inside the write loop except one `getBoundingClientRect()` per visible band per scroll event.
- Bands outside the viewport (IntersectionObserver) are skipped.
- Scroll and resize listeners are `passive`; the rAF loop runs only while rows are still easing.
- `will-change: transform` is on the rows only (removed under reduced motion).
- No horizontal page overflow: the band clips with `overflow-x: clip` (not `hidden`, so it does not create a scroll container).

## Files
- `index.html` – self-contained demo (HTML, CSS, JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
