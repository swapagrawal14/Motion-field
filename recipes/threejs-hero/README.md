# three.js hero object

A lit three.js object turns with the pointer and tilts with scroll. One canvas, one mesh, three lights — and it stops rendering the moment it leaves the viewport or the tab hides. A CSS orb stands in if three.js cannot load.

Demo: [`index.html`](index.html).

## When to use it

- A hero whose subject is an object: a product, a sculpture, an abstract brand form.
- Pages that can afford ~150 KB gzipped of three.js (it is the heaviest recipe here).

Don't use it for decoration you could do with CSS, and never run two WebGL contexts on one screen (this and `shader-background` compete).

## How it works

1. `import()` three.js from a CDN (unpkg, jsDelivr as fallback); if both fail, hide the canvas and keep the CSS orb.
2. One `TorusKnotGeometry` with a `MeshStandardMaterial`, lit by two coloured point lights and a low ambient.
3. `pointermove` sets a target rotation, lerped at `0.06`; time adds a slow idle turn.
4. An IntersectionObserver pauses the loop offscreen, `visibilitychange` pauses it when the tab hides, and reduced motion renders exactly one frame.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| geometry | JS | `TorusKnotGeometry(1.45, 0.42, 200, 28)` | swap for any mesh; keep segments modest. |
| idle turn | JS | `t * 0.00022` | slower = calmer. |
| pointer | JS | `mx * 0.7` | how far the object follows the pointer. |
| lights | JS | cyan 60 / violet 45 | colour and intensity set the mood. |
| DPR | JS | `1.5` | cap for retina. |
| `prefers-reduced-motion` | JS | one frame | no loop, no pointer. |

## Reduced motion

The canvas is hidden (the CSS orb remains), or the renderer draws exactly one frame and stops. No pointer listener does anything and the status line says so.

## Performance

- ~150 KB gzipped for three.js; load it with `import()` so it never blocks first paint.
- One draw call per frame; pauses offscreen and on `visibilitychange`; DPR capped at 1.5.
- Fallback is a CSS radial gradient, so the hero still looks complete without WebGL or the CDN.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
