# Image hover distortion

On hover the image warps through an animated SVG displacement map — the grain shifts and the edges breathe, then it settles when the pointer leaves. Tiny (one filter, no library), with a WebGL upgrade path for full grids.

Demo: [`index.html`](index.html).

## When to use it

- Portfolio covers, editorial cards, product photography that should feel alive.
- Anywhere a flat image is the only static thing in an otherwise kinetic layout.

Keep the displacement subtle (scale 20–30). Strong values look like a broken image, not a design choice. For a grid of many images, move this to a single WebGL pass instead of one SVG filter per image.

## How it works

1. One SVG `<filter id="warp">` combines `feTurbulence` (fractal noise) with `feDisplacementMap`, whose `scale` starts at 0.
2. On hover/focus, a rAF loop lerps `scale` to 26 and slowly oscillates `baseFrequency`, so the grain keeps moving instead of freezing.
3. On leave/blur the target returns to 0 and the loop stops when settled.
4. The figure also scales to 1.015 for a little physical push; reduced motion removes the filter entirely.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| strength | JS | `0 → 26` | displacement scale; 15–30 is the useful range. |
| grain | JS | `0.012 0.02` | base frequency; smaller = bigger waves. |
| detail | SVG | `numOctaves 2` | 1 is smoother and cheaper. |
| in/out | JS | `0.12` | lerp speed in and out. |
| `prefers-reduced-motion` | CSS | filter off | the image stays perfectly still. |

## Reduced motion

`filter: none` removes the displacement entirely; the image is static and the figure does not scale. No listeners do anything.

## Performance

- SVG filters run on the GPU in modern browsers, but they are not free — this recipe animates one figure at a time, only while hovered.
- The rAF loop stops when `scale` returns to 0.
- For a grid of 6+ images, use a single WebGL plane with a noise texture instead of six SVG filters.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
