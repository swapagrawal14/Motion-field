# Hover pulse

On hover or keyboard focus a card lifts, its border catches the accent, a soft radial glow follows the pointer, and a thin ring pulses out from the centre. Feedback that says "you're here" without a single line of JavaScript animation.

Demo: [`index.html`](index.html).

## When to use it

- Feature grids, pricing tiers, team cards and link lists.
- Any grid of similar boxes where the visitor needs to know which one is active.
- Pairing with `blur-reveal` for the entrance and `magnetic-button` for the CTA.

Don't put it on static decoration, and don't stack it on a card that already has `card-tilt` — pick one pointer response per element.

## How it works

1. The card has `transition` on `transform`, `border-color` and `box-shadow`; `:hover` and `:focus-visible` share the exact same block, so keyboard users get the same feedback.
2. A `::after` pseudo-element holds a radial gradient positioned by `--mx` / `--my` (percentage of the card), so the glow follows the pointer.
3. A `.hp-pulse` span expands from `scale(.4)` to `scale(16)` while fading — an infinite but cheap ring that only runs while the card is hovered.
4. `tabindex="0"` makes non-interactive cards focusable; real links should use `<a>` instead.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| lift | CSS | `translateY(-4px)` | raise to −6 px for a stronger response. |
| ring size | `@keyframes hpRing` | `scale(16)` | how far the pulse travels. |
| ring period | CSS | `1.15s` | one ring per arrival; slower reads calmer. |
| glow | `::after` gradient | `420px 240px` | size of the pointer-follow highlight. |
| `prefers-reduced-motion` | CSS | off | border + focus ring only. |

## Reduced motion

The lift, glow and ring are removed; the accent border and the `:focus-visible` outline stay. Nothing is hidden and the card is still clearly interactive.

## Performance

- CSS transitions only; the single JS listener just writes two CSS custom properties on `pointermove` (passive).
- The ring is one pseudo-element animating `transform` and `opacity`.
- No observers, no rAF loop.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
