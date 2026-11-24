# Card tilt + glare

Cards tilt in 3D toward the pointer with a moving specular glare and settle flat on leave. Keyboard focus applies a fixed tilt, so the depth is never pointer-only.

Demo: [`index.html`](index.html).

## When to use it

- Case-study grids, product cards, portfolio thumbnails, team cards.
- Pairing with an image that has a clear light source (the glare should agree with it).
- One grid per screen; a whole page of tilting cards is exhausting.

Skip it on text-only cards and on anything the visitor needs to read carefully while the pointer is moving.

## How it works

1. The outer `.tilt` has `perspective: 900px`; the inner card has `transform-style: preserve-3d` and the art layer gets `translateZ(30px)` so it lifts off the surface.
2. `pointermove` converts the pointer position to `rotateX` / `rotateY` within `MAX` degrees and sets `--gx` / `--gy` for the radial glare.
3. A rAF loop lerps the rotation so the card follows smoothly instead of snapping.
4. `pointerleave`, `blur` and reduced motion all return the card to 0. `focus` applies a fixed 5°/−4° tilt for keyboard parity.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| max tilt | JS | `9` degrees | 5–10 reads as depth; 15+ reads as a toy. |
| art lift | CSS | `translateZ(30px)` | how far the image floats above the card. |
| glare size | CSS | `280px 180px` | size of the specular highlight. |
| lerp | JS | `0.18` | lower = floatier, `1` = locked. |
| `prefers-reduced-motion` | CSS | flat | no tilt, no glare, border + focus ring only. |

## Reduced motion

The inner card is forced flat (`transform: none`) and the glare is removed. The accent border and the `:focus-visible` outline stay, so the card is still clearly interactive.

## Performance

- One rect read per pointer move; the rAF loop only runs while the rotation is settling.
- Only `transform` on the card; the glare is a static gradient moved by CSS variables.
- No observers, no images required (the demo art is pure CSS).

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
