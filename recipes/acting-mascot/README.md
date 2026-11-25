# Acting mascot

A painted-cutout mascot changes pose as you scroll: idle at the top, reading in the story, surprised at the reveal, waving at the end. Pose first, motion second — the same method as the video pose packs. The four poses are **generated cutouts** (`assets/mascot/mascot-*.webp`, one pose sheet split into four transparent WebPs), not a rigged SVG doll: a vector face can only rotate and scale, so it always reads as a doll, while a drawn pose reads as acting.

Demo: [`index.html`](index.html).

## When to use it

- Guides, explainers, kids' products, onboarding flows — anywhere a character can host the page.
- Long scroll stories that need a human(ish) presence between sections.

Keep it to one mascot and four or five poses. More becomes a cartoon, and a mascot that moves constantly is worse than no mascot at all.

## How it works

1. One pose sheet: the same character in four poses on a flat magenta background, cut into four alpha WebPs and anchored on a shared feet baseline (see `assets/mascot/README.md`).
2. `data-pose` on the mascot picks the pose; CSS rules set each group's `transform`, and transitions (`0.5s` spring) carry the change.
3. Scroll: an IntersectionObserver with `rootMargin: "-42% 0px -42% 0px"` fires when a section crosses the middle band of the viewport and sets that section's pose.
4. Buttons let the visitor (and keyboard users) scrub the poses. Reduced motion removes transitions and the blink, but poses still switch instantly.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| poses | HTML | `idle / read / surprised / wave` | add a pose by adding a `data-pose` block and its CSS. |
| trigger band | JS | `-42% 0px -42% 0px` | how close to the centre a section must be. |
| transition | CSS | `0.5s var(--spring)` | the pose change speed. |
| blink | CSS | `5.2s` | idle loop; remove under reduced motion. |
| `prefers-reduced-motion` | CSS | instant | no transitions, no blink; poses still switch. |

## Reduced motion

Every transition and the blink are removed. Poses still change instantly as you scroll or press a button — the mascot is state, not motion.

## Performance

- Four images (14–17 KB each), no libraries; the browser swaps an `opacity` and a `transform`, nothing else.
- One IntersectionObserver, four sections; no scroll listener.
- The mascot is `position: sticky` in its column, so it never causes overflow.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
