# Pinned hero shrink

A full-bleed hero holds the viewport while the page scrolls underneath, then folds into a rounded card as the headline lifts away. The classic Apple-style opening, in vanilla CSS and one scroll-linked transform.

Demo: [`index.html`](index.html).

## When to use it

- The very top of a launch page, portfolio or campaign site.
- When the hero media is strong enough to carry a full screen and the page needs a clear "first beat".

One per site. Don't stack it with another pinned section, and keep the pinned distance short on mobile (170 vh or less).

## How it works

1. `.pin` is `height: 220vh`; its child `.pin__sticky` is `position: sticky; top: 0; height: 100vh`.
2. Scroll progress is `clamp(-rect.top / (rect.height - innerHeight), 0, 1)` over the pin's extra height.
3. Each frame: `scale(1 - p * 0.16)`, `border-radius = p * 30px`, a shadow that grows with `p`, and the copy fades (`1 - p * 1.9`) while lifting `p * 70px`.
4. Scroll back and it unfolds, because everything is a pure function of scroll.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| final scale | JS | `1 - p * 0.16` | how far the frame shrinks. |
| radius | JS | `p * 30px` | final corner radius. |
| copy exit | JS | `1 - p * 1.9` | copy is gone by ~55% of the pin. |
| pin length | CSS | `220vh` | scroll distance; 170 vh on mobile. |
| lerp | JS | `0.14` | lower = smoother/floatier. |
| `prefers-reduced-motion` | CSS | static | no pin, no transform. |

## Reduced motion

`.pin` becomes `height: auto`, the sticky wrapper becomes static, the media stays full-bleed and the copy never fades. The hero is a normal section.

## Performance

- One rect read per scroll event; the rAF loop stops when settled.
- Only `transform`, `opacity` and `border-radius` change; no layout properties.
- The art is CSS gradients and spans — no images to decode.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
