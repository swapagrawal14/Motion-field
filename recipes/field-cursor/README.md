# Field cursor

A ring and a dot replace the pointer on fine-pointer devices. The ring lerps behind the dot, grows over targets marked `data-cursor` and shows a short label (View, Drag, Play). Touch and reduced-motion users keep the native cursor.

Demo: [`index.html`](index.html).

## When to use it

- Portfolios, studios and launches where the pointer is part of the language.
- Drag galleries, case-study grids and media that benefits from a verb label.
- Site-wide, once — with labels added only where they say something new.

Avoid it on content-heavy sites, forms and anything where hiding the native cursor would slow someone down. Never make it the only affordance: links still look like links.

## How it works

1. One fixed `.fc-cursor` host holds the ring, the dot and the label. Dot follows the pointer immediately; ring lerps at `0.18`.
2. `pointerover` (delegated) reads the closest `[data-cursor]` target, writes its label and adds `.is-active`, which grows the ring.
3. The native cursor is hidden only inside `.stage--fc` (`cursor: none`), so the rest of the page keeps its normal pointer.
4. Initialisation checks `(pointer: fine)`; coarse pointers and reduced motion never see the custom cursor.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| ring lag | JS | `0.18` | lower = more float; `1` = locked to the pointer. |
| ring size | CSS | `38px` / `74px` active | resting and over-target diameter. |
| label | `data-cursor` | any short verb | keep it under ~12 characters. |
| scope | CSS | `.stage--fc` | which area hides the native cursor. |
| `prefers-reduced-motion` | CSS | hidden | native cursor everywhere. |

## Reduced motion

The custom cursor is `display: none` and the native cursor returns. No listeners are attached on touch devices; on desktop the ring simply never appears and the page behaves normally.

## Performance

- One fixed element per layer, moved with `transform`; no layout work.
- The rAF loop stops once the ring settles and starts again on the next pointer move.
- `pointerover`/`pointerout` are delegated — one listener each for the whole page.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
