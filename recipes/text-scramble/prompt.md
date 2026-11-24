# Prompt: Text scramble

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **text scramble** to the [nav items / hero label]. On hover, keyboard focus and first entrance, each character cycles through a short glyph set (`!<>-_\/[]{}—=+*^?#`) and resolves left to right in about 600 ms.

**Behaviour**
- Store the real text in `data-text`; compute `solved = floor(progress * length)` each frame and show random glyphs after that index (spaces stay spaces).
- One `requestAnimationFrame` loop per element; cancel the previous run when a new one starts.
- Hover/focus runs faster (~420 ms); the heading runs once when it enters view.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: show the real text instantly, no scramble.
- Keep the real text in the DOM for screen readers; never scramble prices, dates or body copy.

**Look**
Monospace labels, wide letter-spacing, one accent underline that draws on hover. Vanilla HTML/CSS/JS, no build step.

**Done when** fast repeated hovers never stack animations, the label always ends on the real text, and there are no console errors or overflow at 390px and 1440px.
