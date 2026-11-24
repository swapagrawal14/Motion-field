# UI sound kit

Procedural WebAudio pops, ticks, whooshes, plips, success and error chimes on hover and click. No audio files, no autoplay: sound stays muted until the visitor turns it on, and every sound is synthesized the moment it plays.

Demo: [`index.html`](index.html).

## When to use it

- Hover ticks on nav items and cards, a pop on the primary CTA, a whoosh on a drawer or page wipe.
- Success / error chimes on forms and destructive actions.

Sound is opt-in. Never autoplay, keep volumes low, and never make sound the only feedback for an action.

## How it works

1. `assets/ui-sound.js` creates the `AudioContext` on the first toggle click (never on load) and keeps `muted = true` until then.
2. Delegated listeners play `data-sfx` on click / Enter / Space and `data-sfx-hover` on `pointerover`.
3. Each sound is a short oscillator or noise buffer with an exponential envelope — no samples, no network.
4. `UIsound.play(name)`, `UIsound.setMuted(false)` and `UIsound.toggle()` are the programmatic API; the toggle button mirrors state with `aria-pressed`.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| sound | `data-sfx` | `pop` | pop / tick / whoosh / plip / boing / dab / ring / success / error. |
| hover sound | `data-sfx-hover` | `tick` | lighter variant for pointerenter. |
| volume | JS `FX` | `0.05–0.2` | gain peak per sound; keep it under 0.2. |
| toggle | HTML | `data-sfx-toggle` | creates the context and flips `aria-pressed`. |
| API | JS | `UIsound.play()` | programmatic playback; still respects mute. |

## Reduced motion

The kit is already silent by default. Reduced-motion users get the same opt-in; if you want to be stricter, call `UIsound.setMuted(true)` when `prefers-reduced-motion` matches.

## Performance

- Zero bytes of audio shipped; sounds are synthesized per event with the WebAudio API.
- The AudioContext is created once, on the first opt-in; nothing runs on load.
- A failed sound is caught and ignored — audio never breaks the page.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
