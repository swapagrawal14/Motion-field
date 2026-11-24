# Prompt: Page transition

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **page transition** between [pages]. Clicking a link should cover the old page with a wipe and reveal the new one in about 420 ms.

**Behaviour**
- Use `document.startViewTransition(() => swapPage())` where supported, with `::view-transition-old/new` durations matching.
- Fallback: a full-screen curtain that animates `scaleY` from bottom to top, swapping the pages at the midpoint, then `scaleY` back to 0 from the top.
- Never block the click; the curtain is `pointer-events: none`.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: instant swap, no curtain, no transition.
- Keep focus and scroll position sensible after the swap; update `aria-current` on the nav.

**Look**
A navy → cyan → navy curtain that matches the accent. Vanilla HTML/CSS/JS, no build step.

**Done when** rapid repeated clicks never leave the curtain stuck, reduced motion swaps instantly, and there are no console errors or overflow at 390px and 1440px.
