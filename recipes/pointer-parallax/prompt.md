# Prompt: pointer parallax

---

Build a **pointer-parallax scene** for [hero / section]. The scene is [describe the layers: background stars, a planet, a ring, two moons, a sparkle, a headline].

**Behaviour**
- The stage sets two CSS variables, `--x` and `--y`, from −1 to 1, based on the pointer position over it (mouse/pen only; ignore `pointerType === "touch"`).
- Each layer has its own `--depth` (far layers −0.3…−1, mid 0.5…1.5, near 2…3) and uses `transform: translate3d(calc(var(--x) * var(--depth) * var(--unit)), calc(var(--y) * var(--depth) * var(--unit) * .75), 0)`.
- Smooth with a lerp in one requestAnimationFrame loop (`x += (tx - x) * 0.07`).
- With no pointer, drift on its own: `tx = sin(t/2600) * .42`, `ty = cos(t/3400) * .34`.
- Pause the loop when the stage is offscreen (IntersectionObserver) or the tab is hidden.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: park every layer at 0, cancel the loop, ignore the pointer.
- The stage is decorative: `role="img"` + `aria-label`. Keep copy at low depth so it stays readable.
- `touch-action: pan-y` on the stage so scrolling on phones is never blocked.

**Look**
Dark navy space (#070d1a → #12306b), one cyan accent (#3fdcff) for glows, layers built from CSS gradients or transparent PNG/WebP cut-outs sized ~10% larger than the stage. 28px radius, soft shadow. Portrait aspect (4:5) under 720px.

Vanilla HTML/CSS/JS, no build step. **Done when** no console errors, no horizontal overflow at 390px and 1440px, and screenshots (normal + reduced motion) look composed in both.
