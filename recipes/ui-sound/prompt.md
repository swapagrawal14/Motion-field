# Prompt: UI sound kit

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **procedural UI sound kit** to [the site]. On hover play a short tick, on click play a pop, on a drawer or page transition play a whoosh, and on form success / error play a two-note chime. No audio files: synthesize everything with WebAudio.

**Behaviour**
- Sound is muted by default. The first click on a `[data-sfx-toggle]` button creates the AudioContext and enables playback; it mirrors state with `aria-pressed`.
- Delegated listeners: `data-sfx` on click / Enter / Space, `data-sfx-hover` on `pointerover`.
- Each sound is a short oscillator or filtered noise burst with an exponential envelope (peaks 0.05–0.2).
- Never let a sound error break the page; wrap playback in try/catch.

**Accessibility and fallbacks**
- Never autoplay; never make sound the only feedback.
- Provide a visible mute toggle and keep it keyboard reachable.
- Respect `prefers-reduced-motion` by staying muted unless the visitor explicitly opts in.

**Look**
A small pill toggle in the nav, one accent, no visible audio player. One JS file, no dependencies, no build step.

**Done when** the page is silent on load, the toggle enables and disables sound, keyboard activation plays the click sound, and there are no console errors at 390px and 1440px.
