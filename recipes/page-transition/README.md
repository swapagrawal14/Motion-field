# Page transition

A wipe covers the old page and reveals the new one. Uses the View Transitions API where available, with a curtain fallback for browsers without it. Reduced motion swaps instantly. The demo runs both pages inside one document.

Demo: [`index.html`](index.html).

## When to use it

- Case studies, documentation, portfolios — anywhere a click should feel like moving through one space.
- Sites with a consistent chrome (nav, footer) that can stay put while the content swaps.

Keep it under ~450 ms. Long transitions make a fast site feel slow, and never block the navigation on the animation.

## How it works

1. The old page is hidden and the new one shown inside a callback; the browser screenshots before and after.
2. `document.startViewTransition(() => swap(name))` cross-fades/wipes the two states; CSS `::view-transition-old/new` tunes the duration.
3. Without the API, a `.pt__curtain` element animates `scaleY` from bottom to top, swapping the pages at the midpoint (190 ms).
4. Reduced motion skips both and swaps immediately.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| duration | CSS | `.42s` | total wipe; swap at 190 ms in the fallback. |
| direction | CSS | bottom → top | change `transform-origin` per keyframe. |
| curtain colour | CSS | navy → cyan → navy | match the site accent. |
| API duration | CSS | `.42s` on `::view-transition-*` | keep it equal to the fallback. |
| `prefers-reduced-motion` | JS | instant | no curtain, no transition. |

## Reduced motion

The curtain is `display: none` and the page swaps instantly with no animation. Focus and scroll position behave as a normal navigation.

## Performance

- The View Transitions API is compositor-driven; the fallback is one `transform` animation on a single overlay.
- Nothing runs when the visitor is not navigating.
- The curtain is `pointer-events: none` so it never blocks a click.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
