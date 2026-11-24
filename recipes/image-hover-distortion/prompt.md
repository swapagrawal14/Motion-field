# Prompt: Image hover distortion

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **hover distortion** to the [portfolio / editorial] images. On hover and keyboard focus, the image warps through an SVG displacement filter: `feTurbulence` (fractal noise, `baseFrequency 0.012 0.02`, 2 octaves) feeding `feDisplacementMap` with `scale` animated from 0 to ~26, and `baseFrequency` oscillating slowly so the grain keeps moving. On leave it settles back to 0.

**Behaviour**
- One shared `<filter id="warp">`; each figure applies it with `filter: url(#warp)`.
- Lerp `scale` at `0.12` in a rAF loop; stop the loop once it returns to 0.
- Add a tiny `scale(1.015)` push on the figure.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: `filter: none`, no scale, no listeners.
- Figures are focusable so keyboard users see the same effect; keep a visible focus ring.

**Look**
Rounded 20 px frames, CSS-gradient art or real WebP/AVIF under 150 KB. Vanilla HTML/CSS/JS + one SVG filter, no build step.

**Done when** the image settles perfectly still on leave, the effect works from the keyboard, and there are no console errors or overflow at 390px and 1440px.
