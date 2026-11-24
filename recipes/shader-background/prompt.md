# Prompt: Shader background

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **WebGL shader background** behind [the hero]. Use one full-screen triangle and a fragment shader with layered value noise (fbm, ~5 octaves) flowing through deep navy into a cyan glow, with a soft halo that follows the pointer. No library.

**Behaviour**
- `u_res`, `u_t`, `u_m` uniforms; `gl.viewport` on resize; cap device pixel ratio at 1.5.
- Draw in a `requestAnimationFrame` loop that pauses when the section is offscreen (IntersectionObserver) and on `visibilitychange`.
- Keep a CSS gradient behind the canvas as the fallback for browsers without WebGL.
- Add a scrim between the shader and any text.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: one still frame or the CSS gradient; no loop.
- Text over the shader must still hit 4.5:1 contrast.

**Look**
Deep navy base, one cyan accent, soft vignette. Vanilla JS + GLSL, no build step.

**Done when** the context pauses offscreen, the page still looks right with WebGL disabled, and there are no console errors or overflow at 390px and 1440px.
