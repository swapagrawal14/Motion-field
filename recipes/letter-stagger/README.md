# Letter stagger

Headline letters ease in one by one: a short lift, a touch of blur, a tight stagger. Words stay intact so the line never breaks mid-word, and hovering a word replays just that word.

Demo: [`index.html`](index.html).

## When to use it

- Hero headlines and section titles that need a beat of arrival.
- Numbers, chapter labels and short manifesto lines (under ~8 words).
- Anywhere you want the type to feel *performed* rather than printed.

Avoid it for body copy, long headings and anything the visitor needs to read instantly — a 40-character headline at 26 ms per letter takes over a second to finish.

## How it works

1. The headline keeps its real text for screen readers (`aria-label`), then JS wraps each **word** in a `.w` span and each **character** in a `.ch` span with `--i` (global index) and `--j` (index inside the word).
2. `.ch` runs one keyframe animation — `opacity`, `translateY`, `rotate`, `filter: blur()` — with `animation-delay: calc(var(--i) * 26ms)`.
3. Words are `inline-block` with `white-space: nowrap`, so wrapping happens between words only.
4. Hovering a word adds `.is-replay` for one short run (removed on `animationend`), so the entrance does not retrigger when the pointer leaves.
5. A "Replay" button resets the inline animation on every character.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| `--i` stagger | JS | `26ms` | delay per character. 20–40 ms reads best; 60+ feels slow. |
| lift | CSS keyframe | `translateY(.42em)` | how far each letter travels. |
| blur | CSS keyframe | `blur(8px)` → `0` | softens the arrival; set to `0` for a crisp cut. |
| word stagger | `.ls-words` | `70ms` | per word for section titles. |
| `prefers-reduced-motion` | CSS | animation off | all letters visible immediately. |

## Reduced motion

`prefers-reduced-motion: reduce` (mirrored to `html.reduce-motion`) sets `animation: none` on every character and word, so the headline is fully visible with no movement. The demo's toggle lets you compare both.

## Performance

- Only `transform`, `opacity` and `filter` animate; characters are inline-block spans, so there is no layout thrash after the split.
- The split happens once on load; hover replays touch one word only.
- No observers, no scroll listeners, no libraries.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
