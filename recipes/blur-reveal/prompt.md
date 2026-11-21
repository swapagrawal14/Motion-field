# Prompt: blur reveal

---

Add a **blur-to-clear reveal** to [these sections: feature rows / chapters / spec grid]. Each block resolves from soft to sharp the first time it enters the viewport: the image first, then label, title and body a beat behind.

**Behaviour**
- Mark blocks with `data-reveal`; give children `--i` (0, 1, 2…) for a 90 ms stagger.
- In `<head>`, add `document.documentElement.classList.add("js-reveal")` so the hidden state applies before first paint and never applies without JS.
- One IntersectionObserver (`threshold: 0.35`, `rootMargin: "0px 0px -6% 0px"`) adds `.is-in` once and unobserves.
- Hidden state: image `filter: blur(22px) saturate(.6); transform: scale(1.06); opacity: .4`; text `filter: blur(10px); opacity: 0; transform: translateY(18px)`.
- Transitions: image 1.4 s, text 1.1–1.2 s with `transition-delay: calc(350ms + var(--i) * 90ms)`, easing `cubic-bezier(.16, 1, .3, 1)`.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: add `.is-in` to everything immediately and disable the transitions.
- No IntersectionObserver: remove `.js-reveal` so everything shows.
- Do not use it on the hero's LCP element.

**Look**
Editorial and calm: large titles (34–64px, tracking −0.045em) with a muted second phrase, 26px-radius media, generous vertical spacing (72–160px between blocks).

Vanilla HTML/CSS/JS, no build step. **Done when** no console errors, no horizontal overflow at 390px and 1440px, and screenshots at 1440x900 and 390x844 (normal + reduced) show no text stuck invisible.
