# Prompt: 3D tilted card wall

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **3D tilted card wall** to [the showcase section]. A grid of preview cards sits in perspective (`rotateX(13deg) rotateY(-16deg) rotateZ(3deg)`); as the visitor scrolls, columns drift vertically in alternating directions, and the plane leans a few degrees toward the pointer.

**Behaviour**
- Scene `perspective: 1400px`, plane `transform-style: preserve-3d`.
- Scroll progress measured against the scene; each column translates `±26px` in alternating directions.
- `pointermove` adds ±4° / ±5° to the plane rotation, lerped at `0.08`; `pointerleave` returns to 0.
- Only `transform` changes; stop the rAF loop when settled.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce` and screens under 700 px: flat grid, no transforms.
- Cards stay real links with visible focus rings.

**Look**
Dark glass cards, three tinted columns, one accent label. Vanilla HTML/CSS/JS, no build step.

**Done when** the wall is flat and readable on mobile, the plane returns to its base tilt on leave, and there are no console errors or overflow at 390px and 1440px.
