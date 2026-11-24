# Prompt: Hover pulse

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **hover pulse** to the [feature / pricing] cards. On hover and keyboard focus the card lifts `translateY(-4px)`, its border turns accent, a soft radial glow follows the pointer, and a thin ring pulses out once from the centre.

**Behaviour**
- Use the same declarations for `:hover` and `:focus-visible` so keyboard users get identical feedback.
- The glow is a `::after` radial gradient positioned by `--mx` / `--my` percentages set on `pointermove` (passive listener).
- The ring is a 10 px circle animating `scale(.4) → scale(16)` with `opacity: .75 → 0` over about 1.15 s.
- Cards are focusable (`tabindex="0"` if they are not links).

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: no lift, glow or ring; keep the accent border and a visible focus outline.
- Never hide information behind the hover state.

**Look**
Dark glass cards, 20 px radius, one cyan accent. Vanilla HTML/CSS/JS, no build step.

**Done when** tabbing through the grid shows the same treatment as hovering, and there are no console errors or horizontal overflow at 390px and 1440px.
