# Prompt: three.js hero object

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **three.js hero object** to [the hero]. A lit object (torus knot or [your mesh]) turns slowly with time, follows the pointer and tilts with scroll. It must pause when offscreen and when the tab is hidden.

**Behaviour**
- `import()` three.js from a CDN (unpkg, jsDelivr fallback); never block first paint.
- One mesh, `MeshStandardMaterial`, two coloured point lights + ambient.
- Pointer target lerped at `0.06`; idle turn `t * 0.00022`.
- IntersectionObserver pauses the loop offscreen; `visibilitychange` pauses it when hidden; cap DPR at 1.5.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: one still frame, no loop, no pointer.
- If three.js or WebGL fails, keep a CSS/SVG stand-in so the hero still looks finished.

**Look**
Cyan and violet rim light on deep navy, object off-centre with the headline to one side. Vanilla JS + three.js ESM, no build step.

**Done when** the canvas stops rendering offscreen (check with a frame counter), the fallback shows if the CDN is blocked, and there are no console errors or overflow at 390px and 1440px.
