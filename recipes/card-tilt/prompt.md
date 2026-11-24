# Prompt: Card tilt + glare

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **3D card tilt with glare** to the [work / product] cards. On pointer move the card tilts up to 9° toward the pointer and a soft specular highlight follows the pointer across the surface; on leave it settles flat.

**Behaviour**
- Outer wrapper `perspective: 900px`, inner card `transform-style: preserve-3d`, image layer `translateZ(30px)`.
- `pointermove` → `rotateX` / `rotateY` (max 9°) plus `--gx` / `--gy` for the glare; lerp at `0.18` in a rAF loop that stops when settled.
- `pointerleave` returns to 0; `focus` applies a fixed tilt (5° / −4°) for keyboard parity.
- Write only `transform`; the glare is a `::after`/span radial gradient.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: no tilt, no glare; keep the border and a visible focus ring.
- Cards must be reachable with the keyboard (`tabindex="0"` or a real link).

**Look**
Rounded 22 px cards, soft dark glass, one accent edge on hover. Vanilla HTML/CSS/JS, no build step.

**Done when** the card returns perfectly flat on leave, keyboard focus shows the same treatment, and there are no console errors or overflow at 390px and 1440px.
