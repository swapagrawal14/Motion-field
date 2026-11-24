# Prompt: Field cursor

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **custom field cursor** to [page]. On fine-pointer devices, replace the pointer with a 38 px ring plus a 5 px accent dot; the dot tracks exactly, the ring lerps behind it (`0.18`). Over any element with `data-cursor="View"` (or Drag / Play) the ring grows to ~74 px and shows that verb as a small accent pill.

**Behaviour**
- Hide the native cursor only inside `[scope]` with `cursor: none`, never globally.
- Initialise only when `matchMedia("(pointer: fine)")` matches.
- Use one delegated `pointerover` / `pointerout` pair; move the three layers with `transform` inside a rAF loop that stops when settled.
- Never show the ring before the first pointer move.

**Accessibility and fallbacks**
- Touch devices and `prefers-reduced-motion: reduce` keep the native cursor and see no ring.
- Links and buttons must still look interactive without the cursor (underline, border, label).

**Look**
Thin cyan ring, soft inner glow, uppercase mono label. Vanilla HTML/CSS/JS, no build step.

**Done when** the ring never appears on a touch device, there are no console errors or overflow at 390px and 1440px, and tabbing through the page is unaffected.
