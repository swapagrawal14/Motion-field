# 3D tilted card wall

A perspective-tilted wall of preview cards. Columns drift in opposite directions as you scroll and the whole plane leans a few degrees toward the pointer. Reads as depth, costs one transform per column.

Demo: [`index.html`](index.html).

## When to use it

- A portfolio project index, a studio capabilities wall, a feature mosaic.
- When you want "a lot of work" to feel like a wall you can scan, not a list you must read.

Avoid it for content that must be read in full — tilted, drifting cards are for scanning, not reading.

## How it works

1. `.wall__scene` provides `perspective: 1400px`; `.wall__plane` carries the base tilt (`rotateX(13deg) rotateY(-16deg) rotateZ(3deg)`) and `transform-style: preserve-3d`.
2. Scroll progress is measured against the scene (`(vh - rect.top) / (vh + rect.height) - 0.5`), then each column translates by `±26px` in alternating directions.
3. `pointermove` adds ±4° / ±5° to the plane's rotation, lerped at `0.08`.
4. Below 700 px or with reduced motion the transforms are cleared and the wall becomes a flat grid.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| base tilt | CSS | `13 / -16 / 3` deg | how much perspective the wall has. |
| column drift | JS | `±26px` | vertical travel per column. |
| directions | JS | `[1, -1, 1]` | alternating = depth; all same = a wave. |
| pointer lean | JS | `±4° / ±5°` | how far the plane follows the pointer. |
| `prefers-reduced-motion` | JS | flat | no tilt, no drift. |

## Reduced motion

The plane and every column get their transforms cleared; the wall is a flat, readable grid. No pointer listeners do anything.

## Performance

- One rect read per scroll event; the rAF loop stops when everything settles.
- Only `transform` on the plane and three columns.
- Cards are CSS-only in the demo; if you use images, keep them under 150 KB and `loading="lazy"`.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
