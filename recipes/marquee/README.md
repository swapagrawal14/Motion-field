# Infinite marquee

A seamless looping strip of words or logos, built from one duplicated track and a single CSS animation. Pauses on hover and focus, stops dead under reduced motion, and never causes page overflow.

Demo: [`index.html`](index.html).

## When to use it

- Logo walls, client lists, manifesto strips, category tags between sections.
- Filling a band with rhythm when you don't have imagery for it.

Keep it decorative: no essential information should only exist in the marquee, and keep the text short enough to read at a glance.

## How it works

1. The track contains the content once; a second identical track (`aria-hidden`) sits beside it.
2. `@keyframes mqMove { to { transform: translate3d(-100%, 0, 0) } }` moves exactly one track width, so the loop is seamless.
3. `gap` on the track and `padding-right` must be equal, otherwise there is a jump at the seam.
4. `mask-image` fades both edges; `:hover`/`:focus-within` pauses; reduced motion hides the duplicate and lays the items out statically.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| speed | CSS | `34s` | one full loop; longer = calmer. |
| reverse row | CSS | `42s` + `reverse` | counter-motion reads as depth. |
| gap / padding | CSS | `44px` | must match for a seamless seam. |
| edge fade | CSS | `mask-image` 7% / 93% | how softly the strip disappears. |
| `prefers-reduced-motion` | CSS | static | duplicate hidden, no animation. |

## Reduced motion

The duplicate track is hidden, the row becomes a static evenly spaced strip, and the mask is removed so nothing is faded out. All text stays visible.

## Performance

- One `transform` animation per row, composited on the GPU; no JS in the loop.
- `will-change: transform` only on the two tracks.
- `overflow: clip` on the section so the wide track never widens the page.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
