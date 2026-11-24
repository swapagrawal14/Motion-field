# Prompt: Horizontal scroll

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **horizontal scroll section** to [the showcase]. The section pins, and vertical scroll drives the panel track sideways; a thin progress bar mirrors the travel. On mobile and reduced motion it becomes a native swipe row with scroll-snap.

**Behaviour**
- Section height = `100vh + (track.scrollWidth - viewport width)`; progress = `clamp(-rect.top / extra, 0, 1)`.
- Translate the track by `-p * extra`; lerp at `0.14` in a rAF loop that stops when settled.
- `overflow: clip` on the sticky wrapper so nothing causes page overflow.
- Mobile (≤860 px): section height auto, `overflow-x: auto`, `scroll-snap-type: x mandatory`, no transform.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: native horizontal row, no pinning.
- Each panel is real markup with headings; the track is not a single image.

**Look**
Wide rounded panels, one accent, 4–6 panels. Vanilla HTML/CSS/JS, no build step.

**Done when** the progress bar reaches 100% exactly as the last panel arrives, mobile is a swipe row, and there are no console errors or page overflow at 390px and 1440px.
