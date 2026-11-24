# Templates

Starter pages that combine the [recipes](../recipes/INDEX.md). Copy one to `sites/<name>/`, then follow its README.

| Template | For | Moves |
|---|---|---|
| [landing/](landing/) | product / launch page | Lenis smooth scroll, pinned hero shrink, word stagger, tide canvas, marquee, staggered reveals, 3D card wall, progress rail, magnetic CTA |
| [portfolio/](portfolio/) | creative portfolio | letter stagger, infinite marquee, pinned horizontal work gallery, card tilt, count-up stats, drawn process path, hover distortion, magnetic CTA |
| [event/](event/) | event / invite page | letter stagger, countdown, lime marquee, card tilt lineup, drawn schedule path, CSS map with pulsing pin, magnetic ticket CTA, native FAQ accordions |
| [product-launch/](product-launch/) | product launch / waitlist page | letter stagger, count-up stats, floating spec chips, CSS device mock, sticky three-stop tour, drawn link graph, spec tab switcher, timeline, waitlist form |

All four use only CSS / SVG / canvas / WebGL visuals (no image files), honour `prefers-reduced-motion`,
and pass `tools/qa.py` at 390 and 1440. The landing page is the only one that pulls libraries (Lenis +
GSAP); the other three are vanilla. Placeholder copy is marked with `data-swap` attributes; never
ship it or invent stats, prices or testimonials.

Design lint every template with `python3 tools/design_lint.py templates/<name>/`.
