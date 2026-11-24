# Prompt: Pinned hero shrink

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **pinned hero shrink** to [the top of the page]. The hero media fills the viewport and pins while the page scrolls; as you scroll it shrinks to ~84% and rounds into a 30 px card, while the headline lifts away and fades.

**Behaviour**
- `.pin { height: 220vh }` (170 vh on mobile), inner `.pin__sticky { position: sticky; top: 0; height: 100vh; overflow: clip }`.
- Progress = `clamp(-rect.top / (rect.height - innerHeight), 0, 1)`.
- Media: `scale(1 - p * 0.16)`, `border-radius: p * 30px`, a shadow that grows with `p`.
- Copy: `opacity: 1 - p * 1.9`, `translateY(-p * 70px)`.
- Lerp at `0.14` in a rAF loop that stops when settled.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: no pinning, no transform; the hero is a normal static section.
- Never pin two sections back to back; keep the pin under ~220 vh.

**Look**
Deep navy, one cyan orb, soft grid, tight display type. Vanilla HTML/CSS/JS, no build step.

**Done when** scrolling back up unfolds the hero, reduced motion shows a normal hero, and there are no console errors or overflow at 390px and 1440px.
