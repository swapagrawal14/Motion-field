# Prompt: Acting mascot

Paste this to an agent building a page. Replace the bracketed parts.

---

Add an **acting mascot** to [the page]. Four **generated character cutouts** of the SAME character — idle, reading (book up), surprised (eyes wide, mouth open, arms up) and waving — change as the visitor scrolls through the sections. Transparent WebP, under 20 KB each, generated from one pose sheet on a flat magenta background.

**Behaviour**
- Stack the four `<img>` poses in one `aspect-ratio` box, anchor them on the same feet baseline, and switch with `data-pose` on the mascot (`opacity` + a small `transform`).
- Transitions on the groups (`0.5s` spring) so the pose change feels acted, not cut.
- Scroll: IntersectionObserver with `rootMargin: "-42% 0px -42% 0px"` sets the pose of the section crossing the middle band.
- Add buttons to scrub poses for keyboard and touch users.

**Accessibility and fallbacks**
- The mascot is decorative: `role="img"` with a short `aria-label`, or `aria-hidden` if it adds nothing.
- `prefers-reduced-motion: reduce`: remove transitions and the blink; poses still switch instantly.
- Never make the mascot the only way to understand a section.

**Look**
Flat picture-book fills with a uniform thick dark outline, same character in every pose. Vanilla HTML/CSS/JS, no build step. **Do not** build the mascot as inline SVG — a vector doll can only rotate and scale, so it never reads as acting.

**Done when** each section sets the right pose, the buttons and scroll agree, reduced motion still switches poses, and there are no console errors or overflow at 390px and 1440px.
