# Text scramble

Characters cycle through a glyph set and settle into the real word, left to right. Hover a nav item or let a heading enter view and it resolves out of noise in about half a second.

Demo: [`index.html`](index.html).

## When to use it

- Nav items, eyebrows, tags, small labels and short hero lines.
- Tech, studio and editorial sites that want a "signal arriving" feel.
- Monospace contexts, where the fixed glyph width keeps the line still.

Never use it on body copy, prices, dates or anything someone needs to read at a glance. Keep it to one or two elements per screen.

## How it works

1. Each element stores its real text in `data-text` on first run.
2. Every frame computes `solved = floor(progress * length)`; characters before that index are real, the rest are random glyphs (spaces stay spaces).
3. The loop runs with `requestAnimationFrame` and writes `textContent` — cheap for short strings.
4. `pointerenter` and `focus` trigger a faster 420 ms run; the heading runs once when it enters view.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| duration | JS | `620ms` / `420ms` hover | how long the noise takes to resolve. |
| glyph set | JS | `!<>-_\/[]{}—=+*^?#` | 16–20 marks; avoid letters so it reads as noise. |
| reveal | JS | left → right | `floor(p * length)`; reverse it for a different feel. |
| trigger | HTML | hover + focus + entrance | keep at least one non-pointer trigger. |
| `prefers-reduced-motion` | JS | instant | real text, no animation. |

## Reduced motion

The scramble function returns before touching the element, so every label shows its real text immediately. Nothing is hidden and no animation runs.

## Performance

- Text content changes only for the scrambling element, and only for ~0.6 s.
- One rAF id per element, cancelled when a new run starts.
- No observers except one for the headline entrance.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
