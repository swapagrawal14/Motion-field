# Pointer parallax

A layered scene that leans toward the pointer. Every layer reads the same two CSS variables, `--x` and `--y` (the pointer's position from −1 to 1), and multiplies them by its own `--depth`. Near layers travel far, distant ones barely move, and the eye reads depth. With no pointer (touch, keyboard, idle) the scene drifts on a slow Lissajous loop.

Extracted from Motion Field's *Study 02 · Orbit, gently*. Demo: [`index.html`](index.html).

## When to use it
- A hero illustration or product shot cut into 3–8 layers.
- 404 pages, "about" toys, interactive section breaks.
- Not on text people must read: keep copy on a low depth (≤ 0.5) or outside the scene.

## How it works
```css
.layer { transform: translate3d(calc(var(--x) * var(--depth) * var(--unit)),
                                calc(var(--y) * var(--depth) * var(--unit) * .75), 0); }
```
```js
stage.addEventListener('pointermove', e => {           // mouse / pen only
  const r = stage.getBoundingClientRect();
  tx = ((e.clientX - r.left) / r.width - .5) * 2;
  ty = ((e.clientY - r.top) / r.height - .5) * 2;
}, { passive: true });
// rAF: x += (tx - x) * 0.07 → stage.style.setProperty('--x', x)
```
The stage sets the variables once per frame; CSS does the per-layer maths, so adding a layer costs no JS.

## Knobs
| Knob | Default | Effect |
|---|---|---|
| `--depth` (per layer) | −2.2 … 3 | travel multiplier. Negative moves against the pointer (background). |
| `--unit` (stage) | `clamp(14px, 2.2vw, 30px)` | pixels per depth step. |
| `FOLLOW` | `0.07` | lerp per frame. 0.04 heavy and dreamy, 0.2 snappy. |
| Idle drift | `sin(t/2600) * .42`, `cos(t/3400) * .34` | amplitude and period of the self-running loop. Different periods keep it from looking mechanical. |
| Vertical factor | `.75` | vertical travel is damped; scenes are usually wider than tall. |

## Reduced motion
Under `prefers-reduced-motion: reduce` (mirrored to `html.reduce-motion`; the demo toggle can force it) every layer is parked at 0, the loop is cancelled, and the pointer is ignored. The scene stays fully composed, just still.

## Performance
- One rAF loop per stage; it stops when the stage is offscreen (IntersectionObserver), when the tab is hidden, and under reduced motion.
- Only CSS custom properties and `transform` change. `will-change: transform` on layers (dropped under reduced motion).
- Touch `pointermove` is ignored so it never fights vertical scroll (`touch-action: pan-y`); touch users get the idle drift.
- Pure CSS art in the demo (gradients, no images). With images, size each layer ~10% larger than the stage so edges never show.

## Accessibility
The scene is decorative: the stage is `role="img"` with an `aria-label`. Any real copy inside stays real text.
