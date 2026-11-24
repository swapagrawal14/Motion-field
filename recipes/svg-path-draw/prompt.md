# Prompt: SVG path draw

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **scroll-drawn SVG path** through the [process / timeline] section. The path connects [4] steps with a smooth curve and draws itself as the visitor scrolls, retracing when they scroll back.

**Behaviour**
- Put `pathLength="1"` on the path so `stroke-dasharray: 1` + `stroke-dashoffset` work in 0–1 units.
- Progress = `clamp((innerHeight * 0.9 - rect.top) / (rect.height + innerHeight * 0.55), 0, 1)`; lerp toward it (`0.12`) in a requestAnimationFrame loop that stops when settled.
- Each node lights up when progress passes its threshold; do the same for the matching step card.
- Scroll back → the line retraces.

**Accessibility and fallbacks**
- Give the SVG `role="img"` and an `aria-label` describing the journey; the visible step text stays real HTML.
- `prefers-reduced-motion: reduce`: path fully drawn, all steps lit, no loop.
- Keep the path inside one section with `overflow: visible` so it never causes page overflow.

**Look**
Thin 2.5 px accent stroke with a soft glow, dotted ghost line underneath, dark surface. Vanilla HTML/CSS/JS, no build step.

**Done when** there are no console errors, no horizontal overflow at 390px and 1440px, and the path is fully drawn under reduced motion.
