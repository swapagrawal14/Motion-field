# Magnetic button

The primary CTA is pulled toward the pointer inside a padded zone and springs home when the pointer leaves. The label travels a little further than the shell, which is what makes it read as depth rather than a stuck button.

Demo: [`index.html`](index.html).

## When to use it

- The one primary action on a screen: hero CTA, pricing button, final "book a call".
- Linking a button to the pointer on a page that already feels physical (custom cursor, tilt cards).

Don't make every button magnetic — the effect only means something when there is one obvious action. Skip it on forms and dense toolbars.

## How it works

1. The pointer listener sits on a `.mag-zone` with generous padding, not on the button itself, so the field starts before you reach it.
2. For each button, the offset from the pointer to the button centre is multiplied by `PULL` (0.35) — but only inside a radius, otherwise the target is 0.
3. A rAF loop lerps the current offset toward the target at `0.16` and writes `translate3d` on the shell; the label gets `x * 0.45` on top.
4. `pointerleave` sets every target back to 0 and the same loop springs it home.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| pull | JS | `0.35` | how far the shell follows. 0.2 is subtle, 0.5 is sticky. |
| label | JS | `x * 0.45` | extra counter-move on the label. |
| radius | JS | `170` | how far away the field starts. |
| lerp | JS | `0.16` | lower = more float, higher = tighter. |
| `prefers-reduced-motion` | JS | off | normal button, no listeners. |

## Reduced motion

Initialisation returns immediately on reduced motion or coarse pointers, so the button never moves. It stays a normal, fully clickable button with its focus ring.

## Performance

- Only `transform` on two elements per button; no layout reads inside the rAF loop (the rect is read once per pointer move).
- The loop stops when all buttons settle at 0.
- Passive pointer listeners; no observers.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
