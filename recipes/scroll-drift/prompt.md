# Prompt: scroll drift

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **scroll drift band** to [section / page]. While the band crosses the viewport, its rows of large type and image tiles slide horizontally; the page scrolls down, the story moves sideways.

**Content**
- Row 1: [4–6 short words, e.g. "Drift with the tide of the page."] interleaved with [3–5 image tiles / rounded pills].
- Row 2 (optional, decorative, `aria-hidden="true"`): an outlined phrase repeated, moving the opposite way.

**Behaviour**
- Each row has `data-drift` in vw (row 1 `-28`, row 2 `+20`). Progress per band = `clamp((innerHeight - rect.top) / (innerHeight + rect.height), 0, 1)`; offset = `(progress - 0.5) * drift`.
- Smooth with a lerp (`current += (target - current) * 0.12`) inside a requestAnimationFrame loop that stops once settled. Write only `transform: translate3d(Xvw, 0, 0)`.
- Passive scroll/resize listeners; skip bands outside the viewport with an IntersectionObserver.
- The band uses `overflow-x: clip` so the page never scrolls horizontally. Make each row long enough to cover the viewport at both ends of its travel.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: rows sit at 0 with no easing; stop any decorative cue animation.
- Real text stays real text; decorative duplicate rows are `aria-hidden`.

**Look**
Large display type (clamp 64–164px, tight tracking around −0.05em), one accent colour for a soft word, tiles with 22px radius and a soft shadow. Vanilla HTML/CSS/JS, no build step, no libraries.

**Done when** there are no console errors, no horizontal overflow at 390px and 1440px, and screenshots at 1440x900 and 390x844 (normal and reduced motion) look intentional.
