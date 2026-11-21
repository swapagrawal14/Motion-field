# Blur reveal

Blocks resolve from **soft to sharp** the first time they enter view: blur, scale and opacity settle together, the image first and the words a beat behind. No sliding in from off-screen, no bounce; the content was always there and the reader's eyes simply adjust.

Extracted from Motion Field's *Study 03 · Soft-focus reveal*. Demo: [`index.html`](index.html).

## When to use it
- Feature rows, case-study chapters, image + copy pairs, pull quotes, spec grids.
- Calm enough to use on every section of a page, as the page's single entrance style.
- Skip it above the fold for the LCP element (don't delay your hero's first paint).

## How it works
1. Mark blocks with `data-reveal`. Children can carry `style="--i:N"` for a stagger.
2. A one-line `<head>` script adds `html.js-reveal` before first paint. The hidden state only exists under that class, so with no JS everything is visible and nothing flashes.
3. An IntersectionObserver (`threshold: 0.35`, `rootMargin: 0px 0px -6% 0px`) adds `.is-in` once and unobserves.
4. CSS transitions do the rest:
```css
.js-reveal [data-reveal]:not(.is-in) .media { filter: blur(22px) saturate(.6); transform: scale(1.06); opacity: .4; }
.js-reveal [data-reveal]:not(.is-in) .copy > * { filter: blur(10px); opacity: 0; transform: translateY(18px); }
.copy > * { transition: filter 1.1s var(--ease-out), opacity 1.1s, transform 1.2s var(--ease-out);
            transition-delay: calc(350ms + var(--i) * 90ms); }
```

## Knobs
| Knob | Default | Effect |
|---|---|---|
| Image start blur / scale | `22px`, `1.06` (outer) + `1.15` (inner) | softness of the arrival; the inner scale gives a slow "lens settle". |
| Text start blur / offset | `10px`, `18px` | keep the offset small; this is not a slide-in. |
| Durations | 1.4 s image, 1.1–1.2 s text | slower = more editorial. |
| Copy delay + stagger | `350ms` + `90ms × --i` | image lands first, then label, title, body. |
| `threshold` / `rootMargin` | `0.35` / `-6%` bottom | how far into view before it fires. |
| Ease | `cubic-bezier(.16, 1, .3, 1)` | long, soft tail. |

## Reduced motion
Under `prefers-reduced-motion: reduce` (mirrored to `html.reduce-motion`; the demo toggle can force it) every block gets `.is-in` immediately and transitions are disabled, so content is simply present. Blur is never used as a resting state.

## Performance
- One observer for the whole page; each element is unobserved after its reveal.
- `filter: blur()` is composited but scales with area: keep blurred elements to about one screen, and never blur a full-bleed video.
- Only `filter`, `opacity` and `transform` transition. No scroll listeners.

## Accessibility
Content is in the DOM and readable by assistive tech from the start; only its paint state changes. The demo's "Replay" button is for the demo only.
