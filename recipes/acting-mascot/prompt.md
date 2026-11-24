# Prompt: Acting mascot

Paste this to an agent building a page. Replace the bracketed parts.

---

Add an **acting mascot** to [the page]. A single inline SVG character with four poses — idle, reading (book up), surprised (eyes wide, mouth open, arms up) and waving — changes pose as the visitor scrolls through the sections.

**Behaviour**
- Put every pose in one SVG (book, arm rotations, eye scale, brows, three mouth shapes) and switch them with `data-pose` on the mascot.
- Transitions on the groups (`0.5s` spring) so the pose change feels acted, not cut.
- Scroll: IntersectionObserver with `rootMargin: "-42% 0px -42% 0px"` sets the pose of the section crossing the middle band.
- Add buttons to scrub poses for keyboard and touch users.

**Accessibility and fallbacks**
- The mascot is decorative: `role="img"` with a short `aria-label`, or `aria-hidden` if it adds nothing.
- `prefers-reduced-motion: reduce`: remove transitions and the blink; poses still switch instantly.
- Never make the mascot the only way to understand a section.

**Look**
Painted-cutout feel: one body colour with a soft gradient, dark facial features, a cream book. Vanilla SVG/CSS/JS, no build step.

**Done when** each section sets the right pose, the buttons and scroll agree, reduced motion still switches poses, and there are no console errors or overflow at 390px and 1440px.
