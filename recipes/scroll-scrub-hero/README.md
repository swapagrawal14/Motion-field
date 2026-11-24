# Scroll-scrub video hero

Apple-style frame scrubbing: a WebP frame sequence sits on a canvas and scroll position picks the frame. No video decode, no autoplay, no sound — and the poster is the very first frame, so the hero is never empty.

Demo: [`index.html`](index.html).

## When to use it

- Product turntables, architectural walkthroughs, title sequences — anything you would otherwise autoplay.
- A hero that must feel like video but stay cheap, silent and reversible.

Keep the sequence short (18–30 frames) and the frame size close to display size. For longer sequences, ship a real `<video>` with `preload="none"` and use this only for the first beat.

## How it works

1. `tools/frames.py` turns a video (ffmpeg) or the built-in turntable (Playwright) into `frames/f-000.webp … f-023.webp`, a poster and `manifest.json`.
2. The demo preloads every frame once, showing a progress bar; when the last one decodes it adds `.is-ready` and reveals the canvas.
3. Scroll progress over the pinned section is mapped to `Math.round(p * (count - 1))`; a new frame is drawn only when that index changes.
4. Reduced motion hides the canvas and leaves the poster. The poster is also the `alt`-carrying element, so the hero has real content before any JS runs.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| pin length | CSS | `240vh` (190 mobile) | how much scroll the whole sequence spans. |
| frames | tool | `24` | 18–30 is the sweet spot; more = heavier. |
| frame size | tool | `720×450` | match display size ×1.5 for retina. |
| lerp | JS | `0.16` | lower = smoother scrub, higher = tighter. |
| `prefers-reduced-motion` | JS/CSS | poster | no canvas, no loop. |

## Reduced motion

The canvas is hidden and the poster remains — the hero is a normal image. No frames are drawn and no scroll listener runs.

## Performance

- Frames are decoded once and kept in memory; `drawImage` runs only when the frame index changes.
- The rAF loop stops when the scrub settles; the pinned section is `overflow: clip` so nothing overflows.
- 24 frames at 720×450 is ~510 KB. Use `quality=72` and `method=6`; drop to 18 frames or 640 px wide if that is too heavy.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
