# Prompt: Infinite marquee

Paste this to an agent building a page. Replace the bracketed parts.

---

Add an **infinite marquee** to [the proof / logo band]. Two rows (the second in the opposite direction) loop seamlessly, pause on hover and keyboard focus, and become a static strip under reduced motion.

**Behaviour**
- Each row contains the content once plus an identical `aria-hidden` duplicate; animate `translate3d(-100%, 0, 0)` so the loop is exactly one track wide.
- `gap` and `padding-right` must be equal, or the loop jumps.
- `mask-image: linear-gradient(90deg, transparent, #000 7%, #000 93%, transparent)` fades both edges.
- `overflow: clip` on the section so the page never scrolls sideways.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: hide the duplicate, lay the items out statically, remove the mask.
- Never put essential information only in the marquee.

**Look**
Large tight type, one accent dot between items, two speeds. Vanilla HTML/CSS, no build step.

**Done when** the loop has no visible seam at any width, hovering pauses both rows, and there are no console errors or horizontal overflow at 390px and 1440px.
