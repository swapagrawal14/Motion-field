# Prompt: Letter stagger

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **letter stagger** entrance to the main heading of [page/section]. Split the heading into words, then characters; each character eases up from `translateY(.42em)` with `blur(8px)` → `0` and a `26ms` stagger per character. Words must never break across lines (wrap each word in an `inline-block` with `white-space: nowrap`).

**Behaviour**
- Keep the real text for assistive tech: set `aria-label` on the heading and `aria-hidden="true"` on the split spans.
- Play once when the heading enters view (IntersectionObserver, ~40% visible).
- Hovering a word replays only that word (add a class for one animation run, remove it on `animationend`).
- Include a "Replay" button that resets the animation.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: no animation, all characters visible immediately.
- No layout shift: the split must not change the line height.

**Look**
Display type, tight tracking (−0.04em), one accent word. Vanilla HTML/CSS/JS, no build step.

**Done when** there are no console errors, no horizontal overflow at 390px and 1440px, and the heading reads correctly with reduced motion on.
