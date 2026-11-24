# Prompt: Scroll-scrub video hero

Paste this to an agent building a page. Replace the bracketed parts.

---

Add a **scroll-scrub video hero** to [the hero]. A short frame sequence (18–30 WebP frames, extracted from a video) is drawn on a canvas; scroll position picks the frame. It must not autoplay and must have no sound.

**Behaviour**
- Pin the section for ~240 vh (190 vh on mobile); progress = `clamp(-rect.top / (height - innerHeight), 0, 1)`.
- Frame index = `Math.round(p * (count - 1))`; draw with `drawImage` only when the index changes.
- Preload every frame once with a progress bar; reveal the canvas only when the last frame has decoded.
- Keep the poster as the first frame and give it real `alt` text.

**Accessibility and fallbacks**
- `prefers-reduced-motion: reduce`: hide the canvas, show the poster, no loop.
- The hero must look complete before any frame loads (poster + headline).

**Look**
Full-bleed rounded frame, dark scrim, headline bottom-left, frame counter top-right. Vanilla HTML/CSS/JS, no build step.

**Done when** scrolling back up reverses the sequence, reduced motion shows only the poster, and there are no console errors or overflow at 390px and 1440px.
