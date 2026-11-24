# Horizontal scroll

Vertical scroll drives a sideways gallery: the section pins, the track travels horizontally, and a progress bar shows how far you are. On phones and reduced motion it becomes a native swipe row with snap points.

Demo: [`index.html`](index.html).

## When to use it

- Work showcases, product tours, process stories — anything with a sequence of panels.
- When the panels are wide and landscape (a horizontal track wastes less space than a vertical stack).

Don't use it for content people must read in full, and never pin two sections back to back. Keep it to 4–6 panels.

## How it works

1. The section's height is set to `100vh + (track.scrollWidth - sticky.clientWidth)`, so the scroll distance matches the horizontal travel exactly.
2. Progress = `clamp(-rect.top / extra, 0, 1)` over that extra height.
3. The track is translated by `-p * extra`; a progress bar mirrors `p`.
4. On mobile (≤860 px) and reduced motion the section height resets, the sticky wrapper becomes `overflow-x: auto` with `scroll-snap-type: x mandatory`, and JS writes no transform.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| panel width | CSS | `40vw` (300–520 px) | wider panels = fewer visible at once. |
| travel | JS | `track.scrollWidth - viewport` | exact 1:1 mapping with scroll. |
| lerp | JS | `0.14` | lower = floatier, `1` = locked. |
| snap | CSS | `x mandatory` | mobile only; use `proximity` for a softer feel. |
| `prefers-reduced-motion` | JS/CSS | native row | no pin, no transform. |

## Reduced motion

The section height resets to auto, the sticky wrapper becomes a native horizontal scroller with snap points, and no transform is written. The visitor swipes instead of scrolling the page.

## Performance

- One rect read per scroll event; the rAF loop stops when settled.
- Only `transform` on the track (plus one `height` set on resize, not per frame).
- `overflow: clip` on the sticky wrapper prevents horizontal page overflow.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
