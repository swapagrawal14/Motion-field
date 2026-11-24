# SVG path draw

A single SVG path traces a journey between steps and retraces when you scroll back. The stroke is scrubbed by scroll progress; the nodes light up as the line reaches them.

Demo: [`index.html`](index.html).

## When to use it

- Process pages ("how it works"), timelines and numbered steps.
- Story pages with a clear direction (from → to, then → now).
- Anywhere four cards in a row feel like four separate things instead of one journey.

Keep the path inside one section: a line that runs the whole page is hard to follow and expensive to measure.

## How it works

1. The path carries `pathLength="1"`, so `stroke-dasharray: 1` and `stroke-dashoffset` work in 0–1 units — no `getTotalLength()` call.
2. On scroll, progress is `clamp((innerHeight * 0.9 - rect.top) / (rect.height + innerHeight * 0.55), 0, 1)`: 0 when the section is still below the fold, 1 when it has passed.
3. A short rAF loop lerps the current progress toward the target and writes `strokeDashoffset = 1 - progress`.
4. Nodes (and the matching step cards) get `.is-on` when progress crosses their threshold in `cut[]`.
5. Scroll back and the line retraces, because the stroke is a pure function of scroll.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| `pathLength` | SVG attribute | `1` | keeps dash units in 0–1; change the dash math if you remove it. |
| start / travel | `target()` | `0.9` / `0.55` | when the draw starts and how much scroll it spans. |
| `cut[]` | JS | `0.02, 0.34, 0.66, 0.99` | progress at which each node lights up. |
| lerp | JS | `0.12` | `0.06` floaty, `1` locked to the scrollbar. |
| stroke width | CSS | `2.5` | raise to 3–4 on light backgrounds. |

## Reduced motion

The line is drawn completely (`stroke-dashoffset: 0`), every node and step is lit, and the progress meter reads 100%. No scroll listener work happens.

## Performance

- Only `stroke-dashoffset` changes per frame; the SVG is static otherwise.
- The rAF loop stops once the current value settles on the target.
- No libraries, no canvas, no images.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
