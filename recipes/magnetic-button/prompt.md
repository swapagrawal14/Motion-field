# Prompt: Magnetic button

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **magnetic button** to the [primary CTA]. Inside a padded zone around the button, the shell is pulled toward the pointer (`offset * 0.35`) and the label a little further (`offset * 0.45` more). When the pointer leaves the zone it springs back to centre.

**Behaviour**
- Listen on the padded zone, not the button, so the field starts before the pointer arrives.
- Lerp toward the target at `0.16` inside a requestAnimationFrame loop that stops once every button has settled.
- Write only `transform: translate3d(...)` on the shell and label.
- Radius ~170 px; outside it the target is 0.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce` and touch devices: normal button, no listeners, no movement.
- Keep the button a real `<button>` with a visible `:focus-visible` ring; focus must not depend on the pointer.

**Look**
Pill button, accent fill, 16 px 30 px padding. Vanilla HTML/CSS/JS, no build step.

**Done when** the button returns exactly to centre on leave, works with keyboard only, and there are no console errors or overflow at 390px and 1440px.
