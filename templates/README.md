# Templates

Starter pages that combine the [recipes](../recipes/INDEX.md). Copy one to `sites/<name>/`, then follow its README.

| Template | For | Moves |
|---|---|---|
| [landing/](landing/) | product / launch page | Lenis smooth scroll, pinned hero shrink, word stagger, tide canvas, marquee, staggered reveals, 3D card wall, progress rail, magnetic CTA |
| [portfolio/](portfolio/) | creative portfolio | Lenis smooth scroll, pinned hero with three.js object, letter stagger, marquee, tilted 3D project grid, scrubbed word reveal, magnetic CTA |

Both share one art direction (midnight navy, one cyan accent, Inter Tight + JetBrains Mono), use only CSS /
SVG / canvas / WebGL visuals (no image files), honour `prefers-reduced-motion`, and pass `tools/qa.py` at 390 and 1440.
Placeholder copy is marked with `data-swap` attributes; never ship it or invent stats and testimonials.
